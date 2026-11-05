#!/usr/bin/env python3
"""Independent switch tick originals through the shared exact source harness."""
from pathlib import Path

import tick_switch_review_cases as cases
import tick_switch_sources as sources


if __name__ == '__main__':
    previous = sources.ticks.fingerprint
    sources.ticks.fingerprint = lambda: {
        **previous(), 'tests/semantics/tick_switch_review_cases.py': sources.ticks.sha(Path(cases.__file__))}
    normal = {name: (raw, cases.EXPECTED[name]) for name, raw in cases.CASES.items()}
    normal['review-effectful-constant-result'] = (
        cases.CONTROLS['review-effectful-constant-result'], cases.EXPECTED['review-effectful-constant-result'])
    controls = {'review-empty-multiline-case-line': (cases.CONTROLS['review-empty-multiline-case-line'], b'')}
    sources.main(normal, controls, Path(__file__))
