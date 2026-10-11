#!/usr/bin/env python3
"""Independent reached-state checks for borrowed targets and nested warnings."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import sys
import tempfile

import incdec_warning_protocol as protocol

ROOT = Path(__file__).resolve().parents[2]
CASES = ('review-null-ref-rebind-throw', 'review-bool-unwrapped-wrap-mutate',
         'review-nested-registry-restoration')


def conditions(name, program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_entry = $update_seek(S_initial, 0, 2000)[.COMPLETION = NORMAL]',
        '$update_frontier(S_entry, 0)', '$call_descriptors_valid(S_entry)',
        '$update_warning_plan(S_entry) = (pupdatewarning)',
        '$update_warning_valid(S_entry, pupdatewarning)',
        'PhpStep: S_entry ~> S_capture',
        'S_capture.TODO = (UPDATE_WARNING_NOTICE pupdatewarning) :: ptask_tail*',
        'S_capture.STORE = S_entry.STORE',
        '$task_nodes(UPDATE_WARNING_NOTICE pupdatewarning) = eps',
        'PhpStep: S_capture ~> S_dispatch',
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = UPDATE_WARNING_RESTORE pupdatewarning',
        '$error_call_valid(S_dispatch, perrorcall)',
        'S_restore = $update_seek(S_dispatch, 3, 2000)[.COMPLETION = NORMAL]',
        'S_restore.TODO = (UPDATE_WARNING_RESTORE pupdatewarning_restore) :: ptask_restore*',
        '$call_descriptors_valid(S_restore)',
        '$update_warning_valid(S_restore, pupdatewarning_restore)',
    ]
    if name == 'review-null-ref-rebind-throw':
        checks += [
            'pupdatewarning.INPUT = PNULL',
            'pupdatewarning.POINTER = UPDATE_CELL n_old',
            '$lookup(S_entry.ENV, $ptascii("a")) = (n_old)',
            '$lookup(S_entry.ENV, $ptascii("keep")) = (n_old)',
            '$heap_owners($heap_prune($heap_graph(S_entry)), HCELL n_old) = 2',
            'pupdatewarning_restore[.PENDING = eps] = pupdatewarning',
            'pupdatewarning_restore.PENDING = (n_throwable)',
            '$lookup(S_restore.ENV, $ptascii("boom")) = (n_boom)',
            'S_restore.STORE[n_boom] = DEFINED (POBJECT n_throwable)',
            '$task_nodes(UPDATE_WARNING_RESTORE pupdatewarning_restore) = [HOBJECT n_throwable]',
            '$lookup(S_restore.ENV, $ptascii("keep")) = (n_old)',
            '$lookup(S_restore.ENV, $ptascii("a")) = (n_peer)',
            '$lookup(S_restore.ENV, $ptascii("peer")) = (n_peer)',
            'n_old =/= n_peer',
            'S_restore.STORE[n_old] = DEFINED (PINT 7)',
            'S_restore.STORE[n_peer] = DEFINED (PINT 41)',
            '$heap_owners($heap_prune($heap_graph(S_restore)), HCELL n_old) = 1',
            'PhpStep: S_restore ~> S_commit',
            'S_commit.TODO = (UPDATE_WARNING_DONE pupdatewarning_restore) :: ptask_restore*',
            'S_commit.STORE[n_old] = DEFINED PNULL',
            'S_commit.STORE[n_peer] = S_restore.STORE[n_peer]',
            '$lookup(S_commit.ENV, $ptascii("a")) = (n_peer)',
            '$task_nodes(UPDATE_WARNING_DONE pupdatewarning_restore) = [HOBJECT n_throwable]',
            'PhpStep: S_commit ~> S_throw',
            'S_throw.TODO = (THROW_SEARCH n_throwable) :: ptask_restore*',
            'S_throw.RESULT = KNOWN PNULL',
        ]
    elif name == 'review-bool-unwrapped-wrap-mutate':
        checks += [
            'pupdatewarning.INPUT = PBOOL true',
            'pupdatewarning.POINTER = UPDATE_CV ($ptascii("a"))',
            'pupdatewarning_restore = pupdatewarning',
            '$lookup(S_restore.ENV, $ptascii("a")) = (n_old)',
            '$lookup(S_restore.ENV, $ptascii("keep")) = (n_old)',
            'n_old <- S_restore.REFCELLS',
            'S_restore.STORE[n_old] = DEFINED (PINT 7)',
            '$task_nodes(UPDATE_WARNING_RESTORE pupdatewarning_restore) = eps',
            'PhpStep: S_restore ~> S_commit',
            'S_commit.TODO = (UPDATE_WARNING_DONE pupdatewarning_restore) :: ptask_restore*',
            '$lookup(S_commit.ENV, $ptascii("a")) = (n_direct)',
            'n_direct =/= n_old', '~(n_direct <- S_commit.REFCELLS)',
            'S_commit.STORE[n_direct] = DEFINED (PBOOL true)',
            '$lookup(S_commit.ENV, $ptascii("keep")) = (n_old)',
            'S_commit.STORE[n_old] = DEFINED (PINT 7)',
            '$heap_owners($heap_prune($heap_graph(S_commit)), HCELL n_old) = 1',
        ]
    else:
        assert name == 'review-nested-registry-restoration'
        checks += [
            'pupdatewarning.INPUT = PBOOL true',
            'pupdatewarning.POINTER = UPDATE_CELL n_old',
            'pupdatewarning_restore.INPUT = PBOOL false',
            'pupdatewarning_restore.SITE =/= pupdatewarning.SITE',
            'pupdatewarning_restore.POINTER = pupdatewarning.POINTER',
            'pupdatewarning_restore.PENDING = eps',
            'S_restore.STORE[n_old] = DEFINED pvalue_nested',
            '$string_bytes(pvalue_nested) = ($ptascii("Z"))',
            '$task_nodes(UPDATE_WARNING_RESTORE pupdatewarning_restore) = eps',
            'PhpStep: S_restore ~> S_inner_commit',
            'S_inner_commit.STORE[n_old] = DEFINED (PBOOL false)',
            'S_outer = $update_seek(S_inner_commit, 3, 2000)[.COMPLETION = NORMAL]',
            'S_outer.TODO = (UPDATE_WARNING_RESTORE pupdatewarning) :: ptask_outer*',
            'S_outer.STORE[n_old] = DEFINED (PBOOL false)',
            '$call_descriptors_valid(S_outer)',
            'PhpStep: S_outer ~> S_commit',
            'S_commit.TODO = (UPDATE_WARNING_DONE pupdatewarning) :: ptask_outer*',
            'S_commit.STORE[n_old] = DEFINED (PBOOL true)',
            '$task_nodes(UPDATE_WARNING_DONE pupdatewarning) = eps',
            '$drive_steps(S_outer, 0) = S_outer[.COMPLETION = BUDGET]',
        ]
    checks += [
        '$drive_steps(S_restore, 0) = S_restore[.COMPLETION = BUDGET]',
        'S_done = $drive_steps(S_commit, 2500)',
        'S_done.COMPLETION = NORMAL',
        '$integer_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
        'S_budget = $drive_steps(S_restore, 1)',
        'S_budget.COMPLETION = BUDGET',
        '$drive_steps(S_budget[.COMPLETION = NORMAL], 2500) = S_done',
    ]
    if name == 'review-bool-unwrapped-wrap-mutate':
        checks += [
            'S_done.STORE[n_old] = DEFINED (PINT 7)',
            'S_done.STORE[n_direct] = DEFINED (PINT 5)',
        ]
    return checks


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--output', type=Path)
    args, _ = parser.parse_known_args()
    out = args.output
    if out is None:
        out = Path(tempfile.mkdtemp(prefix='incdec-warning-state-review-', dir=ROOT / '.tools'))
        sys.argv += ['--output', str(out)]
    wrapper = Path(__file__)
    before = hashlib.sha256(wrapper.read_bytes()).hexdigest()
    protocol.CASES, protocol.conditions = CASES, conditions
    passed = protocol.main()
    assert before == hashlib.sha256(wrapper.read_bytes()).hexdigest()
    report = json.loads((out / 'report.json').read_bytes())
    report['helper_inputs'][str(wrapper)] = before
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
