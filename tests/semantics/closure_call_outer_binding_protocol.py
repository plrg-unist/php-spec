#!/usr/bin/env python3
"""Outer fixed-formal capture, missing receiver and early duplicate priority."""
from pathlib import Path

import closure_call_argument_list_protocol as reuse
import closure_call_outer_binding_sources as sources

base, old = reuse.base, reuse.old
define, packet, common = base.define, base.packet, base.common
ROOT, text, term = base.ROOT, base.text, base.term
PREFIX, reach = reuse.PREFIX, reuse.reach
settle, budget = old.settle, old.budget


def lines(name):
    return [n for n, line in enumerate(sources.family.CASES[name].splitlines(), 1)
            if b'->call(' in line]


def normal(initial, stdout):
    first_line, second_line = lines(sources.NORMAL)
    extras_output = b'B|E|calleeHeld|'
    positional_output = extras_output + b'P|calleeHeld|receiverHeld|'
    first_done = positional_output + b'BODY|17|7|29|received|R|36|2|1|99|currentNull|calleeGone|receiverGone|'
    named_output = first_done + b'N|calleeHeld|receiverHeld|'
    value_output = named_output + b'V|'
    assert stdout == value_output + b'BODY2|17|7|29|R2|36|2|1|99|replacement|currentNull|calleeGone|receiverGone|A|'
    values = [*initial, *reach('S_capture', 'S_initial', 0, first_line),
        'S_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_capture) :: ptask_capture*',
        'n_source = pclosurecall_capture.SOURCE',
        'pclosurecall_capture.INDEX = 0', 'pclosurecall_capture.FIRST = eps',
        'pclosurecall_capture.RECEIVER = eps', 'pclosurecall_capture.PACKS = eps',
        '$closure_call_array_pack_site(S_capture,pclosurecall_capture.SITE)',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in
          ['call', 'receiver', 'extras', 'positionals', 'effects', 'bodies', 'result']],
        'S_capture.STORE[n_call_cv] = DEFINED (POBJECT n_source)',
        'S_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_receiver)',
        'S_capture.STORE[n_extras_cv] = DEFINED (PARRAY n_extras)',
        'S_capture.STORE[n_positionals_cv] = DEFINED (PARRAY n_positionals)',
        *reach('S_extras', 'S_capture', 1, first_line, 0),
        'S_extras.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_extras (KNOWN (PARRAY n_extras)) 0) :: ptask_extras*',
        'pclosurecall_extras.FIRST = eps', 'pclosurecall_extras.RECEIVER = eps',
        'pclosurecall_extras.PACKS = [pconfigpack_extras]',
        'pconfigpack_extras.INDEX = 0',
        'pconfigpack_extras.ITEMS = [ENTRY (KSTRING $ptascii("second")) (DIRECT (PINT 29))]',
        'S_extras.STORE[n_call_cv] = DEFINED PNULL',
        'S_extras.STORE[n_extras_cv] = DEFINED (PARRAY n_extras_current)',
        'n_extras_current =/= n_extras',
        'S_extras.ARRAYS[n_extras_current].ITEMS = [ENTRY (KSTRING $ptascii("second")) (DIRECT (PINT 99))]',
        '$test_outputs(S_extras.EVENTS) = ' + term(extras_output),
        *reach('S_between_pending', 'S_extras', 0, first_line, 1),
        *settle('S_between', 'S_between_pending'),
        'S_between.TODO = (CLOSURE_CALL_ARGS pclosurecall_between) :: ptask_between*',
        'pclosurecall_between.FIRST = eps', 'pclosurecall_between.RECEIVER = eps',
        'pclosurecall_between.RAW = [(KSTRING $ptascii("second"),KNOWN (PINT 29))]',
        'pclosurecall_between.SENT = {SLOTS ([NAMED_HOLE,(NAMED_SENT (KNOWN (PINT 29)))]),NAMED eps}',
        'pclosurecall_between.ERROR = eps',
        '~(HARRAY n_extras <- S_between.ALLOCATIONS)',
        *budget('S_between'),
        *reach('S_positional', 'S_between', 1, first_line, 1),
        'S_positional.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_positional (KNOWN (PARRAY n_positionals)) 0) :: ptask_positional*',
        'pclosurecall_positional.PACKS = [pconfigpack_extras,pconfigpack_positionals]',
        'pconfigpack_positionals.INDEX = 1',
        'pconfigpack_positionals.ITEMS = [ENTRY (KINT 9) (DIRECT (POBJECT n_receiver)),ENTRY (KINT 13) (DIRECT pvalue_first)]',
        '$string_plain(pvalue_first) = PSTRING $ptascii("7")',
        'pclosurecall_positional.FIRST = eps',
        '$closure_call_needs_first(pclosurecall_positional,KINT 9)',
        'S_positional.STORE[n_receiver_cv] = DEFINED PNULL',
        'S_positional.STORE[n_positionals_cv] = DEFINED PNULL',
        '$test_outputs(S_positional.EVENTS) = ' + term(positional_output),
        'S_received_found = $drive_steps(S_positional,1)',
        r'S_received_found.COMPLETION = NORMAL \/ S_received_found.COMPLETION = BUDGET',
        'S_received = $test_running(S_received_found)', *common.public('S_received'),
        'S_received.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_received (KNOWN (PARRAY n_positionals)) 1) :: ptask_received*',
        'pclosurecall_received.FIRST = (POBJECT n_receiver)',
        'pclosurecall_received.RECEIVER = (n_receiver)',
        'pclosurecall_received.RAW = pclosurecall_between.RAW',
        'pclosurecall_received.SENT = pclosurecall_between.SENT',
        '~$closure_call_needs_first(pclosurecall_received,KINT 13)',
        *reach('S_invoke_pending', 'S_received', 3, first_line),
        *settle('S_invoke', 'S_invoke_pending'),
        'S_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_invoke*',
        'pclosurecall.SOURCE = n_source', 'pclosurecall.INDEX = 2',
        'pclosurecall.FIRST = (POBJECT n_receiver)', 'pclosurecall.RECEIVER = (n_receiver)',
        'pclosurecall.PACKS = [pconfigpack_extras,pconfigpack_positionals]',
        'pclosurecall.RAW = [(KINT 1,KNOWN pvalue_first),(KSTRING $ptascii("second"),KNOWN (PINT 29))]',
        'pclosurecall.SENT = {SLOTS ([(NAMED_SENT (KNOWN pvalue_first)),(NAMED_SENT (KNOWN (PINT 29)))]),NAMED eps}',
        'pclosurecall.ERROR = eps',
        '~(HARRAY n_positionals <- S_invoke.ALLOCATIONS)',
        '~(HARRAY n_extras <- S_invoke.ALLOCATIONS)',
        '(HOBJECT n_source) <- S_invoke.ALLOCATIONS',
        '(HOBJECT n_receiver) <- S_invoke.ALLOCATIONS',
        *budget('S_invoke')]
    for change in ['.FIRST = eps', '.RECEIVER = eps', '.FIRST = (PINT 17)',
                   '.PACKS = eps', '.PACKS = [pconfigpack_positionals,pconfigpack_extras]',
                   '.INDEX = 1', '.RAW = [(KINT 0,KNOWN pvalue_first),(KSTRING $ptascii("second"),KNOWN (PINT 29))]']:
        values += [f'~$call_task_valid(S_invoke,CLOSURE_CALL_INVOKE pclosurecall[{change}])']
    values += [
        'S_history = S_invoke[.ARRAYS[n_positionals].ITEMS = [ENTRY (KINT 9) (DIRECT (PINT 99)),ENTRY (KINT 13) (DIRECT (PINT 88))]]',
        '$call_task_valid(S_history,CLOSURE_CALL_INVOKE pclosurecall)',
        *body('S_body', 'S_invoke', first_line, 'n_source', 'n_receiver', 'pclosurecall.RAW', False),
        *reach('S_named_capture', 'S_body', 0, second_line),
        'S_named_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_named_capture) :: ptask_named_capture*',
        'n_named_source = pclosurecall_named_capture.SOURCE', 'n_named_source =/= n_source',
        'S_named_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_named_receiver)',
        '$lookup(S_named_capture.ENV,$ptascii("named")) = (n_named_cv)',
        '$lookup(S_named_capture.ENV,$ptascii("values")) = (n_values_cv)',
        '$lookup(S_named_capture.ENV,$ptascii("other")) = (n_other_cv)',
        'S_named_capture.STORE[n_named_cv] = DEFINED (PARRAY n_named_pack)',
        'S_named_capture.STORE[n_values_cv] = DEFINED (PARRAY n_values_pack)',
        'S_named_capture.STORE[n_other_cv] = DEFINED (POBJECT n_other)',
        '~(HOBJECT n_source <- S_named_capture.ALLOCATIONS)',
        '~(HOBJECT n_receiver <- S_named_capture.ALLOCATIONS)',
        '$test_outputs(S_named_capture.EVENTS) = ' + term(first_done),
        *reach('S_named', 'S_named_capture', 1, second_line, 0),
        'S_named.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_named (KNOWN (PARRAY n_named_pack)) 0) :: ptask_named*',
        'pclosurecall_named.FIRST = eps', 'pclosurecall_named.PACKS = [pconfigpack_named]',
        'pconfigpack_named.INDEX = 0',
        'pconfigpack_named.ITEMS = [ENTRY (KSTRING $ptascii("newThis")) (DIRECT (POBJECT n_named_receiver)),ENTRY (KSTRING $ptascii("second")) (DIRECT (PINT 29))]',
        'S_named.STORE[n_named_cv] = DEFINED (PARRAY n_named_current)',
        'n_named_current =/= n_named_pack',
        'S_named.ARRAYS[n_named_current].ITEMS = [ENTRY (KSTRING $ptascii("newThis")) (DIRECT (POBJECT n_other)),ENTRY (KSTRING $ptascii("second")) (DIRECT (PINT 99))]',
        'S_named.STORE[n_receiver_cv] = DEFINED PNULL',
        '$test_outputs(S_named.EVENTS) = ' + term(named_output),
        *reach('S_values', 'S_named', 1, second_line, 1),
        'S_values.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_values (KNOWN (PARRAY n_values_pack)) 0) :: ptask_values*',
        'pclosurecall_values.FIRST = (POBJECT n_named_receiver)',
        'pclosurecall_values.RECEIVER = (n_named_receiver)',
        'pclosurecall_values.PACKS = [pconfigpack_named,pconfigpack_values]',
        'pconfigpack_values.INDEX = 1',
        'pconfigpack_values.ITEMS = [ENTRY (KINT 21) (DIRECT pvalue_first)]',
        'pclosurecall_values.RAW = [(KSTRING $ptascii("second"),KNOWN (PINT 29))]',
        '~$closure_call_needs_first(pclosurecall_values,KINT 21)',
        '$test_outputs(S_values.EVENTS) = ' + term(value_output),
        *reach('S_named_invoke_pending', 'S_values', 3, second_line),
        *settle('S_named_invoke', 'S_named_invoke_pending'),
        'S_named_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall_named_complete) :: ptask_named_complete*',
        'pclosurecall_named_complete.FIRST = (POBJECT n_named_receiver)',
        'pclosurecall_named_complete.RECEIVER = (n_named_receiver)',
        'pclosurecall_named_complete.RAW = pclosurecall.RAW',
        'pclosurecall_named_complete.SENT = pclosurecall.SENT',
        'pclosurecall_named_complete.ERROR = eps',
        '~(HARRAY n_named_pack <- S_named_invoke.ALLOCATIONS)',
        '~(HARRAY n_values_pack <- S_named_invoke.ALLOCATIONS)',
        '~$call_task_valid(S_named_invoke,CLOSURE_CALL_INVOKE pclosurecall_named_complete[.FIRST = (POBJECT n_other)][.RECEIVER = (n_other)])',
        *budget('S_named_invoke'),
        *body('S_named_body', 'S_named_invoke', second_line, 'n_named_source', 'n_named_receiver', 'pclosurecall_named_complete.RAW', False),
        *define.finish('S_named_body', stdout)]
    for node in ['HOBJECT n_source', 'HOBJECT n_receiver', 'HOBJECT n_named_source',
                 'HOBJECT n_named_receiver', 'HOBJECT n_other', 'HARRAY n_extras',
                 'HARRAY n_extras_current', 'HARRAY n_positionals', 'HARRAY n_named_pack',
                 'HARRAY n_named_current', 'HARRAY n_values_pack']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


def body(state, start, line, source, receiver, raw, default):
    return [*reach(state, start, 4, line),
        f'{state}.CURRENT = (pcallcontext_{state})',
        f'pcallcontext_{state}.TARGET = CLOSURE_CALL_TARGET {source} {receiver}',
        f'pcallcontext_{state}.ARGC = 2',
        f'pcallcontext_{state}.HOLES = ' + ('[0]' if default else 'eps'),
        f'pcallcontext_{state}.WRAPPER = ($closure_call_wrapper({raw}))',
        f'$lookup({state}.ENV,$ptascii("first")) = (n_first_{state})',
        f'$lookup({state}.ENV,$ptascii("second")) = (n_second_{state})',
        f'{state}.STORE[n_first_{state}] = DEFINED (PINT {11 if default else 7})',
        f'{state}.STORE[n_second_{state}] = DEFINED (PINT 29)',
        f'{state}.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        f'$wrapper_context_valid({state},pcallcontext_{state})']


def priority(initial, stdout):
    late_line, missing_line, duplicate_line = lines(sources.PRIORITY)
    duplicate = 'Named parameter $newThis overwrites previous argument'
    missing = 'Closure::call() expects at least 1 argument, 0 given'
    before_body = b'B|P|L|calleeHeld|receiverHeld|'
    normal_done = before_body + b'BODY|23|11|29|R|40|2|1|calleeGone|receiverGone|'
    missing_output = normal_done + b'P|'
    missing_caught = missing_output + f'COUNT|{missing}|{missing_line}|none|call|noSlot0|named17|calleeGone|receiverGone|97|1|0|0|'.encode()
    duplicate_output = missing_caught + b'P|D|'
    duplicate_caught = duplicate_output + f'ERROR|{duplicate}|{duplicate_line}|none|noFrame|calleeGone|receiverGone|97|2|0|0|'.encode()
    assert stdout == duplicate_caught + b'23|A|'
    values = [*initial, *reach('S_capture', 'S_initial', 0, late_line),
        'S_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_capture) :: ptask_capture*',
        'n_source = pclosurecall_capture.SOURCE',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in
          ['call', 'receiver', 'params', 'effects', 'bodies', 'skipped', 'result']],
        'S_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_receiver)',
        'S_capture.STORE[n_params_cv] = DEFINED (PARRAY n_params)',
        *reach('S_pack', 'S_capture', 1, late_line, 0),
        'S_pack.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_pack (KNOWN (PARRAY n_params)) 0) :: ptask_pack*',
        'pclosurecall_pack.FIRST = eps',
        'pclosurecall_pack.PACKS = [pconfigpack]', 'pconfigpack.INDEX = 0',
        'pconfigpack.ITEMS = [ENTRY (KSTRING $ptascii("second")) (DIRECT (PINT 29))]',
        *reach('S_send', 'S_pack', 6, late_line, 1),
        'S_send.TODO = (CLOSURE_CALL_SEND pclosurecall_send) :: ptask_send*',
        'pclosurecall_send.FIRST = eps', 'pclosurecall_send.RECEIVER = eps',
        'pclosurecall_send.RAW = [(KSTRING $ptascii("second"),KNOWN (PINT 29))]',
        'S_send.RESULT = KNOWN (POBJECT n_receiver)',
        'S_send.STORE[n_call_cv] = DEFINED PNULL',
        'S_send.STORE[n_receiver_cv] = DEFINED PNULL',
        '~(HARRAY n_params <- S_send.ALLOCATIONS)',
        '$test_outputs(S_send.EVENTS) = ' + term(before_body),
        *reach('S_invoke_pending', 'S_send', 3, late_line),
        *settle('S_invoke', 'S_invoke_pending'),
        'S_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_invoke*',
        'pclosurecall.FIRST = (POBJECT n_receiver)', 'pclosurecall.RECEIVER = (n_receiver)',
        'pclosurecall.PACKS = [pconfigpack]', 'pclosurecall.RAW = pclosurecall_send.RAW',
        'pclosurecall.ERROR = eps',
        *budget('S_invoke'),
        *body('S_body', 'S_invoke', late_line, 'n_source', 'n_receiver', 'pclosurecall.RAW', True),
        *reach('S_missing_capture', 'S_body', 0, missing_line),
        'S_missing_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_missing_capture) :: ptask_missing_capture*',
        'n_missing_source = pclosurecall_missing_capture.SOURCE',
        'S_missing_capture.STORE[n_params_cv] = DEFINED (PARRAY n_missing_pack)',
        '~(HOBJECT n_source <- S_missing_capture.ALLOCATIONS)',
        '~(HOBJECT n_receiver <- S_missing_capture.ALLOCATIONS)',
        '$test_outputs(S_missing_capture.EVENTS) = ' + term(normal_done),
        *reach('S_missing_invoke_pending', 'S_missing_capture', 3, missing_line),
        *settle('S_missing_invoke', 'S_missing_invoke_pending'),
        'S_missing_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall_missing) :: ptask_missing_invoke*',
        'pclosurecall_missing.FIRST = eps', 'pclosurecall_missing.RECEIVER = eps',
        'pclosurecall_missing.RAW = [(KSTRING $ptascii("x"),KNOWN (PINT 17))]',
        'pclosurecall_missing.SENT = {SLOTS ([(NAMED_SENT (KNOWN (PINT 17)))]),NAMED eps}',
        'pclosurecall_missing.ERROR = eps',
        'pclosurecall_missing.PACKS = [pconfigpack_missing]',
        'pconfigpack_missing.INDEX = 0',
        '~(HARRAY n_missing_pack <- S_missing_invoke.ALLOCATIONS)',
        'S_missing_invoke.STORE[n_result_cv] = DEFINED (PINT 97)',
        'S_missing_invoke.STORE[n_effects_cv] = DEFINED (PINT 1)',
        '$test_outputs(S_missing_invoke.EVENTS) = ' + term(missing_output),
        *budget('S_missing_invoke'),
        *reach('S_missing_error_pending', 'S_missing_invoke', 5, missing_line),
        *settle('S_missing_error', 'S_missing_error_pending'),
        'S_missing_error.TODO = (THROW_SEARCH n_missing_error) :: ptask_missing_error*',
        'S_missing_error.OBJECTS[n_missing_error] = THROWABLE pthrowable_missing',
        'pthrowable_missing.KIND = "ArgumentCountError"',
        '$string_bytes($throwable_field(S_missing_error,n_missing_error,"message")) = (' + text(missing) + ')',
        f'$throwable_field(S_missing_error,n_missing_error,"line") = PINT {missing_line}',
        '$throwable_field(S_missing_error,n_missing_error,"previous") = PNULL',
        '$throwable_field(S_missing_error,n_missing_error,"trace") = PARRAY n_missing_trace',
        'S_missing_error.ARRAYS[n_missing_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_missing_frame))]',
        '$entry_lookup(S_missing_error.ARRAYS[n_missing_frame].ITEMS,KSTRING $ptascii("args")) = (DIRECT (PARRAY n_missing_args))',
        'S_missing_error.ARRAYS[n_missing_args].ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 17))]',
        '~(HOBJECT n_missing_source <- S_missing_error.ALLOCATIONS)',
        'S_missing_error.STORE[n_result_cv] = DEFINED (PINT 97)',
        *reach('S_missing_caught', 'S_missing_error', 7),
        '$test_outputs(S_missing_caught.EVENTS) = ' + term(missing_caught),
        *reach('S_duplicate_capture', 'S_missing_caught', 0, duplicate_line),
        'S_duplicate_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_duplicate_capture) :: ptask_duplicate_capture*',
        'n_duplicate_source = pclosurecall_duplicate_capture.SOURCE',
        'S_duplicate_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_duplicate_receiver)',
        'S_duplicate_capture.STORE[n_params_cv] = DEFINED (PARRAY n_duplicate_pack)',
        *reach('S_duplicate_send', 'S_duplicate_capture', 6, duplicate_line, 1),
        'S_duplicate_send.TODO = (CLOSURE_CALL_SEND pclosurecall_duplicate) :: ptask_duplicate*',
        'pclosurecall_duplicate.FIRST = (POBJECT n_duplicate_receiver)',
        'pclosurecall_duplicate.RECEIVER = (n_duplicate_receiver)',
        'pclosurecall_duplicate.PACKS = [pconfigpack_duplicate]',
        'pconfigpack_duplicate.INDEX = 0',
        'pconfigpack_duplicate.ITEMS = [ENTRY (KSTRING $ptascii("newThis")) (DIRECT (POBJECT n_duplicate_receiver))]',
        'pclosurecall_duplicate.RAW = eps', 'pclosurecall_duplicate.ERROR = eps',
        'S_duplicate_send.RESULT = KNOWN PNULL',
        'S_duplicate_send.STORE[n_effects_cv] = DEFINED (PINT 2)',
        'S_duplicate_send.STORE[n_skipped_cv] = DEFINED (PINT 0)',
        'S_duplicate_send.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_duplicate_send.STORE[n_result_cv] = DEFINED (PINT 97)',
        '~(HARRAY n_duplicate_pack <- S_duplicate_send.ALLOCATIONS)',
        '$closure_call_outer_error(pclosurecall_duplicate,eps,KSTRING $ptascii("newThis")) = (' + text(duplicate) + ')',
        '$closure_call_pack_append($closure_call_parameters(S_duplicate_send,n_duplicate_source),pclosurecall_duplicate,KSTRING $ptascii("newThis"),PNULL) = eps',
        '$test_outputs(S_duplicate_send.EVENTS) = ' + term(duplicate_output),
        *budget('S_duplicate_send'),
        *reach('S_duplicate_error_pending', 'S_duplicate_send', 5, duplicate_line),
        *settle('S_duplicate_error', 'S_duplicate_error_pending'),
        *reuse.outer_error('S_duplicate_error', 'duplicate', duplicate_line, duplicate, 2),
        '~(HOBJECT n_duplicate_source <- S_duplicate_error.ALLOCATIONS)',
        '~(HOBJECT n_duplicate_receiver <- S_duplicate_error.ALLOCATIONS)',
        *reach('S_duplicate_caught', 'S_duplicate_error', 7),
        '$test_outputs(S_duplicate_caught.EVENTS) = ' + term(duplicate_caught),
        *define.finish('S_duplicate_caught', stdout)]
    for node in ['HOBJECT n_source', 'HOBJECT n_receiver', 'HOBJECT n_missing_source',
                 'HOBJECT n_duplicate_source', 'HOBJECT n_duplicate_receiver',
                 'HARRAY n_params', 'HARRAY n_missing_pack', 'HARRAY n_duplicate_pack',
                 'HOBJECT n_missing_error', 'HOBJECT n_error_duplicate']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


def checks(initial, name, stdout):
    return (normal if name == sources.NORMAL else priority)(initial, stdout)


base.sources, base.checks, base.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare, packet.process = sources, base.prepare, old.process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
