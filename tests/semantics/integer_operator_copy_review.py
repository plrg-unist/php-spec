#!/usr/bin/env python3
"""Independent two-operand ownership and second-conversion snapshot checks."""
import base64
import hashlib
import json
from pathlib import Path

from integer_operator_copy_review_cases import CASES
import integer_operator_copy_protocol as runner


def conditions(name, program, path, stdout):
    assert name == 'refcall-both-shared-review'
    return [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry = $integer_seek(S_initial, 0, 2000)[.COMPLETION = NORMAL]',
        '$integer_frontier(S_entry, 0)',
        '$integer_operator_plan(S_entry) = (pintegeroperation)',
        '$integer_operation_valid(S_entry, pintegeroperation)',
        'pintegeroperation.LEFT = REFERENCE n_old',
        'pintegeroperation.RIGHT = REFERENCE n_old',
        'pintegeroperation.LEFTPOINTER = INTEGER_CELL n_old',
        'pintegeroperation.RIGHTPOINTER = INTEGER_CELL n_old',
        '$lookup(S_entry.ENV, $ptascii("old")) = (n_old)',
        'S_entry.STORE[n_old] = DEFINED pvalue_initial',
        '$call_reference_operand_valid(S_entry, REFERENCE n_old)',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) = [HCELL n_old, HCELL n_old]',
        '~$integer_operation_valid(S_entry, pintegeroperation[.LEFT = KNOWN pvalue_initial][.LEFTPOINTER = INTEGER_COPY pvalue_initial])',
        '~$integer_operation_valid(S_entry, pintegeroperation[.RIGHT = KNOWN pvalue_initial][.RIGHTPOINTER = INTEGER_COPY pvalue_initial])',
        '$call_descriptors_valid(S_entry)',
        'PhpStep: S_entry ~> S_begin',
        'S_begin.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation INTEGER_LEFT) :: ptask_tail*',
        'S_begin.ALLOCATIONS = S_entry.ALLOCATIONS',
        'S_left = $integer_seek(S_begin, 1, 2000)[.COMPLETION = NORMAL]',
        'S_left.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation INTEGER_LEFT pintegerconversion_left 0) :: ptask_tail*',
        'pintegerconversion_left.INPUT = pvalue_initial',
        'pintegerconversion_left.VALUE = 5',
        'S_right = $integer_seek(S_left, 4, 2000)[.COMPLETION = NORMAL]',
        'S_right.TODO = (INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 5)) :: ptask_tail*',
        '$lookup(S_right.ENV, $ptascii("old")) = (n_old)',
        '$lookup(S_right.ENV, $ptascii("x")) = (n_replacement)',
        'n_replacement =/= n_old',
        'S_right.STORE[n_old] = DEFINED pvalue_right',
        'pvalue_right =/= pvalue_initial',
        '$integer_pointer_value(S_right, pintegeroperation.RIGHTPOINTER) = (pvalue_right)',
        '$task_nodes(INTEGER_OPERATOR_CONVERT pintegeroperation (INTEGER_RIGHT 5)) = [HCELL n_old, HCELL n_old]',
        '$heap_owners($heap_prune($heap_graph(S_right)), HCELL n_old) = 3',
        '$call_descriptors_valid(S_right)',
        'PhpStep: S_right ~> S_snapshot',
        'S_snapshot.TODO = (INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 5) pintegerconversion_right 0) :: ptask_tail*',
        'pintegerconversion_right.INPUT = pvalue_right',
        'pintegerconversion_right.VALUE = 3',
        '|pintegerconversion_right.NOTICES| = 1',
        '$integer_warning_valid(S_snapshot, pintegeroperation, INTEGER_RIGHT 5, pintegerconversion_right, 0)',
        '$task_nodes(INTEGER_OPERATOR_WARNING pintegeroperation (INTEGER_RIGHT 5) pintegerconversion_right 0) = [HCELL n_old, HCELL n_old]',
        '$heap_valid($heap_graph(S_snapshot))',
        'S_done = $drive_steps(S_snapshot, 2500)',
        'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.STORE[n_old] = DEFINED pvalue_final',
        'pvalue_final =/= pintegerconversion_right.INPUT',
        '$integer_conversion(pvalue_final) = (pintegerconversion_final)',
        'pintegerconversion_final.VALUE = 7',
        '$lookup(S_done.ENV, $ptascii("old")) = (n_old)',
        '$heap_owners($heap_prune($heap_graph(S_done)), HCELL n_old) = 1',
        'S_done.FRAMES = eps',
        'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)',
        '$heap_valid($heap_graph(S_done))',
        '$drive_steps(S_snapshot, 0) = S_snapshot[.COMPLETION = BUDGET]',
    ]


def main():
    data = Path(__file__).with_name('integer_operator_copy_review_cases.py')
    before = hashlib.sha256(data.read_bytes()).hexdigest()
    runner.CASES = tuple(CASES)
    runner.sources.CASES.update(CASES)
    runner.conditions = conditions
    runner.__file__ = __file__
    original_recorded = runner.recorded

    def recorded_checked(command, stem, cap):
        result = original_recorded(command, stem, cap)
        assert result['interruption'] is None and not result['group_after']
        if '--sl' in command and result['exit'] == 0 and not result['timeout']:
            assert Path(str(stem) + '.stdout').read_bytes() == b'true\n'
        return result

    runner.recorded = recorded_checked
    passed = runner.main()
    assert before == hashlib.sha256(data.read_bytes()).hexdigest()
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
