#!/usr/bin/env python3
"""
clinvar_enricher.py — Query NCBI ClinVar for known clinical significance of variants.

Uses the NCBI E-utilities API (free, no key required for low-volume use).
Adds ClinVar data to variant JSON produced by vcf_parser.py.

Usage:
    python clinvar_enricher.py --variants variants.json --output enriched.json
    python clinvar_enricher.py --variants variants.json --email you@lab.com
"""
import argparse
import json
import logging
import time
from pathlib import Path
from urllib import request, parse

logging.basicConfig(format="%(asctime)s [%(levelname)s] %(message)s",
                    datefmt="%H:%M:%S", level=logging.INFO)
log = logging.getLogger(__name__)

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

# Well-known oncogenic variants for offline lookup (avoids network in tests)
KNOWN_VARIANTS: dict[str, dict] = {
    "KRAS:p.Gly12Asp":    {"significance": "Pathogenic",        "condition": "Multiple cancers",        "review_stars": 2},
    "KRAS:p.G12D":         {"significance": "Pathogenic",        "condition": "Pancreatic/colorectal",   "review_stars": 2},
    "BRAF:p.Val600Glu":   {"significance": "Pathogenic",        "condition": "Melanoma/colorectal",     "review_stars": 2},
    "BRAF:p.V600E":        {"significance": "Pathogenic",        "condition": "Melanoma",                "review_stars": 2},
    "EGFR:p.Leu858Arg":   {"significance": "Pathogenic",        "condition": "Lung adenocarcinoma",     "review_stars": 3},
    "EGFR:p.L858R":        {"significance": "Pathogenic",        "condition": "Non-small cell lung",     "review_stars": 3},
    "TP53:p.Arg175His":   {"significance": "Pathogenic",        "condition": "Li-Fraumeni syndrome",    "review_stars": 3},
    "TP53:p.R175H":        {"significance": "Pathogenic",        "condition": "Multiple cancers",        "review_stars": 3},
    "PIK3CA:p.Glu545Lys": {"significance": "Pathogenic",        "condition": "Multiple cancers",        "review_stars": 2},
    "PIK3CA:p.E545K":      {"significance": "Pathogenic",        "condition": "Breast/colorectal",       "review_stars": 2},
    "BRCA1:p.5382insC":   {"significance": "Pathogenic",        "condition": "Hereditary breast/ovarian", "review_stars": 3},
    "BRCA2:p.6174delT":   {"significance": "Pathogenic",        "condition": "Hereditary breast",       "review_stars": 3},
    "IDH1:p.Arg132His":   {"significance": "Pathogenic",        "condition": "Glioma/AML",              "review_stars": 2},
    "IDH1:p.R132H":        {"significance": "Pathogenic",        "condition": "Glioma",                  "review_stars": 2},
    "ALK:p.Fusion":        {"significance": "Pathogenic",        "condition": "Lung adenocarcinoma",     "review_stars": 2},
    "RET:p.Cys634Arg":    {"significance": "Pathogenic",        "condition": "MEN2A/thyroid",           "review_stars": 3},
    "KIT:p.Asp816Val":    {"significance": "Pathogenic",        "condition": "Mastocytosis/GIST",       "review_stars": 2},
    "PTEN:p.Arg130Gln":   {"significance": "Likely pathogenic", "condition": "PTEN hamartoma",          "review_stars": 2},
    "MET:p.Tyr1253Asp":   {"significance": "Pathogenic",        "condition": "HPRC",                    "review_stars": 2},
    "VHL:p.Arg167Gln":    {"significance": "Likely pathogenic", "condition": "Von Hippel-Lindau",       "review_stars": 2},
}


def clinvar_search(gene: str, hgvs_p: str, email: str) -> dict | None:
    """Query ClinVar by gene + HGVS protein change. Returns first hit or None."""
    if not gene or not hgvs_p:
        return None

    # Check offline known variants first
    keys_to_try = [
        f"{gene}:{hgvs_p}",
        f"{gene}:{hgvs_p.replace('p.', '')}",
    ]
    for k in keys_to_try:
        if k in KNOWN_VARIANTS:
            log.debug(f"  Offline hit: {k}")
            return KNOWN_VARIANTS[k]

    # Try NCBI E-utilities
    try:
        query = f"{gene}[gene] AND {hgvs_p}[Variant Name]"
        params = parse.urlencode({
            "db": "clinvar",
            "term": query,
            "retmax": 1,
            "retmode": "json",
            "email": email or "noreply@tarvia-lab.com",
        })
        url = f"{BASE_URL}/esearch.fcgi?{params}"
        with request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
        ids = data.get("esearchresult", {}).get("idlist", [])
        if not ids:
            return None

        # Fetch summary for the first ID
        time.sleep(0.4)  # NCBI rate limit: ≤ 3 req/s without API key
        sum_params = parse.urlencode({
            "db": "clinvar",
            "id": ids[0],
            "retmode": "json",
            "email": email or "noreply@tarvia-lab.com",
        })
        sum_url = f"{BASE_URL}/esummary.fcgi?{sum_params}"
        with request.urlopen(sum_url, timeout=10) as resp:
            summary = json.loads(resp.read())

        result = summary.get("result", {}).get(ids[0], {})
        sig = result.get("clinical_significance", {})
        return {
            "significance":  sig.get("description", "Unknown"),
            "condition":     "; ".join(
                t.get("name", "") for t in result.get("trait_set", [])[:3]
            ) or "Unknown",
            "review_stars":  sig.get("review_status_value", 0),
            "variation_id":  result.get("obj_type", ""),
            "clinvar_id":    ids[0],
        }
    except Exception as e:
        log.debug(f"  ClinVar lookup failed for {gene} {hgvs_p}: {e}")
        return None


def enrich(variants: list[dict], email: str = "", network: bool = True) -> list[dict]:
    enriched = []
    for i, v in enumerate(variants, 1):
        gene    = v.get("gene", "")
        hgvs_p  = v.get("hgvs_p", "")
        hgvs_c  = v.get("hgvs_c", "")

        if gene or hgvs_p:
            log.info(f"  [{i}/{len(variants)}] {gene} {hgvs_p or hgvs_c}")

        if network:
            clinvar = clinvar_search(gene, hgvs_p, email)
        else:
            clinvar = None

        # Fall back to offline known variants even without network call
        if clinvar is None and gene and hgvs_p:
            for k in [f"{gene}:{hgvs_p}", f"{gene}:{hgvs_p.replace('p.', '')}"]:
                if k in KNOWN_VARIANTS:
                    clinvar = KNOWN_VARIANTS[k]
                    break

        v["clinvar"] = clinvar or {}
        enriched.append(v)

    n_hits = sum(1 for v in enriched if v["clinvar"])
    log.info(f"ClinVar hits: {n_hits}/{len(enriched)}")
    return enriched


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--variants",    type=Path, required=True,
                        help="JSON from vcf_parser.py")
    parser.add_argument("--output",      type=Path, default=None)
    parser.add_argument("--email",       default="",
                        help="Email for NCBI E-utilities (recommended)")
    parser.add_argument("--no-network",  action="store_true",
                        help="Use only offline known-variant lookup")
    args = parser.parse_args()

    variants = json.loads(args.variants.read_text())
    log.info(f"Enriching {len(variants)} variant(s)...")
    enriched = enrich(variants, args.email, not args.no_network)

    out = json.dumps(enriched, indent=2)
    if args.output:
        args.output.write_text(out)
        log.info(f"Written to: {args.output}")
    else:
        print(out)


if __name__ == "__main__":
    main()
