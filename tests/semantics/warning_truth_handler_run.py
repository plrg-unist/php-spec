"""Run only the method-handler/truth source and its reached frame."""
import warning_truth_pipe_run as family
from warning_truth_handler import SOURCES, CASES

base_inputs = family.inputs

def inputs():
    watched = base_inputs()
    for name in ('warning_truth_handler.py', 'warning_truth_handler_prepare.py', 'warning_truth_handler_run.py'):
        path = family.ROOT / 'tests/semantics' / name
        watched[str(path)] = family.describe(path)
    return watched

family.SOURCES, family.CASES, family.inputs = SOURCES, CASES, inputs

if __name__ == '__main__':
    raise SystemExit(0 if family.main() else 1)
