#!/usr/bin/env python3
"""Nested cache DAG edges, quiet Iterator discard and staged Generator retirement."""
import array_traversable_nested_cache_review_cases as cases
import list_missing_warning_protocol as shared
from array_aggregate_unpack_state_review import initial, seek
from array_generator_unpack_state_review import budget, finish, owners, public

HELPERS = shared.HELPERS + r'''
dec $nested_cache_echo(pstate, ptbytes) : bool
def $nested_cache_echo(S, n_prefix*) = true
  -- if S.TODO = (STMT (NStmtEcho (SEQUENCE ((NScalarString (BYTES text) metadata_string) :: expression_tail*)) metadata)) :: ptask*
  -- if $base64(text) = n_prefix*
def $nested_cache_echo(S, n_prefix*) = false -- otherwise
def $list_warning_frontier(S, 150) = true
  -- if S.TODO = (ARRAY_UNPACK n phpType13* z) :: ptask*
def $list_warning_frontier(S, 151) = true
  -- if S.TODO = (ARRAY_ITERATOR parrayiterator "key-start") :: ptask*
def $list_warning_frontier(S, 152) = true
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask*
  -- if S.CURRENT = (pcallcontext)
def $list_warning_frontier(S, 153) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_ITERATOR parrayiterator text) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 154) = $nested_cache_echo(S, $ptascii("C:"))
def $list_warning_frontier(S, 155) = true
  -- if S.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask*
  -- if S.OBJECTS[parraygenerator.OBJECT] = GENERATOR pgenerator
  -- if pgenerator.PHASE = GENERATOR_PAUSED
def $list_warning_frontier(S, 156) = $nested_cache_echo(S, $ptascii("F:"))
def $list_warning_frontier(S, 157) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "next") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 158) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $list_warning_frontier(S, 159) = true
  -- if S.TODO = (THROW_SEARCH n) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def pair(state, array, first):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {first})),ENTRY (KINT 1) (DIRECT (PINT 7))]'


def graph(state):
    return [
        f'{state}.ARRAYS[n_tree].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_upper))]',
        f'{state}.ARRAYS[n_upper].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_deep))]',
        f'{state}.ARRAYS[n_deep].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf))]',
        pair(state, 'n_leaf', 2),
    ]


def entry(program, path):
    return initial(program, path) + seek('S_initial', 150, 'S_pre') + [
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        'S_pre.RESULT = VARIABLE ($ptascii("it")) z',
        '$lookup(S_pre.ENV, $ptascii("it")) = (n_it)',
        'S_pre.STORE[n_it] = DEFINED (POBJECT n_object)',
        '$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf_cell)',
        'S_pre.STORE[n_leaf_cell] = DEFINED (PARRAY n_leaf)',
        '$lookup(S_pre.ENV, $ptascii("tree")) = (n_tree_cell)',
        'S_pre.STORE[n_tree_cell] = DEFINED (PARRAY n_tree)',
        '$lookup(S_pre.ENV, $ptascii("before")) = (n_before)',
        'S_pre.STORE[n_before] = DEFINED (PARRAY n_leaf)',
        '$lookup(S_pre.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_pre.ENV, $ptascii("later")) = (n_later)',
        '$lookup(S_pre.ENV, $ptascii("second")) = (n_second)',
        'S_pre.STORE[n_second] = DEFINED (POBJECT n_exception)',
        'S_pre.STORE[n_dest] = DEFINED (PINT 99)',
        'S_pre.STORE[n_later] = DEFINED (PINT 7)',
        'S_pre.ARRAYS[n_target].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf))]',
        'S_pre.ARRAYS[n_tree].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_leaf)),ENTRY (KINT 1) (DIRECT (PARRAY n_upper))]',
        'S_pre.ARRAYS[n_upper].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_deep))]',
        *[f'$heap_count(HARRAY {node}, $pools_nodes(S_pre.POOLS)) = 0' for node in ['n_tree', 'n_upper', 'n_deep', 'n_leaf']],
        owners('S_pre', 'HARRAY n_leaf', 5), owners('S_pre', 'HARRAY n_target', 1),
        owners('S_pre', 'HARRAY n_upper', 1), owners('S_pre', 'HARRAY n_deep', 1),
        owners('S_pre', 'HOBJECT n_object', 1),
    ] + graph('S_pre') + public('S_pre')


def cache_controls(state, descriptor, generator=False):
    ready = 'array_generator_ready' if generator else 'array_iterator_ready'
    source = 'array_generator_source' if generator else 'array_iterator_source'
    reason = 'array Generator cache or builder outside direct domain' if generator else 'array Iterator unpack state outside quiet payload domain'
    return [
        f'$array_iterator_table({state}, n_tree)',
        f'$entries_nodes({state}.ARRAYS[n_tree].ITEMS) = [HARRAY n_leaf,HARRAY n_upper]',
        f'S_cycle = {state}[.ARRAYS[n_tree].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_tree))]]',
        '$heap_valid($heap_graph(S_cycle))', '~$array_iterator_table(S_cycle, n_tree)',
        f'~${ready}(S_cycle, {descriptor})',
        f'S_alias = {state}[.REFCELLS = n_before :: {state}.REFCELLS][.ARRAYS[n_tree].ITEMS = [ENTRY (KINT 0) (ALIAS n_before)]]',
        '$heap_valid($heap_graph(S_alias))', '~$array_iterator_table(S_alias, n_tree)',
        f'~${ready}(S_alias, {descriptor})',
        f'S_object = {state}[.ARRAYS[n_tree].ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_object))]]',
        '$heap_valid($heap_graph(S_object))', '~$array_iterator_table(S_object, n_tree)',
        f'~${ready}(S_object, {descriptor})',
        f'S_debt = {state}[.LITERALARRAYDEBTS = n_deep :: {state}.LITERALARRAYDEBTS]',
        '$heap_valid($heap_graph(S_debt))', '~$array_iterator_table(S_debt, n_tree)',
        f'~${ready}(S_debt, {descriptor})',
        f'S_cross = {state}[.ARRAYS[n_tree].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_target))]]',
        '$heap_valid($heap_graph(S_cross))', '$array_iterator_table(S_cross, n_tree)',
        f'${source}(S_cross, {descriptor})', f'~${ready}(S_cross, {descriptor})',
        'PhpStep: S_cross ~> S_cross_refused',
        f'S_cross_refused = S_cross[.COMPLETION = UNSUPPORTED "{reason}"]',
    ] + (['$drive_steps(S_cross_refused, 2) = S_cross_refused'] if generator else [])


def caught(state, later):
    return [
        f'{state}.STORE[n_dest] = DEFINED (PINT 99)', f'{state}.STORE[n_later] = DEFINED (PINT {later})',
        f'{state}.STORE[n_before] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_leaf', pair(state, 'n_copy', 44),
        owners(state, 'HARRAY n_copy', 1),
        *[f'~((HARRAY {node}) <- {state}.ALLOCATIONS)' for node in ['n_target', 'n_tree', 'n_upper', 'n_deep', 'n_leaf']],
    ] + public(state)


def key_throw(program, path, stdout):
    checks = entry(program, path) + [
        '$array_iterator_plan(S_pre) = (parrayiterator)',
        'parrayiterator.ARRAY = n_target', 'parrayiterator.OBJECT = n_object',
        'parrayiterator.INPUT = S_pre.RESULT', 'parrayiterator.TAIL = phpType13*',
        'parrayiterator.LINE = z', 'parrayiterator.ITERATOR = S_pre.NEXTITER',
        'PhpStep: S_pre ~> S_active',
        'S_active.TODO = (ARRAY_ITERATOR parrayiterator "rewind-start") :: ptask_tail*',
        'S_active.ITERATORS = S_pre.ITERATORS ++ [OBJECTITER parrayiterator.ITERATOR n_object 0 false]',
        'S_active.NEXTITER = $(S_pre.NEXTITER + 1)',
        owners('S_active', 'HOBJECT n_object', 2),
    ] + public('S_active') + budget('S_pre', 'S_entry_budget') + seek('S_active', 151, 'S_cache') + [
        'S_cache.TODO = (ARRAY_ITERATOR parrayiterator_cached "key-start") :: ptask_tail*',
        'parrayiterator_cached = parrayiterator[.CURRENT = KNOWN (PARRAY n_tree)]',
        '$array_iterator_source(S_cache, parrayiterator_cached)',
        '$array_iterator_ready(S_cache, parrayiterator_cached)',
        '~((HCELL n_tree_cell) <- S_cache.ALLOCATIONS)', '~((HCELL n_leaf_cell) <- S_cache.ALLOCATIONS)',
        '$lookup(S_cache.ENV, $ptascii("tree")) = eps', '$lookup(S_cache.ENV, $ptascii("leaf")) = eps',
        owners('S_cache', 'HARRAY n_tree', 1), owners('S_cache', 'HARRAY n_leaf', 4),
        owners('S_cache', 'HARRAY n_upper', 1), owners('S_cache', 'HARRAY n_deep', 1),
    ] + graph('S_cache') + public('S_cache') + cache_controls('S_cache', 'parrayiterator_cached')
    checks += seek('S_cache', 152, 'S_body') + [
        'S_body.STORE[n_before] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_leaf', pair('S_body', 'n_copy', 44),
        owners('S_body', 'HARRAY n_copy', 1), owners('S_body', 'HARRAY n_leaf', 3),
        owners('S_body', 'HARRAY n_tree', 1), owners('S_body', 'HARRAY n_target', 1),
    ] + public('S_body') + seek('S_body', 153, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_exception) :: (ARRAY_ITERATOR parrayiterator_cached "key") :: ptask_tail*',
        '$array_iterator_ready(S_pending, parrayiterator_cached)',
        'S_pending.OBJECTS[n_exception] = THROWABLE pthrowable',
        '$string_bytes($throwable_field(S_pending, n_exception, "message")) = ($ptascii("supplied"))',
        '$throwable_field(S_pending, n_exception, "previous") = PNULL',
        '$throwable_field(S_pending, n_exception, "trace") = PARRAY n_trace', 'S_pending.ARRAYS[n_trace].ITEMS = eps',
        owners('S_pending', 'HARRAY n_tree', 1), owners('S_pending', 'HARRAY n_target', 1),
        owners('S_pending', 'HARRAY n_leaf', 3), owners('S_pending', 'HOBJECT n_object', 2),
        'S_popped = S_pending[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*]',
        'PhpStep: S_pending ~> S_raw',
        'S_raw = $array_iterator_discard(S_popped, parrayiterator_cached, "key")',
        'S_raw.ITERATORS = eps', owners('S_raw', 'HARRAY n_tree', 0), owners('S_raw', 'HARRAY n_target', 0),
        owners('S_raw', 'HARRAY n_upper', 1), owners('S_raw', 'HARRAY n_deep', 1),
        owners('S_raw', 'HARRAY n_leaf', 3), owners('S_raw', 'HOBJECT n_object', 1),
        '$array_iterator_table(S_raw, n_tree)',
    ] + public('S_pending') + budget('S_pending', 'S_discard_budget')
    checks += seek('S_pending', 154, 'S_caught') + caught('S_caught', 7) + [
        'S_caught.ITERATORS = eps', owners('S_caught', 'HOBJECT n_object', 1),
    ]
    return checks + finish('S_caught', stdout, ['HOBJECT n_object', 'HOBJECT n_exception', 'HARRAY n_copy',
        'HARRAY n_target', 'HARRAY n_tree', 'HARRAY n_upper', 'HARRAY n_deep', 'HARRAY n_leaf'])


def body_throw(program, path, stdout):
    checks = entry(program, path) + [
        'S_pre.OBJECTS[n_object] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH', 'pgenerator_initial.FRAME = (pframe_generator)',
        'pframe_generator.LOCALS = (psymboltable_generator)',
        '$lookup(psymboltable_generator.ENV, $ptascii("local")) = (n_local)',
        'S_pre.STORE[n_local] = DEFINED (PARRAY n_tree)',
        '$lookup(S_pre.ENV, $ptascii("watch")) = (n_watch)',
        'S_pre.STORE[n_watch] = DEFINED (POBJECT n_observer)',
        owners('S_pre', 'HARRAY n_tree', 2), owners('S_pre', 'HCELL n_local', 1),
        '$array_generator_plan(S_pre) = (parraygenerator)',
        'parraygenerator.ARRAY = n_target', 'parraygenerator.OBJECT = n_object',
        'parraygenerator.INPUT = S_pre.RESULT', 'parraygenerator.TAIL = phpType13*',
        'parraygenerator.LINE = z', 'parraygenerator.FUNCTION = pgenerator_initial.FUNCTION',
        'PhpStep: S_pre ~> S_active',
        'S_active.TODO = (ARRAY_GENERATOR parraygenerator "rewind") :: ptask_tail*',
        owners('S_active', 'HOBJECT n_object', 2), owners('S_active', 'HARRAY n_tree', 2),
    ] + public('S_active') + budget('S_pre', 'S_entry_budget') + seek('S_active', 155, 'S_first') + [
        'S_first.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        'S_first.OBJECTS[n_object] = GENERATOR pgenerator_first',
        'pgenerator_first.VALUE = (PARRAY n_tree)', 'pgenerator_first.REFCELL = eps',
        '$string_bytes($generator_cached_value(S_first, n_object, true)) = ($ptascii("first"))',
        '$array_generator_ready(S_first, parraygenerator)',
        owners('S_first', 'HARRAY n_tree', 3), owners('S_first', 'HARRAY n_leaf', 5),
        owners('S_first', 'HARRAY n_upper', 1), owners('S_first', 'HARRAY n_deep', 1),
    ] + graph('S_first') + public('S_first') + cache_controls('S_first', 'parraygenerator', True) + [
        'PhpStep: S_first ~> S_insert',
        'S_insert.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        '$entry_lookup(S_insert.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("first"))) = (DIRECT (PARRAY n_tree))',
        'S_insert.OBJECTS[n_object] = GENERATOR pgenerator_first',
        owners('S_insert', 'HARRAY n_tree', 4), owners('S_insert', 'HARRAY n_leaf', 5),
    ] + public('S_insert') + seek('S_insert', 152, 'S_body') + [
        'S_body.OBJECTS[n_object] = GENERATOR pgenerator_running',
        'pgenerator_running.PHASE = GENERATOR_RUNNING', 'pgenerator_running.VALUE = (PARRAY n_tree)',
        'S_body.STORE[n_local] = DEFINED (PARRAY n_tree)',
        'S_body.STORE[n_before] = DEFINED (PARRAY n_copy)', 'n_copy =/= n_leaf', pair('S_body', 'n_copy', 44),
        owners('S_body', 'HARRAY n_tree', 3), owners('S_body', 'HARRAY n_leaf', 3),
        owners('S_body', 'HOBJECT n_object', 1), '~((HCELL n_it) <- S_body.ALLOCATIONS)',
        '~((HCELL n_tree_cell) <- S_body.ALLOCATIONS)', '~((HCELL n_leaf_cell) <- S_body.ALLOCATIONS)',
    ] + public('S_body') + seek('S_body', 156, 'S_finally') + [
        'S_finally.OBJECTS[n_object] = GENERATOR pgenerator_finally',
        'pgenerator_finally.PHASE = GENERATOR_RUNNING', 'pgenerator_finally.VALUE = (PARRAY n_tree)',
        'S_finally.STORE[n_local] = DEFINED (PARRAY n_tree)',
        '$weakref_get(S_finally, n_observer) = POBJECT n_object',
        owners('S_finally', 'HOBJECT n_object', 1), owners('S_finally', 'HARRAY n_tree', 3),
        owners('S_finally', 'HARRAY n_leaf', 3),
    ] + public('S_finally') + seek('S_finally', 157, 'S_pending') + [
        'S_pending.TODO = (THROW_SEARCH n_exception) :: (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        'S_pending.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        'pgenerator_closed.PHASE = GENERATOR_CLOSED', 'pgenerator_closed.FRAME = eps',
        'pgenerator_closed.VALUE = (PARRAY n_tree)', 'pgenerator_closed.REFCELL = eps',
        '~((HCELL n_local) <- S_pending.ALLOCATIONS)',
        'S_pending.OBJECTS[n_exception] = THROWABLE pthrowable',
        '$string_bytes($throwable_field(S_pending, n_exception, "message")) = ($ptascii("supplied"))',
        '$throwable_field(S_pending, n_exception, "previous") = PNULL',
        '$throwable_field(S_pending, n_exception, "trace") = PARRAY n_trace', 'S_pending.ARRAYS[n_trace].ITEMS = eps',
        '$array_generator_ready(S_pending, parraygenerator)',
        owners('S_pending', 'HOBJECT n_object', 1), owners('S_pending', 'HARRAY n_tree', 2),
        owners('S_pending', 'HARRAY n_leaf', 3), owners('S_pending', 'HARRAY n_target', 1),
    ] + public('S_pending') + seek('S_pending', 158, 'S_data') + [
        '~((HOBJECT n_object) <- S_data.ALLOCATIONS)', '$weakref_get(S_data, n_observer) = PNULL',
        '$array_generator_history(S_data, parraygenerator)', '~$array_generator_source(S_data, parraygenerator)',
        '$array_generator_valid(S_data, parraygenerator, "data-released")',
        'S_data.OBJECTS[n_object] = GENERATOR pgenerator_closed',
        owners('S_data', 'HARRAY n_tree', 1), owners('S_data', 'HARRAY n_leaf', 3),
        owners('S_data', 'HARRAY n_upper', 1), owners('S_data', 'HARRAY n_deep', 1),
        owners('S_data', 'HARRAY n_target', 1),
    ] + graph('S_data') + public('S_data') + seek('S_data', 159, 'S_input') + [
        '$array_generator_nodes(parraygenerator, "input-released") = [HARRAY n_target]',
        'S_input.TODO = (THROW_SEARCH n_exception) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask_tail*',
        'PhpStep: S_input ~> S_raw',
        'S_raw.TODO = (THROW_SEARCH n_exception) :: ptask_tail*',
        owners('S_raw', 'HARRAY n_target', 0), owners('S_raw', 'HARRAY n_tree', 1),
        owners('S_raw', 'HARRAY n_leaf', 3),
    ] + public('S_input') + budget('S_input', 'S_discard_budget')
    checks += seek('S_input', 154, 'S_caught') + caught('S_caught', 8) + [
        '$weakref_get(S_caught, n_observer) = PNULL', '~((HOBJECT n_object) <- S_caught.ALLOCATIONS)',
    ]
    return checks + finish('S_caught', stdout, ['HOBJECT n_object', 'HOBJECT n_exception', 'HOBJECT n_observer',
        'HARRAY n_copy', 'HARRAY n_target', 'HARRAY n_tree', 'HARRAY n_upper', 'HARRAY n_deep', 'HARRAY n_leaf'])


def conditions(name, program, path, stdout):
    return key_throw(program, path, stdout) if name.endswith('key-throw') else body_throw(program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
