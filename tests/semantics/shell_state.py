#!/usr/bin/env python3
"""Reached shell requests: authentication, byte ownership, handlers and resumption."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile

from recorded_worker import Worker
import shell_sources as sources

ROOT = sources.ROOT
PREFIX = r'''
dec $shell_test_output(pevent*) : preqbytes
def $shell_test_output(eps) = eps
def $shell_test_output((OUTPUT n*) :: pevent*) = n* ++ $shell_test_output(pevent*)
dec $shell_test_is_output(pevent) : bool
def $shell_test_is_output(OUTPUT n*) = true
def $shell_test_is_output(pevent) = false -- otherwise
def $shell_test_output(pevent :: pevent_tail*) = $shell_test_output(pevent_tail*) -- if ~$shell_test_is_output(pevent)
dec $shell_test_phase(pstate, nat) : bool
def $shell_test_phase(S, 0) = true -- if S.TODO = (SHELL_INVOKE porigin z) :: ptask_tail*
def $shell_test_phase(S, 1) = true
  -- if S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
  -- if perrorcall.RESUME = SHELL_WARNING_RESULT pshellcontext
def $shell_test_phase(S, 2) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $error_context_call(S, pcallcontext) = (perrorcall)
  -- if perrorcall.RESUME = SHELL_WARNING_RESULT pshellcontext
def $shell_test_phase(S, 3) = true -- if S.TODO = (SHELL_WARNING_RESULT pshellcontext) :: ptask_tail*
def $shell_test_phase(S, n) = false -- otherwise
dec $shell_test_seek(pstate, nat, nat) : pstate
def $shell_test_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $shell_test_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $shell_test_phase(S, n_phase)
def $shell_test_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$shell_test_phase(S, n_phase)
def $shell_test_seek(S, n_phase, n) = $shell_test_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$shell_test_phase(S, n_phase) /\ $(n > 0)
'''
GROUPS = ['literal', 'binary-output', 'empty-output', 'stringable-once', 'array-handler',
          'command-empty', 'command-nul', 'cast-throw', 'read-throw',
          'pipe-failure-handler', 'pipe-failure-throw']


def byte_expr(value):
    return '$base64(' + json.dumps(sources.b64(value)) + ')'


def request_expr(path, directory):
    env = ', '.join('(' + byte_expr(name) + ', ' + byte_expr(value) + ')' for name, value in sources.ENV)
    return ('{ENV ([' + env + ']), ARGV ([' + byte_expr(os.fsencode(path)) + ']), FILE ' +
            byte_expr(os.fsencode(path)) + ', SECONDS 0, MICROSECONDS 0, VARIABLES ' +
            byte_expr(b'EGPCS') + ', JIT true, CWD (' + byte_expr(os.fsencode(directory)) + ')}')


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))',
            '$shell_state_valid(' + state + ')']


def seek(parent, state, phase):
    return [state + '_found = $shell_test_seek(' + parent + ', ' + str(phase) + ', 1024)',
            state + '_found.COMPLETION = NORMAL \\/ ' + state + '_found.COMPLETION = BUDGET',
            state + ' = ' + state + '_found[.COMPLETION = NORMAL]',
            '$shell_test_phase(' + state + ', ' + str(phase) + ')', *valid(state)]


def response(fact, nonce):
    identity = (str(nonce) + ' pshellcontext.CWD pshellcontext.ENV ' + byte_expr(fact['command']))
    if fact['opened']:
        return 'SHELL_OPENED ' + identity + ' ' + byte_expr(fact['stdout']) + ' ' + byte_expr(fact['stderr'])
    return 'SHELL_OPEN_FAILED ' + identity


def assertions(name, fixture, directory, path):
    source, expected, facts = sources.CASES[name]
    initial = '$php_request_file_run(' + fixture + ', 0, ' + byte_expr(os.fsencode(path)) + ', ' + \
        request_expr(path, directory) + ', ' + byte_expr(os.fsencode(directory)) + ')'
    checks = ['S_initial = ' + initial, 'S_initial.COMPLETION = BUDGET', *valid('S_initial')]
    if name in ('cast-throw', 'read-throw'):
        checks += ['S_done = $drive_steps(S_initial[.COMPLETION = NORMAL], 1024)',
                   'S_done.COMPLETION = NORMAL /\\ S_done.SHELLSEQ = 0 /\\ S_done.SHELLCONTEXT = eps',
                   '$shell_test_output(S_done.EVENTS) = ' + byte_expr(expected), *valid('S_done')]
        return checks
    checks += seek('S_initial', 'S_invoke', 0)
    checks += ['S_invoke.TODO = (SHELL_INVOKE porigin_0 z_0) :: ptask_tail_0*',
               '$shell_site_valid(S_invoke, porigin_0, z_0)',
               'S_invoke.SHELLSEQ = 0 /\\ S_invoke.SHELLCONTEXT = eps']
    if not facts:
        checks += ['S_done = $drive_steps(S_invoke, 1024)',
                   'S_done.COMPLETION = NORMAL /\\ S_done.SHELLSEQ = 0 /\\ S_done.SHELLCONTEXT = eps',
                   '$shell_test_output(S_done.EVENTS) = ' + byte_expr(expected), *valid('S_done')]
        return checks
    parent = 'S_invoke'
    for index, fact in enumerate(facts):
        round_start = len(checks)
        suffix = str(index)
        before = 'S_before_' + suffix
        wait = 'S_wait_' + suffix
        resumed = 'S_resumed_' + suffix
        checks += [before + ' = ' + parent,
                   before + '.RESULT = KNOWN pvalue_command_' + suffix,
                   '$string_bytes(pvalue_command_' + suffix + ') = (' + byte_expr(fact['command']) + ')',
                   wait + ' = $drive_steps(' + before + ', 1)',
                   wait + '.COMPLETION = SOURCE_PENDING /\\ ' + wait + '.SERVICELEFT = (0)',
                   wait + '.SHELLCONTEXT = (pshellcontext)',
                   'pshellcontext.COMMAND = pvalue_command_' + suffix,
                   'pshellcontext.SITE = porigin /\\ pshellcontext.LINE = z',
                   'pshellcontext.FRAMEOWNER = |' + wait + '.FRAMES|',
                   'pshellcontext.NONCE = ' + suffix,
                   '$shell_pending_state_valid(' + wait + ')', *valid(wait),
                   'pshellresponse = ' + response(fact, index),
                   '$shell_response_valid(' + wait + ', pshellresponse)']
        if index == 0:
            for label, changed in [
                ('nonce', wait + '[.SHELLSEQ = 77]'),
                ('origin', wait + '[.ORIGIN = eps]'),
                ('cwd', wait + '[.FILECWD = (' + byte_expr(b'/foreign') + ')]'),
                ('result', wait + '[.RESULT = KNOWN (PINT 0)]'),
                ('base', wait + '[.BASE = BASE_VALUE (KNOWN (PINT 0))]'),
                ('tail', wait + '[.TODO = ' + wait + '.TODO ++ [DISCARD]]'),
                ('line', wait + '[.SHELLCONTEXT = (pshellcontext[.LINE = $(z + 1)])]'),
                ('command', wait + '[.SHELLCONTEXT = (pshellcontext[.COMMAND = (PSTRING ' + byte_expr(b'foreign') + ')])]'),
                ('owner', wait + '[.SHELLCONTEXT = (pshellcontext[.FRAMEOWNER = 77])]'),
                ('env', wait + '[.SHELLCONTEXT = (pshellcontext[.ENV = eps])]'),
            ]:
                state = 'S_bad_' + label
                checks += [state + ' = ' + changed, '~$shell_pending_state_valid(' + state + ')',
                           '~$call_descriptors_valid(' + state + ')',
                           '~$shell_response_valid(' + state + ', pshellresponse)']
            checks += ['~$shell_response_valid(' + wait + '[.SERVICELEFT = eps], pshellresponse)',
                       '~$shell_response_valid(' + wait + ', SHELL_OPEN_FAILED 77 pshellcontext.CWD pshellcontext.ENV ' + byte_expr(fact['command']) + ')',
                       '~$shell_response_valid(' + wait + ', SHELL_OPEN_FAILED 0 pshellcontext.CWD eps ' + byte_expr(fact['command']) + ')',
                       '~$shell_response_valid(' + wait + ', SHELL_OPEN_FAILED 0 pshellcontext.CWD pshellcontext.ENV ' + byte_expr(b'foreign') + ')',
                       '~$shell_response_valid(' + wait + ', SHELL_OPENED 0 pshellcontext.CWD pshellcontext.ENV ' + byte_expr(fact['command']) + ' ([256]) eps)']
        checks += [resumed + '_budget = $shell_continue(' + wait + ', pshellresponse)',
                   resumed + '_budget.COMPLETION = BUDGET',
                   resumed + ' = ' + resumed + '_budget[.COMPLETION = NORMAL]',
                   resumed + '.SHELLCONTEXT = eps /\\ ' + resumed + '.SERVICELEFT = eps',
                   resumed + '.SHELLSEQ = ' + str(index + 1), *valid(resumed),
                   'S_replay_' + suffix + ' = $shell_resume(' + resumed + ', pshellresponse)',
                   'S_replay_' + suffix + '.COMPLETION = UNSUPPORTED "invalid shell provider response"']
        if fact['opened']:
            if fact['stdout']:
                checks += [resumed + '.RESULT = KNOWN (PSTRING_CARRIER (REQUEST_STRING n_output_' + suffix + ') ' + byte_expr(fact['stdout']) + ')',
                           resumed + '.STRINGDATA[n_output_' + suffix + '] = ' + byte_expr(fact['stdout']),
                           'n_output_' + suffix + ' = |' + wait + '.STRINGDATA|',
                           '|' + resumed + '.STRINGDATA| = $(n_output_' + suffix + ' + 1)']
            else:
                checks += [resumed + '.RESULT = KNOWN PNULL', resumed + '.STRINGDATA = ' + wait + '.STRINGDATA']
        else:
            checks += seek(resumed, 'S_handler', 1)
            checks += seek('S_handler', 'S_entered', 2)
            checks += ['S_entered.CURRENT = (pcallcontext)',
                       '$error_context_trigger(S_entered, pcallcontext) = (pconfigcall)',
                       'pconfigcall.KIND = INTRINSIC_SHELL_EXEC',
                       'pconfigcall.SENT = [NAMED_SENT (KNOWN pshellcontext.COMMAND)]',
                       '$error_handler_trace_values(S_entered, pcallcontext, pconfigcall) = [pshellcontext.COMMAND]']
            if name == 'pipe-failure-handler':
                checks += seek('S_entered', 'S_false', 3)
                checks += ['S_false.TODO = (SHELL_WARNING_RESULT pshellcontext) :: ptask_tail*',
                           'S_false_result = $drive_steps(S_false, 1)',
                           'S_false_result.COMPLETION = BUDGET',
                           'S_false_result.RESULT = KNOWN (PBOOL false)',
                           'S_false_result.TODO = pshellcontext.TAIL',
                           'S_false_result.SHELLSEQ = 1', *valid('S_false_result')]
        parent = resumed
        if index + 1 < len(facts):
            next_state = 'S_next_' + suffix
            checks += seek(parent, next_state, 0)
            parent = next_state
            checks += [parent + '.TODO = (SHELL_INVOKE porigin_' + str(index + 1) + ' z_' + str(index + 1) + ') :: ptask_tail_' + str(index + 1) + '*']
        checks[round_start:] = [re.sub(r'\b(pshellcontext|pshellresponse|porigin|z|ptask_tail)\b',
                                      lambda match: match[0] + '_' + suffix, check)
                                for check in checks[round_start:]]
    checks += ['S_done = $drive_steps(' + parent + ', 2048)',
               'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps',
               'S_done.SHELLCONTEXT = eps /\\ S_done.SHELLSEQ = ' + str(len(facts)),
               '$shell_test_output(S_done.EVENTS) = ' + byte_expr(expected), *valid('S_done')]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else GROUPS
    assert selected and all(name in GROUPS for name in selected) and len(selected) == len(set(selected))
    out = args.output or Path(tempfile.mkdtemp(prefix='shell-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    before = sources.fingerprint()
    before['tests/semantics/shell_state.py'] = sources.sha(Path(__file__))
    report = {'before': before, 'groups': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    bodies = []
    try:
        for index, name in enumerate(selected):
            directory = out / name; directory.mkdir()
            path = directory / 'source.php'; path.write_bytes(sources.CASES[name][0])
            sources.native_case(name, directory, path)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                               'extension=' + str(ROOT / '.tools/php-file.so'),
                               str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': sources.b64(path.read_bytes())})
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            checks = assertions(name, checked['fixture'], directory, path)
            bodies.append('dec $shell_case_' + str(index) + '() : bool\ndef $shell_case_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\n'.join(bodies) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $shell_case_' + str(index) + '()\n' for index in range(len(bodies))))
        report['fixture_sha256'] = sources.sha(fixture)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = sources.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                              *[str(ROOT / name) for name in modules], str(fixture)], out, 'state')
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (
            result.returncode, result.stdout, result.stderr)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = sources.fingerprint()
        report['after']['tests/semantics/shell_state.py'] = sources.sha(Path(__file__))
        report['passed'] = report['passed'] and report['before'] == report['after']
        report['runner_sha256'] = sources.sha(ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
