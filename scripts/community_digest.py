"""
Community Digest — searches for upcoming local events relevant to SAMA.
Uses Claude claude-sonnet-4-6 with web_search tool (server-side, agentic loop).
Runs on Mondays only.
"""
import os
import time
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

    all_text = []

    while True:
        for attempt in range(5):
            try:
                response = client.messages.create(
                    model=MODEL,
                    max_tokens=8096,
                    tools=TOOLS,
                    messages=messages,
                )
                break
            except anthropic.RateLimitError:
                wait = 30 * (attempt + 1)
                print(f"[community_digest] Rate limited, retrying in {wait}s")
                time.sleep(wait)
        else:
            raise RuntimeError("Rate limit retries exhausted")

        # Collect all text blocks from this response
        for block in response.content:
            if hasattr(block, "text") and block.text.strip():
                all_text.append(block.text.strip())

        if response.stop_reason == "end_turn":
            return "\n\n".join(all_text)

        if response.stop_reason == "pause_turn":
            if continuations >= MAX_CONTINUATIONS:
                return "\n\n".join(all_text)
            continuations += 1
            # Append assistant response and ask to continue
            messages = messages + [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": "Please continue."},
            ]
            print(f"[community_digest] Continuing (iteration {continuations})")
            continue

        return "\n\n".join(all_text)
