#!/usr/bin/env python3
"""
Padly MTL Rental Intelligence — Auto Dashboard Generator v2
Runs every Monday, Wednesday, Friday via GitHub Actions.

PHASE 1: Claude searches the web for:
  - Latest posts/content from each competitor
  - Global viral real estate content trends
  - What's working in other countries

PHASE 2: Claude generates the full dashboard HTML with all findings.
"""

import json
import os
import anthropic
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
today = datetime.now().strftime("%b %d, %Y")

with open("data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

competitors = data["competitors"]
meta = data["meta"]

print(f"🔍 PHASE 1: Researching competitors and global trends ({today})...")

# ── PHASE 1: Web research for each competitor ───────────────────────────────
def research_competitor(comp):
    name = comp["name"]
    ig_url = comp["instagram"].get("url", "")
    tt_url = comp["tiktok"].get("url", "")
    print(f"   🔎 Researching: {name}")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""Research the latest social media activity for "{name}", a Montreal real estate/rental company.

Search for:
1. Their most recent Instagram posts (what type of content, topics, format)
2. Their most recent TikTok videos (what went viral, what flopped)
3. Their engagement patterns (what gets the most likes/comments/shares)
4. Any campaigns or promotions they are running right now

Instagram: {ig_url}
TikTok: {tt_url}

Return a structured summary with:
- RECENT_CONTENT: What they posted in the last 2 weeks (type, topic, format)
- TOP_PERFORMING: Their best performing content style
- WEAKNESSES: What they are NOT doing (gaps Padly can exploit)
- ENGAGEMENT_RATE: Estimated engagement rate
- RECOMMENDATION: One specific thing Padly should copy or avoid from this competitor

Be specific and actionable. If you can't find specific posts, say so and note general patterns."""
        }]
    )
    # Extract text from response
    result = ""
    for block in response.content:
        if hasattr(block, "text"):
            result += block.text
    return result

# ── PHASE 2: Global viral trends research ───────────────────────────────────
def research_global_trends():
    print("   🌍 Researching global viral real estate trends...")
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": f"""Today is {today}. Research what real estate and apartment rental content is going viral RIGHT NOW globally on TikTok, Instagram Reels, and YouTube Shorts.

Search for:
1. Most viral real estate TikTok videos this week (any country)
2. Best performing apartment tour formats on Instagram Reels right now
3. What rental/housing content is getting millions of views globally
4. Successful real estate social media strategies from USA, UK, Australia, Spain, Latin America
5. Any viral hooks, formats, or trends in property content (before/after, day in the life, apartment hunting, etc.)

Return:
- TOP_VIRAL_FORMATS: The 5 content formats getting the most views globally right now
- VIRAL_HOOKS: The best opening hooks/lines that are working
- COPY_FOR_PADLY: 5 specific content ideas Padly can copy immediately (adapted for Montreal)
- TRENDING_SOUNDS: Any trending audio/sounds being used in real estate content
- BEST_EXAMPLES: Specific accounts or videos that are crushing it right now

Focus on what can be directly adapted for a Montreal rental company targeting newcomers and immigrants."""
        }]
    )
    result = ""
    for block in response.content:
        if hasattr(block, "text"):
            result += block.text
    return result

# Run research
competitor_research = {}
for comp in competitors:
    competitor_research[comp["id"]] = research_competitor(comp)

global_trends = research_global_trends()

print("✅ Research complete. Building intelligence report...")

# ── PHASE 3: Generate full dashboard HTML ───────────────────────────────────
print("🤖 PHASE 2: Generating dashboard with all intelligence...")

comp_data_str = "\n\n".join([
    f"=== {c['name']} (Threat: {c['threat']}) ===\n"
    f"IG: {c['instagram']['followers']:,} followers | TikTok: {c['tiktok']['followers']:,} | FB: {c['facebook']['followers']:,}\n"
    f"Notes: {c['notes']}\n"
    f"RESEARCH FINDINGS:\n{competitor_research.get(c['id'], 'No data')}"
    for c in competitors
])

system_prompt = """You are an expert web developer and digital marketing strategist specializing in competitive intelligence dashboards.
You generate complete, self-contained HTML files with embedded CSS and JavaScript.
You output ONLY raw HTML — no markdown, no backticks, no explanation. Start directly with <!DOCTYPE html>."""

user_prompt = f"""Generate a complete, beautiful competitive intelligence dashboard for Padly — a Montreal apartment rental company targeting newcomers/immigrants.

Today: {today}
Padly IG: @padlylisting ({meta['padly_ig_followers']:,} followers)
Padly FB: @padly.mtl ({meta['padly_fb_followers']:,} followers)
Padly TikTok: NOT CREATED YET — CRITICAL OPPORTUNITY

=== LIVE COMPETITOR RESEARCH (just gathered from web) ===
{comp_data_str}

=== GLOBAL VIRAL TRENDS (just gathered from web) ===
{global_trends}

=== DASHBOARD DESIGN ===
- Dark mode default (#0f0f0f bg, #7C3AED purple accent), toggle to light
- Fixed sidebar 196px + main scrollable content area (app-shell layout)
- CSS variables: --bg, --bg2, --bg3, --border, --txt, --txt2, --txt3, --acc: #7C3AED, --acc2: #a78bfa, --acc-bg: rgba(124,58,237,.12), --acc-bd: rgba(124,58,237,.3)
- Mobile: sidebar hidden <680px, bottom nav bar appears
- Trilingual toggle EN/FR/ES (affects all UI labels)

=== 7 TABS ===

TAB 1 — 📊 Overview
- 4 KPI cards: Padly followers total, #1 competitor gap, TikTok opportunity score, content gap score
- Big "OPPORTUNITY ALERT" banner: TikTok completely open, no competitor has influencers
- Threat matrix table: all 11 competitors ranked by threat
- Last updated timestamp

TAB 2 — 🏢 Competitor Analysis
- One expandable card per competitor
- Each card shows: platform stats, threat badge, RECENT CONTENT (from research), TOP PERFORMING content, WEAKNESSES, specific recommendation for Padly
- Color-code by threat: red=high, orange=medium, gray=low

TAB 3 — 📱 Platform Rankings
- Instagram table: rank all competitors + Padly (highlighted in purple), followers, est. engagement rate, content quality score
- TikTok table: same, note which ones have 0 (opportunity)
- Facebook table: same

TAB 4 — 🌍 Global Viral Trends
- THIS IS THE KEY NEW TAB — populate entirely from the global trends research
- Show: Top 5 viral content formats right now
- Show: Best viral hooks/openers
- Show: "Copy This For Padly" — 5 specific ideas with full description
- Show: Trending sounds/audio
- Show: Best accounts to follow for inspiration
- Make this tab actionable and inspiring

TAB 5 — 💡 Content Strategy
- Weekly content calendar recommendation (Mon-Sun)
- "What to post tomorrow" section — specific idea based on what's trending
- Content pillars for Padly (based on competitor gaps)
- Scripts/captions ideas for first 3 videos
- Hashtag strategy

TAB 6 — 📅 Weekly Intel
- Auto-generated summary of what changed this week
- Competitor activity log
- Opportunities spotted
- "This week's action items for Padly"

TAB 7 — 📈 My Stats
- Simple tracker: Padly's follower count per platform
- Week-over-week growth
- Manual input fields to update numbers
- Progress toward goals

=== FLOATING AI ASSISTANT (💬 FAB bottom-right) ===
- Chat panel, 420px wide, 580px tall
- AI avatar, "ARIA — Padly Intelligence"
- Knows all competitor data and research findings
- Anthropic API (claude-sonnet-4-6), no auth header in browser
- Show API key input field if not set (stores in localStorage as 'padly_api_key')
- Preset questions: "What should I post today?", "What's my biggest opportunity?", "What is The Rental Agents doing?"
- Trilingual, file upload support

=== IMPORTANT ===
- ALL research data must appear in the dashboard (don't summarize it away)
- TAB 4 (Global Trends) should feel like a live feed of inspiration
- Every recommendation must be SPECIFIC and ACTIONABLE for Padly
- Make the "Copy This For Padly" section the most useful thing in the whole dashboard

Output ONLY the complete HTML. Nothing else."""

response = client.messages.create(
    model="claude-sonnet-4-6",
    max_tokens=16000,
    messages=[{"role": "user", "content": user_prompt}],
    system=system_prompt,
)

html_content = response.content[0].text

# Clean markdown fences if present
if "```" in html_content[:50]:
    lines = html_content.split("\n")
    html_content = "\n".join(lines[1:])
    if html_content.strip().endswith("```"):
        html_content = "\n".join(html_content.split("\n")[:-1])

# Ensure starts with DOCTYPE
if not html_content.strip().startswith("<!"):
    idx = html_content.find("<!DOCTYPE")
    if idx > 0:
        html_content = html_content[idx:]

with open("index.html", "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"✅ Dashboard generated! ({len(html_content):,} chars)")
print(f"📅 {today} | Competitors researched: {len(competitors)} | Tabs: 7")
