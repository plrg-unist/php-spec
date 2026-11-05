#!/usr/bin/env python3
"""Source-reached prefix, producer and pending-output ownership counterexamples."""
import argparse
import json
import os
from pathlib import Path
import tempfile

from recorded_worker import Worker
import output_automatic_reference_warning_review_sources as sources

ROOT = sources.ROOT
CASES = {
    'warning-cursor-prefix': sources.CASES['print-second-warning-typed-prefix'],
    'produced-deprecation-cursor': sources.CASES['produced-deprecation-cursor-disable'],
    'typed-reference-prefix': sources.CASES['print-second-warning-typed-prefix'],
    'known-prefix-in-source-frame': sources.CASES['echo-phase-warning-known-prefix'],
    'retired-borrowed-receiver': sources.CASES['warning-retires-borrowed-receiver'],
    'pending-lower-user': sources.CASES['lower-user-threshold-skips-reference-warning'],
    'owned-stringable-prefix': sources.CASES['owned-stringable-retires-before-print-catch'],
}
PREFIX = r'''
dec $ow_output(pevent*) : preqbytes
dec $ow_is_output(pevent) : bool
def $ow_output(eps) = eps
def $ow_output((OUTPUT n*) :: pevent_tail*) = n* ++ $ow_output(pevent_tail*)
def $ow_output(pevent :: pevent_tail*) = $ow_output(pevent_tail*) -- if ~$ow_is_output(pevent)
def $ow_is_output(OUTPUT n*) = true
def $ow_is_output(pevent) = false -- otherwise
dec $ow_phase(pstate, nat) : bool
def $ow_phase(S, 0) = true
  -- if S.TODO = (OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending) :: ptask_tail*
  -- if pobinvoke.CALL = OB_WRITE pobwrite
def $ow_phase(S, 1) = true
  -- if S.TODO = (OUTPUT_FAIL_FINISH pobwrite n_pending) :: ptask_tail*
  -- if pobwrite.FINISH = OUTPUT_VM_DONE
def $ow_phase(S, 2) = true
  -- if S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_ERROR perrorcall
  -- if perrorcall.RESUME = OB_USER_REFERENCE pobinvoke 1
  -- if pobinvoke.CALL = OB_WRITE pobwrite
def $ow_phase(S, 3) = true
  -- if S.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*
  -- if papiargcursor.CALL = API_ERROR perrorcall
  -- if perrorcall.RESUME = OB_USER_DEPRECATED pobinvoke pvalue
  -- if pobinvoke.CALL = OB_WRITE pobwrite
def $ow_phase(S, 4) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_FAIL_ARGS pobinvoke n_pending) :: ptask_tail*
  -- if pdestructionoperation.SOURCE = OB_USER_REFERENCE_RELEASE pobinvoke_original n_index n_pending
def $ow_phase(S, n) = false -- otherwise
dec $ow_seek(pstate, nat, nat) : pstate
def $ow_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $ow_seek(S, n_phase, n) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $ow_phase(S, n_phase)
def $ow_seek(S, n_phase, 0) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if ~$ow_phase(S, n_phase)
def $ow_seek(S, n_phase, n) = $ow_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ow_phase(S, n_phase) /\ $(n > 0)
'''


def bytes_expr(value):
    return '$base64(' + json.dumps(sources.base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))',
            '$output_state_valid(' + state + ')']


def budget(state, target):
    return [target + ' = $drive_steps(' + state + ', 0)', target + '.COMPLETION = BUDGET',
            target + '.TODO = ' + state + '.TODO', target + '.OUTPUTBUFFERS = ' + state + '.OUTPUTBUFFERS',
            target + '.STORE = ' + state + '.STORE', target + '.ALLOCATIONS = ' + state + '.ALLOCATIONS',
            target + '.DESTRUCTION = ' + state + '.DESTRUCTION', *valid(target)]


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_automatic_reference_warning_review_state.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.common.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    phase = {'pending-lower-user': 1, 'warning-cursor-prefix': 2, 'produced-deprecation-cursor': 3}.get(name, 0)
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET', *valid('S_initial'),
              'S_found = $ow_seek(S_initial, ' + str(phase) + ', 1024)',
              r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
              'S_reached = S_found[.COMPLETION = NORMAL]', '$ow_phase(S_reached, ' + str(phase) + ')',
              *valid('S_reached'), *budget('S_reached', 'S_budget')]
    if name == 'produced-deprecation-cursor':
        checks += [
            'S_reached.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*',
            'papiargcursor.CALL = API_ERROR perrorcall',
            'perrorcall.LEVEL = 8192',
            'perrorcall.RESUME = OB_USER_DEPRECATED pobinvoke (PBOOL false)',
            'pobinvoke.CALL = OB_WRITE pobwrite',
            'pobwrite.TAIL = ptask_tail*', 'pobwrite.FINISH = OUTPUT_VM_DONE',
            'S_reached.OUTPUTBUFFERS = [poutputbuffer]',
            r'poutputbuffer.FLAGS = 8305 /\ poutputbuffer.BYTES = ([65,72])',
            '$ob_user_running(S_reached)',
            '$output_task_write(API_CALLBACK_SEND papiargcursor) = (pobwrite)',
            '$output_task_write(API_CALLBACK_REF papiargcursor) = (pobwrite)',
            '$ob_user_active_task(API_CALLBACK_SEND papiargcursor) = (pobinvoke.BUFFER.ID)',
            '$ob_user_active_task(API_CALLBACK_REF papiargcursor) = (pobinvoke.BUFFER.ID)',
            '$ob_user_disabled_task(API_CALLBACK_SEND papiargcursor, pobinvoke.BUFFER.ID)',
            '$ob_user_disabled_task(API_CALLBACK_REF papiargcursor, pobinvoke.BUFFER.ID)',
            '~$ob_user_disabled_task(API_CALLBACK_SEND papiargcursor, 999999)',
            '$call_task_valid(S_reached, API_CALLBACK_SEND papiargcursor)',
            '~$call_task_valid(S_reached, API_CALLBACK_REF papiargcursor)',
            '~$call_task_valid(S_reached, API_CALLBACK_SEND papiargcursor[.INDEX = 999])']
    elif name == 'warning-cursor-prefix':
        checks += [
            'S_reached.TODO = (API_CALLBACK_SEND papiargcursor) :: ptask_tail*',
            'papiargcursor.CALL = API_ERROR perrorcall',
            'perrorcall.RESUME = OB_USER_REFERENCE pobinvoke 1',
            'pobinvoke.CALL = OB_WRITE pobwrite',
            'pobwrite.TAIL = ptask_tail*', 'pobwrite.FINISH = OUTPUT_VM_DONE',
            'pobinvoke.SENT = [REFERENCE n_cell]',
            'S_reached.STORE[n_cell] = DEFINED pobinvoke.INPUT',
            '$string_bytes(pobinvoke.INPUT) = ([55])',
            '$heap_owners($heap_graph(S_reached), HCELL n_cell) = 1',
            '$ob_user_running(S_reached)',
            '$output_task_write(API_CALLBACK_SEND papiargcursor) = (pobwrite)',
            '$output_task_write(API_CALLBACK_REF papiargcursor) = (pobwrite)',
            '$ob_user_active_task(API_CALLBACK_SEND papiargcursor) = (pobinvoke.BUFFER.ID)',
            '$ob_user_active_task(API_CALLBACK_REF papiargcursor) = (pobinvoke.BUFFER.ID)',
            '~$ob_user_disabled_task(API_CALLBACK_SEND papiargcursor, pobinvoke.BUFFER.ID)',
            '$call_task_valid(S_reached, API_CALLBACK_SEND papiargcursor)',
            '~$call_task_valid(S_reached, API_CALLBACK_REF papiargcursor)',
            '~$call_task_valid(S_reached, API_CALLBACK_SEND papiargcursor[.INDEX = 999])',
            '~$call_task_valid(S_reached[.ORIGIN = eps], API_CALLBACK_SEND papiargcursor)']
    elif name == 'pending-lower-user':
        checks += [
            'S_reached.TODO = (OUTPUT_FAIL_FINISH pobwrite n_pending) :: ptask_tail*',
            'pobwrite.TAIL = ptask_tail*', 'pobwrite.IDS = ([1,0])',
            'pobwrite.INDEX = 2', 'pobwrite.BYTES = ([65])',
            '$ow_output(S_reached.EVENTS) = ([80,65])',
            'S_reached.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
            r'poutputbuffer_upper.FLAGS = 12401 /\ poutputbuffer_upper.SIZE = 0 /\ poutputbuffer_upper.BYTES = eps',
            r'poutputbuffer_lower.FLAGS = 12401 /\ poutputbuffer_lower.SIZE = 0 /\ poutputbuffer_lower.BYTES = eps',
            '~$ob_user_running(S_reached)', '$throwable_live(S_reached, n_pending)',
            '$lookup(S_reached.ENV, ([119,97,114,110,105,110,103,115])) = (n_warnings)',
            'S_reached.STORE[n_warnings] = DEFINED (PINT 1)',
            '$lookup(S_reached.ENV, ([108,111,119,101,114])) = (n_hits)',
            'S_reached.STORE[n_hits] = DEFINED (PINT 0)',
            '~$call_task_valid(S_reached, OUTPUT_FAIL_FINISH pobwrite[.IDS = ([0,1])] n_pending)',
            '~$call_task_valid(S_reached, OUTPUT_FAIL_FINISH pobwrite[.INDEX = 3] n_pending)',
            '~$call_task_valid(S_reached, OUTPUT_FAIL_FINISH pobwrite[.TAIL = eps] n_pending)',
            '~$call_task_valid(S_reached, OUTPUT_FAIL_FINISH pobwrite 999999)',
            '~$call_task_valid(S_reached[.ORIGIN = eps], OUTPUT_FAIL_FINISH pobwrite n_pending)']
    else:
        checks += [
            'S_reached.TODO = (OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending) :: ptask_tail*',
            'pobinvoke.CALL = OB_WRITE pobwrite', 'pobwrite.TAIL = ptask_tail*',
            'pobwrite.FINISH = OUTPUT_VM_DONE', 'pobwrite.INDEX = 0',
            'S_reached.CURRENT = pobwrite.CONTEXT',
            'S_reached.ORIGIN = ($output_caller_site(pobwrite.CALLER))',
            '$output_task_write(OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending) = (pobwrite)',
            '$ob_user_running(S_reached)', '$throwable_live(S_reached, n_pending)',
            '$ob_reference_metadata(S_reached, pobinvoke, n_index)',
            '$ob_reference_prefix(S_reached, pobinvoke, pobinvoke.SENT, 0)',
            '$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending)',
            'pobinvoke.BUFFER.HANDLER = (poutputhandler)',
            '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke 2 n_pending)',
            '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke n_index 999999)',
            '~$call_task_valid(S_reached[.ORIGIN = eps], OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending)',
            '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke[.PHASE = 0] n_index n_pending)',
            '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke[.BUFFER.ID = 999999] n_index n_pending)',
            '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke[.CALL = OB_WRITE pobwrite[.TAIL = eps]] n_index n_pending)',
            '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke[.CALL = OB_WRITE pobwrite[.IDS = eps]] n_index n_pending)',
            'S_wrong_string = $string_request(S_reached, ([88]))',
            'S_wrong_string.RESULT = KNOWN pvalue_wrong',
            '$string_carrier_valid(S_wrong_string, pvalue_wrong)',
            '~$call_task_valid(S_wrong_string, OB_USER_REFERENCE_RELEASE pobinvoke[.INPUT = pvalue_wrong] n_index n_pending)']
        if name == 'known-prefix-in-source-frame':
            checks += ['n_index = 1', 'pobinvoke.SENT = [KNOWN pobinvoke.INPUT]',
                       'S_reached.CURRENT = (pcallcontext)',
                       'pcallcontext.NAME = ([101,109,105,116])',
                       '$string_bytes(pobinvoke.INPUT) = ([65])',
                       '~$call_task_valid(S_reached[.CURRENT = eps], OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending)',
                       '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke[.CALL = OB_WRITE pobwrite[.CONTEXT = eps]] n_index n_pending)']
        elif name == 'owned-stringable-prefix':
            checks += ['n_index = 0', 'pobinvoke.SENT = eps',
                       'pobwrite.TAIL = (OUTPUT_STRING_RELEASE pobstringrelease) :: ptask_producer*',
                       'pobstringrelease.CALLER = pobwrite.CALLER',
                       '(HOBJECT pobstringrelease.OBJECT) <- S_reached.ALLOCATIONS',
                       '$heap_count(HOBJECT pobstringrelease.OBJECT, $machine_roots(S_reached)) = 1',
                       '~((HOBJECT pobstringrelease.OBJECT) <- $task_nodes(OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending))',
                       '$lookup(S_reached.ENV, ([120])) = (n_x)',
                       'S_reached.STORE[n_x] = DEFINED (PINT 99)']
        else:
            checks += ['n_index = 1', 'pobinvoke.SENT = [REFERENCE n_cell]',
                       'S_reached.STORE[n_cell] = DEFINED pobinvoke.INPUT',
                       '$heap_owners($heap_graph(S_reached), HCELL n_cell) = 1',
                       'S_extra = S_reached[.RESULT = REFERENCE n_cell]',
                       '$heap_owners($heap_graph(S_extra), HCELL n_cell) = 2',
                       '~$call_task_valid(S_extra, OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending)',
                       'S_wrong_value = S_reached[.STORE[n_cell] = DEFINED (PINT 7)]',
                       '$call_reference_operand_valid(S_wrong_value, REFERENCE n_cell)',
                       '~$call_task_valid(S_wrong_value, OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending)',
                       '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke 0 n_pending)']
            if name == 'typed-reference-prefix':
                checks += ['$string_bytes(pobinvoke.INPUT) = ([55])',
                           'S_reached.OUTPUTBUFFERS = [poutputbuffer]',
                           r'poutputbuffer.FLAGS = 32881 /\ poutputbuffer.BYTES = ([55,49,50])',
                           '$lookup(S_reached.ENV, ([120])) = (n_x)',
                           'S_reached.STORE[n_x] = DEFINED (PINT 99)']
            else:
                checks += ['poutputhandler.ZOH = PARRAY n_array',
                           'S_history = $ob_user_history(S_reached, poutputhandler)',
                           '$target_receiver(S_history, poutputhandler.ENTRY.TARGET) = (n_receiver)',
                           '~((HOBJECT n_receiver) <- S_reached.ALLOCATIONS)',
                           '$heap_count(HOBJECT n_receiver, $machine_roots(S_reached)) = 0',
                           '$heap_owners($heap_graph(S_reached), HARRAY n_array) = 1']
            checks += [('S_retired_found = $ow_seek(S_reached, 4, 32)' if name == 'retired-borrowed-receiver' else
                        'S_retired_found = $drive_steps(S_reached, 1)'),
                       r'S_retired_found.COMPLETION = NORMAL \/ S_retired_found.COMPLETION = BUDGET',
                       'S_retired = S_retired_found[.COMPLETION = NORMAL]', *valid('S_retired')]
            if name == 'retired-borrowed-receiver':
                checks += ['$ow_phase(S_retired, 4)',
                           'S_retired.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: (OB_USER_FAIL_ARGS pobinvoke_fci n_pending) :: ptask_tail*',
                           'pdestructionoperation.SOURCE = OB_USER_REFERENCE_RELEASE pobinvoke n_index n_pending',
                           r'pdestructionoperation.PENDING = eps /\ pdestructionoperation.COMPLETION = NORMAL',
                           r'pdestructionoperation.VALUE = KNOWN PNULL /\ pdestructionoperation.BASE = BASE_VALUE (KNOWN PNULL)',
                           '$eager_operation_source_guard(S_retired, pdestructionoperation)',
                           '~$eager_operation_source_guard(S_retired, pdestructionoperation[.PENDING = (n_pending)])',
                           '~$eager_operation_source_guard(S_retired, pdestructionoperation[.VALUE = KNOWN (PINT 7)])',
                           '~$eager_operation_source_guard(S_retired, pdestructionoperation[.SOURCE = OB_USER_REFERENCE_RELEASE pobinvoke[.CALL = OB_WRITE pobwrite[.TAIL = eps]] n_index n_pending])']
            else:
                checks += ['S_retired.TODO = (OB_USER_FAIL_ARGS pobinvoke_fci n_pending) :: ptask_tail*']
            checks += [
                       'pobinvoke_fci = $ob_reference_fci(pobinvoke)',
                       '$ob_user_fci_arguments(pobinvoke_fci)',
                       '~((HCELL n_cell) <- S_retired.ALLOCATIONS)',
                       '$heap_count(HCELL n_cell, $machine_roots(S_retired)) = 0',
                       '$ob_reference_metadata(S_retired, pobinvoke, n_index)',
                       '~$ob_reference_release_valid(S_retired, pobinvoke, n_index, n_pending)',
                       '$throwable_live(S_retired, n_pending)', *budget('S_retired', 'S_retired_budget')]
    checks += ['S_done = $drive_steps(S_reached, 2048)',
               r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.FRAMES = eps /\ S_done.CURRENT = eps',
               'S_done.OUTPUTBUFFERS = eps', '~$ob_user_running(S_done)',
               '$ow_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-automatic-reference-review-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    report = {'revision': sources.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': sources.common.PROFILE, 'selected': selected,
              'groups': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        groups = []
        for index, name in enumerate(selected):
            directory = out / name; directory.mkdir()
            source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
            native = sources.common.run([str(ROOT / '.tools/php/bin/php'), '-n', *sources.common.FLAGS, str(path)], directory, 'native', 10)
            assert native.returncode == 0 and native.stdout == expected and not native.stderr, (name, native.stdout, native.stderr)
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
            groups.append('\ndec $ow_group_' + str(index) + '() : bool\ndef $ow_group_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.common.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + ''.join(groups) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $ow_group_' + str(index) + '()\n' for index in range(len(groups))))
        report['fixture_sha256'] = sources.common.sha(fixture)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = sources.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                     *[str(ROOT / module) for module in modules], str(fixture)], out, 'state', 600)
        assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, (result.returncode, result.stdout, result.stderr)
        report.update(passed=True, completed=True)
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
