#!/usr/bin/env python3
"""
Generates a professional GitHub social preview image (1280x640) for Canary SRS.
Uses headless Chromium to render an authentic, elegantly styled HTML layout.
"""

import os
import subprocess
import tempfile

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,600;1,6..72,400&family=JetBrains+Mono:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap');

  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    width: 1280px;
    height: 640px;
    background: #0C0F17;
    color: #F8FAFC;
    font-family: 'Inter', sans-serif;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 64px 80px;
    position: relative;
    overflow: hidden;
  }

  /* Subtle background grid and accent aura */
  .grid-pattern {
    position: absolute;
    inset: 0;
    background-image: 
      linear-gradient(to right, rgba(255,255,255,0.03) 1px, transparent 1px),
      linear-gradient(to bottom, rgba(255,255,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
  }
  .accent-glow {
    position: absolute;
    top: -120px;
    right: -80px;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(217, 119, 6, 0.15) 0%, rgba(217, 119, 6, 0) 70%);
    pointer-events: none;
  }
  .blue-glow {
    position: absolute;
    bottom: -150px;
    left: -100px;
    width: 500px;
    height: 500px;
    background: radial-gradient(circle, rgba(59, 130, 246, 0.08) 0%, rgba(59, 130, 246, 0) 70%);
    pointer-events: none;
  }

  /* Header */
  .header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    z-index: 10;
  }
  .brand {
    display: flex;
    align-items: center;
    gap: 14px;
  }
  .brand-logo {
    width: 44px;
    height: 44px;
    border-radius: 10px;
    background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%);
    color: #0C0F17;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: 'Newsreader', serif;
    font-size: 26px;
    font-weight: 700;
    box-shadow: 0 4px 20px rgba(217, 119, 6, 0.3);
  }
  .brand-meta {
    display: flex;
    flex-direction: column;
  }
  .brand-name {
    font-size: 18px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: #F8FAFC;
  }
  .brand-sub {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .badge {
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    padding: 6px 14px;
    border-radius: 20px;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #FBBF24;
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .badge-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #FBBF24;
    box-shadow: 0 0 8px #FBBF24;
  }

  /* Center Content */
  .main-content {
    position: relative;
    z-index: 10;
    margin: auto 0;
  }
  .title-tag {
    display: inline-block;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12px;
    font-weight: 600;
    color: #F59E0B;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 16px;
  }
  .title {
    font-family: 'Newsreader', Georgia, serif;
    font-size: 58px;
    line-height: 1.08;
    font-weight: 600;
    letter-spacing: -0.03em;
    color: #FFFFFF;
    margin-bottom: 18px;
    max-width: 1000px;
  }
  .subtitle {
    font-size: 20px;
    line-height: 1.45;
    color: #94A3B8;
    max-width: 860px;
    font-weight: 400;
  }
  .subtitle strong {
    color: #E2E8F0;
    font-weight: 600;
  }

  /* Footer */
  .footer {
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    z-index: 10;
    border-top: 1px solid rgba(255, 255, 255, 0.08);
    padding-top: 20px;
  }
  .features-pills {
    display: flex;
    gap: 8px;
  }
  .pill {
    font-family: 'JetBrains Mono', monospace;
    font-size: 10.5px;
    color: #CBD5E1;
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.08);
    padding: 5px 10px;
    border-radius: 6px;
  }
  .author-info {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: #94A3B8;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .author-name {
    color: #F8FAFC;
    font-weight: 600;
  }
</style>
</head>
<body>
  <div class="grid-pattern"></div>
  <div class="accent-glow"></div>
  <div class="blue-glow"></div>

  <!-- Header -->
  <div class="header">
    <div class="brand">
      <div class="brand-logo">C</div>
      <div class="brand-meta">
        <span class="brand-name">CANARY SRS</span>
        <span class="brand-sub">Contamination Audit for Human Datasets</span>
      </div>
    </div>
    <div class="badge">
      <span class="badge-dot"></span>
      <span>Evidence, Not Verdict</span>
    </div>
  </div>

  <!-- Main Showcase Title -->
  <div class="main-content">
    <div class="title-tag">Dataset Integrity & Human Review Platform</div>
    <h1 class="title">Privacy-First Contamination Investigation for Crowd & Vendor Datasets</h1>
    <p class="subtitle">
      Systematically surfaces <strong>hidden canary markers</strong>, <strong>AI reference peer distributions</strong>, 
      and <strong>cross-worker duplicates</strong> through transparent, reproducible, and offline-capable evidence.
    </p>
  </div>

  <!-- Footer Metadata -->
  <div class="footer">
    <div class="features-pills">
      <span class="pill">React 18 + TypeScript</span>
      <span class="pill">FastAPI + Python 3.12</span>
      <span class="pill">Zero Stylometric Guesswork</span>
      <span class="pill">7-Day Ephemeral Retention</span>
    </div>
    <div class="author-info">
      <span>Engineered by</span>
      <span class="author-name">Temkin Abdulmelik</span>
      <span>• Temkin236/canary-srs</span>
    </div>
  </div>
</body>
</html>
"""

def generate():
    os.makedirs("docs/assets", exist_ok=True)
    out_file = os.path.abspath("docs/assets/social-preview.png")

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(HTML_TEMPLATE)
        temp_html = f.name

    try:
        cmd = [
            "chromium",
            "--headless",
            "--disable-gpu",
            "--no-sandbox",
            "--window-size=1280,640",
            f"--screenshot={out_file}",
            f"file://{temp_html}",
        ]
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if os.path.exists(out_file) and os.path.getsize(out_file) > 1000:
            print(f"✓ Generated social preview: {out_file} ({os.path.getsize(out_file)/1024:.1f} KB)")
        else:
            print(f"✗ Failed generating social preview: {res.stderr}")
    finally:
        if os.path.exists(temp_html):
            os.remove(temp_html)


if __name__ == "__main__":
    generate()
