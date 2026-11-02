"""Reached declared holes, physical caches and Previous/trace ownership."""
import json

from throwable_uninitialized_cases import EXPECTED as SOURCE_EXPECTED
from throwable_interface_protocol import front
from throwable_previous_graph_protocol import raw, trace
from throwable_builtin_previous_protocol import PREFIX as BASE_PREFIX

EXPECTED = {name: data.decode() for name, data in SOURCE_EXPECTED.items()
            if not name.endswith('-control')}
PREFIX = BASE_PREFIX + r'''
dec $tui_seek_output(pstate, nat, ptbytes) : pstate
def $tui_seek_output(S, n, ptbytes) = S
  -- if $tbp_output(S.EVENTS) = ptbytes \/ n = 0
def $tui_seek_output(S, n, ptbytes) = $tui_seek_output($drive_steps(S, 1)[.COMPLETION = NORMAL], $nabs($(n - 1)), ptbytes)
  -- if $tbp_output(S.EVENTS) =/= ptbytes /\ $(n > 0)
  -- if S.COMPLETION = NORMAL
def $tui_seek_output(S, n, ptbytes) = S -- otherwise
'''

# Only a supplied active-object guard is projected; every image is source-reached.
DERIVED = ['$trace_visit_object_effect(S,n_left,n_right,[HOBJECT n_left],z_S) = (S,ORDERRECURSIVE)']


def value(state, name, label, item):
    return [f'$lookup({state}.ENV,$ptascii({json.dumps(name)})) = (n_cv_{label})',
            f'{state}.STORE[n_cv_{label}] = DEFINED ({item})']


def slot(state, node, label, desc, propstate):
    return [f'$objectprops_record_at({state}.OBJECTPROPS,{node}) = (pobjectprops_{label})',
            f'$property_slot_at(pobjectprops_{label}.SLOTS,{desc}.KEY) = (ppropertyslot_{label})',
            f'ppropertyslot_{label}.DECL = ({desc}.ORIGIN)',
            f'ppropertyslot_{label}.STATE = {propstate}']


def output(state, out, prefix):
    return [f'{out} = $tui_seek_output({state},15000,$ptascii({json.dumps(prefix)}))',
            f'$tbp_output({out}.EVENTS) = $ptascii({json.dumps(prefix)})']


def stage(state, out, prefix):
    return output(state, out + '_prefix', prefix) + [
        f'{out} = $tbp_seek({out}_prefix,15000)[.COMPLETION = NORMAL]',
        f'$tbp_stage({out})',
        f'{out}.TODO = (BINARY_RIGHT SPACESHIP poperand_{out} z_{out}) :: ptask_{out}*']


def finish(state, name):
    return [f'S_done = $drive_steps({state},15000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')']


def common():
    return [
        'S.OBJECTS[n_left] = INSTANCE porigin_packet',
        'S.OBJECTS[n_right] = INSTANCE porigin_packet',
        '$class_at(S.CLASSES,porigin_packet) = (pclassdesc_packet)',
        '$trace_visit_parent_path(S,pclassdesc_packet,eps)',
        '$trace_visit_interfaces(S,pclassdesc_packet)',
        '$property_layout(S,porigin_packet,|S.CLASSES|) = ppropertydesc_layout*',
        '$trace_visit_object_header(S,n_left)',
        '$trace_visit_object_header(S,n_right)',
        '$trace_visit_object_image(S,n_left)',
        '$trace_visit_object_image(S,n_right)',
        '$trace_visit_inline_pair(S,n_left,n_right)',
        '$object_table_at(S.OBJECTTABLES,n_left) = eps',
        '$object_table_at(S.OBJECTTABLES,n_right) = eps',
        '$object_table_ordinary(S,n_left)',
        '$object_table_ordinary(S,n_right)',
    ]


def table(state, node, label, descriptors):
    entries = ','.join(f'ENTRY (KSTRING {desc}.KEY) (INDIRECT {node} {desc}.KEY)' for desc in descriptors)
    return [f'$object_table_at({state}.OBJECTTABLES,{node}) = (n_table_{label})',
            f'{state}.ARRAYS[n_table_{label}].ITEMS = [{entries}]',
            f'$aggregate_hash_image({state},{node},n_table_{label})',
            f'$trace_visit_object_image({state},{node})',
            f'$heap_owners($heap_prune($heap_graph({state})),HARRAY n_table_{label}) = 1']


def checks(program, path, name):
    rows = front(program, path)
    if name == 'declared-holes-physical-cache-count':
        rows += trace('S', 'n_a', 'a', 'POBJECT n_left')[:4]
        rows += trace('S', 'n_b', 'b', 'POBJECT n_right')[:4]
        rows += common() + [
            'ppropertydesc_layout* = [ppropertydesc_first,ppropertydesc_middle,ppropertydesc_last]',
            'ppropertydesc_first.KEY = $ptascii("first")',
            'ppropertydesc_middle.KEY = [0] ++ $ptascii("Packet160") ++ [0] ++ $ptascii("middle")',
            'ppropertydesc_last.KEY = [0,42,0] ++ $ptascii("last")',
            'ppropertydesc_first.VISIBILITY = PROPERTY_PUBLIC',
            'ppropertydesc_middle.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_last.VISIBILITY = PROPERTY_PROTECTED',
            'ppropertydesc_first.DEFAULT = PROP_UNINITIALIZED',
            'ppropertydesc_middle.DEFAULT = PROP_UNINITIALIZED',
            'ppropertydesc_last.DEFAULT = PROP_UNINITIALIZED',
        ]
        for node, states in [('left',('PROP_INITIAL','PROP_VALUE (DIRECT (PINT 9))','PROP_VALUE (DIRECT (PINT 9))')),
                             ('right',('PROP_VALUE (DIRECT (PINT 1))','PROP_INITIAL','PROP_INITIAL'))]:
            for desc, propstate in zip(('first','middle','last'),states):
                rows += slot('S','n_'+node,desc+'_'+node,'ppropertydesc_'+desc,propstate)
        rows += [
            '$trace_object_inline_shape(S,n_left)',
            '$trace_object_inline_shape(S,n_right)',
            '~$aggregate_decl_initialized($object_table_slots_at(S,n_left))',
            '~$aggregate_decl_initialized($object_table_slots_at(S,n_right))',
            '$trace_visit_object_effect(S,n_left,n_right,eps,z_S) = (S,ORDER 1)',
            '$trace_visit_object_effect(S,n_right,n_left,eps,z_S) = (S,ORDER 1)',
        ] + DERIVED + raw('S',1)
        rows += stage('S_raw','S_warm','B|1:1:0:1:0:0:0:0|W|1:') + [
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
        ] + raw('S_warm',1)
        rows += stage('S_warm_raw','S_cast','B|1:1:0:1:0:0:0:0|W|1:1|A|2:1:')
        rows += value('S_cast','va','va','PARRAY n_va') + value('S_cast','vb','vb','PARRAY n_vb') + [
            '|S_cast.ARRAYS[n_va].ITEMS| = 2',
            '|S_cast.ARRAYS[n_vb].ITEMS| = 1',
            '$entry_lookup(S_cast.ARRAYS[n_va].ITEMS,KSTRING ppropertydesc_first.KEY) = eps',
            '$entry_lookup(S_cast.ARRAYS[n_vb].ITEMS,KSTRING ppropertydesc_first.KEY) = (DIRECT (PINT 1))',
            '$entry_lookup(S_cast.ARRAYS[n_vb].ITEMS,KSTRING ppropertydesc_middle.KEY) = eps',
            '$object_table_at(S_cast.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S_cast.OBJECTTABLES,n_right) = eps',
        ] + raw('S_cast',1)
        rows += stage('S_cast_raw','S_cached','B|1:1:0:1:0:0:0:0|W|1:1|A|2:1:1|C|')
        descs=['ppropertydesc_first','ppropertydesc_middle','ppropertydesc_last']
        rows += table('S_cached','n_left','left',descs) + [
            '$object_table_at(S_cached.OBJECTTABLES,n_right) = eps',
            '$object_table_item(S_cached,INDIRECT n_left ppropertydesc_first.KEY) = UNINITIALIZED',
            '$trace_visit_inline_pair(S_cached,n_left,n_right) = false',
            '$value_order_effect(S_cached,POBJECT n_a,POBJECT n_b,eps,z_S_cached) = (S_cached_effect,ORDER $(-1))',
            'S_cached_effect.COMPLETION = NORMAL',
            '|S_cached_effect.ARRAYS| = $(|S_cached.ARRAYS| + 1)',
            'n_table_right = |S_cached.ARRAYS|',
            '$object_table_at(S_cached_effect.OBJECTTABLES,n_right) = (n_table_right)',
            '|S_cached_effect.ARRAYS[n_table_left].ITEMS| = 3',
            '|S_cached_effect.ARRAYS[n_table_right].ITEMS| = 3',
            '$object_table_item(S_cached_effect,INDIRECT n_right ppropertydesc_first.KEY) = DIRECT (PINT 1)',
            '$trace_visit_object_effect(S_cached_effect,n_left,n_right,eps,z_S_cached) = (S_cached_effect,ORDER $(-1))',
            '$trace_visit_object_effect(S_cached_effect,n_right,n_left,eps,z_S_cached) = (S_cached_effect,ORDER 1)',
            '$object_tables_valid(S_cached_effect)',
        ] + raw('S_cached',-1,'S_cached_effect')
        rows += stage('S_cached_raw','S_unset','B|1:1:0:1:0:0:0:0|W|1:1|A|2:1:1|C|-1:1|U|')
        rows += slot('S_unset','n_left','first_initial','ppropertydesc_first','PROP_INITIAL')
        rows += slot('S_unset','n_right','first_unset','ppropertydesc_first','PROP_UNSET')
        rows += [
            '$object_table_item(S_unset,INDIRECT n_left ppropertydesc_first.KEY) = UNINITIALIZED',
            '$object_table_item(S_unset,INDIRECT n_right ppropertydesc_first.KEY) = UNINITIALIZED',
            '$object_table_item(S_unset,INDIRECT n_left ppropertydesc_middle.KEY) = DIRECT (PINT 9)',
            '$object_table_item(S_unset,INDIRECT n_right ppropertydesc_middle.KEY) = UNINITIALIZED',
            '$object_tables_valid(S_unset)',
            '$trace_visit_object_effect(S_unset,n_right,n_left,eps,z_S_unset) = (S_unset,ORDER $(-1))',
        ] + raw('S_unset',1)
        rows += stage('S_unset_raw','S_equal','B|1:1:0:1:0:0:0:0|W|1:1|A|2:1:1|C|-1:1|U|1:-1|E|')
        rows += [
            '$object_table_at(S_equal.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_equal.OBJECTTABLES,n_right) = (n_table_right)',
            '$trace_visit_object_effect(S_equal,n_left,n_right,eps,z_S_equal) = (S_equal,ORDER 0)',
            '$entry_lookup(S_equal.ARRAYS[n_vb].ITEMS,KSTRING ppropertydesc_first.KEY) = (DIRECT (PINT 1))',
        ] + raw('S_equal',0)
        return rows + finish('S_equal_raw',name)
    assert name == 'declared-holes-previous-alias-owners'
    rows += [
        '$throwable_field(S,n_a,"previous") = POBJECT n_p',
        '$throwable_field(S,n_b,"previous") = POBJECT n_q',
    ] + trace('S','n_p','p','POBJECT n_left')[:4] + trace('S','n_q','q','POBJECT n_right')[:4]
    rows += common() + [
        'ppropertydesc_layout* = [ppropertydesc_hole,ppropertydesc_data]',
        'ppropertydesc_hole.KEY = [0] ++ $ptascii("Packet160") ++ [0] ++ $ptascii("hole")',
        'ppropertydesc_hole.VISIBILITY = PROPERTY_PRIVATE',
        'ppropertydesc_hole.DEFAULT = PROP_UNINITIALIZED',
        'ppropertydesc_data.KEY = $ptascii("data")',
        'ppropertydesc_data.VISIBILITY = PROPERTY_PUBLIC',
        'ppropertydesc_data.TYPE =/= eps',
    ]
    rows += slot('S','n_left','hole_left','ppropertydesc_hole','PROP_INITIAL')
    rows += slot('S','n_right','hole_right','ppropertydesc_hole','PROP_INITIAL')
    rows += slot('S','n_left','data_left','ppropertydesc_data','PROP_VALUE (ALIAS n_cell)')
    rows += slot('S','n_right','data_right','ppropertydesc_data','PROP_VALUE (DIRECT (PARRAY n_data_right))')
    rows += [
        '$lookup(S.ENV,$ptascii("live")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_data_left)',
        '$entry_lookup(S.ARRAYS[n_data_left].ITEMS,KINT 0) = (DIRECT (PINT 1))',
        '$entry_lookup(S.ARRAYS[n_data_right].ITEMS,KINT 0) = (DIRECT (PINT 2))',
        '$propref_at(S.PROPREFS,n_cell) = (ppropref_data)',
        'ppropref_data.SOURCES = [OBJECT_PROP_SOURCE n_left ppropertydesc_data.KEY ppropertydesc_data.ORIGIN]',
        '$propref_sources_valid(S,n_cell,ppropref_data.SOURCES)',
        '$trace_visit_object_effect(S,n_left,n_right,eps,z_S) = (S,ORDER $(-1))',
    ] + raw('S',-1)
    rows += stage('S_raw','S_cached','B|-1:1:-1|C|99:3:')
    rows += value('S_cached','view','view','PARRAY n_view') + value('S_cached','snapshot','snapshot','PARRAY n_snapshot')
    for node in ('left','right'):
        rows += table('S_cached','n_'+node,node,['ppropertydesc_hole','ppropertydesc_data'])
    rows += [
        '$object_tables_valid(S_cached)',
        '$object_table_item(S_cached,INDIRECT n_left ppropertydesc_hole.KEY) = UNINITIALIZED',
        '$object_table_item(S_cached,INDIRECT n_right ppropertydesc_hole.KEY) = UNINITIALIZED',
        '$object_table_item(S_cached,INDIRECT n_left ppropertydesc_data.KEY) = ALIAS n_cell',
        '$entry_lookup(S_cached.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_hole.KEY) = eps',
        '$entry_lookup(S_cached.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_data.KEY) = (ALIAS n_cell)',
        '$entry_lookup(S_cached.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
        'S_cached.STORE[n_cell] = DEFINED (PARRAY n_three)',
        '$entry_lookup(S_cached.ARRAYS[n_three].ITEMS,KINT 0) = (DIRECT (PINT 3))',
        '$heap_owners($heap_prune($heap_graph(S_cached)),HCELL n_cell) = 3',
    ] + raw('S_cached',1)
    rows += stage('S_cached_raw','S_equal','B|-1:1:-1|C|99:3:1:1|E|') + [
        '$trace_visit_object_effect(S_equal,n_left,n_right,eps,z_S_equal) = (S_equal,ORDER 0)',
    ] + raw('S_equal',0)
    rows += ['S_severity = $tbp_seek(S_equal_raw,15000)[.COMPLETION = NORMAL]']
    rows += value('S_severity','c','c','POBJECT n_c') + value('S_severity','d','d','POBJECT n_d') + [
        '$throwable_field(S_severity,n_c,"severity") = PINT 9',
        '$throwable_field(S_severity,n_d,"severity") = PINT 1',
        '$trace_visit_object_effect(S_severity,n_left,n_right,eps,z_S) = (S_severity,ORDER 0)',
    ] + [row.replace('POBJECT n_a','POBJECT n_c').replace('POBJECT n_b','POBJECT n_d') for row in raw('S_severity',1)]
    prefix='B|-1:1:-1|C|99:3:1:1|E|0:1:-1|H|'
    rows += output('S_severity_raw','S_hold',prefix)
    for name_cv in ('left','p','c'):
        rows += value('S_hold',name_cv,name_cv+'_hold','PNULL')
    rows += [
        '(HOBJECT n_left) <- S_hold.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HARRAY n_trace_p) = 2',
        '$propref_at(S_hold.PROPREFS,n_cell) = (ppropref_data)',
        '$propref_sources_valid(S_hold,n_cell,ppropref_data.SOURCES)',
    ]
    rows += output('S_hold','S_trace_only',prefix+'1|T|') + value('S_trace_only','a','a_trace_only','PNULL') + [
        '(HOBJECT n_left) <- S_trace_only.ALLOCATIONS',
        '~((HOBJECT n_p) <- S_trace_only.ALLOCATIONS)',
        '$heap_owners($heap_prune($heap_graph(S_trace_only)),HOBJECT n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_trace_only)),HARRAY n_trace_p) = 1',
        '$propref_at(S_trace_only.PROPREFS,n_cell) = (ppropref_data)',
    ]
    rows += output('S_trace_only','S_drop',prefix+'1|T|1|D|') + [
        '~((HOBJECT n_left) <- S_drop.ALLOCATIONS)',
        '$objectprops_record_at(S_drop.OBJECTPROPS,n_left) = eps',
        '$propref_at(S_drop.PROPREFS,n_cell) = eps',
        '(HCELL n_cell) <- S_drop.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_drop)),HCELL n_cell) = 2',
    ] + finish('S_drop',name) + [
        'S_done.STORE[n_cell] = DEFINED (PINT 5)',
        '$propref_at(S_done.PROPREFS,n_cell) = eps',
        '$entry_lookup(S_done.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_data.KEY) = (ALIAS n_cell)',
        '$entry_lookup(S_done.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
    ]
    return rows
