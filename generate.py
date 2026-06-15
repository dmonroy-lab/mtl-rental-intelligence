#!/usr/bin/env python3
"""
Padly MTL Rental Intelligence — Auto Dashboard Generator v4
2 API calls total, rate-limit safe.
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

comp_list = "\n".join([
    f"- {c['name']} | IG: {c['instagram'].get('url','')} | TikTok: {c['tiktok'].get('url','')}"
    for c in competitors[:3]  # Only top 3 to save tokens
])

print(f"🔍 CALL 1: Web research ({today})...")

# ── CALL 1: Research ────────────────────────────────────────────────────────
research_response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=2000,
    tools=[{"type": "web_search_20250305", "name": "web_search"}],
    messages=[{
        "role": "user",
        "content": f"""Today is {today}. You are a social media analyst for Padly, a Montreal rental company.

Search and answer briefly:

1. What content are these Montreal competitors posting lately on Instagram/TikTok?
{comp_list}

2. What real estate content is viral globally on TikTok/Reels in 2026?

3. What are 5 specific content ideas Padly can copy from global trends?

Be concise. Max 1500 words total."""
    }]
)

research_text = ""
for block in research_response.content:
    if hasattr(block, "text"):
        research_text += block.text

# Trim to 3000 chars max to stay under token limits
research_text = research_text[:3000]

print(f"✅ Research done ({len(research_text)} chars). Sleeping 65s to reset rate limit...")
time.sleep(65)  # Wait 65 seconds to fully reset the per-minute rate limit

# ── CALL 2: Generate dashboard ──────────────────────────────────────────────
print("🤖 CALL 2: Generating dashboard HTML...")

comp_data_str = "\n".join([
    f"{c['name']} | Threat:{c['threat']} | IG:{c['instagram']['followers']:,} | TikTok:{c['tiktok']['followers']:,} | FB:{c['facebook']['followers']:,} | {c['notes']}"
    for c in competitors
])

system_prompt = """You are an expert web developer. Generate complete self-contained HTML files.
Output ONLY raw HTML starting with <!DOCTYPE html>. No markdown, no backticks."""

user_prompt = f"""Build a competitive intelligence dashboard for Padly (Montreal rental company, targets newcomers).

DATE: {today}
PADLY: @padlylisting IG {meta['padly_ig_followers']:,} | @padly.mtl FB {meta['padly_fb_followers']:,} | TikTok: NOT CREATED YET

COMPETITORS:
{comp_data_str}

RESEARCH FINDINGS TODAY:
{research_text}

DESIGN: Dark (#0f0f0f), purple accent #7C3AED, CSS vars (--bg --bg2 --bg3 --border --txt --txt2 --txt3 --acc --acc2 --acc-bg --acc-bd), light mode toggle, app-shell layout (sidebar 196px fixed + scrollable main), mobile responsive (hide sidebar <680px, show bottom nav), EN/FR/ES toggle.

7 SIDEBAR TABS:
1. 📊 Overview — KPI cards (Padly followers, gap to #1, TikTok opportunity 10/10), URGENT alert banner "TikTok libre!", threat matrix table all 11 competitors
2. 🏢 Competitors — expandable card per competitor: stats, threat badge, content analysis from research, weakness, 1 recommendation for Padly
3. 📱 Platforms — 3 sub-tabs (IG/TikTok/FB), ranked table each platform, Padly highlighted purple
4. 🌍 Global Trends — viral formats right now, "Copy For Padly" section with 5 ready ideas, best hooks copy-paste ready
5. 💡 Content Strategy — weekly calendar Mon-Sun, "Post Tomorrow" with full caption+hashtags, 3 video scripts
6. 📅 Weekly Intel — competitor activity this week, 3 opportunities, action items list
7. 📈 My Stats — input fields IG/FB/TikTok (localStorage), growth tracker, goals

FLOATING CHAT 💬 (bottom-right FAB, purple):
- Panel 400x560px, "ARIA — Padly Intelligence"
- Anthropic API claude-sonnet-4-6
- localStorage key 'padly_api_key' — show input if missing
- 3 quick hints: "Post idea today?" / "Biggest opportunity?" / "Rental Agents activity?"
- All competitor data in system prompt

Output ONLY complete HTML. Start with <!DOCTYPE html>."""

dashboard_response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    messages=[{"role": "user", "content": user_prompt}],
    system=system_prompt,
)

html_content = dashboard_response.content[0].text

# Clean markdown fences
if "```" in html_content[:100]:
    lines = html_content.split("\n")
    start = 1 if lines[0].startswith("```") else 0
    end = -1 if lines[-1].strip() == "```" else len(lines)
    html_content = "\n".join(lines[start:end])

# Ensure DOCTYPE
if not html_content.strip().startswith("<!"):
    idx = html_content.find("<!DOCTYPE")
    if idx >= 0:
        html_content = html_content[idx:]

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Done! ({len(html_content):,} chars) — Live at GitHub Pages")
