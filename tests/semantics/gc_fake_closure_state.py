#!/usr/bin/env python3
"""Check source-reached fake Closure GC birth flags and physical root slots."""
import argparse

import gc_fake_closure_collectability_sources as sources
import shutdown_state_review as runner


def bind(name, ident):
    cell = ident + '_cell'
    return [
        f'$lookup(S.ENV, $ptascii("{name}")) = (n_{cell})',
        f'S.STORE[n_{cell}] = DEFINED (POBJECT n_{ident})',
    ]


def flagged(ident):
    return [
        f'n_{ident} <- S.GC.FAKE_NOCOLLECT',
        f'$gc_fake_flag_valid(S, n_{ident})',
        f'$gc_possible_root(S, HOBJECT n_{ident}) = false',
        f'~((HOBJECT n_{ident}) <- $gc_physical_nodes(S.GC.BUFFER))',
    ]


def collectable(ident):
    return [
        f'~(n_{ident} <- S.GC.FAKE_NOCOLLECT)',
        f'$gc_possible_root(S, HOBJECT n_{ident})',
        f'(HOBJECT n_{ident}) <- $gc_physical_nodes(S.GC.BUFFER)',
    ]


STAGE = 'S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask_tail* '
STAGE += '-- if pconfigcall.KIND = INTRINSIC_GC_ENABLED '
STAGE += '-- if $config_invoke_valid(S, pconfigcall)'
SOURCE = sources.family.CASES
CASES = {
    'named-intrinsic-factory-clone-bind': {
        'source': SOURCE['fake-closure-named-reached'].decode(),
        'stage': STAGE,
        'checks': [
            *bind('named', 'named'), *bind('namedFrom', 'named_from'),
            *bind('intrinsic', 'intrinsic'), *bind('intrinsicFrom', 'intrinsic_from'),
            *bind('factory', 'factory'), *bind('clone', 'clone'),
            *bind('boundCopy', 'bind'), *bind('real', 'real'),
            '$lookup(S.ENV, $ptascii("identity")) = (n_identity_cell)',
            'S.STORE[n_identity_cell] = DEFINED (POBJECT n_named)',
            *flagged('named'), *flagged('named_from'),
            *flagged('intrinsic'), *flagged('intrinsic_from'), *flagged('factory'),
            *collectable('clone'), *collectable('bind'), *collectable('real'),
            'S_bad_real = S[.GC.FAKE_NOCOLLECT = S.GC.FAKE_NOCOLLECT ++ [n_real]]',
            '~$gc_state_valid(S_bad_real)',
            '$gc_buffer_valid(S, S.GC)', '$gc_state_valid(S)',
        ], 'timeout': 240,
    },
    'method-array-string-constant-from': {
        'source': SOURCE['fake-closure-method-reached'].decode(),
        'stage': STAGE,
        'checks': [
            *bind('method', 'method'), *bind('array', 'array'),
            *bind('string', 'string'), *bind('constant', 'constant'),
            *bind('from', 'from'), *bind('bound', 'bound'),
            *flagged('method'), *flagged('array'), *flagged('string'),
            *flagged('constant'), *flagged('from'), *collectable('bound'),
            'S_bad_bound = S[.GC.FAKE_NOCOLLECT = S.GC.FAKE_NOCOLLECT ++ [n_bound]]',
            '~$gc_state_valid(S_bad_bound)',
            '$gc_buffer_valid(S, S.GC)', '$gc_state_valid(S)',
        ], 'timeout': 240,
    },
    'fiber-enum-static-vs-bound': {
        'source': SOURCE['fake-closure-fiber-reached'].decode(),
        'stage': STAGE,
        'checks': [
            *bind('enum', 'enum'), *bind('static', 'static'),
            *bind('objectStatic', 'object_static'), *bind('arrayStatic', 'array_static'),
            *bind('fromStatic', 'from_static'), *bind('bound', 'bound'),
            *bind('clone', 'clone'), *bind('fiber', 'fiber'), *bind('weak', 'weak'),
            *flagged('enum'), *flagged('static'), *flagged('object_static'),
            *flagged('array_static'), *flagged('from_static'),
            *collectable('bound'), *collectable('clone'),
            '$node_children(S, HOBJECT n_object_static) = eps',
            '$node_children(S, HOBJECT n_array_static) = eps',
            '$node_children(S, HOBJECT n_from_static) = eps',
            '$node_children(S, HOBJECT n_bound) = [HOBJECT n_fiber]',
            'S.OBJECTS[n_weak] = WEAKREFERENCE (n_fiber)',
            '$weakref_get(S, n_weak) = POBJECT n_fiber',
            'S_bad_bound = S[.GC.FAKE_NOCOLLECT = S.GC.FAKE_NOCOLLECT ++ [n_bound]]',
            '~$gc_state_valid(S_bad_bound)',
            '$gc_buffer_valid(S, S.GC)', '$gc_state_valid(S)',
        ], 'timeout': 240,
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
