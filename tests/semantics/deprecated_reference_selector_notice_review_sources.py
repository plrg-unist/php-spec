#!/usr/bin/env python3
"""Run defined reference selectors with handler retirement and array COW."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name('deprecated_reference_selector_notice_review')

if __name__ == '__main__':
    sources.main()
