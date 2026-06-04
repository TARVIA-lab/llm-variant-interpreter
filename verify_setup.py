#!/usr/bin/env python3
"""
Setup verification script for llm-variant-interpreter

Checks if all dependencies are installed and API key is configured.
"""

import sys
import os

# ANSI colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'


def check_python_version():
    """Check Python 3.10+"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"{GREEN}✓{RESET} Python {version.major}.{version.minor}")
        return True
    else:
        print(f"{RED}✗{RESET} Python {version.major}.{version.minor} (need 3.10+)")
        return False


def check_package(name, import_name=None):
    """Check if a package is installed"""
    if import_name is None:
        import_name = name
    try:
        mod = __import__(import_name)
        version = getattr(mod, '__version__', 'installed')
        print(f"{GREEN}✓{RESET} {name:20} {version}")
        return True
    except ImportError:
        print(f"{RED}✗{RESET} {name:20} not installed")
        return False


def check_api_key():
    """Check if ANTHROPIC_API_KEY is set"""
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if api_key:
        # Show masked key
        masked = api_key[:7] + '...' + api_key[-4:]
        print(f"{GREEN}✓{RESET} ANTHROPIC_API_KEY  {masked}")
        return True
    else:
        print(f"{RED}✗{RESET} ANTHROPIC_API_KEY  not set")
        return False


def main():
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}LLM Variant Interpreter: Setup Verification{RESET:^60}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")

    all_ok = True

    # Python version
    print(f"{BOLD}1. Python Version{RESET}")
    print("-" * 60)
    if not check_python_version():
        all_ok = False
    print()

    # Dependencies
    print(f"{BOLD}2. Python Dependencies{RESET}")
    print("-" * 60)
    deps = [
        ('anthropic', 'anthropic'),
        ('requests', 'requests'),
        ('jinja2', 'jinja2'),
        ('pydantic', 'pydantic'),
        ('pyyaml', 'yaml'),
    ]
    for name, imp in deps:
        if not check_package(name, imp):
            all_ok = False
    print()

    # API Key
    print(f"{BOLD}3. API Configuration{RESET}")
    print("-" * 60)
    if not check_api_key():
        print(f"\n{YELLOW}⚠ Warning:{RESET} API key not found. You'll need it to run interpretations.")
        print(f"   Set it with: export ANTHROPIC_API_KEY=sk-ant-...\n")
    else:
        print()

    # Summary
    print(f"{BOLD}4. Summary{RESET}")
    print("-" * 60)
    if all_ok:
        print(f"{GREEN}{BOLD}✓ All dependencies installed!{RESET}")
        print(f"\n{BOLD}Ready to use:{RESET}")
        print(f"  python scripts/run_interpreter.py --vcf variants.vcf --execute")
        print(f"  python scripts/vcf_parser.py --help")
    else:
        print(f"{RED}{BOLD}✗ Some dependencies missing{RESET}")
        print(f"\n{BOLD}Install missing packages:{RESET}")
        print(f"  pip install -r requirements.txt")
        sys.exit(1)

    print()


if __name__ == '__main__':
    main()
