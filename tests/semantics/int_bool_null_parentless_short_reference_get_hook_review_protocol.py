#!/usr/bin/env python3
"""Check strict int/bool/null Get with literal-string backing names."""
from pathlib import Path
import int_bool_null_parentless_short_reference_get_hook_protocol as protocol

protocol.STRICT = True
protocol.SUFFIX = "318peer"
protocol.SOURCES = Path(__file__).with_name('int_bool_null_parentless_short_reference_get_hook_review')

if __name__ == '__main__':
    protocol.main()
