# Installation Guide

## Prerequisites

- **Python 3.10+**
- **ANTHROPIC_API_KEY** environment variable set (for Claude interpretation step)
- **Internet connection** (for ClinVar enrichment, optional for local testing)

## Quick Setup (2 minutes)

```bash
# 1. Clone repository
git clone https://github.com/TARVIA-lab/llm-variant-interpreter.git
cd llm-variant-interpreter

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set API key
export ANTHROPIC_API_KEY=sk-ant-...  # Your Anthropic API key

# 5. Verify installation
python3 scripts/vcf_parser.py --help
```

## Installation Methods

### Method 1: pip from requirements.txt (Recommended)

```bash
pip install -r requirements.txt
```

### Method 2: pip install editable (for development)

```bash
pip install -e .
```

### Method 3: pip install with dependencies

```bash
pip install anthropic requests jinja2 pydantic pyyaml
```

## API Key Setup

### 1. Get your API key

Visit: https://console.anthropic.com/account/keys

### 2. Set environment variable

**macOS/Linux:**
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Add to ~/.bashrc or ~/.zshrc for persistence:
echo 'export ANTHROPIC_API_KEY=sk-ant-...' >> ~/.bashrc
```

**Windows (PowerShell):**
```powershell
$env:ANTHROPIC_API_KEY="sk-ant-..."
# For persistence, use:
[Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```

### 3. Verify

```bash
echo $ANTHROPIC_API_KEY  # Should show your key (or sk-ant-... prefix)
```

## Verify Installation

```bash
python verify_setup.py
```

Expected output:
```
✓ Python 3.10+
✓ anthropic (0.24.0+)
✓ requests
✓ jinja2
✓ pydantic
✓ pyyaml
✓ API key set
✓ All dependencies ready
```

## Test Installation

Run the offline test (no API calls):

```bash
# Parse VCF (offline)
python scripts/vcf_parser.py \
  --vcf test_data/test_variants.vcf \
  --output test_data/variants.json

# ClinVar enrichment (offline, with --no-network)
python scripts/clinvar_enricher.py \
  --variants test_data/variants.json \
  --no-network \
  --output test_data/enriched.json

# Verify files created
ls -la test_data/*.json
```

## Full Pipeline Test (with Claude API)

```bash
# Run complete interpretation pipeline
python scripts/run_interpreter.py \
  --vcf test_data/test_variants.vcf \
  --sample-id TEST_001 \
  --tumor-type "Melanoma" \
  --execute
```

**Cost:** ~$0.04 for 8 variants (with prompt caching)

## Virtual Environment Management

### Create new environment

```bash
python3 -m venv venv
```

### Activate environment

```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### Deactivate environment

```bash
deactivate
```

### Delete environment (if needed)

```bash
rm -rf venv
```

## Troubleshooting

### Error: "No module named anthropic"

**Solution:** Install missing package
```bash
pip install anthropic
# Or install all:
pip install -r requirements.txt
```

### Error: "ANTHROPIC_API_KEY not found"

**Solution:** Set the API key
```bash
export ANTHROPIC_API_KEY=sk-ant-...
# Verify:
echo $ANTHROPIC_API_KEY
```

### Error: "Python 3.9 or older"

**Solution:** Upgrade Python to 3.10+
```bash
python3 --version  # Check current version
# Install 3.10+ from python.org or use conda
```

### Error: "Connection error to ClinVar"

**Solution:** Use `--no-network` flag for testing
```bash
python scripts/clinvar_enricher.py \
  --variants variants.json \
  --no-network \
  --output enriched.json
```

### Error: VCF parsing fails

**Solution:** Ensure VCF is valid and gzipped correctly
```bash
# Check VCF format
gunzip -t input.vcf.gz  # Tests compression
head -20 input.vcf  # View first lines
```

## Next Steps

1. **Review README:** [README.md](README.md) for architecture and concepts
2. **Run test pipeline:** `python scripts/run_interpreter.py --vcf test_data/test_variants.vcf`
3. **Integration:** Feed output from [ngs-variant-plugin](https://github.com/TARVIA-lab/ngs-variant-plugin)

## Getting Help

- **Check setup:** `python verify_setup.py`
- **See usage:** `python scripts/run_interpreter.py --help`
- **View README:** [README.md](README.md)
- **Report issues:** GitHub Issues on the repository

---

**Last Updated:** 2026-06-04
