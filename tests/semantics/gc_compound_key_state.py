#!/usr/bin/env python3
"""Source-reached compound free phases and honest ordinary-Key refusals."""
import argparse
import fiber_state_review as review
import gc_compound_key_sources as sources

ROOT = sources.ROOT
STAGE = ('S.TODO = [EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE] '
         '-- if S.DESTRUCTION.OPERATIONS = eps /\\ S.DESTRUCTION.CALLS = eps '
         '-- if S.DESTRUCTION.CLEANUPS = eps /\\ S.DESTRUCTION.RELEASES = eps')
COMMON = [
    '$call_task_valid(S, EXECUTOR_RELEASE pexecutorqueue EXECUTOR_DONE)',
    '$call_descriptors_valid(S)', '$destruction_state_valid(S)',
    '$output_state_valid(S)', '$class_state_valid(S)',
    'S.CURRENT = eps /\\ S.FRAMES = eps /\\ S.ITERATORS = eps',
    'S_global = $global_table_view(S)', 'H = $heap_graph(S)', '$heap_valid(H)',
    'S_endpoint = S[.TODO = eps][.COMPLETION = pexecutorqueue.COMPLETION][.ORIGIN = pexecutorqueue.ORIGIN]',
    '$executor_free_endpoint(S_endpoint)',
    'pexecutorfree_start = {HEAP H, MARKED eps, DETACHED eps, FAILED eps, UNKNOWN false}',
]
FINISH = [
    'S_zero = $drive_steps(S, 0)', 'S_zero.COMPLETION = BUDGET /\\ S_zero.TODO = S.TODO',
    'S_done = $drive_steps(S, 1)', '$drive_steps(S_zero[.COMPLETION = NORMAL], 1) = S_done',
    'S_done.OBJECTS = S.OBJECTS /\\ S_done.ALLOCATIONS = S.ALLOCATIONS',
    'S_done.GC = S.GC', '$heap_valid($heap_graph(S_done))',
]

def binding(name, cell, obj):
    return [f'$lookup(S_global.ENV, $ptascii("{name}")) = ({cell})',
            f'S.STORE[{cell}] = DEFINED (POBJECT {obj})']

def fatal(name):
    return [f'ptbytes_fatal = $ptascii("Couldn\'t execute method {name}::__destruct")',
        'S_done.COMPLETION = REQUESTFATAL ($ptascii("Error")) ptbytes_fatal 0',
        'S_done.EXITSTATUS = 0',
        'S_done.EVENTS = S.EVENTS ++ [STDERR ($ptascii("Fatal error: ") ++ ptbytes_fatal ++ $ptascii(" in Unknown on line 0") ++ [10] ++ $ptascii("Stack trace:") ++ [10] ++ $ptascii("#0 {main}") ++ [10])]',
    ]

def map_case(held):
    checks = [*COMMON, '$executor_allocator_fast(S.REQUEST)',
        *binding('compoundOuterMap33', 'n_outer_cell', 'n_outer'),
        *binding('compoundInnerMap33', 'n_inner_cell', 'n_inner'),
        *binding('compoundOutgoingKey33', 'n_plain_cell', 'n_plain'),
        'S.OBJECTS[n_outer] = WEAKMAP (pweakmapentry_outer)',
        'S.OBJECTS[n_inner] = WEAKMAP (pweakmapentry_inner)',
        'pweakmapentry_outer.KEY = n_inner', 'pweakmapentry_outer.VALUE = POBJECT n_incoming',
        'pweakmapentry_inner.KEY = n_plain', 'pweakmapentry_inner.VALUE = POBJECT n_own',
        'pweakmapentry_outer.ORDER = 1 /\\ pweakmapentry_inner.ORDER = 1',
        'pweakmapentry_outer.BEFORE = eps /\\ pweakmapentry_inner.BEFORE = eps',
        '$heap_owners(H, HOBJECT n_outer) = 1 /\\ $heap_owners(H, HOBJECT n_inner) = 1',
        '$heap_owners(H, HOBJECT n_incoming) = 1',
        '$heap_children(HOBJECT n_inner, H.EDGES) = [HOBJECT n_own]',
        '$heap_children(HOBJECT n_outer, H.EDGES) = [HOBJECT n_incoming]',
        '$(S.DESTRUCTION.HANDLES[n_outer] < S.DESTRUCTION.HANDLES[n_incoming])',
        '$(S.DESTRUCTION.HANDLES[n_incoming] < S.DESTRUCTION.HANDLES[n_own])',
        '$(S.DESTRUCTION.HANDLES[n_own] < S.DESTRUCTION.HANDLES[n_plain])',
        '$(S.DESTRUCTION.HANDLES[n_plain] < S.DESTRUCTION.HANDLES[n_inner])',
        '$weakmap_insert_key(S_endpoint, n_inner)', '~$weakmap_insert_key(S_endpoint, n_own)',
        '~$weakmap_insert_key(S_endpoint, |S.OBJECTS|)',
        'S_missing = S_endpoint[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS, HOBJECT n_inner)]',
        '~$weakmap_insert_key(S_missing, n_inner)',
        '$executor_free_kind(S_endpoint, eps, n_inner) = 1',
        '$executor_free_key_maps(S_endpoint, eps, n_inner) = [n_outer]',
        'pexecutorfree_inner = $executor_free_force(S_endpoint, pexecutorfree_start, n_inner)',
        '~pexecutorfree_inner.UNKNOWN', 'pexecutorfree_inner.MARKED = [HOBJECT n_inner]',
        '$heap_owners(pexecutorfree_inner.HEAP, HOBJECT n_inner) = 2',
        '$heap_children(HOBJECT n_inner, pexecutorfree_inner.HEAP.EDGES) = eps',
        '$executor_free_key_maps(S_endpoint, pexecutorfree_inner.MARKED, n_plain) = eps',
        'S_bad = S_endpoint[.OBJECTS[n_outer] = WEAKMAP (pweakmapentry_outer[.ORDER = 0])]',
        '~$gc_ephemeron_key_order_safe(S_bad, n_inner)',
        '$executor_free_notify(S_bad, pexecutorfree_inner, n_inner) = pexecutorfree_inner',
        'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_start, S.DESTRUCTION.NEXT)',
        'pexecutorfree_done.FAILED = pexecutorfree_inner.FAILED', *FINISH,
    ]
    if held:
        return checks + [*binding('compoundHeldOwn33', 'n_held_cell', 'n_own'),
            '$heap_owners(H, HOBJECT n_own) = 2',
            'pexecutorfree_inner.FAILED = (n_incoming)',
            'pexecutorfree_inner.DETACHED = [(n_outer, n_inner)]',
            '$heap_owners(pexecutorfree_inner.HEAP, HOBJECT n_own) = 1',
            '$heap_owners(pexecutorfree_inner.HEAP, HOBJECT n_incoming) = 0',
            '$heap_children(HOBJECT n_outer, pexecutorfree_inner.HEAP.EDGES) = eps',
            *fatal('GcCompoundMapHeldIncoming33')]
    return checks + [
        '$heap_owners(H, HOBJECT n_own) = 1',
        'pexecutorfree_inner.FAILED = (n_own)', 'pexecutorfree_inner.DETACHED = eps',
        '$heap_owners(pexecutorfree_inner.HEAP, HOBJECT n_own) = 0',
        '$heap_owners(pexecutorfree_inner.HEAP, HOBJECT n_incoming) = 1',
        '$heap_children(HOBJECT n_outer, pexecutorfree_inner.HEAP.EDGES) = [HOBJECT n_incoming]',
        '$executor_free_live_maps(S_endpoint, pexecutorfree_inner.MARKED, eps, n_inner) = [n_outer]',
        *fatal('GcCompoundMapOwn33')]

WR = [*COMMON, '$executor_allocator_fast(S.REQUEST)',
    *binding('compoundWeakFastMap33', 'n_map_cell', 'n_map'),
    *binding('compoundWeakFastTarget33', 'n_target_cell', 'n_target'),
    *binding('compoundWeakFastKey33', 'n_key_cell', 'n_key'),
    'S.OBJECTS[n_key] = WEAKREFERENCE (n_target)',
    'S.OBJECTS[n_map] = WEAKMAP ({KEY n_key, VALUE (PINT 7), BEFORE eps, ORDER 1})',
    '$node_children(S, HOBJECT n_target) = [HOBJECT n_field]',
    '$object_name(S, n_field) = $ptascii("GcCompoundWeakField33")',
    '$heap_owners(H, HOBJECT n_target) = 1 /\\ $heap_owners(H, HOBJECT n_key) = 1',
    '$heap_owners(H, HOBJECT n_field) = 1',
    '$node_children(S, HOBJECT n_key) = eps /\\ $node_children(S, HOBJECT n_map) = eps',
    '$weakmap_insert_key(S_endpoint, n_key)',
    '$executor_free_kind(S_endpoint, eps, n_key) = 1',
    '$executor_free_kind(S_endpoint, eps, n_target) = 1',
    '$(S.DESTRUCTION.HANDLES[n_map] < S.DESTRUCTION.HANDLES[n_field])',
    '$(S.DESTRUCTION.HANDLES[n_field] < S.DESTRUCTION.HANDLES[n_target])',
    '$(S.DESTRUCTION.HANDLES[n_target] < S.DESTRUCTION.HANDLES[n_key])',
    'pexecutorfree_key = $executor_free_force(S_endpoint, pexecutorfree_start, n_key)',
    '~pexecutorfree_key.UNKNOWN /\\ pexecutorfree_key.FAILED = eps',
    'pexecutorfree_key.MARKED = [HOBJECT n_key]',
    'pexecutorfree_key.DETACHED = [(n_map, n_key)]',
    'pexecutorfree_key.HEAP.EDGES = H.EDGES',
    '$heap_owners(pexecutorfree_key.HEAP, HOBJECT n_key) = 2',
    '$heap_owners(pexecutorfree_key.HEAP, HOBJECT n_target) = 1',
    '~$executor_free_weak(S_endpoint, pexecutorfree_key.MARKED, n_target)',
    '$executor_free_kind(S_endpoint, pexecutorfree_key.MARKED, n_target) = 0',
    'pexecutorfree_target = $executor_free_force(S_endpoint, pexecutorfree_key, n_target)',
    'pexecutorfree_target.HEAP = pexecutorfree_key.HEAP',
    '$heap_children(HOBJECT n_target, pexecutorfree_target.HEAP.EDGES) = [HOBJECT n_field]',
    'pexecutorfree_done = $executor_free_walk(S_endpoint, pexecutorfree_start, S.DESTRUCTION.NEXT)',
    '~pexecutorfree_done.UNKNOWN /\\ pexecutorfree_done.FAILED = eps',
    '$heap_owners(pexecutorfree_done.HEAP, HOBJECT n_field) = 1',
    *FINISH, 'S_done = S_endpoint',
]
SELF = [*COMMON, '$executor_allocator_fast(S.REQUEST)',
    *binding('compoundSelfMap33', 'n_map_cell', 'n_map'),
    'S.OBJECTS[n_map] = WEAKMAP ({KEY n_map, VALUE (POBJECT n_value), BEFORE eps, ORDER 1})',
    '$object_name(S, n_value) = $ptascii("GcCompoundSelfValue33")',
    '$heap_owners(H, HOBJECT n_map) = 1 /\\ $heap_owners(H, HOBJECT n_value) = 1',
    '$executor_free_key_maps(S_endpoint, eps, n_map) = [n_map]',
    '$(S.DESTRUCTION.HANDLES[n_map] < S.DESTRUCTION.HANDLES[n_value])',
    'pexecutorfree_value = $executor_free_force(S_endpoint, pexecutorfree_start, n_value)',
    'pexecutorfree_value.HEAP = H',
    'pexecutorfree_map = $executor_free_force(S_endpoint, pexecutorfree_value, n_map)',
    '~pexecutorfree_map.UNKNOWN /\\ pexecutorfree_map.FAILED = eps',
    'pexecutorfree_map.MARKED = [HOBJECT n_map, HOBJECT n_value]',
    'pexecutorfree_map.DETACHED = eps',
    '$executor_free_live_maps(S_endpoint, pexecutorfree_map.MARKED, eps, n_map) = eps',
    '$heap_children(HOBJECT n_map, pexecutorfree_map.HEAP.EDGES) = eps',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_value) = 0',
    '$heap_owners(pexecutorfree_map.HEAP, HOBJECT n_map) = 2',
    *FINISH, 'S_done = S_endpoint',
]
CROSS_BINDINGS = [*COMMON,
    *binding('compoundCrossOuter33', 'n_outer_cell', 'n_outer'),
    *binding('compoundCrossOther33', 'n_other_cell', 'n_other'),
    *binding('compoundCrossInner33', 'n_inner_cell', 'n_inner'),
    *binding('compoundCrossPlain33', 'n_plain_cell', 'n_plain'),
    *binding('compoundCrossSecond33', 'n_second_cell', 'n_second'),
    'S.OBJECTS[n_outer] = WEAKMAP (pweakmapentry_outer)',
    'S.OBJECTS[n_other] = WEAKMAP (pweakmapentry_other)',
    'S.OBJECTS[n_inner] = WEAKMAPENTRIES ([pweakmapentry_plain, pweakmapentry_second])',
    'pweakmapentry_outer.KEY = n_inner', 'pweakmapentry_outer.VALUE = POBJECT n_value',
    'pweakmapentry_other.KEY = n_inner', 'pweakmapentry_other.VALUE = POBJECT n_value',
    'pweakmapentry_outer.ORDER = 2 /\\ pweakmapentry_other.ORDER = 1',
    'pweakmapentry_plain.KEY = n_plain /\\ pweakmapentry_plain.VALUE = POBJECT n_value',
    'pweakmapentry_second.KEY = n_second /\\ pweakmapentry_second.VALUE = POBJECT n_value',
    '$heap_children(HOBJECT n_inner, H.EDGES) = [HOBJECT n_value, HOBJECT n_value]',
    '$heap_owners(H, HOBJECT n_value) = 4',
    '$heap_owners(H, HOBJECT n_inner) = 1',
    '$heap_owners(H, HOBJECT n_outer) = 1 /\\ $heap_owners(H, HOBJECT n_other) = 1',
    '$(S.DESTRUCTION.HANDLES[n_outer] < S.DESTRUCTION.HANDLES[n_other])',
    '$(S.DESTRUCTION.HANDLES[n_second] < S.DESTRUCTION.HANDLES[n_inner])',
    '$executor_free_key_maps(S_endpoint, eps, n_inner) = [n_outer, n_other]',
    '$executor_free_map_order(S_endpoint, n_inner, [n_outer, n_other]) = [n_other, n_outer]',
]
CROSS = [*CROSS_BINDINGS, '$executor_allocator_fast(S.REQUEST)',
    'pexecutorfree_inner = $executor_free_force(S_endpoint, pexecutorfree_start, n_inner)',
    '~pexecutorfree_inner.UNKNOWN /\\ pexecutorfree_inner.FAILED = eps',
    'pexecutorfree_inner.DETACHED = [(n_other, n_inner), (n_outer, n_inner)]',
    '$heap_children(HOBJECT n_inner, pexecutorfree_inner.HEAP.EDGES) = eps',
    '$heap_children(HOBJECT n_outer, pexecutorfree_inner.HEAP.EDGES) = eps',
    '$heap_children(HOBJECT n_other, pexecutorfree_inner.HEAP.EDGES) = eps',
    '$heap_owners(pexecutorfree_inner.HEAP, HOBJECT n_value) = 0',
    '$heap_owners(pexecutorfree_inner.HEAP, HOBJECT n_inner) = 2',
    '$executor_free_live_maps(S_endpoint, pexecutorfree_inner.MARKED, pexecutorfree_inner.DETACHED, n_inner) = eps',
    *FINISH, 'S_done = S_endpoint',
]
SLOW = [*CROSS_BINDINGS, '~$executor_allocator_fast(S.REQUEST)',
    'pexecutorfree_tables = $executor_free_tables(S_endpoint, pexecutorfree_start)',
    '~pexecutorfree_tables.UNKNOWN /\\ pexecutorfree_tables.FAILED = eps',
    'pexecutorfree_tables.DETACHED = [(n_inner, n_second), (n_inner, n_plain), (n_other, n_inner), (n_outer, n_inner)]',
    '$heap_children(HOBJECT n_inner, pexecutorfree_tables.HEAP.EDGES) = eps',
    '$heap_children(HOBJECT n_outer, pexecutorfree_tables.HEAP.EDGES) = eps',
    '$heap_children(HOBJECT n_other, pexecutorfree_tables.HEAP.EDGES) = eps',
    '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_value) = 0',
    '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_inner) = 0',
    '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_outer) = 0',
    '$heap_owners(pexecutorfree_tables.HEAP, HOBJECT n_other) = 0',
    *FINISH, 'S_done = S_endpoint',
]
ORDINARY_STAGE = ('S.TODO = (DESTRUCTOR_RELEASE pdestructionrelease) :: ptask_tail* '
    '-- if pdestructionrelease.JOBS = (DESTRUCTION_VALUE (HOBJECT n_key)) :: pdestructionjob* '
    '-- if $weakref_object(S.OBJECTS[n_key]) \\/ $weakmap_object(S.OBJECTS[n_key]) '
    '-- if $weakmap_key_waiting(S, n_key) '
    '-- if S_unheld = $destructor_release_replace(S, pdestructionrelease[.JOBS = pdestructionjob*]) '
    '-- if $heap_owners($heap_graph(S_unheld), HOBJECT n_key) = 0')
ORDINARY = [
    '$destructor_release_valid(S, pdestructionrelease)', '$destruction_state_valid(S)',
    '$call_descriptors_valid(S)', 'S_global = $global_table_view(S)',
    *binding('map', 'n_map_cell', 'n_map'),
    'S.OBJECTS[n_map] = WEAKMAP (pweakmapentry_outer)',
    'pweakmapentry_outer.KEY = n_key', 'pweakmapentry_outer.VALUE = POBJECT n_value',
    'H = $heap_graph(S)', '$heap_valid(H)',
    '$heap_owners(H, HOBJECT n_value) = 1', '$heap_owners(H, HOBJECT n_key) = 1',
    '(HOBJECT n_key) <- S.ALLOCATIONS',
    'S_block = $destructor_free(S_unheld, HOBJECT n_key, pdestructionrelease[.JOBS = pdestructionjob*])',
    'S_block.COMPLETION = UNSUPPORTED "ordinary internal weak-key notification"',
    'S_block.OBJECTS = S.OBJECTS /\\ S_block.ALLOCATIONS = S.ALLOCATIONS',
    'S_block.EVENTS = S.EVENTS',
    '$heap_children(HOBJECT n_map, $heap_graph(S_block).EDGES) = [HOBJECT n_value]',
    '$heap_owners($heap_graph(S_block), HOBJECT n_value) = 1',
    '$heap_owners($heap_graph(S_block), HOBJECT n_key) = 1',
    'S_zero = $drive_steps(S, 0)', 'S_zero.COMPLETION = BUDGET',
    'PhpStep: S ~> S_done', 'S_done = S_block',
    'S_resume = S_zero[.COMPLETION = NORMAL]',
    'PhpStep: S_resume ~> S_resumed', 'S_resumed = S_done',
]
review.CASES = {name: {'source': sources.family.CASES[source].decode(), 'stage': STAGE, 'checks': checks}
    for name, source, checks in [
        ('own-values-before-incoming-fatal', 'map-key-own-before-incoming', map_case(False)),
        ('held-own-reaches-incoming-fatal', 'map-key-held-own', map_case(True)),
        ('weak-key-unregister-shields-target-field', 'weak-key-field-shield', WR),
        ('self-key-unregisters-once', 'map-key-self', SELF)]}
for name in ['ordinary-weak-key', 'ordinary-map-key', 'ordinary-nonempty-map-key']:
    checks = [*ORDINARY]
    if name == 'ordinary-weak-key':
        checks += ['S.OBJECTS[n_key] = WEAKREFERENCE (n_target)', '$node_children(S, HOBJECT n_key) = eps']
    elif name == 'ordinary-map-key':
        checks = [check.replace('$ptascii("map")', '$ptascii("outer")') for check in checks]
        checks += ['S.OBJECTS[n_key] = WEAKMAP eps', '$node_children(S, HOBJECT n_key) = eps']
    else:
        checks += ['S.OBJECTS[n_key] = WEAKMAPENTRIES ([pweakmapentry_first, pweakmapentry_second])',
                   'pweakmapentry_first.VALUE = POBJECT n_leaf', 'pweakmapentry_second.VALUE = POBJECT n_leaf',
                   '$node_children(S, HOBJECT n_key) = [HOBJECT n_leaf, HOBJECT n_leaf]',
                   '$heap_children(HOBJECT n_key, $heap_graph(S_block).EDGES) = [HOBJECT n_leaf, HOBJECT n_leaf]']
    review.CASES[name] = {'source': sources.family.CASES[name].decode(), 'stage': ORDINARY_STAGE, 'checks': checks}
review.CASES['cross-shared-registration-order'] = {
    'source': sources.family.CASES['map-key-cross-shared'].decode(), 'stage': STAGE, 'checks': CROSS}
review.CASES['cross-shared-nonfast-tables'] = {
    'source': sources.family.CASES['map-key-cross-shared'].decode(), 'stage': STAGE,
    'request_env': [(b'LC_ALL', b'C'), (b'TZ', b'UTC'), (b'FIRST', b'one'), (b'USE_ZEND_ALLOC', b'0')],
    'checks': SLOW}
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', default=[])
    args = parser.parse_args()
    raise SystemExit(0 if review.run(args.case or None, process_seconds=240) else 1)
