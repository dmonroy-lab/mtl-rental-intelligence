#!/usr/bin/env python3
"""
Padly MTL Rental Intelligence — Auto Dashboard Generator v3
Runs every Monday, Wednesday, Friday via GitHub Actions.

2 API calls total (was 12 before — fixes rate limit):
  CALL 1: One big web search — all competitors + global trends together
  CALL 2: Generate the full dashboard HTML with all findings
"""

import json
import os
import time
import anthropic
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
today = datetime.now().strftime("%b %d, %Y")

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

competitors = data["competitors"]
meta = data["meta"]

# Build compact competitor list for the research prompt
comp_list = "\n".join([
    f"- {c['name']} | IG: {c['instagram'].get('url','')} | TikTok: {c['tiktok'].get('url','')}"
    for c in competitors
])

print(f"🔍 CALL 1: Researching all competitors + global trends ({today})...")

# ── CALL 1: One single research call covering everything ────────────────────
research_response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=4000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"""Today is {today}. You are a social media intelligence analyst for Padly, a Montreal apartment rental company.

Do web searches to answer ALL of the following in one response:

PART A — MONTREAL COMPETITOR ACTIVITY (search the top 3 most active ones):
{comp_list}

For the top 3 most active competitors (The Rental Agents, Tatiana Londono, The Agency Montreal):
- What type of content have they posted recently on Instagram/TikTok?
- What formats are they using (Reels, carousels, stories)?
- Any campaigns, promotions, or trends they are following?
- What gaps exist that Padly can exploit?

PART B — GLOBAL VIRAL REAL ESTATE CONTENT (search this now):
- What real estate / apartment rental content is going viral on TikTok and Reels RIGHT NOW in 2026?
- Best performing content formats globally (tours, before/after, day-in-the-life, etc.)
- Top viral hooks/opening lines that get attention
- What are successful rental companies doing in USA, Spain, Latin America that Padly can copy?
- Any trending sounds or formats in real estate content?

Return everything as a structured report. Be specific with examples."""
    }]
)

research_text = ""
for block in research_response.content:
    if hasattr(block, "text"):
        research_text += block.text

print(f"✅ Research done ({len(research_text)} chars). Waiting 10s before next call...")
time.sleep(10)  # Brief pause to respect rate limits

# ── CALL 2: Generate full dashboard HTML ────────────────────────────────────
print("🤖 CALL 2: Generating dashboard HTML...")

comp_data_str = "\n".join([
    f"{c['name']} | Threat:{c['threat']} | IG:{c['instagram']['followers']:,} | TikTok:{c['tiktok']['followers']:,} | FB:{c['facebook']['followers']:,} | {c['notes']}"
    for c in competitors
])

system_prompt = """You are an expert web developer and digital marketing strategist.
You generate complete, self-contained HTML files with embedded CSS and JavaScript.
Output ONLY raw HTML starting with <!DOCTYPE html>. No markdown, no backticks, no explanation."""

user_prompt = f"""Generate a complete competitive intelligence dashboard HTML for Padly — Montreal apartment rental company targeting newcomers/immigrants.

TODAY: {today}
PADLY: @padlylisting IG {meta['padly_ig_followers']:,} | @padly.mtl FB {meta['padly_fb_followers']:,} | TikTok: NOT CREATED (URGENT gap)

COMPETITORS (11 tracked):
{comp_data_str}

LIVE RESEARCH FINDINGS (gathered today via web search):
{research_text}

DESIGN:
- Dark mode default, CSS vars: --bg:#0f0f0f --bg2:#191919 --bg3:#212121 --bg4:#2b2b2b --border:#272727 --txt:#f0f0f0 --txt2:#aaa --txt3:#666 --acc:#7C3AED --acc2:#a78bfa --acc-bg:rgba(124,58,237,.12) --acc-bd:rgba(124,58,237,.3)
- Toggle light mode
- App shell: fixed sidebar 196px left + scrollable main content right
- Mobile <680px: hide sidebar, show bottom nav
- Trilingual toggle EN/FR/ES in sidebar footer

7 TABS (sidebar navigation):

1. 📊 Overview
- 4 KPI cards: total Padly followers, gap to #1 competitor, TikTok opportunity (10/10), content gap score
- URGENT ALERT banner: "TikTok completement libre — Aucun compétiteur ne domine"
- Threat matrix: all 11 competitors as rows with threat color, followers, key weakness

2. 🏢 Competitors
- Expandable card per competitor
- Shows: all platform stats, threat badge (red/orange/gray), recent content found in research, top performing format, weakness, ONE specific recommendation for Padly

3. 📱 Platforms
- 3 sub-tabs: Instagram / TikTok / Facebook
- Ranked table per platform: position, name, followers, est. engagement %, content score /10
- Padly row highlighted in purple with crown emoji

4. 🌍 Global Trends
- "What's viral RIGHT NOW" section from research findings
- Top 5 viral formats with description + why it works
- "Copy This For Padly" — 5 specific ready-to-execute ideas
- Best viral hooks/openers (copy-paste ready)
- Accounts to follow for inspiration

5. 💡 Content Strategy
- Weekly calendar (Mon-Sun) with specific post ideas
- "Post This Tomorrow" — one specific idea with full caption + hashtags
- 3 content pillars for Padly based on competitor gaps
- First 3 video scripts (short, punchy, for Reels/TikTok)

6. 📅 Weekly Intel
- This week's competitive summary (from research)
- What each top competitor did
- 3 opportunities spotted
- This week's action items (numbered list)

7. 📈 My Stats
- Input fields for IG/FB/TikTok followers (saves to localStorage)
- Week-over-week change display
- Simple line sparkline showing growth
- Goals tracker (1K TikTok, 5K IG, etc.)

FLOATING CHAT (💬 FAB bottom-right, z-index 999):
- Opens panel 400px wide 560px tall
- Name: "ARIA — Padly Intelligence"  
- Powered by Anthropic API claude-sonnet-4-6
- If no API key in localStorage('padly_api_key'), show input field to enter it
- System prompt includes all competitor data + research findings
- 3 quick hint buttons: "Post idea today?", "Biggest opportunity?", "What is The Rental Agents doing?"
- Supports file upload (images/PDFs)
- Responds in same language as user (EN/FR/ES)

Make it polished, data-rich, and immediately useful. Every tab must contain real data from the research above.
Output ONLY the complete HTML file. Start with <!DOCTYPE html>."""

dashboard_response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    messages=[{"role": "user", "content": user_prompt}],
    system=system_prompt,
)

html_content = dashboard_response.content[0].text

# Clean markdown fences if present
if html_content.strip().startswith("```"):
    lines = html_content.strip().split("\n")
    html_content = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

# Ensure starts with DOCTYPE
if not html_content.strip().startswith("<!"):
    idx = html_content.find("<!DOCTYPE")
    if idx >= 0:
        html_content = html_content[idx:]

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Dashboard generated! ({len(html_content):,} chars)")
print(f"📅 {today} — 2 API calls used — ready on GitHub Pages")
