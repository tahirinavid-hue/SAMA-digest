"""
Community Digest — searches for upcoming local events relevant to SAMA.
Uses Claude claude-sonnet-4-6 with web_search tool (server-side, agentic loop).
Runs on Mondays only.
"""
import os
import anthropic

MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 15,
    }
]

PROMPT = """You are the SAMA community digest assistant. Search for upcoming events (next 2 weeks) on these sites: grandislandny.gov, isledegrande.com, wnypapers.com, gicf.org, gineighbors.org, gichamber.org, volunteerwny.org, stepoutbuffalo.com, wnymuslims.org, isnfwny.org

For each relevant event include: event name, date, description, why it matters to SAMA (Service and Mercy Alliance, Muslim community musallah at 1822 Huth Rd, Grand Island, NY), and 3–5 recommended actions SAMA should take.

Focus on events relevant to a Muslim community organization: interfaith events, community gatherings, volunteer opportunities, family events, local civic meetings."""

MAX_CONTINUATIONS = 5


def generate() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [{"role": "user", "content": PROMPT}]
    continuations = 0

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    return block.text
            return ""

        if response.stop_reason == "pause_turn":
            # Server-side tool loop hit its iteration limit — re-send to continue
            if continuations >= MAX_CONTINUATIONS:
                # Extract whatever text we have so far
                for block in response.content:
                    if hasattr(block, "text"):
                        return block.text
                return ""
            continuations += 1
            messages = [
                {"role": "user", "content": PROMPT},
                {"role": "assistant", "content": response.content},
            ]
            print(f"[community_digest] Continuing (iteration {continuations})")
            continue

        # Unexpected stop reason — return whatever text we have
        for block in response.content:
            if hasattr(block, "text"):
                return block.text
        return ""
