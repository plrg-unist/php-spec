"""Prepare only the source-derived deferred-cache/truth checkpoint."""
import warning_truth_pipe_prepare as family
import warning_truth_constant_run as runtime
from warning_truth_constant import SOURCES, CASES, PREFIX

family.SOURCES, family.CASES, family.PREFIX = SOURCES, CASES, PREFIX
family.inputs = runtime.inputs

if __name__ == '__main__':
    raise SystemExit(0 if family.main() else 1)
