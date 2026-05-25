import logging
import os
import asyncio
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.agents.multimodal import MultimodalAgent
from livekit.plugins import google
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from .. import models, database

load_dotenv()

logger = logging.getLogger("coach-agent")

def prewarm(proc: JobProcess):
    proc.warmup_canary()

async def entrypoint(ctx: JobContext):
    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    participant = await ctx.wait_for_participant()
    logger.info(f"starting agent for participant {participant.identity}")

    # The room name is session_{id}
    try:
        session_id = int(ctx.room.name.split("_")[1])
    except (IndexError, ValueError):
        logger.error(f"Invalid room name: {ctx.room.name}")
        return

    # Fetch session data from DB
    db: Session = next(database.get_db())
    try:
        db_session = db.query(models.ReflectionSession).filter(models.ReflectionSession.id == session_id).first()
        context_text = db_session.context_text if db_session else "ไม่ระบุ"
        system_prompt_extra = db_session.system_prompt if db_session else ""
    finally:
        db.close()

    instructions = f"""
คุณคือโค้ชสอนการสะท้อนคิด (Reflective Coach) ที่เชี่ยวชาญด้าน Gibbs' Reflective Cycle
หน้าที่ของคุณคือช่วยให้ผู้เรียนได้ทบทวนประสบการณ์ผ่าน 6 ขั้นตอนของ Gibbs ดังนี้:
1. Description: เกิดอะไรขึ้น? (เล่าเหตุการณ์)
2. Feelings: คุณคิดและรู้สึกอย่างไรในตอนนั้น?
3. Evaluation: อะไรคือสิ่งที่ดีและไม่ดีในประสบการณ์นั้น?
4. Analysis: คุณจะทำความเข้าใจสถานการณ์นั้นอย่างไร? (วิเคราะห์สาเหตุ/ปัจจัย)
5. Conclusion: คุณสามารถทำอะไรได้อีกบ้างในสถานการณ์นั้น? (ทางเลือกอื่นๆ)
6. Action Plan: ถ้าเหตุการณ์นี้เกิดขึ้นอีก คุณจะทำอย่างไร? (แผนงานในอนาคต)

คำแนะนำเพิ่มเติม:
- พูดภาษาไทยอย่างเป็นธรรมชาติ สุภาพ และให้กำลังใจ
- ฟังอย่างตั้งใจและถามคำถามกระตุ้นความคิดในแต่ละลำดับขั้นของ Gibbs' Cycle
- ห้ามข้ามขั้นตอน ต้องทำตามลำดับ 1-6 เท่านั้น
- เมื่อผู้เรียนตอบในขั้นตอนหนึ่งแล้ว ให้สรุปสั้นๆ และชวนคุยต่อในขั้นตอนถัดไป
- สามารถแทรกคำตอบรับ เช่น "เข้าใจครับ/ค่ะ", "อืม", "ครับ" เพื่อแสดงว่ากำลังฟังอยู่

บริบทของเหตุการณ์ที่จะคุยในวันนี้:
{{context_text}}

คำแนะนำเพิ่มเติมสำหรับเซสชันนี้:
{{system_prompt_extra}}
""".format(context_text=context_text, system_prompt_extra=system_prompt_extra)

    model = google.beta.RealtimeModel(
        model="gemini-3.1-flash-live-preview",
        instructions=instructions,
        voice="puck",
    )

    # Spec requires VAD tuning for Thai fillers
    # In livekit-plugins-google, VAD settings can be passed to the model or agent.
    # We use the specified values: silence_threshold: 0.15, silence_timeout: 1.0s, min_speech_duration: 0.3s
    # Note: padding_duration in LiveKit VAD is equivalent to silence_timeout.

    vad = google.VAD(
        silence_threshold=0.15,
        min_speech_duration=0.3,
        padding_duration=1.0,
    )

    agent = MultimodalAgent(
        model=model,
        vad=vad,
    )

    agent.start(ctx.room, participant)

    # Transcript collection logic
    transcript_parts = []

    @agent.on("user_speech_committed")
    def on_user_speech(msg):
        if msg.content:
            transcript_parts.append(f"User: {msg.content}")
            update_transcript(session_id, "\n".join(transcript_parts))

    @agent.on("agent_speech_committed")
    def on_agent_speech(msg):
        if msg.content:
            transcript_parts.append(f"Coach: {msg.content}")
            update_transcript(session_id, "\n".join(transcript_parts))

def update_transcript(session_id, transcript_text):
    db: Session = next(database.get_db())
    try:
        db_session = db.query(models.ReflectionSession).filter(models.ReflectionSession.id == session_id).first()
        if db_session:
            db_session.transcript = transcript_text
            db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        )
    )
