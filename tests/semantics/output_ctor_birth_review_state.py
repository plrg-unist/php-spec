#!/usr/bin/env python3
"""Completed constructor provenance, matching throws, and immutable report facts."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import tempfile
import time

from recorded_worker import Worker
import output_ctor_birth_sources as sources
import output_deprecation_warning_review_state as runner
import output_object_conversion_review_sources as support

ROOT = support.ROOT
PREFIX = r'''
dec $cb_phase(pstate, nat) : bool
def $cb_phase(S, 0) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.INDEX = 3 /\ pordinaryinternal.CALL.MODE = CTOR_NEW
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n porigin z) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
def $cb_phase(S, 1) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.INDEX = 3 /\ pordinaryinternal.CALL.MODE = CTOR_NEW
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*
  -- if pdestructorcall.FRAME = (pdestructionframe)
def $cb_phase(S, n) = false -- otherwise
dec $cb_seek(pstate, nat, nat) : pstate
def $cb_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $cb_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $cb_phase(S, n_phase)
def $cb_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$cb_phase(S, n_phase)
def $cb_seek(S, n_phase, n) = $cb_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$cb_phase(S, n_phase) /\ $(n > 0)
'''


def public(state):
    return (f'$call_descriptors_valid({state}) /\\ $heap_valid($heap_graph({state})) /\\ '
            f'$output_state_valid({state}) /\\ $destruction_state_valid({state})')


def ctor_assertions(fixture, path, local=False):
    phase = int(local)
    bindings = [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(path.parent)) + ')',
        f'S_found = $cb_seek(S_initial, {phase}, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', f'$cb_phase(S, {phase})',
        'S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*',
        'pctorcall_source = pordinaryinternal.SOURCE', 'pctorcall = pordinaryinternal.CALL',
        'pordinaryinternal.VALUES = [pvalue_message, PINT z_code, PNULL]',
        'n = pctorcall.RECEIVER', 'S.CURRENT = (pcallcontext)', 'S.FRAMES = [pframe]',
        'S_done_found = $drive_steps(S, 1)', 'S_done_found.COMPLETION = BUDGET',
        'S_done = S_done_found[.COMPLETION = NORMAL]', 'S_done.RESULT = KNOWN (POBJECT n)',
        'S_done.FRAMES = [pframe_born]', 'n_last = $nabs($(|S.OBJECTS| - 1))',
    ]
    if local:
        bindings += [
            'pframe_born.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_born eps) :: ptask_native*',
        ]
    else:
        bindings += [
            'pframe_born.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*',
            'pobobjectreturn.SOURCE = (pobobjectsource_born)',
        ]
    bindings += [
        'pobobjectsource_born = OBJECT_NEW_BIRTH porigin_throw pobctorbirth',
        'S_result = S_done[.FRAMES = S.FRAMES]',
        'S_throw_found = $drive_steps(S_done, 1)', 'S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]',
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
        'S_active_found = $drive_steps(S_throw, 1)', 'S_active_found.COMPLETION = BUDGET',
        'S_active = S_active_found[.COMPLETION = NORMAL]',
        'S_active.TODO = (THROW_SEARCH n) :: ptask_active*', 'S_active.FRAMES = [pframe_active]',
        'pobctorbirth_message = pobctorbirth[.MESSAGE = [90]]',
        'pobctorbirth_code = pobctorbirth[.CODE = $(z_code + 1)]',
        'pobctorbirth_site = pobctorbirth[.SITE = porigin_throw]',
        'pobctorbirth_receiver = pobctorbirth[.OBJECT = pobobjectreturn.OBJECT]',
    ]
    if local:
        bindings += [
            'pframe_active.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_active eps) :: ptask_native*',
            'pdestructorcall.FRAME = (pdestructionframe_outer)', 'pdestructionframe_outer.PENDING = (n_old)',
        ]
        inject = lambda source: '$ob_object_final_local_capture(S_throw, pobobjectreturn, pdestructorcall, ' + source + ', ptask_native*)'
        refuse = lambda state: '$ob_object_final_local_birth(' + state + ', pdestructorcall, porigin_throw, n) = eps'
        pending = '$ob_object_final_local_pending(S_active)'
        no_pending = lambda state: '~$ob_object_final_local_pending(' + state + ')'
    else:
        bindings += [
            'pframe_active.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_active) :: ptask_native*',
            'pobobjectreturn_active.SOURCE = (pobobjectsource_active)',
        ]
        inject = lambda source: '$ob_object_final_capture(S_throw, pobobjectreturn, ' + source + ')'
        pending = '$ob_object_final_saved_context(S_active) =/= eps'
        no_pending = lambda state: '$ob_object_final_saved_context(' + state + ') = eps'
    mutations = []
    for label in ('message', 'code', 'site', 'receiver'):
        source = '(OBJECT_NEW_BIRTH porigin_throw pobctorbirth_' + label + ')'
        state = 'S_bad_' + label
        bindings.append(state + ' = ' + inject(source))
        if local:
            check = refuse(state)
        else:
            check = '$ob_object_final_capture_source(' + state + ', pobobjectreturn[.SOURCE = ' + source + '], porigin_throw, n) = eps'
        mutations.append((label, check))
    bindings += ['S_missing = ' + inject('eps'), 'S_legacy = ' + inject('(OBJECT_LEGACY_THROW porigin_throw n)')]
    checks = [
        ('actual selected constructor survives argument reception', r'pctorcall_source.MODE = CTOR_NEW /\ pctorcall.MODE = CTOR_NEW /\ pctorcall_source.RECEIVER = n /\ pctorcall_source.SITE = pctorcall.SITE /\ $ctor_selected(S, pctorcall_source) /\ S_done.CURRENT = S.CURRENT /\ S_done.ENV = S.ENV /\ S_done.OBJECTS = S.OBJECTS'),
        ('completed fields match the selected receiver and immutable fact', r'pobctorbirth.OBJECT = n /\ pobctorbirth.SITE = pctorcall.SITE /\ $string_bytes(pvalue_message) = (pobctorbirth.MESSAGE) /\ pobctorbirth.CODE = z_code /\ pobctorbirth.LINE = pctorcall.LINE /\ $ob_object_ctor_fact_live(S_done, pobctorbirth)'),
        ('birth is borrowed and cannot act as pending throw', r'$ob_object_source_pending((pobobjectsource_born)) = eps /\ $ob_object_source_thrown((pobobjectsource_born)) = eps /\ $heap_count(HOBJECT n, $machine_roots(S_done)) = 1 /\ S_done.ALLOCATIONS = S.ALLOCATIONS'),
        ('method capture wrong result and failed completion produce no fact', r'$ctor_completed(S_result, pctorcall[.MODE = CTOR_METHOD], pvalue_message, PINT z_code, PNULL) = S_result /\ $ctor_completed(S_result, pctorcall[.MODE = CTOR_CAPTURE 0], pvalue_message, PINT z_code, PNULL) = S_result /\ $ctor_completed(S_result[.RESULT = KNOWN PNULL], pctorcall, pvalue_message, PINT z_code, PNULL) = S_result[.RESULT = KNOWN PNULL] /\ $ctor_completed(S_result[.COMPLETION = THROWING n], pctorcall, pvalue_message, PINT z_code, PNULL) = S_result[.COMPLETION = THROWING n]'),
        ('completed constructor is publicly valid', public('S_done')),
        ('actual THROW_VALUE consumes the same constructor fact', r'pobobjectsource_active = OBJECT_THROW_BIRTH porigin_throw pobctorbirth /\ S_throw.RESULT = KNOWN (POBJECT n) /\ ' + pending + r' /\ $heap_count(HOBJECT n, $machine_roots(S_active)) = 1'),
    ]
    checks += [('altered ' + label + ' cannot authenticate THROW_VALUE', check) for label, check in mutations]
    if local:
        missing = refuse('S_missing') + r' /\ ' + refuse('S_legacy')
    else:
        missing = (r'$ob_object_final_capture_source(S_missing, pobobjectreturn[.SOURCE = eps], porigin_throw, n) = eps /\ '
                   r'$ob_object_final_capture_source(S_legacy, pobobjectreturn[.SOURCE = (OBJECT_LEGACY_THROW porigin_throw n)], porigin_throw, n) = eps')
    checks += [
        ('missing or legacy fact cannot mint a fresh throw', missing),
        ('NEW and legacy facts cannot act as active pending provenance', no_pending('S_throw') + r' /\ ' + no_pending('S_legacy')),
        ('consumed constructor is publicly valid', public('S_active')),
    ]
    if local:
        checks += [('argument allocation follows the genuine receiver and retires independently', r'$(n < n_last) /\ $object_name(S, n_last) = $ptascii("Q") /\ ~((HOBJECT n_last) <- S.ALLOCATIONS) /\ $heap_count(HOBJECT n_last, $machine_roots(S)) = 0 /\ pobobjectreturn.OBJECT =/= pdestructorcall.OBJECT /\ $object_name(S, pobobjectreturn.OBJECT) = $ptascii("T") /\ $object_name(S, pdestructorcall.OBJECT) = $ptascii("T") /\ $heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_active)) = 2 /\ $heap_count(HOBJECT pdestructorcall.OBJECT, $machine_roots(S_active)) = 2 /\ $heap_count(HOBJECT n_old, $machine_roots(S_active)) = 1')]
    else:
        checks += [('ordinary message CV contributes bytes without becoming provenance owner', r'pobctorbirth.MESSAGE = [69] /\ S_throw.CURRENT = S_active.CURRENT /\ $heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_active)) = 2')]
    return bindings, checks


EXTRA_PHASES = r'''
def $cb_phase(S, 2) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_tail*
  -- if pdestructionframe.PENDING =/= eps
def $cb_phase(S, 3) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource eps) :: ptask_tail*
def $cb_phase(S, 4) = true
  -- if S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]
  -- if pobdeactivate.INDEX = 0
def $cb_phase(S, 5) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
def $cb_phase(S, 6) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*
def $cb_phase(S, 7) = true
  -- if S.TODO = [RETURN_UNWIND poperand porigin?]
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
def $cb_phase(S, 8) = true
  -- if S.TODO = [RETURN_UNWIND poperand porigin?]
  -- if S.FRAMES = [pframe]
  -- if pframe.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*
'''


def fatal(path, local):
    message, line, method = ('F', 9, '__destruct') if local else ('E', 10, '__toString')
    return (f'Fatal error: Uncaught Exception: {message} in {path}:{line}\nStack trace:\n'
            f'#0 [internal function]: T->{method}()\n#1 {{main}}\n'
            f'  thrown in {path} on line {line}\n').encode()


def endpoint_assertions(fixture, path, local=False):
    bindings, _ = ctor_assertions(fixture, path, local)
    bindings += [
        f'S_exit_found = $cb_seek(S_active, {3 if local else 2}, 512)',
        r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_return*',
        'pobctorbirth_message_thrown = pobctorbirth[.MESSAGE = [90]]',
        'pobctorbirth_code_thrown = pobctorbirth[.CODE = $(z_code + 1)]',
    ]
    if local:
        bindings += [
            'ptask_marker = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_active eps',
            'ptask_return* = [DESTRUCTOR_C_RETURN pdestructorcall, DESTRUCTOR_RESULT pdestructorcall, ptask_marker] ++ ptask_native*',
        ]
        ready = '$ob_object_final_local_ready(S_exit, pobobjectreturn, pdestructorcall, porigin_throw, n, pdestructionframe, ptask_return*)'
        task = lambda src: 'OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall (' + src + ') eps'
        prefix = '[DESTRUCTOR_FRAME_EXIT pdestructionframe, DESTRUCTOR_C_RETURN pdestructorcall, DESTRUCTOR_RESULT pdestructorcall, '
    else:
        bindings += ['ptask_return* = (OUTPUT_FINAL_OBJECT_CV pobobjectreturn_active) :: ptask_native*']
        ready = '$ob_object_final_cv_ready(S_exit, pobobjectreturn_active, pdestructionframe, n)'
        task = lambda src: 'OUTPUT_FINAL_OBJECT_CV pobobjectreturn_active[.SOURCE = (' + src + ')]'
        prefix = '[DESTRUCTOR_FRAME_EXIT pdestructionframe, '
    guards = []
    for label, source in (
            ('message', 'OBJECT_THROW_BIRTH porigin_throw pobctorbirth_message_thrown'),
            ('code', 'OBJECT_THROW_BIRTH porigin_throw pobctorbirth_code_thrown'),
            ('new', 'OBJECT_NEW_BIRTH porigin_throw pobctorbirth'),
            ('legacy', 'OBJECT_LEGACY_THROW porigin_throw n')):
        tag = task(source)
        tail = ' ++ ptask_native*' if local else ' ++ ptask_native*'
        bindings.append('S_exit_' + label + ' = S_exit[.TODO = ' + prefix + tag + ']' + tail + ']')
        if local and label in ('new', 'legacy'):
            bindings.append('S_exit_' + label + '.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: ptask_return_' + label + '*')
            guards.append('~$ob_object_final_local_ready(S_exit_' + label + ', pobobjectreturn, pdestructorcall, porigin_throw, n, pdestructionframe, ptask_return_' + label + '*)')
        else:
            guards.append('~$call_task_valid(S_exit_' + label + ', ' + tag + ')')
    bindings += [
        'S_report_found = $drive_steps(S_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n true]',
        'S_deactivate_found = $cb_seek(S_report, 4, 512)',
        r'S_deactivate_found.COMPLETION = NORMAL \/ S_deactivate_found.COMPLETION = BUDGET',
        'S_deactivate = S_deactivate_found[.COMPLETION = NORMAL]',
    ]
    warning = '' if local else ', WARNING ($ptascii("missing")) 4'
    events = '[OUTPUT ([80])' + warning + ', STDERR ' + runner.bytes_expr(fatal(path, local)) + ']'
    message, line = ('F', 9) if local else ('E', 10)
    checks = [
        ('real null-C report retains the completed fact', ready + r' /\ S_exit.CURRENT = eps /\ S_exit.FRAMES = eps /\ S_exit.ORIGIN = eps /\ $heap_count(HOBJECT n, $machine_roots(S_exit)) = 1'),
        ('active public tasks reject wrong normalized fields and unconsumed facts', r' /\ '.join(guards)),
        ('actual fatal uses normalized constructor bytes and own source line', 'S_report.EVENTS = ' + events + f' /\\ pobdeactivate.COMPLETION = REQUESTFATAL ($ptascii("Exception")) ($ptascii("{message}")) {line}' + r' /\ S_report.EXITSTATUS = 255 /\ $heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_report)) = 2'),
        ('reported Throwable retires without a borrowed owner', r'~((HOBJECT n) <- S_deactivate.ALLOCATIONS) /\ $heap_count(HOBJECT n, $machine_roots(S_deactivate)) = 0 /\ $heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_deactivate)) = 2 /\ S_deactivate.EVENTS = S_report.EVENTS'),
    ]
    if local:
        bindings += [
            'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_outer]',
            'ptask_receipt_bad = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall (OBJECT_THROW_BIRTH porigin_throw pobctorbirth_message_thrown) (pobdeactivate)',
            'pdestructioncleanup_bad = pdestructioncleanup_outer[.SOURCE = ptask_receipt_bad]',
            'S_retired_bad = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_bad]]',
        ]
        checks += [('retired local receipt uses immutable facts and real C owners', r'$eager_cleanup_valid(S_deactivate, pdestructioncleanup_local) /\ $eager_cleanup_valid(S_deactivate, pdestructioncleanup_outer) /\ ~$eager_cleanup_valid(S_retired_bad, pdestructioncleanup_bad) /\ $heap_count(HOBJECT pdestructorcall.OBJECT, $machine_roots(S_deactivate)) = 2 /\ $heap_count(HOBJECT n_old, $machine_roots(S_deactivate)) = 1 /\ $task_nodes(pdestructioncleanup_outer.SOURCE) = eps /\ $eager_abandoned_owner(pdestructioncleanup_outer.SOURCE) = [HOBJECT pobobjectreturn.OBJECT, HOBJECT pobobjectreturn.OBJECT]')]
    else:
        bindings += [
            'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup]',
            'pobobjectreturn_receipt_bad = pobobjectreturn_active[.SOURCE = (OBJECT_THROW_BIRTH porigin_throw pobctorbirth_message_thrown)]',
            'pdestructioncleanup_bad = pdestructioncleanup[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_receipt_bad pobdeactivate porigin_throw n]',
            'S_retired_bad = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_bad]]',
        ]
        checks += [('retired CV receipt uses immutable facts and retained cast pair', r'$eager_cleanup_valid(S_deactivate, pdestructioncleanup) /\ ~$eager_cleanup_valid(S_retired_bad, pdestructioncleanup_bad) /\ $task_nodes(pdestructioncleanup.SOURCE) = eps /\ $eager_abandoned_owner(pdestructioncleanup.SOURCE) = [HOBJECT pobobjectreturn.OBJECT, HOBJECT pobobjectreturn.OBJECT]')]
    return bindings, checks


def clearing_assertions(fixture, path, local=False, normal=False):
    bindings, _ = ctor_assertions(fixture, path, local)
    phase = (8 if local else 7) if normal else (6 if local else 5)
    bindings += [f'S_clear_found = $cb_seek(S_active, {phase}, 512)',
                 r'S_clear_found.COMPLETION = NORMAL \/ S_clear_found.COMPLETION = BUDGET',
                 'S_clear = S_clear_found[.COMPLETION = NORMAL]', 'S_clear.FRAMES = [pframe_clear]']
    if local:
        bindings += ['pframe_clear.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*']
        retained = r'$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_clear)) = 2 /\ $heap_count(HOBJECT pdestructorcall.OBJECT, $machine_roots(S_clear)) = 2 /\ $heap_count(HOBJECT n_old, $machine_roots(S_clear)) = 1'
    else:
        bindings += ['pframe_clear.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_clear) :: ptask_native*',
                     'pobobjectreturn_clear = pobobjectreturn[.SOURCE = eps]']
        retained = '$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots(S_clear)) = 2'
    if normal:
        bindings += ['S_clear.TODO = [RETURN_UNWIND poperand porigin_return?]']
        check = r'~((HOBJECT n) <- S_clear.ALLOCATIONS) /\ $heap_count(HOBJECT n, $machine_roots(S_clear)) = 0'
    else:
        bindings += ['S_clear.TODO = (CATCH_BIND porigin_try n_index n) :: ptask_catch*']
        check = r'(HOBJECT n) <- S_clear.ALLOCATIONS /\ $heap_count(HOBJECT n, $machine_roots(S_clear)) = 1 /\ $task_nodes(CATCH_BIND porigin_try n_index n) = [HOBJECT n]'
    return bindings, [('real normal consumption retires the borrowed fact' if normal else 'real catch consumes provenance while retaining its Throwable', check + r' /\ ' + retained), ('cleared actual budget state remains publicly valid', public('S_clear'))]

PREFIX = PREFIX.replace("def $cb_phase(S, n) = false -- otherwise", EXTRA_PHASES + "def $cb_phase(S, n) = false -- otherwise")

def render(bindings, checks):
    return (PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
            ', '.join('(' + check + ')' for _, check in checks) + ']\n' +
            ''.join('  -- if ' + binding + '\n' for binding in bindings))


def fingerprint():
    return {name: support.common.sha(ROOT / name) for name in (
        'spec/semantics/161-throwable-constructors.watsup', 'spec/semantics/30-storage.watsup',
        'spec/semantics/456-output-object-returns.watsup', 'spec/semantics/modules.json',
        'tests/semantics/output_ctor_birth_sources.py', 'tests/semantics/output_ctor_birth_review_state.py',
        'tests/semantics/_build/default/numeric_runner.exe')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--native-root', type=Path, help='Reuse frozen native source paths; never execute the oracle.')
    parser.add_argument('--stage', choices=('ctor', 'endpoint', 'caught', 'normal'), default='ctor')
    parser.add_argument('--select', choices=('cv', 'local', 'all'), default='all')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-ctor-birth-review-'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': support.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': support.common.PROFILE, 'native_agreement_credit': 0, 'stage': args.stage, 'cap_seconds': 300,
              'records': [], 'passed': False}
    directory = out
    try:
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        for index, (name, source) in enumerate(sources.CASES.items()):
            short = 'local' if index else 'cv'
            if args.select not in ('all', short):
                continue
            directory = out / short
            directory.mkdir()
            if args.stage in ('caught', 'normal'):
                needle = b'throw new Exception(message());' if index else b'throw new Exception($message);'
                suffix = b' catch (Exception $e) { }' if index else b" catch (Exception $e) { return 'H'; }"
                if args.stage == 'normal':
                    suffix = b' finally { return; }' if index else b" finally { return 'H'; }"
                assert source.count(needle) == 1
                source = source.replace(needle, b'try { ' + needle + b' }' + suffix)
            frozen = args.native_root and args.stage in ('ctor', 'endpoint')
            path = args.native_root / f'native-0{index + 1}' / 'source.php' if frozen else directory / 'source.php'
            if frozen:
                assert path.read_bytes() == source
            else:
                path.write_bytes(source)
            frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], directory / 'frontend')
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            finally:
                frontend.close()
            adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], directory / 'adapter')
            try:
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            finally:
                adapter.close()
            if args.stage == 'endpoint':
                bindings, checks = endpoint_assertions(checked['fixture'], path, bool(index))
            elif args.stage in ('caught', 'normal'):
                bindings, checks = clearing_assertions(checked['fixture'], path, bool(index), args.stage == 'normal')
            else:
                bindings, checks = ctor_assertions(checked['fixture'], path, bool(index))
            fixture = directory / 'state.watsup'
            fixture.write_text(render(bindings, checks))
            record = {'case': name, 'fixture_sha256': support.common.sha(fixture), 'checks': [label for label, _ in checks], 'passed': False}
            report['records'].append(record)
            started = time.monotonic()
            result = support.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            record['seconds'] = round(time.monotonic() - started, 3)
            text = result.stdout.decode('ascii')
            values = re.findall(r'\b(?:true|false)\b', text)
            record.update(exit_status=result.returncode, results=dict(zip(record['checks'], [value == 'true' for value in values])))
            assert not re.sub(r'true|false|[\[\](),;\s]', '', text), text
            assert result.returncode == 0 and not result.stderr and values == ['true'] * len(checks), (result.returncode, result.stdout, result.stderr)
            record['passed'] = True
            print(short, True, flush=True)
        report['passed'] = True
    except BaseException as error:
        if isinstance(error, support.subprocess.TimeoutExpired):
            (directory / 'state.stdout').write_bytes(error.stdout or b'')
            (directory / 'state.stderr').write_bytes(error.stderr or b'')
            (directory / 'state.timeout').write_text(str(error.timeout) + '\n')
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = fingerprint()
        report['stable'] = report['before'] == report['after']
        report['passed'] = report['passed'] and report['stable']
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(out / 'report.json', report['passed'], flush=True)


if __name__ == '__main__':
    main()
