#!/usr/bin/env python3
"""Source-reached buffer ownership, capability notices and lifecycle states."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker
import output_buffer_sources as sources

ROOT = sources.ROOT
CASES = {
    'budget-copy': (b'<?php ob_start(); echo "A"; $x=ob_get_contents(); echo "B"; $y=ob_get_clean(); echo $x,"/",$y;', b'A/AB'),
    'chunks': sources.CASES['chunk-whole'],
    'notice-child': (b'<?php $n=0; set_error_handler(function($c,$m){global $n; $n=$n+1; if($n === 1){ob_start();} echo "H"; return true;}); ob_start(null,0,0); echo "A"; $s=ob_get_clean(); $c=ob_get_clean(); echo "|",$s,"/",$c;', b'A|A/HH'),
    'shutdown-order': (b'<?php class C{function __destruct(){echo "D",ob_get_level();}} ob_start(null,0,0); $c=new C; echo "A"; register_shutdown_function(function(){echo "S",ob_get_level();});', b'AS1D1'),
    'blocked-warning': (sources.CONTROLS['stdout-warning'], None),
}
PREFIX = r'''
dec $ob_test_output(pevent*) : preqbytes
def $ob_test_output(eps) = eps
def $ob_test_output((OUTPUT n*) :: pevent*) = n* ++ $ob_test_output(pevent*)
dec $ob_test_is_output(pevent) : bool
def $ob_test_is_output(OUTPUT n*) = true
def $ob_test_is_output(pevent) = false -- otherwise
def $ob_test_output(pevent :: pevent_tail*) = $ob_test_output(pevent_tail*) -- if ~$ob_test_is_output(pevent)
dec $ob_test_phase(pstate, nat) : bool
def $ob_test_phase(S, 0) = true
  -- if S.TODO = (OB_PARSE pconfigcall 0 eps) :: ptask_tail*
  -- if pconfigcall.KIND = INTRINSIC_OB_GET_CONTENTS
  -- if S.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES ([65])}]
def $ob_test_phase(S, 1) = true
  -- if S.OUTPUTBUFFERS = [{ID 1, HANDLER eps, CHUNK 3, FLAGS 20592, SIZE 4096, BYTES eps}, {ID 0, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES ([97,98,99,100,101,102])}]
def $ob_test_phase(S, 2) = true
  -- if S.TODO = (OB_NOTICE_RESULT pobnotice) :: ptask_tail*
  -- if pobnotice.SECOND /\ ~pobnotice.WRAPPER
  -- if S.OUTPUTBUFFERS = [{ID 1, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES ([72])}, {ID 0, HANDLER eps, CHUNK 0, FLAGS 0, SIZE 16384, BYTES ([65])}]
def $ob_test_phase(S, 3) = true
  -- if S.TODO = (OB_NOTICE_RESULT pobnotice) :: ptask_tail*
  -- if pobnotice.WRAPPER
  -- if S.OUTPUTBUFFERS = [{ID 1, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES ([72,72])}, {ID 0, HANDLER eps, CHUNK 0, FLAGS 0, SIZE 16384, BYTES ([65])}]
def $ob_test_phase(S, 4) = true
  -- if S.SHUTDOWN.PHASE = SHUTDOWN_RUNNING
  -- if S.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 0, FLAGS 0, SIZE 16384, BYTES ([65])}]
def $ob_test_phase(S, n) = false -- otherwise
dec $ob_test_seek(pstate, nat, nat) : pstate
def $ob_test_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $ob_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ob_test_phase(S, n_phase)
def $ob_test_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ob_test_phase(S, n_phase)
def $ob_test_seek(S, n_phase, n) = $ob_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ob_test_phase(S, n_phase) /\ $(n > 0)
'''


def bytes_expr(value):
    import base64
    return '$base64(' + json.dumps(base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))',
            '$output_state_valid(' + state + ')']


def seek(parent, state, phase):
    return [state + '_found = $ob_test_seek(' + parent + ', ' + str(phase) + ', 1024)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$ob_test_phase(' + state + ', ' + str(phase) + ')', *valid(state)]


def assertions(name, fixture, directory, path):
    initial = '$php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, 'S_initial.COMPLETION = BUDGET',
              'S_initial.OUTPUTBUFFERS = eps /\\ ~S_initial.OUTPUTBLOCKED /\\ S_initial.OUTPUTIMPLICIT', *valid('S_initial')]
    if name == 'blocked-warning':
        return checks + ['S_blocked = $drive_steps(S_initial[.COMPLETION = NORMAL], 1024)',
                         'S_blocked.COMPLETION = UNSUPPORTED "stdout diagnostic rendering inside an output buffer"',
                         'S_blocked.OUTPUTBLOCKED /\\ S_blocked.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES eps}]',
                         '$ob_test_output(S_blocked.EVENTS) = ([80])',
                         'S_reblocked = $output_guard(S_blocked[.COMPLETION = NORMAL])',
                         'S_reblocked.COMPLETION = S_blocked.COMPLETION',
                         'S_preserved = $output_finalize(S_reblocked)',
                         'S_preserved.OUTPUTBUFFERS = S_blocked.OUTPUTBUFFERS /\\ S_preserved.EVENTS = S_blocked.EVENTS', *valid('S_blocked')]
    phase = {'budget-copy': 0, 'chunks': 1, 'notice-child': 2, 'shutdown-order': 4}[name]
    checks += seek('S_initial', 'S_reached', phase)
    checks += ['$ob_test_output(S_reached.EVENTS) = eps',
               'S_budget = $drive_steps(S_reached, 0)', 'S_budget.COMPLETION = BUDGET',
               'S_budget.OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS',
               'S_budget.EVENTS = S_reached.EVENTS', *valid('S_budget')]
    if name == 'budget-copy':
        checks += ['S_reached.TODO = (OB_PARSE pconfigcall 0 eps) :: ptask_tail*',
                   '~$ob_parse_valid(S_reached, pconfigcall, 1, [PINT 7])',
                   '~$config_invoke_valid(S_reached, pconfigcall[.LINE = $(pconfigcall.LINE + 1)])',
                   '~$config_invoke_valid(S_reached, pconfigcall[.SITE = PORIGIN 999 eps])',
                   'S_copied = $drive_steps(S_reached, 1)',
                   'S_copied.COMPLETION = BUDGET',
                   'S_copied.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_copy) ([65]))',
                   'n_copy = |S_reached.STRINGDATA|',
                   'S_copied.STRINGDATA[n_copy] = ([65])',
                   'S_copied.OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS', *valid('S_copied'),
                   'S_malformed = S_reached[.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 4096, BYTES ([65])}]]',
                   '~$output_state_valid(S_malformed) /\\ ~$call_descriptors_valid(S_malformed)',
                   '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 0, FLAGS 112, SIZE 16384, BYTES ([256])}]])',
                   '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 0, FLAGS 8192, SIZE 16384, BYTES eps}]])',
                   '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 0, FLAGS 4096, SIZE 16384, BYTES eps}]])',
                   '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 0, FLAGS 4294967408, SIZE 16384, BYTES eps}]])']
    if name == 'chunks':
        checks += ['~$output_state_valid(S_reached[.OUTPUTBUFFERS = [{ID 0, HANDLER eps, CHUNK 3, FLAGS 112, SIZE 4096, BYTES ([65,66,67])}]])',
                   '$ob_test_output($output_finalize(S_reached[.COMPLETION = SOURCE_PENDING]).EVENTS) = eps',
                   '$output_finalize(S_reached[.COMPLETION = SOURCE_PENDING]).OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS',
                   '$output_finalize(S_reached[.COMPLETION = UNSUPPORTED "dependency"]).OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS']
    if name == 'notice-child':
        checks += ['S_reached.TODO = (OB_NOTICE_RESULT pobnotice_first) :: ptask_first_tail*',
                   'pobnotice_first.VALUE = PSTRING_CARRIER (REQUEST_STRING n_saved) ([65])',
                   'S_reached.STRINGDATA[n_saved] = ([65])',
                   'pobnotice_first.LEVEL = (0)',
                   '~$ob_notice_valid(S_reached, pobnotice_first[.TAIL = eps])',
                   '~$ob_notice_valid(S_reached, pobnotice_first[.CALL.LINE = $(pobnotice_first.CALL.LINE + 1)])',
                   '~$ob_notice_valid(S_reached, pobnotice_first[.OWNER = $(pobnotice_first.OWNER + 1)])',
                   '~$ob_notice_valid(S_reached, pobnotice_first[.VALUE = PSTRING_CARRIER (REQUEST_STRING (|S_reached.STRINGDATA|)) ([65])])']
        checks += seek('S_reached', 'S_wrapper', 3)
        checks += ['S_wrapper.TODO = (OB_NOTICE_RESULT pobnotice_second) :: ptask_second_tail*',
                   'pobnotice_second.VALUE = pobnotice_first.VALUE /\\ pobnotice_second.LEVEL = (1)',
                   '$ob_notice_message(pobnotice_first) = ' + bytes_expr(b'ob_get_clean(): Failed to discard buffer of default output handler (0)'),
                   '$ob_notice_message(pobnotice_second) = ' + bytes_expr(b'ob_get_clean(): Failed to delete buffer of default output handler (1)'),
                   'S_result = $drive_steps(S_wrapper, 1)',
                   'S_result.RESULT = KNOWN pobnotice_first.VALUE',
                   'S_result.OUTPUTBUFFERS = S_wrapper.OUTPUTBUFFERS', *valid('S_result')]
    checks += ['S_done = $drive_steps(S_reached, 2048)',
               'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
               'S_done.OUTPUTBUFFERS = eps /\\ ~S_done.OUTPUTBLOCKED',
               '$ob_test_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-buffer-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    before = sources.fingerprint(); before['tests/semantics/output_buffer_state.py'] = sources.sha(Path(__file__))
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
            bodies.append('dec $ob_case_' + str(index) + '() : bool\ndef $ob_case_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\n'.join(bodies) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $ob_case_' + str(index) + '()\n' for index in range(len(bodies))))
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
        report['after'] = sources.fingerprint(); report['after']['tests/semantics/output_buffer_state.py'] = sources.sha(Path(__file__))
        report['passed'] = report['passed'] and report['before'] == report['after']
        report['runner_sha256'] = sources.sha(ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
