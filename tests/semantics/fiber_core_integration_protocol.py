"""Genuine eval response, Stringable owner, and reporting Fiber C result."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from exception_handler_review import recorded
from recorded_worker import Worker
from error_handler_protocol import PREFIX

SOURCE_ID = 'review-fiber-core-reporting-current-parent-stringable-eval-cv-emission'
CASE = {
    'source': next(row['source'] for row in json.loads(Path(__file__).with_name('fiber_review_cases.json').read_text()) if row['id'] == SOURCE_ID),
    'stage': 'S.TODO = [FIBER_CORE_RESULT n pconfigcall, FIBER_FINISH n] -- if S.RESULT = KNOWN (PINT 19)',
    'checks': ['S.ACTIVEFIBER = (n)',
 '$fiber_at(S, n) = (pfiber)',
 'pfiber.TARGET = (FIBER_REPORTING_TARGET)',
 'pfiber.STATUS = FIBER_RUNNING',
 '~pfiber.RETURNED',
 'pfiber.VALUE = PNULL',
 'pfiber.ENTRY = ({SLOTS pconfigcall.SENT, NAMED eps})',
 'pconfigcall.SENT = [NAMED_SENT (KNOWN (PFLOAT 4612811918334230528))]',
 'S.CURRENT = eps',
 'S.FRAMES = eps',
 'S.ORIGIN = (pconfigcall.SITE)',
 'S.REPORTING = 2',
 'S.REPORTINGINI = $ptascii("2")',
 '$task_nodes(FIBER_CORE_RESULT n pconfigcall) = eps',
 '$heap_owners($heap_graph(S), HOBJECT n) = 2',
 '$fiber_core_result_valid(S, n, pconfigcall)',
 '$call_descriptors_valid(S)',
 '$heap_valid($heap_graph(S))',
 'pconfigcall_bad = pconfigcall[.LINE = 0]',
 'S_bad = S[.TODO = [FIBER_CORE_RESULT n pconfigcall_bad, FIBER_FINISH n]]',
 '$heap_graph(S_bad) = $heap_graph(S)',
 '~$call_descriptors_valid(S_bad)',
 'S_duplicate = S[.TODO = [FIBER_CORE_RESULT n pconfigcall, FIBER_CORE_RESULT n pconfigcall, '
 'FIBER_FINISH n]]',
 '$heap_graph(S_duplicate) = $heap_graph(S)',
 '~$fiber_core_result_valid(S_duplicate, n, pconfigcall)',
 '~$call_descriptors_valid(S_duplicate)',
 'S_paused = $drive(S, 0)',
 'S_paused.COMPLETION = BUDGET',
 'S_paused[.COMPLETION = NORMAL] = S',
 'S_one = $drive_steps(S_paused[.COMPLETION = NORMAL], 1)',
 'S_one.COMPLETION = BUDGET',
 'S_one.TODO = [FIBER_FINISH n]',
 'S_one.ORIGIN = eps',
 'S_one.RESULT = KNOWN (PINT 19)',
 'S_one.OBJECTS = S.OBJECTS',
 'S_one.FIBERCALLERS = S.FIBERCALLERS',
 '$call_descriptors_valid(S_one[.COMPLETION = NORMAL])'],
}
CHILD = b'echo $probe;'
CHECKS = r'''
S_wait.COMPLETION = SOURCE_PENDING
S_wait.EVALCONTEXTS = [pevalcontext]
pevalcontext.PHASE = PARSER_WAIT
n_unit = pevalcontext.UNIT
S_wait.TODO = (EVAL_AWAIT n_unit) :: pevalcontext.TAIL
pevalcontext.BYTES = $ptascii("echo $probe;")
pevalcontext.OWNER = |S_wait.FRAMES|
$(pevalcontext.OWNER > 0)
S_wait.SOURCEPENDING = eps
S_wait.FILECONTEXTS = eps
S_wait.ACTIVEFIBER = (n_fiber)
S_wait.FRAMES = pframe_active :: pframe_tail*
$call_descriptors_valid(S_wait)
$heap_valid($heap_graph(S_wait))
psourceresponse = SOURCE_ACCEPT n_unit pevalcontext.BYTES $core_eval_child()
$eval_response_valid(S_wait, psourceresponse)
S_owner_bad = S_wait[.EVALCONTEXTS = [pevalcontext[.OWNER = $(pevalcontext.OWNER + 1)]]]
$heap_graph(S_owner_bad) = $heap_graph(S_wait)
~$call_descriptors_valid(S_owner_bad)
~$eval_response_valid(S_owner_bad, psourceresponse)
$eval_resume(S_owner_bad, psourceresponse).COMPLETION = UNSUPPORTED "invalid eval parser response"
S_wait.FIBERCALLERS = [pfibercaller]
pfibercaller.VM.GLOBAL
pfibercaller.VM.FRAMES = eps
pfibercaller.VM.TODO = (FIBER_WAIT pfibercaller.API) :: ptask_wait_tail*
S_view = $fiber_vm_restore(S_wait, pfibercaller.VM)[.ACTIVEFIBER = pfibercaller.PREVIOUS][.FIBERCALLERS = eps][.COMPLETION = NORMAL][.EVALCONTEXTS = eps][.FILECONTEXTS = eps]
$fiber_vm_valid(S_wait, pfibercaller.VM, pfibercaller.PREVIOUS, eps)
$call_descriptors_scoped_valid(S_wait, S_view)
~$call_descriptors_scoped_valid(S_owner_bad, S_view)
pfibervm_direct = pfibercaller.VM[.TODO = (FIBER_WAIT pfibercaller.API) :: (EVAL_AWAIT n_unit) :: ptask_wait_tail*]
pfibervm_choose = pfibercaller.VM[.TODO = (FIBER_WAIT pfibercaller.API) :: (CHOOSE ([EVAL_AWAIT n_unit]) eps 1) :: ptask_wait_tail*]
pframe_marker = pframe_active[.TODO = [EVAL_AWAIT n_unit]]
~$eval_frames_markers_valid(S_view, [pframe_marker])
S_parked_direct = S_wait[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_direct]]]
~$fiber_vm_valid(S_parked_direct, pfibervm_direct, pfibercaller.PREVIOUS, eps)
~$call_descriptors_valid(S_parked_direct)
S_parked_choose = S_wait[.FIBERCALLERS = [pfibercaller[.VM = pfibervm_choose]]]
~$fiber_vm_valid(S_parked_choose, pfibervm_choose, pfibercaller.PREVIOUS, eps)
~$call_descriptors_valid(S_parked_choose)
S_entry = $eval_resume(S_wait, psourceresponse)
S_entry.COMPLETION = NORMAL
S_entry.TODO = (SOURCE_OPERAND_ENTER psourceoperand n_unit) :: ptask_body*
psourceoperand.INPUT = KNOWN (POBJECT n_source)
psourceoperand.OWNER = pevalcontext.OWNER
psourceoperand.KIND = 0
$source_operand_enter_valid(S_entry, psourceoperand, n_unit)
$heap_valid($heap_graph(S_entry))
$call_descriptors_valid(S_entry)
S_enter_owner_bad = S_entry[.TODO = (SOURCE_OPERAND_ENTER psourceoperand[.OWNER = $(psourceoperand.OWNER + 1)] n_unit) :: ptask_body*]
$heap_graph(S_enter_owner_bad) = $heap_graph(S_entry)
~$source_operand_enter_valid(S_enter_owner_bad, psourceoperand[.OWNER = $(psourceoperand.OWNER + 1)], n_unit)
~$call_descriptors_valid(S_enter_owner_bad)
S_enter_tail_bad = S_entry[.TODO = [SOURCE_OPERAND_ENTER psourceoperand n_unit]]
~$source_operand_enter_valid(S_enter_tail_bad, psourceoperand, n_unit)
~$call_descriptors_valid(S_enter_tail_bad)
S_reached = $seek(S_entry, 4000)
S_reached.COMPLETION = NORMAL \/ S_reached.COMPLETION = BUDGET
S = S_reached[.COMPLETION = NORMAL]
'''.strip().splitlines()


def main():
    out = Path(tempfile.mkdtemp(prefix='fiber-core-parent-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    source = out / 'source.php'
    source.write_text(CASE['source'])
    (out / 'child.php-fragment').write_bytes(CHILD)
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'], checked
        parsed_child = frontend.request({'op': 'parse-eval', 'id': '1', 'mode': 'eval',
                                        'profile': 'cli-raw-85', 'source': base64.b64encode(CHILD).decode()})
        assert parsed_child['accepted'], parsed_child
        child = adapter.request({'op': 'check', 'ast': parsed_child['ast'], 'fixture': True})
        assert child['ok'], child
    finally:
        adapter.close()
        frontend.close()
    fixture = out / 'test.watsup'
    checks = ['S_wait = $php_run(' + checked['fixture'] + ', 4000, '
              + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
              *CHECKS, CASE['stage'], *CASE['checks']]
    fixture.write_text(PREFIX.replace('STAGE', CASE['stage'])
                       + '\ndec $core_eval_child() : program\ndef $core_eval_child() = ' + child['fixture']
                       + '\ndec $main() : bool\ndef $main() = true\n'
                       + ''.join('  -- if ' + clause + '\n' for clause in checks))
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [Path(__file__), Path(__file__).with_name('fiber_review_cases.json'), source, fixture,
               ROOT / 'spec/semantics/modules.json', ROOT / 'spec/semantics/84-call-integrity.watsup',
               ROOT / 'spec/semantics/281-fibers.watsup', ROOT / 'spec/semantics/313-fiber-core-callbacks.watsup',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', ROOT / '_build/default/adapter/main.exe']
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    environment = dict(os.environ, LC_ALL='C', TZ='UTC')
    environment.pop('PHP_SPEC_SCRIPT_ENCODING', None)
    command = [ROOT / 'tests/semantics/_build/default/numeric_runner.exe', '--sl', *modules, fixture]
    process = recorded(command, out, 'model', environment, 120)
    passed = process['exit'] == 0 and not process['timeout'] and (out / 'model.stdout').read_bytes() == b'true\n' and not (out / 'model.stderr').read_bytes()
    assert inputs == {str(path.relative_to(ROOT)): sha(path) for path in watched}
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'selection': 'current-parent-authentic-eval-and-borrowed-core-result',
        'assertions': len(checks), 'process': process, 'passed': passed, 'inputs': inputs,
        'compiler': {'mode': 'SL', 'cache': False, 'determinism_checks': True,
                     'spectec_commit': 'da36ac3c434cd291940293a63da64544307730a3', 'ocaml': '5.1.0'},
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING_removed': True},
        'budgets': {'seek_steps': 4000, 'process_seconds': 120, 'jobs': 1}, 'raw': str(out)}, indent=2) + '\n')
    print('genuine-eval-core-result', passed, len(checks), flush=True)
    if not passed:
        print((out / 'model.stderr').read_text()[-2500:], flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
