from __future__ import annotations

import html
import re
from pathlib import Path

from pypdf import PdfReader


PDF_PATH = Path(r"C:\Users\paras\Downloads\RDM-CV detailed 18-Jul-2023 final.pdf")
OUT_PATH = Path("rdmichael_cv.html")


def extract_lines(pdf_path: Path) -> list[str]:
    reader = PdfReader(str(pdf_path))
    lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text() or ""
        for raw in text.splitlines():
            line = " ".join(raw.replace("\uf0d8", "•").split())
            if line:
                lines.append(line)
    return lines


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return value.strip("-") or "section"


def is_major_heading(line: str) -> str | None:
    if line.startswith("**") and line.endswith("**"):
        return line.strip("* ").replace(" **", "")
    if re.fullmatch(r"Annexure\s*-?\s*\d+", line, flags=re.I):
        return line
    return None


def is_minor_heading(line: str) -> bool:
    headings = {
        "Research Interest",
        "Teaching",
        "Research",
        "Books",
        "Journals and chapters",
        "Patents",
        "International Conferences Abroad",
        "International Conferences in India",
        "National Conferences",
        "Invited lectures on Fish Immunology and related areas delivered at",
        "Major Research Projects completed in the last 15 years",
        "Membership in Science Professional Societies",
    }
    return line.strip("* ") in headings


def is_list_item(line: str) -> bool:
    return bool(
        re.match(r"^(•|\d+\.|[IVX]+\.)\s+", line)
        or re.match(r"^(19|20)\d{2}\b", line)
        or re.match(r"^[A-Z][A-Za-z.\s]+-\d+", line)
    )


def build_content(lines: list[str]) -> tuple[str, list[tuple[str, str]]]:
    out: list[str] = []
    nav: list[tuple[str, str]] = []
    in_list = False
    seen_ids: set[str] = set()
    section_open = False

    def close_list() -> None:
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    for line in lines:
        if line == "CURRICULUM VITAE (Detailed)":
            continue
        if line in {
            "rdmichael2000@gmail.com",
            "linkedin.com/in/r-dinakaran-",
            "michael-464b4640",
            "https://scholar.google.com/citation",
            "s?user=4YPwzIMAAAAJ&hl=en",
            "https://www.scopus.com/authid/de",
            "tail.uri?authorId=7102954651",
            "Cited by",
            "All Since 2018",
            "Citations 2113 812",
            "h-index 21 15",
            "i10-index 33 23",
            "R. Dinakaran",
            "Michael",
        }:
            continue

        major = is_major_heading(line)
        if major:
            close_list()
            if section_open:
                out.append("</section>")
            section_id = slugify(major)
            base = section_id
            n = 2
            while section_id in seen_ids:
                section_id = f"{base}-{n}"
                n += 1
            seen_ids.add(section_id)
            nav.append((major, section_id))
            out.append(f'<section id="{section_id}" class="content-section">')
            out.append(f"<h2>{html.escape(major)}</h2>")
            section_open = True
            continue

        if is_minor_heading(line):
            close_list()
            out.append(f"<h3>{html.escape(line.strip('* '))}</h3>")
            continue

        if is_list_item(line):
            if not in_list:
                out.append('<ul class="cv-list">')
                in_list = True
            clean = re.sub(r"^•\s*", "", line)
            out.append(f"<li>{html.escape(clean)}</li>")
        else:
            close_list()
            out.append(f"<p>{html.escape(line)}</p>")

    close_list()
    if section_open:
        out.append("</section>")
    return "\n".join(out), nav


def render_html(content: str, nav: list[tuple[str, str]]) -> str:
    nav_links = "\n".join(
        f'<a href="#{section_id}">{html.escape(title)}</a>' for title, section_id in nav
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>R. Dinakaran Michael | Curriculum Vitae</title>
  <style>
    :root {{
      --ink: #17201f;
      --muted: #5f6b67;
      --line: #dfe7e2;
      --paper: #fbfcf9;
      --panel: #ffffff;
      --accent: #0f766e;
      --accent-2: #9a3412;
      --soft: #eef6f3;
      --shadow: 0 18px 50px rgba(23, 32, 31, 0.10);
    }}

    * {{ box-sizing: border-box; }}

    html {{ scroll-behavior: smooth; }}

    body {{
      margin: 0;
      color: var(--ink);
      background:
        linear-gradient(180deg, #eef6f3 0, rgba(238, 246, 243, 0) 420px),
        var(--paper);
      font-family: "Inter", "Segoe UI", Arial, sans-serif;
      line-height: 1.6;
    }}

    a {{ color: inherit; }}

    .page {{
      width: min(1180px, calc(100% - 36px));
      margin: 0 auto;
    }}

    header {{
      padding: 46px 0 28px;
      border-bottom: 1px solid var(--line);
    }}

    .hero {{
      display: grid;
      grid-template-columns: minmax(0, 1fr) 340px;
      gap: 32px;
      align-items: end;
    }}

    .eyebrow {{
      margin: 0 0 10px;
      color: var(--accent-2);
      font-size: 0.82rem;
      font-weight: 750;
      letter-spacing: 0.08em;
      text-transform: uppercase;
    }}

    h1 {{
      margin: 0;
      max-width: 780px;
      font-size: clamp(2.6rem, 6vw, 5rem);
      line-height: 0.98;
      letter-spacing: 0;
    }}

    .subtitle {{
      max-width: 780px;
      margin: 18px 0 0;
      color: var(--muted);
      font-size: 1.08rem;
    }}

    .contact {{
      display: grid;
      gap: 10px;
      padding: 18px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: var(--shadow);
    }}

    .contact a, .contact span {{
      display: block;
      overflow-wrap: anywhere;
      color: var(--muted);
      text-decoration: none;
      font-size: 0.95rem;
    }}

    .contact strong {{
      display: block;
      color: var(--ink);
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }}

    .metrics {{
      display: grid;
      grid-template-columns: repeat(4, minmax(0, 1fr));
      gap: 12px;
      padding: 22px 0 0;
    }}

    .metric {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 16px;
    }}

    .metric b {{
      display: block;
      font-size: 1.8rem;
      line-height: 1;
      color: var(--accent);
    }}

    .metric span {{
      display: block;
      margin-top: 8px;
      color: var(--muted);
      font-size: 0.86rem;
    }}

    .layout {{
      display: grid;
      grid-template-columns: 260px minmax(0, 1fr);
      gap: 34px;
      padding: 30px 0 70px;
    }}

    nav {{
      position: sticky;
      top: 18px;
      align-self: start;
      max-height: calc(100vh - 36px);
      overflow: auto;
      padding: 16px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
    }}

    nav strong {{
      display: block;
      margin-bottom: 10px;
      font-size: 0.78rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--accent-2);
    }}

    nav a {{
      display: block;
      padding: 8px 0;
      color: var(--muted);
      text-decoration: none;
      border-top: 1px solid #edf1ee;
      font-size: 0.92rem;
    }}

    nav a:hover {{ color: var(--accent); }}

    main {{
      display: grid;
      gap: 18px;
    }}

    .content-section {{
      padding: 26px;
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      box-shadow: 0 10px 30px rgba(23, 32, 31, 0.055);
    }}

    .content-section + .content-section {{ margin-top: 0; }}

    h2 {{
      margin: 0 0 18px;
      padding-bottom: 12px;
      border-bottom: 2px solid var(--soft);
      font-size: 1.45rem;
      line-height: 1.2;
    }}

    h3 {{
      margin: 26px 0 10px;
      color: var(--accent);
      font-size: 1.05rem;
      line-height: 1.25;
    }}

    p {{
      margin: 0 0 12px;
      color: #26302d;
    }}

    .cv-list {{
      margin: 0 0 14px;
      padding-left: 1.25rem;
    }}

    .cv-list li {{
      margin: 0 0 8px;
      padding-left: 0.15rem;
    }}

    footer {{
      padding: 24px 0 42px;
      color: var(--muted);
      border-top: 1px solid var(--line);
      font-size: 0.92rem;
    }}

    @media (max-width: 860px) {{
      .hero, .layout, .metrics {{
        grid-template-columns: 1fr;
      }}

      nav {{
        position: static;
        max-height: none;
      }}
    }}

    @media print {{
      body {{ background: #fff; }}
      .page {{ width: 100%; }}
      nav {{ display: none; }}
      .layout {{ display: block; }}
      .contact, .metric, .content-section {{
        box-shadow: none;
        break-inside: avoid;
      }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="page hero">
      <div>
        <p class="eyebrow">Curriculum Vitae</p>
        <h1>R. Dinakaran Michael</h1>
        <p class="subtitle">Fish immunology researcher, educator, and former Dean of Life Sciences with more than four decades of teaching and research leadership.</p>
      </div>
      <address class="contact">
        <span><strong>Email</strong><a href="mailto:rdmichael2000@gmail.com">rdmichael2000@gmail.com</a></span>
        <span><strong>LinkedIn</strong><a href="https://linkedin.com/in/r-dinakaran-michael-464b4640">linkedin.com/in/r-dinakaran-michael-464b4640</a></span>
        <span><strong>Google Scholar</strong><a href="https://scholar.google.com/citations?user=4YPwzIMAAAAJ&hl=en">Scholar profile</a></span>
        <span><strong>Scopus</strong><a href="https://www.scopus.com/authid/detail.uri?authorId=7102954651">Author ID 7102954651</a></span>
      </address>
    </div>
    <div class="page metrics" aria-label="Research metrics">
      <div class="metric"><b>53</b><span>Indexed journal publications</span></div>
      <div class="metric"><b>12</b><span>PhD students guided</span></div>
      <div class="metric"><b>2,113</b><span>Total citations listed in the CV</span></div>
      <div class="metric"><b>21</b><span>h-index listed in the CV</span></div>
    </div>
  </header>

  <div class="page layout">
    <nav aria-label="CV sections">
      <strong>Sections</strong>
      {nav_links}
    </nav>
    <main>
      {content}
    </main>
  </div>

  <footer>
    <div class="page">Converted from “RDM-CV detailed 18-Jul-2023 final.pdf”.</div>
  </footer>
</body>
</html>
"""


def main() -> None:
    lines = extract_lines(PDF_PATH)
    content, nav = build_content(lines)
    OUT_PATH.write_text(render_html(content, nav), encoding="utf-8")
    print(OUT_PATH.resolve())


if __name__ == "__main__":
    main()
