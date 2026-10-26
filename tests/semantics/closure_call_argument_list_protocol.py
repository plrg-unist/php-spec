#!/usr/bin/env python3
"""Canonical list replay, saved direct values and early outer Error ownership."""
from pathlib import Path

import define_stdclass_array_duplicate_protocol as base
import closure_call_array_pack_protocol as old
import closure_call_argument_list_sources as sources

define, packet, common = base.define, base.packet, base.common
ROOT, text, term = base.ROOT, base.text, base.term
PREFIX = old.PREFIX + r'''
dec $test_closure_list_front(pstate,nat,int,nat) : bool
def $test_closure_list_front(S,0,z,n_index) = true
  -- if S.TODO = (CLOSURE_CALL_ARGS pclosurecall) :: ptask_tail*
  -- if pclosurecall.LINE = z
  -- if pclosurecall.INDEX = n_index
def $test_closure_list_front(S,1,z,n_index) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n_array)) 0) :: ptask_tail*
  -- if pclosurecall.LINE = z
  -- if pclosurecall.INDEX = n_index
def $test_closure_list_front(S,2,z,n_index) = true
  -- if S.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall (KNOWN (PARRAY n_array)) n_cursor) :: ptask_tail*
  -- if pclosurecall.LINE = z
  -- if pclosurecall.INDEX = n_index
  -- if n_last = $nabs($(|pclosurecall.PACKS| - 1))
  -- if pconfigpack = pclosurecall.PACKS[n_last]
  -- if n_cursor = |pconfigpack.ITEMS|
def $test_closure_list_front(S,3,z,n_index) = true
  -- if S.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_tail*
  -- if pclosurecall.LINE = z
def $test_closure_list_front(S,4,z,n_index) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver
  -- if pcallcontext.LINE = z
  -- if S.TODO = (STMT statement) :: ptask_tail*
def $test_closure_list_front(S,5,z,n_index) = true
  -- if S.TODO = (THROW_SEARCH n_error) :: ptask_tail*
  -- if $throwable_field(S,n_error,"line") = PINT z
def $test_closure_list_front(S,6,z,n_index) = true
  -- if S.TODO = (CLOSURE_CALL_SEND pclosurecall) :: ptask_tail*
  -- if pclosurecall.LINE = z
  -- if pclosurecall.INDEX = n_index
def $test_closure_list_front(S,7,z,n_index) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("error")
def $test_closure_list_front(S,8,z,n_index) = true
  -- if S.TODO = (STMT (NStmtUnset (SEQUENCE expression*) metadata)) :: ptask_tail*
  -- if expression* = (NExprVariable (BYTES text_name) metadata_name) :: expression_tail*
  -- if $base64(text_name) = $ptascii("call")
def $test_closure_list_front(S,n_phase,z,n_index) = false -- otherwise
dec $test_closure_list_seek(pstate,nat,int,nat,nat) : pstate
def $test_closure_list_seek(S,n_phase,z,n_index,0) = S
def $test_closure_list_seek(S,n_phase,z,n_index,n) = S
  -- if $(n > 0)
  -- if $test_closure_list_front(S,n_phase,z,n_index) \/ (S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET)
def $test_closure_list_seek(S,n_phase,z,n_index,n) = $test_closure_list_seek($drive_steps($test_running(S),1),n_phase,z,n_index,$nabs($(n - 1)))
  -- if $(n > 0)
  -- if ~$test_closure_list_front(S,n_phase,z,n_index)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
'''


def lines(name):
    return [n for n,line in enumerate(sources.family.CASES[name].splitlines(),1) if b'->call(' in line]


def reach(state, start, phase, line=0, index=0):
    return [f'{state}_found = $test_closure_list_seek({start},{phase},{line},{index},4000)',
        fr'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
        f'{state} = $test_running({state}_found)',
        f'$test_closure_list_front({state},{phase},{line},{index})', *common.public(state)]


def normal(initial, stdout):
    first_line, second_line = lines(sources.NORMAL)
    first = b'B|N|calleeHeld|receiverHeld|'
    before_body = first + b'P|calleeHeld|receiverHeld|'
    first_done = before_body + b'BODY|17|7|13|29|received|R|36|2|1|99|currentNull|calleeGone|receiverGone|'
    before_second = first_done + b'M|T|calleeHeld|receiverHeld|'
    assert stdout == before_second + b'BODY2|17|5|17|23|29|47|R2|121|2|1|99|currentNull|calleeGone|receiverGone|23|A|'
    values = [*initial,*reach('S_capture','S_initial',0,first_line),
        'S_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_capture) :: ptask_capture*',
        'n_source = pclosurecall_capture.SOURCE',
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in
            ['call','receiver','namedPack','positionalPack','effects','bodies','result']],
        'S_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_receiver)',
        'S_capture.STORE[n_namedPack_cv] = DEFINED (PARRAY n_named_pack)',
        'S_capture.STORE[n_positionalPack_cv] = DEFINED (PARRAY n_positional_pack)',
        *reach('S_first','S_capture',1,first_line,1),
        'S_first.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_first (KNOWN (PARRAY n_named_pack)) 0) :: ptask_first*',
        'pclosurecall_first.PACKS = [pconfigpack_first]',
        'pconfigpack_first.INDEX = 1',
        'pconfigpack_first.ITEMS = [ENTRY (KSTRING $ptascii("third")) (DIRECT (PINT 29))]',
        '$test_outputs(S_first.EVENTS) = ' + term(first),
        *reach('S_between_pending','S_first',0,first_line,2),*old.settle('S_between','S_between_pending'),
        'S_between.TODO = (CLOSURE_CALL_ARGS pclosurecall_between) :: ptask_between*',
        'pclosurecall_between.RAW = [(KSTRING $ptascii("third"),KNOWN (PINT 29))]',
        'pclosurecall_between.SENT = {SLOTS ([NAMED_HOLE,NAMED_HOLE,(NAMED_SENT (KNOWN (PINT 29)))]),NAMED eps}',
        'pclosurecall_between.ERROR = eps',
        '~(HARRAY n_named_pack <- S_between.ALLOCATIONS)',
        'S_between.STORE[n_namedPack_cv] = DEFINED (PARRAY n_named_current)',
        'n_named_current =/= n_named_pack',
        'S_between.ARRAYS[n_named_current].ITEMS = [ENTRY (KSTRING $ptascii("third")) (DIRECT (PINT 99))]',
        *old.budget('S_between'),
        *reach('S_second_pack','S_between',1,first_line,2),
        'S_second_pack.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_second_pack (KNOWN (PARRAY n_positional_pack)) 0) :: ptask_second_pack*',
        'pclosurecall_second_pack.PACKS = [pconfigpack_first,pconfigpack_second]',
        'pconfigpack_second.INDEX = 2',
        'pconfigpack_second.ITEMS = [ENTRY (KINT 9) (DIRECT pvalue_first)]',
        '$string_plain(pvalue_first) = PSTRING $ptascii("7")',
        'pclosurecall_second_pack.RAW = pclosurecall_between.RAW',
        '$closure_call_pack_outer_error(pclosurecall_second_pack.RAW,eps,KINT 9) = eps',
        *reach('S_invoke_pending','S_second_pack',3,first_line),*old.settle('S_invoke','S_invoke_pending'),
        'S_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall) :: ptask_invoke*',
        'pclosurecall.PACKS = [pconfigpack_first,pconfigpack_second]',
        'pclosurecall.RAW = [(KINT 1,KNOWN pvalue_first),(KSTRING $ptascii("third"),KNOWN (PINT 29))]',
        'pclosurecall.SENT = {SLOTS ([(NAMED_SENT (KNOWN pvalue_first)),NAMED_HOLE,(NAMED_SENT (KNOWN (PINT 29)))]),NAMED eps}',
        'pclosurecall.ERROR = eps',
        'S_invoke.STORE[n_call_cv] = DEFINED PNULL',
        'S_invoke.STORE[n_receiver_cv] = DEFINED PNULL',
        'S_invoke.STORE[n_positionalPack_cv] = DEFINED PNULL',
        '~(HARRAY n_named_pack <- S_invoke.ALLOCATIONS)',
        '~(HARRAY n_positional_pack <- S_invoke.ALLOCATIONS)',
        '$test_outputs(S_invoke.EVENTS) = ' + term(before_body),
        *old.budget('S_invoke')]
    for packs in ['eps','[pconfigpack_second,pconfigpack_first]','[pconfigpack_first]',
            '[pconfigpack_first,pconfigpack_second,pconfigpack_second]']:
        values += [f'~$call_task_valid(S_invoke,CLOSURE_CALL_INVOKE pclosurecall[.PACKS = {packs}])']
    values += [*reach('S_body','S_invoke',4,first_line),
        'S_body.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver',
        'pcallcontext.ARGC = 3','pcallcontext.HOLES = [1]',
        'pcallcontext.WRAPPER = (pnamedargs_wrapper)',
        'pnamedargs_wrapper = {SLOTS ([(NAMED_SENT (KNOWN pvalue_first))]),NAMED ([($ptascii("third"),KNOWN (PINT 29))])}',
        '$lookup(S_body.ENV,$ptascii("first")) = (n_first)',
        '$lookup(S_body.ENV,$ptascii("second")) = (n_second)',
        '$lookup(S_body.ENV,$ptascii("third")) = (n_third)',
        'S_body.STORE[n_first] = DEFINED (PINT 7)',
        'S_body.STORE[n_second] = DEFINED pvalue_default',
        '$string_plain(pvalue_default) = PSTRING $ptascii("13")',
        'S_body.STORE[n_third] = DEFINED (PINT 29)',
        '~$wrapper_context_valid(S_body,pcallcontext[.HOLES = eps])',
        'S_body.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        *reach('S_mixed_capture','S_body',0,second_line),
        'S_mixed_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_mixed) :: ptask_mixed*',
        'n_mixed_source = pclosurecall_mixed.SOURCE','n_mixed_source =/= n_source',
        'S_mixed_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_mixed_receiver)',
        '$lookup(S_mixed_capture.ENV,$ptascii("direct")) = (n_direct_cv)',
        '$lookup(S_mixed_capture.ENV,$ptascii("mixedPack")) = (n_mixed_cv)',
        'S_mixed_capture.STORE[n_mixed_cv] = DEFINED (PARRAY n_mixed_pack)',
        '~(HOBJECT n_source <- S_mixed_capture.ALLOCATIONS)',
        '~(HOBJECT n_receiver <- S_mixed_capture.ALLOCATIONS)',
        '$test_outputs(S_mixed_capture.EVENTS) = ' + term(first_done),
        *reach('S_direct','S_mixed_capture',0,second_line,2),
        'S_direct.TODO = (CLOSURE_CALL_ARGS pclosurecall_direct) :: ptask_direct*',
        'pclosurecall_direct.PACKS = eps',
        'pclosurecall_direct.RAW = [(KINT 1,KNOWN pvalue_direct)]',
        '$string_plain(pvalue_direct) = PSTRING $ptascii("5")',
        *reach('S_mixed_pack','S_direct',1,second_line,2),
        'S_mixed_pack.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_pack (KNOWN (PARRAY n_mixed_pack)) 0) :: ptask_pack*',
        'pclosurecall_pack.PACKS = [pconfigpack_mixed]',
        'pconfigpack_mixed.INDEX = 2',
        'pconfigpack_mixed.ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 17)),ENTRY (KINT 9) (DIRECT (PINT 23)),ENTRY (KSTRING $ptascii("third")) (DIRECT (PINT 29))]',
        'pclosurecall_pack.RAW = pclosurecall_direct.RAW',
        'S_mixed_pack.STORE[n_direct_cv] = DEFINED pvalue_direct_current',
        '$string_plain(pvalue_direct_current) = PSTRING $ptascii("99")',
        'S_changed_direct = S_mixed_pack[.STORE[n_direct_cv] = DEFINED PNULL]',
        '$call_task_valid(S_changed_direct,CLOSURE_CALL_UNPACK_NEXT pclosurecall_pack (KNOWN (PARRAY n_mixed_pack)) 0)',
        *old.budget('S_mixed_pack'),
        *reach('S_tail','S_mixed_pack',6,second_line,3),
        'S_tail.TODO = (CLOSURE_CALL_SEND pclosurecall_tail) :: ptask_tail*',
        'S_tail.RESULT = KNOWN (PINT 47)',
        'pclosurecall_tail.RAW = [(KINT 1,KNOWN pvalue_direct),(KINT 2,KNOWN (PINT 17)),(KINT 3,KNOWN (PINT 23)),(KSTRING $ptascii("third"),KNOWN (PINT 29))]',
        'S_tail.STORE[n_call_cv] = DEFINED PNULL',
        'S_tail.STORE[n_receiver_cv] = DEFINED PNULL',
        'S_tail.STORE[n_mixed_cv] = DEFINED PNULL',
        '~(HARRAY n_mixed_pack <- S_tail.ALLOCATIONS)',
        '$test_outputs(S_tail.EVENTS) = ' + term(before_second),
        *reach('S_mixed_invoke_pending','S_tail',3,second_line),*old.settle('S_mixed_invoke','S_mixed_invoke_pending'),
        'S_mixed_invoke.TODO = (CLOSURE_CALL_INVOKE pclosurecall_complete) :: ptask_complete*',
        'pclosurecall_complete.INDEX = 4','pclosurecall_complete.PACKS = [pconfigpack_mixed]',
        'pclosurecall_complete.RAW = pclosurecall_tail.RAW ++ [(KSTRING $ptascii("fourth"),KNOWN (PINT 47))]',
        'pclosurecall_complete.SENT.NAMED = [($ptascii("third"),KNOWN (PINT 29)),($ptascii("fourth"),KNOWN (PINT 47))]',
        'pclosurecall_complete.ERROR = eps',
        *old.budget('S_mixed_invoke'),
        *reach('S_mixed_body','S_mixed_invoke',4,second_line),
        'S_mixed_body.CURRENT = (pcallcontext_mixed)',
        'pcallcontext_mixed.TARGET = CLOSURE_CALL_TARGET n_mixed_source n_mixed_receiver',
        'pcallcontext_mixed.ARGC = 3','pcallcontext_mixed.HOLES = eps',
        'pcallcontext_mixed.WRAPPER = ($closure_call_wrapper(pclosurecall_complete.RAW))',
        '$lookup(S_mixed_body.ENV,$ptascii("first")) = (n_mixed_first)',
        '$lookup(S_mixed_body.ENV,$ptascii("second")) = (n_mixed_second)',
        '$lookup(S_mixed_body.ENV,$ptascii("rest")) = (n_rest)',
        'S_mixed_body.STORE[n_mixed_first] = DEFINED (PINT 5)',
        'S_mixed_body.STORE[n_mixed_second] = DEFINED (PINT 17)',
        'S_mixed_body.STORE[n_rest] = DEFINED (PARRAY n_variadic)',
        'S_mixed_body.ARRAYS[n_variadic].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 23)),ENTRY (KSTRING $ptascii("third")) (DIRECT (PINT 29)),ENTRY (KSTRING $ptascii("fourth")) (DIRECT (PINT 47))]',
        'S_mixed_body.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_mixed_body.EVENTS) = ' + term(before_second),
        *reach('S_cleanup_pending','S_mixed_body',8),*old.settle('S_cleanup','S_cleanup_pending'),
        'S_cleanup.STORE[n_result_cv] = DEFINED (PINT 121)',
        'S_cleanup.STORE[n_effects_cv] = DEFINED (PINT 2)',
        'S_cleanup.STORE[n_bodies_cv] = DEFINED (PINT 1)',
        *define.finish('S_cleanup',stdout)]
    for node in ['HOBJECT n_source','HOBJECT n_receiver','HOBJECT n_mixed_source','HOBJECT n_mixed_receiver',
            'HARRAY n_named_pack','HARRAY n_named_current','HARRAY n_positional_pack','HARRAY n_mixed_pack','HARRAY n_variadic']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


def outer(initial, stdout):
    duplicate = 'Named parameter $x overwrites previous argument'
    order = 'Cannot use positional argument after named argument during unpacking'
    first_line, second_line, third_line = lines(sources.OUTER)
    first_output = b'B|L|R|'
    first_caught = first_output + f'E|{duplicate}|{first_line}|file|none|noFrame|calleeGone|receiverGone|97|2|0|0|'.encode()
    second_output = first_caught + b'R|'
    second_caught = second_output + f'E|{order}|{second_line}|file|none|noFrame|calleeGone|receiverGone|97|3|0|0|'.encode()
    third_output = second_caught + b'L|T|'
    third_caught = third_output + f'E|{duplicate}|{third_line}|file|none|noFrame|calleeGone|receiverGone|97|5|0|0|'.encode()
    assert stdout == third_caught + b'23|A|'
    values = [*initial,*reach('S_capture','S_initial',0,first_line),
        *[f'$lookup(S_capture.ENV,{text(name)}) = (n_{name}_cv)' for name in
            ['call','receiver','left','right','effects','bodies','skipped','result']],
        *reach('S_left','S_capture',1,first_line,1),
        'S_left.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_left (KNOWN (PARRAY n_left)) 0) :: ptask_left*',
        'pclosurecall_left.PACKS = [pconfigpack_left]',
        'pconfigpack_left.ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 17))]',
        *reach('S_duplicate','S_left',1,first_line,2),
        'S_duplicate.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_duplicate (KNOWN (PARRAY n_right)) 0) :: ptask_duplicate*',
        'n_source = pclosurecall_duplicate.SOURCE',
        'pclosurecall_duplicate.RECEIVER = (n_receiver)',
        'pclosurecall_duplicate.PACKS = [pconfigpack_left,pconfigpack_right]',
        'pconfigpack_right.INDEX = 2',
        'pconfigpack_right.ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 29))]',
        'pclosurecall_duplicate.RAW = [(KSTRING $ptascii("x"),KNOWN (PINT 17))]',
        'pclosurecall_duplicate.ERROR = eps',
        '$closure_call_pack_outer_error(pclosurecall_duplicate.RAW,eps,KSTRING $ptascii("x")) = (' + text(duplicate) + ')',
        '$closure_call_pack_append($closure_call_parameters(S_duplicate,n_source),pclosurecall_duplicate,KSTRING $ptascii("x"),PINT 29) = eps',
        'S_duplicate.STORE[n_call_cv] = DEFINED PNULL',
        'S_duplicate.STORE[n_receiver_cv] = DEFINED PNULL',
        'S_duplicate.STORE[n_effects_cv] = DEFINED (PINT 2)',
        'S_duplicate.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        'S_duplicate.STORE[n_skipped_cv] = DEFINED (PINT 0)',
        'S_duplicate.STORE[n_result_cv] = DEFINED (PINT 97)',
        '~(HARRAY n_left <- S_duplicate.ALLOCATIONS)',
        '(HARRAY n_right) <- S_duplicate.ALLOCATIONS',
        '(HOBJECT n_source) <- S_duplicate.ALLOCATIONS',
        '(HOBJECT n_receiver) <- S_duplicate.ALLOCATIONS',
        '$test_outputs(S_duplicate.EVENTS) = ' + term(first_output),
        *old.budget('S_duplicate'),
        *reach('S_duplicate_error_pending','S_duplicate',5,first_line),*old.settle('S_duplicate_error','S_duplicate_error_pending'),
        *outer_error('S_duplicate_error','duplicate',first_line,duplicate,2),
        '~(HOBJECT n_source <- S_duplicate_error.ALLOCATIONS)',
        '~(HOBJECT n_receiver <- S_duplicate_error.ALLOCATIONS)',
        '~(HARRAY n_right <- S_duplicate_error.ALLOCATIONS)',
        '$test_outputs(S_duplicate_error.EVENTS) = ' + term(first_output),
        *reach('S_first_caught','S_duplicate_error',7),
        '$test_outputs(S_first_caught.EVENTS) = ' + term(first_caught),
        *reach('S_order_start','S_first_caught',1,second_line,1),
        'S_order_start.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_order_start (KNOWN (PARRAY n_order)) 0) :: ptask_order_start*',
        'pclosurecall_order_start.SOURCE = n_order_source',
        'pclosurecall_order_start.RECEIVER = (n_order_receiver)',
        'pclosurecall_order_start.PACKS = [pconfigpack_order]',
        'pconfigpack_order.ITEMS = [ENTRY (KSTRING $ptascii("x")) (DIRECT (PINT 17)),ENTRY (KINT 9) (DIRECT (PINT 29))]',
        'S_order_found = $drive_steps(S_order_start,1)',
        r'S_order_found.COMPLETION = NORMAL \/ S_order_found.COMPLETION = BUDGET',
        'S_order = $test_running(S_order_found)',*common.public('S_order'),
        'S_order.TODO = (CLOSURE_CALL_UNPACK_NEXT pclosurecall_order (KNOWN (PARRAY n_order)) 1) :: ptask_order*',
        'pclosurecall_order.RAW = [(KSTRING $ptascii("x"),KNOWN (PINT 17))]',
        'pclosurecall_order.ERROR = eps',
        '$closure_call_pack_outer_error(pclosurecall_order.RAW,pconfigpack_order.ITEMS[0:1],KINT 9) = (' + text(order) + ')',
        '$closure_call_pack_outer_error(pclosurecall_order.RAW,eps,KINT 9) = eps',
        'S_order.STORE[n_effects_cv] = DEFINED (PINT 3)',
        'S_order.STORE[n_skipped_cv] = DEFINED (PINT 0)',
        'S_order.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        '$test_outputs(S_order.EVENTS) = ' + term(second_output),
        *old.budget('S_order'),
        *reach('S_order_error_pending','S_order',5,second_line),*old.settle('S_order_error','S_order_error_pending'),
        *outer_error('S_order_error','order',second_line,order,3),
        '~(HOBJECT n_order_source <- S_order_error.ALLOCATIONS)',
        '~(HOBJECT n_order_receiver <- S_order_error.ALLOCATIONS)',
        '~(HARRAY n_order <- S_order_error.ALLOCATIONS)',
        *reach('S_second_caught','S_order_error',7),
        '$test_outputs(S_second_caught.EVENTS) = ' + term(second_caught),
        *reach('S_tail_capture','S_second_caught',0,third_line),
        'S_tail_capture.TODO = (CLOSURE_CALL_ARGS pclosurecall_tail_capture) :: ptask_tail_capture*',
        'n_tail_source = pclosurecall_tail_capture.SOURCE',
        'S_tail_capture.STORE[n_receiver_cv] = DEFINED (POBJECT n_tail_receiver)',
        'S_tail_capture.STORE[n_left_cv] = DEFINED (PARRAY n_tail_array)',
        *reach('S_tail','S_tail_capture',6,third_line,2),
        'S_tail.TODO = (CLOSURE_CALL_SEND pclosurecall_tail) :: ptask_tail*',
        'pclosurecall_tail.PACKS = [pconfigpack_tail]',
        'pclosurecall_tail.RAW = [(KSTRING $ptascii("x"),KNOWN (PINT 17))]',
        'pclosurecall_tail.ERROR = eps','S_tail.RESULT = KNOWN (PINT 29)',
        'S_tail.STORE[n_effects_cv] = DEFINED (PINT 5)',
        'S_tail.STORE[n_skipped_cv] = DEFINED (PINT 0)',
        'S_tail.STORE[n_call_cv] = DEFINED PNULL',
        'S_tail.STORE[n_receiver_cv] = DEFINED PNULL',
        '~(HARRAY n_tail_array <- S_tail.ALLOCATIONS)',
        '$test_outputs(S_tail.EVENTS) = ' + term(third_output),
        *old.budget('S_tail'),
        *reach('S_tail_error_pending','S_tail',5,third_line),*old.settle('S_tail_error','S_tail_error_pending'),
        *outer_error('S_tail_error','tail',third_line,duplicate,5),
        '~(HOBJECT n_tail_source <- S_tail_error.ALLOCATIONS)',
        '~(HOBJECT n_tail_receiver <- S_tail_error.ALLOCATIONS)',
        *reach('S_third_caught','S_tail_error',7),
        '$test_outputs(S_third_caught.EVENTS) = ' + term(third_caught),
        *define.finish('S_third_caught',stdout)]
    for node in ['HOBJECT n_source','HOBJECT n_receiver','HOBJECT n_order_source','HOBJECT n_order_receiver',
            'HOBJECT n_tail_source','HOBJECT n_tail_receiver','HARRAY n_left','HARRAY n_right','HARRAY n_order','HARRAY n_tail_array',
            'HOBJECT n_error_duplicate','HOBJECT n_error_order','HOBJECT n_error_tail']:
        values += [f'~({node} <- S_final.ALLOCATIONS)']
    return values


def outer_error(state, label, line, message, effects):
    return [f'{state}.TODO = (THROW_SEARCH n_error_{label}) :: ptask_error_{label}*',
        f'{state}.OBJECTS[n_error_{label}] = THROWABLE pthrowable_{label}',
        f'pthrowable_{label}.KIND = "Error"',
        f'$string_bytes($throwable_field({state},n_error_{label},"message")) = ({text(message)})',
        f'$throwable_field({state},n_error_{label},"line") = PINT {line}',
        f'$throwable_field({state},n_error_{label},"previous") = PNULL',
        f'$throwable_field({state},n_error_{label},"trace") = PARRAY n_trace_{label}',
        f'{state}.ARRAYS[n_trace_{label}].ITEMS = eps',
        f'{state}.STORE[n_effects_cv] = DEFINED (PINT {effects})',
        f'{state}.STORE[n_bodies_cv] = DEFINED (PINT 0)',
        f'{state}.STORE[n_skipped_cv] = DEFINED (PINT 0)',
        f'{state}.STORE[n_result_cv] = DEFINED (PINT 97)']


def checks(initial, name, stdout):
    return (normal if name == sources.NORMAL else outer)(initial,stdout)


base.sources, base.checks, base.PREFIX = sources, checks, PREFIX
packet.sources, packet.prepare, packet.process = sources, base.prepare, old.process
family_fingerprint = sources.family.fingerprint


def fingerprint():
    return dict(family_fingerprint(), **{
        str(Path(__file__).relative_to(ROOT)): sources.family.sha(__file__)})


sources.family.fingerprint = fingerprint

if __name__ == '__main__':
    raise SystemExit(0 if packet.main() else 1)
