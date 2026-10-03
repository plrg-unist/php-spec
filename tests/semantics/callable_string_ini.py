#!/usr/bin/env python3
"""Callable parameter admission composed with raw/effective INI paths."""
import json
from pathlib import Path
import include_mutable_execution

CATALOGUE = Path(__file__).with_name('callable_string_ini_cases.json')
CASES = {row['id']: row['source'].encode() for row in json.loads(CATALOGUE.read_text())}

def main():
    include_mutable_execution.CASES = CASES
    include_mutable_execution.main()

if __name__ == '__main__':
    main()
