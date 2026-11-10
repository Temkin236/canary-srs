#!/usr/bin/env python3
"""
Captures high-resolution, genuine screenshots of the running Canary SRS web application
for GitHub repository presentation and portfolio documentation.
"""

import os
import subprocess
import sys
import time

PAGES = [
    {
        "filename": "docs/screenshots/01-landing-page.png",
        "url": "http://127.0.0.1:5173/",
        "title": "Landing Page & Product Philosophy",
    },
    {
        "filename": "docs/screenshots/02-task-preparation.png",
        "url": "http://127.0.0.1:5173/prepare",
        "title": "Task Preparation & Canary Marker Seeding",
    },
    {
        "filename": "docs/screenshots/03-dataset-audit.png",
        "url": "http://127.0.0.1:5173/audit",
        "title": "Dataset Ingestion & Audit Configuration",
    },
    {
        "filename": "docs/screenshots/04-audit-results.png",
        "url": "http://127.0.0.1:5173/results/sec_demo_review_2026_canary",
        "title": "Audit Summary & Multi-Format Report Export",
    },
    {
        "filename": "docs/screenshots/05-reviewer-dashboard.png",
        "url": "http://127.0.0.1:5173/dashboard",
        "title": "Enterprise Reviewer Dashboard & Analytics",
    },
    {
        "filename": "docs/screenshots/06-evidence-investigation.png",
        "url": "http://127.0.0.1:5173/audits/canary-audit-demo-8492",
        "title": "Evidence Adjudication Workspace",
    },
    {
        "filename": "docs/screenshots/07-accuracy-benchmark.png",
        "url": "http://127.0.0.1:5173/accuracy",
        "title": "Measured Empirical Accuracy Benchmark (Wilson 95% CI)",
    },
    {
        "filename": "docs/screenshots/08-how-it-works.png",
        "url": "http://127.0.0.1:5173/how-it-works",
        "title": "How It Works & Multi-Modal Detection Architecture",
    },
    {
        "filename": "docs/screenshots/09-privacy.png",
        "url": "http://127.0.0.1:5173/privacy",
        "title": "Privacy Invariants & 7-Day Ephemeral Retention Policy",
    },
    {
        "filename": "docs/screenshots/10-api-documentation.png",
        "url": "http://127.0.0.1:8000/docs",
        "title": "Interactive OpenAPI (Swagger) Documentation",
    },
    {
        "filename": "docs/screenshots/11-dataset-quality.png",
        "url": "http://127.0.0.1:5173/audits/canary-audit-demo-8492?tab=quality",
        "title": "Dataset Quality & Hygiene Analytics",
    },
]

def capture_all():
    os.makedirs("docs/screenshots", exist_ok=True)
    os.makedirs("docs/assets", exist_ok=True)
    success_count = 0

    for item in PAGES:
        output_file = item["filename"]
        url = item["url"]
        title = item["title"]

        cmd = [
            "chromium",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--virtual-time-budget=4000",
            "--window-size=1440,1000",
            f"--screenshot={output_file}",
            url,
        ]

        print(f"Capturing: {title} -> {output_file} ({url})")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if os.path.exists(output_file) and os.path.getsize(output_file) > 1000:
            size_kb = os.path.getsize(output_file) / 1024
            print(f"  ✓ Saved {output_file} ({size_kb:.1f} KB)")
            success_count += 1
        else:
            print(f"  ✗ Failed to capture {output_file}: {res.stderr}")

    print(f"\nScreenshot capture finished: {success_count}/{len(PAGES)} successful.")


if __name__ == "__main__":
    capture_all()
