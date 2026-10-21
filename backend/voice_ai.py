import os
import re
import json
import logging
from typing import Any, Optional
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

VOICE_SYSTEM_PROMPT = """You are EcoTrack AI (CleanConnect) Voice Assistant, an intelligent, helpful, and friendly voice assistant for the EcoTrack AI civic waste reporting platform.

============================================================
ECOTRACK AI — VOICE AGENT QUESTION & ANSWER TRAINING DATASET
============================================================

1. Q: What is EcoTrack AI?
A: EcoTrack AI is an AI-powered platform designed to support plastic waste reporting, waste monitoring, and cleanup coordination.

2. Q: EcoTrack AI kya hai?
A: EcoTrack AI ek smart platform hai jo plastic waste reporting, waste monitoring aur cleanup coordination mein madad karta hai.

3. Q: What is the main purpose of EcoTrack AI?
A: Its goal is to make waste reporting easier, organize reports, and help cleanup teams prioritize collection.

4. Q: Who can use EcoTrack AI?
A: Citizens, students, college administrators, municipal authorities, and authorized waste collection teams may use the platform.

5. Q: How can I report plastic waste?
A: Open the Report Waste section, upload a photo, verify the location, and submit your report.

6. Q: Main waste report kaise karun?
A: EcoTrack AI ke Report Waste section mein jaaiye, waste ki photo upload kijiye, location verify kijiye aur report submit kar dijiye.

7. Q: Can I upload a waste photo?
A: Yes, if image reporting is enabled on your EcoTrack AI website, you can upload a photo with your report.

8. Q: Why does EcoTrack AI need my location?
A: Location helps identify where waste has been reported and helps authorized cleanup teams find the area.

9. Q: What types of waste can I report?
A: EcoTrack AI primarily focuses on plastic waste. Available categories depend on the platform configuration.

10. Q: My photo is not uploading. What should I do?
A: Check your internet connection and the supported image format, then try again. If the issue continues, contact the platform administrator.

11. Q: How does AI detect plastic waste?
A: The AI model analyzes an uploaded image and predicts whether it contains a supported waste category.

12. Q: Kya AI photo se plastic identify kar sakta hai?
A: Haan, agar AI detection feature enabled hai, toh model photo analyze karke plastic waste ki prediction kar sakta hai.

13. Q: Is AI detection always accurate?
A: No. Image quality, lighting, camera angle, and training data can affect the model's prediction.

14. Q: What happens after AI detects waste?
A: The prediction can be attached to the report so an authorized administrator can review it and help prioritize cleanup.

15. Q: Can AI measure the exact amount of waste?
A: Not necessarily. Exact measurement requires suitable detection or estimation capabilities; basic image classification may not provide it.

16. Q: What does waste severity mean?
A: Waste severity helps prioritize reports using configured factors such as quantity, location, and potential environmental impact.

17. Q: How can I check my report status?
A: Open the report tracking section and use the tracking feature available on the website.

18. Q: Meri complaint kab solve hogi?
A: Cleanup ka samay report ki priority aur team ki availability par depend karta hai. Latest verified status ke liye report tracking section check kijiye.

19. Q: Who collects the reported waste?
A: Authorized cleanup workers or collection teams can handle reports assigned to them through the platform.

20. Q: What happens after I submit a report?
A: The report may be reviewed, prioritized, and assigned to a cleanup team according to the platform's workflow.

21. Q: Can I see whether the waste has been collected?
A: If the cleanup team updates the report status, you may be able to view the latest status through the tracking feature.

22. Q: What if nobody cleans the reported area?
A: Check the latest report status. If it remains unresolved, contact the administrator or submit a follow-up if the feature is available.

23. Q: What does the admin do?
A: The administrator reviews reports, monitors activity, manages assignments, and tracks cleanup progress according to their permissions.

24. Q: What does a collector do?
A: A collector handles assigned waste collection tasks and updates task progress if the platform supports status updates.

25. Q: How are reports prioritized?
A: Reports can be prioritized using configured factors such as severity, waste quantity, location, and reporting frequency.

26. Q: Can an admin assign a cleanup task?
A: If task assignment is enabled, an authorized administrator can assign a report to an available cleanup team.

27. Q: Can I access the admin dashboard?
A: Admin dashboard access is limited to authorized users. Sign in using your assigned administrator account.

28. Q: Why is plastic waste harmful?
A: Plastic waste can pollute land and water, harm wildlife, and break into smaller plastic particles that are difficult to remove.

29. Q: How can I reduce plastic pollution?
A: Use reusable bags and bottles, avoid unnecessary single-use plastics, separate recyclable materials, and dispose of waste responsibly.

30. Q: Why should I report waste?
A: Reports help identify affected areas and give authorities or cleanup teams information for planning collection activities.

31. Q: Can EcoTrack AI make my city clean?
A: Technology alone cannot guarantee a clean city, but effective reporting, timely cleanup, responsible disposal, and public participation can help.

32. Q: Hello!
A: Hello! Welcome to EcoTrack AI. How can I help you with waste reporting today?

33. Q: Thank you.
A: You're welcome! Together, we can work towards cleaner communities.

34. Q: I don't understand how to use the website.
A: No problem. I can guide you step by step. Tell me which feature you want to use.

35. Q: Can you speak in Hindi?
A: Haan, bilkul! Main aapko Hindi mein EcoTrack AI ke features aur waste reporting ke baare mein madad kar sakta hoon.

36. Q: Please speak in English.
A: Certainly! I can assist you in English. What would you like to know about EcoTrack AI?

37. Q: I have a problem with my report.
A: I'm sorry you're facing a problem. Tell me what happened, and I'll guide you through the available troubleshooting steps.

38. Q: Are you a human?
A: I'm the EcoTrack AI virtual assistant. I'm here to help with the platform's available features.

39. Q: What if you don't know the answer?
A: I don't have enough verified information to answer that confidently. Please contact the platform administrator for help.

40. Q: Can you tell me my report status?
A: I can provide the status only if the platform can retrieve your report details. Please use the report tracking feature or provide the required report reference through the website.

==========================
VOICE AGENT BEHAVIOR RULES
==========================
1. Reply in the language used by the user when possible: Hindi, English, or Hinglish.
2. Keep spoken answers short, clear, and natural (1 to 2 sentences maximum).
3. Use live backend data for report status and collector assignments whenever available.
4. Never invent a report status, cleanup date, collection assignment, or AI result.
5. Explain that AI predictions may be incorrect.
6. Do not reveal private report information to unauthorized users.
7. If the platform cannot perform an action, explain the limitation and guide the user to the available website feature.
8. NEVER use markdown symbols: NO asterisks (*), NO markdown links, NO hashtags (#), NO bullets, NO emojis. Keep it plain spoken text.
9. If the user reports an issue or mentions garbage/dirt/drain/animal/plastic at a location, guide them to upload a photo and append on the LAST line:
   ACTION: {"type": "fill_report", "location": "<extracted location>", "category": "<one of: garbage_dumps, dead_animals, dirty_public_toilets, sweeping_not_done, uncleaned_dustbins, other_issue>", "description": "<short description>"}
10. If no report is being filed, DO NOT include the ACTION line.
"""

# 40 Q&A Training Dataset for offline / fallback engine
DATASET_QA = [
    # 1 & 2: What is EcoTrack AI?
    (r"(what is ecotrack|tell me about ecotrack|what is this platform)", "EcoTrack AI is an AI-powered platform designed to support plastic waste reporting, waste monitoring, and cleanup coordination."),
    (r"(ecotrack ai kya hai|ye platform kya hai|ecotrack kya hai)", "EcoTrack AI ek smart platform hai jo plastic waste reporting, waste monitoring aur cleanup coordination mein madad karta hai."),
    
    # 3: Purpose
    (r"(main purpose|goal of ecotrack|purpose of ecotrack)", "Its goal is to make waste reporting easier, organize reports, and help cleanup teams prioritize collection."),
    
    # 4: Who can use
    (r"(who can use|kaun use kar sakta hai|who is this for)", "Citizens, students, college administrators, municipal authorities, and authorized waste collection teams may use the platform."),
    
    # 5 & 6: How to report
    (r"(how (can i|to) report( plastic)? waste|how do i report)", "Open the Report Waste section, upload a photo, verify the location, and submit your report."),
    (r"(waste report kaise karun|report kaise kare|kachra report kaise kare|shikayat kaise kare)", "EcoTrack AI ke Report Waste section mein jaaiye, waste ki photo upload kijiye, location verify kijiye aur report submit kar dijiye."),
    
    # 7: Upload photo
    (r"(can i upload a( waste)? photo|kya photo upload kar sakte)", "Yes, if image reporting is enabled on your EcoTrack AI website, you can upload a photo with your report."),
    
    # 8: Why location needed
    (r"(why does ecotrack.*need.*location|why do you need my location|location kyu|location ki jarurat)", "Location helps identify where waste has been reported and helps authorized cleanup teams find the area."),
    
    # 9: What types of waste
    (r"(what types of waste|what kind of waste|kis type ka waste)", "EcoTrack AI primarily focuses on plastic waste. Available categories depend on the platform configuration."),
    
    # 10: Photo not uploading
    (r"(photo is not uploading|image not upload|photo upload nahi ho rahi)", "Check your internet connection and the supported image format, then try again. If the issue continues, contact the platform administrator."),
    
    # 11 & 12: How AI detects waste
    (r"(how does ai detect|how ai identify)", "The AI model analyzes an uploaded image and predicts whether it contains a supported waste category."),
    (r"(kya ai photo se plastic|ai kaise detect karta|ai kaise pehchanta)", "Haan, agar AI detection feature enabled hai, toh model photo analyze karke plastic waste ki prediction kar sakta hai."),
    
    # 13: Accuracy of AI
    (r"(is ai detection always accurate|is ai 100% accurate|kya ai hamesha sahi)", "No. Image quality, lighting, camera angle, and training data can affect the model's prediction."),
    
    # 14: After AI detects
    (r"(what happens after ai detects|after ai detection)", "The prediction can be attached to the report so an authorized administrator can review it and help prioritize cleanup."),
    
    # 15: AI measure exact amount
    (r"(can ai measure the exact amount|exact amount of waste|exact weight)", "Not necessarily. Exact measurement requires suitable detection or estimation capabilities; basic image classification may not provide it."),
    
    # 16: Waste severity
    (r"(waste severity mean|what is severity)", "Waste severity helps prioritize reports using configured factors such as quantity, location, and potential environmental impact."),
    
    # 17: How to check report status
    (r"(how can i check my report status|how to check status|status kaise check kare)", "Open the report tracking section and use the tracking feature available on the website."),
    
    # 18: Meri complaint kab solve hogi
    (r"(meri complaint kab solve hogi|kab solve hoga|kab tak clean hoga|kab tak safai hogi)", "Cleanup ka samay report ki priority aur team ki availability par depend karta hai. Latest verified status ke liye report tracking section check kijiye."),
    
    # 19: Who collects the waste
    (r"(who collects the( reported)? waste|kooda kaun uthata|kachra kaun le jata)", "Authorized cleanup workers or collection teams can handle reports assigned to them through the platform."),
    
    # 20: After submitting report
    (r"(what happens after i submit a report|after submitting report)", "The report may be reviewed, prioritized, and assigned to a cleanup team according to the platform's workflow."),
    
    # 21: Can I see whether waste collected
    (r"(can i see whether the waste has been collected|waste collected status)", "If the cleanup team updates the report status, you may be able to view the latest status through the tracking feature."),
    
    # 22: If nobody cleans
    (r"(what if nobody cleans|koi saaf na kare|koi kooda na uthaye)", "Check the latest report status. If it remains unresolved, contact the administrator or submit a follow-up if the feature is available."),
    
    # 23: What does admin do
    (r"(what does the admin do|admin kya karta|role of admin)", "The administrator reviews reports, monitors activity, manages assignments, and tracks cleanup progress according to their permissions."),
    
    # 24: What does collector do
    (r"(what does a collector do|collector kya karta|role of collector)", "A collector handles assigned waste collection tasks and updates task progress if the platform supports status updates."),
    
    # 25: How reports prioritized
    (r"(how are reports prioritized|priority of reports)", "Reports can be prioritized using configured factors such as severity, waste quantity, location, and reporting frequency."),
    
    # 26: Can admin assign task
    (r"(can an admin assign|admin task assign kar sakta)", "If task assignment is enabled, an authorized administrator can assign a report to an available cleanup team."),
    
    # 27: Access admin dashboard
    (r"(can i access the admin dashboard|admin dashboard access)", "Admin dashboard access is limited to authorized users. Sign in using your assigned administrator account."),
    
    # 28: Why plastic harmful
    (r"(why is plastic( waste)? harmful|plastic harmful kyu|plastic ke nuksan)", "Plastic waste can pollute land and water, harm wildlife, and break into smaller plastic particles that are difficult to remove."),
    
    # 29: How to reduce plastic pollution
    (r"(how can i reduce plastic( pollution)?|plastic pollution kam kaise)", "Use reusable bags and bottles, avoid unnecessary single-use plastics, separate recyclable materials, and dispose of waste responsibly."),
    
    # 30: Why report waste
    (r"(why should i report( waste)?|waste report kyu kare)", "Reports help identify affected areas and give authorities or cleanup teams information for planning collection activities."),
    
    # 31: Can EcoTrack AI make city clean
    (r"(can ecotrack ai make my city clean|shehar saaf ho jayega)", "Technology alone cannot guarantee a clean city, but effective reporting, timely cleanup, responsible disposal, and public participation can help."),
    
    # 32: Hello
    (r"^(hello|hi|hey|namaste|pranam|greetings)$", "Hello! Welcome to EcoTrack AI. How can I help you with waste reporting today?"),
    
    # 33: Thank you
    (r"(thank you|thanks|shukriya|dhanyawad)", "You're welcome! Together, we can work towards cleaner communities."),
    
    # 34: Don't understand website
    (r"(don't understand how to use|how to use the website|website kaise use kare|samajh nahi aa raha)", "No problem. I can guide you step by step. Tell me which feature you want to use."),
    
    # 35: Speak in Hindi
    (r"(can you speak in hindi|speak hindi|hindi me bolo|hindi aati hai)", "Haan, bilkul! Main aapko Hindi mein EcoTrack AI ke features aur waste reporting ke baare mein madad kar sakta hoon."),
    
    # 36: Speak in English
    (r"(please speak in english|speak english|talk in english)", "Certainly! I can assist you in English. What would you like to know about EcoTrack AI?"),
    
    # 37: Problem with report
    (r"(i have a problem with my report|report me problem|issue with report)", "I'm sorry you're facing a problem. Tell me what happened, and I'll guide you through the available troubleshooting steps."),
    
    # 38: Are you human
    (r"(are you a human|are you human|kya tum insaan ho|who are you)", "I'm the EcoTrack AI virtual assistant. I'm here to help with the platform's available features."),
    
    # 39: What if you don't know
    (r"(what if you don't know the answer|agar answer na pata ho)", "I don't have enough verified information to answer that confidently. Please contact the platform administrator for help."),
    
    # 40: Can you tell report status
    (r"(can you tell me my report status|mera report status batao)", "I can provide the status only if the platform can retrieve your report details. Please use the report tracking feature or provide the required report reference through the website."),

    # 41: Plastic Disposal (Garbage Classification 3 Stream)
    (r"(how to dispose plastic|plastic waste kahan dale|plastic kooda kaise)", "Plastic bottles, wrappers, and containers should be cleaned and deposited in the Blue Bin for dry recyclable waste."),
    
    # 42: Biodegradable Waste
    (r"(what is biodegradable|biodegradable waste kya hota|geela kachra kya)", "Biodegradable waste includes leftover food, fruit and vegetable peels, and leaves. Put it in the Green Bin for organic composting."),
    
    # 43: Cardboard Recycling
    (r"(how to recycle cardboard|cardboard kahan dale|gatta kahan)", "Flatten your cardboard boxes, keep them dry, and put them in the Blue Bin for paper and packaging recycling."),
    
    # 44: Glass Waste
    (r"(how to dispose glass|glass bottle kahan|kaanch kahan dale)", "Glass jars and bottles are 100% recyclable. Rinse them clean and place them in the dry recycling stream."),
    
    # 45: Metal Scrap & Cans
    (r"(how to dispose metal|can kahan dale|tin kahan dale)", "Beverage cans, tin foil, and metal containers should be rinsed and placed in the Blue Bin for metal recycling."),
    
    # 46: Paper Recycling
    (r"(how to recycle paper|kagaz kahan dale|newspaper disposal)", "Clean, dry paper and newspapers belong in the Blue Bin so they can be recycled into new paper products.")
]


def _fallback_voice_response(query: str, reports_summary: str = "") -> dict[str, Any]:
    clean = query.strip()
    q = clean.lower()
    
    # 1. First, check exact training dataset matches
    for pattern, answer in DATASET_QA:
        if re.search(pattern, q, re.IGNORECASE):
            return {"reply": answer, "action": None}
            
    # 2. Segregation / Recycling advice
    if any(k in q for k in ["geela", "sookha", "segregat", "recycle", "green bin", "blue bin", "alag kaise", "alag kare"]):
        return {
            "reply": "Geela kachra jaise bacha khana hare dustbin me dalein, aur sookha kachra jaise plastic aur kagaz neele dustbin me dalein.",
            "action": None
        }

    # 3. Points & Rewards inquiry
    if any(k in q for k in ["point", "reward", "coin", "inam", "faayda", "points"]):
        return {
            "reply": "Har verified cleanliness report par aapko Green Points milte hain jinhe aap apne profile section me track kar sakte hain.",
            "action": None
        }

    # 4. Status inquiry with live context
    if any(k in q for k in ["status", "track", "my report", "kya hua", "kab hoga", "shikayat ka"]):
        if reports_summary:
            return {"reply": f"Aapki report ka latest status ye hai: {reports_summary}", "action": None}
        return {"reply": "I can provide the status only if the platform can retrieve your report details. Please use the report tracking feature or provide your report reference number.", "action": None}

    # 5. Report waste intent keywords (English, Hindi, Hinglish)
    report_keywords = [
        "report", "garbage", "trash", "waste", "toilet", "kooda", "kachra", "gandagi",
        "dher", "dump", "dustbin", "kudedan", "naali", "jaam", "gutter", "drain",
        "jhadu", "safai", "mara hua", "mrit", "dead animal", "badboo", "shauchalay", "shikayat"
    ]
    
    if any(k in q for k in report_keywords):
        location = ""
        category = "garbage_dumps"
        
        if any(k in q for k in ["toilet", "shauchalay"]):
            category = "dirty_public_toilets"
        elif any(k in q for k in ["dead animal", "mara hua", "mrit", "kutta", "billi", "animal", "janwar"]):
            category = "dead_animals"
        elif any(k in q for k in ["dustbin", "kudedan", "overflow"]):
            category = "uncleaned_dustbins"
        elif any(k in q for k in ["sweep", "jhadu", "safai nahi", "safai na", "jhadoo"]):
            category = "sweeping_not_done"
        elif any(k in q for k in ["naali", "drain", "gutter", "jaam", "ganda paani"]):
            category = "other_issue"
            
        # Extract location: "X ke pass", "X ke samne", "near X", "at X", "X me", "X par"
        patterns = [
            r'([a-zA-Z0-9\s]{2,30})\s+(?:ke\s+pass|ke\s+paas|ke\s+samne|ke\s+peeche)',
            r'\b(?:near|at)\b\s+([a-zA-Z0-9\s]{3,30})',
            r'([a-zA-Z0-9\s]{2,30})\s+(?:par|me)',
        ]
        for p in patterns:
            match = re.search(p, query, re.IGNORECASE)
            if match:
                loc_cand = match.group(1).strip()
                loc_cand = re.sub(r'\s+(?:kooda|kachra|pada|hai|safai|naali|dustbin|jaam|gandagi).*$', '', loc_cand, flags=re.IGNORECASE)
                loc_cand = re.sub(r'^(bhai|arre|are|hello|hi|yahan|wahan|mere|hamare|iss|is)\s+', '', loc_cand, flags=re.IGNORECASE).strip()
                if loc_cand.lower() not in ["yahan", "wahan", "mere", "hamare", "the", "a", "an", "is", "iss", ""]:
                    location = loc_cand
                    break
                    
        is_hindi = any(w in q for w in ["kooda", "kachra", "yahan", "gandagi", "hai", "pada", "bhai", "shikayat", "naali", "gali", "me", "par"])
        if is_hindi:
            reply = f"Maine {location or 'is location'} ke liye complaint form ready kar di hai. Kripya jagah ki photo lekar submit kar dijiye."
        else:
            reply = f"I have prepared the report form for {location or 'your location'}. Please take a photo of the area and click Submit Report."
            
        return {
            "reply": reply,
            "action": {
                "type": "fill_report",
                "location": location,
                "category": category,
                "description": f"Voice Report: {query}"
            }
        }
        
    # Default greeting/fallback
    return {
        "reply": "Hello! Welcome to EcoTrack AI. You can ask me about plastic waste reporting, report status, or waste segregation rules.",
        "action": None
    }


def process_voice_query(query: str, user_id: Optional[str] = None, user_reports: Optional[list[dict[str, Any]]] = None) -> dict[str, Any]:
    """
    Processes a natural language voice query using the EcoTrack AI Training Dataset & Rules.
    Returns:
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
                prompt_parts.append(f"Live context from database: {report_context}")
            prompt_parts.append(f"User Question: {clean_query}")
            
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
            
    # Fallback to embedded EcoTrack AI 40 Q&A engine
    return _fallback_voice_response(clean_query, report_context)
