import html
from typing import List

from app.models.audit import Audit, CheckResult, Finding


def generate_html_report(
    audit: Audit,
    findings: List[Finding],
    check_results: List[CheckResult],
) -> str:
    """
    Generates a 100% self-contained offline HTML report with inline CSS and XSS escaping (FR-38).
    Zero external font, script, or image dependencies.
    """
    metrics = audit.summary_metrics or {}
    total_answers = metrics.get("total_answers", audit.answers_count)
    total_workers = metrics.get("total_workers", audit.workers_count)
    flagged_workers = metrics.get("flagged_workers_count", audit.flagged_workers_count)
    high_count = metrics.get("high_confidence_findings", 0)
    med_count = metrics.get("medium_confidence_findings", 0)
    low_count = metrics.get("low_confidence_findings", 0)

    rows_html = []
    for f in findings:
        conf = f.evidence_confidence or "Low"
        badge_style = {
            "High": "background:#FEE2E2; color:#991B1B; border:1px solid #FCA5A5;",
            "Medium": "background:#FEF3C7; color:#92400E; border:1px solid #FCD34D;",
            "Low": "background:#F3F4F6; color:#374151; border:1px solid #D1D5DB;",
        }.get(conf, "background:#F3F4F6; color:#374151;")

        evidence_snippet = ""
        if f.evidence_text:
            evidence_snippet = (
                '<div style="font-family:monospace; font-size:11px; background:#FAF5EE; '
                "padding:6px 10px; border-radius:4px; margin-top:6px; "
                'border:1px solid #E8DEC8; word-break:break-all;">'
                f"{html.escape(f.evidence_text)}"
                "</div>"
            )

        badge_span = (
            f'<span style="display:inline-block; padding:2px 8px; border-radius:12px; '
            f'font-size:11px; font-weight:600; {badge_style}">'
            f"{html.escape(conf)}</span>"
        )

        row = (
            '<tr style="border-bottom:1px solid #E7E5E4;">'
            f'<td style="padding:10px 12px; font-family:monospace; font-size:12px;">'
            f"{html.escape(f.worker_id)}</td>"
            f'<td style="padding:10px 12px; font-family:monospace; font-size:12px;">'
            f"{html.escape(f.task_id)}</td>"
            f'<td style="padding:10px 12px; font-size:12px;">{html.escape(f.check_identifier)}</td>'
            f'<td style="padding:10px 12px;">{badge_span}</td>'
            f'<td style="padding:10px 12px; font-size:12px; color:#44403C;">'
            f"<div>{html.escape(f.explanation)}</div>{evidence_snippet}</td>"
            "</tr>"
        )
        rows_html.append(row)

    findings_tbody = (
        "".join(rows_html)
        if rows_html
        else (
            '<tr><td colspan="5" style="padding:24px; text-align:center; '
            'color:#78716C; font-size:13px;">No contamination findings detected. '
            "Dataset appears clean across all checks.</td></tr>"
        )
    )

    created_str = audit.created_at.strftime("%Y-%m-%d %H:%M UTC") if audit.created_at else "N/A"
    expires_str = audit.expires_at.strftime("%Y-%m-%d %H:%M UTC") if audit.expires_at else "N/A"
    worker_color = "#DC2626" if flagged_workers > 0 else "#16A34A"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Canary SRS — Audit Report {html.escape(audit.id[:8])}</title>
<style>
  body {{
    margin: 0;
    padding: 32px 16px;
    background-color: #FAF8F5;
    color: #1C1917;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    line-height: 1.5;
  }}
  .container {{ max-width: 960px; margin: 0 auto; }}
  .card {{
    background: #FFFFFF;
    border: 1px solid #E7E5E4;
    border-radius: 8px;
    padding: 24px;
    margin-bottom: 24px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.02);
  }}
  .banner {{
    background: #FFFBEB;
    border-left: 4px solid #B8860B;
    padding: 16px 20px;
    border-radius: 4px;
    margin-bottom: 24px;
  }}
  .banner-title {{
    font-weight: 700;
    font-size: 13px;
    color: #92400E;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
  }}
  .banner-text {{ font-size: 12px; color: #78350F; }}
  .grid {{
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
    gap: 16px;
    margin-bottom: 24px;
  }}
  .metric-box {{
    background: #FAF8F5;
    border: 1px solid #E7E5E4;
    border-radius: 6px;
    padding: 14px;
    text-align: center;
  }}
  .metric-value {{ font-size: 24px; font-weight: 700; color: #1C1917; margin-bottom: 2px; }}
  .metric-label {{ font-size: 11px; text-transform: uppercase; color: #78716C; }}
  table {{ width: 100%; border-collapse: collapse; text-align: left; }}
  th {{
    background: #F5F5F4;
    padding: 10px 12px;
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #57534E;
    border-bottom: 2px solid #E7E5E4;
  }}
  .footer {{ text-align: center; font-size: 11px; color: #A8A29E; margin-top: 32px; }}
</style>
</head>
<body>
<div class="container">
  <div style="margin-bottom:24px;">
    <div style="font-size:12px; font-weight:600; color:#B8860B; text-transform:uppercase;">
      Canary SRS &bull; Contamination Audit Report
    </div>
    <h1 style="margin:4px 0 0 0; font-size:26px; font-weight:600; color:#1C1917;">
      Dataset Integrity Findings
    </h1>
    <div style="font-size:12px; color:#78716C; margin-top:4px;">
      Audit ID: <code style="font-family:monospace;">{html.escape(audit.id)}</code> &bull;
      Generated: {created_str} &bull; Ephemeral Retention Expiry: {expires_str}
    </div>
  </div>

  <div class="banner">
    <div class="banner-title">Invariant 1: Evidence, Not Verdict</div>
    <div class="banner-text">
      This report provides forensic evidence for human review. Findings do not prove AI
      authorship, fraud, or worker cheating. Never use these results to automatically reject
      submissions or withhold compensation without human review.
    </div>
  </div>

  <div class="card">
    <h2 style="font-size:16px; margin:0 0 16px 0; font-weight:600;">Executive Metrics</h2>
    <div class="grid">
      <div class="metric-box">
        <div class="metric-value">{total_answers}</div>
        <div class="metric-label">Total Answers</div>
      </div>
      <div class="metric-box">
        <div class="metric-value">{total_workers}</div>
        <div class="metric-label">Total Workers</div>
      </div>
      <div class="metric-box">
        <div class="metric-value" style="color:{worker_color};">{flagged_workers}</div>
        <div class="metric-label">Flagged Workers</div>
      </div>
      <div class="metric-box">
        <div class="metric-value" style="color:#DC2626;">{high_count}</div>
        <div class="metric-label">High Confidence</div>
      </div>
      <div class="metric-box">
        <div class="metric-value" style="color:#D97706;">{med_count}</div>
        <div class="metric-label">Medium Conf</div>
      </div>
      <div class="metric-box">
        <div class="metric-value" style="color:#6B7280;">{low_count}</div>
        <div class="metric-label">Low Conf</div>
      </div>
    </div>
  </div>

  <div class="card" style="padding:0; overflow:hidden;">
    <div style="padding:16px 20px; border-bottom:1px solid #E7E5E4; background:#FAFAF9;">
      <h2 style="font-size:15px; margin:0; font-weight:600; color:#1C1917;">
        Forensic Evidence Findings ({len(findings)})
      </h2>
    </div>
    <div style="overflow-x:auto;">
      <table>
        <thead>
          <tr>
            <th>Worker ID</th>
            <th>Task ID</th>
            <th>Check</th>
            <th>Confidence</th>
            <th>Forensic Explanation &amp; Excerpt</th>
          </tr>
        </thead>
        <tbody>
          {findings_tbody}
        </tbody>
      </table>
    </div>
  </div>

  <div class="footer">
    Generated by Canary SRS &bull; 100% Offline Static Export &bull; No External Network Connections
  </div>
</div>
</body>
</html>"""
