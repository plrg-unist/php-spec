#!/usr/bin/env python3
"""Reached Stringable ECHO input ownership, output and throwing cleanup."""
import argparse
import base64
import json
import os
from pathlib import Path
import tempfile

import dynamic_property_warning_sources as sources
import magic_property_get_protocol as get

cross, ROOT = sources.cross, sources.ROOT
CASES = {group: 'review-stringable-echo-'+group+'38' for group in
         ('owned', 'borrowed', 'self-drop', 'destructor-throw', 'cast-throw', 'concat-control')}
PREFIX = get.PREFIX.split('dec $get_test_copy', 1)[0] + r'''
dec $echo38_borrowed(pstate) : bool
def $echo38_borrowed(S) = true
  -- if S.TODO = (EMIT z) :: ptask_tail*
  -- if S.ORIGIN = (PORIGIN n_unit pcpath)
  -- if $origin_node(S.SOURCES, PORIGIN n_unit pcpath) = (NExprVariable (BYTES text) metadata_cv)
  -- if $source_emission_cv(S, n_unit, pcpath, NExprVariable (BYTES text) metadata_cv)
  -- if S_read = $quiet_operand(S, S.RESULT)
  -- if S_read.RESULT = KNOWN (POBJECT n)
  -- if $stringable_instance(S_read, n)
def $echo38_borrowed(S) = false -- otherwise
dec $echo38_phase(pstate, nat, nat) : bool
def $echo38_phase(S, 0, n) = ($call_echo_string_plan(S[.COMPLETION = NORMAL]) =/= eps)
def $echo38_phase(S, 1, n) = $echo38_borrowed(S)
def $echo38_phase(S, 2, n) = true
  -- if S.TODO = (STRINGIFY_RESULT n porigin_site z) :: ptask_consumer :: ptask_tail*
  -- if S.CURRENT = eps
def $echo38_phase(S, 3, n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext, S.CURRENT, S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
  -- if pdestructorcall.OPERATION =/= eps
def $echo38_phase(S, 4, n) = true
  -- if S.TODO = (ECHO_CALL_RESULT pechoresult) :: ptask_tail*
  -- if pechoresult.OBJECT = n
  -- if S.CURRENT = eps
def $echo38_phase(S, 5, n) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if S.CURRENT = eps
def $echo38_phase(S, 6, n) = true
  -- if S.TODO = (EMIT z) :: ptask_tail*
  -- if S.RESULT = KNOWN pvalue_text
  -- if $string_bytes(pvalue_text) =/= eps
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $echo38_phase(S, 7, n) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.DESTRUCTION.OPERATIONS = eps
def $echo38_phase(S, 9, n) = true
  -- if S.TODO = (STRINGIFY_RESULT n_receiver porigin_site z) :: (CONCAT_AFTER_RIGHT porigin_parent pvalue_left z) :: ptask_tail*
  -- if S.CURRENT = eps
def $echo38_phase(S, n_phase, n) = false -- otherwise
dec $echo38_seek(pstate, nat, nat, nat) : pstate
def $echo38_seek(S, n_phase, n_receiver, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $echo38_seek(S, n_phase, n_receiver, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $echo38_phase(S, n_phase, n_receiver) \/ n = 0
def $echo38_seek(S, n_phase, n_receiver, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$echo38_phase(S, n_phase, n_receiver) /\ $(n > 0)
  -- if S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps
def $echo38_seek(S, n_phase, n_receiver, n) = $echo38_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_phase, n_receiver, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$echo38_phase(S, n_phase, n_receiver) /\ $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
dec $echo38_exit_source(pstate, ptask) : bool
def $echo38_exit_source(S, ptask_source) = true
  -- if S.TODO = (DESTRUCTOR_OPERATION_EXIT pdestructionoperation) :: ptask_tail*
  -- if S.CURRENT = eps
  -- if pdestructionoperation.SOURCE = ptask_source
def $echo38_exit_source(S, ptask_source) = false -- otherwise
dec $echo38_seek_exit(pstate, ptask, nat) : pstate
def $echo38_seek_exit(S, ptask_source, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
def $echo38_seek_exit(S, ptask_source, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $echo38_exit_source(S, ptask_source) \/ n = 0 \/ (S.TODO = eps /\ S.CURRENT = eps /\ S.FRAMES = eps)
def $echo38_seek_exit(S, ptask_source, n) = $echo38_seek_exit($drive_steps(S[.COMPLETION = NORMAL], 1), ptask_source, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$echo38_exit_source(S, ptask_source) /\ $(n > 0)
  -- if S.TODO =/= eps \/ S.CURRENT =/= eps \/ S.FRAMES =/= eps
'''


def seek(parent, state, phase, receiver='n_receiver'):
    return [f'{state}_found = $echo38_seek({parent}, {phase}, {receiver}, 2048)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = {state}_found[.COMPLETION = NORMAL]',
        f'$echo38_phase({state}, {phase}, {receiver})', *get.valid(state)]


def output(state, text):
    return '$get_test_output('+state+'.EVENTS) = '+cross.invoke.byte_expr(text.encode())


def before(parent, label, owned):
    state, receiver = 'S_'+label+'_before', 'n_'+label+'_receiver'
    site, line, tail = 'porigin_'+label, 'z_'+label, 'ptask_'+label+'_tail*'
    clauses = [*seek(parent, state, 0 if owned else 1, '0'),
        f'{state}.TODO = (EMIT {line}) :: {tail}', f'{state}.ORIGIN = ({site})',
        f'{state}_read = $quiet_operand({state}, {state}.RESULT)',
        f'{state}_read.RESULT = KNOWN (POBJECT {receiver})',
        f'$stringable_instance({state}, {receiver})',
        f'$stringify_source({state}, {site}, {line}, EMIT {line})',
        f'$heap_owners($heap_graph({state}), HOBJECT {receiver}) = 1']
    if owned:
        record = 'pechoresult_'+label
        clauses += [f'{state}_found.COMPLETION = BUDGET',
            f'$call_echo_string_plan({state}) = ({record})',
            f'{record} = {{TEMP KNOWN (POBJECT {receiver}), OBJECT {receiver}, SITE {site}, LINE {line}, TAIL {tail}}}',
            f'$echo_new_class({state}, {site}, {line}) = (porigin_{label}_class)',
            f'{state}.OBJECTS[{receiver}] = INSTANCE porigin_{label}_class',
            f'$echo_call_result_source({state}, {record})',
            f'$echo_call_temporary_valid({state}, {record})',
            f'$call_echo_string_plan({state}[.RESULT = VARIABLE ($ptascii("reader")) {line}]) = eps',
            f'~$echo_call_result_source({state}, {record}[.TEMP = REFERENCE 0])',
            f'~$echo_call_temporary_valid({state}, {record}[.OBJECT = |{state}.OBJECTS|][.TEMP = KNOWN (POBJECT (|{state}.OBJECTS|))])',
            f'~$echo_call_site_valid({state}, {site}, $({line} + 1))',
            f'$task_nodes(ECHO_CALL_RESULT {record}) = [HOBJECT {receiver}]']
    else:
        clauses += [f'$call_echo_string_plan({state}) = eps',
            f'$echo_new_class({state}, {site}, {line}) = eps',
            f'{state}.RESULT = VARIABLE ($ptascii("reader")) z_{label}_cv',
            f'$trace_slot({state}, {state}.ENV, $ptascii("reader")) = POBJECT {receiver}']
    clauses += [*get.step(state, 'S_'+label+'_pending'),
        f'S_{label}_pending.TODO = (CALL_ARGS (METHOD_TARGET {receiver} porigin_{label}_method) eps 0 eps ({site}) {line}) :: (STRINGIFY_RESULT {receiver} {site} {line}) :: ptask_{label}_consumer :: {tail}',
        f'ptask_{label}_consumer = '+(f'ECHO_CALL_RESULT pechoresult_{label}' if owned else f'EMIT {line}'),
        f'$stringify_pending(S_{label}_pending, METHOD_TARGET {receiver} porigin_{label}_method, {site})',
        f'$task_nodes(STRINGIFY_RESULT {receiver} {site} {line}) = [HOBJECT {receiver}]',
        f'$heap_owners($heap_graph(S_{label}_pending), HOBJECT {receiver}) = 3']
    return clauses


def returned(parent, label, text, owners):
    state, receiver = 'S_'+label+'_cast', 'n_'+label+'_receiver'
    site, line, tail = 'porigin_'+label, 'z_'+label, 'ptask_'+label+'_tail*'
    value = 'pvalue_'+label+'_text'
    return [*seek(parent, state, 2, receiver),
        f'{state}.TODO = (STRINGIFY_RESULT {receiver} {site} {line}) :: ptask_{label}_consumer :: {tail}',
        f'$stringify_result_valid({state}, {receiver}, {site}, {line})',
        f'{state}.RESULT = KNOWN {value}',
        f'{value} = PSTRING_CARRIER (REQUEST_STRING n_{label}_identity) n_{label}_bytes*',
        f'n_{label}_bytes* = '+cross.invoke.byte_expr(text.encode()),
        f'$string_carrier_valid({state}, {value})',
        f'$heap_owners($heap_graph({state}), HOBJECT {receiver}) = {owners}',
        f'{state}_expected = {state}[.TODO = ptask_{label}_consumer :: {tail}][.BASE = BASE_VALUE (KNOWN {value})]',
        f'PhpStep: {state} ~> {state}_raw', f'{state}_raw = {state}_expected',
        *get.step(state, 'S_'+label+'_released')]


def emit(state, label, task, text):
    tail, value, line = 'ptask_'+label+'_emit_tail*', 'pvalue_'+label+'_emit', 'z_'+label
    return [f'{state}.TODO = ({task}) :: {tail}', f'{state}.RESULT = KNOWN {value}',
        f'n_{label}_emit_bytes* = '+cross.invoke.byte_expr(text.encode()),
        f'$string_bytes({value}) = (n_{label}_emit_bytes*)',
        f'$string_carrier_valid({state}, {value})',
        f'{state}_paused = $drive_steps({state}, 0)', f'{state}_paused = {state}[.COMPLETION = BUDGET]',
        f'{state}_expected = {state}[.TODO = {tail}][.EVENTS = {state}.EVENTS ++ [OUTPUT n_{label}_emit_bytes*]][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]',
        f'PhpStep: {state} ~> {state}_raw', f'{state}_raw = {state}_expected',
        *get.step(state, state+'_after')]


def destructor(parent, label, source, prefix, pending=False):
    state, receiver = 'S_'+label+'_dtor', 'n_'+label+'_receiver'
    operation, call = 'pdestructionoperation_'+label, 'pdestructorcall_'+label
    clauses = [*seek(parent, state, 3, receiver),
        f'{state}.CURRENT = (pcallcontext_{label}_dtor)',
        f'$destructor_context_call(pcallcontext_{label}_dtor, {state}.CURRENT, {state}.FRAMES) = ({call})',
        f'{call}.OBJECT = {receiver}', f'{call}.OPERATION = ({operation})',
        f'{operation}.SOURCE = {source}', f'$destructor_operation_live({state}, {operation})',
        output(state, prefix)]
    if pending:
        clauses += [f'{operation}.PENDING = (n_{label}_prior)',
            f'$string_bytes($throwable_field({state}, n_{label}_prior, "message")) = ($ptascii("cast38"))']
    else:
        clauses += [f'{operation}.PENDING = eps']
    return clauses


def operation_exit(parent, label, exact_source=False):
    state, operation = 'S_'+label+'_exit', 'pdestructionoperation_'+label+'_exit'
    found = seek(parent, state, 5, 'n_'+label+'_receiver')
    if exact_source:
        source = 'pdestructionoperation_'+label+'.SOURCE'
        found = [f'{state}_found = $echo38_seek_exit({parent}, {source}, 2048)',
            fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$echo38_exit_source({state}, {source})', *get.valid(state)]
    return [*found,
        f'{state}.TODO = (DESTRUCTOR_OPERATION_EXIT {operation}) :: ptask_{label}_exit_tail*',
        f'{state}.DESTRUCTION.OPERATIONS = {operation} :: pdestructionoperation_{label}_tail*',
        f'$destructor_operation_valid({state}, {operation})',
        f'~((HOBJECT n_{label}_receiver) <- {state}.ALLOCATIONS)',
        f'S_{label}_exit_cleanup = $eager_cleanup_finish({state}, {operation})',
        f'S_{label}_exit_cleanup = {state}']


def pending_checks():
    state, operation = 'S_throw_exit', 'pdestructionoperation_throw_exit'
    args = 'n_throw_pending, (EMIT z_throw) :: ptask_throw_tail*'
    checks = []
    for name, update in (
            ('line', '.SOURCE = STRINGIFY_RESULT n_throw_receiver porigin_throw $(z_throw + 1)'),
            ('origin', '.ORIGIN = eps'), ('caller', '.CALLER = (pcallcontext_throw_dtor)'),
            ('value', '.VALUE = KNOWN (PINT 1)'), ('base', '.BASE = BASE_VALUE (KNOWN PNULL)'),
            ('completion', '.COMPLETION = THROWING n_throw_pending')):
        checks += [f'pdestructionoperation_bad_{name} = {operation}[{update}]',
            f'$destructor_pending_finish({state}, pdestructionoperation_bad_{name}, {args}) = {state}[.TODO = (THROW_SEARCH n_throw_pending) :: (EMIT z_throw) :: ptask_throw_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = NORMAL]']
    checks += [f'$destructor_pending_finish({state}, {operation}, n_throw_pending, (EMIT $(z_throw + 1)) :: ptask_throw_tail*) = {state}[.TODO = (THROW_SEARCH n_throw_pending) :: (EMIT $(z_throw + 1)) :: ptask_throw_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = NORMAL]',
        f'$destructor_pending_finish({state}, {operation}, |{state}.OBJECTS|, (EMIT z_throw) :: ptask_throw_tail*) = {state}[.TODO = (THROW_SEARCH (|{state}.OBJECTS|)) :: (EMIT z_throw) :: ptask_throw_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = NORMAL]']
    checks += [f'pdestructionoperation_plain = {operation}[.VALUE = KNOWN (PSTRING n_throw_bytes*)][.BASE = BASE_VALUE (KNOWN (PSTRING n_throw_bytes*))]',
        f'$destructor_pending_finish({state}, pdestructionoperation_plain, {args}) = {state}[.TODO = (EMIT z_throw) :: (THROW_SEARCH n_throw_pending) :: ptask_throw_tail*][.RESULT = pdestructionoperation_plain.VALUE][.BASE = pdestructionoperation_plain.BASE][.CELL = pdestructionoperation_plain.CELL][.KEY = pdestructionoperation_plain.KEY][.LOCATION = pdestructionoperation_plain.LOCATION][.COMPLETION = NORMAL]',
        f'pvalue_bad_carrier = PSTRING_CARRIER (REQUEST_STRING (|{state}.STRINGDATA|)) n_throw_bytes*',
        f'~$string_carrier_valid({state}, pvalue_bad_carrier)',
        f'pdestructionoperation_bad_carrier = {operation}[.VALUE = KNOWN pvalue_bad_carrier][.BASE = BASE_VALUE (KNOWN pvalue_bad_carrier)]',
        f'$destructor_pending_finish({state}, pdestructionoperation_bad_carrier, {args}) = {state}[.TODO = (THROW_SEARCH n_throw_pending) :: (EMIT z_throw) :: ptask_throw_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)][.COMPLETION = NORMAL]']
    return checks


def body(run, source, expected, group):
    clauses = ['S_initial = '+run, '~S_initial.COMPILESTOP']
    if group == 'concat-control':
        clauses += [*seek('S_initial', 'S_concat_cast', 9, '0'),
            'S_concat_cast.TODO = (STRINGIFY_RESULT n_concat_receiver porigin_concat z_concat) :: (CONCAT_AFTER_RIGHT porigin_concat_parent pvalue_concat_left z_concat) :: ptask_concat_tail*',
            '$echo_new_class(S_concat_cast, porigin_concat, z_concat) = eps',
            '~$echo_call_site_valid(S_concat_cast, porigin_concat, z_concat)',
            '$stringify_result_valid(S_concat_cast, n_concat_receiver, porigin_concat, z_concat)',
            '$heap_owners($heap_graph(S_concat_cast), HOBJECT n_concat_receiver) = 1',
            *get.step('S_concat_cast', 'S_concat_release'),
            *destructor('S_concat_release', 'concat', 'STRINGIFY_RESULT n_concat_receiver porigin_concat z_concat', 'T|'),
            *operation_exit('S_concat_dtor', 'concat', True), output('S_concat_exit', 'T|D|'),
            'pdestructionoperation_concat_exit.VALUE = KNOWN pvalue_concat_text',
            '$string_bytes(pvalue_concat_text) = ($ptascii("S1"))',
            'ptask_concat_exit_tail* = (CONCAT_AFTER_RIGHT porigin_concat_parent pvalue_concat_left z_concat) :: ptask_concat_tail*',
            *get.finish('S_concat_exit', expected)]
        return clauses
    owned = group in ('owned', 'destructor-throw', 'cast-throw')
    label = 'normal'
    clauses += before('S_initial', label, owned)
    if group == 'cast-throw':
        clauses += [*destructor('S_normal_pending', label, 'ptask_normal_cleanup', 'direct|T|', True),
            *operation_exit('S_normal_dtor', label, True), output('S_normal_exit', 'direct|T|D|'),
            'pdestructionoperation_normal_exit.PENDING = (n_cleanup)',
            '$string_bytes($throwable_field(S_normal_exit, n_cleanup, "message")) = ($ptascii("cleanup38"))',
            '$throwable_previous_id(S_normal_exit, n_cleanup) = (n_normal_prior)',
            'pdestructionoperation_normal_exit.VALUE = KNOWN PNULL',
            *seek('S_normal_exit', 'S_error', 7, 'n_normal_receiver'),
            'S_error.TODO = (THROW_SEARCH n_cleanup) :: ptask_error_tail*',
            *get.finish('S_error', expected)]
        return clauses
    text = 'B1' if group == 'borrowed' else 'V1' if group == 'self-drop' else 'S1'
    clauses += returned('S_normal_pending', label, text, 1 if group == 'self-drop' else 2)
    if owned:
        clauses += [*seek('S_normal_released', 'S_emit', 4, 'n_normal_receiver'),
            '$echo_call_result_valid(S_emit, pechoresult_normal)',
            '$heap_owners($heap_graph(S_emit), HOBJECT n_normal_receiver) = 1',
            output('S_emit', 'direct|T|'), *emit('S_emit', label, 'ECHO_CALL_RESULT pechoresult_normal', text),
            # Constructed byte-string completion on the same authentic owner/site.
            'S_plain = S_emit[.RESULT = KNOWN (PSTRING n_normal_emit_bytes*)][.BASE = BASE_VALUE (KNOWN (PSTRING n_normal_emit_bytes*))]',
            '$echo_call_result_valid(S_plain, pechoresult_normal)',
            'PhpStep: S_plain ~> S_plain_raw', 'S_plain_raw = S_emit_expected',
            *destructor('S_emit_after', label, 'ECHO_CALL_RESULT pechoresult_normal', 'direct|T|S1'),
            'pdestructionoperation_normal.VALUE = KNOWN PNULL',
            'pdestructionoperation_normal.BASE = BASE_VALUE (KNOWN PNULL)',
            *operation_exit('S_normal_dtor', label, group == 'destructor-throw'), output('S_normal_exit', 'direct|T|S1D|')]
        if group == 'destructor-throw':
            clauses += ['pdestructionoperation_normal_exit.PENDING = (n_owned_error)',
                '$string_bytes($throwable_field(S_normal_exit, n_owned_error, "message")) = ($ptascii("owned-dtor38"))',
                '$throwable_previous_id(S_normal_exit, n_owned_error) = eps',
                *seek('S_normal_exit', 'S_error', 7, 'n_normal_receiver'),
                'S_error.TODO = (THROW_SEARCH n_owned_error) :: ptask_error_tail*',
                output('S_error', 'direct|T|S1D|'), *get.finish('S_error', expected)]
        else:
            clauses += get.finish('S_normal_exit', expected)
    elif group == 'borrowed':
        clauses += [*seek('S_normal_released', 'S_emit', 6, 'n_normal_receiver'),
            '$trace_slot(S_emit, S_emit.ENV, $ptascii("reader")) = POBJECT n_normal_receiver',
            '$heap_owners($heap_graph(S_emit), HOBJECT n_normal_receiver) = 1',
            'S_emit.DESTRUCTION.OPERATIONS = eps', output('S_emit', 'borrowed|T|'),
            *emit('S_emit', label, 'EMIT z_normal', text),
            output('S_emit_after', 'borrowed|T|B1'),
            '$trace_slot(S_emit_after, S_emit_after.ENV, $ptascii("drops")) = PINT 0',
            *get.finish('S_emit_after', expected)]
    else:
        clauses += ['$trace_slot(S_normal_cast, S_normal_cast.ENV, $ptascii("reader")) = PNULL',
            *destructor('S_normal_released', label, 'STRINGIFY_RESULT n_normal_receiver porigin_normal z_normal', 'normal|T|'),
            *operation_exit('S_normal_dtor', label, True), output('S_normal_exit', 'normal|T|D|'),
            'pdestructionoperation_normal_exit.PENDING = eps',
            'pdestructionoperation_normal_exit.VALUE = KNOWN pvalue_normal_text',
            *seek('S_normal_exit', 'S_emit', 6, 'n_normal_receiver'),
            *emit('S_emit', label, 'EMIT z_normal', text), output('S_emit_after', 'normal|T|D|V1'),
            *before('S_emit_after', 'throw', False),
            *returned('S_throw_pending', 'throw', 'V2', 1),
            '$trace_slot(S_throw_cast, S_throw_cast.ENV, $ptascii("reader")) = PNULL',
            *destructor('S_throw_released', 'throw', 'STRINGIFY_RESULT n_throw_receiver porigin_throw z_throw', 'normal|T|D|V1|gone|1/1|throwing|T|'),
            *operation_exit('S_throw_dtor', 'throw', True),
            output('S_throw_exit', 'normal|T|D|V1|gone|1/1|throwing|T|D|'),
            'pdestructionoperation_throw_exit.SOURCE = STRINGIFY_RESULT n_throw_receiver porigin_throw z_throw',
            'pdestructionoperation_throw_exit.VALUE = KNOWN pvalue_throw_text',
            'pdestructionoperation_throw_exit.BASE = BASE_VALUE (KNOWN pvalue_throw_text)',
            'pdestructionoperation_throw_exit.COMPLETION = NORMAL',
            'pdestructionoperation_throw_exit.PENDING = (n_throw_pending)',
            'ptask_throw_exit_tail* = (EMIT z_throw) :: ptask_throw_tail*',
            '$string_bytes($throwable_field(S_throw_exit, n_throw_pending, "message")) = ($ptascii("borrowed-dtor38"))',
            '$throwable_previous_id(S_throw_exit, n_throw_pending) = eps',
            'S_throw_exit_paused = $drive_steps(S_throw_exit, 0)',
            'S_throw_exit_paused = S_throw_exit[.COMPLETION = BUDGET]',
            'S_throw_exit_expected = S_throw_exit[.DESTRUCTION.OPERATIONS = pdestructionoperation_throw_tail*][.TODO = (EMIT z_throw) :: (THROW_SEARCH n_throw_pending) :: ptask_throw_tail*][.RESULT = pdestructionoperation_throw_exit.VALUE][.BASE = pdestructionoperation_throw_exit.BASE][.CELL = pdestructionoperation_throw_exit.CELL][.KEY = pdestructionoperation_throw_exit.KEY][.LOCATION = pdestructionoperation_throw_exit.LOCATION][.COMPLETION = NORMAL]',
            'PhpStep: S_throw_exit ~> S_throw_exit_raw', 'S_throw_exit_raw = S_throw_exit_expected',
            *get.step('S_throw_exit', 'S_throw_emit'), 'S_throw_emit = S_throw_exit_expected',
            '(HOBJECT n_throw_pending) <- $machine_roots(S_throw_emit)',
            *pending_checks(), *emit('S_throw_emit', 'throw', 'EMIT z_throw', 'V2'),
            'S_throw_emit_after.TODO = (THROW_SEARCH n_throw_pending) :: ptask_throw_tail*',
            output('S_throw_emit_after', 'normal|T|D|V1|gone|1/1|throwing|T|D|V2'),
            *get.finish('S_throw_emit_after', expected)]
    clauses += ['$trace_slot(S_done, S_done.ENV, $ptascii("casts")) = PINT '+('2' if group == 'self-drop' else '1'),
        '$trace_slot(S_done, S_done.ENV, $ptascii("drops")) = PINT '+('2' if group == 'self-drop' else '1')]
    return clauses


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=list(CASES), required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    before_cut = cross.snapshot(None)
    out = Path(tempfile.mkdtemp(prefix='stringable-echo-state38-', dir=ROOT/'.tools'))
    report = {'before': before_cut, 'profile': cross.invoke.types.PROFILE, 'passed': False,
        'native_evaluations': 0, 'model_evaluations': 0, 'state_assertions_evaluated': 0,
        'runner_mode': 'SL', 'numeric_cap_seconds': 120, 'case': CASES[args.group], 'jobs': 1}
    print(out, flush=True)
    try:
        original = sources.CASES[CASES[args.group]]
        source = out/'source.php'; source.write_bytes(original)
        sources.prepare(out, source)
        run = '$php_run(program_source,0,'+json.dumps(base64.b64encode(os.fsencode(source)).decode())+')'
        clauses = ['program_source = '+(out/'program.watsup').read_text().strip(),
            *body(run, original, sources.EXPECTED[CASES[args.group]], args.group)]
        fixture = out/'protocol.watsup'
        fixture.write_text(PREFIX+'dec $body() : bool\ndef $body() = true\n'+
            ''.join('  -- '+('' if clause.startswith('PhpStep:') else 'if ')+clause+'\n' for clause in clauses)+'\ndec $main() : bool\ndef $main() = $body()\n')
        (out/'assertions.json').write_text(json.dumps(clauses, indent=2)+'\n')
        report.update(state_assertions=len(clauses), source_sha256=cross.invoke.sha(source),
            fixture_sha256=cross.invoke.sha(fixture), helper_sha256=cross.invoke.sha(Path(__file__)))
        if not args.prepare_only:
            runner = ROOT/'tests/semantics/_build/default/numeric_runner.exe'
            report['numeric_runner_sha256'] = cross.invoke.sha(runner)
            assert report['numeric_runner_sha256'] == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
            result = cross.invoke.process([str(runner), '--sl', *[str(ROOT/module) for module in before_cut['ordered_modules']], str(fixture)], out/'numeric', 120, ROOT)
            assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
            report['state_assertions_evaluated'] = len(clauses)
        assert source.read_bytes() == original and cross.snapshot(None) == before_cut
        report['passed'] = True
    except BaseException as error:
        report['failure'] = {'type': type(error).__name__, 'message': str(error)}
        raise
    finally:
        report['after'] = cross.snapshot(None)
        (out/'report.json').write_text(json.dumps(report, indent=2)+'\n')
        print(out/'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
