"""Reached nonpublic clone cache locators and per-copy typed-cell sources."""
import json

from throwable_empty_clone_protocol import PREFIX
from throwable_interface_protocol import front
from throwable_previous_graph_protocol import raw, trace

EXPECTED = {'nonpublic-cached-clone-types':
    'B|0:0|A|0:2|T|1:-1|H|1|C|TypeError:2|D|1|R|3|G|K|-1:1|'}


def mark(state, out, prefix):
    return [out + ' = $tec_seek_output(' + state + ',10000,$ptascii(' + json.dumps(prefix) + '))',
            '$tbp_output(' + out + '.EVENTS) = $ptascii(' + json.dumps(prefix) + ')']


def value(state, name, label, item):
    return ['$lookup(' + state + '.ENV,$ptascii(' + json.dumps(name) + ')) = (n_cv_' + label + ')',
            state + '.STORE[n_cv_' + label + '] = DEFINED (' + item + ')']


def checks(program, path, name):
    assert name in EXPECTED
    rows = front(program, path)
    rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
    rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
    rows += [
        'n_left =/= n_right',
        'S.OBJECTS[n_left] = INSTANCE porigin_plain',
        'S.OBJECTS[n_right] = INSTANCE porigin_plain',
        '$property_layout(S,porigin_plain,|S.CLASSES|) = [ppropertydesc_data,ppropertydesc_tail]',
        'ppropertydesc_data.KEY = [0] ++ $ptascii("Plain159") ++ [0] ++ $ptascii("data")',
        'ppropertydesc_data.VISIBILITY = PROPERTY_PRIVATE',
        'ppropertydesc_data.TYPE =/= eps',
        'ppropertydesc_tail.KEY = [0,42,0] ++ $ptascii("tail")',
        '$object_table_at(S.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(S.OBJECTTABLES,n_right) = (n_table_right)',
        'n_table_left =/= n_table_right',
        'S.ARRAYS[n_table_left].ITEMS = [ENTRY (KSTRING ppropertydesc_data.KEY) (INDIRECT n_left ppropertydesc_data.KEY),ENTRY (KSTRING ppropertydesc_tail.KEY) (INDIRECT n_left ppropertydesc_tail.KEY)]',
        'S.ARRAYS[n_table_right].ITEMS = [ENTRY (KSTRING ppropertydesc_data.KEY) (INDIRECT n_right ppropertydesc_data.KEY),ENTRY (KSTRING ppropertydesc_tail.KEY) (INDIRECT n_right ppropertydesc_tail.KEY)]',
        '$object_table_item(S,INDIRECT n_left ppropertydesc_data.KEY) = ALIAS n_cell',
        '$object_table_item(S,INDIRECT n_right ppropertydesc_data.KEY) = ALIAS n_cell',
        '$lookup(S.ENV,$ptascii("live")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_one)',
        '$entry_lookup(S.ARRAYS[n_one].ITEMS,KINT 0) = (DIRECT (PINT 1))',
        '$object_tables_valid(S)',
        r'$trace_visit_object_image(S,n_left) /\ $trace_visit_object_image(S,n_right)',
        '$propref_at(S.PROPREFS,n_cell) = (ppropref_pair)',
        '|ppropref_pair.SOURCES| = 2',
        '(OBJECT_PROP_SOURCE n_left ppropertydesc_data.KEY ppropertydesc_data.ORIGIN) <- ppropref_pair.SOURCES',
        '(OBJECT_PROP_SOURCE n_right ppropertydesc_data.KEY ppropertydesc_data.ORIGIN) <- ppropref_pair.SOURCES',
        '$propref_sources_valid(S,n_cell,ppropref_pair.SOURCES)',
    ]
    rows += raw('S', 0)
    rows += [
        'S_alias = $tbp_seek(S_raw,10000)[.COMPLETION = NORMAL]',
        'S_alias.STORE[n_cell] = DEFINED (PARRAY n_two)',
        '$entry_lookup(S_alias.ARRAYS[n_two].ITEMS,KINT 0) = (DIRECT (PINT 2))',
        '$value_order_effect(S_alias,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_alias,ORDER 0)',
        '$heap_owners($heap_prune($heap_graph(S_alias)),HCELL n_cell) = 4',
    ]
    rows += value('S_alias', 'view', 'view', 'PARRAY n_view')
    rows += [
        r'n_view =/= n_table_left /\ n_view =/= n_table_right',
        '$entry_lookup(S_alias.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_data.KEY) = (ALIAS n_cell)',
        'S_tail = $tbp_next(S_alias)',
        '$object_table_item(S_tail,INDIRECT n_left ppropertydesc_tail.KEY) = DIRECT (PINT 7)',
        '$object_table_item(S_tail,INDIRECT n_right ppropertydesc_tail.KEY) = DIRECT (PINT 0)',
    ]
    rows += raw('S_tail', 1)
    prefix = 'B|0:0|A|0:2|T|1:-1|H|'
    rows += mark('S_tail_raw', 'S_hold', prefix)
    rows += [
        '~((HOBJECT n_left) <- S_hold.ALLOCATIONS)',
        '$object_table_at(S_hold.OBJECTTABLES,n_left) = eps',
        '(HOBJECT n_right) <- S_hold.ALLOCATIONS',
        '$propref_at(S_hold.PROPREFS,n_cell) = (ppropref_copy)',
        'ppropref_copy.SOURCES = [OBJECT_PROP_SOURCE n_right ppropertydesc_data.KEY ppropertydesc_data.ORIGIN]',
        '$propref_sources_valid(S_hold,n_cell,ppropref_copy.SOURCES)',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HCELL n_cell) = 3',
    ]
    prefix += '1|C|TypeError:2|'
    rows += mark('S_hold', 'S_rejected', prefix)
    rows += [
        'S_rejected.STORE[n_cell] = DEFINED (PARRAY n_two)',
        '$propref_at(S_rejected.PROPREFS,n_cell) = (ppropref_copy)',
        '$propref_sources_valid(S_rejected,n_cell,ppropref_copy.SOURCES)',
    ]
    rows += mark('S_rejected', 'S_drop', prefix + 'D|')
    rows += [
        '~((HOBJECT n_right) <- S_drop.ALLOCATIONS)',
        '$object_table_at(S_drop.OBJECTTABLES,n_right) = eps',
        '$propref_at(S_drop.PROPREFS,n_cell) = eps',
        '(HCELL n_cell) <- S_drop.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_drop)),HCELL n_cell) = 2',
        'S_callback = $tbp_seek(S_drop,10000)[.COMPLETION = NORMAL]',
        'S_callback.STORE[n_cell] = DEFINED (PINT 3)',
        '$entry_lookup(S_callback.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_data.KEY) = (ALIAS n_cell)',
    ]
    rows += value('S_callback', 'c', 'c', 'POBJECT n_c')
    rows += value('S_callback', 'd', 'd', 'POBJECT n_d')
    rows += trace('S_callback', 'n_c', 'c', 'POBJECT n_callback_source')[:4]
    rows += trace('S_callback', 'n_d', 'd', 'POBJECT n_callback_copy')[:4]
    rows += [
        'S_callback.OBJECTS[n_callback_source] = INSTANCE porigin_callback',
        'S_callback.OBJECTS[n_callback_copy] = INSTANCE porigin_callback',
        '$property_layout(S_callback,porigin_callback,|S_callback.CLASSES|) = [ppropertydesc_callback_data,ppropertydesc_callback_tail]',
        'ppropertydesc_callback_data.KEY = [0] ++ $ptascii("Callback159") ++ [0] ++ $ptascii("data")',
        '$object_table_at(S_callback.OBJECTTABLES,n_callback_source) = (n_callback_source_table)',
        '$object_table_at(S_callback.OBJECTTABLES,n_callback_copy) = (n_callback_copy_table)',
        'n_callback_source_table =/= n_callback_copy_table',
        '$entry_lookup(S_callback.ARRAYS[n_callback_source_table].ITEMS,KSTRING ppropertydesc_callback_data.KEY) = (INDIRECT n_callback_source ppropertydesc_callback_data.KEY)',
        '$entry_lookup(S_callback.ARRAYS[n_callback_copy_table].ITEMS,KSTRING ppropertydesc_callback_data.KEY) = (INDIRECT n_callback_copy ppropertydesc_callback_data.KEY)',
        '$object_table_item(S_callback,INDIRECT n_callback_source ppropertydesc_callback_data.KEY) = DIRECT (PINT 1)',
        '$object_table_item(S_callback,INDIRECT n_callback_copy ppropertydesc_callback_data.KEY) = DIRECT (PINT 2)',
        '$object_tables_valid(S_callback)',
    ]
    rows += [row.replace('POBJECT n_a,POBJECT n_b', 'POBJECT n_c,POBJECT n_d')
             for row in raw('S_callback', -1)]
    rows += [
        'S_done = $drive_steps(S_callback_raw,10000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')',
    ]
    return rows
