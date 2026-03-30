# SAMA Daily Instagram Story — Workflow (MVP)

## Overview
Every evening at 8:00 PM ET, a Claude agent drafts a ready-to-review Instagram Story post.
You review it, drop the text into your Canva template, and post to @sama.grandisland.
Total time: ~5 minutes.

## Step-by-Step

### Step 1 — Review the Draft (8:00 PM ET)
1. Open: https://claude.ai/code/scheduled/trig_01WySGxZzoA7GDmZE83yJoQ1
2. Click the most recent run to see today's draft
3. Review the caption and source — edit if needed

### Step 2 — Open Your Canva Template
1. Go to canva.com → Your designs → **SAMA Story Template**
2. Click **"Use this template"** (or duplicate it)

### Step 3 — Drop In the Text
Replace the placeholder text with today's draft:
- **Main quote area** → paste the core hadith/ayah/reminder text
- **Attribution line** → paste the source (e.g., "Sahih al-Bukhari" or "Quran 49:10")
- Keep footer (samagi.org · @sama.grandisland) unchanged

### Step 4 — Download & Post
1. In Canva: **Share → Download → PNG**
2. Open Instagram → **Your Story → Add image**
3. Post!

---

## Canva Template Specs
- **Size**: 1080 × 1920 px (Instagram Story)
- **Background**: Deep green `#2D5016` or warm cream `#F5F0E8`
- **Accent / Logo color**: Gold `#C9A84C`
- **Quote font**: Cormorant Garamond or Playfair Display (large, centered)
- **Attribution font**: Lato or Montserrat (small, below quote)
- **Footer**: `samagi.org  ·  @sama.grandisland` (small, bottom)

## Agent Details
- **Name**: SAMA Daily Instagram Story Draft
- **Schedule**: Daily at 8:00 PM ET
- **Output**: Full caption + source + visual suggestion
- **Manage**: https://claude.ai/code/scheduled/trig_01WySGxZzoA7GDmZE83yJoQ1

## Content Themes (Rotated Automatically)
- Hadith on consistency, kindness, neighborliness, generosity
- Quranic reminders (with surah/ayah citation)
- Practical daily Islamic advice
- Calendar-aware reminders (Fridays, Islamic months, etc.)
- Community-focused reminders

## Future Upgrade
When ready: connect Canva MCP at https://claude.ai/settings/connectors
to have the agent generate the graphic automatically.
