#!/usr/bin/env python3
"""Reject nullsafe chains in parentless implicit reference returns."""
from pathlib import Path
import property_hook_parameter_list_sources as sources

sources.SOURCE = Path(__file__).with_name('nullsafe_chain_parentless_short_reference_get_hook')

if __name__ == '__main__':
    sources.main()
