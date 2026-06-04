<div align="center">

# llm-variant-interpreter

**AI-powered clinical interpretation of genomic variants using Claude**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white)](https://www.python.org/)
[![Claude Opus 4.8](https://img.shields.io/badge/Claude-Opus%204.8-blueviolet?logo=anthropic)](https://www.anthropic.com/)
[![Prompt Caching](https://img.shields.io/badge/Prompt%20Caching-Enabled-green)](https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![TARVIA-lab](https://img.shields.io/badge/TARVIA--lab-GitHub-black?logo=github)](https://github.com/TARVIA-lab)

Routes variant calls (VCF) through ClinVar enrichment and Claude-powered oncology interpretation, producing structured JSON and a self-contained clinical HTML report.

[Quick Start](#quick-start) · [Architecture](#architecture) · [Pipeline](#pipeline) · [API Design](#claude-api-design) · [Output](#output-format)

</div>

---

## Overview

`llm-variant-interpreter` bridges TARVIA-lab's genomics pipeline with its LLM research work. It takes VCF files (output from [`ngs-variant-plugin`](https://github.com/TARVIA-lab/ngs-variant-plugin)) and uses `claude-opus-4-8` to generate oncologist-level clinical interpretations: clinical significance, oncological relevance, targeted therapy tier, germline implications, and mechanism of action — all as structured JSON.

```
germline.filtered.vcf.gz  →  parsed variants
                          →  + ClinVar enrichment
                          →  + Claude interpretation (cached system prompt)
                          →  HTML clinical report
```

**Key differentiator**: The oncology knowledge base (~3,500 tokens) is loaded once as a cached system prompt. Subsequent API calls across the same session cost ~90% less for the prompt portion.

---

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                  Claude Opus 4.8                          │
│                                                           │
│  System prompt: Oncology expert context (CACHED)         │
│  ┌─────────────────────────────────────────────────┐     │
│  │ • ACMG/AMP classification framework             │     │
│  │ • Oncogene / tumor suppressor catalogue         │     │
│  │ • FDA-approved targeted therapy map             │     │
│  │ • Evidence tier framework (Tier 1-4)            │     │
│  │ • Germline syndrome reference                   │     │
│  └──────────────────────┬──────────────────────────┘     │
│                         │ cache_control: ephemeral        │
│  Per-call: variants     │ → ~90% savings on repeats       │
│  Tool: record_variant_interpretation (forces JSON)        │
│  → 1 tool call per variant, structured output             │
└──────────────────────────────────────────────────────────┘
```

### Claude API Design

- **Model**: `claude-opus-4-8` (most capable, adaptive thinking)
- **Prompt caching**: System prompt marked `cache_control: {type: "ephemeral"}`. First call writes the cache (~1.25× cost); subsequent calls read it (~0.1× cost)
- **Tool use**: `record_variant_interpretation` tool forces structured JSON output per variant — no regex parsing of free text
- **Batch processing**: Up to 8 variants per API call to minimize round-trips
- **Adaptive thinking**: `thinking: {type: "adaptive"}` — Claude reasons when beneficial without requiring a fixed budget

---

## Pipeline

```
vcf_parser.py         run_interpreter.py (orchestrates all 4 steps)
    ↓
clinvar_enricher.py   ← NCBI E-utilities + offline known-variant DB
    ↓
interpret_variants.py ← Claude Opus 4.8 (tool use + prompt caching)
    ↓
generate_report.py    → self-contained HTML clinical report
```

| Step | Script | What it does |
|------|--------|-------------|
| 1 | `vcf_parser.py` | VCF → structured JSON with SnpEff annotations |
| 2 | `clinvar_enricher.py` | Add ClinVar significance + offline known-variant lookup |
| 3 | `interpret_variants.py` | Claude API: clinical significance, therapy tiers, germline flags |
| 4 | `generate_report.py` | Self-contained HTML clinical report |

---

## Quick Start

### Prerequisites

```bash
pip install anthropic requests jinja2
export ANTHROPIC_API_KEY=sk-ant-...
```

### Run from VCF (full pipeline)

```bash
python scripts/run_interpreter.py \
  --vcf variant_out/germline_<ts>/germline.filtered.vcf.gz \
  --sample-id PATIENT_001 \
  --tumor-type "Non-small cell lung adenocarcinoma" \
  --execute
```

### Step by step

```bash
# 1. Parse VCF
python scripts/vcf_parser.py --vcf filtered.vcf.gz --output variants.json

# 2. ClinVar enrichment
python scripts/clinvar_enricher.py --variants variants.json --output enriched.json

# 3. Claude interpretation
python scripts/interpret_variants.py --variants enriched.json --output interpretations.json

# 4. Generate report
python scripts/generate_report.py \
  --interpretations interpretations.json \
  --sample-id PATIENT_001 \
  --tumor-type "Melanoma" \
  --output report.html
```

### Dry run (no API call)

```bash
python scripts/run_interpreter.py --vcf filtered.vcf.gz
```

---

## Input / Output

### Accepts

- **VCF files** (`.vcf` or `.vcf.gz`) from any variant caller
- Works best with SnpEff-annotated VCFs (adds ANN field with gene/consequence)
- Compatible with output from [`ngs-variant-plugin`](https://github.com/TARVIA-lab/ngs-variant-plugin)

### Produces

```
interpreter_out_<timestamp>/
├── variants.json          ← parsed VCF (all variants)
├── enriched.json          ← + ClinVar significance
├── interpretations.json   ← + Claude interpretation per variant
└── report.html            ← self-contained clinical HTML report
```

---

## Output Format

### `interpretations.json` — per-variant fields

| Field | Description |
|-------|-------------|
| `clinical_significance` | Pathogenic / Likely Pathogenic / VUS / Benign (ACMG) |
| `oncological_relevance` | High / Moderate / Low / None |
| `evidence_tier` | Tier 1 (FDA-approved) → Tier 4 (preclinical) |
| `cancer_types` | Most relevant tumor types for this variant |
| `mechanism` | Molecular mechanism (e.g., "Activating kinase mutation") |
| `targeted_therapies` | Approved / investigational drugs targeting this variant |
| `germline_implications` | Boolean — flags for genetic counseling referral |
| `interpretation_summary` | 2-4 sentence clinical interpretation |
| `confidence` | High / Moderate / Low (AI confidence in interpretation) |
| `caveats` | Important caveats, resistance considerations, follow-up tests |

### HTML Report

The report includes:
- **Summary statistics**: total variants, pathogenic count, Tier 1 actionable, germline flags
- **Actionable variants**: high-relevance variants with therapy details
- **Germline flags**: variants requiring counseling highlighted
- **Summary table**: all variants in a scannable format
- **Disclaimer**: AI interpretation disclaimer for clinical use

---

## Running the Test Suite

`test_data/` contains 8 synthetic variants representing well-known oncogenic drivers:

```bash
# Parse + ClinVar enrich (no API key needed)
python scripts/vcf_parser.py \
  --vcf test_data/test_variants.vcf \
  --output test_data/variants.json

python scripts/clinvar_enricher.py \
  --variants test_data/variants.json \
  --no-network \
  --output test_data/enriched.json

# Interpret with Claude (requires ANTHROPIC_API_KEY)
python scripts/interpret_variants.py \
  --variants test_data/enriched.json \
  --output test_data/interpretations.json

# Generate report
python scripts/generate_report.py \
  --interpretations test_data/interpretations.json \
  --sample-id TARVIA_DEMO_001 \
  --tumor-type "NSCLC adenocarcinoma" \
  --output test_data/report.html
```

Expected results:
- **7/8 ClinVar hits** (offline known-variant database)
- **8/8 variants interpreted** by Claude
- **6 Tier 1** actionable variants (EGFR L858R, BRAF V600E, PIK3CA E545K, IDH1 R132H, BRCA2, PIK3CA)
- **2 germline flags** (TP53 R175H, BRCA2 frameshift)

### Test variants

| Gene | Variant | Tumor Type | Targeted Therapy |
|------|---------|-----------|-----------------|
| KRAS | G12D | Pancreatic/CRC | Clinical trials (G12D-specific) |
| BRAF | V600E | Melanoma/CRC/NSCLC | Dabrafenib+trametinib, encorafenib |
| EGFR | L858R | NSCLC | Osimertinib (Tier 1) |
| TP53 | R175H | Pan-cancer | Clinical trials, germline counseling |
| PIK3CA | E545K | Breast/CRC | Alpelisib (Tier 1, HR+/HER2- BC) |
| IDH1 | R132H | Glioma/AML | Vorasidenib, ivosidenib (Tier 1) |
| BRCA2 | 6174delT | Breast/Ovarian | Olaparib/niraparib (Tier 1) |
| PTEN | R130Q | Endometrial/GBM | mTOR inhibitors (Tier 3) |

---

## Cost Estimation

With prompt caching enabled:

| Scenario | Tokens | Cost (approx.) |
|----------|--------|----------------|
| First call (cache write, 10 variants) | ~4,500 system + ~800 user + ~1,500 output | ~$0.04 |
| Subsequent calls (cache hit, 10 variants) | ~450 system + ~800 user + ~1,500 output | ~$0.01 |
| 100-variant batch (5 calls, 4 cache hits) | — | ~$0.08 |

The system prompt (~3,500 tokens) is written to cache on first call and served at ~10% cost on all subsequent calls within the 5-minute TTL.

---

## Integration with TARVIA-lab Genomics Pipeline

This tool is designed to consume output from [`ngs-variant-plugin`](https://github.com/TARVIA-lab/ngs-variant-plugin):

```bash
# 1. Call variants with ngs-variant-plugin
python ../ngs-variant-plugin/scripts/run_germline_variants.py \
  --bam-manifest alignment/manifest.json \
  --reference /refs/GRCh38/genome.fa \
  --execute

# 2. (Optional) Annotate with SnpEff for gene/consequence info
# pip install snpeff → snpEff GRCh38 germline.filtered.vcf.gz > annotated.vcf

# 3. Interpret with Claude
python scripts/run_interpreter.py \
  --vcf variant_out/germline_<ts>/germline.filtered.vcf.gz \
  --sample-id PATIENT_001 \
  --tumor-type "Breast cancer" \
  --execute
```

---

## Project Structure

```
llm-variant-interpreter/
├── scripts/
│   ├── vcf_parser.py          # VCF → structured JSON (handles SnpEff ANN fields)
│   ├── clinvar_enricher.py    # ClinVar API + offline known-variant DB
│   ├── interpret_variants.py  # Claude API: tool use + prompt caching
│   ├── generate_report.py     # Self-contained HTML clinical report
│   └── run_interpreter.py     # Pipeline orchestrator
│
├── skills/
│   ├── variant-interpreter/SKILL.md
│   └── report-generator/SKILL.md
│
├── references/
│   └── oncogene_list.json     # Curated oncogene/TSG catalogue
│
└── test_data/
    ├── test_variants.vcf      # 8 synthetic oncogenic variants
    ├── variants.json          # Parsed output
    ├── enriched.json          # + ClinVar data
    ├── interpretations.json   # + Claude interpretations (pre-baked demo)
    └── report.html            # Example HTML report output
```

---

## Related Work

| Repo | Description |
|------|-------------|
| [ngs-variant-plugin](https://github.com/TARVIA-lab/ngs-variant-plugin) | DNA variant calling pipeline (BWA-MEM2 → GATK4) |
| [ngs-rnaseq-plugin](https://github.com/TARVIA-lab/ngs-rnaseq-plugin) | Bulk RNA-seq analysis |
| [ngs-scrna-plugin](https://github.com/TARVIA-lab/ngs-scrna-plugin) | Single-cell RNA-seq analysis |
| [Benchmarking-LLM-Scientific-Reasoning-in-Oncology](https://github.com/TARVIA-lab/Benchmarking-Large-Language-Model-Scientific-Reasoning-in-Oncology) | LLM benchmarks in oncology |
| **llm-variant-interpreter** | This repo — LLM variant interpretation |

---

## Disclaimer

This tool uses AI-generated interpretations intended to support — not replace — clinical judgment. All variants flagged as Pathogenic or of potential germline significance must be confirmed by a board-certified molecular pathologist or clinical geneticist. Clinical decisions should be made in the context of the full patient history and multidisciplinary tumor board review.

---

## License

[Apache License 2.0](LICENSE)

---

## Acknowledgments

Built with [Claude Opus 4.8](https://www.anthropic.com/) via the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python). Variant annotations informed by ClinVar, OncoKB, and COSMIC. Therapy associations based on FDA-approved oncology indications and NCCN guidelines.
