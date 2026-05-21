"""
Grand Island Community Digest — searches for upcoming local events for all GI residents.
Uses Claude claude-sonnet-4-6 with web_search tool (server-side, agentic loop).
"""
import os
import time
import anthropic
from datetime import datetime, timezone as _tz, timedelta

MODEL = "claude-sonnet-4-6"

TOOLS = [
    {
        "type": "web_search_20250305",
        "name": "web_search",
        "max_uses": 12,
    }
]


def _get_weeks() -> list[tuple[str, str]]:
    """Return two calendar week ranges (Mon–Sun) starting from today."""
    today = datetime.now(_tz.utc).date()
    # Start of this week (Monday)
    monday = today - timedelta(days=today.weekday())
    weeks = []
    for i in range(2):
        start = monday + timedelta(weeks=i)
        end = start + timedelta(days=6)
        weeks.append((start.strftime("%b %d"), end.strftime("%b %d")))
    return weeks


def _build_prompt() -> str:
    today = datetime.now(_tz.utc)
    today_str = today.strftime("%B %d, %Y")
    today_date = today.date()
    weeks = _get_weeks()
    week1_start, week1_end = weeks[0]
    week2_start, week2_end = weeks[1]

    return f"""Today's date is {today_str}. Search for upcoming events on Grand Island, NY in the next 2 weeks using: grandislandny.gov, isledegrande.com, wnypapers.com, gicf.org, gineighbors.org, gichamber.org, volunteerwny.org, stepoutbuffalo.com, ecdparks.org

Search priority — run these searches in this order:
1. General upcoming events on Grand Island NY
2. "Grand Island NY kids" OR "Grand Island NY children" OR "Grand Island NY family events"
3. "Grand Island NY parks and recreation" OR "Grand Island NY youth sports"
4. Grand Island Memorial Library upcoming programs
5. Beaver Island State Park OR Buckhorn Island State Park upcoming events programs ecdparks.org
6. Grand Island school events or PTA events

Make sure at least 2-3 family/kids events appear in the final digest if any exist.

STRICT EXCLUSION RULES — exclude any event that:
- Has a date before today ({today_str}) — no past events, not even "just passed"
- Has no confirmed specific date (no "Date TBD", "TBA", "check website", "ongoing", "season-long")
- Is a general facility announcement (e.g. "park is open for the season") not a specific event

Output format — follow exactly:
- Begin with NOTHING except the header. No preamble, no thinking out loud, no intro sentences.
- Line 1: # Grand Island, NY
- Line 2: *[A short, original, family-friendly joke. Different every time. Not "Why did the chicken..."]*
- Line 3: blank
- Line 4: ### Upcoming Events
- Then a summary — one line per event, no bullets, no dashes, format: `N. **Event Name** · Day, Mon DD`
  List in strict chronological order. Number sequentially from 1.
- Then a horizontal rule: ---
- Then events grouped into exactly these two weeks:
  ## 📅 Week 1: {week1_start} – {week1_end}
  ## 📅 Week 2: {week2_start} – {week2_end}
  Place each event in the correct week based on its date. If an event falls outside both weeks, exclude it.
- For each event:
  **N. [emoji] Event Name**
  Day, Month DD · Time (if known) · Location
  1-2 sentence description in plain conversational English, reworded in your own words
- Emoji guide: 🎵 music, 🎨 arts, 🏃 sports/fitness, 🌿 outdoors/nature, 🍽️ food/dining, 👨‍👩‍👧 family/kids, 🏛️ civic/government, 🙌 volunteer/charity, 🎉 festival/celebration, 📚 education/library
- Write like a local newsletter editor — no em-dashes, no "join us", "don't miss", "be sure to"
- Do NOT mention sources, disclaimers, footnotes, or closing remarks
- Do NOT copy descriptions verbatim — always reword in plain English"""


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
