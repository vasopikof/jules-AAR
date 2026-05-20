import google.generativeai as genai
import os
from . import models, database
from sqlalchemy.orm import Session

def generate_report(session_id: int):
    db_gen: Session = next(database.get_db())
    try:
        db_session = db_gen.query(models.ReflectionSession).filter(models.ReflectionSession.id == session_id).first()

        if not db_session or not db_session.transcript:
            return

        api_key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')

        prompt = f"""
วิเคราะห์บทสนทนาต่อไปนี้และสรุปรายงานตามโครงสร้าง Gibbs' Reflective Cycle เป็นภาษาไทย
รายงานต้องแบ่งเป็น 6 หัวข้อชัดเจน:
1. Description (การบรรยายเหตุการณ์)
2. Feelings (ความรู้สึก)
3. Evaluation (การประเมินผล)
4. Analysis (การวิเคราะห์)
5. Conclusion (บทสรุป)
6. Action Plan (แผนการปฏิบัติ)

บทสนทนา:
{db_session.transcript}

กรุณาเขียนรายงานในรูปแบบ Markdown ที่สวยงามและอ่านง่าย
"""

        response = model.generate_content(prompt)

        db_session.report = response.text
        db_gen.commit()
    finally:
        db_gen.close()
