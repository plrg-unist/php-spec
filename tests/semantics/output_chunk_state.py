#!/usr/bin/env python3
"""Reached automatic-write caller, active/lower, restoration and ownership fronts."""
import argparse
import json
import os
from pathlib import Path
import tempfile
from recorded_worker import Worker
import output_chunk_sources as sources
import output_chunk_review_sources as review
ROOT = sources.ROOT
CASES = {
    'vm-strict-print': (b'<?php declare(strict_types=1);function h(string $b,int $p){return $b;}ob_start("h",1);$n=print "A";ob_end_clean();echo "|".$n;', b'A|1'),
    'lower-active': review.CASES['lower-user-active-upper-default'],
    'detached-flush': (review.CASES['flush-detached-active-getters'][0].replace(
        b'<?php ', b'<?php ob_start();ob_end_clean(); ', 1),
        review.CASES['flush-detached-active-getters'][1]),
    'popped-owner': review.CASES['api-cascade-weak-owned-pop'],
    'retained-upper': review.CASES['busy-upper-user-next-write'],
}
PREFIX = r"""
dec $oc_output(pevent*) : preqbytes
dec $oc_is_output(pevent) : bool
def $oc_output(eps) = eps
def $oc_output((OUTPUT n*) :: pevent_tail*) = n* ++ $oc_output(pevent_tail*)
def $oc_output(pevent :: pevent_tail*) = $oc_output(pevent_tail*) -- if ~$oc_is_output(pevent)
def $oc_is_output(OUTPUT n*) = true
def $oc_is_output(pevent) = false -- otherwise
dec $oc_phase(pstate, nat) : bool
def $oc_phase(S, 0) = true
  -- if S.TODO = (OB_USER_ENTER pobinvoke) :: ptask_tail*
  -- if pobinvoke.CALL = OB_WRITE pobwrite
  -- if pobwrite.CALLER = OUTPUT_VM porigin (PRINT_EMIT porigin z) z
  -- if pobinvoke.PHASE = 1
def $oc_phase(S, 1) = true
  -- if S.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]
  -- if poutputbuffer_upper.ID = 1 /\ poutputbuffer_upper.BYTES = ([72])
  -- if poutputbuffer_upper.HANDLER = eps
  -- if S.CURRENT = (pcallcontext)
  -- if $ob_user_context(pcallcontext, S.CURRENT, S.FRAMES) = (pobinvoke)
  -- if pobinvoke.CALL = OB_WRITE pobwrite
  -- if pobinvoke.BUFFER.ID = 0
  -- if $ob_user_running(S)
def $oc_phase(S, 2) = true
  -- if S.TODO = (OB_USER_SEND pobinvoke 0) :: ptask_tail*
  -- if pobinvoke.CALL = OB_WRITE pobwrite
  -- if pobwrite.FINISH = OUTPUT_DEFAULT_DONE pconfigcall poutputbuffer pvalue true
  -- if pobinvoke.PHASE = 1
def $oc_phase(S, 3) = true
  -- if S.TODO = (OB_USER_SEND pobinvoke 0) :: ptask_tail*
  -- if pobinvoke.CALL = OB_WRITE pobwrite
  -- if pobwrite.FINISH = OUTPUT_USER_DONE pobinvoke_upper poutputbuffer poboutput false
  -- if pobinvoke.PHASE = 1
def $oc_phase(S, 4) = true
  -- if S.TODO = (AT porigin (STMT (NStmtEcho (SEQUENCE ([NScalarString (BYTES "Qg==") metadata_string])) metadata_echo))) :: ptask_tail*
  -- if S.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]
  -- if poutputbuffer_upper.ID = 1 /\ poutputbuffer_upper.BYTES = ([72])
  -- if poutputbuffer_upper.FLAGS = 53361
  -- if ~$ob_user_running(S)
def $oc_phase(S, n) = false -- otherwise
dec $oc_seek(pstate, nat, nat) : pstate
def $oc_seek(S, n_phase, n) = S -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $oc_seek(S, n_phase, n) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if $oc_phase(S, n_phase)
def $oc_seek(S, n_phase, 0) = S -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET -- if ~$oc_phase(S, n_phase)
def $oc_seek(S, n_phase, n) = $oc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$oc_phase(S, n_phase) /\ $(n > 0)
"""


def bytes_expr(value):
    return '$base64(' + json.dumps(sources.base64.b64encode(value).decode()) + ')'


def valid(state):
    return ['$call_descriptors_valid(' + state + ')', '$heap_valid($heap_graph(' + state + '))', '$output_state_valid(' + state + ')']


def fingerprint():
    inputs = sources.fingerprint()
    for name in ('tests/semantics/output_chunk_state.py',
                 'tests/semantics/output_chunk_review_sources.py',
                 'tests/semantics/_build/default/numeric_runner.exe'):
        inputs[name] = sources.sha(ROOT / name)
    return inputs


def assertions(name, fixture, directory, path):
    phase = list(CASES).index(name)
    checks = ['S_initial = $php_file_run(' + fixture + ', 0, ' + bytes_expr(os.fsencode(path)) + ', ' + bytes_expr(os.fsencode(directory)) + ')',
              'S_initial.COMPLETION = BUDGET', *valid('S_initial'),
              'S_found = $oc_seek(S_initial, ' + str(phase) + ', 1024)',
              r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
              'S_reached = S_found[.COMPLETION = NORMAL]', '$oc_phase(S_reached, ' + str(phase) + ')', *valid('S_reached'),
              'S_budget = $drive_steps(S_reached, 0)', 'S_budget.COMPLETION = BUDGET',
              r'S_budget.TODO = S_reached.TODO /\ S_budget.OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS', *valid('S_budget')]
    if name in ('vm-strict-print', 'detached-flush', 'popped-owner'):
        task = 'OB_USER_ENTER' if name == 'vm-strict-print' else 'OB_USER_SEND'
        suffix = '' if name == 'vm-strict-print' else ' 0'
        checks += ['S_reached.TODO = (' + task + ' pobinvoke' + suffix + ') :: ptask_tail*',
                   'pobinvoke.CALL = OB_WRITE pobwrite', '$output_write_valid(S_reached, pobwrite)',
                   'pobwrite.TAIL = ptask_tail*', '$output_selected(S_reached, pobinvoke) = (poutputbuffer_selected)',
                   'poutputbuffer_selected.ID = pobinvoke.BUFFER.ID',
                   'pobwrite.TAIL =/= eps',
                   '~$output_write_valid(S_reached, pobwrite[.TAIL = eps])',
                   '~$ob_user_invoke_valid(S_reached, pobinvoke[.CALL = OB_WRITE pobwrite[.TAIL = eps]])',
                   '~$output_write_valid(S_reached, pobwrite[.INDEX = $(|pobwrite.IDS| + 1)])',
                   '~$output_write_valid(S_reached, pobwrite[.IDS = ([999])])',
                   '~$ob_user_invoke_valid(S_reached, pobinvoke[.CALL = OB_WRITE pobwrite[.CALLER = OUTPUT_VM (PORIGIN 999 eps) (EMIT 1) 1]])']
    if name == 'vm-strict-print':
        checks += ['pobwrite.CALLER = OUTPUT_VM porigin (PRINT_EMIT porigin z) z',
                   r'pobwrite.IDS = ([0]) /\ pobwrite.INDEX = 0', 'pobwrite.BYTES = ([65])',
                   '~$output_write_valid(S_reached, pobwrite[.BYTES = ([66])])',
                   '~$ob_user_invoke_valid(S_reached, pobinvoke[.CALL = OB_WRITE pobwrite[.CALLER = OUTPUT_VM porigin (PRINT_EMIT porigin $(z + 1)) $(z + 1)]])',
                   'S_entered_found = $drive_steps(S_reached, 1)', 'S_entered = S_entered_found[.COMPLETION = NORMAL]',
                   'S_entered.CURRENT = (pcallcontext)', '$ob_user_context_valid(S_entered, pcallcontext)',
                   '$output_write_context(S_entered, pobwrite)',
                   '~$output_write_context(S_entered, pobwrite[.CONTEXT = S_entered.CURRENT])',
                   r'pcallcontext.CALLSITE = (porigin) /\ pcallcontext.LINE = z', '$typed_caller_strict(S_entered)', *valid('S_entered')]
    if name == 'lower-active':
        checks += ['S_reached.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
                   'S_reached.CURRENT = (pcallcontext)', '$ob_user_context(pcallcontext, S_reached.CURRENT, S_reached.FRAMES) = (pobinvoke)',
                   'pobinvoke.CALL = OB_WRITE pobwrite', '$output_selected(S_reached, pobinvoke) = (poutputbuffer_lower)',
                   r'pobwrite.IDS = ([1,0]) /\ pobwrite.INDEX = 1', '$output_write_valid(S_reached, pobwrite)',
                   r'poutputbuffer_upper.FLAGS = 53360 /\ poutputbuffer_lower.FLAGS = 113',
                   '$long_and(poutputbuffer_lower.FLAGS, 32768) = 0', '$output_restore_active(S_reached) = eps',
                   '$output_getter_buffers(S_reached) = S_reached.OUTPUTBUFFERS']
    if name == 'detached-flush':
        checks += ['pobwrite.FINISH = OUTPUT_DEFAULT_DONE pconfigcall poutputbuffer_saved pvalue true',
                   r'poutputbuffer_saved.ID = 2 /\ poutputbuffer_saved.BYTES = ([65])',
                   r'pobwrite.IDS = ([1]) /\ |S_reached.OUTPUTBUFFERS| = 1',
                   '$output_restore_active(S_reached) = (poutputbuffer_active)',
                   r'poutputbuffer_active.ID = 2 /\ poutputbuffer_active.BYTES = eps /\ poutputbuffer_active.FLAGS = 20592',
                   '$output_getter_buffers(S_reached) = poutputbuffer_active :: S_reached.OUTPUTBUFFERS',
                   '~$ob_user_present(S_reached.OUTPUTBUFFERS, 0)',
                   '~$output_finish_valid(S_reached, pobwrite[.FINISH = OUTPUT_DEFAULT_DONE pconfigcall poutputbuffer_saved[.ID = 0] pvalue true])']
    if name == 'popped-owner':
        checks += ['pobwrite.FINISH = OUTPUT_USER_DONE pobinvoke_upper poutputbuffer_saved poboutput false',
                   r'poutputbuffer_saved.ID = 1 /\ pobinvoke.BUFFER.ID = 0',
                   'poutputbuffer_saved.HANDLER = (poutputhandler)', 'poutputhandler.ZOH = POBJECT n_receiver',
                   '$heap_owners($heap_graph(S_reached), HOBJECT n_receiver) = 1',
                   '$heap_count(HOBJECT n_receiver, $machine_roots(S_reached)) = 1',
                   '$output_restore_active(S_reached) = eps', '$output_getter_buffers(S_reached) = S_reached.OUTPUTBUFFERS',
                   '~$output_finish_valid(S_reached, pobwrite[.FINISH = OUTPUT_USER_DONE pobinvoke_upper poutputbuffer_saved[.ID = 0] poboutput false])']
    if name == 'retained-upper':
        checks += ['S_reached.OUTPUTBUFFERS = [poutputbuffer_upper, poutputbuffer_lower]',
                   r'poutputbuffer_upper.CHUNK = 1 /\ poutputbuffer_upper.BYTES = ([72])',
                   '~$output_state_valid(S_reached[.OUTPUTBUFFERS = [poutputbuffer_upper[.FLAGS = 20593], poutputbuffer_lower]])',
                   '$output_write(S_reached, eps).OUTPUTBUFFERS = S_reached.OUTPUTBUFFERS', '$oc_output(S_reached.EVENTS) = ([76,73,65])']
    checks += ['S_done = $drive_steps(S_reached, 2048)',
               r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
               'S_done.OUTPUTBUFFERS = eps', '$oc_output(S_done.EVENTS) = ' + bytes_expr(CASES[name][1]), *valid('S_done')]
    return checks

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--select', help='comma-separated exact group IDs')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    selected = args.select.split(',') if args.select else list(CASES)
    assert selected and len(set(selected)) == len(selected) and all(name in CASES for name in selected)
    out = args.output or Path(tempfile.mkdtemp(prefix='output-chunk-state-', dir=ROOT / '.tools'))
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
            bodies.append('dec $oc_case_' + str(index) + '() : bool\ndef $oc_case_' + str(index) + '() = true\n' +
                          ''.join('  -- if ' + check + '\n' for check in checks))
            report['groups'].append({'id': name, 'premises': len(checks), 'source_sha256': sources.sha(path)})
        fixture = out / 'state.watsup'
        fixture.write_text(PREFIX + '\n'.join(bodies) + '\ndec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if $oc_case_' + str(index) + '()\n' for index in range(len(bodies))))
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
