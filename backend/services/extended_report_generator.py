from datetime import datetime
from pathlib import Path
from uuid import uuid4
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

from backend.models.asset import Asset
from backend.models.assessment import Assessment
from backend.models.incident import Incident, IncidentTimeline
from backend.models.report import Report
from backend.models.risk import Risk
from backend.models.vulnerability import Vulnerability


PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports" / "generated"


def _value(obj, *names, default="—"):
    for name in names:
        value = getattr(obj, name, None)
        if value is not None and value != "":
            return value
    return default


def _p(value):
    return Paragraph(
        escape(str(value)),
        ParagraphStyle(
            "cell",
            fontName="Helvetica",
            fontSize=8,
            leading=10,
        ),
    )


def _table(rows, widths=None):
    table = Table(
        rows,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f2937")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [colors.white, colors.HexColor("#f3f4f6")],
                ),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )

    return table


def _base_styles():
    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=20,
        leading=24,
        alignment=TA_CENTER,
        spaceAfter=12,
    )

    heading = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=13,
        leading=16,
        spaceBefore=10,
        spaceAfter=8,
    )

    body = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=6,
    )

    return title, heading, body


def _save_report(
    db,
    generated_by,
    report_type,
    title,
    file_prefix,
    story,
    summary,
):
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    now = datetime.utcnow()

    report_id = (
        f"RPT-{now.strftime('%Y%m%d%H%M%S')}-"
        f"{uuid4().hex[:6].upper()}"
    )

    file_name = (
        f"{file_prefix}_"
        f"{now.strftime('%Y%m%d_%H%M%S')}_"
        f"{uuid4().hex[:6].upper()}.pdf"
    )

    file_path = REPORT_DIR / file_name

    document = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=15,
        leftMargin=15,
        topMargin=15,
        bottomMargin=15,
        title=title,
        author="SecureSphere",
    )

    document.build(story)

    report = Report(
        report_id=report_id,
        report_type=report_type,
        generated_by=generated_by,
        generated_at=now,
        file_name=file_name,
        file_path=str(file_path),
        status="GENERATED",
        created_at=now,
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "id": report.id,
        "report_id": report.report_id,
        "report_type": report.report_type,
        "status": report.status,
        "file_name": report.file_name,
        "file_path": report.file_path,
        "generated_at": report.generated_at,
        "summary": summary,
    }


def build_vulnerability_assessment_report(db, generated_by=None):
    title, heading, body = _base_styles()

    vulnerabilities = (
        db.query(Vulnerability)
        .order_by(Vulnerability.id)
        .all()
    )

    high = sum(
        1 for v in vulnerabilities
        if str(v.severity).upper() in {"HIGH", "CRITICAL"}
    )

    story = [
        Paragraph(
            "SecureSphere Vulnerability Assessment Report",
            title,
        ),
        Paragraph(
            f"Generated: {datetime.utcnow().isoformat()} UTC",
            body,
        ),
        Paragraph(
            "Assessment Scope",
            heading,
        ),
        Paragraph(
            f"Total findings: {len(vulnerabilities)}. "
            f"High/Critical findings: {high}. "
            "This report summarizes authorized security assessment "
            "findings recorded in SecureSphere.",
            body,
        ),
        Paragraph("Vulnerability Findings", heading),
    ]

    rows = [[
        "ID",
        "Title",
        "Asset",
        "Category",
        "Severity",
        "Risk",
        "Status",
    ]]

    for v in vulnerabilities:
        rows.append([
            _p(v.vulnerability_id),
            _p(v.title),
            _p(v.asset_id),
            _p(v.category),
            _p(v.severity),
            _p(_value(v, "risk_level")),
            _p(v.status),
        ])

    story.append(
        _table(
            rows,
            [24 * 1, 105, 38, 72, 45, 38, 55],
        )
    )

    story.extend([
        Spacer(1, 10),
        Paragraph("Mitigation Recommendations", heading),
        Paragraph(
            "Prioritize remediation of HIGH and CRITICAL findings, "
            "apply vendor/security patches, enforce least privilege, "
            "strengthen authentication controls, validate input, "
            "and verify remediation through follow-up assessment.",
            body,
        ),
    ])

    return _save_report(
        db,
        generated_by,
        "VULNERABILITY_ASSESSMENT",
        "SecureSphere Vulnerability Assessment Report",
        "SECURESPHERE_VULNERABILITY_ASSESSMENT",
        story,
        f"{len(vulnerabilities)} vulnerability finding(s) documented.",
    )


def build_security_incident_report(db, generated_by=None):
    title, heading, body = _base_styles()

    incidents = (
        db.query(Incident)
        .order_by(Incident.id)
        .all()
    )

    story = [
        Paragraph(
            "SecureSphere Security Incident Report",
            title,
        ),
        Paragraph(
            f"Generated: {datetime.utcnow().isoformat()} UTC",
            body,
        ),
        Paragraph("Incident Summary", heading),
        Paragraph(
            f"{len(incidents)} incident(s) are recorded in SecureSphere. "
            "The report summarizes detection, investigation status, "
            "evidence, containment, root cause and resolution data.",
            body,
        ),
        Paragraph("Incident Register", heading),
    ]

    rows = [[
        "ID",
        "Title",
        "Asset",
        "Severity",
        "Status",
        "Detection Time",
    ]]

    for incident in incidents:
        rows.append([
            _p(incident.incident_id),
            _p(incident.title),
            _p(incident.asset_id),
            _p(incident.severity),
            _p(incident.status),
            _p(incident.detection_time),
        ])

    story.append(_table(rows, [58, 125, 38, 48, 55, 78]))

    story.extend([
        Spacer(1, 10),
        Paragraph("Investigation & Response", heading),
    ])

    for incident in incidents:
        story.append(
            Paragraph(
                f"<b>{escape(str(incident.incident_id))}</b> — "
                f"{escape(str(incident.title))}<br/>"
                f"Investigation: "
                f"{escape(str(_value(incident, 'investigation_notes')))}<br/>"
                f"Evidence: "
                f"{escape(str(_value(incident, 'evidence')))}<br/>"
                f"Containment: "
                f"{escape(str(_value(incident, 'containment_action')))}<br/>"
                f"Root Cause: "
                f"{escape(str(_value(incident, 'root_cause')))}<br/>"
                f"Resolution: "
                f"{escape(str(_value(incident, 'resolution')))}",
                body,
            )
        )

    return _save_report(
        db,
        generated_by,
        "SECURITY_INCIDENT",
        "SecureSphere Security Incident Report",
        "SECURESPHERE_SECURITY_INCIDENT",
        story,
        f"{len(incidents)} incident(s) documented.",
    )


def build_risk_assessment_report(db, generated_by=None):
    title, heading, body = _base_styles()

    risks = (
        db.query(Risk)
        .order_by(Risk.id)
        .all()
    )

    critical = sum(
        1 for r in risks
        if str(r.risk_level).upper() == "CRITICAL"
    )

    high = sum(
        1 for r in risks
        if str(r.risk_level).upper() == "HIGH"
    )

    story = [
        Paragraph(
            "SecureSphere Risk Assessment Report",
            title,
        ),
        Paragraph(
            f"Generated: {datetime.utcnow().isoformat()} UTC",
            body,
        ),
        Paragraph("Risk Overview", heading),
        Paragraph(
            f"Total risks: {len(risks)}. "
            f"Critical: {critical}. High: {high}. "
            "Risk scores are based on likelihood, impact and "
            "the platform's risk calculation model.",
            body,
        ),
        Paragraph("Risk Register", heading),
    ]

    rows = [[
        "Risk ID",
        "Asset",
        "Threat",
        "Score",
        "Level",
        "Status",
        "Mitigation",
    ]]

    for risk in risks:
        rows.append([
            _p(risk.risk_id),
            _p(risk.asset_id),
            _p(risk.threat),
            _p(risk.risk_score),
            _p(risk.risk_level),
            _p(risk.status),
            _p(_value(risk, "mitigation")),
        ])

    story.append(
        _table(
            rows,
            [55, 35, 85, 40, 45, 50, 110],
        )
    )

    story.extend([
        Spacer(1, 10),
        Paragraph("Mitigation Recommendations", heading),
        Paragraph(
            "Prioritize critical and high risks, address their "
            "associated vulnerabilities, apply least-privilege "
            "controls, strengthen authentication, patch exposed "
            "components and continuously monitor affected assets.",
            body,
        ),
    ])

    return _save_report(
        db,
        generated_by,
        "RISK_ASSESSMENT",
        "SecureSphere Risk Assessment Report",
        "SECURESPHERE_RISK_ASSESSMENT",
        story,
        f"{len(risks)} risk(s) documented.",
    )


def build_asset_security_report(db, generated_by=None):
    title, heading, body = _base_styles()

    assets = db.query(Asset).order_by(Asset.id).all()
    assessments = db.query(Assessment).all()
    vulnerabilities = db.query(Vulnerability).all()

    assessment_by_asset = {}

    for assessment in assessments:
        assessment_by_asset.setdefault(
            assessment.asset_id,
            []
        ).append(assessment)

    findings_by_asset = {}

    for vulnerability in vulnerabilities:
        if str(vulnerability.status).upper() not in {
            "RESOLVED",
            "CLOSED",
        }:
            findings_by_asset.setdefault(
                vulnerability.asset_id,
                []
            ).append(vulnerability)

    story = [
        Paragraph(
            "SecureSphere Asset Security Report",
            title,
        ),
        Paragraph(
            f"Generated: {datetime.utcnow().isoformat()} UTC",
            body,
        ),
        Paragraph("Asset Inventory & Security Status", heading),
        Paragraph(
            f"{len(assets)} asset(s) are currently registered. "
            "The report includes asset inventory, criticality, "
            "assessment status and open security findings.",
            body,
        ),
    ]

    rows = [[
        "Asset",
        "Name",
        "Type",
        "Criticality",
        "Status",
        "Assessments",
        "Open Findings",
    ]]

    for asset in assets:
        asset_name = _value(
            asset,
            "name",
            "asset_name",
            "hostname",
            "ip_address",
        )

        asset_type = _value(
            asset,
            "asset_type",
            "type",
            "category",
        )

        asset_assessments = assessment_by_asset.get(
            asset.id,
            []
        )

        assessment_status = (
            ", ".join(
                sorted(
                    {
                        str(a.status)
                        for a in asset_assessments
                    }
                )
            )
            if asset_assessments
            else "NOT ASSESSED"
        )

        rows.append([
            _p(asset.id),
            _p(asset_name),
            _p(asset_type),
            _p(_value(asset, "criticality")),
            _p(_value(asset, "status")),
            _p(assessment_status),
            _p(len(findings_by_asset.get(asset.id, []))),
        ])

    story.append(
        _table(
            rows,
            [35, 95, 65, 55, 55, 80, 60],
        )
    )

    story.extend([
        Spacer(1, 10),
        Paragraph("Open Security Findings", heading),
    ])

    for asset in assets:
        findings = findings_by_asset.get(asset.id, [])

        if not findings:
            continue

        story.append(
            Paragraph(
                f"<b>Asset {escape(str(asset.id))}</b>",
                body,
            )
        )

        for finding in findings:
            story.append(
                Paragraph(
                    f"• {escape(str(finding.vulnerability_id))}: "
                    f"{escape(str(finding.title))} — "
                    f"{escape(str(finding.severity))}",
                    body,
                )
            )

    return _save_report(
        db,
        generated_by,
        "ASSET_SECURITY",
        "SecureSphere Asset Security Report",
        "SECURESPHERE_ASSET_SECURITY",
        story,
        f"{len(assets)} asset(s) documented.",
    )
