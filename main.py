import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Header, BackgroundTasks
from upstash_redis import Redis
from schemas import IncomingRequest, AgentResponse
from logic import detect_scam, extract_intelligence
from agent import generate_reply

app = FastAPI()

redis = Redis(
    url=os.getenv("UPSTASH_REDIS_REST_URL"),
    token=os.getenv("UPSTASH_REDIS_REST_TOKEN")
)

GUVI_CALLBACK_URL = os.getenv("GUVI_CALLBACK_URL", "https://hackathon.guvi.in/api/updateHoneyPotFinalResult")

def report_final_result(session_id: str, intel_data: dict, msg_count: int):
    payload = {
        "sessionId": session_id,
        "scamDetected": True,
        "totalMessagesExchanged": msg_count,
        "extractedIntelligence": intel_data,
        "agentNotes": "Scammer engaged. Attempted to extract payment details."
    }
    try:
        requests.post(GUVI_CALLBACK_URL, json=payload, timeout=5)
        print(f"REPORT SENT for Session {session_id}")
    except Exception as e:
        print(f"Failed to report: {e}")

@app.post("/chat", response_model=AgentResponse)
async def chat_endpoint(
    request: IncomingRequest, 
    background_tasks: BackgroundTasks,
    x_api_key: str = Header(None)
):
    if x_api_key != os.getenv("MY_SECRET_KEY"):
        return {"status": "error", "reply": "Unauthorized"}

    sid = request.sessionId
    user_text = request.message.text

    raw_data = redis.get(sid)
    if raw_data:
        session_data = json.loads(raw_data)
    else:
        session_data = {
            "intel": {"bankAccounts": [], "upiIds": [], "phishingLinks": [], "phoneNumbers": [], "suspiciousKeywords": []},
            "msg_count": 0
        }

    new_intel = extract_intelligence(user_text)
    
    for key in new_intel:
        if key in session_data["intel"]:
            session_data["intel"][key].extend(new_intel[key])
            session_data["intel"][key] = list(set(session_data["intel"][key]))

    session_data["msg_count"] += 1

    has_critical_intel = bool(session_data["intel"]["upiIds"] or session_data["intel"]["phoneNumbers"])
    
    if has_critical_intel or session_data["msg_count"] > 10:
        background_tasks.add_task(
            report_final_result, 
            sid, 
            session_data["intel"], 
            session_data["msg_count"]
        )

    redis.set(sid, json.dumps(session_data))

    if detect_scam(user_text) or session_data["msg_count"] > 1:
        reply_text = generate_reply(user_text, request.conversationHistory)
    else:
        reply_text = "I am sorry, I think you have the wrong number."

    return {
        "status": "success",
        "reply": reply_text
    }
