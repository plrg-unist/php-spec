#!/usr/bin/env python3
"""Generator spread acquisition, cached edges and staged abrupt retirement."""
import base64
import json

import array_generator_unpack_review_cases as cases
import list_missing_warning_protocol as shared

HELPERS = shared.HELPERS + r'''
dec $array_gen_review_echo(pstate, ptbytes) : bool
def $array_gen_review_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = n_prefix*
def $array_gen_review_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 70) = true
  -- if S.TODO = (ARRAY_UNPACK n phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 71) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*
def $list_warning_frontier(S, 72) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator text) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 73) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*
def $list_warning_frontier(S, 74) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 75) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "input-released") :: ptask_tail*
def $list_warning_frontier(S, 76) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 77) = $array_gen_review_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 78) = $array_gen_review_echo(S, $ptascii("S:"))
def $list_warning_frontier(S, 79) = $array_gen_review_echo(S, $ptascii("N:"))
def $list_warning_frontier(S, 80) = $array_gen_review_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 81) = $array_gen_review_echo(S, $ptascii("A;"))
def $list_warning_frontier(S, 82) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_body*
  -- if S.CURRENT = (pcallcontext)
  -- if S.FRAMES = pframe :: pframe_tail*
  -- if pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (ARRAY_GENERATOR parraygenerator "next") :: ptask_caller*
def $list_warning_frontier(S, 83) = $array_gen_review_echo(S, $ptascii("E1:"))
def $list_warning_frontier(S, 84) = $array_gen_review_echo(S, $ptascii("R1:"))
def $list_warning_frontier(S, 85) = $array_gen_review_echo(S, $ptascii("E2:"))
def $list_warning_frontier(S, 86) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_CLOSED
def $list_warning_frontier(S, 87) = $array_gen_review_echo(S, $ptascii("R2:"))
'''


def seek(start, stage, state):
    return [f'{state}_found = $list_warning_seek({start}, {stage}, 3000)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$list_warning_frontier({state}, {stage})']


def public(state):
    return [f'$heap_valid($heap_graph({state}))', f'$call_descriptors_valid({state})']


def owners(state, node, count):
    return f'$heap_owners($heap_graph({state}), {node}) = {count}'


def output(state, value):
    return f'$list_warning_outputs({state}.EVENTS) = $ptascii({json.dumps(value)})'


def singleton(state, array, value):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def budget(state, label):
    return [f'{label}_zero = $drive_steps({state}, 0)',
            f'{label}_zero = {state}[.COMPLETION = BUDGET]',
            f'{label}_whole = $drive_steps({state}, 2)',
            f'{label}_one = $drive_steps({state}, 1)',
            f'{label}_one.COMPLETION = BUDGET',
            f'{label}_split = $drive_steps({label}_one[.COMPLETION = NORMAL], 1)',
            f'{label}_split = {label}_whole']


def initial(program, path):
    return ['S_initial = $php_run(' + program + ', 0, '
            + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
            'S_initial.COMPLETION = BUDGET']


def entry(start, suffix, line, generator_owners, entries):
    pre, active = f'S_pre_{suffix}', f'S_active_{suffix}'
    desc, target = f'parraygenerator_{suffix}', f'n_target_{suffix}'
    obj, gen, it = f'n_generator_{suffix}', f'pgenerator_{suffix}', f'n_it_{suffix}'
    checks = seek(start, 70, pre) + [
        f'{pre}.TODO = (ARRAY_UNPACK {target} phpType13_{suffix}* z_{suffix}) :: ptask_{suffix}*',
        f'z_{suffix} = {line}',
        f'{pre}.RESULT = VARIABLE ($ptascii("it")) z_{suffix}',
        f'$lookup({pre}.ENV, $ptascii("it")) = ({it})',
        f'{pre}.STORE[{it}] = DEFINED (POBJECT {obj})',
        f'{pre}.OBJECTS[{obj}] = GENERATOR {gen}',
        f'{pre}.ARRAYS[{target}].ITEMS = {entries}',
        f'$array_generator_plan({pre}) = ({desc})',
        f'{desc}.ARRAY = {target}', f'{desc}.OBJECT = {obj}',
        f'{desc}.FUNCTION = {gen}.FUNCTION', f'{desc}.INPUT = {pre}.RESULT',
        f'{desc}.TAIL = phpType13_{suffix}*', f'{desc}.LINE = z_{suffix}',
        f'{pre}.ORIGIN = ({desc}.SITE)',
        f'$array_generator_history({pre}, {desc})', f'$array_generator_source({pre}, {desc})',
        owners(pre, f'HOBJECT {obj}', generator_owners),
        owners(pre, f'HARRAY {target}', 1),
        f'$task_nodes(ARRAY_UNPACK {target} phpType13_{suffix}* z_{suffix}) = [HARRAY {target}]',
    ] + public(pre)
    return checks, pre, active, desc, target, obj, gen, it


def start(pre, active, desc, target, obj, generator_owners):
    tail = 'ptask_' + pre.removeprefix('S_pre_') + '*'
    return [
        f'PhpStep: {pre} ~> {active}',
        f'{active}.TODO = (ARRAY_GENERATOR {desc} "rewind") :: {tail}',
        f'$array_generator_valid({active}, {desc}, "rewind")',
        f'$array_generator_nodes({desc}, "rewind") = [HARRAY {target}, HOBJECT {obj}]',
        f'{active}.RESULT = KNOWN PNULL', f'{active}.BASE = BASE_VALUE (KNOWN PNULL)',
        f'{active}.STORE = {pre}.STORE', f'{active}.ARRAYS = {pre}.ARRAYS',
        f'{active}.OBJECTS = {pre}.OBJECTS', f'{active}.EVENTS = {pre}.EVENTS',
        f'{active}.ITERATORS = {pre}.ITERATORS', f'{active}.NEXTITER = {pre}.NEXTITER',
        owners(active, f'HOBJECT {obj}', generator_owners),
        owners(active, f'HARRAY {target}', 1),
    ] + public(active)


def source_controls(state, desc):
    return [
        f'~$array_generator_history({state}[.CODE = eps], {desc})',
        f'~$array_generator_history({state}[.SOURCES = eps], {desc})',
        f'~$array_generator_history({state}, {desc}[.LINE = $({desc}.LINE + 1)])',
        f'~$array_generator_history({state}, {desc}[.SITE = PORIGIN 0 eps])',
        f'~$array_generator_history({state}, {desc}[.FUNCTION = PORIGIN 0 eps])',
        f'~$array_generator_history({state}, {desc}[.INPUT = KNOWN (POBJECT {desc}.OBJECT)])',
        f'~$array_generator_history({state}, {desc}[.TAIL = eps])',
        f'~$array_generator_source({state}, {desc}[.ARRAY = |{state}.ARRAYS|])',
    ]


def finish(state, stdout, retired):
    return [
        f'S_done = $drive_steps({state}, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.RESULT = KNOWN PNULL',
        output('S_done', stdout.decode()),
        *[f'~(({node}) <- S_done.ALLOCATIONS)' for node in retired],
    ] + public('S_done')


def shared_invalid(program, path, stdout):
    checks = initial(program, path)
    more, pre, active, desc, target, obj, gen, it = entry(
        'S_initial', 'shared', 13, 2, '[ENTRY (KINT 0) (DIRECT (PINT 2))]')
    checks += more + source_controls(pre, desc) + [
        f'{gen}.PHASE = GENERATOR_FRESH', f'{gen}.VALUE = eps', f'{gen}.REFCELL = eps',
        f'$lookup({pre}.ENV, $ptascii("hold")) = (n_hold)',
        f'{pre}.STORE[n_hold] = DEFINED (POBJECT {obj})',
        f'$lookup({pre}.ENV, $ptascii("row")) = (n_row)',
        f'{pre}.STORE[n_row] = DEFINED (PARRAY n_old)', singleton(pre, 'n_old', 2),
        owners(pre, 'HARRAY n_old', 1),
        f'$lookup({pre}.ENV, $ptascii("dest")) = (n_dest)',
        f'$lookup({pre}.ENV, $ptascii("later")) = (n_later)',
        f'{pre}.STORE[n_dest] = DEFINED (PINT 100)', f'{pre}.STORE[n_later] = DEFINED (PINT 7)',
    ] + start(pre, active, desc, target, obj, 3) + budget(pre, 'S_start_budget')
    checks += seek(active, 71, 'S_ready') + [
        f'S_ready.TODO = (ARRAY_GENERATOR {desc} "ready") :: ptask_ready*',
        f'S_ready.OBJECTS[{obj}] = GENERATOR pgenerator_ready',
        'pgenerator_ready.PHASE = GENERATOR_PAUSED', 'pgenerator_ready.FIRST',
        'pgenerator_ready.VALUE = (PARRAY n_old)', 'pgenerator_ready.REFCELL = eps',
        'pgenerator_ready.KEY = (PBOOL true)',
        f'$node_children(S_ready, HOBJECT {obj}) = [HARRAY n_old]',
        '$lookup(S_ready.ENV, $ptascii("it")) = eps',
        f'$array_generator_source(S_ready, {desc})',
        f'$array_generator_valid(S_ready, {desc}, "ready")',
        f'$array_generator_ready(S_ready, {desc})',
        f'$heap_count(HARRAY n_old, $task_nodes(ARRAY_GENERATOR {desc} "ready")) = 0',
        f'$heap_count(HCELL {it}, $task_nodes(ARRAY_GENERATOR {desc} "ready")) = 0',
        owners('S_ready', f'HOBJECT {obj}', 2), owners('S_ready', 'HARRAY n_old', 2),
        owners('S_ready', f'HARRAY {target}', 1), singleton('S_ready', 'n_old', 2),
        f'S_ready.ARRAYS[{target}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
        output('S_ready', 'P;B;'),
        f'S_object_current = S_ready[.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT {obj}))]]',
        '$heap_valid($heap_graph(S_object_current))',
        '$call_descriptors_valid(S_object_current)',
        f'$array_generator_source(S_object_current, {desc})',
        f'$array_generator_valid(S_object_current, {desc}, "ready")',
        f'~$array_generator_ready(S_object_current, {desc})',
        'PhpStep: S_object_current ~> S_object_refused',
        'S_object_refused = S_object_current[.COMPLETION = UNSUPPORTED "array Generator cache or builder outside direct domain"]',
        '$array_generator_blocked(S_object_refused)',
        '~$array_generator_blocked(S_ready[.COMPLETION = UNSUPPORTED "array Generator cache or builder outside direct domain"])',
        '$drive_steps(S_object_refused, 1) = S_object_refused',
        'PhpStep: S_ready ~> S_invalid',
        'S_invalid = S_ready[.COMPLETION = THROWN "Error" ($ptascii("Keys must be of type int|string during array unpacking")) 13]',
    ] + public('S_ready')
    # Public stepping registers the new Throwable handle after the raw step.
    checks += seek('S_ready', 72, 'S_pending') + [
        f'S_pending.TODO = (THROW_SEARCH n_error) :: (ARRAY_GENERATOR {desc} "ready") :: ptask_pending*',
        '$throwable_field(S_pending, n_error, "message") = pvalue_message',
        '$string_bytes(pvalue_message) = ($ptascii("Keys must be of type int|string during array unpacking"))',
        '$throwable_field(S_pending, n_error, "line") = PINT 13',
        '$throwable_field(S_pending, n_error, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = eps',
        '$throwable_field(S_pending, n_error, "previous") = PNULL',
        f'S_pending.ARRAYS[{target}].ITEMS = S_ready.ARRAYS[{target}].ITEMS',
        'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
        'S_pending.STORE[n_later] = DEFINED (PINT 7)',
        f'S_object_builder = S_pending[.ARRAYS[{target}].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT {obj}))]]',
        '$heap_valid($heap_graph(S_object_builder))', '$call_descriptors_valid(S_object_builder)',
        f'$array_generator_valid(S_object_builder, {desc}, "ready")',
        f'~$array_generator_builder(S_object_builder, {desc})',
        'PhpStep: S_object_builder ~> S_builder_refused',
        'S_builder_refused = S_object_builder[.COMPLETION = UNSUPPORTED "array Generator abrupt builder outside direct domain"]',
        '$array_generator_blocked(S_builder_refused)',
        '$drive_steps(S_builder_refused, 1) = S_builder_refused',
        '~$array_generator_blocked(S_pending[.COMPLETION = UNSUPPORTED "array Generator abrupt builder outside direct domain"])',
        'PhpStep: S_pending ~> S_data_released',
        f'S_data_released.TODO = (THROW_SEARCH n_error) :: (ARRAY_GENERATOR {desc} "data-released") :: ptask_pending*',
        f'$array_generator_nodes({desc}, "data-released") = [HARRAY {target}]',
        f'$array_generator_valid(S_data_released, {desc}, "data-released")',
        owners('S_data_released', f'HOBJECT {obj}', 1),
        owners('S_data_released', 'HARRAY n_old', 2),
        owners('S_data_released', f'HARRAY {target}', 1),
        'S_data_released.STORE = S_pending.STORE',
        'S_data_released.ARRAYS = S_pending.ARRAYS',
        'S_data_released.OBJECTS = S_pending.OBJECTS',
        'S_data_released.EVENTS = S_pending.EVENTS',
        'PhpStep: S_data_released ~> S_input_released',
        f'S_input_released.TODO = (THROW_SEARCH n_error) :: (ARRAY_GENERATOR {desc} "input-released") :: ptask_pending*',
        f'$array_generator_nodes({desc}, "input-released") = [HARRAY {target}]',
        owners('S_input_released', f'HOBJECT {obj}', 1),
        owners('S_input_released', f'HARRAY {target}', 1),
        '$throwable_live(S_input_released, n_error)',
    ] + public('S_pending') + public('S_data_released') + public('S_input_released')
    checks += seek('S_input_released', 77, 'S_catch_done') + [
        f'~((HARRAY {target}) <- S_catch_done.ALLOCATIONS)',
        'S_catch_done.STORE[n_dest] = DEFINED (PINT 100)',
        'S_catch_done.STORE[n_later] = DEFINED (PINT 7)',
        'S_catch_done.STORE[n_row] = DEFINED (PARRAY n_old)',
        f'S_catch_done.OBJECTS[{obj}] = GENERATOR pgenerator_caught',
        'pgenerator_caught.PHASE = GENERATOR_PAUSED',
        'pgenerator_caught.VALUE = (PARRAY n_old)',
        owners('S_catch_done', f'HOBJECT {obj}', 1),
        owners('S_catch_done', 'HARRAY n_old', 2),
        output('S_catch_done', 'P;B;E:Keys must be of type int|string during array unpacking:13:1:1;'),
    ] + public('S_catch_done')
    checks += seek('S_catch_done', 78, 'S_separated') + [
        'S_separated.STORE[n_row] = DEFINED (PARRAY n_replaced)',
        'n_replaced =/= n_old', singleton('S_separated', 'n_replaced', 33),
        singleton('S_separated', 'n_old', 2),
        f'S_separated.OBJECTS[{obj}] = GENERATOR pgenerator_separated',
        'pgenerator_separated.VALUE = (PARRAY n_old)',
        owners('S_separated', 'HARRAY n_old', 1),
        owners('S_separated', 'HARRAY n_replaced', 1),
    ] + public('S_separated')
    checks += seek('S_separated', 81, 'S_resuming') + [
        f'S_resuming.OBJECTS[{obj}] = GENERATOR pgenerator_running',
        'pgenerator_running.PHASE = GENERATOR_RUNNING',
        'pgenerator_running.VALUE = (PARRAY n_old)',
        singleton('S_resuming', 'n_old', 2),
        owners('S_resuming', 'HARRAY n_old', 1),
    ] + public('S_resuming')
    checks += seek('S_resuming', 79, 'S_next') + [
        'S_next.STORE[n_row] = DEFINED (PARRAY n_replaced)',
        singleton('S_next', 'n_replaced', 44),
        '~((HARRAY n_old) <- S_next.ALLOCATIONS)',
        f'S_next.OBJECTS[{obj}] = GENERATOR pgenerator_next',
        'pgenerator_next.PHASE = GENERATOR_PAUSED',
        'pgenerator_next.VALUE = (PARRAY n_replaced)',
        '$string_bytes($generator_cache_value(pgenerator_next.KEY)) = ($ptascii("later"))',
        owners('S_next', 'HARRAY n_replaced', 2),
    ] + public('S_next')
    checks += seek('S_next', 80, 'S_closed') + [
        f'S_closed.OBJECTS[{obj}] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (PARRAY n_replaced)',
        f'$node_children(S_closed, HOBJECT {obj}) = [HARRAY n_replaced]',
        owners('S_closed', 'HARRAY n_replaced', 2),
        owners('S_closed', f'HOBJECT {obj}', 1),
        'S_closed.STORE[n_dest] = DEFINED (PINT 100)',
        'S_closed.STORE[n_later] = DEFINED (PINT 7)',
    ] + public('S_closed')
    checks += finish('S_closed', stdout, [f'HARRAY {target}', f'HOBJECT {obj}',
                                        'HARRAY n_old', 'HARRAY n_replaced'])
    return checks


def body_throw(program, path, stdout):
    checks = initial(program, path)
    more, pre, active, desc, target, obj, gen, it = entry(
        'S_initial', 'body', 12, 2, '[ENTRY (KINT 0) (DIRECT (PINT 2))]')
    checks += more + [
        f'{gen}.PHASE = GENERATOR_FRESH',
        f'$lookup({pre}.ENV, $ptascii("hold")) = (n_hold)',
        f'{pre}.STORE[n_hold] = DEFINED (POBJECT {obj})',
        f'$lookup({pre}.ENV, $ptascii("row")) = (n_row)',
        f'{pre}.STORE[n_row] = DEFINED (PARRAY n_old)', singleton(pre, 'n_old', 2),
        f'$lookup({pre}.ENV, $ptascii("second")) = (n_second_cell)',
        f'{pre}.STORE[n_second_cell] = DEFINED PNULL',
        f'$lookup({pre}.ENV, $ptascii("dest")) = (n_dest)',
        f'$lookup({pre}.ENV, $ptascii("later")) = (n_later)',
        f'{pre}.STORE[n_dest] = DEFINED (PINT 100)', f'{pre}.STORE[n_later] = DEFINED (PINT 7)',
    ] + start(pre, active, desc, target, obj, 3)
    checks += seek(active, 71, 'S_ready') + [
        f'S_ready.TODO = (ARRAY_GENERATOR {desc} "ready") :: ptask_ready*',
        f'S_ready.OBJECTS[{obj}] = GENERATOR pgenerator_ready',
        'pgenerator_ready.PHASE = GENERATOR_PAUSED', 'pgenerator_ready.FIRST',
        'pgenerator_ready.VALUE = (PARRAY n_old)', 'pgenerator_ready.REFCELL = eps',
        '$string_bytes($generator_cache_value(pgenerator_ready.KEY)) = ($ptascii("ok"))',
        '$lookup(S_ready.ENV, $ptascii("it")) = eps',
        'S_ready.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$throwable_field(S_ready, n_second, "message") = pvalue_message',
        '$string_bytes(pvalue_message) = ($ptascii("supplied"))',
        '$throwable_field(S_ready, n_second, "previous") = PNULL',
        '$throwable_field(S_ready, n_second, "trace") = PARRAY n_trace',
        'S_ready.ARRAYS[n_trace].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_trace_frame))]',
        '$entry_lookup(S_ready.ARRAYS[n_trace_frame].ITEMS, KSTRING ($ptascii("function"))) = (DIRECT pvalue_function)',
        '$string_bytes(pvalue_function) = ($ptascii("array_spread_body_throw"))',
        '$entry_lookup(S_ready.ARRAYS[n_trace_frame].ITEMS, KSTRING ($ptascii("line"))) = (DIRECT (PINT 12))',
        f'$array_generator_valid(S_ready, {desc}, "ready")',
        f'$array_generator_ready(S_ready, {desc})',
        owners('S_ready', f'HOBJECT {obj}', 2), owners('S_ready', 'HARRAY n_old', 2),
        'PhpStep: S_ready ~> S_inserted',
        f'S_inserted.TODO = (ARRAY_GENERATOR {desc} "next") :: ptask_ready*',
        f'S_inserted.ARRAYS[{target}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2)), ENTRY (KSTRING ($ptascii("ok"))) (DIRECT (PARRAY n_old))]',
        f'S_inserted.ARRAYS[{target}].NEXT = 1',
        'S_inserted.OBJECTS = S_ready.OBJECTS', 'S_inserted.STORE = S_ready.STORE',
        owners('S_inserted', 'HARRAY n_old', 3),
        f'$heap_count(HARRAY n_old, $task_nodes(ARRAY_GENERATOR {desc} "next")) = 0',
    ] + public('S_ready') + public('S_inserted') + budget('S_ready', 'S_insert_budget')
    checks += seek('S_inserted', 81, 'S_resuming') + [
        f'S_resuming.OBJECTS[{obj}] = GENERATOR pgenerator_running',
        'pgenerator_running.PHASE = GENERATOR_RUNNING',
        'pgenerator_running.VALUE = (PARRAY n_old)',
        'S_resuming.STORE[n_row] = DEFINED (PARRAY n_old)',
        owners('S_resuming', 'HARRAY n_old', 3),
        'S_resuming.CURRENT = (pcallcontext)',
        f'pcallcontext.FUNCTION = {desc}.FUNCTION',
        'S_resuming.FRAMES = pframe :: pframe_tail*',
        f'pframe.TODO = (GENERATOR_RESUME pgeneratorop) :: (ARRAY_GENERATOR {desc} "next") :: ptask_ready*',
        f'pgeneratorop = {{OBJECT {obj}, NAME "next", SITE {desc}.SITE, LINE 12, LOOP eps, ADVANCE false, ARGUMENTS eps, STARTPACK true, BORROWED true}}',
        '$generator_operation_valid(S_resuming, pgeneratorop)',
        '$generator_operation_nodes(pgeneratorop) = eps',
        '$generator_operation_trace(S_resuming, pgeneratorop) = eps',
    ] + public('S_resuming')
    checks += seek('S_resuming', 82, 'S_throw') + [
        'S_throw.STORE[n_row] = DEFINED (PARRAY n_new)',
        'n_new =/= n_old', singleton('S_throw', 'n_new', 44),
        singleton('S_throw', 'n_old', 2),
        f'S_throw.OBJECTS[{obj}] = GENERATOR pgenerator_throwing',
        'pgenerator_throwing.PHASE = GENERATOR_RUNNING',
        'pgenerator_throwing.VALUE = (PARRAY n_old)',
        'S_throw.RESULT = KNOWN (POBJECT n_second)',
        owners('S_throw', 'HARRAY n_old', 2), owners('S_throw', 'HARRAY n_new', 1),
        output('S_throw', 'P;B;A;'),
    ] + public('S_throw')
    checks += seek('S_throw', 72, 'S_pending') + [
        f'S_pending.TODO = (THROW_SEARCH n_second) :: (ARRAY_GENERATOR {desc} "next") :: ptask_pending*',
        f'S_pending.OBJECTS[{obj}] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (PARRAY n_old)', 'pgenerator_closed.RETURN = eps',
        f'$node_children(S_pending, HOBJECT {obj}) = [HARRAY n_old]',
        '$throwable_field(S_pending, n_second, "trace") = PARRAY n_trace',
        'S_pending.ARRAYS[n_trace].ITEMS = S_ready.ARRAYS[n_trace].ITEMS',
        'S_pending.ARRAYS[n_trace_frame].ITEMS = S_ready.ARRAYS[n_trace_frame].ITEMS',
        '$throwable_field(S_pending, n_second, "previous") = PNULL',
        'S_pending.STORE[n_dest] = DEFINED (PINT 100)',
        'S_pending.STORE[n_later] = DEFINED (PINT 7)',
        owners('S_pending', f'HOBJECT {obj}', 2), owners('S_pending', 'HARRAY n_old', 2),
        output('S_pending', 'P;B;A;F;'),
        'PhpStep: S_pending ~> S_data_released',
        f'S_data_released.TODO = (THROW_SEARCH n_second) :: (ARRAY_GENERATOR {desc} "data-released") :: ptask_pending*',
        f'$array_generator_nodes({desc}, "data-released") = [HARRAY {target}]',
        owners('S_data_released', f'HOBJECT {obj}', 1),
        owners('S_data_released', 'HARRAY n_old', 2),
        owners('S_data_released', f'HARRAY {target}', 1),
        'S_data_released.OBJECTS = S_pending.OBJECTS',
        'S_data_released.ARRAYS = S_pending.ARRAYS',
        'S_data_released.STORE = S_pending.STORE',
        'PhpStep: S_data_released ~> S_input_released',
        f'S_input_released.TODO = (THROW_SEARCH n_second) :: (ARRAY_GENERATOR {desc} "input-released") :: ptask_pending*',
        f'$array_generator_valid(S_input_released, {desc}, "input-released")',
        '$throwable_live(S_input_released, n_second)',
        owners('S_input_released', 'HARRAY n_old', 2),
    ] + public('S_pending') + public('S_data_released') + public('S_input_released')
    checks += seek('S_input_released', 77, 'S_caught') + [
        f'~((HARRAY {target}) <- S_caught.ALLOCATIONS)',
        f'S_caught.OBJECTS[{obj}] = GENERATOR pgenerator_caught',
        'pgenerator_caught.PHASE = GENERATOR_CLOSED',
        'pgenerator_caught.VALUE = (PARRAY n_old)',
        owners('S_caught', 'HARRAY n_old', 1),
        owners('S_caught', 'HARRAY n_new', 1), owners('S_caught', f'HOBJECT {obj}', 1),
        '$lookup(S_caught.ENV, $ptascii("e")) = (n_caught)',
        'S_caught.STORE[n_caught] = DEFINED (POBJECT n_second)',
        'S_caught.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        '$throwable_field(S_caught, n_second, "trace") = PARRAY n_trace',
        '$throwable_field(S_caught, n_second, "previous") = PNULL',
        'S_caught.STORE[n_row] = DEFINED (PARRAY n_new)',
        'S_caught.STORE[n_dest] = DEFINED (PINT 100)',
        'S_caught.STORE[n_later] = DEFINED (PINT 7)',
    ] + public('S_caught')
    checks += finish('S_caught', stdout, [f'HARRAY {target}', f'HOBJECT {obj}',
                                        'HARRAY n_old', 'HARRAY n_new', 'HOBJECT n_second'])
    return checks


def acquisition(program, path, stdout):
    checks = initial(program, path)
    more, pre, active, desc, target, obj, gen, _ = entry(
        'S_initial', 'first', 9, 1, '[ENTRY (KINT 4) (DIRECT (PINT 88))]')
    checks += more + [
        f'{gen}.PHASE = GENERATOR_PAUSED', f'{gen}.FIRST',
        f'{gen}.VALUE = (PINT 2)', f'{gen}.REFCELL = eps',
        f'$string_bytes($generator_cache_value({gen}.KEY)) = ($ptascii("first"))',
        output(pre, 'P0;B;V0:2;'),
    ] + start(pre, active, desc, target, obj, 2) + budget(pre, 'S_first_budget')
    checks += seek(active, 71, 'S_first') + [
        f'S_first.TODO = (ARRAY_GENERATOR {desc} "ready") :: ptask_first_ready*',
        f'S_first.OBJECTS[{obj}] = GENERATOR {gen}',
        f'S_first.STORE = {pre}.STORE', f'S_first.EVENTS = {pre}.EVENTS',
        'PhpStep: S_first ~> S_first_inserted',
        f'S_first_inserted.TODO = (ARRAY_GENERATOR {desc} "next") :: ptask_first_ready*',
        f'S_first_inserted.ARRAYS[{target}].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 88)), ENTRY (KSTRING ($ptascii("first"))) (DIRECT (PINT 2))]',
        f'S_first_inserted.ARRAYS[{target}].NEXT = 5',
    ] + public('S_first') + public('S_first_inserted')
    checks += seek('S_first_inserted', 71, 'S_second') + [
        f'S_second.TODO = (ARRAY_GENERATOR {desc} "ready") :: ptask_second_ready*',
        f'S_second.OBJECTS[{obj}] = GENERATOR pgenerator_second',
        'pgenerator_second.PHASE = GENERATOR_PAUSED', '~pgenerator_second.FIRST',
        'pgenerator_second.VALUE = (PINT 3)', 'pgenerator_second.KEY = (PINT 7)',
        output('S_second', 'P0;B;V0:2;M;'),
        'PhpStep: S_second ~> S_second_inserted',
        f'S_second_inserted.TODO = (ARRAY_GENERATOR {desc} "next") :: ptask_second_ready*',
        f'S_second_inserted.ARRAYS[{target}].ITEMS = [ENTRY (KINT 4) (DIRECT (PINT 88)), ENTRY (KSTRING ($ptascii("first"))) (DIRECT (PINT 2)), ENTRY (KINT 5) (DIRECT (PINT 3))]',
        f'S_second_inserted.ARRAYS[{target}].NEXT = 6',
    ] + public('S_second') + public('S_second_inserted')
    checks += seek('S_second_inserted', 86, 'S_first_closed') + [
        f'S_first_closed.OBJECTS[{obj}] = GENERATOR pgenerator_first_closed',
        'pgenerator_first_closed.PHASE = GENERATOR_CLOSED',
        'pgenerator_first_closed.FRAME = eps',
        'pgenerator_first_closed.VALUE = (PINT 3)',
        'pgenerator_first_closed.KEY = (PINT 7)',
        'pgenerator_first_closed.RETURN = (PNULL)',
        f'$node_children(S_first_closed, HOBJECT {obj}) = eps',
        owners('S_first_closed', f'HOBJECT {obj}', 2),
        'PhpStep: S_first_closed ~> S_first_data_released',
        f'S_first_data_released.TODO = (ARRAY_GENERATOR {desc} "data-released") :: ptask_first_closed*',
        f'$array_generator_nodes({desc}, "data-released") = [HARRAY {target}]',
        owners('S_first_data_released', f'HOBJECT {obj}', 1),
        owners('S_first_data_released', f'HARRAY {target}', 1),
        'PhpStep: S_first_data_released ~> S_first_input_released',
        f'S_first_input_released.TODO = (ARRAY_GENERATOR {desc} "input-released") :: ptask_first_closed*',
        'PhpStep: S_first_input_released ~> S_first_transferred',
        f'S_first_transferred.TODO = (ARRAY_NEXT {target} {desc}.TAIL) :: ptask_first_closed*',
        f'S_first_transferred.ARRAYS[{target}].ITEMS = S_second_inserted.ARRAYS[{target}].ITEMS',
        owners('S_first_transferred', f'HOBJECT {obj}', 1),
        owners('S_first_transferred', f'HARRAY {target}', 1),
    ] + public('S_first_closed') + public('S_first_input_released') + public('S_first_transferred')
    more, pre_past, active_past, desc_past, target_past, obj_past, gen_past, _ = entry(
        'S_first_transferred', 'past', 15, 1, 'eps')
    checks += more + [
        f'{obj_past} =/= {obj}', f'{target_past} =/= {target}',
        f'~((HOBJECT {obj}) <- {pre_past}.ALLOCATIONS)',
        f'~((HARRAY {target}) <- {pre_past}.ALLOCATIONS)',
        f'{gen_past}.PHASE = GENERATOR_PAUSED', f'~{gen_past}.FIRST',
        f'{gen_past}.VALUE = (PINT 3)', f'{gen_past}.KEY = (PINT 7)',
        f'$lookup({pre_past}.ENV, $ptascii("dest")) = (n_dest)',
        f'$lookup({pre_past}.ENV, $ptascii("later")) = (n_later)',
        f'{pre_past}.STORE[n_dest] = DEFINED (PINT 101)',
        f'{pre_past}.STORE[n_later] = DEFINED (PINT 7)',
    ] + start(pre_past, active_past, desc_past, target_past, obj_past, 2)
    checks += seek(active_past, 72, 'S_past_pending') + [
        f'S_past_pending.TODO = (THROW_SEARCH n_past_error) :: (ARRAY_GENERATOR {desc_past} "rewind") :: ptask_past_pending*',
        f'S_past_pending.OBJECTS[{obj_past}] = GENERATOR {gen_past}',
        f'S_past_pending.ARRAYS[{target_past}].ITEMS = eps',
        '$throwable_field(S_past_pending, n_past_error, "message") = pvalue_past_message',
        '$string_bytes(pvalue_past_message) = ($ptascii("Cannot rewind a generator that was already run"))',
        '$throwable_field(S_past_pending, n_past_error, "line") = PINT 15',
        '$throwable_field(S_past_pending, n_past_error, "trace") = PARRAY n_past_trace',
        'S_past_pending.ARRAYS[n_past_trace].ITEMS = eps',
        owners('S_past_pending', f'HOBJECT {obj_past}', 2),
        'PhpStep: S_past_pending ~> S_past_data_released',
        f'S_past_data_released.TODO = (THROW_SEARCH n_past_error) :: (ARRAY_GENERATOR {desc_past} "data-released") :: ptask_past_pending*',
        owners('S_past_data_released', f'HOBJECT {obj_past}', 1),
        owners('S_past_data_released', f'HARRAY {target_past}', 1),
        'PhpStep: S_past_data_released ~> S_past_input_released',
        f'S_past_input_released.TODO = (THROW_SEARCH n_past_error) :: (ARRAY_GENERATOR {desc_past} "input-released") :: ptask_past_pending*',
        '$throwable_live(S_past_input_released, n_past_error)',
    ] + public('S_past_pending') + public('S_past_input_released')
    checks += seek('S_past_input_released', 83, 'S_past_caught') + [
        f'~((HARRAY {target_past}) <- S_past_caught.ALLOCATIONS)',
        f'S_past_caught.OBJECTS[{obj_past}] = GENERATOR {gen_past}',
        'S_past_caught.STORE[n_dest] = DEFINED (PINT 101)',
        'S_past_caught.STORE[n_later] = DEFINED (PINT 7)',
        owners('S_past_caught', f'HOBJECT {obj_past}', 1),
    ] + public('S_past_caught')
    more, pre_closed, _, desc_closed, target_closed, obj_closed, gen_closed, _ = entry(
        'S_past_caught', 'closed', 26, 1, 'eps')
    checks += more + [
        f'{obj_closed} = {obj_past}', f'{target_closed} =/= {target_past}',
        f'{gen_closed}.PHASE = GENERATOR_CLOSED', f'{gen_closed}.FRAME = eps',
        f'{gen_closed}.VALUE = (PINT 3)', f'{gen_closed}.KEY = (PINT 7)',
        f'{pre_closed}.STORE[n_dest] = DEFINED (PINT 102)',
        f'{pre_closed}.STORE[n_later] = DEFINED (PINT 7)',
        f'PhpStep: {pre_closed} ~> S_closed_rejected',
        owners('S_closed_rejected', f'HOBJECT {obj_closed}', 1),
        owners('S_closed_rejected', f'HARRAY {target_closed}', 1),
    ]
    checks += seek(pre_closed, 74, 'S_closed_pending') + [
        f'S_closed_pending.TODO = (THROW_SEARCH n_closed_error) :: (ARRAY_GENERATOR {desc_closed} "data-released") :: ptask_closed_pending*',
        f'$array_generator_nodes({desc_closed}, "data-released") = [HARRAY {target_closed}]',
        f'S_closed_pending.OBJECTS[{obj_closed}] = GENERATOR {gen_closed}',
        owners('S_closed_pending', f'HOBJECT {obj_closed}', 1),
        '$throwable_field(S_closed_pending, n_closed_error, "message") = pvalue_closed_message',
        '$string_bytes(pvalue_closed_message) = ($ptascii("Cannot traverse an already closed generator"))',
        '$throwable_field(S_closed_pending, n_closed_error, "line") = PINT 26',
        '$throwable_field(S_closed_pending, n_closed_error, "trace") = PARRAY n_closed_trace',
        'S_closed_pending.ARRAYS[n_closed_trace].ITEMS = eps',
        'S_closed_pending.ITERATORS = eps',
        'PhpStep: S_closed_pending ~> S_closed_input_released',
        f'S_closed_input_released.TODO = (THROW_SEARCH n_closed_error) :: (ARRAY_GENERATOR {desc_closed} "input-released") :: ptask_closed_pending*',
        owners('S_closed_input_released', f'HOBJECT {obj_closed}', 1),
    ] + public('S_closed_pending') + public('S_closed_input_released')
    checks += seek('S_closed_input_released', 85, 'S_closed_caught') + [
        f'~((HARRAY {target_closed}) <- S_closed_caught.ALLOCATIONS)',
        f'S_closed_caught.OBJECTS[{obj_closed}] = GENERATOR {gen_closed}',
        'S_closed_caught.STORE[n_dest] = DEFINED (PINT 102)',
        'S_closed_caught.STORE[n_later] = DEFINED (PINT 7)',
    ] + public('S_closed_caught')
    checks += finish('S_closed_caught', stdout, [f'HOBJECT {obj}', f'HARRAY {target}',
        f'HOBJECT {obj_past}', f'HARRAY {target_past}', f'HARRAY {target_closed}'])
    return checks


def conditions(name, program, path, stdout):
    if name.endswith('acquisition-states'):
        return acquisition(program, path, stdout)
    if name.endswith('shared-invalid-key'):
        return shared_invalid(program, path, stdout)
    assert name.endswith('body-supplied-throw')
    return body_throw(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
