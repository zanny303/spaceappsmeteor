# backend/report_generator.py
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from io import BytesIO
import datetime
import logging

logger = logging.getLogger(__name__)

def create_pdf_briefing(mission_plan):
    """
    Generate comprehensive PDF briefing using pure-Python ReportLab.
    Includes AI recommendations, physics predictions, and mission parameters.
    """
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, topMargin=0.5*inch)
        styles = getSampleStyleSheet()
        
        # Custom styles for professional appearance
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.HexColor('#B22222'),
            spaceAfter=12,
            borderPadding=5,
            borderColor=colors.HexColor('#B22222'),
            borderWidth=1
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading', 
            parent=styles['Heading2'],
            fontSize=12,
            textColor=colors.HexColor('#0056b3'),
            spaceAfter=6
        )
        
        highlight_style = ParagraphStyle(
            'Highlight',
            parent=styles['Normal'],
            backColor=colors.HexColor('#FFFACD'),
            borderPadding=5,
            borderColor=colors.HexColor('#FFD700'),
            borderWidth=1
        )
        
        # Build story content
        story = []
        
        # Header with NASA-style branding
        story.append(Paragraph("PLANETARY DEFENSE COORDINATION OFFICE", styles['Heading2']))
        story.append(Paragraph("AI-Enhanced Threat Assessment & Mission Planning", title_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Asteroid information
        asteroid_info = mission_plan.get('asteroid_info', {})
        asteroid_name = asteroid_info.get('name', 'Unknown Asteroid')
        
        story.append(Paragraph(f"THREAT ANALYSIS: {asteroid_name}", heading_style))
        
        # Basic asteroid data table
        asteroid_data = [
            ["Parameter", "Value"],
            ["Asteroid ID", asteroid_info.get('id', 'N/A')],
            ["Diameter", f"{asteroid_info.get('diameter_m', 0):.1f} meters"],
            ["Approach Velocity", f"{asteroid_info.get('velocity_kms', 0):.1f} km/s"],
            ["Estimated Mass", f"{asteroid_info.get('mass_kg', 0):.2e} kg"]
        ]
        
        asteroid_table = Table(asteroid_data, colWidths=[2*inch, 3*inch])
        asteroid_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0056b3')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dee2e6'))
        ]))
        story.append(asteroid_table)
        story.append(Spacer(1, 0.3*inch))
        
        # AI Impact Consequences
        story.append(Paragraph("AI-PREDICTED IMPACT CONSEQUENCES", heading_style))
        
        consequences = mission_plan.get('ai_predicted_consequences', {})
        consequence_data = [
            ["Impact Effect", "Predicted Magnitude", "Severity"],
            ["Kinetic Energy", f"{consequences.get('impact_energy_megatons', 0):,} MT TNT", "Catastrophic" if consequences.get('impact_energy_megatons', 0) > 100 else "Major"],
            ["Economic Damage", f"${consequences.get('economic_damage_usd', 0):,.0f}", "Extreme" if consequences.get('economic_damage_usd', 0) > 1e12 else "Severe"],
            ["Predicted Casualties", f"{consequences.get('predicted_casualties', 0):,}", "Mass Casualty" if consequences.get('predicted_casualties', 0) > 1000000 else "Significant"],
            ["Seismic Magnitude", f"{consequences.get('predicted_seismic_magnitude', 0)}", "Major Earthquake" if consequences.get('predicted_seismic_magnitude', 0) > 7 else "Moderate"],
            ["Blast Radius", f"{consequences.get('blast_radius_km', 0)} km", "Regional" if consequences.get('blast_radius_km', 0) > 50 else "Localized"],
            ["Crater Diameter", f"{consequences.get('crater_diameter_km', 0)} km", "Continental" if consequences.get('crater_diameter_km', 0) > 10 else "Regional"]
        ]
        
        consequence_table = Table(consequence_data, colWidths=[1.8*inch, 1.8*inch, 1.4*inch])
        consequence_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#dc3545')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ffe6e6')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#dc3545')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        story.append(consequence_table)
        story.append(Spacer(1, 0.3*inch))
        
        # AI Mission Recommendation (Highlighted)
        story.append(Paragraph("AI-GENERATED MISSION RECOMMENDATION", heading_style))
        
        mission_rec = mission_plan.get('mission_recommendation', {})
        mission_data = [
            ["Decision Parameter", "AI Recommendation"],
            ["Optimal Mission Architecture", mission_rec.get('source', 'N/A')],
            ["Recommended Interceptor", mission_rec.get('interceptor_type', 'N/A')],
            ["AI Confidence Score", f"{mission_rec.get('confidence_score', 0)}%"],
            ["Model Type", mission_rec.get('model_type', 'N/A').replace('_', ' ').title()]
        ]
        
        mission_table = Table(mission_data, colWidths=[2*inch, 3*inch])
        mission_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#28a745')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0fff4')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#28a745'))
        ]))
        story.append(mission_table)
        
        # AI Rationale
        rationale = mission_rec.get('rationale', 'No rationale provided.')
        story.append(Spacer(1, 0.2*inch))
        story.append(Paragraph("AI Decision Rationale:", styles['Heading3']))
        story.append(Paragraph(rationale, highlight_style))
        story.append(Spacer(1, 0.3*inch))
        
        # Mission Parameters
        story.append(Paragraph("MISSION CRITICAL PARAMETERS", heading_style))
        
        mission_params = mission_plan.get('mission_parameters', {})
        params_data = [
            ["Parameter", "Value", "Criticality"],
            ["Latest Time for Intercept (LTI)", f"{mission_params.get('lti_days', 0):,} days", "HIGH" if mission_params.get('lti_days', 0) < 365 else "MEDIUM"],
            ["Required Velocity Change (ΔV)", f"{mission_params.get('required_dv_ms', 0):.6f} m/s", "HIGH" if mission_params.get('required_dv_ms', 0) > 0.01 else "MEDIUM"],
            ["Asteroid Mass", f"{mission_params.get('calculated_mass_kg', 0):.2e} kg", "HIGH" if mission_params.get('calculated_mass_kg', 0) > 1e11 else "MEDIUM"],
            ["Deflection Difficulty", calculate_difficulty(mission_params), "See note"]
        ]
        
        params_table = Table(params_data, colWidths=[1.8*inch, 1.8*inch, 1.4*inch])
        params_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6f42c1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8f9fa')),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#6f42c1'))
        ]))
        story.append(params_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Analysis Metadata
        metadata = mission_plan.get('analysis_metadata', {})
        story.append(Paragraph("ANALYSIS METADATA", heading_style))
        meta_text = f"""
        Analysis Version: {metadata.get('version', 'N/A')}<br/>
        Model Type: {metadata.get('model_type', 'N/A').replace('_', ' ').title()}<br/>
        AI Model Loaded: {'Yes' if metadata.get('ai_model_loaded', False) else 'No'}<br/>
        Timestamp: {metadata.get('timestamp', 'N/A')}<br/>
        Generated by: Planetary Defense AI System v3.0
        """
        story.append(Paragraph(meta_text, styles['Normal']))
        story.append(Spacer(1, 0.2*inch))
        
        # Footer with disclaimer
        disclaimer = """
        <i>This report was generated by an AI-enhanced planetary defense decision support system. 
        All predictions are based on physics-based models and machine learning algorithms. 
        Recommendations should be verified by domain experts before mission implementation. 
        This system is for decision support and does not replace professional assessment.</i>
        """
        story.append(Paragraph(disclaimer, styles['Italic']))
        
        # Build PDF
        doc.build(story)
        pdf_data = buffer.getvalue()
        buffer.close()
        
        logger.info("✅ PDF briefing generated successfully")
        return pdf_data
        
    except Exception as e:
        logger.error(f"❌ PDF generation failed: {e}")
        return None

def calculate_difficulty(mission_params):
    """Calculate mission difficulty based on parameters."""
    lti_days = mission_params.get('lti_days', 0)
    delta_v = mission_params.get('required_dv_ms', 0)
    mass = mission_params.get('calculated_mass_kg', 0)
    
    if lti_days < 180 or delta_v > 0.02 or mass > 1e12:
        return "VERY HIGH"
    elif lti_days < 365 or delta_v > 0.01 or mass > 1e11:
        return "HIGH"
    elif lti_days < 730 or delta_v > 0.005 or mass > 1e10:
        return "MODERATE"
    else:
        return "LOW"