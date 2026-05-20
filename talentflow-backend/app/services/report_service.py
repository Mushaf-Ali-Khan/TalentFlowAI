import csv
import io
import json
from fpdf import FPDF
from sqlalchemy import select
from app.models.candidate import Candidate

class ReportService:
    async def generate_batch_report(self, db, batch_id) -> bytes:
        result = await db.execute(
            select(Candidate).where(Candidate.batch_id == batch_id)
        )
        candidates = list(result.scalars().all())

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow([
            "candidate_id",
            "name",
            "email",
            "phone",
            "location",
            "total_score",
            "semantic_score",
            "llm_score",
            "auto_rejected",
            "needs_manual_review",
            "processing_status",
            "recruiter_status",
        ])

        for c in candidates:
            profile = c.profile
            if isinstance(profile, str):
                try:
                    profile = json.loads(profile)
                except Exception:
                    profile = {}

            writer.writerow([
                str(c.id),
                profile.get("name", "") if isinstance(profile, dict) else "",
                profile.get("email", "") if isinstance(profile, dict) else "",
                profile.get("phone", "") if isinstance(profile, dict) else "",
                profile.get("location", "") if isinstance(profile, dict) else "",
                c.total_score or 0,
                c.semantic_score or 0,
                c.llm_score or 0,
                c.auto_rejected or False,
                c.needs_manual_review or False,
                c.processing_status or "",
                c.recruiter_status or "",
            ])

        return output.getvalue().encode("utf-8")

    async def generate_batch_report_pdf(self, db, batch_id) -> bytes:
        result = await db.execute(
            select(Candidate).where(Candidate.batch_id == batch_id)
        )
        candidates = list(result.scalars().all())

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Helvetica", size=12)
        pdf.cell(0, 10, f"TalentFlow AI Batch Report", ln=True)
        pdf.set_font("Helvetica", size=10)
        pdf.cell(0, 8, f"Batch ID: {batch_id}", ln=True)
        pdf.ln(4)

        for candidate in candidates:
            profile = candidate.profile
            if isinstance(profile, str):
                try:
                    profile = json.loads(profile)
                except Exception:
                    profile = {}

            name = profile.get("name", "Candidate") if isinstance(profile, dict) else "Candidate"
            email = profile.get("email", "") if isinstance(profile, dict) else ""
            total_score = candidate.total_score or 0
            semantic_score = candidate.semantic_score or 0
            llm_score = candidate.llm_score or 0
            status = candidate.recruiter_status or "new"

            pdf.set_font("Helvetica", size=10)
            pdf.cell(0, 6, f"Name: {name}", ln=True)
            if email:
                pdf.cell(0, 6, f"Email: {email}", ln=True)
            pdf.cell(0, 6, f"Total Score: {total_score}", ln=True)
            pdf.cell(0, 6, f"Semantic: {semantic_score} | LLM: {llm_score}", ln=True)
            pdf.cell(0, 6, f"Recruiter Status: {status}", ln=True)
            pdf.ln(3)

        return pdf.output(dest="S").encode("latin-1", "replace")

report_service = ReportService()
