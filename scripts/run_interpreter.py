#!/usr/bin/env python3
"""
run_interpreter.py — Run the full variant interpretation pipeline end-to-end.

Steps:
  1. Parse VCF → variants.json
  2. Enrich with ClinVar data → enriched.json
  3. Interpret with Claude → interpretations.json
  4. Generate HTML report → report.html

Requires: ANTHROPIC_API_KEY environment variable

Usage:
    # Full run from VCF
    python run_interpreter.py \\
        --vcf variant_out/germline_<ts>/germline.filtered.vcf.gz \\
        --sample-id PATIENT_001 \\
        --tumor-type "NSCLC adenocarcinoma" \\
        --execute

    # Start from pre-parsed variants (skip VCF parsing)
    python run_interpreter.py \\
        --variants-json existing_variants.json \\
        --execute

    # Dry run (no API call)
    python run_interpreter.py --vcf filtered.vcf.gz
"""
import argparse
import json
import logging
import shutil
import sys
from datetime import datetime
from pathlib import Path

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S", level=logging.INFO)
log = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)

    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("--vcf",           type=Path, help="Input VCF file (.vcf or .vcf.gz)")
    grp.add_argument("--variants-json", type=Path, help="Pre-parsed variants JSON")

    parser.add_argument("--sample-id",     default="SAMPLE_001")
    parser.add_argument("--tumor-type",    default="Not specified")
    parser.add_argument("--output-dir",    type=Path, default=Path("interpreter_out"))
    parser.add_argument("--max-variants",  type=int, default=30,
                        help="Max variants to interpret (default: 30, higher = more API cost)")
    parser.add_argument("--batch-size",    type=int, default=8)
    parser.add_argument("--filter-pass",   action="store_true",
                        help="Only include PASS variants from VCF")
    parser.add_argument("--no-network",    action="store_true",
                        help="Skip live ClinVar lookup (use offline known-variant DB)")
    parser.add_argument("--execute",       action="store_true",
                        help="Run (default: dry run)")

    args = parser.parse_args()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = args.output_dir.with_name(f"{args.output_dir.name}_{timestamp}")

    if not args.execute:
        log.info("=== DRY RUN (pass --execute to run) ===")
        log.info(f"Would write outputs to: {out_dir}")
        log.info(f"Sample: {args.sample_id}  |  Tumor type: {args.tumor_type}")
        if args.vcf:
            log.info(f"Input VCF: {args.vcf}")
        else:
            log.info(f"Input variants JSON: {args.variants_json}")
        log.info(f"Max variants to interpret: {args.max_variants} (batch size: {args.batch_size})")
        log.info("[DRY RUN] Would produce: variants.json → enriched.json → interpretations.json → report.html")
        log.info("Note: Interpretation uses claude-opus-4-8 with prompt caching")
        log.info("  → System prompt (~3,500 tokens) cached after first call (~90% savings on repeats)")
        log.info("=== DRY RUN complete — pass --execute to run ===")
        return

    out_dir.mkdir(parents=True, exist_ok=True)
    log.info(f"Output directory: {out_dir}")

    # Import scripts as modules
    scripts_dir = Path(__file__).parent
    sys.path.insert(0, str(scripts_dir))
    from vcf_parser       import vcf_to_variants
    from clinvar_enricher import enrich
    from interpret_variants import interpret_batch, merge_interpretations, INTERPRET_TOOL
    from generate_report  import build_report

    # ── Step 1: Parse VCF ──────────────────────────────────────────────────
    if args.vcf:
        if not args.vcf.exists():
            log.error(f"VCF not found: {args.vcf}")
            sys.exit(1)
        log.info(f"Step 1: Parsing VCF: {args.vcf.name}")
        variants = vcf_to_variants(args.vcf, args.filter_pass, max_variants=500)
    else:
        log.info(f"Step 1: Loading variants from: {args.variants_json}")
        variants = json.loads(args.variants_json.read_text())

    variants_path = out_dir / "variants.json"
    variants_path.write_text(json.dumps(variants, indent=2))
    log.info(f"  → {len(variants)} variants saved to: {variants_path.name}")

    # ── Step 2: ClinVar enrichment ─────────────────────────────────────────
    log.info(f"Step 2: ClinVar enrichment {'(offline only)' if args.no_network else '(online)'}")
    enriched = enrich(variants, email="", network=not args.no_network)
    enriched_path = out_dir / "enriched.json"
    enriched_path.write_text(json.dumps(enriched, indent=2))
    n_hits = sum(1 for v in enriched if v.get("clinvar"))
    log.info(f"  → {n_hits}/{len(enriched)} ClinVar hits saved to: {enriched_path.name}")

    # ── Step 3: Claude interpretation ─────────────────────────────────────
    log.info(f"Step 3: Interpreting with claude-opus-4-8 (max {args.max_variants} variants)")
    try:
        import anthropic
        client = anthropic.Anthropic()
    except Exception as e:
        log.error(f"Cannot create Anthropic client: {e}")
        log.error("Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    # Sort and cap
    impact_order = {"HIGH": 0, "MODERATE": 1, "LOW": 2, "MODIFIER": 3, "": 4}
    to_interpret = sorted(
        enriched,
        key=lambda v: (impact_order.get(v.get("impact", ""), 4),
                       0 if v.get("clinvar") else 1)
    )[:args.max_variants]
    log.info(f"  Selected {len(to_interpret)} variants by impact priority")

    all_interps: list[dict] = []
    batches = [to_interpret[i:i+args.batch_size]
               for i in range(0, len(to_interpret), args.batch_size)]
    for idx, batch in enumerate(batches, 1):
        log.info(f"  Batch {idx}/{len(batches)}")
        interps = interpret_batch(client, batch, dry_run=False)
        all_interps.extend(interps)

    merged = merge_interpretations(to_interpret, all_interps)
    interp_path = out_dir / "interpretations.json"
    interp_path.write_text(json.dumps(merged, indent=2))
    log.info(f"  → {len(all_interps)} interpretations saved to: {interp_path.name}")

    # ── Step 4: Generate HTML report ──────────────────────────────────────
    log.info("Step 4: Generating HTML report")
    date_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    html = build_report(merged, args.sample_id, args.tumor_type, date_str)
    report_path = out_dir / "report.html"
    report_path.write_text(html)
    log.info(f"  → Report written to: {report_path}")

    # ── Summary ───────────────────────────────────────────────────────────
    high = [m for m in merged if m.get("interpretation", {}).get("oncological_relevance") == "High"]
    path = [m for m in merged if m.get("interpretation", {}).get(
        "clinical_significance") in ("Pathogenic", "Likely Pathogenic")]
    tier1 = [m for m in merged if "Tier 1" in m.get("interpretation", {}).get("evidence_tier", "")]

    log.info("")
    log.info("═" * 50)
    log.info(f"INTERPRETATION COMPLETE — {args.sample_id}")
    log.info(f"  Variants interpreted: {len(merged)}")
    log.info(f"  Pathogenic / Likely Pathogenic: {len(path)}")
    log.info(f"  High oncological relevance: {len(high)}")
    log.info(f"  Tier 1 (FDA-approved therapy): {len(tier1)}")
    log.info(f"  Report: {report_path}")
    log.info("═" * 50)
    if tier1:
        log.info("Tier 1 actionable variants:")
        for m in tier1:
            i = m["interpretation"]
            log.info(f"  ● {i.get('gene')} {i.get('hgvs_p','')} — "
                     f"{', '.join(i.get('targeted_therapies', [])[:2])}")


if __name__ == "__main__":
    main()
