import os
import re
import json
import logging
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

VOICE_SYSTEM_PROMPT = """You are CleanConnect Voice AI, an intelligent, helpful, and friendly voice assistant for CleanConnect (a civic cleanliness and waste management platform).
Citizens talk to you to:
1. Ask questions about civic cleanliness, waste segregation (wet waste, dry waste, e-waste, hazardous waste), and Swachh Bharat cleanliness mission.
2. Ask how to report garbage or civic issues on CleanConnect.
3. Check the status of their submitted reports or inquiries.
4. Report garbage or sanitation problems by voice (e.g., "There is a garbage dump near Gandhi Chowk").

STRICT RULES FOR YOUR RESPONSE:
- Keep answers concise, natural, and conversational (1 to 3 short sentences maximum), because it will be spoken aloud by browser text-to-speech.
- DO NOT use any markdown formatting: NO asterisks (*), NO markdown links, NO hashtags (#), NO bullet points, NO emojis.
- If the citizen wants to report an issue or says there is trash/garbage at a specific place, guide them to upload a photo and at the very end of your response, output an action JSON on a single line starting with "ACTION:":
  ACTION: {"type": "fill_report", "location": "<extracted location>", "category": "<one of: garbage_dumps, dead_animals, dirty_public_toilets, sweeping_not_done, uncleaned_dustbins, other_issue>", "description": "<short description>"}
- If no action is needed, DO NOT include the ACTION line.
- You can understand and respond in English and Hinglish (Hindi written in Latin script) as preferred by the user.
"""

def _fallback_voice_response(query: str, reports_summary: str = "") -> dict[str, Any]:
    q = query.lower()
    
    # 1. Report waste intent
    if any(k in q for k in ["report", "garbage at", "trash at", "waste at", "dirty toilet", "kooda", "kachra"]):
        location = ""
        category = "garbage_dumps"
        
        if "toilet" in q:
            category = "dirty_public_toilets"
        elif "dead animal" in q:
            category = "dead_animals"
        elif "dustbin" in q:
            category = "uncleaned_dustbins"
        elif "sweep" in q:
            category = "sweeping_not_done"
            
        # Try extracting location after 'at' or 'near'
        match = re.search(r'(?:at|near|in)\s+([a-zA-Z0-9\s]{3,30})', query, re.IGNORECASE)
        if match:
            location = match.group(1).strip()
            
        reply = f"I have prepared the report form for {location or 'your location'}. Please take a photo of the area and click Submit Report."
        return {
            "reply": reply,
            "action": {
                "type": "fill_report",
                "location": location,
                "category": category,
                "description": f"Reported via Voice Assistant: {query}"
            }
        }
        
    # 2. Status inquiry
    if any(k in q for k in ["status", "track", "my report", "complaint", "kya hua"]):
        if reports_summary:
            return {"reply": f"Here is the status of your recent report: {reports_summary}", "action": None}
        return {"reply": "You can view all your active reports in the My Reports tab or give me your report tracking reference number.", "action": None}
        
    # 3. Segregation / Recycling advice
    if any(k in q for k in ["wet", "dry", "segregat", "recycle", "green bin", "blue bin"]):
        return {
            "reply": "Green bins are for biodegradable wet waste like food and leaves. Blue bins are for dry recyclable waste like plastic, paper, and metal cans.",
            "action": None
        }
        
    # 4. Points & Rewards
    if any(k in q for k in ["point", "reward", "coin"]):
        return {
            "reply": "You earn green points whenever your verified cleanliness report is cleaned by our sanitation team. Points can be tracked on your profile.",
            "action": None
        }
        
    # 5. General greeting
    return {
        "reply": "Hello! I am CleanConnect Voice AI. You can ask me to file a waste report, check your complaint status, or learn waste segregation rules.",
        "action": None
    }


def process_voice_query(query: str, user_id: Optional[str] = None, user_reports: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
    """
    Processes a natural language voice query and returns:
    {
        "reply": "Spoken text response",
        "action": { "type": "fill_report", ... } or None
    }
    """
    clean_query = query.strip()
    if not clean_query:
        return {"reply": "I did not hear anything. Please try speaking again.", "action": None}
        
    # Build report context if relevant
    report_context = ""
    if user_reports:
        # Check if query matches specific report id
        for rep in user_reports:
            rep_id = rep.get("report_id", "")
            if rep_id and (rep_id.lower() in clean_query.lower() or rep_id.split("-")[-1].lower() in clean_query.lower()):
                report_context = f"Report {rep_id} is currently {rep.get('status', 'pending')} (Category: {rep.get('category', 'waste')})."
                break
        if not report_context and len(user_reports) > 0:
            latest = user_reports[0]
            report_context = f"User's latest report is {latest.get('report_id')}, status: {latest.get('status')}."

    # Try Gemini 2.5 Flash
    if GEMINI_API_KEY:
        try:
            from google import genai
            client = genai.Client(api_key=GEMINI_API_KEY)
            
            prompt_parts = [VOICE_SYSTEM_PROMPT]
            if report_context:
                prompt_parts.append(f"Context about user's reports: {report_context}")
            prompt_parts.append(f"User Query: {clean_query}")
            
            full_prompt = "\n\n".join(prompt_parts)
            
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=full_prompt
            )
            raw_text = response.text.strip()
            
            # Check for ACTION line
            action = None
            reply = raw_text
            
            if "ACTION:" in raw_text:
                parts = raw_text.split("ACTION:", 1)
                reply = parts[0].strip()
                action_str = parts[1].strip()
                try:
                    action = json.loads(action_str)
                except Exception:
                    # Match json object with regex
                    m = re.search(r'\{.*\}', action_str)
                    if m:
                        try:
                            action = json.loads(m.group(0))
                        except Exception:
                            action = None
                            
            # Clean reply of any residual markdown symbols
            reply = re.sub(r'[*_#`]', '', reply)
            
            return {
                "reply": reply,
                "action": action
            }
        except Exception as e:
            logger.error(f"Gemini Voice AI call failed: {e}")
            
    # Fallback rule-based
    return _fallback_voice_response(clean_query, report_context)
