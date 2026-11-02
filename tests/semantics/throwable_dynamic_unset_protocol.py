"""Reached deleted-history clone selection, locators and final typed sources."""
import json

from throwable_dynamic_unset_cases import CASES as AUTHOR_CASES, EXPECTED as AUTHOR_EXPECTED
from throwable_dynamic_unset_order_cases import CASES as ORDER_CASES, EXPECTED as ORDER_EXPECTED
CASES = dict(AUTHOR_CASES, **ORDER_CASES)
SOURCE_EXPECTED = dict(AUTHOR_EXPECTED, **ORDER_EXPECTED)
from throwable_dynamic_unset_peer_protocol import PREFIX, dynamic, cache, value, stage, mark
from throwable_interface_protocol import front
from throwable_previous_graph_protocol import raw, trace
from throwable_uninitialized_protocol import slot, table

EXPECTED={name:data.decode() for name,data in SOURCE_EXPECTED.items() if not name.endswith('-control')}
DERIVED=['$trace_visit_object_effect(S_clone,n_left,n_copy,[HARRAY n_table_left],z_S_clone) = (S_clone,ORDER 0)']


def finish(state,name):
    return [f'S_done = $drive_steps({state},15000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tbp_output(S_done.EVENTS) = $ptascii('+json.dumps(EXPECTED[name])+')']


def pair_raw(state,result,left='n_a',right='n_b',effect=None):
    return [row.replace('POBJECT n_a','POBJECT __PAIR_LEFT__').replace('POBJECT n_b','POBJECT '+right).replace('POBJECT __PAIR_LEFT__','POBJECT '+left)
            for row in raw(state,result,effect)]


def operands(state,left,right):
    return [f'$string_compare_values({state},poperand_{state},{state}.RESULT,z_{state}) = ((S_read_{state},POBJECT {left},POBJECT {right}))']


def common():
    return [
        'S.OBJECTS[n_left] = INSTANCE porigin_packet',
        'S.OBJECTS[n_right] = INSTANCE porigin_packet',
        '$class_at(S.CLASSES,porigin_packet) = (pclassdesc_packet)',
        '$class_dynamic_attribute(S,porigin_packet)',
        '$trace_visit_parent_path(S,pclassdesc_packet,eps)',
        '$trace_visit_interfaces(S,pclassdesc_packet)',
        '$trace_visit_object_header(S,n_left)',
        '$trace_visit_object_header(S,n_right)',
        '$trace_visit_object_image(S,n_left)',
        '$trace_visit_object_image(S,n_right)',
        '$trace_visit_slots_admitted($object_table_slots_at(S,n_left))',
        '$object_table_ordinary(S,n_left)',
        '$object_table_ordinary(S,n_right)',
        '~$trace_visit_inline_pair(S,n_left,n_right)',
        '$object_table_at(S.OBJECTTABLES,n_right) = eps',
    ]


def checks(program,path,name):
    if name=='dynamic-reinsert-later-key-stability':
        return order_checks(program,path)
    rows=front(program,path)
    rows+=trace('S','n_a','a','POBJECT n_left')[:4]
    rows+=trace('S','n_b','b','POBJECT n_right')[:4]
    rows+=common()+dynamic('S','n_left','gone_left','gone','PROP_UNSET')
    if name=='dynamic-deleted-empty-clone-owners':
        rows+=[
            '$property_layout(S,porigin_packet,|S.CLASSES|) = eps',
            '$object_table_slots_at(S,n_right) = eps',
            'pclassdesc_packet.INTERFACES =/= eps',
            '$object_table_dynamic_history($object_table_slots_at(S,n_left))',
        ]+cache('S','n_left','left',[])+[
            '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_table_left) = 1',
            '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_effect,ORDER 0)',
            'n_table_right = |S.ARRAYS|',
            '|S_effect.ARRAYS| = $(|S.ARRAYS| + 1)',
            '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_table_right)',
            'S_effect.ARRAYS[n_table_right].ITEMS = eps',
            '$object_tables_valid(S_effect)',
        ]+raw('S',0,'S_effect')
        rows+=stage('S_raw','S_clone','B|0:0|C|')
        rows+=value('S_clone','copy','copy','POBJECT n_copy')
        rows+=value('S_clone','c','c','POBJECT n_c')+value('S_clone','d','d','POBJECT n_d')
        rows+=trace('S_clone','n_c','c','POBJECT n_left')[:4]+trace('S_clone','n_d','d','POBJECT n_copy')[:4]
        rows+=operands('S_clone','n_c','n_d')
        rows+=value('S_clone','view','view','PARRAY n_table_left')
        rows+=dynamic('S_clone','n_copy','gone_copy','gone','PROP_UNSET')+[
            'n_copy =/= n_left',
            'S_clone.OBJECTS[n_copy] = INSTANCE porigin_packet',
            '$object_table_at(S_clone.OBJECTTABLES,n_left) = (n_table_left)',
            '$object_table_at(S_clone.OBJECTTABLES,n_copy) = (n_table_left)',
            'S_clone.ARRAYS[n_table_left].ITEMS = eps',
            '$heap_owners($heap_prune($heap_graph(S_clone)),HARRAY n_table_left) = 3',
            '$clone_dynamic_share_ready(S_clone,n_left)',
            '~$clone_empty_callback_ready(S_clone,n_left)',
            '$object_tables_valid(S_clone)',
        ]+DERIVED+pair_raw('S_clone',0,'n_c','n_d')
        rows+=stage('S_clone_raw','S_write','B|0:0|C|0|W|')
        rows+=cache('S_write','n_copy','copy',[('extra','DIRECT (PINT 1)')])+[
            'n_table_copy =/= n_table_left',
            '$object_table_at(S_write.OBJECTTABLES,n_left) = (n_table_left)',
            'S_write.ARRAYS[n_table_left].ITEMS = eps',
            '$heap_owners($heap_prune($heap_graph(S_write)),HARRAY n_table_left) = 2',
        ]+pair_raw('S_write',-1,'n_c','n_d')
        prefix='B|0:0|C|0|W|-1:1|V|0:0|H|'
        rows+=mark('S_write_raw','S_hold',prefix)
        for cv in ('left','a','c'):
            rows+=value('S_hold',cv,cv+'_hold','PNULL')
        rows+=value('S_hold','sourceView','source_view','PARRAY n_table_left')+[
            '(HOBJECT n_left) <- S_hold.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_left) = 1',
            '$heap_owners($heap_prune($heap_graph(S_hold)),HARRAY n_table_left) = 2',
            'S_hold.ARRAYS[n_table_left].ITEMS = eps',
        ]
        rows+=mark('S_hold','S_drop',prefix+'1|D|')+[
            '~((HOBJECT n_left) <- S_drop.ALLOCATIONS)',
            '$object_table_at(S_drop.OBJECTTABLES,n_left) = eps',
            '(HARRAY n_table_left) <- S_drop.ALLOCATIONS',
            '$heap_owners($heap_prune($heap_graph(S_drop)),HARRAY n_table_left) = 1',
        ]
        prefix+='1|D|1|A|2|Q|'
        rows+=mark('S_drop','S_callback',prefix)
        rows+=value('S_callback','target','target','POBJECT n_target')
        rows+=dynamic('S_callback','n_target','gone_callback','gone','PROP_UNSET')
        rows+=cache('S_callback','n_target','callback',[])+[
            'S_callback.OBJECTS[n_target] = INSTANCE porigin_callback',
            '$property_layout(S_callback,porigin_callback,|S_callback.CLASSES|) = eps',
            '$clone_method(S_callback,n_target) =/= eps',
            '$clone_empty_callback_ready(S_callback,n_target)',
            '~$clone_dynamic_share_ready(S_callback,n_target)',
            '$clone_mixed_ready(S_callback,n_target)',
            '~$clone_mixed_dynamic($object_table_slots_at(S_callback,n_target))',
            '$entry_lookup(S_callback.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("after")) = (DIRECT (PINT 2))',
        ]
        rows+=stage('S_callback','S_after_callback',prefix+'G|K|')
        rows+=value('S_after_callback','callbackCopy','callback_copy','POBJECT n_callback_copy')
        rows+=value('S_after_callback','e','e','POBJECT n_e')+value('S_after_callback','f','f','POBJECT n_f')
        rows+=operands('S_after_callback','n_e','n_f')+[
            '$object_table_at(S_after_callback.OBJECTTABLES,n_target) = (n_table_callback)',
            '$object_table_at(S_after_callback.OBJECTTABLES,n_callback_copy) = eps',
            '$objectprops_record_at(S_after_callback.OBJECTPROPS,n_callback_copy) = (pobjectprops_callback_copy)',
            'pobjectprops_callback_copy.SLOTS = eps',
            '~pobjectprops_callback_copy.MATERIALIZED',
            '$trace_visit_object_image(S_after_callback,n_callback_copy)',
            '$value_order_effect(S_after_callback,POBJECT n_e,POBJECT n_f,eps,z_S_after_callback) = (S_callback_effect,ORDER 0)',
            '|S_callback_effect.ARRAYS| = $(|S_after_callback.ARRAYS| + 1)',
            'n_table_callback_copy = |S_after_callback.ARRAYS|',
            '$object_table_at(S_callback_effect.OBJECTTABLES,n_callback_copy) = (n_table_callback_copy)',
            'S_callback_effect.ARRAYS[n_table_callback_copy].ITEMS = eps',
            '$object_tables_valid(S_callback_effect)',
        ]+pair_raw('S_after_callback',0,'n_e','n_f','S_callback_effect')
        return rows+finish('S_after_callback_raw',name)
    assert name=='declared-deleted-history-clone-alias'
    descs=['ppropertydesc_hole','ppropertydesc_data','ppropertydesc_tail']
    rows+=[
        '$property_layout(S,porigin_packet,|S.CLASSES|) = [ppropertydesc_hole,ppropertydesc_data,ppropertydesc_tail]',
        'ppropertydesc_hole.KEY = [0] ++ $ptascii("Packet161") ++ [0] ++ $ptascii("hole")',
        'ppropertydesc_hole.DEFAULT = PROP_UNINITIALIZED',
        'ppropertydesc_data.KEY = [0] ++ $ptascii("Packet161") ++ [0] ++ $ptascii("data")',
        'ppropertydesc_data.TYPE =/= eps',
        'ppropertydesc_tail.KEY = [0,42,0] ++ $ptascii("tail")',
    ]
    for node in ('left','right'):
        rows+=slot('S','n_'+node,'hole_'+node,'ppropertydesc_hole','PROP_INITIAL')
    rows+=slot('S','n_left','data_left','ppropertydesc_data','PROP_VALUE (ALIAS n_cell)')
    rows+=slot('S','n_right','data_right','ppropertydesc_data','PROP_VALUE (DIRECT (PARRAY n_right_data))')
    rows+=table('S','n_left','left',descs)+[
        '$lookup(S.ENV,$ptascii("live")) = (n_cell)',
        'S.STORE[n_cell] = DEFINED (PARRAY n_initial)',
        '$entry_lookup(S.ARRAYS[n_initial].ITEMS,KINT 0) = (DIRECT (PINT 1))',
        '$entry_lookup(S.ARRAYS[n_right_data].ITEMS,KINT 0) = (DIRECT (PINT 2))',
        '$object_table_item(S,INDIRECT n_left ppropertydesc_hole.KEY) = UNINITIALIZED',
        '$entry_lookup(S.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("gone")) = eps',
        '$value_order_effect(S,POBJECT n_a,POBJECT n_b,eps,z_S) = (S_effect,ORDER $(-1))',
        'n_table_right = |S.ARRAYS|',
        '|S_effect.ARRAYS| = $(|S.ARRAYS| + 1)',
        '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_table_right)',
        '|S_effect.ARRAYS[n_table_left].ITEMS| = 3',
        '|S_effect.ARRAYS[n_table_right].ITEMS| = 3',
    ]+raw('S',-1,'S_effect')
    rows+=stage('S_raw','S_clone','B|-1:1|C|')
    rows+=value('S_clone','copy','copy','POBJECT n_copy')
    rows+=value('S_clone','c','c','POBJECT n_c')+value('S_clone','d','d','POBJECT n_d')
    rows+=value('S_clone','view','view','PARRAY n_view')+operands('S_clone','n_c','n_d')
    rows+=dynamic('S_clone','n_copy','gone_copy','gone','PROP_UNSET')
    rows+=slot('S_clone','n_copy','hole_copy','ppropertydesc_hole','PROP_INITIAL')
    rows+=slot('S_clone','n_copy','data_copy','ppropertydesc_data','PROP_VALUE (ALIAS n_cell)')
    rows+=table('S_clone','n_copy','copy',descs)+[
        'n_copy =/= n_left',
        'n_table_copy =/= n_table_left',
        'n_table_copy =/= n_table_right',
        '$entry_lookup(S_clone.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_hole.KEY) = eps',
        '$entry_lookup(S_clone.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_data.KEY) = (ALIAS n_cell)',
        '$heap_owners($heap_prune($heap_graph(S_clone)),HCELL n_cell) = 4',
        '$propref_at(S_clone.PROPREFS,n_cell) = (ppropref_data)',
        '|ppropref_data.SOURCES| = 2',
        '(OBJECT_PROP_SOURCE n_left ppropertydesc_data.KEY ppropertydesc_data.ORIGIN) <- ppropref_data.SOURCES',
        '(OBJECT_PROP_SOURCE n_copy ppropertydesc_data.KEY ppropertydesc_data.ORIGIN) <- ppropref_data.SOURCES',
        '$propref_sources_valid(S_clone,n_cell,ppropref_data.SOURCES)',
        '$clone_mixed_ready(S_clone,n_left)',
        '~$clone_mixed_dynamic($object_table_slots_at(S_clone,n_left))',
        '~$clone_dynamic_share_ready(S_clone,n_left)',
        '~$clone_empty_callback_ready(S_clone,n_left)',
        '$object_tables_valid(S_clone)',
    ]+pair_raw('S_clone',0,'n_c','n_d')
    rows+=stage('S_clone_raw','S_tail','B|-1:1|C|0|L|')
    rows+=slot('S_tail','n_left','tail_source','ppropertydesc_tail','PROP_VALUE (DIRECT (PINT 0))')
    rows+=slot('S_tail','n_copy','tail_copy','ppropertydesc_tail','PROP_VALUE (DIRECT (PINT 1))')+[
        '$object_table_item(S_tail,INDIRECT n_left ppropertydesc_tail.KEY) = DIRECT (PINT 0)',
        '$object_table_item(S_tail,INDIRECT n_copy ppropertydesc_tail.KEY) = DIRECT (PINT 1)',
    ]+pair_raw('S_tail',-1,'n_c','n_d')
    rows+=stage('S_tail_raw','S_live','B|-1:1|C|0|L|-1:1|V|99:3:')
    rows+=value('S_live','snapshot','snapshot','PARRAY n_snapshot')+[
        'S_live.STORE[n_cell] = DEFINED (PARRAY n_three)',
        '$entry_lookup(S_live.ARRAYS[n_three].ITEMS,KINT 0) = (DIRECT (PINT 3))',
        '$entry_lookup(S_live.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
    ]+pair_raw('S_live',-1,'n_c','n_d')
    prefix='B|-1:1|C|0|L|-1:1|V|99:3:-1|T|3|H|'
    rows+=mark('S_live_raw','S_original_dead',prefix)
    for cv in ('left','a','c'):
        rows+=value('S_original_dead',cv,cv+'_dead','PNULL')
    rows+=[
        '~((HOBJECT n_left) <- S_original_dead.ALLOCATIONS)',
        '$object_table_at(S_original_dead.OBJECTTABLES,n_left) = eps',
        '$propref_at(S_original_dead.PROPREFS,n_cell) = (ppropref_copy)',
        'ppropref_copy.SOURCES = [OBJECT_PROP_SOURCE n_copy ppropertydesc_data.KEY ppropertydesc_data.ORIGIN]',
        '$propref_sources_valid(S_original_dead,n_cell,ppropref_copy.SOURCES)',
        '$heap_owners($heap_prune($heap_graph(S_original_dead)),HCELL n_cell) = 3',
    ]
    rows+=mark('S_original_dead','S_copy_held',prefix+'1|P|3|')+[
        'S_copy_held.STORE[n_cell] = DEFINED (PARRAY n_three)',
        '$propref_at(S_copy_held.PROPREFS,n_cell) = (ppropref_copy)',
    ]
    rows+=mark('S_copy_held','S_copy_dead',prefix+'1|P|3|D|')+[
        '~((HOBJECT n_copy) <- S_copy_dead.ALLOCATIONS)',
        '$object_table_at(S_copy_dead.OBJECTTABLES,n_copy) = eps',
        '$propref_at(S_copy_dead.PROPREFS,n_cell) = eps',
        '(HCELL n_cell) <- S_copy_dead.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_copy_dead)),HCELL n_cell) = 2',
    ]+finish('S_copy_dead',name)+[
        'S_done.STORE[n_cell] = DEFINED (PINT 5)',
        '$entry_lookup(S_done.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_data.KEY) = (ALIAS n_cell)',
        '$entry_lookup(S_done.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
    ]
    return rows


def order_checks(program,path):
    # The witness checks current storage independently of older root admissions.
    rows=[row for row in front(program,path)
          if not row.startswith('$throwable_builtin_previous_order(')]
    rows+=trace('S','n_a','a','POBJECT n_left')[:4]+trace('S','n_b','b','POBJECT n_right')[:4]+[
        'S.OBJECTS[n_left] = INSTANCE porigin_packet',
        'S.OBJECTS[n_right] = INSTANCE porigin_packet',
        '$property_layout(S,porigin_packet,|S.CLASSES|) = eps',
        '$class_dynamic_attribute(S,porigin_packet)',
        '$trace_visit_object_header(S,n_left)',
        '$trace_visit_object_header(S,n_right)',
        '$trace_visit_object_image(S,n_left)',
        '$trace_visit_object_image(S,n_right)',
    ]
    for key,item in [('gone',0),('tail',0),('first',1),('later',9)]:
        rows+=dynamic('S','n_left',key+'_left',key,f'PROP_VALUE (DIRECT (PINT {item}))')
    rows+=[
        'ppropertyslot_dead_first = {DECL eps,NAME $ptascii("first"),STATE PROP_UNSET}',
        'ppropertyslot_dead_first <- pobjectprops_first_left.SLOTS',
        'pobjectprops_first_left.SLOTS = [ppropertyslot_gone_left,ppropertyslot_dead_first,ppropertyslot_tail_left,ppropertyslot_first_left,ppropertyslot_later_left]',
        '$property_slot_named([ppropertyslot_tail_left,ppropertyslot_first_left,ppropertyslot_later_left],$ptascii("first"))',
        '$property_slot_at(pobjectprops_first_left.SLOTS,$ptascii("first")) = (ppropertyslot_first_left)',
    ]
    left=[('gone','DIRECT (PINT 0)'),('tail','DIRECT (PINT 0)'),('first','DIRECT (PINT 1)'),('later','DIRECT (PINT 9)')]
    right=[('gone','DIRECT (PINT 0)'),('tail','DIRECT (PINT 0)'),('first','DIRECT (PINT 2)'),('later','DIRECT (PINT 0)')]
    rows+=cache('S','n_left','left',left)+cache('S','n_right','right',right)+[
        '$object_tables_valid(S)',
        '$object_table_sync(S,n_left) = S',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_table_left) = 1',
    ]+raw('S',-1)
    rows+=stage('S_raw','S_mutated','B|-1|M|')
    rows+=value('S_mutated','view','view','PARRAY n_table_left')
    rows+=cache('S_mutated','n_left','left_new',left)+[
        'n_table_left_new =/= n_table_left',
        'S_mutated.ARRAYS[n_table_left_new].ITEMS = S_mutated.ARRAYS[n_table_left].ITEMS',
        '$heap_owners($heap_prune($heap_graph(S_mutated)),HARRAY n_table_left) = 1',
        '$heap_owners($heap_prune($heap_graph(S_mutated)),HARRAY n_table_left_new) = 1',
        '$property_slot_at($object_table_slots_at(S_mutated,n_left),$ptascii("first")) = (ppropertyslot_first_left)',
        '$object_table_sync(S_mutated,n_left) = S_mutated',
        '$object_tables_valid(S_mutated)',
    ]+raw('S_mutated',-1)
    rows+=[
        'S_reverse = $tbp_seek(S_mutated_raw,15000)[.COMPLETION = NORMAL]',
        'S_reverse.TODO = (BINARY_RIGHT SPACESHIP poperand_S_reverse z_S_reverse) :: ptask_S_reverse*',
    ]+operands('S_reverse','n_b','n_a')+pair_raw('S_reverse',1,'n_b','n_a')
    return rows+finish('S_reverse_raw','dynamic-reinsert-later-key-stability')+[
        '$entry_lookup(S_done.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("first")) = (DIRECT (PINT 1))',
        '$entry_lookup(S_done.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("later")) = (DIRECT (PINT 9))',
    ]
