#!/usr/bin/env python3
"""Check source-authenticated declare goto reconstruction in plain functions."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile

from exception_handler_review import recorded
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('plain_goto_declare_review_cases.json')
EXPECTED = {
    'ctrl1-declare-forward': '63db6785fddd9a088c0d38f2634da8c2d2a28092bbcb1ea72efc7a58cc7bbc40',
    'ctrl1-declare-backward-loop': '21822ab62949d947373e239676c91d28b5cf8c8bea947842a7db16a0ee38567e',
}
PREFIX = r'''
dec $test_ctrl1_front(pstate) : bool
def $test_ctrl1_front(S) = true
  -- if S.TODO = (STMT (NStmtGoto phpType11 metadata)) :: ptask*
def $test_ctrl1_front(S) = false -- otherwise
dec $test_ctrl1_seek(pstate, nat) : pstate
def $test_ctrl1_seek(S, 0) = S
def $test_ctrl1_seek(S, n) = S
  -- if $(n > 0)
  -- if $test_ctrl1_front(S) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET) \/ S.TODO = eps
def $test_ctrl1_seek(S, n) = $test_ctrl1_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_ctrl1_front(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S.TODO =/= eps
dec $test_ctrl1_event(pevent) : nat*
def $test_ctrl1_event(OUTPUT n*) = n*
def $test_ctrl1_event(pevent) = eps -- otherwise
dec $test_ctrl1_output(pevent*) : nat*
def $test_ctrl1_output(eps) = eps
def $test_ctrl1_output(pevent :: pevent_tail*) = $test_ctrl1_event(pevent) ++ $test_ctrl1_output(pevent_tail*)
'''


def lines(text):
    return [x.strip() for x in text.splitlines() if x.strip()]


def checks(name, program, path):
    encoded = json.dumps(base64.b64encode(os.fsencode(path)).decode())
    values = ['S_initial = $php_run(' + program + ', 0, ' + encoded + ')',
              'S_initial.COMPLETION = BUDGET']
    values += lines(r'''
S_found = $test_ctrl1_seek(S_initial, 1024)
S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET
S = S_found[.COMPLETION = NORMAL]
$test_ctrl1_front(S)
S.CURRENT = (pcallcontext)
$goto_plain_context(S, pcallcontext)
$goto_plain_buffers(S)
$goto_plain_stack(S)
$goto_plain_control(S)
S.ACTIVEFIBER = eps /\ S.FIBERCALLERS = eps /\ S.FIBERCLOSERS = eps
S.TICKENTRIES = eps /\ S.RETIREDOWNERS = eps
S.TODO = (STMT (NStmtGoto phpType11 metadata_goto)) :: ptask_old*
S.ORIGIN = (PORIGIN n_unit pcpath_source)
$goto_task_valid(S, NStmtGoto phpType11 metadata_goto, S.ORIGIN)
$goto_target(S, PORIGIN n_unit pcpath_source) = (pcpath_target)
$goto_site(S, PORIGIN n_unit pcpath_source, pcpath_target)
~$goto_site(S, PORIGIN n_unit pcpath_source, pcpath_source)
$origin_node(S.SOURCES, PORIGIN n_unit pcpath_target) = (NStmtLabel phpType11_label metadata_label)
$(|pcpath_target| >= 2)
n_parent = $(|pcpath_target| - 2)
pcpath_declare = pcpath_target[0:n_parent]
pcpath_target = pcpath_declare ++ [PCFIELD 1, PCINDEX 1]
$origin_node(S.SOURCES, PORIGIN n_unit pcpath_declare) = (NStmtDeclare (SEQUENCE phpType49*) (SEQUENCE statement_body*) metadata_declare)
phpType49* = [NDeclareItem (NIdentifier (BYTES text_directive) metadata_directive) expression_directive metadata_item]
$base64(text_directive) = $ptascii("ticks")
$parser_literal(expression_directive) = (PINT 0)
$goto_plain_origin(S, (PORIGIN n_unit pcpath_declare))
$goto_plain_origin(S, (PORIGIN n_unit pcpath_target))
$unknown_declare_valid(S[.ORIGIN = (PORIGIN n_unit pcpath_declare)], NStmtDeclare (SEQUENCE phpType49*) (SEQUENCE statement_body*) metadata_declare)
$goto_base(S, PORIGIN n_unit pcpath_source) = GOTOTASKS ptask_base*
$goto_find(S, PORIGIN n_unit pcpath_target, ptask_base*, ptask_old*) = GOTOTASKS ptask_new*
ptask_new* = (AT (PORIGIN n_unit pcpath_target) (STMT (NStmtLabel phpType11_label metadata_label))) :: ptask_after_label*
$goto_markers_valid(S, ptask_new*)
~$goto_exits_finally(S, PORIGIN n_unit pcpath_source, pcpath_target)
~$goto_plain_context(S, pcallcontext[.CALLSITE = eps])
~$goto_plain_control(S[.CURRENT = (pcallcontext[.CALLSITE = eps])])
~$goto_task_valid(S, NStmtGoto phpType11 metadata_goto, eps)
S_popped = S[.TODO = ptask_old*]
S_raw = $goto_jump(S_popped, PORIGIN n_unit pcpath_source, pcpath_target)
S_raw.COMPLETION = NORMAL
S_raw.TODO = ptask_new*
S_raw.STORE = S.STORE /\ S_raw.ENV = S.ENV /\ S_raw.FRAMES = S.FRAMES
S_raw.EVENTS = S.EVENTS
PhpStep: S ~> S_raw
S_pause = $drive(S, 0)
S_pause = S[.COMPLETION = BUDGET]
$call_descriptors_valid(S_pause)
$heap_valid($heap_graph(S_pause))
S_one = $drive(S, 1)
S_one = S_raw[.COMPLETION = BUDGET]
$drive(S_pause[.COMPLETION = NORMAL], 1) = S_one
$call_descriptors_valid(S_one)
$heap_valid($heap_graph(S_one))
''')
    if name == 'ctrl1-declare-forward':
        values += lines(r'''
$test_ctrl1_output(S.EVENTS) = $ptascii("ENTER|")
$effect_below(pcpath_declare, pcpath_source) = false
$goto_plain_bindings(S, S.ENV)
''')
    else:
        assert name == 'ctrl1-declare-backward-loop'
        values += lines(r'''
$test_ctrl1_output(S.EVENTS) = $ptascii("PREFIX|COUNT|1|")
$effect_below(pcpath_declare, pcpath_source)
$lookup(S.ENV, $ptascii("tests")) = (n_tests)
S.STORE[n_tests] = DEFINED (PINT 1)
$lookup(S.ENV, $ptascii("count")) = (n_count)
S.STORE[n_count] = DEFINED (PINT 1)
~$goto_plain_slot(S[.REFCELLS = S.REFCELLS ++ [n_count]], n_count)
~$goto_plain_control(S[.REFCELLS = S.REFCELLS ++ [n_count]])
$(|pcpath_declare| >= 2)
n_loop = $(|pcpath_declare| - 2)
pcpath_loop = pcpath_declare[0:n_loop]
$origin_node(S.SOURCES, PORIGIN n_unit pcpath_loop) = (statement_loop)
$goto_loop_statement(statement_loop)
$goto_saved(ptask_old*, PORIGIN n_unit pcpath_loop) = GOTOTASKS ptask_saved*
ptask_saved* = (LOOP_NEXT statement_loop (PORIGIN n_unit pcpath_loop)) :: ptask_outer*
$goto_saved(S_one.TODO, PORIGIN n_unit pcpath_loop) = GOTOTASKS ptask_saved*
$goto_marker_valid(S_one, LOOP_NEXT statement_loop (PORIGIN n_unit pcpath_loop))
''')
    return values


def run(out=None, process_seconds=180):
    catalog = {x['id']: x for x in json.loads(CATALOG.read_bytes())}
    out = Path(out) if out else Path(tempfile.mkdtemp(prefix='plain-goto-declare-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    modules = [ROOT / x for x in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    records = []
    for name, digest in EXPECTED.items():
        row = catalog[name]
        assert row['source_sha256'] == digest == hashlib.sha256(row['source'].encode()).hexdigest()
        directory = out / name
        directory.mkdir()
        source = directory / 'source.php'
        source.write_text(row['source'])
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted']
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok']
        finally:
            adapter.close()
        conditions = checks(name, checked['fixture'], source)
        fixture = directory / 'test.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- ' + (x if x.startswith('PhpStep:') else 'if ' + x) + '\n' for x in conditions))
        (directory / 'assertions.json').write_text(json.dumps(conditions, indent=2) + '\n')
        process = recorded([ROOT / 'tests/semantics/_build/default/numeric_runner.exe', '--sl', *modules, fixture], directory, 'model', environment, process_seconds)
        passed = process['exit'] == 0 and not process['timeout'] and (directory / 'model.stdout').read_bytes() == b'true\n' and (directory / 'model.stderr').read_bytes() == b''
        records.append({'id': name, 'source_sha256': digest, 'assertions': len(conditions), 'process': process, 'passed': passed})
        print(name, len(conditions), 'PASS' if passed else 'FAIL', flush=True)
        if not passed:
            break
    report = {'revision': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'selection': list(EXPECTED), 'records': records, 'passed': len(records) == len(EXPECTED) and all(x['passed'] for x in records)}
    (out / 'raw-report.json').write_text(json.dumps(report, indent=2) + '\n')
    return report['passed']


if __name__ == '__main__':
    raise SystemExit(0 if run() else 1)
