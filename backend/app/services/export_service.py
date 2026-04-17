import io
import uuid
from datetime import datetime
from typing import List, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import inch

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.itinerary import Itinerary
from app.models.transit_blueprint import TransitBlueprint
from app.models.nomad_metrics import NomadMetric
from app.models.emergency_facility import EmergencyFacility

class ExportService:
    """Service to generate PDF exports of travel itineraries."""

    def __init__(self, db: Session):
        self.db = db
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

    def _setup_custom_styles(self):
        self.styles.add(ParagraphStyle(
            name='ItineraryTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            spaceAfter=12,
            textColor=colors.HexColor("#059669")  # Emerald-600
        ))
        self.styles.add(ParagraphStyle(
            name='DayHeader',
            parent=self.styles['Heading2'],
            fontSize=18,
            spaceBefore=12,
            spaceAfter=6,
            textColor=colors.HexColor("#047857") # Emerald-700
        ))
        self.styles.add(ParagraphStyle(
            name='ActivityTime',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.grey
        ))
        self.styles.add(ParagraphStyle(
            name='BlueprintHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor("#1d4ed8") # Blue-700
        ))

    def generate_itinerary_pdf(self, itinerary_id: uuid.UUID) -> bytes:
        """Fetch itinerary data and generate a PDF byte stream."""
        # 1. Fetch data
        itinerary = self._get_itinerary_full(itinerary_id)
        blueprints = self._get_relevant_blueprints(itinerary.destination)
        metrics = self._get_relevant_metrics(itinerary.destination)
        emergency = self._get_emergency_resources(itinerary.destination)

        # 2. Build PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
        elements = []

        # --- Title Page ---
        elements.append(Paragraph(itinerary.title, self.styles['ItineraryTitle']))
        elements.append(Paragraph(f"Destination: {itinerary.destination}", self.styles['Heading3']))
        elements.append(Paragraph(f"Duration: {itinerary.duration_days} Days", self.styles['Normal']))
        elements.append(Paragraph(f"Budget: {itinerary.budget} BDT", self.styles['Normal']))
        elements.append(Paragraph(f"Style: {itinerary.travel_style.capitalize()}", self.styles['Normal']))
        elements.append(Spacer(1, 0.5 * inch))

        # --- Daily Schedule ---
        elements.append(Paragraph("Your Schedule", self.styles['Heading2']))
        elements.append(Spacer(1, 0.2 * inch))

        current_day = 0
        activities = sorted(itinerary.activities, key=lambda x: (x.day_number, x.start_time))
        
        for act in activities:
            if act.day_number != current_day:
                current_day = act.day_number
                elements.append(Paragraph(f"Day {current_day}", self.styles['DayHeader']))
            
            # Activity Row
            time_str = f"{act.start_time} - {act.end_time}"
            elements.append(Paragraph(f"<b>{time_str}</b>: {act.title}", self.styles['Normal']))
            elements.append(Paragraph(act.description, self.styles['Normal']))
            elements.append(Paragraph(f"Location: {act.location} | Est. Cost: {act.estimated_cost} BDT", self.styles['ActivityTime']))
            elements.append(Spacer(1, 0.1 * inch))

        elements.append(PageBreak())

        # --- Transit Blueprints ---
        if blueprints:
            elements.append(Paragraph("Community Transit Blueprints", self.styles['BlueprintHeader']))
            elements.append(Paragraph("Detailed instructions for reaching off-grid spots in this area.", self.styles['Normal']))
            elements.append(Spacer(1, 0.1 * inch))

            for bp in blueprints:
                elements.append(Paragraph(f"Route: {bp.origin} → {bp.destination}", self.styles['Heading3']))
                elements.append(Paragraph(bp.raw_description, self.styles['Normal']))
                if bp.notes:
                    elements.append(Paragraph(f"Note: {bp.notes}", self.styles['Italic']))
                elements.append(Spacer(1, 0.2 * inch))
            
            elements.append(PageBreak())

        # --- Infrastructure & Emergency ---
        elements.append(Paragraph("Essential Info: Bangladesh Nomad Metrics", self.styles['Heading2']))
        if metrics:
            data = [["Resource", "Rating/Provider", "Notes"]]
            for m in metrics:
                data.append([m.carrier_name or m.category, f"{m.connectivity_rating}/5" if m.connectivity_rating else "N/A", m.notes or ""])
            
            t = Table(data, colWidths=[1.5*inch, 1.5*inch, 2.5*inch])
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#f3f4f6")),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
            ]))
            elements.append(t)
        else:
            elements.append(Paragraph("No specific infrastructure data available for this remote area.", self.styles['Normal']))

        elements.append(Spacer(1, 0.3 * inch))
        elements.append(Paragraph("Emergency Support", self.styles['Heading2']))
        if emergency:
            for f in emergency[:5]: # Top 5 nearest
                elements.append(Paragraph(f"<b>{f.name}</b> ({f.category.capitalize()})", self.styles['Normal']))
                elements.append(Paragraph(f"Location: {f.location} | Phone: {f.phone or 'N/A'}", self.styles['Normal']))
        else:
            elements.append(Paragraph("Check local resources upon arrival.", self.styles['Normal']))

        # 3. Finish
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()
        return pdf_bytes

    # --- Data Helpers ---

    def _get_itinerary_full(self, itinerary_id: uuid.UUID) -> Itinerary:
        query = select(Itinerary).where(Itinerary.id == itinerary_id).options(selectinload(Itinerary.activities))
        res = self.db.execute(query).scalar_one_or_none()
        if not res:
            raise ValueError("Itinerary not found")
        return res

    def _get_relevant_blueprints(self, destination: str) -> List[TransitBlueprint]:
        query = select(TransitBlueprint).where(TransitBlueprint.destination.ilike(f"%{destination}%")).limit(3)
        return list(self.db.execute(query).scalars().all())

    def _get_relevant_metrics(self, destination: str) -> List[NomadMetric]:
        query = select(NomadMetric).where(NomadMetric.location.ilike(f"%{destination}%")).limit(5)
        return list(self.db.execute(query).scalars().all())

    def _get_emergency_resources(self, destination: str) -> List[EmergencyFacility]:
        query = select(EmergencyFacility).where(EmergencyFacility.location.ilike(f"%{destination}%")).limit(5)
        return list(self.db.execute(query).scalars().all())
