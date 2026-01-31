from fastapi import FastAPI
from datetime import datetime

app = FastAPI(title="Notification Service")

@app.get("/")
def health_check():
    return {"status": "Notification Service is running"}

@app.post("/notify/match-start")
def notify_match_start(tournament_id: int, match_id: int):
    notification = {
        "event": "MATCH_STARTED",
        "tournament_id": tournament_id,
        "match_id": match_id,
        "timestamp": datetime.utcnow().isoformat()
    }

    # Simulated notification (email / websocket / push)
    print("NOTIFICATION SENT:", notification)

    return {
        "message": "Notification triggered successfully",
        "data": notification
    }
