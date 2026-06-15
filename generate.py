#!/usr/bin/env python3
"""
Padly MTL Rental Intelligence — Auto Dashboard Generator
Runs every Monday, Wednesday, Friday via GitHub Actions.
Reads data.json → calls Claude API → writes updated index.html
"""

import json
import os
import anthropic
from datetime import datetime

# ── Load competitor data ────────────────────────────────────────────────────
with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

today = datetime.now().strftime("%b %d, %Y")
competitors = data["competitors"]
meta = data["meta"]
weekly = data.get("weekly_intel", [{}])[0]

# ── Build prompt for Claude ─────────────────────────────────────────────────
comp_summary = "\n".join([
    f"- {c['name']} | Threat: {c['threat']} | IG: {c['instagram']['followers']:,} | TikTok: {c['tiktok']['followers']:,} | FB: {c['facebook']['followers']:,} | Notes: {c['notes']}"
    for c in competitors
])

weekly_highlights = "\n".join([f"  • {h}" for h in weekly.get("highlights", [])])

system_prompt = """You are an expert web developer specializing in competitive intelligence dashboards.
You generate complete, self-contained HTML files with embedded CSS and JavaScript.
You output ONLY raw HTML — no markdown, no backticks, no explanation. Just the HTML file content starting with <!DOCTYPE html>."""

user_prompt = f"""Generate a complete, beautiful competitive intelligence dashboard HTML file for Padly, a Montreal apartment rental company targeting newcomers/immigrants.

Today's date: {today}
Padly Instagram followers: {meta['padly_ig_followers']:,}
Padly Facebook followers: {meta['padly_fb_followers']:,}
Padly TikTok followers: {meta['padly_tiktok_followers']:,} (NOT CREATED YET — urgent gap)

COMPETITOR DATA (11 companies tracked):
{comp_summary}

WEEKLY INTEL ({weekly.get('week', today)}):
{weekly_highlights}

DESIGN REQUIREMENTS:
- Dark mode by default (toggle to light mode)
- Sidebar navigation (196px wide, fixed) + main scrollable content area
- App-shell layout: sidebar left, content right, full viewport height
- CSS variables for theming (--bg, --txt, --acc: #7C3AED purple, etc.)
- Mobile responsive: sidebar hidden on <680px, bottom nav appears
- Trilingual toggle: EN / FR / ES

TABS (6 total):
1. 📊 Overview — KPI cards (Padly vs competitors), key opportunity callouts, threat matrix
2. 🏢 Competitors — Expandable cards per competitor with all platform stats, threat level badge, notes
3. 📱 By Platform — Instagram ranking table, TikTok ranking table, Facebook ranking table (Padly highlighted in each)
4. 📰 Weekly Intel — This week's highlights, what competitors posted, opportunities spotted
5. 💡 Content Ideas — 6-8 specific content ideas based on competitor gaps (what nobody is doing that Padly should)
6. 📈 My Stats — Padly's own follower evolution tracker (simple manual-input interface)

KEY INSIGHTS TO HIGHLIGHT (show prominently):
- TikTok is completely open — NO competitor dominates it
- No competitor has done influencer collaborations
- Padly's opportunity: be the first rental brand to dominate Montreal social media
- The Rental Agents is the main threat (11K IG, active TikTok)

FLOATING CHAT BUTTON (💬 bottom-right):
- Opens a chat panel powered by Anthropic API
- System prompt: expert in Montreal real estate, digital marketing, neuromarketing (Cialdini/Kahneman)
- Has all competitor data pre-loaded
- File upload support (images, PDFs)
- Trilingual responses
- Uses model: claude-sonnet-4-6
- API call pattern: fetch('https://api.anthropic.com/v1/messages', POST, no auth header needed from browser — NOTE: for demo purposes, show a "Connect API Key" input field if no key is stored in localStorage)

PADLY BRAND:
- Instagram: @padlylisting
- Facebook: @padly.mtl  
- Colors: purple accent (#7C3AED), dark background (#0f0f0f)
- Tagline: "Le premier à dominer les réseaux sociaux de la location à Montréal"

Generate the COMPLETE HTML file. Make it polished, professional, and data-rich. Include all 6 tabs fully functional with real data from the competitors above. Output ONLY the HTML, nothing else."""

# ── Call Claude API ─────────────────────────────────────────────────────────
print(f"🤖 Calling Claude API to generate dashboard for {today}...")
client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

message = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    messages=[{"role": "user", "content": user_prompt}],
    system=system_prompt,
)

html_content = message.content[0].text

# Clean up in case Claude adds markdown fences
if html_content.startswith("```"):
    lines = html_content.split("\n")
    html_content = "\n".join(lines[1:-1] if lines[-1] == "```" else lines[1:])

# ── Write output ────────────────────────────────────────────────────────────
with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Dashboard generated successfully! ({len(html_content):,} chars)")
print(f"📅 Updated: {today}")
