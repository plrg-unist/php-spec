"""Reached nonpublic physical keys, typed aliases and final type-source release."""
import json

from throwable_nonpublic_cases import EXPECTED as SOURCE_EXPECTED
from throwable_interface_protocol import front
from throwable_previous_graph_protocol import raw, trace
from throwable_builtin_previous_protocol import PREFIX as BASE_PREFIX

EXPECTED = {name: data.decode() for name, data in SOURCE_EXPECTED.items()
            if not name.endswith('-control')}
PREFIX = BASE_PREFIX + r'''
dec $tnp_seek_output(pstate, nat, ptbytes) : pstate
def $tnp_seek_output(S, n, ptbytes) = S
  -- if $tbp_output(S.EVENTS) = ptbytes \/ n = 0
def $tnp_seek_output(S, n, ptbytes) = $tnp_seek_output($drive_steps(S, 1)[.COMPLETION = NORMAL], $nabs($(n - 1)), ptbytes)
  -- if $tbp_output(S.EVENTS) =/= ptbytes /\ $(n > 0)
  -- if S.COMPLETION = NORMAL
def $tnp_seek_output(S, n, ptbytes) = S -- otherwise
'''

# Only these projected slot mutations and supplied identity guard are derived.
DERIVED = [
    'S_badkey = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_base_left[.NAME = $ptascii("base")],ppropertyslot_rank_left,ppropertyslot_tail_left,ppropertyslot_leaf_left])]',
    '~$trace_visit_object_image(S_badkey,n_left)',
    '$trace_visit_object_effect(S_badkey,n_left,n_right,eps,z_S) = (S_badkey,ORDERUNSUPPORTED "Throwable property comparison")',
    '$trace_visit_object_effect(S_badkey,n_left,n_left,[HOBJECT n_left],z_S) = (S_badkey,ORDER 0)',
    'S_baddecl = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_base_left[.DECL = (ppropertydesc_rank.ORIGIN)],ppropertyslot_rank_left,ppropertyslot_tail_left,ppropertyslot_leaf_left])]',
    '~$trace_visit_object_image(S_baddecl,n_left)',
    '$trace_visit_object_effect(S_baddecl,n_left,n_right,eps,z_S) = (S_baddecl,ORDERUNSUPPORTED "Throwable property comparison")',
    'S_unset = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_base_left[.STATE = PROP_UNSET],ppropertyslot_rank_left,ppropertyslot_tail_left,ppropertyslot_leaf_left])]',
    '~$trace_visit_object_image(S_unset,n_left)',
    '$trace_visit_object_effect(S_unset,n_left,n_right,eps,z_S) = (S_unset,ORDERUNSUPPORTED "Throwable property comparison")',
]


def value(state, name, label, item):
    return [f'$lookup({state}.ENV,$ptascii({json.dumps(name)})) = (n_cv_{label})',
            f'{state}.STORE[n_cv_{label}] = DEFINED ({item})']


def slot(state, node, label, key, item, descriptor=None):
    rows = [f'$objectprops_record_at({state}.OBJECTPROPS,{node}) = (pobjectprops_{label})',
            f'$property_slot_at(pobjectprops_{label}.SLOTS,{key}) = (ppropertyslot_{label})',
            f'ppropertyslot_{label}.STATE = PROP_VALUE ({item})']
    if descriptor:
        rows += [f'ppropertyslot_{label}.DECL = ({descriptor}.ORIGIN)']
    return rows


def output(state, out, prefix):
    return [f'{out} = $tnp_seek_output({state},10000,$ptascii({json.dumps(prefix)}))',
            f'$tbp_output({out}.EVENTS) = $ptascii({json.dumps(prefix)})']


def finish(state, name):
    return [f'S_done = $drive_steps({state},10000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name]) + ')']


def start(program, path):
    return front(program, path) + trace('S', 'n_a', 'a', 'POBJECT n_left')[:4] + \
        trace('S', 'n_b', 'b', 'POBJECT n_right')[:4] + [
            'S.OBJECTS[n_left] = INSTANCE porigin_leaf',
            'S.OBJECTS[n_right] = INSTANCE porigin_leaf',
            '$class_at(S.CLASSES,porigin_leaf) = (pclassdesc_leaf)',
            '$trace_visit_interfaces(S,pclassdesc_leaf)',
            '$trace_visit_parent_path(S,pclassdesc_leaf,eps)',
            '$property_layout(S,porigin_leaf,|S.CLASSES|) = ppropertydesc_layout*',
            '~$trace_instance_public(ppropertydesc_layout*)',
            '$trace_visit_object_header(S,n_left)',
            '$trace_visit_object_header(S,n_right)',
            '$trace_visit_object_image(S,n_left)',
            '$trace_visit_object_image(S,n_right)',
            '$trace_visit_inline_pair(S,n_left,n_right)',
            '$object_table_at(S.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S.OBJECTTABLES,n_right) = eps',
        ]


def checks(program, path, name):
    rows = start(program, path)
    if name == 'nonpublic-inline-physical-severity':
        rows += [
            '$class_link_at(S.LINKEDPARENTS,porigin_leaf) = (SOURCE_PARENT porigin_base)',
            '$class_at(S.CLASSES,porigin_base) = (pclassdesc_base)',
            'ppropertydesc_layout* = [ppropertydesc_base,ppropertydesc_rank,ppropertydesc_tail,ppropertydesc_leaf]',
            'ppropertydesc_base.KEY = [0] ++ $ptascii("Base159") ++ [0] ++ $ptascii("base")',
            'ppropertydesc_base.VISIBILITY = PROPERTY_PRIVATE',
            'ppropertydesc_rank.KEY = [0,42,0] ++ $ptascii("rank")',
            'ppropertydesc_rank.VISIBILITY = PROPERTY_PROTECTED',
            'ppropertydesc_tail.KEY = $ptascii("tail")',
            'ppropertydesc_tail.VISIBILITY = PROPERTY_PUBLIC',
            'ppropertydesc_leaf.KEY = [0] ++ $ptascii("Packet159") ++ [0] ++ $ptascii("leaf")',
            'ppropertydesc_leaf.VISIBILITY = PROPERTY_PRIVATE',
            '$property_desc_at(pclassdesc_base.PROPERTIES,ppropertydesc_base.KEY) = (ppropertydesc_base)',
            '$property_desc_at(pclassdesc_leaf.PROPERTIES,ppropertydesc_rank.KEY) = (ppropertydesc_rank)',
        ]
        for label, left, right in [('base',1,2),('rank',9,1),('tail',9,1),('leaf',9,1)]:
            for node, item in [('left',left),('right',right)]:
                rows += slot('S','n_'+node,label+'_'+node,'ppropertydesc_'+label+'.KEY',
                             'DIRECT (PINT '+str(item)+')','ppropertydesc_'+label)
        rows += [
            '$objectprops_at(S.OBJECTPROPS,n_left) = ([ppropertyslot_base_left,ppropertyslot_rank_left,ppropertyslot_tail_left,ppropertyslot_leaf_left])',
            '$property_unique_names([ppropertyslot_base_left,ppropertyslot_rank_left,ppropertyslot_tail_left,ppropertyslot_leaf_left])',
            '$trace_object_current_entries(S,n_left) = [ENTRY (KSTRING ppropertydesc_base.KEY) (INDIRECT n_left ppropertydesc_base.KEY),ENTRY (KSTRING ppropertydesc_rank.KEY) (INDIRECT n_left ppropertydesc_rank.KEY),ENTRY (KSTRING ppropertydesc_tail.KEY) (INDIRECT n_left ppropertydesc_tail.KEY),ENTRY (KSTRING ppropertydesc_leaf.KEY) (INDIRECT n_left ppropertydesc_leaf.KEY)]',
        ] + DERIVED + raw('S',-1)
        rows += output('S_raw','S_warm_prefix','B|-1:0:1:1:1:0:0:1|W|1:')
        rows += [
            'S_warm = $tbp_seek(S_warm_prefix,10000)[.COMPLETION = NORMAL]',
            '$throwable_field(S_warm,n_a,"string") = PSTRING preqbytes_warm',
            '$throwable_field(S_warm,n_b,"string") = PSTRING preqbytes_warm',
            'preqbytes_warm =/= eps',
        ] + raw('S_warm',-1)
        rows += [
            'S_noise = $tbp_seek(S_warm_raw,10000)[.COMPLETION = NORMAL]',
            '$trace_visit_object_effect(S_noise,n_left,n_right,eps,z_S) = (S_noise,ORDER $(-1))',
            'S_rank = $tbp_next(S_noise)',
        ]
        rows += slot('S_rank','n_left','base_rank','ppropertydesc_base.KEY','DIRECT (PINT 2)')
        rows += slot('S_rank','n_left','rank_rank','ppropertydesc_rank.KEY','DIRECT (PINT 9)')
        rows += raw('S_rank',1)
        rows += output('S_rank_raw','S_equal_prefix','B|-1:0:1:1:1:0:0:1|W|1:-1|N|-1|R|1|T|1|L|1|E|')
        rows += ['S_equal = $tbp_seek(S_equal_prefix,10000)[.COMPLETION = NORMAL]'] + raw('S_equal',0)
        rows += ['S_severity = $tbp_seek(S_equal_raw,10000)[.COMPLETION = NORMAL]']
        rows += value('S_severity','c','c','POBJECT n_c') + value('S_severity','d','d','POBJECT n_d')
        rows += [
            '$throwable_field(S_severity,n_c,"severity") = PINT 9',
            '$throwable_field(S_severity,n_d,"severity") = PINT 1',
            '$trace_visit_object_effect(S_severity,n_left,n_right,eps,z_S) = (S_severity,ORDER 0)',
        ]
        rows += [row.replace('POBJECT n_a','POBJECT n_c').replace('POBJECT n_b','POBJECT n_d')
                 for row in raw('S_severity',1)]
        return rows + finish('S_severity_raw',name)
    assert name == 'nonpublic-typed-alias-owners'
    rows += [
        'ppropertydesc_layout* = [ppropertydesc_data,ppropertydesc_tail]',
        'ppropertydesc_data.KEY = [0] ++ $ptascii("Packet159") ++ [0] ++ $ptascii("data")',
        'ppropertydesc_data.VISIBILITY = PROPERTY_PRIVATE',
        'ppropertydesc_data.TYPE =/= eps',
        'ppropertydesc_tail.KEY = [0,42,0] ++ $ptascii("tail")',
        'ppropertydesc_tail.VISIBILITY = PROPERTY_PROTECTED',
    ]
    rows += slot('S','n_left','data_left','ppropertydesc_data.KEY','ALIAS n_cell','ppropertydesc_data')
    rows += slot('S','n_right','data_right','ppropertydesc_data.KEY','DIRECT (PARRAY n_data_right)','ppropertydesc_data')
    rows += [
        '$lookup(S.ENV,$ptascii("live")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_data_left)',
        '$entry_lookup(S.ARRAYS[n_data_left].ITEMS,KINT 0) = (DIRECT (PINT 1))',
        '$entry_lookup(S.ARRAYS[n_data_right].ITEMS,KINT 0) = (DIRECT (PINT 2))',
        '$propref_at(S.PROPREFS,n_cell) = (ppropref_data)',
        'ppropref_data.SOURCES = [OBJECT_PROP_SOURCE n_left ppropertydesc_data.KEY ppropertydesc_data.ORIGIN]',
        '$propref_sources_valid(S,n_cell,ppropref_data.SOURCES)',
    ] + raw('S',-1)
    prefix='B|-1:1|C|99:3:'
    rows += output('S_raw','S_cached_prefix',prefix)
    rows += ['S_cached = $tbp_seek(S_cached_prefix,10000)[.COMPLETION = NORMAL]']
    rows += value('S_cached','view','view','PARRAY n_view')
    rows += value('S_cached','snapshot','snapshot','PARRAY n_snapshot')
    rows += [
        '$object_table_at(S_cached.OBJECTTABLES,n_left) = (n_table_left)',
        '$object_table_at(S_cached.OBJECTTABLES,n_right) = (n_table_right)',
        '$object_tables_valid(S_cached)',
        'S_cached.ARRAYS[n_table_left].ITEMS = [ENTRY (KSTRING ppropertydesc_data.KEY) (INDIRECT n_left ppropertydesc_data.KEY),ENTRY (KSTRING ppropertydesc_tail.KEY) (INDIRECT n_left ppropertydesc_tail.KEY)]',
        '$entry_lookup(S_cached.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_data.KEY) = (ALIAS n_cell)',
        '$entry_lookup(S_cached.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
        'S_cached.STORE[n_cell] = DEFINED (PARRAY n_three)',
        '$entry_lookup(S_cached.ARRAYS[n_three].ITEMS,KINT 0) = (DIRECT (PINT 3))',
        '$heap_owners($heap_prune($heap_graph(S_cached)),HCELL n_cell) = 3',
        '$propref_at(S_cached.PROPREFS,n_cell) = (ppropref_data)',
    ] + raw('S_cached',1)
    prefix+='1|T|TypeError:3|'
    rows += output('S_cached_raw','S_rejected',prefix)
    rows += [
        'S_rejected.STORE[n_cell] = DEFINED (PARRAY n_three)',
        '$propref_at(S_rejected.PROPREFS,n_cell) = (ppropref_data)',
        '$propref_sources_valid(S_rejected,n_cell,ppropref_data.SOURCES)',
        'S_equal = $tbp_seek(S_rejected,10000)[.COMPLETION = NORMAL]',
    ] + raw('S_equal',0)
    prefix+='E|0|H|'
    rows += output('S_equal_raw','S_hold',prefix)
    rows += value('S_hold','left','left_hold','PNULL') + value('S_hold','a','a_hold','PNULL')
    rows += [
        '(HOBJECT n_left) <- S_hold.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_left) = 1',
        '$propref_at(S_hold.PROPREFS,n_cell) = (ppropref_data)',
        '$propref_sources_valid(S_hold,n_cell,ppropref_data.SOURCES)',
    ]
    rows += output('S_hold','S_drop',prefix+'1|D|')
    rows += [
        '~((HOBJECT n_left) <- S_drop.ALLOCATIONS)',
        '$objectprops_record_at(S_drop.OBJECTPROPS,n_left) = eps',
        '$propref_at(S_drop.PROPREFS,n_cell) = eps',
        '(HCELL n_cell) <- S_drop.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_drop)),HCELL n_cell) = 2',
    ] + finish('S_drop',name)
    rows += [
        'S_done.STORE[n_cell] = DEFINED (PINT 5)',
        '$propref_at(S_done.PROPREFS,n_cell) = eps',
        '$entry_lookup(S_done.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_data.KEY) = (ALIAS n_cell)',
        '$entry_lookup(S_done.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
    ]
    return rows
