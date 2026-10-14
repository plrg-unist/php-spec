#!/usr/bin/env python3
"""Genuine prepared-reference release before an output callback enters."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from recorded_worker import Worker
import output_reference_warning_sources as sources
import output_reference_warning_review_sources as review

ROOT = sources.ROOT
CASES = {name: review.CASES['second-reference-warning-trace'] for name in ('live-prefix', 'retired-prefix')}
PREFIX = r"""
dec $rw_output(pevent*) : preqbytes
dec $rw_is_output(pevent) : bool
def $rw_output(eps) = eps
def $rw_output((OUTPUT n*) :: pevent_tail*) = n* ++ $rw_output(pevent_tail*)
def $rw_output(pevent :: pevent_tail*) = $rw_output(pevent_tail*) -- if ~$rw_is_output(pevent)
def $rw_is_output(OUTPUT n*) = true
def $rw_is_output(pevent) = false -- otherwise
dec $rw_phase(pstate, nat) : bool
def $rw_phase(S, 0) = true
  -- if S.TODO = (OB_USER_REFERENCE_RELEASE pobinvoke 1 n) :: ptask_tail*
def $rw_phase(S, n) = false -- otherwise
dec $rw_seek(pstate, nat, nat) : pstate
def $rw_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $rw_seek(S, n_phase, n) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $rw_phase(S, n_phase)
def $rw_seek(S, n_phase, 0) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if ~$rw_phase(S, n_phase)
def $rw_seek(S, n_phase, n) = $rw_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$rw_phase(S, n_phase) /\ $(n > 0)
"""


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
    for name in ('tests/semantics/output_reference_warning_state.py',
                 'tests/semantics/output_reference_warning_review_sources.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.common.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    checks = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET', *valid('S_initial'),
        'S_found = $rw_seek(S_initial, 0, 256)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_reached = S_found[.COMPLETION = NORMAL]', '$rw_phase(S_reached, 0)', *valid('S_reached'),
        'S_reached.TODO = (OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending) :: ptask_native*',
        'pobinvoke.CALL = OB_API_FAILED pconfigcall pcallcontext? ptask_native*',
        'pconfigcall.KIND = INTRINSIC_OB_GET_FLUSH',
        'pobinvoke.SENT = [REFERENCE n_cell]']
    if name == 'live-prefix':
        return checks + budget('S_reached', 'S_budget') + [
        'S_reached.STORE[n_cell] = DEFINED pobinvoke.INPUT',
        '$string_bytes(pobinvoke.INPUT) = ([65])',
        '$heap_owners($heap_graph(S_reached), HCELL n_cell) = 1',
        '$call_reference_operand_valid(S_reached, REFERENCE n_cell)',
        '$ob_reference_prefix(S_reached, pobinvoke, pobinvoke.SENT, 0)',
        '$throwable_live(S_reached, n_pending)',
        '$ob_user_running(S_reached)',
        'S_reached.CURRENT = pcallcontext?', 'S_reached.ORIGIN = (pconfigcall.SITE)',
        'S_reached.OUTPUTBUFFERS = [poutputbuffer]',
        r'poutputbuffer.FLAGS = 113 /\ poutputbuffer.BYTES = ([65])',
        '$lookup(S_reached.ENV, ([104,105,116,115])) = (n_hits)',
        'S_reached.STORE[n_hits] = DEFINED (PINT 0)',
        '$lookup(S_reached.ENV, ([119,97,114,110,105,110,103,115])) = (n_warnings)',
        'S_reached.STORE[n_warnings] = DEFINED (PINT 2)',
        '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke 0 n_pending)',
        '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke 2 n_pending)',
        '~$ob_reference_shape(S_reached, pobinvoke, [REFERENCE n_cell, REFERENCE n_cell, KNOWN (PINT pobinvoke.PHASE)], 0)',
        '~$ob_reference_prefix(S_reached, pobinvoke, [REFERENCE n_cell, KNOWN (PINT pobinvoke.PHASE), KNOWN (PINT pobinvoke.PHASE)], 0)',
        '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke 1 999999)',
        '~$call_task_valid(S_reached[.ORIGIN = eps], OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending)',
        '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke[.CALL = OB_API pconfigcall] 1 n_pending)',
        '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke[.CALL = OB_API_FAILED pconfigcall pcallcontext? eps] 1 n_pending)',
        '~$call_task_valid(S_reached, OB_USER_REFERENCE_RELEASE pobinvoke[.BUFFER.ID = 999999] 1 n_pending)',
        'S_extra_owner = S_reached[.RESULT = REFERENCE n_cell]',
        '$heap_owners($heap_graph(S_extra_owner), HCELL n_cell) = 2',
        '~$call_task_valid(S_extra_owner, OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending)',
        'S_wrong_value = S_reached[.STORE[n_cell] = DEFINED (POBJECT n_pending)]',
        '$call_reference_operand_valid(S_wrong_value, REFERENCE n_cell)',
        '~$ob_reference_prefix(S_wrong_value, pobinvoke, pobinvoke.SENT, 0)',
        '~$call_task_valid(S_wrong_value, OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending)',
        'S_forged_string = $string_request(S_reached, ([66]))',
        'S_forged_string.RESULT = KNOWN pvalue_forged',
        '$string_carrier_valid(S_forged_string, pvalue_forged)',
        '~$call_task_valid(S_forged_string, OB_USER_REFERENCE_RELEASE pobinvoke[.INPUT = pvalue_forged] 1 n_pending)']
    return checks + [
        'S_retired_found = $drive_steps(S_reached, 1)',
        r'S_retired_found.COMPLETION = NORMAL \/ S_retired_found.COMPLETION = BUDGET',
        'S_retired = S_retired_found[.COMPLETION = NORMAL]', *valid('S_retired'),
        'S_retired.TODO = (OB_USER_FAIL_ARGS pobinvoke_fci n_pending) :: ptask_native*',
        'pobinvoke_fci = $ob_reference_fci(pobinvoke)', '$ob_user_fci_arguments(pobinvoke_fci)',
        'S_retired.DESTRUCTION.OPERATIONS = S_reached.DESTRUCTION.OPERATIONS',
        '$ob_reference_metadata(S_retired, pobinvoke, 1)',
        '~((HCELL n_cell) <- S_retired.ALLOCATIONS)',
        '$heap_owners($heap_graph(S_retired), HCELL n_cell) = 0',
        '$ob_user_running(S_retired)',
        '$throwable_live(S_retired, n_pending)',
        '~$call_task_valid(S_retired, OB_USER_REFERENCE_RELEASE pobinvoke 1 n_pending)',
        '~$ob_reference_metadata(S_retired, pobinvoke, 0)',
        '~$ob_reference_metadata(S_retired, pobinvoke[.CALL = OB_API_FAILED pconfigcall pcallcontext? eps], 1)',
        '~$ob_reference_metadata(S_retired[.ORIGIN = eps], pobinvoke, 1)',
        *budget('S_retired', 'S_retired_budget'),
        'S_done = $drive_steps(S_retired, 512)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        'S_done.OUTPUTBUFFERS = eps', '$rw_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]),
        *valid('S_done')]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', choices=list(CASES), required=True)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-reference-warning-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    name = args.select
    report = {'revision': sources.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': sources.common.PROFILE, 'selected': [name],
              'groups': [], 'passed': False, 'completed': False}
    print(out, flush=True)
    try:
        directory = out / name; directory.mkdir()
        source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
        native = sources.common.run([str(ROOT / '.tools/php/bin/php'), '-n', *sources.common.FLAGS, str(path)], directory, 'native', 10)
        assert native.returncode == 0 and native.stdout == expected and not native.stderr, (native.stdout, native.stderr)
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
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.common.sha(path)})
        report['fixture_sha256'] = sources.common.sha(fixture)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = sources.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                     *[str(ROOT / module) for module in modules], str(fixture)], out, 'state', 120)
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
