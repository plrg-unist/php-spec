#!/usr/bin/env python3
"""Regenerate the pure startup-name lookup from the reviewed names-only catalog."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
catalog = json.loads((ROOT / 'tests/semantics/initial-constant-names.json').read_text())
names = sorted({name for group in catalog['groups'].values() for name in group})
source = (';; Generated names-only startup environment; see initial-constant-names.json.\n'
          'dec $initial_constant_bytes(nat*) : bool\n'
          'def $initial_constant_bytes(n*) = (n* <- ' + json.dumps([list(name.encode()) for name in names]) + ')\n'
          'dec $initial_constant(text) : bool\n'
          'def $initial_constant(text) = $initial_constant_bytes($base64(text))\n')
(ROOT / 'spec/semantics/15-constant-names.watsup').write_text(source)
