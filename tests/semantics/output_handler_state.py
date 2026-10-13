#!/usr/bin/env python3
"""Genuine output-handler borrowing, zoh release, deprecation and getter states."""
import argparse
import json
import os
from pathlib import Path
import tempfile

from recorded_worker import Worker
import output_handler_sources as sources

ROOT = sources.ROOT
CASES = {
    'borrowed-alias': (b'<?php $log="";class C{function h($b,$p){global $r;$r=null;return "X".$b;}function __destruct(){global $log;$log.="D".ob_get_level();}}$r=new C;$cb=[&$r,"h"];ob_start($cb);unset($cb);echo "A";ob_end_flush();echo "(".$log.")";', b'XA(D1)'),
    'owned-pop': (b'<?php $log="";class C{function h($b,$p){return "X".$b;}function __destruct(){global $log;$log.="D".ob_get_level();}}$r=new C;$cb=[$r,"h"];ob_start($cb);unset($r,$cb);echo "A";ob_end_flush();echo "(".$log.")";', b'XA(D0)'),
    'produced-deprecation': (b'<?php $log="";set_error_handler(function($n,$m){global $log;$s=ob_get_status();$log=$s["flags"].":".ob_get_contents();echo "E";return true;});function h($b,$p){echo "H";return "X".$b;}ob_start("h");echo "A";ob_end_flush();echo "(".$log.")";', b'EXA(8305:AH)'),
    'frozen-getter': sources.CASES['get-clean-snapshot'],
    'lower-running-threshold': (b'<?php $seen="";function h($b,$p){echo "H";return "X".$b;}function eh($n,$m){global $seen;echo "E";$a=ob_get_status(true);$seen=$a[0]["buffer_used"].":".$a[0]["flags"];return true;}set_error_handler("eh");ob_start(null,1);ob_start("h");echo "A";ob_end_clean();echo "B";ob_end_clean();echo "|".$seen;', b'EB|1:32880'),
}
PREFIX = r'''
dec $oh_test_output(pevent*) : preqbytes
def $oh_test_output(eps) = eps
def $oh_test_output((OUTPUT n*) :: pevent*) = n* ++ $oh_test_output(pevent*)
dec $oh_test_is_output(pevent) : bool
def $oh_test_is_output(OUTPUT n*) = true
def $oh_test_is_output(pevent) = false -- otherwise
def $oh_test_output(pevent :: pevent_tail*) = $oh_test_output(pevent_tail*) -- if ~$oh_test_is_output(pevent)
dec $oh_test_log(pstate) : preqbytes?
def $oh_test_log(S) = $string_bytes(pvalue)
  -- if $lookup(S.ENV, ([108,111,103])) = (n_cell)
  -- if S.STORE[n_cell] = DEFINED pvalue
def $oh_test_log(S) = eps -- otherwise
dec $oh_test_phase(pstate, nat) : bool
def $oh_test_phase(S, 0) = true
  -- if S.TODO = (OB_USER_RESULT pobinvoke) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $oh_test_log(S) = (([68,49]))
def $oh_test_phase(S, 1) = true
  -- if S.TODO = (OB_USER_SEND pobinvoke 0) :: ptask_tail*
  -- if pobinvoke.CALL = OB_API pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_OB_END_FLUSH
  -- if $oh_test_log(S) = (eps)
def $oh_test_phase(S, 2) = true
  -- if S.TODO = (OB_USER_RELEASE pobrelease) :: ptask_tail*
  -- if $oh_test_output(S.EVENTS) = ([88,65])
  -- if $oh_test_log(S) = (eps)
def $oh_test_phase(S, 3) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = OB_USER_DEPRECATED pobinvoke pvalue
  -- if perrorcall.LEVEL = 8192
def $oh_test_phase(S, 4) = true
  -- if S.TODO = (OB_USER_SEND pobinvoke 0) :: ptask_tail*
  -- if pobinvoke.CALL = OB_API pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_OB_GET_CLEAN
def $oh_test_phase(S, 5) = true
  -- if S.TODO = (OB_USER_RELEASE pobrelease) :: ptask_tail*
  -- if pobrelease.CALL.KIND = INTRINSIC_OB_GET_CLEAN
def $oh_test_phase(S, 6) = true
  -- if S.OUTPUTBUFFERS = [poutputbuffer, {ID 0, HANDLER eps, CHUNK 1, FLAGS 32880, SIZE 4096, BYTES ([69])}]
  -- if poutputbuffer.ID = 1 /\ poutputbuffer.FLAGS = 8305
  -- if $ob_user_running(S)
def $oh_test_phase(S, 7) = true
  -- if S.TODO = (AT porigin (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES "Qg==") metadata_string])) metadata_echo))) :: ptask_tail*
  -- if S.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 1, FLAGS 32880, SIZE 4096, BYTES ([69])}]
  -- if ~$ob_user_running(S)
def $oh_test_phase(S, n) = false -- otherwise
dec $oh_test_seek(pstate, nat, nat) : pstate
def $oh_test_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $oh_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $oh_test_phase(S, n_phase)
def $oh_test_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$oh_test_phase(S, n_phase)
def $oh_test_seek(S, n_phase, n) = $oh_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$oh_test_phase(S, n_phase) /\ $(n > 0)
'''


def bytes_expr(value):
    return '$base64(' + json.dumps(sources.base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))',
            '$output_state_valid(' + state + ')']


def seek(parent, state, phase):
    return [state + '_found = $oh_test_seek(' + parent + ', ' + str(phase) + ', 512)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$oh_test_phase(' + state + ', ' + str(phase) + ')', *valid(state)]


def assertions(name, fixture, directory, path):
    initial = '$php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, 'S_initial.COMPLETION = BUDGET', *valid('S_initial')]
    if name == 'lower-running-threshold':
        checks += seek('S_initial', 'S_busy', 6)
        checks += ['$oh_test_output(S_busy.EVENTS) = eps',
                   'S_busy.OUTPUTBUFFERS = poutputbuffer_user :: poutputbuffer_lower :: eps',
                   '$long_and(poutputbuffer_lower.FLAGS, 32768) = 32768',
                   '$output_buffer_valid(poutputbuffer_lower)',
                   '~$output_buffer_valid(poutputbuffer_lower[.FLAGS = 112])',
                   '~$output_buffer_valid(poutputbuffer_lower[.SIZE = 4095])',
                   'S_busy_budget = $drive_steps(S_busy, 0)',
                   'S_busy_budget.COMPLETION = BUDGET',
                   'S_busy_budget.OUTPUTBUFFERS = S_busy.OUTPUTBUFFERS', *valid('S_busy_budget')]
        checks += seek('S_busy', 'S_retained', 7)
        checks += ['S_retained.OUTPUTBUFFERS = [poutputbuffer_lower]',
                   '$oh_test_output(S_retained.EVENTS) = eps',
                   '$output_write(S_retained, eps).OUTPUTBUFFERS = S_retained.OUTPUTBUFFERS',
                   'S_retained_budget = $drive_steps(S_retained, 0)',
                   'S_retained_budget.COMPLETION = BUDGET',
                   'S_retained_budget.OUTPUTBUFFERS = S_retained.OUTPUTBUFFERS', *valid('S_retained_budget'),
                   '~$output_state_valid(S_retained[.OUTPUTBUFFERS = [poutputbuffer_lower[.FLAGS = 112]]])',
                   '~$output_state_valid(S_retained[.OUTPUTBUFFERS = [poutputbuffer_lower[.BYTES = ([256])]]])',
                   'S_done = $drive_steps(S_retained, 1024)',
                   r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
                   r'S_done.OUTPUTBUFFERS = eps /\ ~$ob_user_running(S_done)',
                   '$oh_test_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
        return checks
    phase = {'borrowed-alias': 0, 'owned-pop': 1, 'produced-deprecation': 3, 'frozen-getter': 4}[name]
    checks += seek('S_initial', 'S_reached', phase)
    checks += ['S_reached.OUTPUTBUFFERS = poutputbuffer :: poutputbuffer_tail*',
               'poutputbuffer.HANDLER = (poutputhandler)',
               'poutputbuffer.ID = 0 /\\ S_reached.OUTPUTSEQ = 1',
               'poutputbuffer.CHUNK = 0 /\\ $long_and(poutputbuffer.FLAGS, 15) = 1',
               '$ob_user_running(S_reached)',
               'S_budget = $drive_steps(S_reached, 0)', 'S_budget.COMPLETION = BUDGET',
               'S_budget.OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS /\\ S_budget.TODO = S_reached.TODO', *valid('S_budget'),
               '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [poutputbuffer, poutputbuffer]])',
               '~$output_state_valid(S_reached[.OUTPUTSEQ = 0])',
               '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [poutputbuffer[.HANDLER = eps]]])',
               '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [poutputbuffer[.FLAGS = 112]]])',
               '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [poutputbuffer[.SIZE = 4096]]])',
               '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [poutputbuffer[.FLAGS = 4294967409]]])',
               '~$ob_user_handler_valid(S_reached, poutputhandler[.NAME = ([88])])',
               '~$ob_user_handler_valid(S_reached, poutputhandler[.ENTRY.CALL.SITE = PORIGIN 999 eps])']
    if name in ('borrowed-alias', 'owned-pop'):
        checks += ['poutputhandler.ZOH = PARRAY n_array',
                   'S_history = $ob_user_history(S_reached, poutputhandler)',
                   '$target_receiver(S_history, poutputhandler.ENTRY.TARGET) = (n_receiver)',
                   '$heap_count(HARRAY n_array, $machine_roots(S_reached)) = 1']
    if name == 'borrowed-alias':
        checks += ['S_reached.TODO = (OB_USER_RESULT pobinvoke) :: ptask_tail*',
                   '~((HOBJECT n_receiver) <- S_reached.ALLOCATIONS)',
                   '$heap_count(HOBJECT n_receiver, $machine_roots(S_reached)) = 0',
                   '$ob_user_live(S_reached, pobinvoke)',
                   '$call_task_valid(S_reached, OB_USER_RESULT pobinvoke)',
                   '~$call_task_valid(S_reached, OB_USER_RESULT pobinvoke[.SENT = [KNOWN (PINT 8), KNOWN (PINT 9)]])',
                   '~$call_task_valid(S_reached, OB_USER_RESULT pobinvoke[.BUFFER.ID = 1])',
                   'poutputbuffer.FLAGS = 113 /\\ poutputbuffer.BYTES = ([65])',
                   '$oh_test_output(S_reached.EVENTS) = eps']
    if name == 'owned-pop':
        checks += ['S_reached.TODO = (OB_USER_SEND pobinvoke 0) :: ptask_tail*',
                   '(HOBJECT n_receiver) <- S_reached.ALLOCATIONS',
                   '$heap_owners($heap_graph(S_reached), HARRAY n_array) = 1',
                   '$heap_owners($heap_graph(S_reached), HOBJECT n_receiver) = 1',
                   '$call_task_valid(S_reached, OB_USER_SEND pobinvoke 0)']
        checks += seek('S_reached', 'S_release', 2)
        checks += ['S_release.TODO = (OB_USER_RELEASE pobrelease) :: ptask_release_tail*',
                   'S_release.OUTPUTBUFFERS = eps /\\ ~$ob_user_running(S_release)',
                   '(HOBJECT n_receiver) <- S_release.ALLOCATIONS',
                   '$heap_count(HARRAY n_array, $machine_roots(S_release)) = 1',
                   '$call_task_valid(S_release, OB_USER_RELEASE pobrelease)',
                   '~$ob_user_release_valid(S_release, pobrelease[.BUFFER.ID = S_release.OUTPUTSEQ])',
                   '~$ob_user_release_valid(S_release, pobrelease[.BUFFER.SIZE = 4096])',
                   '~$ob_user_release_valid(S_release, pobrelease[.BUFFER.FLAGS = 1])',
                   '~$ob_user_release_valid(S_release, pobrelease[.CALL.LINE = $(pobrelease.CALL.LINE + 1)])',
                   '~$call_task_valid(S_release[.ORIGIN = eps], OB_USER_RELEASE pobrelease)']
    if name == 'produced-deprecation':
        checks += ['S_reached.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
                   'perrorcall.RESUME = OB_USER_DEPRECATED pobinvoke pvalue',
                   'poutputbuffer.FLAGS = 8305 /\\ poutputbuffer.BYTES = ([65,72])',
                   'pobinvoke.BUFFER.BYTES = ([65]) /\\ pobinvoke.PHASE = 9',
                   '$string_bytes(pobinvoke.INPUT) = (([65]))',
                   '$string_bytes(pvalue) = (([88,65]))',
                   '$ob_user_temporary(S_reached, poutputbuffer.ID)',
                   '$error_call_valid(S_reached, perrorcall)',
                   '~$error_call_valid(S_reached, perrorcall[.LINE = $(perrorcall.LINE + 1)])',
                   '~$call_task_valid(S_reached, OB_USER_DEPRECATED pobinvoke[.PHASE = 0] pvalue)',
                   '~$output_state_valid(S_reached[.TODO = eps])',
                   '$oh_test_output(S_reached.EVENTS) = eps']
    if name == 'frozen-getter':
        checks += ['S_reached.TODO = (OB_USER_SEND pobinvoke 0) :: ptask_tail*',
                   'pobinvoke.VALUE = PSTRING_CARRIER (REQUEST_STRING n_copy) ([65])',
                   'pobinvoke.INPUT = PSTRING_CARRIER (REQUEST_STRING n_input) ([65])',
                   'n_input = $(n_copy + 1)',
                   '$call_task_valid(S_reached, OB_USER_SEND pobinvoke 0)',
                   '~$call_task_valid(S_reached, OB_USER_SEND pobinvoke[.PHASE = 9] 0)',
                   '~$call_task_valid(S_reached, OB_USER_SEND pobinvoke[.VALUE = PSTRING_CARRIER (REQUEST_STRING n_copy) ([66])] 0)',
                   '$output_finalize(S_reached[.COMPLETION = SOURCE_PENDING]).OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS',
                   '$output_finalize(S_reached[.COMPLETION = UNSUPPORTED "dependency"]).OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS',
                   '$output_finalize(S_budget).OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS']
        checks += seek('S_reached', 'S_release', 5)
        checks += ['S_release.TODO = (OB_USER_RELEASE pobrelease) :: ptask_release_tail*',
                   '$call_task_valid(S_release, OB_USER_RELEASE pobrelease)',
                   'pobrelease.VALUE = pobinvoke.VALUE',
                   'S_forged = $string_request(S_release, ([66]))',
                   'S_forged.RESULT = KNOWN pvalue_forged',
                   '$string_carrier_valid(S_forged, pvalue_forged)',
                   '~$ob_user_release_valid(S_forged, pobrelease[.VALUE = pvalue_forged])']
    checks += ['S_done = $drive_steps(S_reached, 1024)',
               'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
               'S_done.OUTPUTBUFFERS = eps /\\ ~$ob_user_running(S_done)',
               '$oh_test_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-handler-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    before = sources.fingerprint(); before['tests/semantics/output_handler_state.py'] = sources.sha(Path(__file__))
    report = {'before': before, 'groups': [], 'passed': False, 'completed': False}
    bodies = []
    print(out, flush=True)
    try:
        for index, name in enumerate(selected):
            directory = out / name; directory.mkdir()
            source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
            native = sources.run([str(ROOT / '.tools/php/bin/php'), '-n', *sources.FLAGS, str(path)], directory, 'native', 10)
            if expected is not None:
                assert native.returncode == 0 and native.stdout == expected, (name, native.stdout, expected, native.stderr)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': sources.base64.b64encode(source).decode()})
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            checks = assertions(name, checked['fixture'], directory, path)
            bodies.append('dec $oh_case_' + str(index) + '() : bool\ndef $oh_case_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\n'.join(bodies) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $oh_case_' + str(index) + '()\n' for index in range(len(bodies))))
        report['fixture_sha256'] = sources.sha(fixture)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = sources.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                              *[str(ROOT / name) for name in modules], str(fixture)], out, 'state', 120)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (
            result.returncode, result.stdout, result.stderr)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = sources.fingerprint(); report['after']['tests/semantics/output_handler_state.py'] = sources.sha(Path(__file__))
        report['passed'] = report['passed'] and report['before'] == report['after']
        report['runner_sha256'] = sources.sha(ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
