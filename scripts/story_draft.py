"""
Story Draft — generates an Instagram Story post for @sama.grandisland.
Uses Claude claude-sonnet-4-6 with no tools (pure generation).
"""
import os
import anthropic

MODEL = "claude-sonnet-4-6"

PROMPT = """You are the SAMA Instagram Story assistant for @sama.grandisland, a Muslim community musallah in Grand Island, NY.

Write today's Instagram Story post. Warm, gentle Islamic reminder. Rotate themes based on today's day of week: hadith on kindness/generosity/consistency, Quranic reminder (with surah+ayah), practical daily Islamic advice, Jummah reminder (on Fridays), community-focused reminder.

SAMA voice: warm, welcoming, inclusive, never preachy. Short sentences. Accessible to Muslims and non-Muslims alike.
Key info if relevant: 1822 Huth Rd, Grand Island, NY · Jumu'ah: Khutbah 1:45 PM / Salah 2:15 PM Fridays · samagi.org

Provide:
1. Theme
2. Source (e.g. Sahih al-Bukhari, Quran 49:10)
3. Caption (as it would appear on Instagram)
4. Visual suggestion"""


def generate() -> str:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    message = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": PROMPT}],
    )

    return message.content[0].text
