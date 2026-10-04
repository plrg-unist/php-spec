"""Fixed missing-reference and constrained-write source/state comparisons."""
import json

import warning_consumer_run as family
from warning_reference_cases import CASES as SOURCES
from warning_reference_protocol import CASES

BASE_INPUTS = family.inputs


def inputs():
    watched = BASE_INPUTS()
    for name in ('warning_reference_cases.py', 'warning_reference_protocol.py',
                 'warning_reference_prepare.py', 'warning_reference_run.py'):
        path = family.ROOT / 'tests/semantics' / name
        watched[str(path)] = family.describe(path)
    return watched


def configure():
    modules = json.loads((family.ROOT / 'spec/semantics/modules.json').read_text())
    assert len(modules) == len(set(modules))
    assert 'spec/semantics/220-missing-reference-constrained-write.watsup' in modules
    family.SOURCES = SOURCES
    family.CASES = CASES
    family.inputs = inputs
    family.SOURCE_CAP = 1245
    family.FINITE_CAP = 930


def main():
    configure()
    return family.main()


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
