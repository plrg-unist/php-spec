#!/usr/bin/env python3
"""Reached NoDiscard saved-frame, selected-reference and abrupt-owner checks."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

import nodiscard_cases as authored
import nodiscard_review_cases as reviewed
from error_handler_run import ENV, recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CASES = (
    'named-hole-before-warning-caller-trace',
    'inherited-method-receiver-and-selected-reference',
    'warning-throw-before-recv-sent-owner-retirement',
    'fixed-extra-named-receiver-throw-release-order',
)
SOURCES = {**authored.CASES, **reviewed.CASES}
EXPECTED = {**authored.EXPECTED_STDOUT, **reviewed.EXPECTED}
HELPERS = r'''
dec $nodiscard_test_front(pstate, nat) : bool
def $nodiscard_test_front(S, 0) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = NODISCARD_RESUME pframe
def $nodiscard_test_front(S, 1) = true
  -- if S.TODO = (NODISCARD_RESUME pframe) :: ptask_tail*
def $nodiscard_test_front(S, 2) = true
  -- if S.TODO = [NODISCARD_RECEIVE porigin]
def $nodiscard_test_front(S, 3) = true
  -- if S.TODO = (THROW_SEARCH n) :: (NODISCARD_RESUME pframe) :: ptask_tail*
def $nodiscard_test_front(S, n) = false -- otherwise
dec $nodiscard_test_seek(pstate, nat, nat) : pstate
def $nodiscard_test_seek(S, n_stage, n) = S -- if $nodiscard_test_front(S, n_stage)
def $nodiscard_test_seek(S, n_stage, 0) = S -- if ~$nodiscard_test_front(S, n_stage)
def $nodiscard_test_seek(S, n_stage, n) = $nodiscard_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$nodiscard_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $nodiscard_test_seek(S, n_stage, n) = S
  -- if ~$nodiscard_test_front(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
dec $nodiscard_test_output(pevent*) : ptbytes
dec $nodiscard_test_is_output(pevent) : bool
def $nodiscard_test_output(eps) = eps
def $nodiscard_test_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $nodiscard_test_output(pevent_tail*)
def $nodiscard_test_output(pevent :: pevent_tail*) = $nodiscard_test_output(pevent_tail*) -- if ~$nodiscard_test_is_output(pevent)
def $nodiscard_test_is_output(OUTPUT ptbytes) = true
def $nodiscard_test_is_output(pevent) = false -- otherwise
'''


def conditions(name, program, path):
    throws = 'throw' in name
    method = name.startswith('inherited-')
    ordered = name.startswith('fixed-')
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]

    def seek(state, prior, stage):
        checks.extend([
            f'{state}_found = $nodiscard_test_seek({prior}, {stage}, 3000)',
            f'{state}_found.COMPLETION = NORMAL \\/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$nodiscard_test_front({state}, {stage})',
        ])

    seek('S_dispatch', 'S_initial', 0)
    checks += [
        'S_dispatch.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_caller*',
        'perrorcall.RESUME = NODISCARD_RESUME pframe',
        'pframe.CONTEXT = (pcallcontext)', 'pframe.LOCALS = (psymboltable)',
        'pframe.TODO = [NODISCARD_RECEIVE pcallcontext.FUNCTION]',
        'pframe.ORIGIN = (pcallcontext.FUNCTION)',
        'S_dispatch.CURRENT = eps', 'S_dispatch.FRAMES = eps',
        'S_dispatch.GLOBALTABLE = eps', 'S_dispatch.HELD = eps',
        'S_dispatch.RESULT = KNOWN PNULL',
        'perrorcall.LEVEL = 512', 'perrorcall.LINE = pcallcontext.LINE',
        'pcallcontext.CALLSITE = (perrorcall.SITE)',
        'pcallcontext.DEFAULTRECEIVE = eps', 'pcallcontext.WRAPPER = eps',
        '$nodiscard_frame_valid(S_dispatch, pframe)',
        '$error_call_valid(S_dispatch, perrorcall)',
        '$call_descriptors_valid(S_dispatch)', '$heap_valid($heap_graph(S_dispatch))',
        '$task_nodes(perrorcall.RESUME) = $nodiscard_frame_nodes(pframe)',
        '$task_nodes(ERROR_HANDLER_INVOKE perrorcall) = $value_nodes(perrorcall.CALLBACK) ++ $nodiscard_frame_nodes(pframe)',
        '$function_at($all_functions(S_dispatch), pcallcontext.FUNCTION) = (pfunction)',
        '$function_nodiscard(S_dispatch, pfunction) = NODISCARD_ATTRIBUTE ptbytes_message n_line',
        '$nodiscard_usage(S_dispatch, perrorcall.SITE) = NODISCARD_UNUSED',
        '$drive_steps(S_dispatch, 0) = S_dispatch[.COMPLETION = BUDGET]',
        # Derived projections: no additional reached-source credit.
        '~$nodiscard_frame_valid(S_dispatch, pframe[.ORIGIN = eps])',
        '~$nodiscard_frame_valid(S_dispatch, pframe[.LOCALS = (psymboltable[.CVS = eps])])',
        '~$nodiscard_frame_valid(S_dispatch, pframe[.CONTEXT = (pcallcontext[.CALLSITE = eps])])',
        '~$nodiscard_frame_valid(S_dispatch, pframe[.CONTEXT = (pcallcontext[.LINE = $(pcallcontext.LINE + 1)])])',
        '~$nodiscard_frame_valid(S_dispatch, pframe[.CONTEXT = (pcallcontext[.DEFAULTRECEIVE = ({ID 0, PREFIX 0, PUBLICATION 0})])])',
        '~$error_call_valid(S_dispatch, perrorcall[.LEVEL = 2])',
    ]
    if method:
        checks += [
            '$lookup(S_dispatch.ENV, $ptascii("arg")) = (n_old)',
            '$lookup(S_dispatch.ENV, $ptascii("outside")) = (n_old)',
            '$lookup(psymboltable.ENV, $ptascii("slot")) = (n_old)',
            'n_old <- S_dispatch.REFCELLS', 'S_dispatch.STORE[n_old] = DEFINED (PINT 5)',
            'pcallcontext.RECEIVER = (n_receiver)', 'pcallcontext.INSTANCE = eps',
            '$heap_owners($heap_prune($heap_graph(S_dispatch)), HCELL n_old) = 3',
            '$heap_owners($heap_prune($heap_graph(S_dispatch)), HOBJECT n_receiver) = 2',
            '$nodiscard_frame_nodes(pframe) = [HCELL n_old, HOBJECT n_receiver]',
        ]
    elif throws:
        fixed = 'fixed' if ordered else 'value'
        arg = 'a' if ordered else 'arg'
        checks += [
            '$lookup(S_dispatch.ENV, $ptascii("' + arg + '")) = (n_arg_cell)',
            'S_dispatch.STORE[n_arg_cell] = DEFINED (POBJECT n_arg)',
            '$lookup(psymboltable.ENV, $ptascii("' + fixed + '")) = (n_sent_cell)',
            'S_dispatch.STORE[n_sent_cell] = DEFINED (POBJECT n_arg)',
            '$heap_owners($heap_prune($heap_graph(S_dispatch)), HOBJECT n_arg) = 2',
        ]
        if ordered:
            checks += [
                'pcallcontext.RECEIVER = (n_receiver)',
                'pcallcontext.EXTRA = [KNOWN (POBJECT n_extra)]',
                'pcallcontext.NAMED = [($ptascii("named"), KNOWN (POBJECT n_named))]',
                '$nodiscard_frame_nodes(pframe) = [HCELL n_sent_cell, HOBJECT n_extra, HOBJECT n_named, HOBJECT n_receiver]',
                '$heap_owners($heap_prune($heap_graph(S_dispatch)), HOBJECT n_extra) = 2',
                '$heap_owners($heap_prune($heap_graph(S_dispatch)), HOBJECT n_named) = 2',
                '$heap_owners($heap_prune($heap_graph(S_dispatch)), HOBJECT n_receiver) = 2',
            ]
    else:
        checks += [
            # HOLES retains source provenance after the literal default is filled.
            'pcallcontext.HOLES = [0]', 'pcallcontext.ARGC = 2',
            '$lookup(psymboltable.ENV, $ptascii("first")) = (n_first)',
            '$lookup(psymboltable.ENV, $ptascii("second")) = (n_second)',
            'S_dispatch.STORE[n_first] = DEFINED (PINT 5)',
            'S_dispatch.STORE[n_second] = DEFINED (PINT 3)',
        ]

    seek('S_after', 'S_dispatch', 3 if throws else 1)
    if throws:
        checks += [
            'S_after.TODO = (THROW_SEARCH n_failure) :: (NODISCARD_RESUME pframe) :: ptask_caller*',
            'S_after.CURRENT = eps', 'S_after.FRAMES = eps',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
            '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_arg) = 1',
            '$lookup(S_after.ENV, $ptascii("failure")) = (n_failure_cell)',
            'S_after.STORE[n_failure_cell] = DEFINED (POBJECT n_failure)',
            '$nodiscard_frame_valid(S_after, pframe)',
        ]
        if ordered:
            checks += [
                '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_extra) = 1',
                '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_named) = 1',
                '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_receiver) = 1',
            ]
    else:
        checks += [
            'S_after.TODO = (NODISCARD_RESUME pframe) :: ptask_caller*',
            '$nodiscard_frame_valid(S_after, pframe)',
            '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
            'PhpStep: S_after ~> S_receive',
            'S_receive.TODO = [NODISCARD_RECEIVE pcallcontext.FUNCTION]',
            'S_receive.CURRENT = (pcallcontext)',
            '$active_table(S_receive) = psymboltable',
            'S_receive.STORE = S_after.STORE', 'S_receive.EVENTS = S_after.EVENTS',
            'S_receive.ALLOCATIONS = S_after.ALLOCATIONS',
            '$call_task_valid(S_receive, NODISCARD_RECEIVE pcallcontext.FUNCTION)',
            '$call_descriptors_valid(S_receive)', '$heap_valid($heap_graph(S_receive))',
            'PhpStep: S_receive ~> S_enter',
            'S_enter.TODO = $call_receive_body(S_receive, pfunction)',
            'S_enter.EVENTS = S_after.EVENTS',
        ]
        if method:
            checks += [
                '$lookup(S_after.ENV, $ptascii("arg")) = (n_new)', 'n_old =/= n_new',
                'S_after.STORE[n_old] = DEFINED (PINT 9)',
                'S_after.STORE[n_new] = DEFINED (PINT 33)',
                '$heap_owners($heap_prune($heap_graph(S_after)), HCELL n_old) = 2',
                '$heap_owners($heap_prune($heap_graph(S_after)), HOBJECT n_receiver) = 1',
                '$lookup(S_receive.ENV, $ptascii("slot")) = (n_old)',
                '$heap_owners($heap_prune($heap_graph(S_receive)), HCELL n_old) = 2',
                '$heap_owners($heap_prune($heap_graph(S_receive)), HOBJECT n_receiver) = 1',
            ]
    checks += [
        'S_done = $drive_steps(S_after, 3000)', 'S_done.COMPLETION = NORMAL',
        '$nodiscard_test_output(S_done.EVENTS) = [' + ','.join(map(str, EXPECTED[name])) + ']',
        'S_done.FRAMES = eps', 'S_done.CURRENT = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = (args.case,) if args.case else CASES
    out = args.output or Path(tempfile.mkdtemp(prefix='nodiscard-protocol-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    print(out, flush=True)
    digest = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, ROOT / 'spec/semantics/modules.json', runner, Path(__file__),
               Path(authored.__file__), Path(reviewed.__file__), ROOT / 'frontend/worker.php',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
               ROOT / 'tests/semantics/error_handler_run.py', ROOT / 'tests/semantics/recorded_worker.py']
    before = {str(p): digest(p) for p in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
                      'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
    try:
        parsed = {n: frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCES[n]).decode()}) for n in selected}
        assert all(p['accepted'] for p in parsed.values())
    finally:
        frontend.close()
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        programs = {n: adapter.request({'op': 'check', 'ast': p['ast'], 'fixture': True})['fixture'] for n, p in parsed.items()}
    finally:
        adapter.close()
    rows = []
    for name in selected:
        path = out / (name + '.php')
        path.write_bytes(SOURCES[name])
        checks = conditions(name, programs[name], path)
        fixture = out / (name + '.watsup')
        fixture.write_text(HELPERS + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
            '  -- ' + ('' if c.startswith('PhpStep:') else 'if ') + c + '\n' for c in checks))
        before[str(fixture)] = digest(fixture)
        process = recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / (name + '-model'), 240)
        passed = (process['exit'] == 0 and not process['timeout'] and process['interruption'] is None
                  and not process['group_after'] and (out / (name + '-model.stdout')).read_bytes() == b'true\n'
                  and not (out / (name + '-model.stderr')).read_bytes())
        rows.append({'id': name, 'source_sha256': digest(path), 'fixture_sha256': digest(fixture),
                     'conditions': len(checks), 'derived_guard_assertions': 6, 'model': process, 'passed': passed})
        print(name, passed, flush=True)
        if not passed:
            break
    assert before == {p: digest(Path(p)) for p in before}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = len(rows) == len(selected) and all(r['passed'] for r in rows)
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'profile': profile,
        'inputs': before, 'selection': selected, 'affinity': sorted(__import__('os').sched_getaffinity(0)),
        'rows': rows, 'passed': passed, 'scope': 'Reached source fronts using native-frozen payloads; no native reexecution'}, indent=2) + '\n')
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
