"""Reached physical holes, honest cached INDIRECTs, clone retargets and refusal."""
import base64
import json
import re

from throwable_empty_clone_protocol import PREFIX
from throwable_interface_protocol import front
from throwable_previous_graph_protocol import raw, trace
from throwable_trace_recursion_protocol import error_rows

EXPECTED = {
    'initial-hole-inline-cache-clone':
        'B|1:1|P|0:0:1|L|-1:1|T|-1:1|U|0:0|C|0|D|-1:1|I|1:-1|V|0:1:0|',
    'private-hole-alias-cycle-owners':
        'B|-1:1|I|1:1|U|-1|C|99:3:1|S|1:-1|X|F|hold|Error:Nesting level too deep - recursive dependency?:1:1:1|R|0:1|H|1|D|1|A|4:99|K|1:1|',
    'initial-hole-stringable-control': 'B|',
}

# Explicitly derived queries: a supplied recursion guard and a mutation of the
# reached INITIAL slot to declared UNSET, queried without invoking a callback.
DERIVED = {
    '$trace_visit_object_effect(S,n_left,n_right,[HOBJECT n_left],z_S) = (S,ORDERRECURSIVE)':
        'A supplied active-object guard on the nonempty inline layout.',
    'S_unset = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_left,[ppropertyslot_hole_left[.STATE = PROP_UNSET],ppropertyslot_value_left])]':
        'Project only the reached public INITIAL slot to declared UNSET.',
    '~$aggregate_decl_has_initial($object_table_slots_at(S_unset,n_left))':
        'The projected left image contains no INITIAL slot.',
    '$aggregate_std_cast_order(S_unset,n_left,ORDERSTRING paggregatecallback) = ORDERSTRING paggregatecallback':
        'Pure continuation-permission query preserves prior public UNSET policy.',
}


def value(state, name, label, item):
    return [f'$lookup({state}.ENV,$ptascii({json.dumps(name)})) = (n_cv_{label})',
            f'{state}.STORE[n_cv_{label}] = DEFINED ({item})']


def bind(state):
    return [f'{state}.TODO = (BINARY_RIGHT SPACESHIP poperand_{state} z_{state}) :: ptask_{state}*']


def mark(state, out, output):
    return [f'{out} = $tec_seek_output({state},15000,$ptascii({json.dumps(output)}))',
            f'$tbp_output({out}.EVENTS) = $ptascii({json.dumps(output)})']


def stage(state, out, output):
    return mark(state, out+'_prefix', output) + [
        f'{out} = $tbp_seek({out}_prefix,15000)[.COMPLETION = NORMAL]',
        f'$tbp_stage({out})'] + bind(out)


def slot(state, node, label, desc, propstate):
    return [f'$objectprops_record_at({state}.OBJECTPROPS,{node}) = (pobjectprops_{label})',
            f'$property_slot_at(pobjectprops_{label}.SLOTS,{desc}.KEY) = (ppropertyslot_{label})',
            f'ppropertyslot_{label}.DECL = ({desc}.ORIGIN)',
            f'ppropertyslot_{label}.STATE = {propstate}']


def table(state, node, label, descriptors):
    entries = ','.join(f'ENTRY (KSTRING {desc}.KEY) (INDIRECT {node} {desc}.KEY)' for desc in descriptors)
    return [f'$object_table_at({state}.OBJECTTABLES,{node}) = (n_table_{label})',
            f'{state}.ARRAYS[n_table_{label}].ITEMS = [{entries}]',
            f'$aggregate_hash_image({state},{node},n_table_{label})',
            f'$trace_visit_object_image({state},{node})',
            f'$heap_owners($heap_prune($heap_graph({state})),HARRAY n_table_{label}) = 1']


def finish(state, name):
    return [f'S_done = $drive_steps({state},15000)',
            r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps',
            '$tbp_output(S_done.EVENTS) = $ptascii('+json.dumps(EXPECTED[name])+')']


def pair_raw(state, result, left='n_a', right='n_b', effect=None):
    return [row.replace('POBJECT n_a','POBJECT '+left).replace('POBJECT n_b','POBJECT '+right)
            for row in raw(state,result,effect)]


def common():
    return [
        'S.OBJECTS[n_left] = INSTANCE porigin_packet',
        'S.OBJECTS[n_right] = INSTANCE porigin_packet',
        '$class_at(S.CLASSES,porigin_packet) = (pclassdesc_packet)',
        '$trace_visit_parent_path(S,pclassdesc_packet,eps)',
        '$trace_visit_interfaces(S,pclassdesc_packet)',
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


def checks(program, path, name):
    if name == 'initial-hole-stringable-control':
        return callback_checks(program,path)
    rows = front(program,path)
    rows += trace('S','n_a','a','POBJECT n_left')[:4]
    rows += trace('S','n_b','b','POBJECT n_right')[:4]
    rows += common()
    if name == 'initial-hole-inline-cache-clone':
        descs = ['ppropertydesc_hole','ppropertydesc_tail']
        rows += [
            '$property_layout(S,porigin_packet,|S.CLASSES|) = [ppropertydesc_hole,ppropertydesc_tail]',
            'ppropertydesc_hole.KEY = $ptascii("hole")',
            'ppropertydesc_hole.VISIBILITY = PROPERTY_PUBLIC',
            'ppropertydesc_hole.DEFAULT = PROP_UNINITIALIZED',
            'ppropertydesc_tail.KEY = $ptascii("tail")',
        ]
        rows += slot('S','n_left','hole_left','ppropertydesc_hole','PROP_INITIAL')
        rows += slot('S','n_right','hole_right','ppropertydesc_hole','PROP_VALUE (DIRECT (PINT 0))')
        for node in ('left','right'):
            rows += slot('S','n_'+node,'tail_'+node,'ppropertydesc_tail','PROP_VALUE (DIRECT (PINT 0))')
        rows += [
            '~$aggregate_decl_initialized($object_table_slots_at(S,n_left))',
            '$trace_visit_slots_admitted($object_table_slots_at(S,n_left))',
            '$trace_visit_object_effect(S,n_left,n_right,eps,z_S) = (S,ORDER 1)',
            '$trace_visit_object_effect(S,n_right,n_left,eps,z_S) = (S,ORDER 1)',
        ] + list(DERIVED)[:1] + raw('S',1)
        rows += stage('S_raw','S_cast','B|1:1|P|0:0:')
        rows += value('S_cast','view','view','PARRAY n_view')
        rows += value('S_cast','snapshot','snapshot','PARRAY n_snapshot') + [
            'n_view =/= n_snapshot',
            '$entry_lookup(S_cast.ARRAYS[n_snapshot].ITEMS,KSTRING ppropertydesc_hole.KEY) = eps',
            '$entry_lookup(S_cast.ARRAYS[n_snapshot].ITEMS,KSTRING ppropertydesc_tail.KEY) = (DIRECT (PINT 0))',
            '$entry_lookup(S_cast.ARRAYS[n_snapshot].ITEMS,KSTRING $ptascii("extra")) = eps',
            '$entry_lookup(S_cast.ARRAYS[n_view].ITEMS,KSTRING $ptascii("extra")) = (DIRECT (PINT 9))',
            '$object_table_at(S_cast.OBJECTTABLES,n_left) = eps',
            '$object_table_at(S_cast.OBJECTTABLES,n_right) = eps',
        ]
        rows += stage('S_cast','S_one','B|1:1|P|0:0:1|L|')
        rows += table('S_one','n_left','left',descs) + [
            '$object_table_at(S_one.OBJECTTABLES,n_right) = eps',
            '$object_table_item(S_one,INDIRECT n_left ppropertydesc_hole.KEY) = UNINITIALIZED',
            '$value_order_effect(S_one,POBJECT n_a,POBJECT n_b,eps,z_S_one) = (S_effect,ORDER $(-1))',
            'n_table_right = |S_one.ARRAYS|',
            'S_effect.ALLOCATIONS = S_one.ALLOCATIONS ++ [HARRAY n_table_right]',
            '$object_table_at(S_effect.OBJECTTABLES,n_right) = (n_table_right)',
            '|S_effect.ARRAYS[n_table_left].ITEMS| = 2',
            '|S_effect.ARRAYS[n_table_right].ITEMS| = 2',
            '$object_table_item(S_effect,INDIRECT n_right ppropertydesc_hole.KEY) = DIRECT (PINT 0)',
            '$object_tables_valid(S_effect)',
        ] + raw('S_one',-1,'S_effect')
        rows += stage('S_one_raw','S_both','B|1:1|P|0:0:1|L|-1:1|T|')
        for node in ('left','right'):
            rows += table('S_both','n_'+node,node,descs)
        rows += [
            '$trace_visit_object_effect(S_both,n_left,n_right,eps,z_S_both) = (S_both,ORDER $(-1))',
            '$trace_visit_object_effect(S_both,n_right,n_left,eps,z_S_both) = (S_both,ORDER 1)',
        ]
        rows += stage('S_both','S_unset','B|1:1|P|0:0:1|L|-1:1|T|-1:1|U|')
        rows += slot('S_unset','n_right','hole_unset','ppropertydesc_hole','PROP_UNSET') + [
            '$object_table_item(S_unset,INDIRECT n_left ppropertydesc_hole.KEY) = UNINITIALIZED',
            '$object_table_item(S_unset,INDIRECT n_right ppropertydesc_hole.KEY) = UNINITIALIZED',
            '$trace_visit_object_effect(S_unset,n_left,n_right,eps,z_S_unset) = (S_unset,ORDER 0)',
        ]
        rows += stage('S_unset','S_clone','B|1:1|P|0:0:1|L|-1:1|T|-1:1|U|0:0|C|')
        rows += value('S_clone','c','c','POBJECT n_c') + value('S_clone','d','d','POBJECT n_d')
        rows += value('S_clone','copy','copy','POBJECT n_copy')
        rows += trace('S_clone','n_c','c','POBJECT n_left')[:4]
        rows += trace('S_clone','n_d','d','POBJECT n_copy')[:4]
        rows += slot('S_clone','n_copy','hole_copy','ppropertydesc_hole','PROP_INITIAL')
        rows += table('S_clone','n_copy','copy',descs) + [
            'n_copy =/= n_left',
            'S_clone.OBJECTS[n_copy] = INSTANCE porigin_packet',
            'n_table_copy =/= n_table_left',
            'n_table_copy =/= n_table_right',
            '$object_table_item(S_clone,INDIRECT n_copy ppropertydesc_hole.KEY) = UNINITIALIZED',
            '$object_table_item(S_clone,INDIRECT n_copy ppropertydesc_tail.KEY) = DIRECT (PINT 0)',
            '$object_tables_valid(S_clone)',
            '$value_order_effect(S_clone,POBJECT n_c,POBJECT n_d,eps,z_S_clone) = (S_clone,ORDER 0)',
        ]
        rows += stage('S_clone','S_defined','B|1:1|P|0:0:1|L|-1:1|T|-1:1|U|0:0|C|0|D|')
        rows += slot('S_defined','n_left','hole_original','ppropertydesc_hole','PROP_INITIAL')
        rows += slot('S_defined','n_copy','hole_defined','ppropertydesc_hole','PROP_VALUE (DIRECT (PINT 7))')
        rows += pair_raw('S_defined',-1,'n_c','n_d')
        return rows + finish('S_defined_raw',name) + [
            '$entry_lookup(S_done.ARRAYS[n_snapshot].ITEMS,KSTRING ppropertydesc_hole.KEY) = eps',
            '$entry_lookup(S_done.ARRAYS[n_snapshot].ITEMS,KSTRING ppropertydesc_tail.KEY) = (DIRECT (PINT 0))',
        ]
    assert name == 'private-hole-alias-cycle-owners'
    descs = ['ppropertydesc_hole','ppropertydesc_payload']
    rows += [
        '$property_layout(S,porigin_packet,|S.CLASSES|) = [ppropertydesc_hole,ppropertydesc_payload]',
        'ppropertydesc_hole.KEY = [0] ++ $ptascii("Packet160") ++ [0] ++ $ptascii("hole")',
        'ppropertydesc_hole.VISIBILITY = PROPERTY_PRIVATE',
        'ppropertydesc_hole.DEFAULT = PROP_UNINITIALIZED',
        'ppropertydesc_payload.KEY = [0,42,0] ++ $ptascii("payload")',
        'ppropertydesc_payload.VISIBILITY = PROPERTY_PROTECTED',
        'ppropertydesc_payload.TYPE = eps',
    ]
    for node in ('left','right'):
        rows += slot('S','n_'+node,'hole_'+node,'ppropertydesc_hole','PROP_INITIAL')
    rows += slot('S','n_left','payload_left','ppropertydesc_payload','PROP_VALUE (ALIAS n_live)')
    rows += slot('S','n_right','payload_right','ppropertydesc_payload','PROP_VALUE (DIRECT (PARRAY n_right_data))')
    rows += [
        '$lookup(S.ENV,$ptascii("live")) = (n_live)',
        'S.STORE[n_live] = DEFINED (PARRAY n_initial)',
        '$entry_lookup(S.ARRAYS[n_initial].ITEMS,KINT 0) = (DIRECT (PINT 1))',
        '$entry_lookup(S.ARRAYS[n_right_data].ITEMS,KINT 0) = (DIRECT (PINT 2))',
    ] + raw('S',-1)
    rows += stage('S_raw','S_init','B|-1:1|I|')
    rows += slot('S_init','n_left','hole_init','ppropertydesc_hole','PROP_VALUE (DIRECT (PINT 1))') + [
        '$trace_visit_object_effect(S_init,n_left,n_right,eps,z_S_init) = (S_init,ORDER 1)',
        '$trace_visit_object_effect(S_init,n_right,n_left,eps,z_S_init) = (S_init,ORDER 1)',
    ]
    rows += stage('S_init','S_clear','B|-1:1|I|1:1|U|')
    rows += slot('S_clear','n_left','hole_clear','ppropertydesc_hole','PROP_UNSET') + [
        '$trace_visit_object_effect(S_clear,n_left,n_right,eps,z_S_clear) = (S_clear,ORDER $(-1))',
    ]
    rows += stage('S_clear','S_cached','B|-1:1|I|1:1|U|-1|C|99:3:')
    for node in ('left','right'):
        rows += table('S_cached','n_'+node,node,descs)
    rows += value('S_cached','view','view','PARRAY n_view')
    rows += value('S_cached','snapshot','snapshot','PARRAY n_snapshot') + [
        '$object_table_item(S_cached,INDIRECT n_left ppropertydesc_hole.KEY) = UNINITIALIZED',
        '$object_table_item(S_cached,INDIRECT n_right ppropertydesc_hole.KEY) = UNINITIALIZED',
        '$object_table_item(S_cached,INDIRECT n_left ppropertydesc_payload.KEY) = ALIAS n_live',
        '$entry_lookup(S_cached.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_hole.KEY) = eps',
        '$entry_lookup(S_cached.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_payload.KEY) = (ALIAS n_live)',
        '$entry_lookup(S_cached.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
        'S_cached.STORE[n_live] = DEFINED (PARRAY n_three)',
        '$entry_lookup(S_cached.ARRAYS[n_three].ITEMS,KINT 0) = (DIRECT (PINT 3))',
        '$($heap_owners($heap_prune($heap_graph(S_cached)),HCELL n_live) >= 3)',
    ] + raw('S_cached',1)
    rows += stage('S_cached_raw','S_skip','B|-1:1|I|1:1|U|-1|C|99:3:1|S|')
    rows += [
        'S_skip.STORE[n_live] = DEFINED (PARRAY n_cycle_left)',
        '$entry_lookup(S_skip.ARRAYS[n_cycle_left].ITEMS,KINT 0) = (DIRECT (POBJECT n_left))',
        '$object_table_item(S_skip,INDIRECT n_right ppropertydesc_payload.KEY) = DIRECT (PARRAY n_cycle_right)',
        '$entry_lookup(S_skip.ARRAYS[n_cycle_right].ITEMS,KINT 0) = (DIRECT (POBJECT n_right))',
        '$object_table_item(S_skip,INDIRECT n_left ppropertydesc_hole.KEY) = DIRECT (PINT 1)',
        '$trace_visit_object_effect(S_skip,n_left,n_right,eps,z_S_skip) = (S_skip,ORDER 1)',
        '$trace_visit_object_effect(S_skip,n_right,n_left,eps,z_S_skip) = (S_skip,ORDER $(-1))',
    ]
    rows += stage('S_skip','S_cycle','B|-1:1|I|1:1|U|-1|C|99:3:1|S|1:-1|X|') + [
        '$object_table_item(S_cycle,INDIRECT n_left ppropertydesc_hole.KEY) = UNINITIALIZED',
        '$object_table_item(S_cycle,INDIRECT n_right ppropertydesc_hole.KEY) = UNINITIALIZED',
        '$value_order_effect(S_cycle,POBJECT n_a,POBJECT n_b,eps,z_S_cycle) = (S_cycle,ORDERRECURSIVE)',
        'S_cycle_effect = S_cycle',
        'pbin = SPACESHIP',
    ]
    rows += [re.sub(r'\bS\b','S_cycle',re.sub(r'\bS_','S_cycle_',row)) for row in error_rows()]
    rows += ['S_cycle_error.ARRAYS[n_error_trace].ITEMS = eps']
    recovery = EXPECTED[name].split('R|')[0]+'R|'
    rows += stage('S_cycle_one[.COMPLETION = NORMAL]','S_identity',recovery)
    rows += [
        '$object_table_item(S_identity,INDIRECT n_right ppropertydesc_payload.KEY) = DIRECT (PARRAY n_identity_array)',
        '$entry_lookup(S_identity.ARRAYS[n_identity_array].ITEMS,KINT 0) = (DIRECT (POBJECT n_left))',
        '$trace_visit_object_effect(S_identity,n_left,n_left,eps,z_S_identity) = (S_identity,ORDER 0)',
    ] + raw('S_identity',0)
    hold = EXPECTED[name].split('H|')[0]+'H|'
    rows += mark('S_identity_raw','S_hold',hold)
    rows += value('S_hold','left','left_hold','PNULL') + value('S_hold','a','a_hold','PNULL') + [
        '(HOBJECT n_left) <- S_hold.ALLOCATIONS',
        '$heap_owners($heap_prune($heap_graph(S_hold)),HOBJECT n_left) = 1',
    ]
    rows += mark('S_hold','S_drop',hold+'1|D|') + [
        '~((HOBJECT n_left) <- S_drop.ALLOCATIONS)',
        '$object_table_at(S_drop.OBJECTTABLES,n_left) = eps',
        '$objectprops_record_at(S_drop.OBJECTPROPS,n_left) = eps',
        '(HCELL n_live) <- S_drop.ALLOCATIONS',
        '$entry_lookup(S_drop.ARRAYS[n_view].ITEMS,KSTRING ppropertydesc_payload.KEY) = (ALIAS n_live)',
    ]
    rows += stage('S_drop','S_foreign',EXPECTED[name].split('K|')[0]+'K|')
    rows += value('S_foreign','c','c','POBJECT n_c') + value('S_foreign','d','d','POBJECT n_d') + [
        '$value_order_effect(S_foreign,POBJECT n_c,POBJECT n_d,eps,z_S_foreign) = (S_foreign,ORDER 1)',
        '$value_order_effect(S_foreign,POBJECT n_d,POBJECT n_c,eps,z_S_foreign) = (S_foreign,ORDER 1)',
    ]
    return rows + finish('S_foreign',name) + [
        'S_done.STORE[n_live] = DEFINED (PARRAY n_final)',
        '$entry_lookup(S_done.ARRAYS[n_final].ITEMS,KINT 0) = (DIRECT (PINT 4))',
        '$entry_lookup(S_done.ARRAYS[n_snapshot].ITEMS,KINT 0) = (DIRECT (PINT 99))',
    ]


def callback_checks(program,path):
    encoded = json.dumps(base64.b64encode(str(path).encode()).decode())
    rows = [
        'S_initial = $php_run('+program+',0,'+encoded+')',
        'S_initial.COMPLETION = BUDGET',
        'S_found = $tbp_seek(S_initial[.COMPLETION = NORMAL],6000)',
        '$tbp_stage(S_found)',
        'S = S_found[.COMPLETION = NORMAL]',
    ] + bind('S')
    rows += value('S','left','left','POBJECT n_left') + value('S','right','right','POBJECT n_right') + [
        '$string_compare_values(S,poperand_S,S.RESULT,z_S) = ((S_read,POBJECT n_left,POBJECT n_right))',
        'S.OBJECTS[n_left] = INSTANCE porigin_packet',
        'S.OBJECTS[n_right] = INSTANCE porigin_packet',
        '$property_layout(S,porigin_packet,|S.CLASSES|) = [ppropertydesc_hole,ppropertydesc_value]',
        'ppropertydesc_hole.DEFAULT = PROP_UNINITIALIZED',
        '$aggregate_decl_public([ppropertydesc_hole,ppropertydesc_value])',
    ]
    for node in ('left','right'):
        rows += slot('S','n_'+node,'hole_'+node,'ppropertydesc_hole','PROP_INITIAL')
        rows += table('S','n_'+node,node,['ppropertydesc_hole','ppropertydesc_value'])
        rows += [f'$object_table_item(S,INDIRECT n_{node} ppropertydesc_hole.KEY) = UNINITIALIZED']
    rows += slot('S','n_left','value_left','ppropertydesc_value','PROP_VALUE (DIRECT (POBJECT n_value))')
    rows += slot('S','n_right','value_right','ppropertydesc_value','PROP_VALUE (DIRECT (PSTRING ($ptascii("x"))))') + [
        '$aggregate_std_pair(S,n_left,n_right)',
        '~$aggregate_decl_pair(S,n_left,n_right)',
        '~$aggregate_backed_hook_rows(S,n_left,$object_table_slots_at(S,n_left))',
        '$aggregate_decl_has_initial($object_table_slots_at(S,n_left))',
        '$value_order_effect(S,POBJECT n_value,PSTRING ($ptascii("x")),eps,z_S) = (S,ORDERSTRING paggregatecallback)',
        '$aggregate_std_cast_order(S,n_left,ORDERSTRING paggregatecallback) = ORDERUNSUPPORTED "materialized-property Stringable comparison continuation"',
        '$value_order_effect(S,POBJECT n_left,POBJECT n_right,eps,z_S) = (S,ORDERUNSUPPORTED "materialized-property Stringable comparison continuation")',
    ] + list(DERIVED)[1:] + [
        'PhpStep: S ~> S_raw',
        'S_raw.COMPLETION = UNSUPPORTED "materialized-property Stringable comparison continuation"',
        'S_raw.TODO = ptask_S*',
        r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.OBJECTPROPS = S.OBJECTPROPS',
        r'S_raw.ARRAYS = S.ARRAYS /\ S_raw.OBJECTTABLES = S.OBJECTTABLES',
        r'S_raw.STORE = S.STORE /\ S_raw.ALLOCATIONS = S.ALLOCATIONS',
        'S_raw.EVENTS = S.EVENTS',
        '$tbp_output(S_raw.EVENTS) = $ptascii("B|")',
    ]
    return rows
