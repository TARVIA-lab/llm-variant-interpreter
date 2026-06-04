---
name: variant-interpreter
description: Use when the user wants to interpret genetic variants with AI, run clinical interpretation on a VCF, get Claude to explain variant significance in oncology context, check therapeutic implications of mutations, or run the llm-variant-interpreter pipeline.
version: 1.0.0
---
# Variant Interpreter
Runs the four-step pipeline: vcf_parser → clinvar_enricher → interpret_variants (Claude) → generate_report.
Requires ANTHROPIC_API_KEY. Use `--dry-run` to preview without API calls.
```bash
python scripts/run_interpreter.py --vcf filtered.vcf.gz --sample-id PATIENT_001 --execute
```
