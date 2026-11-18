#!/usr/bin/env python3
"""Compare strict nullsafe short reference Get CompileErrors."""
from pathlib import Path
import property_hook_parameter_list_sources as sources

sources.SOURCE = Path(__file__).with_name('nullsafe_chain_parentless_short_reference_get_hook_review')

if __name__ == '__main__':
    sources.main()
