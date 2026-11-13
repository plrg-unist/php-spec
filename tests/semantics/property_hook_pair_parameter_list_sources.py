#!/usr/bin/env python3
"""An untyped pair reaches SET arity checking before its invalid void body."""
from pathlib import Path
import property_hook_parameter_list_sources as sources

sources.SOURCE = Path(__file__).with_name('property_hook_pair_parameter_list')

if __name__ == '__main__':
    sources.main()
