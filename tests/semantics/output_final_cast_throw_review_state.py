#!/usr/bin/env python3
"""A direct FINAL throw abandons its real retval and cast guard before reporting."""
import argparse
import json
import os
import re
from pathlib import Path
import tempfile

from recorded_worker import Worker
import output_deprecation_warning_review_state as runner
import output_final_cast_throw_sources as sources
import output_object_conversion_review_sources as support

ROOT = support.ROOT
SOURCE = sources.CASES['fresh-exception-retained-object']
PREFIX = runner.PREFIX.split('dec $dp_phase', 1)[0] + r"""
dec $dp_phase(pstate, nat) : bool
def $dp_phase(S, 0) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
  -- if pobobjectreturn.INVOKE.CALL = OB_FINAL pobdrain
def $dp_phase(S, 1) = true
  -- if S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]
  -- if pobdeactivate.INDEX = 0
def $dp_phase(S, n) = false -- otherwise
""" + 'dec $dp_seek' + runner.PREFIX.split('dec $dp_seek', 1)[1]


def expected_stderr(path):
    name = os.fsencode(path)
    return (b'Fatal error: Uncaught Exception: E in ' + name + b':1\nStack trace:\n'
            b'#0 [internal function]: T->__toString()\n#1 {main}\n  thrown in ' + name + b' on line 1\n')


def fingerprint():
    inputs = support.fingerprint()
    for name in ('tests/semantics/output_final_cast_throw_sources.py',
                 'tests/semantics/output_final_cast_throw_review_state.py',
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
        'S.TODO = (THROW_VALUE porigin z) :: ptask_tail*',
        'S.CURRENT = (pcallcontext)', 'S.FRAMES = [pframe]',
        'pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*',
        'S.RESULT = KNOWN (POBJECT n_exception)',
        '$trace_context(S, S.ENV, S.CURRENT) = [ptraceframe]',
        'S_report_found = $drive_steps(S, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
        'S_budget = $drive_steps(S_report, 0)',
        'S_release_found = $drive_steps(S_budget[.COMPLETION = NORMAL], 1)',
        'S_release_found.COMPLETION = BUDGET',
        'S_release = S_release_found[.COMPLETION = NORMAL]',
        'S_release.DESTRUCTION.OPERATIONS = [pdestructionoperation]',
        'S_deactivate_found = $dp_seek(S_release, 1, 512)',
        r'S_deactivate_found.COMPLETION = NORMAL \/ S_deactivate_found.COMPLETION = BUDGET',
        'S_deactivate = S_deactivate_found[.COMPLETION = NORMAL]',
        'S_deactivate.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]',
        'S_done = $drive_steps(S_deactivate, 2048)',
        'pdestructioncleanup_tail = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn[.TAIL = eps] pobdeactivate porigin n_exception]',
        'pdestructioncleanup_birth = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn pobdeactivate porigin n_object]',
        'pcallcontext_bad = pcallcontext[.CALLSITE = (porigin_site)][.LINE = 0]',
    ]
    components = [
        ('real direct native method throw', r'$ob_object_final_throw_ready(S, pobobjectreturn, porigin, n_exception) /\ n_object = pobobjectreturn.OBJECT /\ $object_name(S, n_object) = $ptascii("T") /\ $heap_count(HOBJECT n_object, $machine_roots(S)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S)) = 1'),
        ('internal method trace', r'ptraceframe.FILE = eps /\ ptraceframe.LINE = $(-1) /\ ptraceframe.FUNCTION = $ptascii("__toString") /\ ptraceframe.CLASS = ($ptascii("T")) /\ ptraceframe.TYPE = ($ptascii("->")) /\ ptraceframe.ARGS = eps /\ ptraceframe.HASARGS'),
        ('actual handoff without decrement', r'S_report.OBJECTS = S.OBJECTS /\ S_report.ALLOCATIONS = S.ALLOCATIONS /\ S_report.GC = S.GC /\ S_report.CURRENT = eps /\ S_report.FRAMES = eps /\ S_report.OUTPUTBUFFERS = S.OUTPUTBUFFERS /\ S_report.EXITSTATUS = 255'),
        ('exact frozen fatal without destructor', 'S_report.EVENTS = [OUTPUT ([80]), STDERR ' + runner.bytes_expr(expected_stderr(path)) + r'] /\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("Exception")) ($ptascii("E")) 1'),
        ('inert source and real receiver pair', r'$task_nodes(pdestructioncleanup.SOURCE) = eps /\ ~$call_task_valid(S_report, pdestructioncleanup.SOURCE) /\ $eager_abandoned_owner(pdestructioncleanup.SOURCE) = [HOBJECT n_object, HOBJECT n_object] /\ $heap_count(HOBJECT n_object, $machine_roots(S_report)) = 2 /\ $heap_count(HOBJECT n_exception, $machine_roots(S_report)) = 1'),
        ('positive receipt and pending owner', r'$eager_cleanup_valid(S_report, pdestructioncleanup) /\ $call_task_valid(S_report, OUTPUT_FINAL_PENDING pobdeactivate n_exception true)'),
        ('public report validity', r'$call_descriptors_valid(S_report) /\ $heap_valid($heap_graph(S_report)) /\ $output_state_valid(S_report) /\ $destruction_state_valid(S_report)'),
        ('native-frame and nested-frame refusals', r'~$ob_object_final_throw_ready(S[.CURRENT = (pcallcontext_bad)], pobobjectreturn, porigin, n_exception) /\ ~$ob_object_final_throw_ready(S[.FRAMES = [pframe, pframe]], pobobjectreturn, porigin, n_exception)'),
        ('control and extra-owner refusals', r'~$ob_object_final_throw_ready(S[.TODO = (THROW_VALUE porigin z) :: (TRY_END porigin) :: ptask_tail*], pobobjectreturn, porigin, n_exception) /\ ~$ob_object_final_throw_ready(S[.HELD = [HOBJECT n_object]], pobobjectreturn, porigin, n_exception) /\ ~$ob_object_final_throw_ready(S[.EXCEPTIONHANDLER = (PSTRING $ptascii("h"))], pobobjectreturn, porigin, n_exception)'),
        ('membership tail and birth refusals', r'~$eager_cleanup_valid(S_report[.DESTRUCTION.ABANDONED = eps], pdestructioncleanup) /\ ~$eager_cleanup_valid(S_report[.DESTRUCTION.ABANDONED = [pdestructioncleanup_tail]], pdestructioncleanup_tail) /\ ~$eager_cleanup_valid(S_report[.DESTRUCTION.ABANDONED = [pdestructioncleanup_birth]], pdestructioncleanup_birth)'),
        ('zero-budget preserves owners', r'S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_report.TODO /\ S_budget.DESTRUCTION = S_report.DESTRUCTION /\ S_budget.ALLOCATIONS = S_report.ALLOCATIONS /\ S_budget.GC = S_report.GC /\ S_budget.EVENTS = S_report.EVENTS'),
        ('one-budget starts ordinary release', r'pdestructionoperation.SOURCE = OUTPUT_FINAL_PENDING pobdeactivate n_exception true /\ $heap_count(HOBJECT n_object, $machine_roots(S_release)) = 2 /\ S_release.OUTPUTBUFFERS = S_report.OUTPUTBUFFERS'),
        ('released Exception leaves the pair', r'~((HOBJECT n_exception) <- S_deactivate.ALLOCATIONS) /\ $eager_cleanup_valid(S_deactivate, pdestructioncleanup) /\ S_deactivate.DESTRUCTION.ABANDONED = [pdestructioncleanup] /\ $heap_count(HOBJECT n_object, $machine_roots(S_deactivate)) = 2 /\ S_deactivate.EVENTS = S_report.EVENTS /\ S_deactivate.OUTPUTBUFFERS = eps'),
        ('complete inactive endpoint', r'S_done.COMPLETION = pobdeactivate.COMPLETION /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.OUTPUTBUFFERS = eps /\ S_done.EXITSTATUS = 255 /\ S_done.EVENTS = S_report.EVENTS /\ S_done.DESTRUCTION.ABANDONED = [pdestructioncleanup] /\ $heap_count(HOBJECT n_object, $machine_roots(S_done)) = 2 /\ ~((HOBJECT n_exception) <- S_done.ALLOCATIONS) /\ $eager_cleanup_valid(S_done, pdestructioncleanup)'),
    ]
    return bindings, components


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-final-cast-throw-review-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': support.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': support.common.PROFILE,
              'source_case': 'fresh-exception-retained-object', 'passed': False, 'completed': False}
    print(out, flush=True)
    stage = 'native'
    try:
        path = out / 'source.php'; path.write_bytes(SOURCE)
        native = support.common.run([str(ROOT / '.tools/php/bin/php'), '-n', *support.common.FLAGS, str(path)], out, 'native', 10)
        assert native.returncode == 255 and native.stdout == b'P' and native.stderr == expected_stderr(path)
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
