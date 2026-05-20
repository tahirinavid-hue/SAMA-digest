"""
Grand Island Community Digest — searches for upcoming local events for all GI residents.
Uses Claude claude-sonnet-4-6 with web_search tool (server-side, agentic loop).
"""
import os
import time
import anthropic

MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 8,
    }
]

PROMPT = """You are a community events digest assistant for Grand Island, NY. Search for upcoming events in the next 2 weeks using these sources: grandislandny.gov, isledegrande.com, wnypapers.com, gicf.org, gineighbors.org, gichamber.org, volunteerwny.org, stepoutbuffalo.com

Rules:
- Do NOT mention the sources or list them anywhere in your output
- Do NOT include any disclaimer, warning, or note about which sites were checked or unavailable
- Do NOT copy descriptions verbatim — always reword or summarize in your own words
- Only include events with confirmed dates
- Include events open to all residents: town meetings, festivals, fundraisers, volunteer opportunities, family events, sports, arts, library programs, school events, civic gatherings

Format:
- Start with exactly this header (fill in the actual date range): 🏝️ Grand Island, NY — Community Events Digest\n[date range, e.g. May 20 – June 2, 2026]
- Then list events grouped by week as clean markdown
- For each event include: event name, date, time if known, location, and a 1-2 sentence description in your own words
- No source citations, no footnotes, no closing remarks about where to find more info"""

MAX_CONTINUATIONS = 2


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
                print(f"[gi_community_digest] Rate limited, retrying in {wait}s")
                time.sleep(wait)
        else:
            raise RuntimeError("Rate limit retries exhausted")

        for block in response.content:
            if hasattr(block, "text") and block.text.strip():
                all_text.append(block.text.strip())

        if response.stop_reason == "end_turn":
            return "\n\n".join(all_text)

        if response.stop_reason == "pause_turn":
            if continuations >= MAX_CONTINUATIONS:
                return "\n\n".join(all_text)
            continuations += 1
            messages = messages + [
                {"role": "assistant", "content": response.content},
                {"role": "user", "content": "Please continue."},
            ]
            print(f"[gi_community_digest] Continuing (iteration {continuations})")
            continue

        return "\n\n".join(all_text)
