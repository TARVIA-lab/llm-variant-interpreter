#!/usr/bin/env python3
"""
interpret_variants.py — Use Claude to interpret genetic variants in oncology context.

Architecture:
  - claude-opus-4-8 with adaptive thinking
  - Large oncology system prompt cached with cache_control (saves ~90% on repeated calls)
  - Tool use forces structured JSON output per variant
  - Variants processed in batches of up to 10 per API call

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...

    python interpret_variants.py --variants enriched.json
    python interpret_variants.py --variants enriched.json --batch-size 5 --output interpretations.json
"""
import argparse
import json
import logging
import sys
from pathlib import Path

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S", level=logging.INFO)
log = logging.getLogger(__name__)

# ── Oncology system prompt (large — will be cached) ───────────────────────────
ONCOLOGY_SYSTEM = """You are an expert oncologist and molecular pathologist specializing in the clinical interpretation of somatic and germline genetic variants.

## Your Role
Interpret genetic variants in the context of cancer biology, clinical significance, and therapeutic implications. Your interpretations will inform clinical decision-making for oncology patients.

## Classification Framework

### Clinical Significance (ACMG/AMP Guidelines)
- **Pathogenic (P)**: Strong evidence variant causes disease
- **Likely Pathogenic (LP)**: Probable disease-causing variant (>90% certainty)
- **Variant of Uncertain Significance (VUS)**: Insufficient evidence to classify
- **Likely Benign (LB)**: Probable benign variant
- **Benign (B)**: Well-established benign variant

### Oncological Relevance
- **High**: Driver mutation, established therapeutic target, or diagnostic/prognostic marker
- **Moderate**: Potentially actionable, context-dependent significance
- **Low**: Passenger mutation or minor functional impact
- **None**: No evidence of oncological relevance

## Key Oncogenes and Tumor Suppressors

### Frequently Mutated Oncogenes
- **KRAS** (G12D, G12V, G12C, G13D): RAS pathway activation; NSCLC, CRC, pancreatic
- **EGFR** (L858R, exon 19 del, T790M): RTK activation; NSCLC targetable with TKIs
- **BRAF** (V600E, V600K): MAPK pathway; melanoma, CRC, thyroid, NSCLC
- **PIK3CA** (E545K, H1047R, E542K): PI3K pathway; breast, endometrial, CRC
- **ALK** (fusions): RTK; NSCLC, ALCL — targeted by crizotinib/alectinib
- **RET** (fusions, M918T, C634R): Thyroid cancer, NSCLC
- **MET** (amplification, exon 14 skip, Y1253D): NSCLC, gastric
- **KIT** (D816V, exon 11 del): GIST, AML — imatinib target
- **FLT3** (ITD, D835): AML — midostaurin/gilteritinib
- **IDH1/2** (R132H, R140Q): Glioma, AML, CCA — ivosidenib/enasidenib
- **FGFR1/2/3** (fusions, amplifications): Bladder, CCA, NSCLC

### Tumor Suppressors
- **TP53** (R175H, R248W, R248Q, R273H, R273C, G245S, R249S): Pan-cancer guardian
- **BRCA1/2** (pathogenic variants): Hereditary breast/ovarian, PARP inhibitor sensitivity
- **PTEN** (loss, R130Q): PI3K pathway; breast, endometrial, GBM
- **RB1** (loss): Retinoblastoma, SCLC, bladder
- **APC** (truncations): Familial adenomatous polyposis, sporadic CRC
- **VHL** (R167Q, truncations): Clear cell RCC — HIF pathway
- **CDH1** (truncations): Hereditary diffuse gastric cancer
- **STK11/LKB1** (loss): PJS, NSCLC — immune exclusion
- **SMAD4** (truncations): Pancreatic, CRC
- **ARID1A** (truncations): Microsatellite instable tumors

## Therapeutic Implications Framework

### FDA-Approved Targeted Therapies (Oncogenic Variants)
| Variant | Drug Class | Examples |
|---------|-----------|---------|
| EGFR L858R / exon19del | EGFR TKI | Osimertinib, erlotinib, gefitinib |
| EGFR T790M | 3rd-gen EGFR TKI | Osimertinib |
| BRAF V600E (melanoma) | BRAF+MEK inhibitor | Vemurafenib+cobimetinib, dabrafenib+trametinib |
| BRAF V600E (CRC) | BRAF+EGFR+MEK | Encorafenib+cetuximab |
| KRAS G12C | KRAS G12C inhibitor | Sotorasib, adagrasib |
| ALK fusion | ALK inhibitor | Alectinib, brigatinib, lorlatinib |
| RET fusion | RET inhibitor | Selpercatinib, pralsetinib |
| MET exon14 skip | MET inhibitor | Capmatinib, tepotinib |
| FGFR2 fusion (CCA) | FGFR inhibitor | Pemigatinib, infigratinib |
| IDH1 R132 | IDH1 inhibitor | Ivosidenib |
| IDH2 R140/R172 | IDH2 inhibitor | Enasidenib |
| PIK3CA (HR+/HER2- BC) | PI3K inhibitor | Alpelisib |
| BRCA1/2 (ovarian/BC) | PARP inhibitor | Olaparib, niraparib, rucaparib |
| FLT3 ITD | FLT3 inhibitor | Midostaurin, gilteritinib |
| KIT D816V (SM) | KIT inhibitor | Avapritinib |
| NTRK fusion | TRK inhibitor | Larotrectinib, entrectinib |

### Germline Implications
Variants in BRCA1/2, MLH1, MSH2, MSH6, PMS2, PALB2, ATM, CHEK2, TP53, RET, VHL, APC, STK11, CDH1, PTEN, MUTYH have hereditary cancer implications. Always flag for genetic counseling referral.

## Interpretation Standards

### Evidence Tiers
- **Tier 1**: FDA-approved therapy in this tumor type for this variant
- **Tier 2**: FDA-approved therapy in different tumor type OR strong clinical evidence
- **Tier 3**: Clinical trials available, preclinical evidence
- **Tier 4**: Biological plausibility, no current evidence

### Confidence Levels
- **High**: Well-characterized variant with strong literature support
- **Moderate**: Known gene, variant type recognized but limited functional data
- **Low**: Gene relevant but variant poorly characterized

Provide clinically actionable, evidence-based interpretations. Be specific about tumor type context. Flag any germline implications. Cite therapeutic opportunities at the highest evidence tier available."""

# ── Tool definition for structured output ─────────────────────────────────────
INTERPRET_TOOL = {
    "name": "record_variant_interpretation",
    "description": (
        "Record a structured clinical interpretation for a genetic variant. "
        "Call this once per variant provided in the user message."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "variant_id": {
                "type": "string",
                "description": "The variant identifier (CHROM:POS:REF>ALT or rs ID)"
            },
            "gene": {"type": "string", "description": "Gene symbol (e.g. KRAS, TP53)"},
            "hgvs_p": {"type": "string", "description": "Protein change (e.g. p.Gly12Asp)"},
            "clinical_significance": {
                "type": "string",
                "enum": ["Pathogenic", "Likely Pathogenic", "VUS",
                         "Likely Benign", "Benign", "Unknown"],
            },
            "oncological_relevance": {
                "type": "string",
                "enum": ["High", "Moderate", "Low", "None"],
            },
            "evidence_tier": {
                "type": "string",
                "enum": ["Tier 1 (FDA-approved)", "Tier 2 (Off-label/strong evidence)",
                         "Tier 3 (Clinical trial)", "Tier 4 (Preclinical)", "None"],
            },
            "cancer_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Most relevant cancer types for this variant"
            },
            "mechanism": {
                "type": "string",
                "description": "Molecular mechanism (e.g. 'Activating kinase mutation', 'Loss of tumor suppression')"
            },
            "targeted_therapies": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Approved or investigational therapies targeting this variant"
            },
            "clinical_trials_keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Search terms for relevant clinical trials"
            },
            "germline_implications": {
                "type": "boolean",
                "description": "Whether this variant has hereditary cancer implications requiring counseling"
            },
            "interpretation_summary": {
                "type": "string",
                "description": "2-4 sentence clinical interpretation for the treating oncologist"
            },
            "confidence": {
                "type": "string",
                "enum": ["High", "Moderate", "Low"],
            },
            "caveats": {
                "type": "string",
                "description": "Important caveats, limitations, or additional workup needed"
            },
        },
        "required": [
            "variant_id", "gene", "clinical_significance", "oncological_relevance",
            "evidence_tier", "cancer_types", "mechanism", "interpretation_summary",
            "confidence", "germline_implications"
        ],
        "additionalProperties": False,
    },
}


def format_variant_for_prompt(v: dict) -> str:
    """Format a single variant as a compact readable block."""
    lines = [
        f"### Variant: {v.get('id', 'unknown')}",
        f"- Gene: {v.get('gene', 'unknown')}",
        f"- Position: {v.get('chrom', '')}:{v.get('pos', '')} {v.get('ref', '')}>{v.get('alt', '')}",
        f"- Consequence: {v.get('consequence', 'unknown')}",
        f"- Impact: {v.get('impact', 'unknown')}",
        f"- HGVS (cDNA): {v.get('hgvs_c', 'N/A')}",
        f"- HGVS (protein): {v.get('hgvs_p', 'N/A')}",
    ]
    if v.get("allele_freq") is not None:
        lines.append(f"- Allele Frequency: {v['allele_freq']:.3f}")
    if v.get("clinvar"):
        cv = v["clinvar"]
        lines.append(f"- ClinVar: {cv.get('significance', 'N/A')} "
                     f"({cv.get('condition', 'N/A')}, "
                     f"★{'★' * int(cv.get('review_stars', 0))})")
    return "\n".join(lines)


def interpret_batch(client, variants: list[dict], dry_run: bool = False) -> list[dict]:
    """Interpret a batch of variants in a single Claude API call."""
    if dry_run:
        log.info(f"[DRY RUN] Would call Claude API for {len(variants)} variant(s)")
        return []

    import anthropic

    variant_blocks = "\n\n".join(format_variant_for_prompt(v) for v in variants)
    user_msg = (
        f"Please interpret each of the following {len(variants)} genetic variant(s). "
        f"Call the `record_variant_interpretation` tool once for each variant.\n\n"
        f"{variant_blocks}"
    )

    log.info(f"  Calling Claude API (batch of {len(variants)})...")
    response = client.messages.create(
        model="claude-opus-4-8",
        max_tokens=4096,
        thinking={"type": "enabled", "budget_tokens": 2000},
        system=[{
            "type": "text",
            "text": ONCOLOGY_SYSTEM,
            "cache_control": {"type": "ephemeral"},  # Cache the large system prompt
        }],
        tools=[INTERPRET_TOOL],
        tool_choice={"type": "any"},   # Force at least one tool call
        messages=[{"role": "user", "content": user_msg}],
    )

    # Log cache stats
    usage = response.usage
    cache_hit   = getattr(usage, "cache_read_input_tokens",   0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    log.info(f"  Tokens — input: {usage.input_tokens}, "
             f"output: {usage.output_tokens}, "
             f"cache_read: {cache_hit}, cache_write: {cache_write}")
    if cache_hit > 0:
        log.info(f"  ✓ System prompt served from cache (saved ~{cache_hit} tokens)")

    # Extract structured interpretations from tool use blocks
    interpretations = []
    for block in response.content:
        if block.type == "tool_use" and block.name == "record_variant_interpretation":
            interpretations.append(block.input)

    log.info(f"  Received {len(interpretations)} interpretation(s)")
    return interpretations


def merge_interpretations(variants: list[dict],
                           interpretations: list[dict]) -> list[dict]:
    """Merge Claude interpretations back into the variant records."""
    # Build lookup by variant_id
    interp_map: dict[str, dict] = {}
    for interp in interpretations:
        vid = interp.get("variant_id", "")
        interp_map[vid] = interp

    merged = []
    for v in variants:
        vid = v.get("id", "")
        interp = interp_map.get(vid, {})

        # Also try gene + hgvs_p as fallback key
        if not interp:
            gene_key = f"{v.get('gene', '')} {v.get('hgvs_p', '')}"
            for k, val in interp_map.items():
                if k.endswith(v.get("hgvs_p", "") or "__NONE__"):
                    interp = val
                    break

        merged.append({**v, "interpretation": interp})
    return merged


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--variants",   type=Path, required=True,
                        help="Enriched variants JSON (from clinvar_enricher.py)")
    parser.add_argument("--output",     type=Path, default=None,
                        help="Output JSON (default: stdout)")
    parser.add_argument("--batch-size", type=int, default=8,
                        help="Variants per API call (default: 8)")
    parser.add_argument("--max-variants", type=int, default=50,
                        help="Max variants to interpret (default: 50)")
    parser.add_argument("--dry-run",    action="store_true",
                        help="Preview without calling Claude API")
    args = parser.parse_args()

    if not args.variants.exists():
        log.error(f"Variants file not found: {args.variants}")
        sys.exit(1)

    variants = json.loads(args.variants.read_text())
    log.info(f"Loaded {len(variants)} variant(s)")

    # Prioritize by impact for the interpretation budget
    impact_order = {"HIGH": 0, "MODERATE": 1, "LOW": 2, "MODIFIER": 3, "": 4}
    variants.sort(key=lambda v: (
        impact_order.get(v.get("impact", ""), 4),
        0 if v.get("clinvar") else 1,
    ))
    variants = variants[:args.max_variants]
    log.info(f"Processing top {len(variants)} variant(s) by impact")

    if not args.dry_run:
        try:
            import anthropic
            client = anthropic.Anthropic()
        except ImportError:
            log.error("anthropic not installed. Run: pip install anthropic")
            sys.exit(1)
        except Exception as e:
            log.error(f"Failed to create Anthropic client: {e}")
            log.error("Set ANTHROPIC_API_KEY environment variable")
            sys.exit(1)
    else:
        client = None

    # Process in batches
    all_interpretations: list[dict] = []
    batches = [variants[i:i+args.batch_size]
               for i in range(0, len(variants), args.batch_size)]
    log.info(f"Processing {len(batches)} batch(es) of ≤{args.batch_size}")

    for i, batch in enumerate(batches, 1):
        log.info(f"Batch {i}/{len(batches)}: {[v.get('gene','?') for v in batch]}")
        interps = interpret_batch(client, batch, dry_run=args.dry_run)
        all_interpretations.extend(interps)

    if args.dry_run:
        log.info(f"[DRY RUN] Would produce {len(variants)} interpretations")
        log.info(f"[DRY RUN] System prompt: {len(ONCOLOGY_SYSTEM)} chars "
                 f"(~{len(ONCOLOGY_SYSTEM)//4} tokens, cached after first call)")
        return

    merged = merge_interpretations(variants, all_interpretations)

    # Summary
    sigs = [m["interpretation"].get("clinical_significance", "Unknown")
            for m in merged if m.get("interpretation")]
    for sig in ["Pathogenic", "Likely Pathogenic", "VUS", "Likely Benign", "Benign"]:
        count = sigs.count(sig)
        if count:
            log.info(f"  {sig}: {count}")

    high_rel = [m for m in merged
                if m.get("interpretation", {}).get("oncological_relevance") == "High"]
    log.info(f"High oncological relevance: {len(high_rel)} variant(s)")
    if high_rel:
        for m in high_rel[:5]:
            i = m["interpretation"]
            therapies = ", ".join(i.get("targeted_therapies", [])[:2]) or "none identified"
            log.info(f"  ● {m.get('gene')} {i.get('hgvs_p','')}: "
                     f"{i.get('clinical_significance')} — {therapies}")

    out = json.dumps(merged, indent=2)
    if args.output:
        args.output.write_text(out)
        log.info(f"Interpretations written to: {args.output}")
    else:
        print(out)


if __name__ == "__main__":
    main()
