"""
Municipal Executive Intelligence Briefing Engine powered by Google Gemini for EcoTrack AI.
Synthesizes city-wide civic cleanliness telemetry, hotspot trends, and operational efficiency
into formal executive briefings for municipal administrators.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Any

logger = logging.getLogger(__name__)


def _generate_heuristic_briefing(stats: dict[str, Any], recent_reports: list[dict[str, Any]]) -> dict[str, Any]:
    """Fallback generator for municipal intelligence when external AI is offline."""
    total = stats.get("total_reports", 0)
    pending = stats.get("pending_reports", 0)
    collected = stats.get("collected_reports", 0)
    cat_counts = stats.get("category_counts", {})
    status_counts = stats.get("status_counts", {})
    verified = status_counts.get("verified", 0)

    res_rate = round((verified / max(total, 1)) * 100, 1) if total > 0 else 100.0

    if res_rate >= 80:
        grade = "A"
        district_status = "EXEMPLARY"
        hygiene_index = int(np_clip := min(95, 80 + int(res_rate * 0.15)))
    elif res_rate >= 60:
        grade = "B+"
        district_status = "STABLE_IMPROVING"
        hygiene_index = int(min(85, 65 + int(res_rate * 0.2)))
    elif res_rate >= 40:
        grade = "B-"
        district_status = "MODERATE_BACKLOG"
        hygiene_index = int(min(65, 50 + int(res_rate * 0.2)))
    else:
        grade = "C"
        district_status = "CRITICAL_ATTENTION_REQUIRED"
        hygiene_index = int(max(35, int(res_rate * 0.9)))

    top_cat = max(cat_counts.items(), key=lambda x: x[1])[0] if cat_counts else "General Waste"
    top_cat_label = top_cat.replace("_", " ").title()

    return {
        "success": True,
        "hygiene_index": hygiene_index,
        "rating_grade": grade,
        "district_status": district_status,
        "executive_headline": f"District operations at {res_rate}% verified resolution across {total} logged civic incidents.",
        "key_findings": [
            f"{top_cat_label} represents the highest volume waste stream with {cat_counts.get(top_cat, 0)} registered reports.",
            f"Municipal collectors have successfully resolved {collected} field tasks, with {pending} pending review/action.",
            f"Verified citizen compliance rate stands at {res_rate}% across active urban monitoring zones."
        ],
        "urgent_directives": [
            f"Prioritize swift dispatch for {pending} pending incidents in dense urban sectors.",
            f"Reinforce targeted recycling and segregation protocols for {top_cat_label}."
        ],
        "resource_allocation_advice": (
            f"Recommend allocating additional collection vehicles toward high-density {top_cat_label} zones "
            f"and accelerating verification approvals for completed collector tasks."
        ),
        "generated_at": datetime.now(timezone.utc).strftime("%b %d, %Y • %I:%M %p UTC"),
        "provider": "ecotrack-municipal-intelligence-engine"
    }


def generate_executive_briefing(stats: dict[str, Any], recent_reports: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Calls Google Gemini to generate a formal executive municipal briefing based on live civic data.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            from google import genai

            client = genai.Client(api_key=api_key)

            total = stats.get("total_reports", 0)
            pending = stats.get("pending_reports", 0)
            collected = stats.get("collected_reports", 0)
            cat_counts = stats.get("category_counts", {})
            status_counts = stats.get("status_counts", {})

            sample_summaries = []
            for r in recent_reports[:8]:
                sample_summaries.append(
                    f"Report {r.get('report_id')}: {r.get('category', 'waste')} at ({r.get('latitude')}, {r.get('longitude')}), status={r.get('status')}"
                )

            prompt = f"""
            You are the Chief AI Municipal Advisor & Civic Intelligence Officer for EcoTrack AI.
            Analyze the following real-time municipal cleanliness telemetry:
            - Total Registered Incidents: {total}
            - Pending Operational Reports: {pending}
            - Collected & Verified Reports: {collected}
            - Waste Stream Breakdown: {json.dumps(cat_counts)}
            - Status Breakdown: {json.dumps(status_counts)}
            - Sample Recent Incidents:
            {chr(10).join(sample_summaries)}

            Generate an executive-grade municipal intelligence briefing for the Municipal Commissioner and City Sanitation Directorate.
            Provide:
            1. hygiene_index (integer from 0 to 100)
            2. rating_grade ("A+", "A", "B+", "B", "C")
            3. district_status ("EXEMPLARY" | "STABLE_IMPROVING" | "MODERATE_BACKLOG" | "CRITICAL_ATTENTION_REQUIRED")
            4. executive_headline (concise 1-sentence high-level summary)
            5. key_findings (array of 3 distinct, analytical observations)
            6. urgent_directives (array of 2 concrete, operational action orders)
            7. resource_allocation_advice (1-2 sentences on fleet/crew deployment)

            Respond strictly in valid JSON without markdown wrapping:
            {{
              "hygiene_index": 86,
              "rating_grade": "A-",
              "district_status": "STABLE_IMPROVING",
              "executive_headline": "Municipal sanitation efficiency reached 82% resolution with strong collector dispatch.",
              "key_findings": [
                "Plastic waste represents 58% of active civic reports, concentrated around central transit hubs.",
                "Collector completion verification is maintaining a sub-24h turnaround for verified points.",
                "Drainage and uncleaned dustbins require secondary weekend sweeps to avert monsoon overflow."
              ],
              "urgent_directives": [
                "Direct Ward 4 sanitation team to expedite collection of 3 open garbage dumps.",
                "Deploy wet-waste segregated tippers to reduce landfill contamination."
              ],
              "resource_allocation_advice": "Focus compactor fleets in eastern sector corridors between 06:00 and 10:00 to preempt traffic buildup."
            }}
            """

            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )

            raw_text = response.text.strip()
            if raw_text.startswith("```json"):
                raw_text = raw_text[7:-3].strip()
            elif raw_text.startswith("```"):
                raw_text = raw_text[3:-3].strip()

            result = json.loads(raw_text)
            if not isinstance(result, dict) or "hygiene_index" not in result:
                raise ValueError("Invalid structure from Gemini Executive Briefing")

            result["success"] = True
            result["generated_at"] = datetime.now(timezone.utc).strftime("%b %d, %Y • %I:%M %p UTC")
            result["provider"] = "google-gemini-executive-briefing"
            return result

        except Exception as e:
            logger.warning(f"Gemini Executive Briefing API failed: {e}. Falling back to internal engine.")

    return _generate_heuristic_briefing(stats, recent_reports)
