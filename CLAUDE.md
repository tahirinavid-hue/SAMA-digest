# SAMA AI Workspace

AI-assisted workspace for **Service and Mercy Alliance (SAMA)**, a Muslim community masjid at 1822 Huth Rd, Grand Island, NY 14072.

- **Website**: https://www.samagi.org (repo: `masjid-site/`, deployed via Vercel)
- **Instagram**: @sama.grandisland
- **Donation**: Zeffy (sadaqa), LaunchGood (building fund)

## Project Structure

```
agents/           — Agent prompt definitions (orchestrator, social media, grants, etc.)
scripts/          — Python automation (digest, email, JotForm, image processing)
context/          — Standing org context: organization.md, goals.md
masjid-site/      — Website submodule (push to both master AND main branches)
content-drafts/   — Draft posts and website copy
social-media/     — IG strategy and scheduling
events/           — Event announcements and recaps
grants/           — Grant research and proposals
meetings/         — Board meeting notes and transcripts
assets/           — Images, logos, design files
```

## Key Commands

```bash
# Activate Python environment
source .venv/Scripts/activate   # Windows/Git Bash

# Run weekly community digest (only sends on Mondays)
python scripts/run_daily.py

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables (in .env)

- `ANTHROPIC_API_KEY` — Claude API for community digest
- `RESEND_API_KEY` — Email delivery via Resend
- `JOTFORM_API_KEY` — JotForm API for form management

## Conventions

- **Website deploys**: After editing `masjid-site/`, push submodule pointer to both `master` and `main` branches.
- **Scripts**: All Python automation lives in `scripts/`. Don't leave one-off scripts at the project root.
- **Tests**: Test files go in `tests/`. Run with `python -m pytest tests/`.
- **Agent definitions**: Markdown files in `agents/` with role, prompt template, and usage instructions.
- **Tone**: SAMA's voice is warm, inclusive, and community-first. Apply this to any generated content.
- **Secrets**: Never commit `.env`. The `.gitignore` already excludes it.
