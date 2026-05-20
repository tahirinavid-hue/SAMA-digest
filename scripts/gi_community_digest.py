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

from datetime import datetime, timezone as _tz
def _build_prompt() -> str:
    today = datetime.now(_tz.utc).strftime("%B %d, %Y")
    return f"""Today's date is {today}. Search for upcoming events on Grand Island, NY in the next 2 weeks using: grandislandny.gov, isledegrande.com, wnypapers.com, gicf.org, gineighbors.org, gichamber.org, volunteerwny.org, stepoutbuffalo.com

Output rules — strictly follow every one:
- Begin your response with NOTHING except the header line below. No preamble, no "here is", no "let me", no thinking out loud.
- First line must be exactly: # 🏝️ Grand Island, NY Community Events Digest
- Second line must be blank
- Third line must be exactly: ### Upcoming Events
- Fourth section is a summary — one line per event, NO bullet points, NO indentation, NO dashes, format: `N. **Event Name** · Date` (e.g. `1. **Memorial Day Ceremony** · Mon, May 25`). List in strict chronological order by date. No emoji, no extra detail. Include every event that appears below, numbered sequentially starting at 1. The numbers here must match the numbers used on each event in the weekly detail section below.
- After the summary, add a horizontal rule: ---
- Then list events grouped by week. Each week heading must start with 📅, e.g.: ## 📅 Week 1: May 24 – May 30
- STRICT DATE RULE: today is {today}. Any event whose date is before today must be completely excluded — do not mention it at all, not even as "just passed"
- Number each event sequentially across the whole digest: 1, 2, 3, etc.
- For each event use this format:
  **N. [single relevant emoji] Event Name**
  Date, time if known, location
  1-2 sentence plain description in your own words
- Choose the emoji based on event type: 🎵 music, 🎨 arts, 🏃 sports/fitness, 🌿 outdoors/nature, 🍽️ food/dining, 👨‍👩‍👧 family, 🏛️ civic/government, 🙌 volunteer/charity, 🎉 festival/celebration, 📚 education/library
- Write like a local newsletter editor, not an AI — no em-dashes, no "join us", "don't miss", "be sure to"
- Do NOT mention sources, disclaimers, footnotes, warnings, or closing remarks
- Do NOT copy any description verbatim — always reword in plain conversational English"""

PROMPT = _build_prompt()

MAX_CONTINUATIONS = 2


def generate() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    messages = [{"role": "user", "content": _build_prompt()}]
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
