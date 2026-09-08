#!/usr/bin/env python3
"""Regenerate the pure startup-name lookup from the reviewed names-only catalog."""
import base64
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'tests/semantics/initial-constant-names.json').read_text())
names = sorted({name for group in catalog['groups'].values() for name in group})
encoded = [base64.b64encode(name.encode()).decode() for name in names]
source = (';; Generated names-only startup environment; see initial-constant-names.json.\n'
          'dec $initial_constant(text) : bool\ndef $initial_constant(text) = true\n'
          '  -- if text <- ' + json.dumps(encoded) + '\n'
          'def $initial_constant(text) = false\n  -- otherwise\n')
(ROOT / 'spec/semantics/15-constant-names.watsup').write_text(source)
