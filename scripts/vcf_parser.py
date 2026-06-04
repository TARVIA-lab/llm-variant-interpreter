#!/usr/bin/env python3
"""
vcf_parser.py — Parse a VCF file into a structured JSON list of variants.

Handles both plain and gzip-compressed VCFs.
Extracts SnpEff ANN fields when present for gene/consequence annotation.

Usage:
    python vcf_parser.py --vcf filtered.vcf.gz
    python vcf_parser.py --vcf filtered.vcf.gz --filter-pass --output variants.json
"""
import argparse
import gzip
import json
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S", level=logging.INFO)
log = logging.getLogger(__name__)

# SnpEff ANN field order
ANN_FIELDS = [
    "allele", "annotation", "annotation_impact", "gene_name", "gene_id",
    "feature_type", "feature_id", "transcript_biotype", "rank",
    "hgvs_c", "hgvs_p", "cdna_pos", "cds_pos", "protein_pos",
    "distance", "errors",
]

IMPACT_RANK = {"HIGH": 0, "MODERATE": 1, "LOW": 2, "MODIFIER": 3, "": 4}


def open_vcf(path: Path):
    if str(path).endswith(".gz"):
        return gzip.open(path, "rt")
    return open(path)


def parse_ann(ann_str: str) -> list[dict]:
    """Parse SnpEff ANN field into list of annotation dicts."""
    annotations = []
    for entry in ann_str.split(","):
        parts = entry.split("|")
        ann = dict(zip(ANN_FIELDS, parts + [""] * (len(ANN_FIELDS) - len(parts))))
        annotations.append(ann)
    # Sort by impact severity
    annotations.sort(key=lambda a: IMPACT_RANK.get(a.get("annotation_impact", ""), 4))
    return annotations


def parse_info(info_str: str) -> dict:
    """Parse VCF INFO field into a dict."""
    result = {}
    for field in info_str.split(";"):
        if "=" in field:
            k, v = field.split("=", 1)
            result[k] = v
        else:
            result[field] = True
    return result


def parse_samples(format_str: str, sample_strs: list[str]) -> list[dict]:
    """Parse FORMAT + sample columns."""
    fmt_keys = format_str.split(":")
    samples = []
    for s in sample_strs:
        vals = s.split(":")
        samples.append(dict(zip(fmt_keys, vals)))
    return samples


def vcf_to_variants(vcf_path: Path, filter_pass: bool = False,
                    max_variants: int = 500) -> list[dict]:
    variants = []
    sample_names = []
    n_total = 0

    with open_vcf(vcf_path) as f:
        for line in f:
            line = line.rstrip()
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                cols = line.lstrip("#").split("\t")
                if len(cols) > 9:
                    sample_names = cols[9:]
                continue

            parts = line.split("\t")
            if len(parts) < 8:
                continue
            n_total += 1

            chrom, pos, vid, ref, alt, qual, filt, info_str = parts[:8]
            format_str = parts[8] if len(parts) > 8 else ""
            sample_strs = parts[9:] if len(parts) > 9 else []

            if filter_pass and filt not in ("PASS", "."):
                continue

            info = parse_info(info_str)
            ann_list = parse_ann(info.get("ANN", "")) if "ANN" in info else []
            top_ann = ann_list[0] if ann_list else {}

            samples = parse_samples(format_str, sample_strs) if format_str else []
            sample_info = dict(zip(sample_names, samples)) if sample_names else {}

            # Extract allele frequency from sample GT/AF fields
            af = None
            dp = None
            for s in samples:
                if "AF" in s:
                    try:
                        af = float(s["AF"])
                    except (ValueError, TypeError):
                        pass
                if "DP" in s:
                    try:
                        dp = int(s["DP"])
                    except (ValueError, TypeError):
                        pass

            variant = {
                "id": vid if vid != "." else f"{chrom}:{pos}:{ref}>{alt}",
                "chrom": chrom,
                "pos": int(pos),
                "ref": ref,
                "alt": alt,
                "qual": qual,
                "filter": filt,
                "gene": top_ann.get("gene_name", ""),
                "gene_id": top_ann.get("gene_id", ""),
                "consequence": top_ann.get("annotation", ""),
                "impact": top_ann.get("annotation_impact", ""),
                "hgvs_c": top_ann.get("hgvs_c", ""),
                "hgvs_p": top_ann.get("hgvs_p", ""),
                "transcript": top_ann.get("feature_id", ""),
                "allele_freq": af,
                "depth": dp,
                "all_annotations": ann_list[:5],  # top 5 transcripts
                "raw_info": {k: v for k, v in info.items()
                             if k not in ("ANN",)},
            }
            variants.append(variant)
            if len(variants) >= max_variants:
                log.warning(f"Truncated at {max_variants} variants (total in VCF: {n_total}+)")
                break

    log.info(f"Parsed {len(variants)} variant(s) from {vcf_path.name} (total lines: {n_total})")
    return variants


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--vcf",          type=Path, required=True)
    parser.add_argument("--output",       type=Path, default=None,
                        help="Output JSON file (default: stdout)")
    parser.add_argument("--filter-pass",  action="store_true",
                        help="Only include PASS / . variants")
    parser.add_argument("--max-variants", type=int, default=500)
    args = parser.parse_args()

    if not args.vcf.exists():
        log.error(f"VCF not found: {args.vcf}")
        sys.exit(1)

    variants = vcf_to_variants(args.vcf, args.filter_pass, args.max_variants)

    out = json.dumps(variants, indent=2)
    if args.output:
        args.output.write_text(out)
        log.info(f"Variants written to: {args.output}")
    else:
        print(out)


if __name__ == "__main__":
    main()
