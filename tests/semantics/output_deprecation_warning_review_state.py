#!/usr/bin/env python3
"""Reached scalar/pending transfer and post-route raw output owner cleanup."""
import argparse
import json
import os
from pathlib import Path
import tempfile

from recorded_worker import Worker
import output_deprecation_warning_review_sources as sources

ROOT = sources.ROOT
CASES = {
    'fresh-pending-getter': sources.CASES['warning-retval-destructor-fresh-getter-trace'],
    'post-route-owner': sources.CASES['get-flush-owner-throw-replaces-pending'],
}
PREFIX = r'''
dec $dp_output(pevent*) : preqbytes
dec $dp_is_output(pevent) : bool
def $dp_output(eps) = eps
def $dp_output((OUTPUT n*) :: pevent_tail*) = n* ++ $dp_output(pevent_tail*)
def $dp_output(pevent :: pevent_tail*) = $dp_output(pevent_tail*) -- if ~$dp_is_output(pevent)
def $dp_is_output(OUTPUT n*) = true
def $dp_is_output(pevent) = false -- otherwise
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.TODO = (OB_USER_DEPRECATED_PENDING pobinvoke pvalue n_pending) :: ptask_tail*
def $dp_phase(S, 1) = true
  -- if S.TODO = (OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_native* n_pending) :: ptask_tail*
  -- if pobrelease.CALL.KIND = INTRINSIC_OB_GET_FLUSH
def $dp_phase(S, n) = false -- otherwise
dec $dp_seek(pstate, nat, nat) : pstate
def $dp_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $dp_seek(S, n_phase, n) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $dp_phase(S, n_phase)
def $dp_seek(S, n_phase, 0) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if ~$dp_phase(S, n_phase)
def $dp_seek(S, n_phase, n) = $dp_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$dp_phase(S, n_phase) /\ $(n > 0)
'''


def bytes_expr(value):
    return '$base64(' + json.dumps(sources.base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))',
            '$output_state_valid(' + state + ')']


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.common.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    phase = 0 if name == 'fresh-pending-getter' else 1
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET',
              'S_found = $dp_seek(S_initial, ' + str(phase) + ', 1024)',
              r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
              'S_reached = S_found[.COMPLETION = NORMAL]', '$dp_phase(S_reached, ' + str(phase) + ')', *valid('S_reached')]
    if name == 'fresh-pending-getter':
        checks += [
            'S_reached.TODO = (OB_USER_DEPRECATED_PENDING pobinvoke pvalue_ret n_pending) :: ptask_native*',
            'pobinvoke.CALL = OB_API_FAILED pconfigcall pcallcontext? ptask_native*',
            'pconfigcall.KIND = INTRINSIC_OB_GET_FLUSH', 'pconfigcall.LINE = 7',
            'pobinvoke.PHASE = 9', '$ob_user_fci_arguments(pobinvoke)',
            'S_reached.CURRENT = pcallcontext?', 'S_reached.ORIGIN = (pconfigcall.SITE)',
            '$string_bytes(pvalue_ret) = ([88,65])',
            'pobinvoke.VALUE = PSTRING_CARRIER (REQUEST_STRING n_copy) ([65])',
            'pobinvoke.INPUT = PSTRING_CARRIER (REQUEST_STRING n_input) ([65])',
            'n_input = $(n_copy + 1)',
            'S_reached.OUTPUTBUFFERS = [poutputbuffer]',
            r'poutputbuffer.FLAGS = 8305 /\ poutputbuffer.BYTES = ([65,72])',
            '$ob_user_running(S_reached)', '$throwable_live(S_reached, n_pending)',
            '$task_nodes(OB_USER_DEPRECATED_PENDING pobinvoke pvalue_ret n_pending) = [HOBJECT n_pending]',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_reached)) = 1',
            'S_reached.DESTRUCTION.CLEANUPS = eps',
            'S_reached.RESULT = KNOWN PNULL', 'S_reached.BASE = BASE_VALUE (KNOWN PNULL)',
            '$lookup(S_reached.ENV, ([120])) = (n_x)',
            'S_reached.STORE[n_x] = DEFINED (PINT 99)',
            '$lookup(S_reached.ENV, ([108,111,103])) = (n_log)',
            'S_reached.STORE[n_log] = DEFINED pvalue_log',
            '$string_bytes(pvalue_log) = ([68,56,51,48,53,58,65,72])',
            '$dp_output(S_reached.EVENTS) = ([80,68])',
            '~$call_task_valid(S_reached, OB_USER_DEPRECATED_PENDING pobinvoke (POBJECT n_pending) n_pending)',
            '~$call_task_valid(S_reached, OB_USER_DEPRECATED_PENDING pobinvoke pvalue_ret 999999)',
            '~$call_task_valid(S_reached[.ORIGIN = eps], OB_USER_DEPRECATED_PENDING pobinvoke pvalue_ret n_pending)',
            'S_enabled = S_reached[.OUTPUTBUFFERS = [poutputbuffer[.FLAGS = 113]]]',
            '~$call_task_valid(S_enabled, OB_USER_DEPRECATED_PENDING pobinvoke pvalue_ret n_pending)',
            'S_produced = S_reached[.OUTPUTBUFFERS = [poutputbuffer[.FLAGS = 41073]]]',
            '~$call_task_valid(S_produced, OB_USER_DEPRECATED_PENDING pobinvoke pvalue_ret n_pending)',
            'ptask_native* =/= eps',
            'pobinvoke_bad = pobinvoke[.CALL = OB_API_FAILED pconfigcall pcallcontext? eps]',
            'S_bad_tail = S_reached[.TODO = (OB_USER_DEPRECATED_PENDING pobinvoke_bad pvalue_ret n_pending) :: ptask_native*]',
            '~$call_task_valid(S_bad_tail, OB_USER_DEPRECATED_PENDING pobinvoke_bad pvalue_ret n_pending)',
            'S_copy = $string_request(S_reached, ([65]))',
            'S_copy.RESULT = KNOWN pvalue_copy', '$string_carrier_valid(S_copy, pvalue_copy)',
            '~$call_task_valid(S_copy, OB_USER_DEPRECATED_PENDING pobinvoke[.VALUE = pvalue_copy] pvalue_ret n_pending)',
            'S_budget = $drive_steps(S_reached, 0)', 'S_budget.COMPLETION = BUDGET',
            'S_budget.TODO = S_reached.TODO', 'S_budget.OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS',
            'S_budget.ALLOCATIONS = S_reached.ALLOCATIONS', *valid('S_budget'),
            'S_routed_found = $drive_steps(S_reached, 1)',
            r'S_routed_found.COMPLETION = NORMAL \/ S_routed_found.COMPLETION = BUDGET',
            'S_routed = S_routed_found[.COMPLETION = NORMAL]', *valid('S_routed'),
            'S_routed.TODO = (OUTPUT_FAIL_WRITE pobwrite n_pending) :: ptask_native*',
            'pobwrite.CALLER = OUTPUT_API pconfigcall',
            r'pobwrite.IDS = eps /\ pobwrite.INDEX = 0 /\ pobwrite.BYTES = ([88,65])',
            'S_routed.OUTPUTBUFFERS = eps', '~$ob_user_running(S_routed)',
            '$heap_count(HOBJECT n_pending, $machine_roots(S_routed)) = 1']
    else:
        checks += [
            'S_reached.TODO = (OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_native* n_pending) :: ptask_native*',
            'pobrelease.CALL.KIND = INTRINSIC_OB_GET_FLUSH',
            '$string_bytes(pobrelease.VALUE) = ([65])',
            'pobrelease.BUFFER.HANDLER = (poutputhandler)',
            'poutputhandler.ZOH = PARRAY n_array',
            '$target_receiver(S_reached, poutputhandler.ENTRY.TARGET) = (n_receiver)',
            '$heap_count(HARRAY n_array, $machine_roots(S_reached)) = 1',
            '$heap_owners($heap_graph(S_reached), HOBJECT n_receiver) = 1',
            '$throwable_live(S_reached, n_pending)',
            'S_reached.OUTPUTBUFFERS = eps', '~$ob_user_running(S_reached)',
            '$dp_output(S_reached.EVENTS) = ([80,87,88,65])',
            '$lookup(S_reached.ENV, ([120])) = (n_x)',
            'S_reached.STORE[n_x] = DEFINED (PINT 99)',
            '~$call_task_valid(S_reached, OB_API_FAIL_RELEASE pobrelease pcallcontext? eps n_pending)',
            '~$call_task_valid(S_reached, OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_native* 999999)']
    checks += ['S_done = $drive_steps(S_reached, 2048)',
               r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
               'S_done.OUTPUTBUFFERS = eps', '$dp_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact source group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-deprecation-warning-review-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
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
            groups.append('\ndec $dp_group_' + str(index) + '() : bool\ndef $dp_group_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.common.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + ''.join(groups) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $dp_group_' + str(index) + '()\n' for index in range(len(groups))))
        report['fixture_sha256'] = sources.common.sha(fixture)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        result = sources.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                     *[str(ROOT / module) for module in modules], str(fixture)], out, 'state', 300)
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
