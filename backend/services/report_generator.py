import os
from collections import Counter
from datetime import datetime
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
)

from sqlalchemy.orm import Session

from backend.models.asset import Asset
from backend.models.alert import Alert
from backend.models.assessment import Assessment
from backend.models.automation import AutomationLog
from backend.models.incident import Incident
from backend.models.risk import Risk
from backend.models.security_event import SecurityEvent
from backend.models.vulnerability import Vulnerability
from backend.models.report import Report
from backend.services.posture_score import (
    calculate_posture_score,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
REPORT_DIR = PROJECT_ROOT / "reports" / "generated"


def _count_by(items, attribute):
    return Counter(
        getattr(item, attribute)
        for item in items
        if getattr(item, attribute, None) is not None
    )


def _table(data, widths=None):
    table = Table(
        data,
        colWidths=widths,
        repeatRows=1,
        hAlign="LEFT",
    )

    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.HexColor("#1f2937"),
                ),
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.white,
                ),
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),
                (
                    "FONTNAME",
                    (0, 1),
                    (-1, -1),
                    "Helvetica",
                ),
                (
                    "FONTSIZE",
                    (0, 0),
                    (-1, -1),
                    8,
                ),
                (
                    "GRID",
                    (0, 0),
                    (-1, -1),
                    0.4,
                    colors.grey,
                ),
                (
                    "VALIGN",
                    (0, 0),
                    (-1, -1),
                    "TOP",
                ),
                (
                    "ROWBACKGROUNDS",
                    (0, 1),
                    (-1, -1),
                    [
                        colors.white,
                        colors.HexColor("#f3f4f6"),
                    ],
                ),
                (
                    "LEFTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "RIGHTPADDING",
                    (0, 0),
                    (-1, -1),
                    6,
                ),
                (
                    "TOPPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, -1),
                    5,
                ),
            ]
        )
    )

    return table


def _paragraph(text, style):
    return Paragraph(
        str(text).replace("&", "&amp;"),
        style,
    )


def build_security_posture_report(
    db: Session,
    generated_by: int | None = None,
):
    """
    Generate a Security Posture Report from the
    current SecureSphere database state.

    Returns report metadata and aggregated metrics.
    """

    REPORT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    assets = db.query(Asset).all()
    alerts = db.query(Alert).all()
    incidents = db.query(Incident).all()
    vulnerabilities = db.query(Vulnerability).all()
    risks = db.query(Risk).all()
    assessments = db.query(Assessment).all()
    events = db.query(SecurityEvent).all()
    automation_logs = (
        db.query(AutomationLog)
        .order_by(
            AutomationLog.id.desc()
        )
        .limit(20)
        .all()
    )

    generated_at = datetime.utcnow()

    report_id = (
        f"RPT-{generated_at.strftime('%Y%m%d%H%M%S')}"
    )

    file_name = (
        f"SECURESPHERE_SECURITY_POSTURE_"
        f"{generated_at.strftime('%Y%m%d_%H%M%S')}.pdf"
    )

    file_path = REPORT_DIR / file_name

    total_assets = len(assets)
    active_assets = sum(
        1
        for asset in assets
        if asset.status == "ACTIVE"
    )

    alert_severity = _count_by(
        alerts,
        "severity",
    )

    incident_severity = _count_by(
        incidents,
        "severity",
    )

    incident_status = _count_by(
        incidents,
        "status",
    )

    vulnerability_severity = _count_by(
        vulnerabilities,
        "severity",
    )

    vulnerability_status = _count_by(
        vulnerabilities,
        "status",
    )

    risk_level = _count_by(
        risks,
        "risk_level",
    )

    risk_status = _count_by(
        risks,
        "status",
    )

    assessment_status = _count_by(
        assessments,
        "status",
    )

    critical_alerts = alert_severity.get(
        "CRITICAL",
        0,
    )

    high_alerts = alert_severity.get(
        "HIGH",
        0,
    )

    open_incidents = sum(
        1
        for incident in incidents
        if incident.status
        in {
            "OPEN",
            "INVESTIGATING",
            "CONTAINED",
        }
    )

    critical_incidents = sum(
        1
        for incident in incidents
        if incident.severity == "CRITICAL"
        and incident.status
        not in {
            "RESOLVED",
            "CLOSED",
        }
    )

    high_vulnerabilities = sum(
        1
        for vulnerability in vulnerabilities
        if vulnerability.severity
        in {
            "HIGH",
            "CRITICAL",
        }
        and vulnerability.status
        not in {
            "RESOLVED",
            "CLOSED",
        }
    )

    open_high_risks = sum(
        1
        for risk in risks
        if risk.risk_level
        in {
            "HIGH",
            "CRITICAL",
        }
        and risk.status
        not in {
            "CLOSED",
            "MITIGATED",
        }
    )

    posture = calculate_posture_score(
        total_assets=total_assets,
        active_assets=active_assets,
        critical_alerts=critical_alerts,
        high_alerts=high_alerts,
        open_incidents=open_incidents,
        critical_incidents=critical_incidents,
        high_vulnerabilities=high_vulnerabilities,
        open_high_risks=open_high_risks,
    )

    security_score = posture.score
    security_status = posture.status
    score_components = posture.components
    findings = []

    if critical_alerts:
        findings.append(
            f"{critical_alerts} critical alert(s) require attention."
        )

    if high_alerts:
        findings.append(
            f"{high_alerts} high-severity alert(s) require review."
        )

    if critical_incidents:
        findings.append(
            f"{critical_incidents} unresolved critical incident(s) require investigation."
        )

    if high_vulnerabilities:
        findings.append(
            f"{high_vulnerabilities} unresolved high/critical vulnerability(ies) require remediation."
        )

    if open_high_risks:
        findings.append(
            f"{open_high_risks} open high/critical risk(s) require treatment."
        )

    if not findings:
        findings.append(
            "No immediate high-priority security findings were identified."
        )

    recommendations = [
        "Review unresolved critical and high-severity alerts.",
        "Continue investigation and remediation of open incidents.",
        "Prioritize remediation of unresolved high and critical vulnerabilities.",
        "Review high and critical risk treatment decisions periodically.",
        "Maintain automated security health and integrity monitoring.",
    ]

    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontSize=22,
        leading=27,
        spaceAfter=12,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        alignment=TA_CENTER,
        fontSize=10,
        textColor=colors.grey,
        spaceAfter=18,
    )

    heading_style = ParagraphStyle(
        "ReportHeading",
        parent=styles["Heading2"],
        fontSize=14,
        leading=18,
        spaceBefore=12,
        spaceAfter=8,
    )

    body_style = ParagraphStyle(
        "ReportBody",
        parent=styles["BodyText"],
        fontSize=9,
        leading=13,
        spaceAfter=6,
    )

    small_style = ParagraphStyle(
        "ReportSmall",
        parent=styles["BodyText"],
        fontSize=8,
        leading=11,
    )

    doc = SimpleDocTemplate(
        str(file_path),
        pagesize=A4,
        rightMargin=15 * mm,
        leftMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title="SecureSphere Security Posture Report",
        author="SecureSphere",
    )

    story = []

    # -------------------------------------------------
    # Cover
    # -------------------------------------------------

    story.append(
        Spacer(1, 25 * mm)
    )

    story.append(
        Paragraph(
            "SecureSphere",
            title_style,
        )
    )

    story.append(
        Paragraph(
            "Security Posture Report",
            title_style,
        )
    )

    story.append(
        Paragraph(
            f"Report ID: {report_id}<br/>"
            f"Generated: {generated_at.strftime('%Y-%m-%d %H:%M:%S')} UTC",
            subtitle_style,
        )
    )

    story.append(
        Spacer(1, 10 * mm)
    )

    story.append(
        _table(
            [
                ["Security Status", "Value"],
		["Security Posture Score", f"{security_score} / 100"],
                ["Overall Status", security_status],
                ["Total Assets", total_assets],
                ["Active Assets", active_assets],
                ["Total Alerts", len(alerts)],
                ["Open Incidents", open_incidents],
                ["Open High/Critical Vulnerabilities", high_vulnerabilities],
                ["Open High/Critical Risks", open_high_risks],
            ],
            widths=[90 * mm, 75 * mm],
        )
    )

    story.append(
        PageBreak()
    )

    # -------------------------------------------------
    # Executive Summary
    # -------------------------------------------------

    story.append(
        Paragraph(
            "1. Executive Summary",
            heading_style,
        )
    )

    story.append(
        _paragraph(
            (
                f"SecureSphere assessed the current security posture as "
		f"<b>{security_score} / 100</b>. The platform currently monitors "
		f"<b>{security_score} / 100</b>."
                f"{total_assets} asset(s), of which {active_assets} are active. "
                f"The environment contains {len(alerts)} alert(s), "
                f"{len(incidents)} incident(s), {len(vulnerabilities)} "
                f"vulnerability finding(s), and {len(risks)} risk record(s)."
            ),
            body_style,
        )
    )

    story.append(
        _paragraph(
            (
                "The following findings and recommendations are based on "
                "the current SecureSphere database state at report generation time."
            ),
            body_style,
        )
    )

    # -------------------------------------------------
    # Security Posture Score
    # -------------------------------------------------

    story.append(
        Paragraph(
            "2. Security Posture Score",
            heading_style,
        )
    )

    story.append(
        _paragraph(
            (
                f"The calculated Security Posture Score is "
                f"<b>{security_score} / 100</b>, classified as "
                f"<b>{security_status}</b>. The score is calculated "
                f"from unresolved alerts, incidents, vulnerabilities, "
                f"risks, and asset health."
            ),
            body_style,
        )
    )

    score_rows = [
        ["Score Component", "Penalty"],
        [
            "Alerts",
            score_components["alert_penalty"],
        ],
        [
            "Incidents",
            score_components["incident_penalty"],
        ],
        [
            "Vulnerabilities",
            score_components["vulnerability_penalty"],
        ],
        [
            "Risks",
            score_components["risk_penalty"],
        ],
        [
            "Asset Health",
            score_components["asset_penalty"],
        ],
        [
            "Total Penalty",
            score_components["total_penalty"],
        ],
        [
            "Final Score",
            f"{security_score} / 100",
        ],
    ]

    story.append(
        _table(
            score_rows,
            widths=[100 * mm, 65 * mm],
        )
    )

    story.append(
        Spacer(1, 6)
    )

    story.append(
        _paragraph(
            (
                "Scoring interpretation: 80–100 indicates HEALTHY, "
                "60–79 indicates WARNING, and 0–59 indicates CRITICAL."
            ),
            small_style,
        )
    )

    # -------------------------------------------------
    # Assets
    # -------------------------------------------------

    story.append(
        Paragraph(
            "2. Asset Overview",
            heading_style,
        )
    )

    asset_type_counts = _count_by(
        assets,
        "asset_type",
    )

    asset_rows = [
        ["Metric", "Value"],
        ["Total Assets", total_assets],
        ["Active", active_assets],
        [
            "Inactive",
            sum(
                1
                for a in assets
                if a.status == "INACTIVE"
            ),
        ],
        [
            "Retired",
            sum(
                1
                for a in assets
                if a.status == "RETIRED"
            ),
        ],
    ]

    for asset_type, count in sorted(
        asset_type_counts.items()
    ):
        asset_rows.append(
            [
                f"Asset Type: {asset_type}",
                count,
            ]
        )

    story.append(
        _table(
            asset_rows,
            widths=[100 * mm, 65 * mm],
        )
    )

    # -------------------------------------------------
    # Alerts
    # -------------------------------------------------

    story.append(
        Paragraph(
            "3. Alert Summary",
            heading_style,
        )
    )

    alert_rows = [
        ["Severity", "Count"],
    ]

    for severity in [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
        "INFORMATIONAL",
    ]:
        alert_rows.append(
            [
                severity,
                alert_severity.get(
                    severity,
                    0,
                ),
            ]
        )

    story.append(
        _table(
            alert_rows,
            widths=[100 * mm, 65 * mm],
        )
    )

    # -------------------------------------------------
    # Incidents
    # -------------------------------------------------

    story.append(
        Paragraph(
            "4. Incident Summary",
            heading_style,
        )
    )

    incident_rows = [
        ["Severity", "Count"],
    ]

    for severity in [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
        "INFORMATIONAL",
    ]:
        incident_rows.append(
            [
                severity,
                incident_severity.get(
                    severity,
                    0,
                ),
            ]
        )

    story.append(
        _table(
            incident_rows,
            widths=[100 * mm, 65 * mm],
        )
    )

    story.append(
        Spacer(1, 5)
    )

    story.append(
        _table(
            [
                ["Status", "Count"],
                [
                    "OPEN",
                    incident_status.get(
                        "OPEN",
                        0,
                    ),
                ],
                [
                    "INVESTIGATING",
                    incident_status.get(
                        "INVESTIGATING",
                        0,
                    ),
                ],
                [
                    "CONTAINED",
                    incident_status.get(
                        "CONTAINED",
                        0,
                    ),
                ],
                [
                    "RESOLVED",
                    incident_status.get(
                        "RESOLVED",
                        0,
                    ),
                ],
                [
                    "CLOSED",
                    incident_status.get(
                        "CLOSED",
                        0,
                    ),
                ],
            ],
            widths=[100 * mm, 65 * mm],
        )
    )

    # -------------------------------------------------
    # Vulnerabilities
    # -------------------------------------------------

    story.append(
        Paragraph(
            "5. Vulnerability Summary",
            heading_style,
        )
    )

    vulnerability_rows = [
        ["Severity", "Count"],
    ]

    for severity in [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
        "INFORMATIONAL",
    ]:
        vulnerability_rows.append(
            [
                severity,
                vulnerability_severity.get(
                    severity,
                    0,
                ),
            ]
        )

    story.append(
        _table(
            vulnerability_rows,
            widths=[100 * mm, 65 * mm],
        )
    )

    story.append(
        Spacer(1, 5)
    )

    story.append(
        _table(
            [
                ["Status", "Count"],
                [
                    "OPEN",
                    vulnerability_status.get(
                        "OPEN",
                        0,
                    ),
                ],
                [
                    "IN_PROGRESS",
                    vulnerability_status.get(
                        "IN_PROGRESS",
                        0,
                    ),
                ],
                [
                    "RESOLVED",
                    vulnerability_status.get(
                        "RESOLVED",
                        0,
                    ),
                ],
                [
                    "CLOSED",
                    vulnerability_status.get(
                        "CLOSED",
                        0,
                    ),
                ],
                [
                    "ACCEPTED_RISK",
                    vulnerability_status.get(
                        "ACCEPTED_RISK",
                        0,
                    ),
                ],
            ],
            widths=[100 * mm, 65 * mm],
        )
    )

    # -------------------------------------------------
    # Risk
    # -------------------------------------------------

    story.append(
        Paragraph(
            "6. Risk Summary",
            heading_style,
        )
    )

    risk_rows = [
        ["Risk Level", "Count"],
    ]

    for level in [
        "CRITICAL",
        "HIGH",
        "MEDIUM",
        "LOW",
    ]:
        risk_rows.append(
            [
                level,
                risk_level.get(
                    level,
                    0,
                ),
            ]
        )

    story.append(
        _table(
            risk_rows,
            widths=[100 * mm, 65 * mm],
        )
    )

    story.append(
        Spacer(1, 5)
    )

    story.append(
        _table(
            [
                ["Status", "Count"],
                [
                    "OPEN",
                    risk_status.get(
                        "OPEN",
                        0,
                    ),
                ],
                [
                    "MITIGATED",
                    risk_status.get(
                        "MITIGATED",
                        0,
                    ),
                ],
                [
                    "ACCEPTED",
                    risk_status.get(
                        "ACCEPTED",
                        0,
                    ),
                ],
                [
                    "CLOSED",
                    risk_status.get(
                        "CLOSED",
                        0,
                    ),
                ],
            ],
            widths=[100 * mm, 65 * mm],
        )
    )

    # -------------------------------------------------
    # Assessments
    # -------------------------------------------------

    story.append(
        Paragraph(
            "7. Assessment Summary",
            heading_style,
        )
    )

    assessment_rows = [
        ["Assessment Status", "Count"],
    ]

    for status in [
        "PLANNED",
        "IN_PROGRESS",
        "COMPLETED",
        "CANCELLED",
    ]:
        assessment_rows.append(
            [
                status,
                assessment_status.get(
                    status,
                    0,
                ),
            ]
        )

    story.append(
        _table(
            assessment_rows,
            widths=[100 * mm, 65 * mm],
        )
    )

    # -------------------------------------------------
    # Automation
    # -------------------------------------------------

    story.append(
        Paragraph(
            "8. Automation & Integrity",
            heading_style,
        )
    )

    latest_automation = {}

    for log in automation_logs:
        if log.automation_name not in latest_automation:
            latest_automation[
                log.automation_name
            ] = log

    automation_rows = [
        [
            "Automation",
            "Execution",
            "Result",
        ]
    ]

    for name, log in sorted(
        latest_automation.items()
    ):
        result = "RECORDED"

        if log.output_data:
            try:
                import json

                output = json.loads(
                    log.output_data
                )

                result = output.get(
                    "status",
                    result,
                )

            except Exception:
                pass

        automation_rows.append(
            [
                name,
                log.execution_time.strftime(
                    "%Y-%m-%d %H:%M"
                ),
                result,
            ]
        )

    if len(automation_rows) == 1:
        automation_rows.append(
            [
                "No automation executions",
                "-",
                "-",
            ]
        )

    story.append(
        _table(
            automation_rows,
            widths=[
                65 * mm,
                50 * mm,
                50 * mm,
            ],
        )
    )

    # -------------------------------------------------
    # Key Findings
    # -------------------------------------------------

    story.append(
        Paragraph(
            "9. Key Findings",
            heading_style,
        )
    )

    for finding in findings:
        story.append(
            _paragraph(
                f"• {finding}",
                body_style,
            )
        )

    # -------------------------------------------------
    # Recommendations
    # -------------------------------------------------

    story.append(
        Paragraph(
            "10. Recommendations",
            heading_style,
        )
    )

    for recommendation in recommendations:
        story.append(
            _paragraph(
                f"• {recommendation}",
                body_style,
            )
        )

    # -------------------------------------------------
    # Footer
    # -------------------------------------------------

    def footer(canvas, document):
        canvas.saveState()

        canvas.setFont(
            "Helvetica",
            7,
        )

        canvas.setFillColor(
            colors.grey
        )

        canvas.drawString(
            15 * mm,
            8 * mm,
            "SecureSphere Security Posture Report",
        )

        canvas.drawRightString(
            A4[0] - 15 * mm,
            8 * mm,
            f"Page {document.page}",
        )

        canvas.restoreState()

    doc.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer,
    )

    report = Report(
        report_id=report_id,
        report_type="SECURITY_POSTURE",
        generated_by=generated_by,
        generated_at=generated_at,
        file_name=file_name,
        file_path=str(file_path),
        status="GENERATED",
    )

    db.add(report)
    db.commit()
    db.refresh(report)

    return {
        "report_id": report_id,
        "report_type": "SECURITY_POSTURE",
        "generated_at": generated_at,
        "file_name": file_name,
        "file_path": str(file_path),
        "status": "GENERATED",
        "metrics": {
            "assets": total_assets,
            "alerts": len(alerts),
            "incidents": len(incidents),
            "vulnerabilities": len(vulnerabilities),
            "risks": len(risks),
            "assessments": len(assessments),
            "security_events": len(events),
        },
        "security_score": security_score,
	"security_status": security_status,
	"score_components": score_components,
    }
