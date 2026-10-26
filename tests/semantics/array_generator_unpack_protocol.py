#!/usr/bin/env python3
"""Source-reached Generator input/cache edges, DIRECT copies and last DATA."""
import array_generator_unpack_cases as cases
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import HELPERS, budget, finish, initial, owners, public, seek

HELPERS += r'''
def $list_warning_frontier(S, 90) = $array_gen_review_echo(S, $ptascii("N1;"))
def $list_warning_frontier(S, 91) = $array_gen_review_echo(S, $ptascii("N;"))
def $list_warning_frontier(S, 92) = $array_gen_review_echo(S, $ptascii("F;"))
  -- if S.CURRENT = (pcallcontext)
  -- if $generator_close_selection(S) = (pgenclose)
'''


def pair(state, array, first, second=7):
    return f'{state}.ARRAYS[{array}].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT {first})), ENTRY (KINT 1) (DIRECT (PINT {second}))]'


def cached(start, name):
    return seek(start, 71, name) + [
        f'{name}.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
        f'{name}.OBJECTS[n_generator] = GENERATOR pgenerator_{name}',
        f'pgenerator_{name}.PHASE = GENERATOR_PAUSED',
        f'$array_generator_valid({name}, parraygenerator, "ready")',
        f'$array_generator_ready({name}, parraygenerator)',
    ] + public(name)


def insert(state, dest, key, array):
    return [
        f'PhpStep: {state} ~> {dest}',
        f'{dest}.TODO = (ARRAY_GENERATOR parraygenerator "next") :: ptask_tail*',
        f'{dest}.OBJECTS = {state}.OBJECTS',
        f'$entry_lookup({dest}.ARRAYS[n_target].ITEMS, {key}) = (DIRECT (PARRAY {array}))',
        f'$heap_count(HCELL n_row, $task_nodes(ARRAY_GENERATOR parraygenerator "next")) = 0',
    ] + public(dest)


def entry(name, program, path):
    owning = name.endswith('value-cow-keys')
    checks = initial(program, path) + seek('S_initial', 70, 'S_pre') + [
        'S_pre.TODO = (ARRAY_UNPACK n_target phpType13* z) :: ptask_tail*',
        '$lookup(S_pre.ENV, $ptascii("row")) = (n_row)',
        'S_pre.STORE[n_row] = DEFINED (PARRAY n_old)', pair('S_pre', 'n_old', 2),
        '$array_generator_plan(S_pre) = (parraygenerator)',
        'parraygenerator.ARRAY = n_target', 'parraygenerator.LINE = z',
        'parraygenerator.TAIL = phpType13*', 'parraygenerator.INPUT = S_pre.RESULT',
        'n_generator = parraygenerator.OBJECT',
        'S_pre.OBJECTS[n_generator] = GENERATOR pgenerator_initial',
        'pgenerator_initial.PHASE = GENERATOR_FRESH',
        'parraygenerator.FUNCTION = pgenerator_initial.FUNCTION',
        '$array_generator_history(S_pre, parraygenerator)',
        '~$array_generator_history(S_pre[.CODE = eps], parraygenerator)',
        '~$array_generator_history(S_pre[.SOURCES = eps], parraygenerator)',
        '~$array_generator_history(S_pre, parraygenerator[.FUNCTION = PORIGIN 0 eps])',
        '~$array_generator_history(S_pre, parraygenerator[.LINE = $(z + 1)])',
        owners('S_pre', 'HOBJECT n_generator', 1), owners('S_pre', 'HARRAY n_target', 1),
    ] + public('S_pre')
    if owning:
        checks += ['S_pre.RESULT = KNOWN (POBJECT n_generator)',
            'pgenerator_initial.FRAME = (pframe_generator)', 'pframe_generator.LOCALS = (psymboltable_generator)',
            '$lookup(psymboltable_generator.ENV, $ptascii("local")) = (n_local)',
            'S_pre.STORE[n_local] = DEFINED (PARRAY n_old)',
            owners('S_pre', 'HCELL n_local', 1), owners('S_pre', 'HARRAY n_old', 2),
            '~$array_generator_history(S_pre, parraygenerator[.INPUT = VARIABLE ($ptascii("it")) z])']
    else:
        checks += ['S_pre.RESULT = VARIABLE ($ptascii("it")) z',
            '$lookup(S_pre.ENV, $ptascii("it")) = (n_it)',
            'S_pre.STORE[n_it] = DEFINED (POBJECT n_generator)']
    checks += [
        'PhpStep: S_pre ~> S_active',
        'S_active.TODO = (ARRAY_GENERATOR parraygenerator "rewind") :: ptask_tail*',
        'S_active.ITERATORS = S_pre.ITERATORS', 'S_active.NEXTITER = S_pre.NEXTITER',
        'S_active.OBJECTS = S_pre.OBJECTS', 'S_active.EVENTS = S_pre.EVENTS',
        owners('S_active', 'HOBJECT n_generator', 2),
        '$heap_count(HARRAY n_target, $task_nodes(ARRAY_GENERATOR parraygenerator "rewind")) = 1',
    ] + public('S_active')
    return checks


def normal(name, program, path, stdout):
    owning = name.endswith('value-cow-keys')
    checks = entry(name, program, path) + cached('S_active', 'S_first')
    if owning:
        checks += [
            'pgenerator_S_first.VALUE = (PARRAY n_old)', 'pgenerator_S_first.REFCELL = eps',
            '$string_bytes($generator_cached_value(S_first, n_generator, true)) = ($ptascii("8"))',
            '$array_generator_nodes(parraygenerator, "ready") = [HARRAY n_target, HOBJECT n_generator, HOBJECT n_generator]',
            owners('S_first', 'HOBJECT n_generator', 2), owners('S_first', 'HCELL n_local', 1),
            owners('S_first', 'HARRAY n_old', 3),
        ] + insert('S_first', 'S_next', 'KINT 5', 'n_old') + [
            owners('S_next', 'HARRAY n_old', 4),
        ] + seek('S_next', 90, 'S_body') + [
            'S_body.OBJECTS[n_generator] = GENERATOR pgenerator_body',
            'pgenerator_body.PHASE = GENERATOR_RUNNING', 'pgenerator_body.VALUE = (PARRAY n_old)',
            '$lookup(S_body.ENV, $ptascii("local")) = (n_local)',
            'S_body.STORE[n_local] = DEFINED (PARRAY n_old)',
            owners('S_body', 'HARRAY n_old', 4), owners('S_body', 'HCELL n_local', 1),
        ] + public('S_body') + seek('S_body', 86, 'S_closed') + [
            'S_closed.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
            'S_closed.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
            'pgenerator_closed.VALUE = (PARRAY n_last)', 'pgenerator_closed.REFCELL = eps',
            pair('S_closed', 'n_last', 44),
            '$entry_lookup(S_closed.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("slot"))) = (DIRECT (PARRAY n_last))',
            '$entry_lookup(S_closed.ARRAYS[n_target].ITEMS, KSTRING ($ptascii("08"))) = (DIRECT (PARRAY n_last))',
            owners('S_closed', 'HOBJECT n_generator', 2), owners('S_closed', 'HARRAY n_last', 3),
            '~((HCELL n_local) <- S_closed.ALLOCATIONS)',
        ]
    else:
        checks += [
            'pgenerator_S_first.REFCELL = (n_row)', 'pgenerator_S_first.VALUE = eps',
            '$lookup(S_first.ENV, $ptascii("it")) = eps',
            owners('S_first', 'HOBJECT n_generator', 1), owners('S_first', 'HCELL n_row', 4),
            owners('S_first', 'HARRAY n_old', 2),
        ] + insert('S_first', 'S_next', 'KSTRING ($ptascii("answer"))', 'n_old') + [
            owners('S_next', 'HARRAY n_old', 3),
        ] + seek('S_next', 91, 'S_body') + [
            'S_body.OBJECTS[n_generator] = GENERATOR pgenerator_body',
            'pgenerator_body.REFCELL = (n_row)', owners('S_body', 'HCELL n_row', 4),
        ] + cached('S_body', 'S_second') + [
            'pgenerator_S_second.REFCELL = (n_row)',
            'S_second.STORE[n_row] = DEFINED (PARRAY n_last)', pair('S_second', 'n_last', 44),
            '$lookup(S_second.ENV, $ptascii("row")) = (n_rebound)', 'n_rebound =/= n_row',
            owners('S_second', 'HCELL n_row', 3), owners('S_second', 'HARRAY n_last', 1),
        ] + insert('S_second', 'S_second_next', 'KSTRING ($ptascii("again"))', 'n_last') + [
            owners('S_second_next', 'HARRAY n_last', 2),
        ] + seek('S_second_next', 86, 'S_closed') + [
            'S_closed.TODO = (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
            'S_closed.OBJECTS[n_generator] = GENERATOR pgenerator_closed',
            'pgenerator_closed.REFCELL = (n_row)', 'pgenerator_closed.VALUE = eps',
            owners('S_closed', 'HOBJECT n_generator', 1), owners('S_closed', 'HCELL n_row', 2),
            owners('S_closed', 'HARRAY n_last', 2),
        ]
    checks += ['$array_generator_ready(S_closed, parraygenerator)'] + public('S_closed') + budget('S_closed', 'S_close_budget')
    checks += seek('S_closed', 73, 'S_data') + [
        'S_data.TODO = (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*',
        '$array_generator_nodes(parraygenerator, "data-released") = [HARRAY n_target]' + (' ++ [HOBJECT n_generator]' if owning else ''),
        owners('S_data', 'HARRAY n_target', 1),
    ]
    if owning:
        checks += ['(HOBJECT n_generator) <- S_data.ALLOCATIONS', owners('S_data', 'HOBJECT n_generator', 1),
                   owners('S_data', 'HARRAY n_last', 3)]
    else:
        checks += ['~((HOBJECT n_generator) <- S_data.ALLOCATIONS)', owners('S_data', 'HCELL n_row', 1),
                   owners('S_data', 'HARRAY n_last', 2)]
    checks += seek('S_data', 75, 'S_input') + [
        'S_input.TODO = (ARRAY_GENERATOR parraygenerator "input-released") :: ptask_tail*',
        '~((HOBJECT n_generator) <- S_input.ALLOCATIONS)',
        '$array_generator_history(S_input, parraygenerator)', '~$array_generator_source(S_input, parraygenerator)',
        '$array_generator_valid(S_input, parraygenerator, "input-released")',
        '$array_generator_nodes(parraygenerator, "input-released") = [HARRAY n_target]',
        owners('S_input', 'HARRAY n_last', 2),
    ] + public('S_input')
    return checks + finish('S_input', stdout, ['HOBJECT n_generator', 'HARRAY n_target', 'HARRAY n_old', 'HARRAY n_last'])


def last_data(program, path, stdout):
    checks = entry('array-generator-unpack-last-data-finally', program, path) + cached('S_active', 'S_first') + [
        'pgenerator_S_first.VALUE = (PARRAY n_old)',
    ] + insert('S_first', 'S_next', 'KINT 1', 'n_old')
    checks += cached('S_next', 'S_invalid') + [
        'pgenerator_S_invalid.VALUE = (PARRAY n_old)', 'pgenerator_S_invalid.KEY = (PBOOL true)',
        '$lookup(S_invalid.ENV, $ptascii("it")) = eps',
        '$lookup(S_invalid.ENV, $ptascii("dest")) = (n_dest)',
        '$lookup(S_invalid.ENV, $ptascii("later")) = (n_later)',
        owners('S_invalid', 'HOBJECT n_generator', 1), owners('S_invalid', 'HARRAY n_old', 3),
        'PhpStep: S_invalid ~> S_error',
        'S_error.COMPLETION = THROWN "Error" ($ptascii("Keys must be of type int|string during array unpacking")) 11',
        'S_error.OBJECTS = S_invalid.OBJECTS',
    ] + seek('S_invalid', 72, 'S_throw') + [
        'S_throw.TODO = (THROW_SEARCH n_error) :: (ARRAY_GENERATOR parraygenerator "ready") :: ptask_tail*',
    ] + public('S_throw') + budget('S_throw', 'S_drop_budget') + seek('S_throw', 92, 'S_finally') + [
        '$generator_close_selection(S_finally) = (pgenclose)',
        'pgenclose.OBJECT = n_generator', 'pgenclose.PENDING = (n_error)',
        'S_finally.OBJECTS[n_generator] = GENERATOR pgenerator_finally',
        'pgenerator_finally.PHASE = GENERATOR_RUNNING', 'pgenerator_finally.VALUE = (PARRAY n_old)',
        '$array_generator_nodes(parraygenerator, "data-released") = [HARRAY n_target]',
        owners('S_finally', 'HOBJECT n_generator', 1), owners('S_finally', 'HARRAY n_target', 1),
        owners('S_finally', 'HARRAY n_old', 3),
        'S_finally.STORE[n_dest] = DEFINED (PINT 99)', 'S_finally.STORE[n_later] = DEFINED (PINT 7)',
    ] + public('S_finally') + seek('S_finally', 74, 'S_data') + [
        'S_data.TODO = (THROW_SEARCH n_error) :: (ARRAY_GENERATOR parraygenerator "data-released") :: ptask_tail*',
        '~((HOBJECT n_generator) <- S_data.ALLOCATIONS)',
        '$array_generator_history(S_data, parraygenerator)', '~$array_generator_source(S_data, parraygenerator)',
        'S_data.STORE[n_row] = DEFINED (PARRAY n_final)', pair('S_data', 'n_final', 44),
        owners('S_data', 'HARRAY n_old', 1), owners('S_data', 'HARRAY n_target', 1),
        '$throwable_previous_id(S_data, n_error) = eps',
    ] + public('S_data') + seek('S_data', 76, 'S_input') + [
        'S_input.TODO = (THROW_SEARCH n_error) :: (ARRAY_GENERATOR parraygenerator "input-released") :: ptask_tail*',
        'PhpStep: S_input ~> S_drop',
        'S_drop.TODO = (THROW_SEARCH n_error) :: ptask_tail*',
        owners('S_drop', 'HARRAY n_target', 0),
    ]
    return checks + finish('S_drop', stdout, ['HOBJECT n_generator', 'HARRAY n_target', 'HARRAY n_old', 'HARRAY n_final'])


def conditions(name, program, path, stdout):
    return last_data(program, path, stdout) if name.endswith('last-data-finally') else normal(name, program, path, stdout)


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(cases, conditions, HELPERS) else 1)
