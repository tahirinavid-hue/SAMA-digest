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

PROMPT = """Search for upcoming events on Grand Island, NY in the next 2 weeks using: grandislandny.gov, isledegrande.com, wnypapers.com, gicf.org, gineighbors.org, gichamber.org, volunteerwny.org, stepoutbuffalo.com

Output rules — strictly follow every one:
- Begin your response with NOTHING except the header line below. No preamble, no "here is", no "let me", no thinking out loud.
- First line must be exactly: # 🏝️ Grand Island, NY — Community Events Digest
- Second line must be exactly the date range, e.g.: May 20 – June 2, 2026
- Then list events grouped by week as clean markdown
- Only include events with confirmed upcoming dates — no past events
- For each event: event name as a bold heading, then date/time/location, then a 1-2 sentence plain description in neutral human language
- Write like a local newsletter editor, not an AI — no em-dashes (—), no phrases like "join us", "don't miss", "be sure to", no bullet points starting with verbs like "Enjoy" or "Discover"
- Do NOT mention sources, disclaimers, footnotes, warnings about unavailable sites, or closing remarks
- Do NOT copy any description verbatim — always reword in plain conversational English"""

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
