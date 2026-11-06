#!/usr/bin/env python3
"""The direct null-C fatal retains its one real C retval through deactivation."""
import argparse
import json
import os
import re
from pathlib import Path
import tempfile

from recorded_worker import Worker
import output_deprecation_warning_review_state as runner
import output_final_error_sources as sources
import output_object_conversion_review_sources as support

ROOT = support.ROOT
SOURCE = sources.CASES['user-dtor']
STDERR = b'Fatal error: Object of class T could not be converted to string in Unknown on line 0\nStack trace:\n#0 {main}\n'
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r'''
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.TODO = (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_tail*
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
  -- if ptask_tail* = [OUTPUT_DRAIN pobdrain]
  -- if ~$stringable_instance(S, pobobjectreturn.OBJECT)
def $dp_phase(S, n) = false -- otherwise
''' + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def fingerprint():
    inputs = support.fingerprint()
    for name in ('tests/semantics/output_final_error_sources.py',
                 'tests/semantics/output_final_error_review_state.py',
                 'tests/semantics/output_deprecation_warning_review_state.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = support.common.sha(ROOT / name)
    return inputs


def assertions(fixture, directory, path):
    bindings = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(directory)) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $dp_seek(S_initial, 0, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]',
        'S.TODO = (OB_USER_OBJECT_CAST pobobjectreturn) :: ptask_tail*',
        'pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain',
        'ptask_tail* = [OUTPUT_DRAIN pobdrain]', 'n_object = pobobjectreturn.OBJECT',
        'S_report_found = $drive_steps(S, 1)',
        'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]',
        'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
        'S_budget = $drive_steps(S_report, 0)',
        'S_pop_found = $drive_steps(S_budget[.COMPLETION = NORMAL], 1)',
        'S_pop_found.COMPLETION = BUDGET',
        'S_pop = S_pop_found[.COMPLETION = NORMAL]',
        'S_done = $drive_steps(S_pop, 2048)',
        'pdestructioncleanup_tail = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_FATAL pobobjectreturn[.TAIL = eps] pobdeactivate]',
        'pdestructioncleanup_index = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_FATAL pobobjectreturn pobdeactivate[.INDEX = 1]]',
    ]
    components = [
        ('actual user-T null-C front', r'$object_name(S, n_object) = $ptascii("T") /\ pobobjectreturn.CALLER = eps /\ pobobjectreturn.PENDING = eps /\ pobobjectreturn.RETURNED = eps /\ S.CURRENT = eps /\ S.FRAMES = eps /\ S.CONSTCONTEXT = eps /\ S.DESTRUCTION.ABANDONED = eps /\ $heap_count(HOBJECT n_object, $machine_roots(S)) = 1'),
        ('actual direct-fatal transition', r'S_report.OBJECTS = S.OBJECTS /\ S_report.ALLOCATIONS = S.ALLOCATIONS /\ S_report.OUTPUTBUFFERS = eps /\ S_report.EXITSTATUS = 255 /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("Error")) ($ptascii("Object of class T could not be converted to string")) 0 /\ pobdeactivate.BUFFERS = S.OUTPUTBUFFERS /\ pdestructioncleanup = $ob_object_final_fatal_receipt(S_report, pobobjectreturn, pobdeactivate)'),
        ('exact fatal diagnostic and noD', 'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + runner.bytes_expr(STDERR) + ']'),
        ('positive user-T receipt', '$eager_cleanup_valid(S_report, pdestructioncleanup)'),
        ('public call validity', '$call_descriptors_valid(S_report)'),
        ('public owner validity', '$heap_valid($heap_graph(S_report))'),
        ('output and destruction validity', r'$output_state_valid(S_report) /\ $destruction_state_valid(S_report)'),
        ('inert marker and one real owner', r'$task_nodes(pdestructioncleanup.SOURCE) = eps /\ ~$call_task_valid(S_report, pdestructioncleanup.SOURCE) /\ $eager_abandoned_owner(pdestructioncleanup.SOURCE) = [HOBJECT n_object] /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 1'),
        ('membership and exact-tail refusals', r'~$eager_cleanup_valid(S_report[.DESTRUCTION.ABANDONED = eps], pdestructioncleanup) /\ ~$eager_cleanup_valid(S_report[.DESTRUCTION.ABANDONED = [pdestructioncleanup_tail]], pdestructioncleanup_tail) /\ ~$eager_cleanup_valid(S_report[.DESTRUCTION.ABANDONED = [pdestructioncleanup_index]], pdestructioncleanup_index)'),
        ('class-source authority refusal', '~$eager_cleanup_valid(S_report[.DECLARATIONS = eps], pdestructioncleanup)'),
        ('projection preserves other records', '$ob_object_final_fatal_other([pdestructioncleanup, pdestructioncleanup_index], pdestructioncleanup) = [pdestructioncleanup_index]'),
        ('zero-budget preservation', r'S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_report.TODO /\ S_budget.DESTRUCTION = S_report.DESTRUCTION /\ S_budget.ALLOCATIONS = S_report.ALLOCATIONS /\ S_budget.EVENTS = S_report.EVENTS'),
        ('one-budget actual deactivate', r'S_pop.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate[.INDEX = 1]] /\ S_pop.DESTRUCTION.ABANDONED = [pdestructioncleanup] /\ $heap_count(HOBJECT n_object, $machine_roots(S_pop)) = 1 /\ ~(n_object <- S_pop.DESTRUCTION.CALLED)'),
        ('complete endpoint without destructor', r'S_done.COMPLETION = pobdeactivate.COMPLETION /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.OUTPUTBUFFERS = eps /\ S_done.EXITSTATUS = 255 /\ S_done.EVENTS = S_report.EVENTS /\ S_done.DESTRUCTION.ABANDONED = [pdestructioncleanup] /\ $heap_count(HOBJECT n_object, $machine_roots(S_done)) = 1 /\ ~(n_object <- S_done.DESTRUCTION.CALLED)'),
    ]
    return bindings, components


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-error-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': support.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': support.common.PROFILE,
              'source_case': 'user-dtor', 'passed': False, 'completed': False}
    print(out, flush=True)
    stage = 'native'
    try:
        path = out / 'source.php'; path.write_bytes(SOURCE)
        native = support.common.run([str(ROOT / '.tools/php/bin/php'), '-n', *support.common.FLAGS, str(path)], out, 'native', 10)
        assert native.returncode == 255 and native.stdout == b'P' and native.stderr == STDERR
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        try:
            parsed = frontend.request({'op': 'parse', 'source': support.base64.b64encode(SOURCE).decode()})
        finally:
            frontend.close()
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        finally:
            adapter.close()
        bindings, components = assertions(checked['fixture'], out, path)
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
                           ', '.join('(' + check + ')' for _, check in components) + ']\n' +
                           ''.join('  -- if ' + binding + '\n' for binding in bindings))
        report.update(source_sha256=support.common.sha(path), binding_premises=len(bindings),
                      native_agreement_credit=0,
                      components=[name for name, _ in components], fixture_sha256=support.common.sha(fixture))
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        stage = 'state'
        result = support.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                     *[str(ROOT / module) for module in modules], str(fixture)], out, 'state', 300)
        rendered = result.stdout.decode('ascii')
        values = re.findall(r'\b(?:true|false)\b', rendered)
        assert not re.sub(r'true|false|[\[\](),;\s]', '', rendered), rendered
        report['component_results'] = dict(zip(report['components'], [value == 'true' for value in values]))
        assert result.returncode == 0 and not result.stderr and values == ['true'] * len(components), (result.returncode, result.stdout, result.stderr)
        report.update(passed=True, completed=True)
    except BaseException as error:
        if isinstance(error, support.subprocess.TimeoutExpired):
            (out / (stage + '.stdout')).write_bytes(error.stdout or b'')
            (out / (stage + '.stderr')).write_bytes(error.stderr or b'')
            (out / (stage + '.timeout')).write_text(str(error.timeout) + '\n')
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
