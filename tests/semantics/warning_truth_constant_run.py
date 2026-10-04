"""Run only the deferred-cache/truth interaction using the bounded family recorder."""
import warning_truth_pipe_run as family
from warning_truth_constant import SOURCES, CASES

base_inputs = family.inputs

def inputs():
    watched = base_inputs()
    for name in ('warning_truth_constant.py', 'warning_truth_constant_prepare.py', 'warning_truth_constant_run.py'):
        path = family.ROOT / 'tests/semantics' / name
        watched[str(path)] = family.describe(path)
    return watched

family.SOURCES, family.CASES, family.inputs = SOURCES, CASES, inputs

if __name__ == '__main__':
    raise SystemExit(0 if family.main() else 1)
