#!/usr/bin/env python3
"""Reached API detached restoration and popped handler ownership."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from recorded_worker import Worker
import output_api_failure_sources as sources
import output_api_failure_review_sources as review
ROOT = sources.ROOT
# The historical late-SENT argv frontier is replaced by output_result_cleanup_state.
CASES = {
    'detached-restore': sources.CASES['normal-upper-lower-throw'],
    'get-clean-release': (b'<?php $e=new Exception("E");$f=new Exception("F");$x=99;$log="";function l($b,$p){global $log;$log.="L";return "L".$b;}class C{function __invoke($b,$p){global $e;throw $e;}function __destruct(){global $f;echo "D".ob_get_level();throw $f;}}ob_start("l",1);ob_start(new C);echo "A";try{$x=ob_get_clean();}catch(Exception $c){$s=ob_get_status();echo ($c===$f?"F":"N").($c->getPrevious()===$e?"P":"N").":".$s["flags"].":".$x;}ob_end_clean();echo "|".$log."Z";', b'LD1LFP:20593:99|LLLZ'),
}
PREFIX = r"""
dec $af_output(pevent*) : preqbytes
dec $af_is_output(pevent) : bool
def $af_output(eps) = eps
def $af_output((OUTPUT n*) :: pevent_tail*) = n* ++ $af_output(pevent_tail*)
def $af_output(pevent :: pevent_tail*) = $af_output(pevent_tail*) -- if ~$af_is_output(pevent)
def $af_is_output(OUTPUT n*) = true
def $af_is_output(pevent) = false -- otherwise
dec $af_phase(pstate, nat) : bool
def $af_phase(S, 2) = true
  -- if S.TODO = (OUTPUT_FAIL_FINISH pobwrite n) :: ptask_tail*
  -- if pobwrite.FINISH = OUTPUT_USER_DONE pobinvoke poutputbuffer poboutput true
  -- if pobwrite.CALLER = OUTPUT_API pconfigcall
  -- if pconfigcall.KIND = INTRINSIC_OB_FLUSH
def $af_phase(S, 3) = true -- if S.TODO = (OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_native* n) :: ptask_tail*
def $af_phase(S, 4) = true
  -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
  -- if pdestructionoperation.SOURCE = OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_native* n
  -- if S.CURRENT = (pcallcontext_current)
  -- if $destructor_context_call(pcallcontext_current, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OPERATION = (pdestructionoperation)
def $af_phase(S, 5) = true
  -- if S.TODO = (OB_USER_ENTER pobinvoke) :: ptask_tail*
  -- if pobinvoke.CALL = OB_WRITE pobwrite
  -- if $output_vm_source(pobwrite.CALLER)
  -- if S.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*
  -- if pdestructionoperation.SOURCE = OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_native* n
def $af_phase(S, n) = false -- otherwise
dec $af_seek(pstate, nat, nat) : pstate
def $af_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $af_seek(S, n_phase, n) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $af_phase(S, n_phase)
def $af_seek(S, n_phase, 0) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if ~$af_phase(S, n_phase)
def $af_seek(S, n_phase, n) = $af_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$af_phase(S, n_phase) /\ $(n > 0)
"""


def bytes_expr(value):
    return '$base64(' + json.dumps(sources.base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))', '$output_state_valid(' + state + ')']


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_api_failure_state.py', 'tests/semantics/output_api_failure_review_sources.py', 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    phase = {'detached-restore': 2, 'get-clean-release': 3}[name]
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET', *valid('S_initial'),
              'S_found = $af_seek(S_initial, ' + str(phase) + ', 512)',
              r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
              'S_reached = S_found[.COMPLETION = NORMAL]', '$af_phase(S_reached, ' + str(phase) + ')', *valid('S_reached'),
              'S_budget = $drive_steps(S_reached, 0)', 'S_budget.COMPLETION = BUDGET',
              r'S_budget.TODO = S_reached.TODO /\ S_budget.OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS', *valid('S_budget')]
    if name == 'detached-restore':
        checks += ['S_reached.TODO = (OUTPUT_FAIL_FINISH pobwrite n_pending) :: ptask_tail*',
                   'pobwrite.CALLER = OUTPUT_API pconfigcall',
                   'pobwrite.FINISH = OUTPUT_USER_DONE pobinvoke poutputbuffer poboutput true',
                   'pobinvoke.CALL = OB_API pconfigcall', 'pobwrite.TAIL = ptask_tail*',
                   'pobwrite.IDS = ([0])', 'S_reached.OUTPUTBUFFERS = [poutputbuffer_lower]',
                   r'poutputbuffer_lower.FLAGS = 12401 /\ poutputbuffer_lower.BYTES = eps',
                   '$output_restore_active(S_reached) = ($ob_user_committed(poutputbuffer, poboutput))',
                   '$output_getter_buffers(S_reached) = ($ob_user_committed(poutputbuffer, poboutput)) :: S_reached.OUTPUTBUFFERS',
                   '$throwable_live(S_reached, n_pending)', '~$ob_user_running(S_reached)',
                   '~$call_task_valid(S_reached, OUTPUT_FAIL_FINISH pobwrite[.TAIL = eps] n_pending)',
                   '~$call_task_valid(S_reached, OUTPUT_FAIL_FINISH pobwrite[.IDS = ([999])] n_pending)',
                   '~$call_task_valid(S_reached, OUTPUT_FAIL_FINISH pobwrite[.CALLER = OUTPUT_VM (PORIGIN 999 eps) (EMIT 1) 1] n_pending)',
                   '~$output_finish_valid(S_reached, pobwrite[.FINISH = OUTPUT_API_FAILED pobinvoke poutputbuffer OB_API_RETAIN])',
                   'S_next_found = $drive_steps(S_reached, 1)',
                   'S_next = S_next_found[.COMPLETION = NORMAL]', *valid('S_next'),
                   'S_next.OUTPUTBUFFERS = [poutputbuffer_normal, poutputbuffer_lower]',
                   r'poutputbuffer_normal.FLAGS = 20593 /\ poutputbuffer_normal.BYTES = eps',
                   'S_next.TODO = (THROW_SEARCH n_pending) :: ptask_tail*']
    else:
        checks += ['S_reached.TODO = (OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_tail* n_pending) :: ptask_tail*',
                   'pobrelease.CALL.KIND = INTRINSIC_OB_GET_CLEAN',
                   '$string_bytes(pobrelease.VALUE) = ([65])',
                   'pobrelease.BUFFER.HANDLER = (poutputhandler)',
                   'poutputhandler.ZOH = POBJECT n_receiver',
                   'S_reached.OUTPUTBUFFERS = [poutputbuffer_lower]',
                   r'poutputbuffer_lower.ID = 0 /\ poutputbuffer_lower.FLAGS = 113 /\ poutputbuffer_lower.BYTES = eps',
                   '~$ob_user_running(S_reached)',
                   '$heap_owners($heap_graph(S_reached), HOBJECT n_receiver) = 1',
                   '$throwable_live(S_reached, n_pending)',
                   '~$call_task_valid(S_reached, OB_API_FAIL_RELEASE pobrelease pcallcontext? eps n_pending)',
                   '~$call_task_valid(S_reached[.ORIGIN = eps], OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_tail* n_pending)',
                   'S_forged_string = $string_request(S_reached, ([66]))',
                   'S_forged_string.RESULT = KNOWN pvalue_forged',
                   '$string_carrier_valid(S_forged_string, pvalue_forged)',
                   '~$call_task_valid(S_forged_string, OB_API_FAIL_RELEASE pobrelease[.VALUE = pvalue_forged] pcallcontext? ptask_tail* n_pending)',
                   'S_child_found = $af_seek(S_reached, 4, 512)',
                   r'S_child_found.COMPLETION = NORMAL \/ S_child_found.COMPLETION = BUDGET',
                   'S_child = S_child_found[.COMPLETION = NORMAL]', '$af_phase(S_child, 4)', *valid('S_child'),
                   'S_child.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
                   'pdestructionoperation.SOURCE = OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_tail* n_pending',
                   r'pdestructionoperation.COMPLETION = THROWING n_pending /\ pdestructionoperation.PENDING = (n_pending)',
                   '$eager_operation_source_guard(S_child, pdestructionoperation)',
                   '$ob_api_release_exit(S_child, pdestructionoperation, pobrelease, pcallcontext?, ptask_tail*)',
                   '~$call_task_valid(S_child, OB_API_FAIL_RELEASE pobrelease pcallcontext? ptask_tail* n_pending)',
                   '~$eager_operation_source_guard(S_child, pdestructionoperation[.SOURCE = OB_API_FAIL_RELEASE pobrelease pcallcontext? eps n_pending])',
                   '~$eager_operation_source_guard(S_child, pdestructionoperation[.PENDING = eps])',
                   'S_lower_found = $af_seek(S_child, 5, 512)',
                   r'S_lower_found.COMPLETION = NORMAL \/ S_lower_found.COMPLETION = BUDGET',
                   'S_lower = S_lower_found[.COMPLETION = NORMAL]', '$af_phase(S_lower, 5)', *valid('S_lower'),
                   'S_lower.TODO = (OB_USER_ENTER pobinvoke_lower) :: ptask_lower_tail*',
                   r'pobinvoke_lower.BUFFER.ID = 0 /\ pobinvoke_lower.BUFFER.BYTES = ([68,49])',
                   '$call_task_valid(S_lower, OB_USER_ENTER pobinvoke_lower)',
                   '$ob_user_running(S_lower)',
                   'S_lower.DESTRUCTION.OPERATIONS = pdestructionoperation :: pdestructionoperation_tail*',
                   'pdestructionoperation.PENDING = (n_pending)']
    if name != 'detached-restore':
        checks += ['S_child.CURRENT = (pcallcontext_destructor)',
                   '$destructor_context_call(pcallcontext_destructor, S_child.CURRENT, S_child.FRAMES) = (pdestructorcall)',
                   'pdestructorcall.USER',
                   r'pcallcontext_destructor.CALLSITE = eps /\ pcallcontext_destructor.LINE = $(-1)',
                   '$destructor_context_valid(S_child, pcallcontext_destructor)',
                   '$ob_api_failure_source_call(pdestructionoperation.SOURCE) = (pconfigcall_destructor)',
                   '~$destructor_context_valid(S_child[.CURRENT = (pcallcontext_destructor[.CALLSITE = (pconfigcall_destructor.SITE)])], pcallcontext_destructor[.CALLSITE = (pconfigcall_destructor.SITE)])',
                   '$eval_exception_trace_raw(S_child) = [ptraceframe_destructor, ptraceframe_api]',
                   r'ptraceframe_destructor.FILE = eps /\ ptraceframe_destructor.LINE = $(-1)',
                   r'ptraceframe_api.FILE = $call_sourcefile(S_child.FILES, pconfigcall_destructor.SITE) /\ ptraceframe_api.LINE = pconfigcall_destructor.LINE /\ ptraceframe_api.FUNCTION = $intrinsic_name(pconfigcall_destructor.KIND)',
                   'S_child_budget = $drive_steps(S_child, 0)',
                   'S_child_budget.COMPLETION = BUDGET',
                   r'S_child_budget.TODO = S_child.TODO /\ S_child_budget.DESTRUCTION.OPERATIONS = S_child.DESTRUCTION.OPERATIONS',
                   *valid('S_child_budget')]
    checks += ['S_done = $drive_steps(S_reached, 1024)',
               r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
               'S_done.OUTPUTBUFFERS = eps', '$af_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-api-failure-state-', dir=ROOT / '.tools'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': sources.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': sources.PROFILE,
              'selected': selected, 'groups': [], 'passed': False, 'completed': False}
    bodies = []
    print(out, flush=True)
    try:
        for index, name in enumerate(selected):
            directory = out / name; directory.mkdir()
            source, expected = CASES[name]; path = directory / 'source.php'; path.write_bytes(source)
            native = sources.run([str(ROOT / '.tools/php/bin/php'), '-n', *sources.FLAGS, str(path)], directory, 'native', 10)
            if expected is not None:
                assert native.returncode == 0 and native.stdout == expected and not native.stderr, (name, native.stdout, expected, native.stderr)
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
            bodies.append('dec $af_case_' + str(index) + '() : bool\ndef $af_case_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\n'.join(bodies) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $af_case_' + str(index) + '()\n' for index in range(len(bodies))))
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
        report['after'] = fingerprint()
        report['passed'] = report['passed'] and report['before'] == report['after']
        report['runner_sha256'] = sources.sha(ROOT / 'tests/semantics/_build/default/numeric_runner.exe')
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)
    assert report['passed'] and report['completed']


if __name__ == '__main__':
    main()
