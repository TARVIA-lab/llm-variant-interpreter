#!/usr/bin/env python3
"""
generate_report.py — Generate a clinical HTML report from variant interpretations.

Input:  JSON from interpret_variants.py
Output: A self-contained HTML report suitable for clinical review

Usage:
    python generate_report.py --interpretations interpretations.json
    python generate_report.py --interpretations interpretations.json \\
        --sample-id TUMOR_001 --tumor-type "Non-small cell lung adenocarcinoma" \\
        --output report.html
"""
import argparse
import json
import logging
from datetime import datetime
from pathlib import Path

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S", level=logging.INFO)
log = logging.getLogger(__name__)

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Variant Interpretation Report — {sample_id}</title>
<style>
  :root {{
    --cream: #F4F1EA; --ink: #1a1a2e; --accent: #c0392b;
    --green: #27ae60; --yellow: #f39c12; --gray: #6c757d;
    --card-bg: #fff; --border: #e0ddd8;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: Georgia, "Palatino Linotype", serif; background: var(--cream);
          color: var(--ink); line-height: 1.6; font-size: 15px; }}
  .container {{ max-width: 1100px; margin: 0 auto; padding: 2rem; }}
  header {{ border-bottom: 3px solid var(--accent); padding-bottom: 1.5rem; margin-bottom: 2rem; }}
  header h1 {{ font-size: 1.8rem; color: var(--ink); margin-bottom: 0.3rem; }}
  header .meta {{ color: var(--gray); font-size: 0.9rem; }}
  header .meta span {{ margin-right: 2rem; }}
  .summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr));
                   gap: 1rem; margin-bottom: 2rem; }}
  .summary-card {{ background: var(--card-bg); border: 1px solid var(--border);
                   border-radius: 8px; padding: 1.2rem; text-align: center; }}
  .summary-card .num {{ font-size: 2.2rem; font-weight: bold; color: var(--accent); }}
  .summary-card .label {{ font-size: 0.8rem; color: var(--gray); text-transform: uppercase;
                           letter-spacing: 0.05em; margin-top: 0.2rem; }}
  section {{ margin-bottom: 2.5rem; }}
  section h2 {{ font-size: 1.2rem; border-bottom: 1px solid var(--border);
                padding-bottom: 0.5rem; margin-bottom: 1rem; color: var(--ink); }}
  .variant-card {{ background: var(--card-bg); border: 1px solid var(--border);
                   border-left: 4px solid var(--border); border-radius: 6px;
                   padding: 1.2rem; margin-bottom: 1rem; }}
  .variant-card.high   {{ border-left-color: var(--accent); }}
  .variant-card.moderate {{ border-left-color: var(--yellow); }}
  .variant-card.low    {{ border-left-color: var(--green); }}
  .variant-header {{ display: flex; justify-content: space-between; align-items: flex-start;
                     flex-wrap: wrap; gap: 0.5rem; margin-bottom: 0.8rem; }}
  .variant-header h3 {{ font-size: 1.1rem; }}
  .badges {{ display: flex; gap: 0.4rem; flex-wrap: wrap; }}
  .badge {{ display: inline-block; padding: 0.2rem 0.6rem; border-radius: 12px;
             font-size: 0.75rem; font-weight: bold; }}
  .badge-path   {{ background: #fde8e8; color: #c0392b; }}
  .badge-lp     {{ background: #fef3e2; color: #e67e22; }}
  .badge-vus    {{ background: #fef9e7; color: #d4ac0d; }}
  .badge-benign {{ background: #e8f5e9; color: #27ae60; }}
  .badge-unk    {{ background: #f0f0f0;  color: #6c757d; }}
  .badge-high   {{ background: #fde8e8; color: #c0392b; }}
  .badge-moderate {{ background: #fef3e2; color: #e67e22; }}
  .badge-low    {{ background: #e8f5e9; color: #27ae60; }}
  .badge-t1     {{ background: #d5e8d4; color: #27ae60; }}
  .badge-t2     {{ background: #dae8fc; color: #2980b9; }}
  .badge-t3     {{ background: #fff2cc; color: #d4ac0d; }}
  .badge-t4     {{ background: #f0f0f0;  color: #6c757d; }}
  .variant-meta {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
                   gap: 0.5rem; font-size: 0.85rem; margin-bottom: 0.8rem; }}
  .variant-meta dt {{ color: var(--gray); }}
  .variant-meta dd {{ font-weight: 500; }}
  .interpretation {{ background: var(--cream); border-radius: 4px; padding: 0.8rem;
                     font-style: italic; margin-bottom: 0.6rem; font-size: 0.9rem; }}
  .therapies {{ margin-top: 0.6rem; }}
  .therapies h4 {{ font-size: 0.85rem; color: var(--gray); margin-bottom: 0.3rem; }}
  .therapies ul {{ list-style: none; }}
  .therapies ul li {{ display: inline-block; background: #d5e8d4; color: #1a6e34;
                       padding: 0.15rem 0.5rem; border-radius: 10px; font-size: 0.8rem;
                       margin: 0.1rem; }}
  .caveats {{ font-size: 0.82rem; color: var(--gray); margin-top: 0.5rem;
               border-top: 1px dashed var(--border); padding-top: 0.4rem; }}
  .clinvar-badge {{ font-size: 0.78rem; color: var(--gray); }}
  .germline-flag {{ display: inline-block; background: #fff2cc; color: #d68910;
                    padding: 0.2rem 0.5rem; border-radius: 4px; font-size: 0.78rem;
                    margin-left: 0.5rem; }}
  table {{ width: 100%; border-collapse: collapse; font-size: 0.88rem; }}
  th {{ background: var(--ink); color: white; padding: 0.6rem 0.8rem; text-align: left; }}
  td {{ padding: 0.5rem 0.8rem; border-bottom: 1px solid var(--border); }}
  tr:nth-child(even) {{ background: #faf9f6; }}
  footer {{ border-top: 1px solid var(--border); padding-top: 1rem; font-size: 0.8rem;
             color: var(--gray); margin-top: 3rem; }}
  .no-variants {{ color: var(--gray); font-style: italic; padding: 1rem 0; }}
  @media print {{
    body {{ background: white; font-size: 11pt; }}
    .variant-card {{ page-break-inside: avoid; }}
  }}
</style>
</head>
<body>
<div class="container">
<header>
  <h1>Variant Interpretation Report</h1>
  <div class="meta">
    <span><strong>Sample:</strong> {sample_id}</span>
    <span><strong>Tumor type:</strong> {tumor_type}</span>
    <span><strong>Date:</strong> {report_date}</span>
    <span><strong>Pipeline:</strong> TARVIA-lab llm-variant-interpreter</span>
    <span><strong>Model:</strong> claude-opus-4-8</span>
  </div>
</header>

<div class="summary-grid">
  <div class="summary-card">
    <div class="num">{n_total}</div>
    <div class="label">Variants Analyzed</div>
  </div>
  <div class="summary-card">
    <div class="num">{n_pathogenic}</div>
    <div class="label">Pathogenic / LP</div>
  </div>
  <div class="summary-card">
    <div class="num">{n_high}</div>
    <div class="label">High Relevance</div>
  </div>
  <div class="summary-card">
    <div class="num">{n_tier1}</div>
    <div class="label">Tier 1 Actionable</div>
  </div>
  <div class="summary-card">
    <div class="num">{n_germline}</div>
    <div class="label">Germline Flag</div>
  </div>
  <div class="summary-card">
    <div class="num">{n_vus}</div>
    <div class="label">VUS</div>
  </div>
</div>

{actionable_section}

{all_variants_section}

<section>
<h2>All Variants — Summary Table</h2>
{summary_table}
</section>

<section>
<h2>Disclaimer</h2>
<p style="font-size:0.85rem;color:var(--gray);">
This report was generated using AI-assisted variant interpretation (Claude claude-opus-4-8, TARVIA-lab llm-variant-interpreter).
Interpretations are intended to support — not replace — clinical judgment. All variants flagged as Pathogenic, Likely Pathogenic,
or of potential germline significance should be confirmed by a board-certified molecular pathologist or clinical geneticist.
Clinical decisions should be made in the context of the full patient history and multidisciplinary tumor board review.
</p>
</section>

<footer>
  Generated {report_date} · TARVIA-lab · <a href="https://github.com/TARVIA-lab">github.com/TARVIA-lab</a>
</footer>
</div>
</body>
</html>"""


def sig_badge(sig: str) -> str:
    cls_map = {
        "Pathogenic":        "badge-path",
        "Likely Pathogenic": "badge-lp",
        "VUS":               "badge-vus",
        "Likely Benign":     "badge-benign",
        "Benign":            "badge-benign",
    }
    css = cls_map.get(sig, "badge-unk")
    return f'<span class="badge {css}">{sig}</span>'


def rel_badge(rel: str) -> str:
    cls_map = {"High": "badge-high", "Moderate": "badge-moderate",
               "Low": "badge-low", "None": "badge-unk"}
    css = cls_map.get(rel, "badge-unk")
    return f'<span class="badge {css}">Relevance: {rel}</span>'


def tier_badge(tier: str) -> str:
    if "Tier 1" in tier:   css = "badge-t1"
    elif "Tier 2" in tier: css = "badge-t2"
    elif "Tier 3" in tier: css = "badge-t3"
    elif "Tier 4" in tier: css = "badge-t4"
    else:                  return ""
    return f'<span class="badge {css}">{tier.split("(")[0].strip()}</span>'


def render_variant_card(v: dict) -> str:
    i = v.get("interpretation", {})
    rel = i.get("oncological_relevance", "None")
    sig = i.get("clinical_significance", "Unknown")
    tier = i.get("evidence_tier", "")
    therapies = i.get("targeted_therapies", [])
    germline = i.get("germline_implications", False)

    rel_class = rel.lower() if rel in ("High", "Moderate", "Low") else ""
    germline_html = '<span class="germline-flag">⚠ Germline implications</span>' if germline else ""

    therapies_html = ""
    if therapies:
        items = "".join(f"<li>{t}</li>" for t in therapies)
        therapies_html = f"""<div class="therapies">
          <h4>Targeted therapies:</h4><ul>{items}</ul></div>"""

    caveats = i.get("caveats", "")
    caveats_html = f'<div class="caveats">⚠ {caveats}</div>' if caveats else ""

    clinvar = v.get("clinvar", {})
    clinvar_html = ""
    if clinvar.get("significance"):
        stars = "★" * int(clinvar.get("review_stars", 0))
        clinvar_html = (f'<div class="clinvar-badge">ClinVar: '
                        f'{clinvar["significance"]} — {clinvar.get("condition","")}'
                        f' {stars}</div>')

    cancer_types = ", ".join(i.get("cancer_types", [])[:4]) or "N/A"
    mechanism    = i.get("mechanism", "N/A")
    confidence   = i.get("confidence", "")
    summary      = i.get("interpretation_summary", "_No interpretation available_")
    gene         = i.get("gene") or v.get("gene", "unknown")
    hgvs_p       = i.get("hgvs_p") or v.get("hgvs_p", "")
    hgvs_c       = v.get("hgvs_c", "")
    vid          = v.get("id", "")
    af_val       = v.get("allele_freq")
    af_str       = f"{af_val:.2f}" if af_val is not None else "N/A"

    return f"""
<div class="variant-card {rel_class}">
  <div class="variant-header">
    <h3>{gene} {hgvs_p or hgvs_c or vid}{germline_html}</h3>
    <div class="badges">
      {sig_badge(sig)}
      {rel_badge(rel)}
      {tier_badge(tier)}
    </div>
  </div>
  <div class="variant-meta">
    <div><dt>Variant ID</dt><dd>{vid}</dd></div>
    <div><dt>HGVS (cDNA)</dt><dd>{hgvs_c or "N/A"}</dd></div>
    <div><dt>Allele Freq</dt><dd>{af_str}</dd></div>
    <div><dt>Cancer types</dt><dd>{cancer_types}</dd></div>
    <div><dt>Mechanism</dt><dd>{mechanism}</dd></div>
    <div><dt>AI Confidence</dt><dd>{confidence}</dd></div>
  </div>
  {clinvar_html}
  <div class="interpretation">{summary}</div>
  {therapies_html}
  {caveats_html}
</div>"""


def build_report(variants: list[dict], sample_id: str,
                 tumor_type: str, report_date: str) -> str:
    interped = [v for v in variants if v.get("interpretation")]

    # Counts
    n_total      = len(interped)
    n_pathogenic = sum(1 for v in interped if v["interpretation"].get(
        "clinical_significance") in ("Pathogenic", "Likely Pathogenic"))
    n_high       = sum(1 for v in interped if v["interpretation"].get(
        "oncological_relevance") == "High")
    n_tier1      = sum(1 for v in interped if "Tier 1" in v["interpretation"].get(
        "evidence_tier", ""))
    n_germline   = sum(1 for v in interped if v["interpretation"].get(
        "germline_implications", False))
    n_vus        = sum(1 for v in interped if v["interpretation"].get(
        "clinical_significance") == "VUS")

    # Actionable variants section
    actionable = [v for v in interped
                  if v["interpretation"].get("oncological_relevance") in ("High", "Moderate")
                  or "Tier 1" in v["interpretation"].get("evidence_tier", "")
                  or "Tier 2" in v["interpretation"].get("evidence_tier", "")]

    if actionable:
        cards = "\n".join(render_variant_card(v) for v in actionable)
        actionable_section = f"<section><h2>Actionable & High-Relevance Variants ({len(actionable)})</h2>{cards}</section>"
    else:
        actionable_section = '<section><h2>Actionable &amp; High-Relevance Variants</h2><p class="no-variants">No high-relevance variants identified.</p></section>'

    # All variants section
    remaining = [v for v in interped if v not in actionable]
    if remaining:
        cards = "\n".join(render_variant_card(v) for v in remaining)
        all_variants_section = f"<section><h2>Additional Variants ({len(remaining)})</h2>{cards}</section>"
    else:
        all_variants_section = ""

    # Summary table
    rows = []
    for v in interped:
        i = v["interpretation"]
        gene   = i.get("gene") or v.get("gene", "")
        hgvs   = i.get("hgvs_p") or v.get("hgvs_p") or v.get("id", "")
        sig    = i.get("clinical_significance", "Unknown")
        rel    = i.get("oncological_relevance", "None")
        tier   = i.get("evidence_tier", "None").split("(")[0].strip()
        therapy_str = "; ".join(i.get("targeted_therapies", [])[:2]) or "—"
        germline = "⚠ Yes" if i.get("germline_implications") else "No"
        rows.append(f"<tr><td>{gene}</td><td>{hgvs}</td><td>{sig_badge(sig)}</td>"
                    f"<td>{rel}</td><td>{tier}</td><td>{therapy_str}</td><td>{germline}</td></tr>")

    summary_table = f"""<table>
<thead><tr>
  <th>Gene</th><th>Variant</th><th>Significance</th>
  <th>Relevance</th><th>Evidence</th><th>Therapies</th><th>Germline</th>
</tr></thead>
<tbody>{"".join(rows) or '<tr><td colspan="7">No interpreted variants</td></tr>'}</tbody>
</table>"""

    return HTML_TEMPLATE.format(
        sample_id=sample_id,
        tumor_type=tumor_type or "Not specified",
        report_date=report_date,
        n_total=n_total,
        n_pathogenic=n_pathogenic,
        n_high=n_high,
        n_tier1=n_tier1,
        n_germline=n_germline,
        n_vus=n_vus,
        actionable_section=actionable_section,
        all_variants_section=all_variants_section,
        summary_table=summary_table,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--interpretations", type=Path, required=True)
    parser.add_argument("--output",          type=Path, default=None)
    parser.add_argument("--sample-id",       default="SAMPLE_001")
    parser.add_argument("--tumor-type",      default="Not specified")
    args = parser.parse_args()

    variants = json.loads(args.interpretations.read_text())
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    log.info(f"Generating report for {len(variants)} variant(s)...")
    html = build_report(variants, args.sample_id, args.tumor_type, date_str)

    if args.output:
        args.output.write_text(html)
        log.info(f"Report written to: {args.output}")
    else:
        print(html)


if __name__ == "__main__":
    main()
