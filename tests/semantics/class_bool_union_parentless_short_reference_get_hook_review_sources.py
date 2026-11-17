#!/usr/bin/env python3
"""Compare strict explicit class/bool Get unions with literal backing names."""
from pathlib import Path
import deprecated_global_constant_sources as sources

sources.SOURCE = Path(__file__).with_name("class_bool_union_parentless_short_reference_get_hook_review")

if __name__ == "__main__":
    sources.main()
