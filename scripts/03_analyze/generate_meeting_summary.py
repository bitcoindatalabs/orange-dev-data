import os
import sys
import json
import hashlib
import time
import re
from datetime import datetime
import urllib.request
import urllib.error

INPUT_FILE = "data/raw/irc_meetings.json"
OUTPUT_FILE = "data/raw/meeting_summaries.json"
HAS_GENAI = True

# Load API keys
env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
if os.path.exists(env_path):
    with open(env_path, "r") as f:
        for line in f:
            if "=" in line and not line.strip().startswith("#"):
                key, val = line.strip().split("=", 1)
                os.environ[key.strip()] = val.strip().strip("'").strip('"')

TARGET_MODEL = os.environ.get('GEMINI_TARGET_MODEL', 'gemini-2.5-flash')
api_keys = []
for k, v in os.environ.items():
    if k.startswith("GEMINI_API_KEY") and v.strip():
        api_keys.append(v.strip())

def clean_narrative_fluff(text: str) -> str:
    """Strip generic corporate filler and meta-commentary from narrative summaries."""
    if not text:
        return ""
    import re
    banned_substrings = [
        "effort is critical",
        "effort is crucial",
        "work is vital",
        "essential for maintaining",
        "crucial for maintaining",
        "convened to discuss",
        "development team convened",
        "strategic consolidation",
        "fostering collaboration",
        "cadence and integrating",
    ]
    paragraphs = text.split("\n\n")
    cleaned_paras = []
    for para in paragraphs:
        sentences = re.split(r'(?<=[.!?])\s+', para.strip())
        good_sentences = []
        for s in sentences:
            s_clean = s.strip()
            if not s_clean:
                continue
            if any(b.lower() in s_clean.lower() for b in banned_substrings):
                continue
            good_sentences.append(s_clean)
        if good_sentences:
            cleaned_paras.append(" ".join(good_sentences))
    return "\n\n".join(cleaned_paras)


def generate_meeting_summary():
    if not HAS_GENAI or not api_keys:
        print("Warning: Gemini API not configured. Skipping meeting summary.")
        return

    if not os.path.exists(INPUT_FILE):
        print(f"Error: {INPUT_FILE} not found.")
        return

    with open(INPUT_FILE, 'r') as f:
        meetings = json.load(f)

    existing_summaries = []
    if os.path.exists(OUTPUT_FILE):
        try:
            with open(OUTPUT_FILE, 'r') as f:
                existing_summaries = json.load(f)
        except:
            pass

    existing_dict = {m['date']: m for m in existing_summaries}
    new_summaries = []
    changed = False

    # Bots to ignore in participant counts
    bots = {'bitcoin-git', 'bitcoin-merge', 'gribble', 'lightningbot', 'lnd-git', 'corebot'}

    for meeting in meetings:
        date = meeting['date']
        messages = meeting.get('messages', [])
        
        # Calculate hash to detect changes
        text_hash = hashlib.md5(json.dumps(messages, sort_keys=True).encode('utf-8')).hexdigest()
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        existing = existing_dict.get(date)
        if date == today_str:
            needs_update = not (existing and existing.get('_text_hash') == text_hash and existing.get('card_topics') and existing.get('spotlight_debate'))
        else:
            needs_update = not (existing and existing.get('_text_hash') == text_hash)

        if not needs_update:
            new_summaries.append(existing)
            continue
            
        print(f"Processing meeting for {date}...")
        changed = True
        
        # Count total attendees vs substantive discussion participants
        greetings = {'hi', 'hello', 'hey', 'here', 'yo', 'gm', 'greetings', 'o/', '\\o', '👋', 'morning', 'afternoon'}
        attendees = set()
        discussion_counts = {}
        for m in messages:
            sender = m.get('sender', '').strip()
            if not sender or sender in bots:
                continue
            attendees.add(sender)
            payload = m.get('payload', '').strip().lower()
            clean_payload = payload.strip('.!?:; ')
            # Exclude simple roll-call greetings from discussion participation
            if clean_payload in greetings or clean_payload.startswith('hi ') or clean_payload.startswith('hello '):
                continue
            discussion_counts[sender] = discussion_counts.get(sender, 0) + 1
                
        participant_count = len(attendees)
        # Senders who actively contributed messages to the technical discussion
        active_discussion_nicks = sorted(discussion_counts.keys(), key=lambda k: discussion_counts[k], reverse=True)
        top_nicks = active_discussion_nicks[:6]
        
        # Construct log_text dynamically for LLM consumption
        raw_text_lines = []
        for m in messages:
            ts = m.get("timestamp", "")
            time_str = ts.split("T")[1][:5] if "T" in ts else ""
            sender = m.get("sender", "")
            payload = m.get("payload", "")
            raw_text_lines.append(f"{time_str} < {sender}> {payload}")
            
        log_text = "\n".join(raw_text_lines)
        if len(log_text) > 30000:
            log_text = log_text[-30000:]
            
        prompt = f"""You are a senior Bitcoin Core engineer writing an executive technical debrief of an IRC engineering sync for Bitcoin Core developers and technical Bitcoiners.
The meeting took place on {date}.

IRC Log Transcript:
{log_text}

Generate a 3-layer technical debrief with ZERO corporate fluff.

LAYER 1: WEBSITE ARCHIVE RECORD (For meetings.html — Technical archive)
1. topics_discussed: 4–6 substantive, factual technical summaries covering every distinct topic/WG update.
   - Format: "[Topic / WG]: [Factual record of status, contributors involved, technical specifics]".
   - Retain developer handles, PR numbers, milestone numbers. Zero fluff. No raw HTTP URLs.
2. decisions_made: Technical decisions / lead transitions (empty array if none).
3. action_items: Concrete next steps, testing calls, or review requests (empty array if none).
4. mentioned_prs: Integer array of PR/issue numbers explicitly discussed.

LAYER 2: EXECUTIVE SOCIAL CARD (For meeting-card.html — High-density visual card)
5. card_topics: Exactly 5 to 6 substantive bullet points (120–180 chars each) covering all active updates.
   - Format: "[Topic / WG]: [Crisp factual update naming developers, tools, branches, and PRs]".
   - Skip empty "no update" reports. Include real debates and progress. Zero raw URLs.
6. spotlight_debate: A 1–2 sentence highlight (under 180 chars) on the most significant technical debate or proposal from the sync.
   - Format: "[Topic / Debate]: [What was proposed and what technical concerns or tradeoffs were raised]".
7. referenced_artifacts: Key milestones, git branches, platforms, or tools discussed. Array of objects:
   [{{"label": "Milestone #84", "icon": "flag"}}, {{"label": "Branch: qt6", "icon": "code-branch"}}, {{"label": "mutanthub.space", "icon": "globe"}}, {{"label": "Fuzzamoto Bot", "icon": "robot"}}]

LAYER 3: NARRATIVE SOCIAL BRIEFING (For LinkedIn & Nostr long-form posts)
8. narrative_summary: A 150–200 word technical engineering briefing across exactly 3 paragraphs (separated by blank lines \\n\\n).
   - STRICT ZERO FLUFF RULES: Write like a Bitcoin Optech or Linux kernel newsletter editor. NO PR/HR language.
     * BANNED: "convened", "crucial for maintaining development velocity", "collaborative effort", "strategic consolidation", "pivotal", "pleased to announce", "critical for maintaining the release cadence", "velocity", "cadence".
     * NO META-COMMENTARY: NEVER comment on why something is important, vital, or critical. State ONLY raw technical facts: what PRs need review, what code was merged or proposed, who spoke, what decisions were made, and what tradeoffs were debated.
     * Sentence 1 must state the technical focus immediately (e.g. "Bitcoin Core 32.0 release preparation centered on resolving outstanding backports for milestone #84, with dzxzg requesting developer review.").
   - Paragraph 1 (Release Milestone): Immediate release status for 32.0, backport issues on milestone #84, and specific testing needed.
   - Paragraph 2 (Tooling & Architecture): Status across GUI (pseudoramdom overhaul, qt6 branch, bitcoincore.app binaries), mutation testing (mutanthub.space launched by brunoerg), and fuzzing (eugenesiegel PR bot proposal).
   - Paragraph 3 (Decisions & Debates): Leadership change in Benchmarking WG (andrewtoth stepping down as lead) and the debate over willcl-ark's proposal for automated AI reviews (ralph bot), noting signal-to-noise concerns raised by andrewtoth and abubakarsadiq.
9. x_priority_takeaway: Single engineering takeaway or call to action under 70 chars (e.g. "Help needed on Bitcoin Core 32.0 milestone items (#84).")
10. x_bullet_points: 2-3 concise bullets under 45 chars each.

Output strictly valid JSON matching this schema:
{{
    "topics_discussed": ["..."],
    "decisions_made": ["..."],
    "action_items": ["..."],
    "mentioned_prs": [84],
    "card_topics": ["..."],
    "spotlight_debate": "...",
    "referenced_artifacts": [{{"label": "...", "icon": "..."}}],
    "narrative_summary": "...",
    "x_priority_takeaway": "...",
    "x_bullet_points": ["..."]
}}
Do NOT use markdown wrappers. Output only JSON.
"""

        success = False
        for key_index, current_key in enumerate(api_keys):
            if success:
                break
                
            for attempt in range(2):
                try:
                    url = f"https://generativelanguage.googleapis.com/v1beta/models/{TARGET_MODEL}:generateContent?key={current_key}"
                    payload = json.dumps({
                        "contents": [{"parts": [{"text": prompt}]}],
                        "generationConfig": {"temperature": 0.1}
                    }).encode('utf-8')
                    
                    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json'})
                    with urllib.request.urlopen(req) as response:
                        result = json.loads(response.read().decode('utf-8'))
                        
                        text = result['candidates'][0]['content']['parts'][0]['text'].strip()
                        
                        if text.startswith('```json'):
                            text = text[7:-3]
                        elif text.startswith('```'):
                            text = text[3:-3]
                        
                        parsed = json.loads(text.strip())
                        
                        narrative = clean_narrative_fluff(parsed.get("narrative_summary", ""))
                        card_topics = parsed.get("card_topics", [])
                        if not card_topics:
                            card_topics = [t[:115] + "..." if len(t) > 118 else t for t in parsed.get("topics_discussed", [])[:3]]

                        summary_obj = {
                            "date": date,
                            "url": meeting.get("url", ""),
                            "participant_count": participant_count,
                            "key_participants": top_nicks,
                            "active_participants": active_discussion_nicks,
                            "topics_discussed": parsed.get("topics_discussed", []),
                            "decisions_made": parsed.get("decisions_made", []),
                            "action_items": parsed.get("action_items", []),
                            "mentioned_prs": parsed.get("mentioned_prs", []),
                            "card_topics": card_topics,
                            "spotlight_debate": parsed.get("spotlight_debate", ""),
                            "referenced_artifacts": parsed.get("referenced_artifacts", []),
                            "narrative_summary": narrative,
                            "x_priority_takeaway": parsed.get("x_priority_takeaway", ""),
                            "x_bullet_points": parsed.get("x_bullet_points", []),
                            "linkedin_context": narrative or parsed.get("linkedin_context", ""),
                            "_text_hash": text_hash
                        }
                        
                        new_summaries.append(summary_obj)
                        success = True
                        time.sleep(1)
                        break

                except urllib.error.HTTPError as e:
                    if e.code in (403, 404, 429):
                        print(f"Key {key_index + 1} hit {e.code}. Rotating to next key...")
                        break 
                    else:
                        print(f"Error on Key {key_index + 1} (attempt {attempt+1}): {e}")
                        time.sleep(2)
                except Exception as e:
                    print(f"Unexpected Error on Key {key_index + 1} (attempt {attempt+1}): {e}")
                    time.sleep(2)
                    
        if not success:
            if existing and existing.get("card_topics"):
                print(f"Failed to refresh summary for {date}. Retaining existing valid summary.")
                new_summaries.append(existing)
            else:
                raise RuntimeError(f"Failed to generate summary for {date}. All {len(api_keys)} Gemini API keys failed.")

    if changed:
        # Sort by date descending
        new_summaries.sort(key=lambda x: x['date'], reverse=True)
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w') as f:
            json.dump(new_summaries, f, indent=2)
        print(f"Successfully generated and saved meeting summaries to {OUTPUT_FILE}")
    else:
        print("All meeting summaries are up to date.")

if __name__ == "__main__":
    generate_meeting_summary()
