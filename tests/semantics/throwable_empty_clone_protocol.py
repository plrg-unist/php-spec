"""Reached empty-cache clone sharing, COW, retirement and callback storage."""
import json

from throwable_interface_protocol import field, front
from throwable_previous_graph_protocol import raw, trace
from throwable_builtin_previous_protocol import PREFIX as BASE_PREFIX

EXPECTED = {'empty-cached-clone-owners':
    'B|0:0|L|1:1:1|R|-1:1:2|H|1|D|1|G|Q|0:0|V|1:1:7|'}


def active_gc_token(state):
    # Only the nonempty ACTIVE guard is tested, not GC call authority.
    return ('{NONCE ' + state + '.GC.NEXT, CALL {SITE (PORIGIN 0 eps), '
            'KIND INTRINSIC_GC_COLLECT, INDEX 0, SENT eps, NAMED false, '
            'OWNER eps, SELECTION eps, LINE 0, PACKS eps}, CALLER ' + state + '.CURRENT, '
            'ORIGIN ' + state + '.ORIGIN, CONSTCONTEXT ' + state + '.CONSTCONTEXT, '
            'PASS 0, TOTAL 0, PENDING eps, COUNT_SOURCE eps}')


# These rows mutate a reached state or supply an artificial active guard.
DERIVED = {
    '$trace_visit_object_effect(S,n_left,n_right,[HARRAY n_shared],z_S) = (S,ORDER 0)':
        'Shared table identity precedes a supplied active-left table guard.',
    'S_gc = S[.GC.ACTIVE = (' + active_gc_token('S') + ')]':
        'Synthetic typed nonempty ACTIVE token on the reached shared-cache image.',
    '~$clone_dynamic_share_ready(S_gc,n_left)':
        'The empty-cache sharing dependency retains the old collection fence.',
    'S_callback_gc = S_callback[.GC.ACTIVE = (' + active_gc_token('S_callback') + ')]':
        'Synthetic typed nonempty ACTIVE token on the reached callback-source image.',
    '~$clone_empty_callback_ready(S_callback_gc,n_callback_source)':
        'The uncached callback clone dependency retains the old collection fence.',
}

PREFIX = BASE_PREFIX + r'''
dec $tec_seek_output(pstate, nat, ptbytes) : pstate
def $tec_seek_output(S, n, ptbytes) = S
  -- if $tbp_output(S.EVENTS) = ptbytes \/ n = 0
def $tec_seek_output(S, n, ptbytes) = $tec_seek_output($drive_steps(S, 1)[.COMPLETION = NORMAL], $nabs($(n - 1)), ptbytes)
  -- if $tbp_output(S.EVENTS) =/= ptbytes /\ $(n > 0)
  -- if S.COMPLETION = NORMAL
def $tec_seek_output(S, n, ptbytes) = S -- otherwise
'''


def value(state, name, label, item):
    return [
        '$lookup(' + state + '.ENV,$ptascii(' + json.dumps(name) + ')) = (n_cv_' + label + ')',
        state + '.STORE[n_cv_' + label + '] = DEFINED (' + item + ')',
    ]


def checks(program, path, name):
    assert name in EXPECTED
    rows = front(program, path)
    rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
    rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
    rows += [
        'n_left =/= n_right',
        'S.OBJECTS[n_left] = INSTANCE porigin_shared',
        'S.OBJECTS[n_right] = INSTANCE porigin_shared',
        '$property_layout(S,porigin_shared,|S.CLASSES|) = eps',
        '$objectprops_record_at(S.OBJECTPROPS,n_left) = (pobjectprops_left)',
        '$objectprops_record_at(S.OBJECTPROPS,n_right) = (pobjectprops_right)',
        r'pobjectprops_left.SLOTS = eps /\ pobjectprops_right.SLOTS = eps',
        r'pobjectprops_left.MATERIALIZED /\ pobjectprops_right.MATERIALIZED',
        '$object_table_at(S.OBJECTTABLES,n_left) = (n_shared)',
        '$object_table_at(S.OBJECTTABLES,n_right) = (n_shared)',
        'S.ARRAYS[n_shared].ITEMS = eps',
        '$object_tables_valid(S)',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_shared) = 2',
        '~$trace_visit_inline_pair(S,n_left,n_right)',
        r'$trace_visit_object_image(S,n_left) /\ $trace_visit_object_image(S,n_right)',
        '$clone_method(S,n_left) = eps',
        '$clone_dynamic_share_ready(S,n_left)',
        '~$clone_cached_ready(S,n_left)',
    ]
    rows += list(DERIVED)[:3]
    rows += raw('S', 0)
    rows += [
        'S_left = $tbp_seek(S_raw,6000)[.COMPLETION = NORMAL]',
        '$object_table_at(S_left.OBJECTTABLES,n_left) = (n_left_table)',
        '$object_table_at(S_left.OBJECTTABLES,n_right) = (n_shared)',
        'n_left_table =/= n_shared',
        '$entry_lookup(S_left.ARRAYS[n_left_table].ITEMS,KSTRING $ptascii("data")) = (DIRECT (PINT 1))',
        'S_left.ARRAYS[n_shared].ITEMS = eps',
        '$object_tables_valid(S_left)',
        '$heap_owners($heap_prune($heap_graph(S_left)),HARRAY n_shared) = 3',
    ]
    rows += value('S_left', 'view', 'view_left', 'PARRAY n_shared')
    rows += value('S_left', 'snapshot', 'snapshot_left', 'PARRAY n_shared')
    rows += field('S_left', 'n_left', 'data_left', 'DIRECT (PINT 1)')
    rows += raw('S_left', 1)
    rows += [
        'S_right = $tbp_seek(S_left_raw,6000)[.COMPLETION = NORMAL]',
        '$object_table_at(S_right.OBJECTTABLES,n_left) = (n_left_table)',
        '$object_table_at(S_right.OBJECTTABLES,n_right) = (n_right_table)',
        r'n_right_table =/= n_shared /\ n_right_table =/= n_left_table',
        '$entry_lookup(S_right.ARRAYS[n_right_table].ITEMS,KSTRING $ptascii("data")) = (DIRECT (PINT 2))',
        'S_right.ARRAYS[n_shared].ITEMS = eps',
        '$heap_owners($heap_prune($heap_graph(S_right)),HARRAY n_shared) = 2',
        '$object_tables_valid(S_right)',
    ]
    rows += raw('S_right', -1)
    before_hold = 'B|0:0|L|1:1:1|R|-1:1:2|H|'
    before_drop = before_hold + '1|D|'
    rows += [
        'S_hold = $tec_seek_output(S_right_raw,6000,$ptascii(' + json.dumps(before_hold) + '))',
        '$tbp_output(S_hold.EVENTS) = $ptascii(' + json.dumps(before_hold) + ')',
        '(HOBJECT n_left) <- S_hold.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_left) = 1',
    ]
    rows += value('S_hold', 'original', 'original_hold', 'PNULL')
    rows += value('S_hold', 'a', 'a_hold', 'PNULL')
    rows += value('S_hold', 'view', 'view_hold', 'PARRAY n_keep')
    rows += [
        'n_keep =/= n_shared',
        '$entry_lookup(S_hold.ARRAYS[n_keep].ITEMS,KSTRING $ptascii("keep")) = (DIRECT (POBJECT n_left))',
        'S_drop = $tec_seek_output(S_hold,6000,$ptascii(' + json.dumps(before_drop) + '))',
        '$tbp_output(S_drop.EVENTS) = $ptascii(' + json.dumps(before_drop) + ')',
        '~((HOBJECT n_left) <- S_drop.ALLOCATIONS)',
        '$object_table_at(S_drop.OBJECTTABLES,n_left) = eps',
        '(HARRAY n_shared) <- S_drop.ALLOCATIONS',
        'S_drop.ARRAYS[n_shared].ITEMS = eps',
    ]
    rows += value('S_drop', 'snapshot', 'snapshot_drop', 'PARRAY n_shared')
    rows += [
        'S_callback = $tbp_seek(S_drop,6000)[.COMPLETION = NORMAL]',
    ]
    rows += value('S_callback', 'e', 'e_callback', 'POBJECT n_e')
    rows += value('S_callback', 'f', 'f_callback', 'POBJECT n_f')
    rows += trace('S_callback', 'n_e', 'e', 'POBJECT n_callback_source')[:4]
    rows += trace('S_callback', 'n_f', 'f', 'POBJECT n_callback_copy')[:4]
    rows += [
        'n_callback_source =/= n_callback_copy',
        'S_callback.OBJECTS[n_callback_source] = INSTANCE porigin_callback',
        'S_callback.OBJECTS[n_callback_copy] = INSTANCE porigin_callback',
        '$property_layout(S_callback,porigin_callback,|S_callback.CLASSES|) = eps',
        '$object_table_at(S_callback.OBJECTTABLES,n_callback_source) = (n_callback_table)',
        'S_callback.ARRAYS[n_callback_table].ITEMS = eps',
        '$object_table_at(S_callback.OBJECTTABLES,n_callback_copy) = eps',
        '$objectprops_record_at(S_callback.OBJECTPROPS,n_callback_copy) = (pobjectprops_callback_copy)',
        r'pobjectprops_callback_copy.SLOTS = eps /\ ~pobjectprops_callback_copy.MATERIALIZED',
        '$clone_method(S_callback,n_callback_source) =/= eps',
        '$clone_empty_callback_ready(S_callback,n_callback_source)',
        '~$clone_dynamic_share_ready(S_callback,n_callback_source)',
        '~$clone_cached_ready(S_callback,n_callback_source)',
        '$object_tables_valid(S_callback)',
        '$heap_owners($heap_prune($heap_graph(S_callback)),HARRAY n_shared) = 1',
        'S_callback.TODO = (BINARY_RIGHT SPACESHIP poperand_S_callback z_S_callback) :: ptask_S_callback*',
        '$trace_visit_object_effect(S_callback,n_callback_source,n_callback_copy,eps,z_S_callback) = (S_callback_effect,ORDER 0)',
        'n_callback_copy_table = |S_callback.ARRAYS|',
        'S_callback_effect.ALLOCATIONS = S_callback.ALLOCATIONS ++ [HARRAY n_callback_copy_table]',
        '|S_callback_effect.ARRAYS| = $(|S_callback.ARRAYS| + 1)',
        'S_callback_effect.ARRAYS[n_callback_copy_table].ITEMS = eps',
        '$object_table_at(S_callback_effect.OBJECTTABLES,n_callback_source) = (n_callback_table)',
        '$object_table_at(S_callback_effect.OBJECTTABLES,n_callback_copy) = (n_callback_copy_table)',
        '$objectprops_materialized(S_callback_effect.OBJECTPROPS,n_callback_copy)',
        '$object_tables_valid(S_callback_effect)',
    ]
    rows += list(DERIVED)[3:]
    rows += [row.replace('POBJECT n_a,POBJECT n_b', 'POBJECT n_e,POBJECT n_f')
             for row in raw('S_callback', 0, 'S_callback_effect')]
    rows += [
        'S_done = $drive_steps(S_callback_raw,6000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
        '$object_table_at(S_done.OBJECTTABLES,n_callback_source) = (n_callback_table)',
        '$object_table_at(S_done.OBJECTTABLES,n_callback_copy) = (n_callback_copy_table)',
        'S_done.ARRAYS[n_callback_table].ITEMS = eps',
        '$entry_lookup(S_done.ARRAYS[n_callback_copy_table].ITEMS,KSTRING $ptascii("data")) = (DIRECT (PINT 7))',
        '~((HOBJECT n_left) <- S_done.ALLOCATIONS)',
        '(HARRAY n_shared) <- S_done.ALLOCATIONS',
    ]
    rows += value('S_done', 'cbView', 'callback_view_done', 'PARRAY n_callback_table')
    return rows
