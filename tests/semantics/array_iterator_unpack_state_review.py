#!/usr/bin/env python3
"""Source-reached spread key priority, cache ownership and abrupt retirement."""
import argparse
import base64
import json
import sys
from pathlib import Path

import array_iterator_unpack_review_cases as cases
import list_missing_warning_protocol as shared

THROW_PART = None
PARTITION_INFO = None

HELPERS = shared.HELPERS + r'''
dec $array_review_echo(pstate, ptbytes) : bool
def $array_review_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask_tail*
  -- if $base64(text) = n_prefix*
def $array_review_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 10) = true
  -- if S.TODO = (ARRAY_UNPACK n phpType13* z) :: ptask_tail*
def $list_warning_frontier(S, 11) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask_tail*
def $list_warning_frontier(S, 12) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "insert") :: ptask_tail*
def $list_warning_frontier(S, 14) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR parrayiterator text) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 15) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "next-start") :: ptask_tail*
def $list_warning_frontier(S, 16) = $array_review_echo(S, $ptascii("R:"))
def $list_warning_frontier(S, 20) = $array_review_echo(S, $ptascii("C0:"))
def $list_warning_frontier(S, 21) = $array_review_echo(S, $ptascii("C1:"))
def $list_warning_frontier(S, 22) = $array_review_echo(S, $ptascii("C2:"))
def $list_warning_frontier(S, 23) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "current-start") :: ptask_tail*
'''


def seek(start, stage, state):
    return [f'{state}_found = $list_warning_seek({start}, {stage}, 3000)',
            rf'{state}_found.COMPLETION = NORMAL \/ {state}_found.COMPLETION = BUDGET',
            f'{state} = {state}_found[.COMPLETION = NORMAL]',
            f'$list_warning_frontier({state}, {stage})']


def public(state):
    return [f'$heap_valid($heap_graph({state}))', f'$call_descriptors_valid({state})']


def budget(state, raw, label):
    fields = ('TODO RESULT BASE STORE ARRAYS OBJECTS OBJECTPROPS ALLOCATIONS '
              'ITERATORS NEXTITER ENV SOURCES CODE POOLS ORIGIN CURRENT FRAMES '
              'HELD EVENTS LITERALREFRETAINED LITERALREFDEBTS '
              'LITERALARRAYRETAINED LITERALARRAYDEBTS').split()
    return [f'{label}_paused = $drive_steps({state}, 0)',
            f'{label}_paused = {state}[.COMPLETION = BUDGET]',
            f'{label}_expected = $prune_allocations({raw})',
            f'{label}_found = $drive_steps({state}, 1)',
            f'{label}_found.COMPLETION = BUDGET',
            f'{label} = {label}_found[.COMPLETION = NORMAL]',
            *[f'{label}.{field} = {label}_expected.{field}' for field in fields],
            f'{label}_resumed = $drive_steps({label}_paused[.COMPLETION = NORMAL], 1)',
            f'{label}_resumed = {label}_found']


def owners(state, node, count):
    return f'$heap_owners($heap_graph({state}), {node}) = {count}'


def row(state, index, value):
    return f'{state}.ARRAYS[{index}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]'


def source_controls(state, desc):
    return [
        f'$array_iterator_source({state}, {desc})',
        f'~$array_iterator_source({state}[.CODE = eps], {desc})',
        f'~$array_iterator_source({state}[.SOURCES = eps], {desc})',
        f'~$array_iterator_source({state}, {desc}[.LINE = $({desc}.LINE + 1)])',
        f'~$array_iterator_source({state}, {desc}[.SITE = PORIGIN 0 eps])',
        f'~$array_iterator_source({state}, {desc}[.INPUT = KNOWN (POBJECT {desc}.OBJECT)])',
        f'~$array_iterator_source({state}, {desc}[.INPUT = VARIABLE ($ptascii("missing_iterator")) {desc}.LINE])',
        f'~$array_iterator_source({state}, {desc}[.ARRAY = |{state}.ARRAYS|])',
        f'~$array_iterator_source({state}, {desc}[.TAIL = eps])',
    ]


def entry(start, suffix, value, dest):
    pre, active, desc = f'S_pre_{suffix}', f'S_active_{suffix}', f'parrayiterator_{suffix}'
    target, obj, old = f'n_target_{suffix}', f'n_object_{suffix}', f'n_old_{suffix}'
    it, rowcell = f'n_it_{suffix}', f'n_row_{suffix}'
    checks = seek(start, 10, pre) + [
        f'{pre}.TODO = (ARRAY_UNPACK {target} phpType13_{suffix}* z_{suffix}) :: ptask_{suffix}*',
        f'{pre}.RESULT = VARIABLE ($ptascii("it")) z_{suffix}',
        f'$lookup({pre}.ENV, $ptascii("it")) = ({it})',
        f'{pre}.STORE[{it}] = DEFINED (POBJECT {obj})',
        f'$lookup({pre}.ENV, $ptascii("row")) = ({rowcell})',
        f'{pre}.STORE[{rowcell}] = DEFINED (PARRAY {old})', row(pre, old, value),
        f'$lookup({pre}.ENV, $ptascii("dest")) = (n_dest_{suffix})',
        f'{pre}.STORE[n_dest_{suffix}] = DEFINED (PINT {dest})',
        f'$lookup({pre}.ENV, $ptascii("later")) = (n_later_{suffix})',
        f'{pre}.STORE[n_later_{suffix}] = DEFINED (PINT 7)',
        f'{pre}.ARRAYS[{target}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {value}))]',
        f'$array_iterator_plan({pre}) = ({desc})',
        f'{desc}.ARRAY = {target}', f'{desc}.OBJECT = {obj}',
        f'{desc}.INPUT = {pre}.RESULT', f'{desc}.TAIL = phpType13_{suffix}*',
        f'{desc}.LINE = z_{suffix}', f'{desc}.ITERATOR = {pre}.NEXTITER',
        f'{pre}.ORIGIN = ({desc}.SITE)', f'{desc}.CURRENT = KNOWN PNULL',
        f'{desc}.KEY = KNOWN PNULL', f'$useriter_instance({pre}, {obj})',
        f'$node_children({pre}, HOBJECT {obj}) = eps',
        owners(pre, f'HOBJECT {obj}', 1), owners(pre, f'HARRAY {target}', 1),
        owners(pre, f'HARRAY {old}', 1),
        f'$task_nodes(ARRAY_UNPACK {target} phpType13_{suffix}* z_{suffix}) = [HARRAY {target}]',
    ] + source_controls(pre, desc) + public(pre) + [
        f'PhpStep: {pre} ~> {active}',
        f'{active}.TODO = (ARRAY_ITERATOR {desc} "rewind-start") :: ptask_{suffix}*',
        f'{active}.NEXTITER = $({pre}.NEXTITER + 1)',
        f'$iterator_lookup({active}.ITERATORS, {desc}.ITERATOR) = (OBJECTITER {desc}.ITERATOR {obj} 0 false)',
        f'$array_iterator_valid({active}, {desc}, "rewind-start")',
        f'$heap_count(HARRAY {target}, $task_nodes(ARRAY_ITERATOR {desc} "rewind-start")) = 1',
        f'$heap_count(HOBJECT {obj}, $task_nodes(ARRAY_ITERATOR {desc} "rewind-start")) = 1',
        owners(active, f'HOBJECT {obj}', 2), owners(active, f'HARRAY {target}', 1),
        f'{active}.STORE = {pre}.STORE', f'{active}.ARRAYS = {pre}.ARRAYS',
        f'{active}.ALLOCATIONS = {pre}.ALLOCATIONS', f'{active}.EVENTS = {pre}.EVENTS',
        f'~$array_iterator_valid({active}[.ITERATORS = eps], {desc}, "rewind-start")',
        f'~$array_iterator_valid({active}, {desc}[.ITERATOR = {active}.NEXTITER], "rewind-start")',
    ] + public(active) + budget(pre, active, f'S_started_{suffix}')
    return checks, pre, active, desc, target, obj, old


def cached(start, suffix, desc, target, obj, old, value):
    state, current = f'S_cached_{suffix}', f'parrayiterator_cached_{suffix}'
    dest = 100 if suffix == 'invalid' else 100 + int(suffix)
    checks = seek(start, 11, state) + [
        f'{state}.TODO = (ARRAY_ITERATOR {current} "key-start") :: ptask_cache_{suffix}*',
        f'{current}.SITE = {desc}.SITE', f'{current}.LINE = {desc}.LINE',
        f'{current}.ARRAY = {target}', f'{current}.OBJECT = {obj}',
        f'{current}.INPUT = {desc}.INPUT', f'{current}.TAIL = {desc}.TAIL',
        f'{current}.ITERATOR = {desc}.ITERATOR',
        f'{current}.CURRENT = KNOWN (PARRAY {old})', f'{current}.KEY = KNOWN PNULL',
        f'$array_iterator_valid({state}, {current}, "key-start")',
        f'$array_iterator_ready({state}, {current})',
        f'$heap_count(HARRAY {old}, $task_nodes(ARRAY_ITERATOR {current} "key-start")) = 1',
        f'$heap_count(HCELL n_row_{suffix}, $task_nodes(ARRAY_ITERATOR {current} "key-start")) = 0',
        owners(state, f'HARRAY {old}', 2), owners(state, f'HARRAY {target}', 1),
        owners(state, f'HOBJECT {obj}', 2), row(state, old, value),
        f'{state}.STORE[n_dest_{suffix}] = DEFINED (PINT {dest})',
        f'{state}.STORE[n_later_{suffix}] = DEFINED (PINT 7)',
        f'S_input_gone_{suffix} = {state}[.STORE[n_it_{suffix}] = DEFINED PNULL]',
        f'$array_iterator_source(S_input_gone_{suffix}, {current})',
        f'$array_iterator_valid(S_input_gone_{suffix}, {current}, "key-start")',
        f'$array_iterator_ready(S_input_gone_{suffix}, {current})',
        owners(f'S_input_gone_{suffix}', f'HOBJECT {obj}', 1),
    ] + public(state) + public(f'S_input_gone_{suffix}')
    return checks, state, current


def finish(start, stdout):
    return seek(start, 16, 'S_read') + public('S_read') + [
        'S_done = $drive_steps(S_read, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.RESULT = KNOWN PNULL',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        'S_done.LITERALREFRETAINED = eps', 'S_done.LITERALREFDEBTS = eps',
        'S_done.LITERALARRAYRETAINED = eps', 'S_done.LITERALARRAYDEBTS = eps',
    ] + public('S_done')


def generator_checks(program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ] + seek('S_initial', 10, 'S') + [
        'S.TODO = (ARRAY_UNPACK n_target eps z) :: ptask_tail*',
        'S.RESULT = VARIABLE ($ptascii("it")) z',
        '$lookup(S.ENV, $ptascii("it")) = (n_it)', 'S.STORE[n_it] = DEFINED (POBJECT n_object)',
        'S.OBJECTS[n_object] = GENERATOR pgenerator', '$config_traversable_value(S, POBJECT n_object)',
        '~$useriter_instance(S, n_object)', '$array_iterator_plan(S) = eps',
        '$array_generator_plan(S) = (parraygenerator)', '$array_generator_pending(S)',
        'parraygenerator.ARRAY = n_target', 'parraygenerator.OBJECT = n_object',
        'parraygenerator.INPUT = S.RESULT', 'parraygenerator.TAIL = eps',
        'parraygenerator.FUNCTION = pgenerator.FUNCTION', 'parraygenerator.LINE = z',
        'pgenerator.PHASE = GENERATOR_FRESH',
        '$lookup(S.ENV, $ptascii("out")) = (n_out)', 'S.STORE[n_out] = DEFINED (PINT 100)',
        '$lookup(S.ENV, $ptascii("later")) = (n_later)', 'S.STORE[n_later] = DEFINED (PINT 7)',
        'S.ARRAYS[n_target].ITEMS = eps', 'S.ITERATORS = eps',
        '$list_warning_outputs(S.EVENTS) = ($ptascii("P;"))',
        owners('S', 'HOBJECT n_object', 1), owners('S', 'HARRAY n_target', 1),
        'PhpStep: S ~> S_started',
        'S_started.TODO = (ARRAY_GENERATOR parraygenerator "rewind") :: ptask_tail*',
        '$array_generator_valid(S_started, parraygenerator, "rewind")',
        '$task_nodes(ARRAY_GENERATOR parraygenerator "rewind") = [HARRAY n_target, HOBJECT n_object]',
        owners('S_started', 'HOBJECT n_object', 2), owners('S_started', 'HARRAY n_target', 1),
        'S_started.STORE = S.STORE', 'S_started.ARRAYS = S.ARRAYS',
        'S_started.OBJECTS = S.OBJECTS', 'S_started.ITERATORS = eps',
        'S_started.NEXTITER = S.NEXTITER',
        '$list_warning_outputs(S_started.EVENTS) = ($ptascii("P;"))',
    ] + public('S_started') + seek('S_started', 16, 'S_read') + [
        'S_read.STORE[n_out] = DEFINED (PARRAY n_target)',
        'S_read.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 3))]',
        'S_read.STORE[n_later] = DEFINED (PINT 88)',
        'S_read.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.VALUE = (PINT 3)',
        'pgenerator_closed.KEY = (PINT 0)', 'pgenerator_closed.RETURN = (PNULL)',
        owners('S_read', 'HOBJECT n_object', 1), owners('S_read', 'HARRAY n_target', 1),
        '$list_warning_outputs(S_read.EVENTS) = ($ptascii("P;G;"))',
    ] + public('S_read') + [
        'S_done = $drive_steps(S_read, 4000)', 'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps', 'S_done.CURRENT = eps', 'S_done.FRAMES = eps',
        'S_done.ITERATORS = eps', 'S_done.RESULT = KNOWN PNULL',
        '$list_warning_outputs(S_done.EVENTS) = ([' + ','.join(map(str, stdout)) + '])',
        '~((HOBJECT n_object) <- S_done.ALLOCATIONS)', '~((HARRAY n_target) <- S_done.ALLOCATIONS)',
    ] + public('S_done')
    return checks


def invalid_checks(program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    more, pre, active, desc, target, obj, old = entry('S_initial', 'invalid', 2, 100)
    checks += more + [
        'z_invalid = 13',
        'S_array_input = S_pre_invalid[.STORE[n_it_invalid] = DEFINED (PARRAY n_old_invalid)]',
        '$heap_valid($heap_graph(S_array_input))',
        '~$array_iterator_pending(S_array_input)', '$array_iterator_plan(S_array_input) = eps',
        'PhpStep: S_array_input ~> S_array_done',
        'S_array_done.TODO = (ARRAY_NEXT n_target_invalid phpType13_invalid*) :: ptask_invalid*',
        'S_array_done.RESULT = KNOWN PNULL', 'S_array_done.COMPLETION = NORMAL',
        'S_array_done.ARRAYS[n_target_invalid].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2)), ENTRY (KINT 1) (DIRECT (PINT 2))]',
        row('S_array_done', 'n_old_invalid', 2),
        'S_array_done.STORE = S_array_input.STORE', 'S_array_done.CODE = S_array_input.CODE',
        'S_array_done.POOLS = S_array_input.POOLS', 'S_array_done.ITERATORS = eps',
        'S_array_done.EVENTS = S_array_input.EVENTS',
    ] + public('S_array_done') + budget('S_array_input', 'S_array_done', 'S_array_driven')
    more, state, current = cached(active, 'invalid', desc, target, obj, old, 2)
    checks += more + [
        'S_object_current = S_cached_invalid[.ARRAYS[n_old_invalid].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object_invalid))]]',
        '$heap_valid($heap_graph(S_object_current))',
        '$array_iterator_source(S_object_current, parrayiterator_cached_invalid)',
        '$array_iterator_valid(S_object_current, parrayiterator_cached_invalid, "key-start")',
        '~$array_iterator_ready(S_object_current, parrayiterator_cached_invalid)',
        'PhpStep: S_object_current ~> S_object_refused',
        'S_object_refused = S_object_current[.COMPLETION = UNSUPPORTED "array Iterator unpack state outside quiet payload domain"]',
        'S_nested_current = S_cached_invalid[.ARRAYS[n_old_invalid].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_target_invalid))]]',
        '$heap_valid($heap_graph(S_nested_current))',
        '$array_iterator_source(S_nested_current, parrayiterator_cached_invalid)',
        '~$array_iterator_ready(S_nested_current, parrayiterator_cached_invalid)',
        'S_current_debt = S_cached_invalid[.LITERALARRAYDEBTS = [n_old_invalid]]',
        '~$array_iterator_ready(S_current_debt, parrayiterator_cached_invalid)',
        '$call_line_valid(S_cached_invalid, (parrayiterator_cached_invalid.SITE), 13)',
        '~$call_line_valid(S_cached_invalid, (parrayiterator_cached_invalid.SITE), 14)',
        'PhpStep: S_cached_invalid ~> S_key_call',
        'S_key_call.TODO = (CALL_ARGS (UNPACK_ITERATOR_TARGET n_object_invalid porigin_key) eps 0 eps (parrayiterator_cached_invalid.SITE) 13) :: (ARRAY_ITERATOR parrayiterator_cached_invalid "key") :: ptask_cache_invalid*',
        '$target_nodes(UNPACK_ITERATOR_TARGET n_object_invalid porigin_key) = eps',
        '$useriter_pending(S_key_call, UNPACK_ITERATOR_TARGET n_object_invalid porigin_key, parrayiterator_cached_invalid.SITE)',
        '$call_selected_valid(S_key_call, UNPACK_ITERATOR_TARGET n_object_invalid porigin_key, (parrayiterator_cached_invalid.SITE))',
        owners('S_key_call', 'HOBJECT n_object_invalid', 2), owners('S_key_call', 'HARRAY n_old_invalid', 2),
    ] + public('S_key_call') + budget('S_cached_invalid', 'S_key_call', 'S_key_call_driven')
    checks += seek(state, 12, 'S_insert') + [
        'S_insert.TODO = (ARRAY_ITERATOR parrayiterator_insert "insert") :: ptask_insert*',
        'parrayiterator_insert.CURRENT = KNOWN (PARRAY n_old_invalid)',
        'parrayiterator_insert.KEY = KNOWN (PBOOL true)',
        'parrayiterator_insert.ARRAY = n_target_invalid',
        '$array_iterator_source(S_insert, parrayiterator_insert)',
        '$array_iterator_valid(S_insert, parrayiterator_insert, "insert")',
        'S_insert.STORE[n_row_invalid] = DEFINED (PARRAY n_new_invalid)',
        'n_new_invalid =/= n_old_invalid',
        row('S_insert', 'n_old_invalid', 2), row('S_insert', 'n_new_invalid', 44),
        owners('S_insert', 'HARRAY n_old_invalid', 1), owners('S_insert', 'HARRAY n_new_invalid', 1),
        owners('S_insert', 'HARRAY n_target_invalid', 1), owners('S_insert', 'HOBJECT n_object_invalid', 2),
        'S_insert.ARRAYS[n_target_invalid].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]',
        '$list_warning_outputs(S_insert.EVENTS) = ($ptascii("P;W;V;C;K;"))',
        'PhpStep: S_insert ~> S_invalid',
        'S_invalid.COMPLETION = THROWN "Error" ($ptascii("Keys must be of type int|string during array unpacking")) 13',
        'S_invalid.ARRAYS = S_insert.ARRAYS', 'S_invalid.STORE[n_dest_invalid] = DEFINED (PINT 100)',
        'S_invalid.STORE[n_later_invalid] = DEFINED (PINT 7)',
        'S_invalid.EVENTS = S_insert.EVENTS',
        'S_invalid_started = $drive_steps(S_invalid, 1)',
        'S_invalid_started.COMPLETION = BUDGET',
    ] + finish('S_invalid_started', stdout) + [
        'S_read.STORE[n_dest_invalid] = DEFINED (PINT 100)',
        'S_read.STORE[n_later_invalid] = DEFINED (PINT 7)',
        'S_read.STORE[n_row_invalid] = DEFINED (PARRAY n_new_invalid)',
        row('S_read', 'n_new_invalid', 44),
        '~((HARRAY n_old_invalid) <- S_read.ALLOCATIONS)',
        '~((HARRAY n_target_invalid) <- S_read.ALLOCATIONS)',
        '$lookup(S_read.ENV, $ptascii("it")) = (n_it_invalid)',
        'S_read.STORE[n_it_invalid] = DEFINED (POBJECT n_object_invalid)',
        owners('S_read', 'HOBJECT n_object_invalid', 1),
        '$lookup(S_read.ENV, $ptascii("e")) = eps',
        '~((HARRAY n_new_invalid) <- S_done.ALLOCATIONS)',
        '~((HOBJECT n_object_invalid) <- S_done.ALLOCATIONS)',
        '~((HCELL n_dest_invalid) <- S_done.ALLOCATIONS)',
        '~((HCELL n_later_invalid) <- S_done.ALLOCATIONS)',
    ]
    return checks


def thrown_stage(start, mode, desc, target, obj, old):
    state, current = f'S_throw_{mode}', f'parrayiterator_throw_{mode}'
    stage = ('current', 'key', 'next')[mode]
    checks = seek(start, 14, state) + [
        f'{state}.TODO = (THROW_SEARCH n_second) :: (ARRAY_ITERATOR {current} "{stage}") :: ptask_throw_{mode}*',
        f'{current}.SITE = {desc}.SITE', f'{current}.LINE = {desc}.LINE',
        f'{current}.ARRAY = {target}', f'{current}.OBJECT = {obj}',
        f'{current}.ITERATOR = {desc}.ITERATOR', f'{current}.INPUT = {desc}.INPUT',
        f'{current}.TAIL = {desc}.TAIL', f'{current}.KEY = KNOWN PNULL',
        f'$array_iterator_source({state}, {current})',
        f'$array_iterator_valid({state}, {current}, "{stage}")',
        f'{state}.STORE[n_dest_{mode}] = DEFINED (PINT {100 + mode})',
        f'{state}.STORE[n_later_{mode}] = DEFINED (PINT 7)',
        f'$throwable_previous_id({state}, n_second) = eps',
        owners(state, f'HOBJECT {obj}', 2 if mode == 0 else 1),
        owners(state, f'HARRAY {target}', 1),
    ]
    if mode == 0:
        checks += [f'{current}.CURRENT = KNOWN PNULL',
                   f'{state}.STORE[n_row_0] = DEFINED (PARRAY {old})', row(state, old, 22),
                   owners(state, f'HARRAY {old}', 1),
                   f'$heap_count(HARRAY {old}, $task_nodes(ARRAY_ITERATOR {current} "{stage}")) = 0',
                   f'{state}.ARRAYS[{target}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 2))]']
    else:
        checks += [f'{state}.STORE[n_row_{mode}] = DEFINED (PARRAY n_new_{mode})',
                   row(state, f'n_new_{mode}', 44 if mode == 1 else 55), row(state, old, 7),
                   owners(state, f'HARRAY n_new_{mode}', 1), owners(state, f'HARRAY {old}', 1),
                   f'$lookup({state}.ENV, $ptascii("it")) = eps']
        if mode == 1:
            checks += [f'{current}.CURRENT = KNOWN (PARRAY {old})',
                       f'$heap_count(HARRAY {old}, $task_nodes(ARRAY_ITERATOR {current} "{stage}")) = 1',
                       f'{state}.ARRAYS[{target}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]']
        else:
            checks += [f'{current}.CURRENT = KNOWN PNULL',
                       f'$heap_count(HARRAY {old}, $task_nodes(ARRAY_ITERATOR {current} "{stage}")) = 0',
                       f'{state}.ARRAYS[{target}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY {old}))]']
    released, retired = f'S_released_{mode}', f'S_retired_{mode}'
    checks += public(state) + [
        f'S_popped_{mode} = {state}[.TODO = (THROW_SEARCH n_second) :: ptask_throw_{mode}*]',
        f'S_direct_{mode} = $return_discard(S_popped_{mode}, ARRAY_ITERATOR {current} "{stage}")',
        f'PhpStep: {state} ~> {released}',
        f'{released} = S_direct_{mode}',
        f'{released}.TODO = (THROW_SEARCH n_second) :: ptask_throw_{mode}*',
        f'{released}.COMPLETION = NORMAL',
        f'{released}.ITERATORS = $iterator_remove({state}.ITERATORS, {desc}.ITERATOR)',
        f'{released}.ARRAYS = {state}.ARRAYS', f'{released}.EVENTS = {state}.EVENTS',
        f'{released}.ALLOCATIONS = {state}.ALLOCATIONS',
        f'{released}.STORE[n_dest_{mode}] = DEFINED (PINT {100 + mode})',
        f'{released}.STORE[n_later_{mode}] = DEFINED (PINT 7)',
        owners(released, f'HARRAY {target}', 0),
        f'{retired} = $prune_allocations({released})',
        f'~((HARRAY {target}) <- {retired}.ALLOCATIONS)',
    ]
    if mode == 0:
        checks += [f'(HOBJECT {obj}) <- {retired}.ALLOCATIONS', owners(retired, f'HOBJECT {obj}', 1),
                   f'(HARRAY {old}) <- {retired}.ALLOCATIONS', owners(retired, f'HARRAY {old}', 1)]
    else:
        checks += [owners(released, f'HOBJECT {obj}', 0), owners(released, f'HARRAY {old}', mode - 1),
                   f'~((HOBJECT {obj}) <- {retired}.ALLOCATIONS)',
                   f'~((HARRAY {old}) <- {retired}.ALLOCATIONS)',
                   f'(HARRAY n_new_{mode}) <- {retired}.ALLOCATIONS', owners(retired, f'HARRAY n_new_{mode}', 1)]
    checks += public(released) + public(retired) + budget(state, released, f'S_discard_driven_{mode}')
    checks += seek(retired, 20 + mode, f'S_catch_{mode}') + [
        f'S_catch_{mode}.STORE[n_dest_{mode}] = DEFINED (PINT {100 + mode})',
        f'S_catch_{mode}.STORE[n_later_{mode}] = DEFINED (PINT 7)',
        f'$throwable_previous_id(S_catch_{mode}, n_second) = eps',
    ] + public(f'S_catch_{mode}')
    return checks, f'S_catch_{mode}'


def throw_checks(program, path, stdout):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(base64.b64encode(bytes(path)).decode()) + ')',
        'S_initial.COMPLETION = BUDGET',
    ]
    start = 'S_initial'
    for mode in range(3):
        suffix = str(mode)
        more, pre, active, desc, target, obj, old = entry(start, suffix, 2 if mode == 0 else 7, 100 + mode)
        checks += more
        if mode == 0:
            checks += [f'$lookup({pre}.ENV, $ptascii("second")) = (n_second_cell)',
                       f'{pre}.STORE[n_second_cell] = DEFINED (POBJECT n_second)']
            checks += seek(active, 23, 'S_before_current_0') + [
                'S_before_current_0.TODO = (ARRAY_ITERATOR parrayiterator_before_current "current-start") :: ptask_current*',
                'parrayiterator_before_current.CURRENT = KNOWN PNULL',
                owners('S_before_current_0', f'HARRAY {old}', 1),
            ]
            start = 'S_before_current_0'
        else:
            more, start, current = cached(active, suffix, desc, target, obj, old, 7)
            checks += more
            if mode == 2:
                checks += seek(start, 15, 'S_before_next_2') + [
                    'S_before_next_2.TODO = (ARRAY_ITERATOR parrayiterator_before_next "next-start") :: ptask_next*',
                    'parrayiterator_before_next.CURRENT = KNOWN PNULL',
                    'parrayiterator_before_next.KEY = KNOWN PNULL',
                    f'S_before_next_2.ARRAYS[{target}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7)), ENTRY (KINT 1) (DIRECT (PARRAY {old}))]',
                    owners('S_before_next_2', f'HARRAY {old}', 1),
                    '$heap_count(HARRAY n_old_2, $task_nodes(ARRAY_ITERATOR parrayiterator_before_next "next-start")) = 0',
                    '$lookup(S_before_next_2.ENV, $ptascii("it")) = eps',
                    owners('S_before_next_2', f'HOBJECT {obj}', 1),
                    'S_before_next_2.STORE[n_row_2] = DEFINED (PARRAY n_new_2)',
                    row('S_before_next_2', 'n_new_2', 44),
                ] + public('S_before_next_2')
                start = 'S_before_next_2'
        more, start = thrown_stage(start, mode, desc, target, obj, old)
        checks += more
    checks += finish(start, stdout) + [
        'S_read.STORE[n_dest_2] = DEFINED (PINT 102)', 'S_read.STORE[n_later_2] = DEFINED (PINT 7)',
        'S_read.STORE[n_row_2] = DEFINED (PARRAY n_new_2)', row('S_read', 'n_new_2', 55),
        '$lookup(S_read.ENV, $ptascii("it")) = eps', '$lookup(S_read.ENV, $ptascii("e")) = eps',
        '$throwable_previous_id(S_read, n_second) = eps', '~((HOBJECT n_second) <- S_done.ALLOCATIONS)',
        '~((HCELL n_dest_2) <- S_done.ALLOCATIONS)', '~((HCELL n_later_2) <- S_done.ALLOCATIONS)',
    ]
    for mode in range(3):
        checks += [f'~((HARRAY n_target_{mode}) <- S_done.ALLOCATIONS)',
                   f'~((HARRAY n_old_{mode}) <- S_done.ALLOCATIONS)',
                   f'~((HOBJECT n_object_{mode}) <- S_done.ALLOCATIONS)']
    checks += ['~((HARRAY n_new_1) <- S_done.ALLOCATIONS)', '~((HARRAY n_new_2) <- S_done.ALLOCATIONS)']
    return checks


def throw_partition(checks, part):
    """Check each existing throw group separately, with source-driven setup."""
    key_start = checks.index('S_pre_1_found = $list_warning_seek(S_catch_0, 10, 3000)')
    next_start = checks.index('S_pre_2_found = $list_warning_seek(S_catch_1, 10, 3000)')
    groups = {'current': checks[:key_start], 'key': checks[key_start:next_start], 'next': checks[next_start:]}
    assert groups['current'] + groups['key'] + groups['next'] == checks

    def identities(mode):
        state = f'S_pre_{mode}'
        return [f'{state}.TODO = (ARRAY_UNPACK n_target_{mode} phpType13_{mode}* z_{mode}) :: ptask_{mode}*',
                f'$lookup({state}.ENV, $ptascii("it")) = (n_it_{mode})',
                f'{state}.STORE[n_it_{mode}] = DEFINED (POBJECT n_object_{mode})',
                f'$lookup({state}.ENV, $ptascii("row")) = (n_row_{mode})',
                f'{state}.STORE[n_row_{mode}] = DEFINED (PARRAY n_old_{mode})']

    setup = []
    if part == 'key':
        setup = checks[:2] + seek('S_initial', 20, 'S_catch_0') + [
            '$lookup(S_catch_0.ENV, $ptascii("second")) = (n_second_cell)',
            'S_catch_0.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        ]
    if part == 'next':
        setup = checks[:2] + seek('S_initial', 10, 'S_pre_0') + identities(0) + [
            '$lookup(S_pre_0.ENV, $ptascii("second")) = (n_second_cell)',
            'S_pre_0.STORE[n_second_cell] = DEFINED (POBJECT n_second)',
        ] + seek('S_pre_0', 20, 'S_catch_0') + seek('S_catch_0', 10, 'S_pre_1') + identities(1)
        setup += seek('S_pre_1', 21, 'S_catch_1') + [
            'S_catch_1.STORE[n_row_1] = DEFINED (PARRAY n_new_1)',
        ]
    return setup + groups[part], len(groups[part]), len(setup)


def conditions(name, program, path, stdout):
    global PARTITION_INFO
    if THROW_PART is not None:
        assert name.endswith('supplied-throw'), '--throw-part requires the supplied-throw case'
    if name.endswith('generator-boundary'):
        return generator_checks(program, path, stdout)
    if name.endswith('invalid-bool-key'):
        return invalid_checks(program, path, stdout)
    assert name.endswith('supplied-throw')
    checks = throw_checks(program, path, stdout)
    assert THROW_PART is not None, 'supplied-throw requires --throw-part current, key, or next'
    selected, original, bootstrap = throw_partition(checks, THROW_PART)
    PARTITION_INFO = {'group': THROW_PART, 'original_case': name,
                      'original_conditions': original, 'bootstrap_conditions': bootstrap,
                      'full_original_conditions': len(checks)}
    return selected


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--throw-part', choices=('current', 'key', 'next'))
    parser.add_argument('--output', type=Path)
    options, remaining = parser.parse_known_args()
    THROW_PART = options.throw_part
    if options.output is not None:
        remaining += ['--output', str(options.output)]
    sys.argv = [sys.argv[0], *remaining]
    passed = shared.run(cases, conditions, HELPERS)
    if THROW_PART is not None:
        report_path = options.output / 'report.json'
        report = json.loads(report_path.read_text())
        report['partition'] = PARTITION_INFO
        report_path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
