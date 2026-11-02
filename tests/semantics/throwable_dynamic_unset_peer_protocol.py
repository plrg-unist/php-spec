"""Reached deleted mirrors, current key order, real table COW and owners."""
import json
import re

from throwable_empty_clone_protocol import PREFIX
from throwable_interface_protocol import front
from throwable_previous_graph_protocol import raw, trace
from throwable_trace_recursion_protocol import error_rows
from throwable_uninitialized_peer_protocol import value, stage, mark

EXPECTED = {
    'dynamic-unset-count-key-reinsert-cow':
        'B|-1:1|C|1:-1|K|-1:1|T|1:-1|M|1:1|D|-1:1|E|0|V|2:0:-1|R|1:1|S|77:2|',
    'dynamic-unset-alias-cycle-owners-v2':
        'B|-1:1|C|99:3:1|D|-1:9|U|1|S|1:-1|X|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|R|0:1|H|1|D|1|A|4:99|K|1:1|',
}

# Only the supplied active table and a deliberately invalid dynamic INITIAL
# projection are derived. No source callback or held context is synthesized.
DERIVED = [
    '$trace_visit_object_effect(S,n_left,n_right,[HARRAY n_table_left],z_S) = (S,ORDERRECURSIVE)',
    'S_bad_initial = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_gone_left[.STATE = PROP_INITIAL],ppropertyslot_first_left,ppropertyslot_tail_left])]',
    '~$trace_visit_object_image(S_bad_initial,n_left)',
    '$trace_visit_object_effect(S_bad_initial,n_left,n_right,eps,z_S) = (S_bad_initial,ORDERUNSUPPORTED "Throwable property comparison")',
]


def dynamic(state,node,label,key,propstate):
    if propstate=='PROP_UNSET':
        return [
            f'$objectprops_record_at({state}.OBJECTPROPS,{node}) = (pobjectprops_{label})',
            f'ppropertyslot_{label} = {{DECL eps,NAME $ptascii({json.dumps(key)}),STATE PROP_UNSET}}',
            f'ppropertyslot_{label} <- pobjectprops_{label}.SLOTS',
            f'$property_slot_at(pobjectprops_{label}.SLOTS,$ptascii({json.dumps(key)})) = eps',
        ]
    return [
        f'$objectprops_record_at({state}.OBJECTPROPS,{node}) = (pobjectprops_{label})',
        f'$property_slot_at(pobjectprops_{label}.SLOTS,$ptascii({json.dumps(key)})) = (ppropertyslot_{label})',
        f'ppropertyslot_{label}.DECL = eps',
        f'ppropertyslot_{label}.STATE = {propstate}',
    ]


def cache(state,node,label,entries):
    items=','.join('ENTRY (KSTRING $ptascii('+json.dumps(key)+')) ('+item+')'
                   for key,item in entries)
    return [
        f'$object_table_at({state}.OBJECTTABLES,{node}) = (n_table_{label})',
        f'{state}.ARRAYS[n_table_{label}].ITEMS = [{items}]',
        f'$aggregate_hash_image({state},{node},n_table_{label})',
        f'$trace_visit_object_image({state},{node})',
    ]


def finish(state,name):
    return [f'S_done = $drive_steps({state},15000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tbp_output(S_done.EVENTS) = $ptascii('+json.dumps(EXPECTED[name])+')']


def checks(program,path,name):
    rows=front(program,path)
    rows+=trace('S','n_a','a','POBJECT n_left')[:4]
    rows+=trace('S','n_b','b','POBJECT n_right')[:4]
    rows+=[
        'S.OBJECTS[n_left] = INSTANCE porigin_packet',
        'S.OBJECTS[n_right] = INSTANCE porigin_packet',
        '$class_at(S.CLASSES,porigin_packet) = (pclassdesc_packet)',
        '$property_layout(S,porigin_packet,|S.CLASSES|) = eps',
        'pclassdesc_packet.PARENT = eps',
        '$class_dynamic_attribute(S,porigin_packet)',
        '$trace_visit_parent_path(S,pclassdesc_packet,eps)',
        '$trace_visit_interfaces(S,pclassdesc_packet)',
        '$trace_visit_object_header(S,n_left)',
        '$trace_visit_object_header(S,n_right)',
        '$trace_visit_object_image(S,n_left)',
        '$trace_visit_object_image(S,n_right)',
        '~$trace_visit_inline_pair(S,n_left,n_right)',
        '$object_table_ordinary(S,n_left)',
        '$object_table_ordinary(S,n_right)',
    ]
    for node in ('left','right'):
        rows+=dynamic('S','n_'+node,'gone_'+node,'gone','PROP_UNSET')
    if name=='dynamic-unset-count-key-reinsert-cow':
        for node,first,tail in [('left',1,9),('right',2,0)]:
            rows+=dynamic('S','n_'+node,'first_'+node,'first',f'PROP_VALUE (DIRECT (PINT {first}))')
            rows+=dynamic('S','n_'+node,'tail_'+node,'tail',f'PROP_VALUE (DIRECT (PINT {tail}))')
            rows+=cache('S','n_'+node,node,[('first',f'DIRECT (PINT {first})'),('tail',f'DIRECT (PINT {tail})')])
        rows+=[
            '$object_tables_valid(S)',
            '$entry_lookup(S.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("gone")) = eps',
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_table_left) = 1',
        ]+DERIVED+raw('S',-1)
        rows+=stage('S_raw','S_count','B|-1:1|C|')
        rows+=cache('S_count','n_left','left',[('first','DIRECT (PINT 1)'),('tail','DIRECT (PINT 9)'),('gone','DIRECT (PINT 99)')])+[
            '|S_count.ARRAYS[n_table_left].ITEMS| = 3',
            '|S_count.ARRAYS[n_table_right].ITEMS| = 2',
        ]+raw('S_count',1)
        rows+=stage('S_count_raw','S_key_skip','B|-1:1|C|1:-1|K|')
        rows+=cache('S_key_skip','n_right','right',[('first','DIRECT (PINT 2)'),('tail','DIRECT (PINT 0)'),('other','DIRECT (PINT 0)')])+[
            '$entry_lookup(S_key_skip.ARRAYS[n_table_right].ITEMS,KSTRING $ptascii("gone")) = eps',
            '$value_order_effect(S_key_skip,POBJECT n_a,POBJECT n_b,eps,z_S_key_skip) = (S_key_skip,ORDER $(-1))',
        ]
        rows+=stage('S_key_skip','S_tail','B|-1:1|C|1:-1|K|-1:1|T|')+[
            '$value_order_effect(S_tail,POBJECT n_a,POBJECT n_b,eps,z_S_tail) = (S_tail,ORDER 1)',
            '$value_order_effect(S_tail,POBJECT n_b,POBJECT n_a,eps,z_S_tail) = (S_tail,ORDER $(-1))',
        ]
        rows+=stage('S_tail','S_missing','B|-1:1|C|1:-1|K|-1:1|T|1:-1|M|')+[
            '$entry_lookup(S_missing.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("first")) = (DIRECT (PINT 2))',
            '$entry_lookup(S_missing.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("tail")) = (DIRECT (PINT 0))',
            '$entry_lookup(S_missing.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("other")) = eps',
            '$entry_lookup(S_missing.ARRAYS[n_table_right].ITEMS,KSTRING $ptascii("gone")) = eps',
            '$value_order_effect(S_missing,POBJECT n_b,POBJECT n_a,eps,z_S_missing) = (S_missing,ORDER 1)',
        ]+raw('S_missing',1)
        rows+=stage('S_missing_raw','S_delete','B|-1:1|C|1:-1|K|-1:1|T|1:-1|M|1:1|D|')
        rows+=dynamic('S_delete','n_left','gone_again','gone','PROP_UNSET')
        rows+=cache('S_delete','n_left','left',[('first','DIRECT (PINT 2)'),('tail','DIRECT (PINT 0)')])+[
            '$value_order_effect(S_delete,POBJECT n_a,POBJECT n_b,eps,z_S_delete) = (S_delete,ORDER $(-1))',
        ]
        rows+=stage('S_delete','S_equal','B|-1:1|C|1:-1|K|-1:1|T|1:-1|M|1:1|D|-1:1|E|')+[
            '$value_order_effect(S_equal,POBJECT n_a,POBJECT n_b,eps,z_S_equal) = (S_equal,ORDER 0)',
        ]
        rows+=stage('S_equal','S_view','B|-1:1|C|1:-1|K|-1:1|T|1:-1|M|1:1|D|-1:1|E|0|V|2:0:')
        rows+=value('S_view','view','view','PARRAY n_table_left')
        rows+=value('S_view','snapshot','snapshot','PARRAY n_table_left')
        rows+=cache('S_view','n_left','left_new',[('tail','DIRECT (PINT 0)'),('other','DIRECT (PINT 0)')])
        rows+=dynamic('S_view','n_left','first_deleted','first','PROP_UNSET')+[
            'n_table_left_new =/= n_table_left',
            'S_view.ARRAYS[n_table_left].ITEMS = [ENTRY (KSTRING $ptascii("first")) (DIRECT (PINT 2)),ENTRY (KSTRING $ptascii("tail")) (DIRECT (PINT 0)),ENTRY (KSTRING $ptascii("other")) (DIRECT (PINT 0))]',
            '$heap_owners($heap_prune($heap_graph(S_view)),HARRAY n_table_left) = 2',
            '$heap_owners($heap_prune($heap_graph(S_view)),HARRAY n_table_left_new) = 1',
            '$value_order_effect(S_view,POBJECT n_a,POBJECT n_b,eps,z_S_view) = (S_view,ORDER $(-1))',
        ]
        rows+=stage('S_view','S_reinsert','B|-1:1|C|1:-1|K|-1:1|T|1:-1|M|1:1|D|-1:1|E|0|V|2:0:-1|R|')
        rows+=cache('S_reinsert','n_left','left_new',[('tail','DIRECT (PINT 1)'),('other','DIRECT (PINT 0)'),('first','DIRECT (PINT 2)')])
        rows+=cache('S_reinsert','n_right','right',[('first','DIRECT (PINT 9)'),('tail','DIRECT (PINT 0)'),('other','DIRECT (PINT 0)')])
        rows+=dynamic('S_reinsert','n_left','first_reinserted','first','PROP_VALUE (DIRECT (PINT 2))')+[
            '$object_tables_valid(S_reinsert)',
            '$value_order_effect(S_reinsert,POBJECT n_b,POBJECT n_a,eps,z_S_reinsert) = (S_reinsert,ORDER 1)',
        ]+raw('S_reinsert',1)
        return rows+finish('S_reinsert_raw',name)+value('S_done','snapshot','snapshot_done','PARRAY n_snapshot_done')+[
            'n_snapshot_done =/= n_table_left',
            '$entry_lookup(S_done.ARRAYS[n_snapshot_done].ITEMS,KSTRING $ptascii("first")) = (DIRECT (PINT 77))',
            '$entry_lookup(S_done.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("first")) = (DIRECT (PINT 2))',
            '$entry_lookup(S_done.ARRAYS[n_table_left_new].ITEMS,KSTRING $ptascii("tail")) = (DIRECT (PINT 1))',
        ]
    assert name=='dynamic-unset-alias-cycle-owners-v2'
    rows+=dynamic('S','n_left','data_left','data','PROP_VALUE (ALIAS n_live)')
    rows+=dynamic('S','n_right','data_right','data','PROP_VALUE (DIRECT (PARRAY n_right_data))')+[
        '$lookup(S.ENV,$ptascii("live")) = (n_live)',
        'S.STORE[n_live] = DEFINED (PARRAY n_initial)',
        '$entry_lookup(S.ARRAYS[n_initial].ITEMS,KINT 0) = (DIRECT (PINT 1))',
        '$entry_lookup(S.ARRAYS[n_right_data].ITEMS,KINT 0) = (DIRECT (PINT 2))',
    ]
    rows+=cache('S','n_left','left',[('data','ALIAS n_live'),('tail','DIRECT (PINT 9)')])
    rows+=cache('S','n_right','right',[('data','DIRECT (PARRAY n_right_data)'),('tail','DIRECT (PINT 0)')])+[
        '$object_tables_valid(S)',
        '$heap_owners($heap_prune($heap_graph(S)),HCELL n_live) = 2',
    ]+raw('S',-1)
    rows+=stage('S_raw','S_cast','B|-1:1|C|99:3:')
    rows+=value('S_cast','view','view','PARRAY n_table_left')
    rows+=value('S_cast','snapshot','snapshot','PARRAY n_snapshot')+[
        '$object_table_at(S_cast.OBJECTTABLES,n_left) = (n_table_left)',
        '$entry_lookup(S_cast.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("data")) = (ALIAS n_live)',
        'S_cast.STORE[n_live] = DEFINED (PARRAY n_three)',
        '$entry_lookup(S_cast.ARRAYS[n_three].ITEMS,KINT 0) = (DIRECT (PINT 3))',
        '$entry_lookup(S_cast.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
        '$heap_owners($heap_prune($heap_graph(S_cast)),HARRAY n_table_left) = 2',
        '$heap_owners($heap_prune($heap_graph(S_cast)),HCELL n_live) = 2',
    ]+raw('S_cast',1)
    rows+=stage('S_cast_raw','S_delete','B|-1:1|C|99:3:1|D|')
    rows+=cache('S_delete','n_left','left_new',[('data','ALIAS n_live')])
    rows+=dynamic('S_delete','n_left','tail_deleted','tail','PROP_UNSET')+[
        'n_table_left_new =/= n_table_left',
        '$entry_lookup(S_delete.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("tail")) = (DIRECT (PINT 9))',
        '$heap_owners($heap_prune($heap_graph(S_delete)),HCELL n_live) = 3',
        '$heap_owners($heap_prune($heap_graph(S_delete)),HARRAY n_table_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_delete)),HARRAY n_table_left_new) = 1',
    ]+raw('S_delete',-1)
    rows+=mark('S_delete_raw','S_unset','B|-1:1|C|99:3:1|D|-1:9|U|')
    rows+=value('S_unset','discard','discard','PNULL')
    rows+=value('S_unset','weakDiscard','weak_discard','POBJECT n_weak_discard')
    rows+=dynamic('S_unset','n_left','gone_retired','gone','PROP_UNSET')+[
        '$weakref_get(S_unset,n_weak_discard) = PNULL',
        '$entry_lookup(S_unset.ARRAYS[n_table_left_new].ITEMS,KSTRING $ptascii("gone")) = eps',
    ]
    rows+=stage('S_unset','S_skip','B|-1:1|C|99:3:1|D|-1:9|U|1|S|')+[
        'S_skip.STORE[n_live] = DEFINED (PARRAY n_cycle_left)',
        '$entry_lookup(S_skip.ARRAYS[n_cycle_left].ITEMS,KINT 0) = (DIRECT (POBJECT n_left))',
        '$entry_lookup(S_skip.ARRAYS[n_table_right].ITEMS,KSTRING $ptascii("data")) = (DIRECT (PARRAY n_cycle_right))',
        '$entry_lookup(S_skip.ARRAYS[n_cycle_right].ITEMS,KINT 0) = (DIRECT (POBJECT n_right))',
        '|S_skip.ARRAYS[n_table_left_new].ITEMS| = 3',
        '|S_skip.ARRAYS[n_table_right].ITEMS| = 2',
        '$value_order_effect(S_skip,POBJECT n_a,POBJECT n_b,eps,z_S_skip) = (S_skip,ORDER 1)',
        '$value_order_effect(S_skip,POBJECT n_b,POBJECT n_a,eps,z_S_skip) = (S_skip,ORDER $(-1))',
    ]
    rows+=stage('S_skip','S_cycle','B|-1:1|C|99:3:1|D|-1:9|U|1|S|1:-1|X|')
    rows+=dynamic('S_cycle','n_left','stop_deleted','stop','PROP_UNSET')+[
        '$entry_lookup(S_cycle.ARRAYS[n_table_left_new].ITEMS,KSTRING $ptascii("stop")) = eps',
        '$value_order_effect(S_cycle,POBJECT n_a,POBJECT n_b,eps,z_S_cycle) = (S_cycle,ORDERRECURSIVE)',
        'S_cycle_effect = S_cycle',
        'pbin = SPACESHIP',
    ]
    rows+=[re.sub(r'\bS\b','S_cycle',re.sub(r'\bS_','S_cycle_',row)) for row in error_rows()]
    rows+=['S_cycle_error.ARRAYS[n_error_trace].ITEMS = eps']
    recovery=EXPECTED[name].split('R|')[0]+'R|'
    rows+=stage('S_cycle_one[.COMPLETION = NORMAL]','S_identity',recovery)+[
        '$entry_lookup(S_identity.ARRAYS[n_table_right].ITEMS,KSTRING $ptascii("data")) = (DIRECT (PARRAY n_identity_array))',
        '$entry_lookup(S_identity.ARRAYS[n_identity_array].ITEMS,KINT 0) = (DIRECT (POBJECT n_left))',
        '$trace_visit_object_effect(S_identity,n_left,n_left,eps,z_S_identity) = (S_identity,ORDER 0)',
    ]+raw('S_identity',0)
    hold=EXPECTED[name].split('H|')[0]+'H|'
    rows+=mark('S_identity_raw','S_hold',hold)
    rows+=value('S_hold','left','left_hold','PNULL')+value('S_hold','a','a_hold','PNULL')+[
        '(HOBJECT n_left) <- S_hold.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HCELL n_live) = 3',
    ]
    rows+=mark('S_hold','S_drop',hold+'1|D|')+[
        '~((HOBJECT n_left) <- S_drop.ALLOCATIONS)',
        '$object_table_at(S_drop.OBJECTTABLES,n_left) = eps',
        '$objectprops_record_at(S_drop.OBJECTPROPS,n_left) = eps',
        '(HCELL n_live) <- S_drop.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_drop)),HCELL n_live) = 2',
        '$entry_lookup(S_drop.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("data")) = (ALIAS n_live)',
    ]
    rows+=stage('S_drop','S_foreign',EXPECTED[name].split('K|')[0]+'K|')
    rows+=value('S_foreign','c','c','POBJECT n_c')+value('S_foreign','d','d','POBJECT n_d')+[
        '$value_order_effect(S_foreign,POBJECT n_c,POBJECT n_d,eps,z_S_foreign) = (S_foreign,ORDER 1)',
        '$value_order_effect(S_foreign,POBJECT n_d,POBJECT n_c,eps,z_S_foreign) = (S_foreign,ORDER 1)',
    ]
    return rows+finish('S_foreign',name)+[
        'S_done.STORE[n_live] = DEFINED (PARRAY n_final)',
        '$entry_lookup(S_done.ARRAYS[n_final].ITEMS,KINT 0) = (DIRECT (PINT 4))',
        '$entry_lookup(S_done.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
    ]
