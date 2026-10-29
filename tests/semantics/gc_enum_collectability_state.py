#!/usr/bin/env python3
"""Source-reached enum case and ordinary GC-root admission."""
import argparse

import gc_enum_collectability_sources as sources
import shutdown_state_review as runner


SOURCE = sources.family.CASES['case-and-ordinary-cycle'].decode()
COMMON = [
    '$config_invoke_valid(S, pconfigcall)',
    'S.OBJECTS[n_weak] = WEAKREFERENCE (n_case)',
    'S.OBJECTS[n_case] = ENUMCASE porigin_case',
    '$enum_case_object(S, n_case) = (pclassconstantdesc)',
    '$default_cache_at(S.CLASSCONSTANTCACHE, porigin_case) = (pdefaultcache_case)',
    'pdefaultcache_case.VALUE = POBJECT n_case',
    '(HOBJECT n_case) <- $class_constant_roots(S.CLASSCONSTANTCACHE)',
    '$heap_owners($heap_graph(S), HOBJECT n_case) = 1',
    '$weakref_get(S, n_weak) = POBJECT n_case',
    '$gc_object_possible_root(S.OBJECTS[n_case]) = false',
    '$gc_possible_root(S, HOBJECT n_case) = false',
    '~((HOBJECT n_case) <- $gc_physical_nodes(S.GC.BUFFER))',
    '$gc_buffer_valid(S, S.GC)',
]
CASES = {
    'case-release-before-get': {
        'source': SOURCE,
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
        '-- if pconfigcall.KIND = INTRINSIC_WEAKREF_GET '
        '-- if pconfigcall.LINE = 8 '
        '-- if $lookup(S.ENV, $ptascii("weak")) = (n_weak_cell) '
        '-- if S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        'checks': [*COMMON, 'S.GC.BUFFER = eps', 'S.GC.FREE = eps'],
        'timeout': 180,
    },
    'ordinary-first-slots': {
        'source': SOURCE,
        'stage': 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
        '-- if pconfigcall.KIND = INTRINSIC_GC_COLLECT '
        '-- if S.GC.ACTIVE = eps '
        '-- if $lookup(S.ENV, $ptascii("weak")) = (n_weak_cell) '
        '-- if S.STORE[n_weak_cell] = DEFINED (POBJECT n_weak)',
        'checks': [
            *COMMON,
            'S.GC.BUFFER = [GC_ROOT pnode_first, GC_ROOT pnode_second]',
            'pnode_first = HOBJECT n_weak',
            'pnode_second = HOBJECT n_cycle',
            'S.OBJECTS[n_cycle] = STDINSTANCE',
            '$gc_possible_root(S, HOBJECT n_cycle)',
            '$object_table_at(S.OBJECTTABLES, n_cycle) = eps',
            '(HOBJECT n_cycle) <- $node_children(S, HOBJECT n_cycle)',
            'S_forged = S[.GC.BUFFER = [GC_ROOT (HOBJECT n_case)]][.GC.FREE = eps]',
            '~$gc_buffer_valid(S_forged, S_forged.GC)',
            'S_bad_case = S[.OBJECTS[n_case] = ENUMCASE pclassconstantdesc.OWNER]',
            '$enum_case_object(S_bad_case, n_case) = eps',
            '$gc_possible_root(S_bad_case, HOBJECT n_case) = false',
            '~$gc_slots_valid(S_bad_case, [GC_ROOT (HOBJECT n_case)], eps, 0)',
        ], 'timeout': 180,
    },
}


RECORDED = runner.recorded


def strict_recorded(command, directory, stem, environment, cap):
    return RECORDED([command[0], '--sl', *command[1:]], directory, stem, environment, cap)


runner.CASES = CASES
runner.recorded = strict_recorded
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    raise SystemExit(0 if runner.run(args.case) else 1)
