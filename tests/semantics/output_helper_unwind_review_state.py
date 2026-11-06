#!/usr/bin/env python3
"""Fresh helper provenance crosses its actual VM return before native reporting."""
import argparse
import base64
import json
import os
from pathlib import Path
import re
import tempfile
import time

from recorded_worker import Worker
import output_deprecation_warning_review_state as runner
import output_helper_unwind_sources as sources
import output_object_conversion_review_sources as support

ROOT = support.ROOT
PREFIX = r'''
dec $hu_phase(pstate, nat) : bool
def $hu_phase(S, 0) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.INDEX = 3 /\ pordinaryinternal.CALL.MODE = CTOR_NEW
  -- if S.FRAMES = [pframe_helper, pframe_native]
  -- if pframe_helper.CONTEXT = (pcallcontext_native)
  -- if pframe_native.TODO = (STRINGIFY_RESULT n porigin z) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*
def $hu_phase(S, 1) = true
  -- if S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*
  -- if pordinaryinternal.INDEX = 3 /\ pordinaryinternal.CALL.MODE = CTOR_NEW
  -- if S.FRAMES = [pframe_helper, pframe_native]
  -- if pframe_helper.CONTEXT = (pcallcontext_native)
  -- if pframe_native.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*
  -- if pdestructorcall.FRAME = (pdestructionframe)
def $hu_phase(S, 2) = true
  -- if S.TODO = [THROW_SEARCH n]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
  -- if S.FRAMES = [pframe_call, pframe_native]
def $hu_phase(S, n) = false -- otherwise
dec $hu_seek(pstate, nat, nat) : pstate
def $hu_seek(S, n_phase, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $hu_seek(S, n_phase, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $hu_phase(S, n_phase)
def $hu_seek(S, n_phase, 0) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$hu_phase(S, n_phase)
def $hu_seek(S, n_phase, n) = $hu_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$hu_phase(S, n_phase) /\ $(n > 0)
'''


def public(state):
    return (f'$call_descriptors_valid({state}) /\\ $heap_valid($heap_graph({state})) /\\ '
            f'$output_state_valid({state}) /\\ $destruction_state_valid({state})')


def reach_ctor(fixture, path, local):
    return [
        'S_initial = $php_file_run(' + fixture + ', 0, ' + runner.bytes_expr(os.fsencode(path)) + ', ' + runner.bytes_expr(os.fsencode(path.parent)) + ')',
        f'S_found = $hu_seek(S_initial, {int(local)}, 1024)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', f'$hu_phase(S, {int(local)})',
        'S.TODO = (ORDINARY_CTOR_RECEIVE pordinaryinternal) :: ptask_tail*',
        'pctorcall_source = pordinaryinternal.SOURCE', 'pctorcall = pordinaryinternal.CALL',
        'pordinaryinternal.VALUES = [pvalue_message, PINT z_code, PNULL]',
        'n_exception = pctorcall.RECEIVER', 'S.CURRENT = (pcallcontext_helper)',
        'S.FRAMES = [pframe_helper, pframe_native]',
        'pframe_helper.CONTEXT = (pcallcontext_native)',
        '$function_at(S.FUNCTIONS, pcallcontext_helper.FUNCTION) = (pfunction_helper)',
        '$function_at($all_functions(S), pcallcontext_native.FUNCTION) = (pfunction_native)',
    ]



def control_source(source, local, stage):
    message = b'F' if local else b'E'
    helper_throw = b'throw new Exception($message);'
    if stage == 'byref':
        return source.replace(b'function fail()', b'function &fail()')
    if stage == 'empty':
        return source.replace(b"    $message = '" + message + b"';\n", b'').replace(helper_throw, b"throw new Exception('" + message + b"');")
    if stage in ('helper-catch', 'helper-normal'):
        suffix = b" catch (Exception $e) { return 'H'; }" if stage == 'helper-catch' else b" finally { return 'H'; }"
        return source.replace(helper_throw, b'try { ' + helper_throw + b' }' + suffix)
    if stage in ('caller-catch', 'caller-normal'):
        call = b'fail();' if local else b'return fail();'
        if stage == 'caller-catch':
            suffix = b' catch (Exception $e) { }' if local else b" catch (Exception $e) { return 'H'; }"
        else:
            suffix = b' finally { return; }' if local else b" finally { return 'H'; }"
        return source.replace(call, b'try { ' + call + b' }' + suffix)
    return source

def reach_throw(fixture, path, local):
    bindings = reach_ctor(fixture, path, local) + [
        'S_done_found = $drive_steps(S, 1)', 'S_done_found.COMPLETION = BUDGET',
        'S_done = S_done_found[.COMPLETION = NORMAL]',
        '$ob_object_call_context(S_done) = ((S_native_born, pfunction_helper, pobsourcecall))',
        '$ob_object_native_source(S_native_born) = (OBJECT_CALL_NEW porigin_throw pobctorbirth pobsourcecall)',
        'pobctorbirth.OBJECT = n_exception',
        'S_throw_found = $drive_steps(S_done, 1)', 'S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]',
        'S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw*',
        'S_active_found = $drive_steps(S_throw, 1)', 'S_active_found.COMPLETION = BUDGET',
        'S_active = S_active_found[.COMPLETION = NORMAL]',
        'S_active.TODO = (THROW_SEARCH n_exception) :: ptask_unwind*',
        '$ob_object_call_context(S_active) = ((S_native_active, pfunction_helper, pobsourcecall))',
        '$ob_object_native_source(S_native_active) = (OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecall)',
        'S_native_active.FRAMES = [pframe_native_active]',
    ]
    if local:
        bindings += [
            'pframe_native_active.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_active eps) :: ptask_native*',
            'pdestructorcall.FRAME = (pdestructionframe_outer)', 'pdestructionframe_outer.PENDING = (n_old)',
        ]
    else:
        bindings += ['pframe_native_active.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn) :: ptask_native*']
    return bindings


def roots(state, local, fresh=1):
    result = (f'$heap_count(HOBJECT pobobjectreturn.OBJECT, $machine_roots({state})) = 2 /\\ '
              f'$heap_count(HOBJECT n_exception, $machine_roots({state})) = {fresh}')
    if local:
        result += (f' /\\ $heap_count(HOBJECT pdestructorcall.OBJECT, $machine_roots({state})) = 2'
                   f' /\\ $heap_count(HOBJECT n_old, $machine_roots({state})) = 1')
    return result


def transport_assertions(fixture, path, local, stage):
    bindings = reach_throw(fixture, path, local) + [
        'S_exit_found = $hu_seek(S_active, 2, 256)',
        r'S_exit_found.COMPLETION = NORMAL \/ S_exit_found.COMPLETION = BUDGET',
        'S_exit = S_exit_found[.COMPLETION = NORMAL]',
        'S_exit.TODO = [THROW_SEARCH n_exception]',
        'S_exit.FRAMES = [pframe_helper, pframe_native_active]',
        'S_raw = $restore_frame_raw(S_exit)',
        'S_budget = $drive_steps(S_exit, 0)',
        'S_one_found = $drive_steps(S_exit, 1)', 'S_one_found.COMPLETION = BUDGET',
        'S_one = S_one_found[.COMPLETION = NORMAL]',
        'S_one.CURRENT = (pcallcontext_native)', 'S_one.FRAMES = [pframe_native_unwind]',
        '$ob_object_native_source(S_one) = (OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecall)',
        'S_bad_pending = S_exit[.TODO = [THROW_SEARCH pobobjectreturn.OBJECT]]',
        'S_bad_held = S_exit[.FRAMES = [pframe_helper[.HELD = [HOBJECT pobobjectreturn.OBJECT]], pframe_native_active]]',
        'S_bad_tasks = S_exit[.FRAMES = [pframe_helper[.TODO = (THROW_SEARCH n_exception) :: pframe_helper.TODO], pframe_native_active]]',
        'S_bad_target = S_exit[.CURRENT = (pcallcontext_helper[.TARGET = pcallcontext_native.TARGET])]',
        'S_bad_native = S_raw[.CURRENT = (pcallcontext_helper)]',
        'pobsourcecall_function = pobsourcecall[.FUNCTION = pfunction_native.ORIGIN]',
        'pobsourcecall_site = pobsourcecall[.SITE = porigin_throw]',
        'S_bad_function = $ob_object_call_capture(S_exit, (OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecall_function))',
        'S_bad_site = $ob_object_call_capture(S_exit, (OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecall_site))',
        'S_missing = $ob_object_call_capture(S_exit, eps)',
    ]
    checks = [
        ('actual selected helper producer differs from native consumer', r'pcallcontext_helper.TARGET = pfunction_helper.ORIGIN /\ pcallcontext_helper.FUNCTION = pfunction_helper.ORIGIN /\ pfunction_helper.ORIGIN =/= pfunction_native.ORIGIN /\ pfunction_helper.SIGNATURE.PARAMETERS = eps /\ ~$function_generator(S, pfunction_helper) /\ pcallcontext_native.CALLSITE = eps /\ pcallcontext_native.LINE = $(-1) /\ $destructor_context_nodes((pcallcontext_helper)) = eps'),
        ('completed constructor fact records the real helper receiver and normalized fields', r'pctorcall_source.RECEIVER = n_exception /\ pctorcall.MODE = CTOR_NEW /\ pctorcall_source.MODE = CTOR_NEW /\ pctorcall_source.SITE = pctorcall.SITE /\ $ctor_selected(S, pctorcall_source) /\ pobctorbirth.SITE = pctorcall.SITE /\ $string_bytes(pvalue_message) = (pobctorbirth.MESSAGE) /\ pobctorbirth.CODE = z_code /\ pobctorbirth.LINE = pctorcall.LINE /\ $ob_object_ctor_fact_live(S_done, pobctorbirth)'),
        ('producer source and actual native own-call site authenticate independently', r'pobsourcecall.FUNCTION = pfunction_helper.ORIGIN /\ pcallcontext_helper.CALLSITE = (pobsourcecall.SITE) /\ pframe_helper.ORIGIN = (pobsourcecall.SITE) /\ $ob_object_call_function(S, pfunction_native, pobsourcecall) = ((pfunction_helper, pcallcontext_helper.LINE)) /\ $ob_object_ctor_fact_source(S, pfunction_helper, porigin_throw, pobctorbirth) /\ ~$ob_object_ctor_fact_source(S, pfunction_native, porigin_throw, pobctorbirth)'),
        ('helper throw has no native pending authority or premature report', r'$ob_object_call_pending(S_active) /\ $ob_object_source_thrown((OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecall)) = eps /\ S_active.CURRENT = S.CURRENT /\ S_active.EVENTS = [OUTPUT ([80])] /\ ' + roots('S_active', local)),
        ('actual helper capture is publicly valid', public('S_active')),
        ('zero budget keeps real helper native and pending owners', r'S_budget.COMPLETION = BUDGET /\ S_budget.CURRENT = S_exit.CURRENT /\ S_budget.FRAMES = S_exit.FRAMES /\ S_budget.TODO = S_exit.TODO /\ S_budget.ALLOCATIONS = S_exit.ALLOCATIONS /\ S_budget.GC = S_exit.GC /\ S_budget.EVENTS = S_exit.EVENTS /\ ' + roots('S_exit', local)),
        ('wrong pending producer target and saved continuation owners cannot restore provenance', r'$destructor_frame_restore(S_bad_pending, S_raw) = S_raw /\ $ob_object_call_context(S_bad_held) = eps /\ $ob_object_call_context(S_bad_tasks) = eps /\ $ob_object_call_context(S_bad_target) = eps /\ $destructor_frame_restore(S_exit, S_bad_native) = S_bad_native'),
        ('missing or altered call fact cannot gain native unwind authority', r'~$ob_object_call_pending(S_bad_function) /\ ~$ob_object_call_pending(S_bad_site) /\ ~$ob_object_call_pending(S_missing) /\ $destructor_frame_restore(S_bad_function, S_raw) = S_raw /\ $destructor_frame_restore(S_bad_site, S_raw) = S_raw /\ $destructor_frame_restore(S_missing, S_raw) = S_raw'),
        ('real restore transports the fact without borrowing an extra C owner', r'$ob_object_source_thrown((OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecall)) = ((porigin_throw, pobctorbirth)) /\ S_one.ORIGIN = (pobsourcecall.SITE) /\ S_one.EVENTS = [OUTPUT ([80])] /\ ' + roots('S_one', local)),
        ('actual restored state remains publicly valid', public('S_one')),
    ]
    if stage == 'empty':
        checks += [('empty helper uses actual unstaged restore and protects the pending root', r'pfunction_helper.CVS = eps /\ ~$destructor_frame_staged(S_exit) /\ S_one.TODO = (THROW_SEARCH n_exception) :: S_raw.TODO /\ S_one.DESTRUCTION.FRAMES = S_exit.DESTRUCTION.FRAMES')]
    else:
        bindings += ['S_one.DESTRUCTION.FRAMES = pdestructionframe_helper :: pdestructionframe_tail*']
        checks += [('helper CV cleanup restores caller before the later native C return', r'pdestructionframe_helper.FUNCTION = pfunction_helper.ORIGIN /\ pdestructionframe_helper.FUNCTION =/= pfunction_native.ORIGIN /\ pdestructionframe_helper.PENDING = (n_exception) /\ pdestructionframe_helper.CALLER = (pcallcontext_native) /\ pdestructionframe_helper.ORIGIN = (pobsourcecall.SITE) /\ S_one.CURRENT =/= eps')]
    if stage == 'byref':
        checks += [('byref declared helper publishes no reference retval on exceptional restore', r'pfunction_helper.SIGNATURE.BYREF /\ S_one.RESULT = KNOWN PNULL /\ ' + roots('S_one', local))]
    if stage == 'byref' and local:
        bindings += [
            'pcallcontext_wrong_receiver = pcallcontext_native[.TARGET = METHOD_TARGET pobobjectreturn.OBJECT pfunction_native.ORIGIN][.RECEIVER = (pobobjectreturn.OBJECT)]',
            'S_wrong_receiver = S_exit[.FRAMES = [pframe_helper[.CONTEXT = (pcallcontext_wrong_receiver)], pframe_native_active]]',
            'S_old_pending = S_exit[.TODO = [THROW_SEARCH n_old]]',
        ]
        checks += [('same-class wrong native receiver and distinct old Throwable cannot receive provenance', r'pobobjectreturn.OBJECT =/= pdestructorcall.OBJECT /\ $object_name(S, pobobjectreturn.OBJECT) = $object_name(S, pdestructorcall.OBJECT) /\ $ob_object_call_context(S_wrong_receiver) = eps /\ $destructor_frame_restore(S_wrong_receiver, S_raw) = S_raw /\ n_old =/= n_exception /\ $throwable_live(S_exit, n_old) /\ $destructor_frame_restore(S_old_pending, S_raw) = S_raw')]
    return bindings, checks


EXTRA_PHASES = r'''
def $hu_phase(S, 5) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
  -- if S.FRAMES = [pframe_call, pframe_native]
def $hu_phase(S, 6) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n) :: ptask_tail*
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = [pframe_native]
def $hu_phase(S, 7) = true
  -- if S.TODO = [RETURN_UNWIND poperand porigin?]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = pcallcontext.FUNCTION
  -- if S.FRAMES = [pframe_call, pframe_native]
def $hu_phase(S, 8) = true
  -- if S.TODO = [RETURN_UNWIND poperand porigin?]
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_object porigin_method
  -- if S.FRAMES = [pframe_native]
def $hu_phase(S, 9) = true
  -- if S.TODO = [OUTPUT_FINAL_DEACTIVATE pobdeactivate]
  -- if pobdeactivate.INDEX = 0
def $hu_phase(S, 10) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (OUTPUT_FINAL_OBJECT_CV pobobjectreturn) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $hu_phase(S, 11) = true
  -- if S.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe) :: (DESTRUCTOR_C_RETURN pdestructorcall) :: (DESTRUCTOR_RESULT pdestructorcall) :: (OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource eps) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def fatal(path, local):
    message, line, call, method = ('F', 12, 8, '__destruct') if local else ('E', 15, 9, '__toString')
    return (f'Fatal error: Uncaught Exception: {message} in {path}:{line}\nStack trace:\n'
            f'#0 {path}({call}): fail()\n#1 [internal function]: T->{method}()\n#2 {{main}}\n'
            f'  thrown in {path} on line {line}\n').encode()


def report_assertions(fixture, path, local):
    bindings, _ = transport_assertions(fixture, path, local, 'transport')
    bindings += [
        'pobobjectsource_unwind = OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecall',
        'pobobjectsource_unreturned = OBJECT_CALL_THROW porigin_throw pobctorbirth pobsourcecall',
        'pobobjectsource_bad_site = OBJECT_CALL_UNWIND porigin_throw pobctorbirth pobsourcecall_site',
        f'S_native_exit_found = $hu_seek(S_one, {11 if local else 10}, 512)',
        r'S_native_exit_found.COMPLETION = NORMAL \/ S_native_exit_found.COMPLETION = BUDGET',
        'S_native_exit = S_native_exit_found[.COMPLETION = NORMAL]',
        'S_native_exit.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe_native) :: ptask_return*',
        'S_native_exit.DESTRUCTION.FRAMES = pdestructionframe_native :: pdestructionframe_native_tail*',
        'pdestructionframe_wrong = pdestructionframe_native[.FUNCTION = pfunction_helper.ORIGIN]',
        'S_wrong_function = S_native_exit[.DESTRUCTION.FRAMES = pdestructionframe_wrong :: pdestructionframe_native_tail*][.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe_wrong) :: ptask_return*]',
    ]
    if local:
        bindings += ['ptask_return* = [DESTRUCTOR_C_RETURN pdestructorcall, DESTRUCTOR_RESULT pdestructorcall, OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_unwind eps] ++ ptask_native*']
        ready = lambda state, frame='pdestructionframe_native', tail='ptask_return*': '$ob_object_final_local_ready(' + state + ', pobobjectreturn, pdestructorcall, porigin_throw, n_exception, ' + frame + ', ' + tail + ')'
        task = lambda source: 'OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall ' + source + ' eps'
        bindings += [
            'ptask_unreturned* = [DESTRUCTOR_C_RETURN pdestructorcall, DESTRUCTOR_RESULT pdestructorcall, ' + task('pobobjectsource_unreturned') + '] ++ ptask_native*',
            'S_unreturned = S_native_exit[.TODO = (DESTRUCTOR_FRAME_EXIT pdestructionframe_native) :: ptask_unreturned*]',
        ]
        phase_refusal = '~' + ready('S_unreturned', tail='ptask_unreturned*')
    else:
        bindings += [
            'ptask_return* = (OUTPUT_FINAL_OBJECT_CV pobobjectreturn_unwind) :: ptask_native*',
            'pobobjectreturn_unwind = pobobjectreturn[.SOURCE = (pobobjectsource_unwind)]',
            'pobobjectreturn_unreturned = pobobjectreturn[.SOURCE = (pobobjectsource_unreturned)]',
            'S_unreturned = S_native_exit[.TODO = [DESTRUCTOR_FRAME_EXIT pdestructionframe_native, OUTPUT_FINAL_OBJECT_CV pobobjectreturn_unreturned] ++ ptask_native*]',
        ]
        ready = lambda state, frame='pdestructionframe_native': '$ob_object_final_cv_ready(' + state + ', pobobjectreturn_unwind, ' + frame + ', n_exception)'
        phase_refusal = '~$ob_object_final_cv_ready(S_unreturned, pobobjectreturn_unreturned, pdestructionframe_native, n_exception)'
    bindings += [
        'S_report_found = $drive_steps(S_native_exit, 1)', 'S_report_found.COMPLETION = BUDGET',
        'S_report = S_report_found[.COMPLETION = NORMAL]',
        'S_report.TODO = [OUTPUT_FINAL_PENDING pobdeactivate n_exception true]',
        'S_deactivate_found = $hu_seek(S_report, 9, 512)',
        r'S_deactivate_found.COMPLETION = NORMAL \/ S_deactivate_found.COMPLETION = BUDGET',
        'S_deactivate = S_deactivate_found[.COMPLETION = NORMAL]',
    ]
    warning = '' if local else ', WARNING ($ptascii("missing")) 4'
    events = '[OUTPUT ([80])' + warning + ', STDERR ' + runner.bytes_expr(fatal(path, local)) + ']'
    checks = [
        ('only the native cleanup frame admits null-C reporting', ready('S_native_exit') + r' /\ pdestructionframe_native.FUNCTION = pfunction_native.ORIGIN /\ pdestructionframe_native.FUNCTION =/= pfunction_helper.ORIGIN /\ pdestructionframe_native.PENDING = (n_exception) /\ pdestructionframe_native.CALLER = eps /\ S_native_exit.CURRENT = eps /\ S_native_exit.FRAMES = eps /\ S_native_exit.ORIGIN = eps'),
        ('wrong producer cleanup function and unreturned helper phase cannot report', '~' + ready('S_wrong_function', frame='pdestructionframe_wrong') + r' /\ ' + phase_refusal),
        ('actual fatal preserves helper source trace and real native C owners', 'S_report.EVENTS = ' + events + r' /\ S_report.EXITSTATUS = 255 /\ $throwable_field(S_report, n_exception, "previous") = PNULL /\ ' + roots('S_report', local)),
        ('reported helper Throwable retires without a borrowed owner', r'~((HOBJECT n_exception) <- S_deactivate.ALLOCATIONS) /\ S_deactivate.EVENTS = S_report.EVENTS /\ ' + roots('S_deactivate', local, 0)),
    ]
    if local:
        bindings += [
            'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_outer]',
            'pdestructioncleanup_phase = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_unreturned (pobdeactivate)]',
            'pdestructioncleanup_site = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_LOCAL_THROW pobobjectreturn pdestructorcall pobobjectsource_bad_site (pobdeactivate)]',
            'S_phase = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_phase]]',
            'S_site = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_local, pdestructioncleanup_site]]',
        ]
        valid = r'$eager_cleanup_valid(S_deactivate, pdestructioncleanup_local) /\ $eager_cleanup_valid(S_deactivate, pdestructioncleanup_outer) /\ ~$eager_cleanup_valid(S_phase, pdestructioncleanup_phase) /\ ~$eager_cleanup_valid(S_site, pdestructioncleanup_site)'
    else:
        bindings += [
            'S_report.DESTRUCTION.ABANDONED = [pdestructioncleanup_outer]',
            'pdestructioncleanup_phase = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_unreturned pobdeactivate porigin_throw n_exception]',
            'pobobjectreturn_site = pobobjectreturn[.SOURCE = (pobobjectsource_bad_site)]',
            'pdestructioncleanup_site = pdestructioncleanup_outer[.SOURCE = OUTPUT_FINAL_OBJECT_THROW pobobjectreturn_site pobdeactivate porigin_throw n_exception]',
            'S_phase = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_phase]]',
            'S_site = S_deactivate[.DESTRUCTION.ABANDONED = [pdestructioncleanup_site]]',
        ]
        valid = r'$eager_cleanup_valid(S_deactivate, pdestructioncleanup_outer) /\ ~$eager_cleanup_valid(S_phase, pdestructioncleanup_phase) /\ ~$eager_cleanup_valid(S_site, pdestructioncleanup_site)'
    checks += [('retired receipts require the real restore phase and native own-call site', valid + r' /\ $task_nodes(pdestructioncleanup_outer.SOURCE) = eps /\ $eager_abandoned_owner(pdestructioncleanup_outer.SOURCE) = [HOBJECT pobobjectreturn.OBJECT, HOBJECT pobobjectreturn.OBJECT]')]
    return bindings, checks


def clearing_assertions(fixture, path, local, stage):
    bindings = reach_throw(fixture, path, local)
    helper = stage.startswith('helper-')
    normal = stage.endswith('normal')
    phase = (7 if helper else 8) if normal else (5 if helper else 6)
    bindings += [f'S_clear_found = $hu_seek(S_active, {phase}, 512)',
                 r'S_clear_found.COMPLETION = NORMAL \/ S_clear_found.COMPLETION = BUDGET',
                 'S_clear = S_clear_found[.COMPLETION = NORMAL]']
    if helper:
        bindings += ['$ob_object_call_context(S_clear) = ((S_native_clear, pfunction_helper, pobsourcecall))']
        scope = 'S_native_clear'
    else:
        scope = 'S_clear'
    bindings += ['$ob_object_native_source(' + scope + ') = eps', scope + '.FRAMES = [pframe_native_clear]']
    if local:
        bindings += ['pframe_native_clear.TODO = (DESTRUCTOR_RESULT pdestructorcall) :: ptask_native*']
    else:
        bindings += [
            'pframe_native_clear.TODO = (STRINGIFY_RESULT n_object porigin_site 0) :: (OB_USER_OBJECT_STRING pobobjectreturn_clear) :: ptask_native*',
            'pobobjectreturn_clear = pobobjectreturn[.SOURCE = eps]',
        ]
    if normal:
        bindings += ['S_clear.TODO = [RETURN_UNWIND (KNOWN pvalue_return) porigin_return?]']
        returned = 'pvalue_return = PNULL' if local and not helper else '$string_bytes(pvalue_return) = ($ptascii("H"))'
        actual = r'~((HOBJECT n_exception) <- S_clear.ALLOCATIONS) /\ $heap_count(HOBJECT n_exception, $machine_roots(S_clear)) = 0 /\ ' + returned
    else:
        bindings += ['S_clear.TODO = (CATCH_BIND porigin_try n_index n_exception) :: ptask_catch*']
        actual = r'(HOBJECT n_exception) <- S_clear.ALLOCATIONS /\ $task_nodes(CATCH_BIND porigin_try n_index n_exception) = [HOBJECT n_exception]'
    checks = [
        ('actual helper or caller consumes the precise captured fact', actual + r' /\ S_clear.CURRENT = ' + ('(pcallcontext_helper)' if helper else '(pcallcontext_native)') + r' /\ ' + roots('S_clear', local, 0 if normal else 1)),
        ('cleared source-reached budget state is publicly valid', public('S_clear')),
    ]
    if normal and helper:
        bindings += ['S_return_found = $drive_steps(S_clear, 1)', 'S_return_found.COMPLETION = BUDGET',
                     'S_return = S_return_found[.COMPLETION = NORMAL]']
        checks += [('normal VM restore publishes no stale native helper fact', r'S_return.CURRENT = (pcallcontext_native) /\ $ob_object_native_source(S_return) = eps /\ ' + roots('S_return', local, 0))]
    return bindings, checks

PREFIX = PREFIX.replace("def $hu_phase(S, n) = false -- otherwise", EXTRA_PHASES + "def $hu_phase(S, n) = false -- otherwise")


def issuer_assertions(fixture, path, local):
    bindings = reach_ctor(fixture, path, local) + [
        'S_done_found = $drive_steps(S, 1)', 'S_done_found.COMPLETION = BUDGET',
        'S_done = S_done_found[.COMPLETION = NORMAL]',
        'S_result = S_done[.FRAMES = S.FRAMES]',
        'S_extra_held = S_result[.HELD = [HOBJECT n_exception]]',
        'S_extra_tasks = S_result[.TODO = S_result.TODO ++ [THROW_SEARCH n_exception]]',
        '$ob_object_call_context(S_done) = ((S_native_born, pfunction_helper, pobsourcecall))',
        '$ob_object_native_source(S_native_born) = (OBJECT_CALL_NEW porigin_throw pobctorbirth pobsourcecall)',
    ]
    checks = [
        ('actual completed constructor satisfies the added owner bound', r'S_done.HELD = eps /\ $tasks_nodes(S_done.TODO) = eps /\ S_done.RESULT = KNOWN (POBJECT n_exception) /\ pobctorbirth.OBJECT = n_exception /\ $ob_object_ctor_fact_live(S_done, pobctorbirth)'),
        ('real positive issuer is unchanged from the accepted82 source transition', r'$ctor_completed(S_result, pctorcall, pvalue_message, PINT z_code, PNULL) = S_done /\ $call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done)) /\ $output_state_valid(S_done) /\ $destruction_state_valid(S_done)'),
        ('owned current held values cannot issue helper authority', r'$ctor_completed(S_extra_held, pctorcall, pvalue_message, PINT z_code, PNULL) = S_extra_held'),
        ('owned current continuation refuses despite the same next throw consumer', r'$ob_object_ctor_tail(S_extra_tasks.TODO) = $ob_object_ctor_tail(S_result.TODO) /\ $tasks_nodes(S_extra_tasks.TODO) =/= eps /\ $ctor_completed(S_extra_tasks, pctorcall, pvalue_message, PINT z_code, PNULL) = S_extra_tasks'),
    ]
    return bindings, checks

def assertions(fixture, path, local, stage):
    if stage == 'issuer':
        return issuer_assertions(fixture, path, local)
    if stage in ('transport', 'empty', 'byref'):
        bindings, checks = transport_assertions(fixture, path, local, stage)
        if stage == 'empty':
            checks = [checks[8], checks[9], checks[-1]]
        elif stage == 'byref':
            checks = [checks[8], checks[9]] + checks[11:]
        return bindings, checks
    if stage == 'report':
        return report_assertions(fixture, path, local)
    return clearing_assertions(fixture, path, local, stage)


def render(bindings, checks):
    return (PREFIX + '\ndec $main() : bool*\ndef $main() = [' +
            ', '.join('(' + check + ')' for _, check in checks) + ']\n' +
            ''.join('  -- if ' + binding + '\n' for binding in bindings))


def fingerprint():
    return {name: support.common.sha(ROOT / name) for name in (
        'spec/semantics/30-storage.watsup', 'spec/semantics/456-output-object-returns.watsup',
        'spec/semantics/257-request-destructors.watsup', 'spec/semantics/modules.json',
        'tests/semantics/output_helper_unwind_sources.py', 'tests/semantics/output_helper_unwind_review_state.py',
        'tests/semantics/_build/default/numeric_runner.exe', '_build/default/adapter/main.exe', '.tools/php/bin/php')}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--stage', choices=('transport', 'report', 'helper-catch', 'caller-catch', 'helper-normal', 'caller-normal', 'empty', 'byref', 'issuer'), default='transport')
    parser.add_argument('--native-root', type=Path, help='Frozen source/path reference; never execute the oracle.')
    parser.add_argument('--select', choices=('cv', 'local', 'all'), default='all')
    args = parser.parse_args()
    out = args.output or Path(tempfile.mkdtemp(prefix='output-helper-unwind-review-'))
    out.mkdir(parents=True, exist_ok=True)
    report = {'revision': support.subprocess.check_output(['git', '-C', str(ROOT), 'rev-parse', 'HEAD']).decode().strip(),
              'before': fingerprint(), 'profile': support.common.PROFILE, 'native_agreement_credit': 0,
              'cap_seconds': 300, 'stage': args.stage, 'records': [], 'passed': False}
    directory = out
    try:
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_text())
        for index, (name, source) in enumerate(sources.CASES.items()):
            short = 'local' if index else 'cv'
            if args.select not in ('all', short):
                continue
            directory = out / short
            directory.mkdir()
            source = control_source(source, bool(index), args.stage)
            frozen = args.native_root and args.stage in ('transport', 'report')
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
            bindings, checks = assertions(checked['fixture'], path, bool(index), args.stage)
            fixture = directory / 'state.watsup'
            fixture.write_text(render(bindings, checks))
            record = {'case': name, 'fixture_sha256': support.common.sha(fixture), 'checks': [label for label, _ in checks], 'passed': False}
            report['records'].append(record)
            started = time.monotonic()
            result = support.common.run([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *[str(ROOT / module) for module in modules], str(fixture)], directory, 'state', 300)
            record['seconds'] = round(time.monotonic() - started, 3)
            rendered = result.stdout.decode('ascii')
            values = re.findall(r'\b(?:true|false)\b', rendered)
            record.update(exit_status=result.returncode, results=dict(zip(record['checks'], [value == 'true' for value in values])))
            assert not re.sub(r'true|false|[\[\](),;\s]', '', rendered), rendered
            assert result.returncode == 0 and not result.stderr and values == ['true'] * len(checks), (result.returncode, result.stdout, result.stderr)
            record['passed'] = True
            (directory / 'report.json').write_text(json.dumps(record, indent=2) + '\n')
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
