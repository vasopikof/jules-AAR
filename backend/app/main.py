from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from . import models, database, synthesis
from pydantic import BaseModel
import os
from livekit import api
import uuid

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SessionCreate(BaseModel):
    context_text: str
    system_prompt: str

class SessionResponse(BaseModel):
    id: int
    context_text: str | None
    system_prompt: str | None
    transcript: str | None
    report: str | None
    token: str | None = None

@app.post("/sessions", response_model=SessionResponse)
def create_session(session_data: SessionCreate, db: Session = Depends(database.get_db)):
    db_session = models.ReflectionSession(
        context_text=session_data.context_text,
        system_prompt=session_data.system_prompt
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)

    # Generate LiveKit Token
    lk_api_key = os.getenv("LIVEKIT_API_KEY", "devkey")
    lk_api_secret = os.getenv("LIVEKIT_API_SECRET", "secret")

    room_name = f"session_{db_session.id}"
    participant_identity = f"user_{uuid.uuid4().hex[:8]}"

    token = api.AccessToken(lk_api_key, lk_api_secret) \
        .with_identity(participant_identity) \
        .with_grants(api.VideoGrants(
            room_join=True,
            room=room_name,
        ))

    jwt_token = token.to_jwt()

    return SessionResponse(
        id=db_session.id,
        context_text=db_session.context_text,
        system_prompt=db_session.system_prompt,
        transcript=db_session.transcript,
        report=db_session.report,
        token=jwt_token
    )

@app.get("/sessions/{session_id}", response_model=SessionResponse)
def get_session(session_id: int, db: Session = Depends(database.get_db)):
    db_session = db.query(models.ReflectionSession).filter(models.ReflectionSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return db_session

@app.post("/sessions/{session_id}/complete")
async def complete_session(session_id: int, background_tasks: BackgroundTasks, db: Session = Depends(database.get_db)):
    db_session = db.query(models.ReflectionSession).filter(models.ReflectionSession.id == session_id).first()
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")

    background_tasks.add_task(synthesis.generate_report, session_id)
    return {"message": "Synthesis started"}
