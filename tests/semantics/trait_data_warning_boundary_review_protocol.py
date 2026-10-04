#!/usr/bin/env python3
"""Direct trait-property warnings remain explicit pending continuations."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_static_access_review_cases.json')
SOURCES = {row['id']: row['source']
           for row in json.loads(CATALOGUE.read_text())['cases']}
STAGE = ('S.ORIGIN = (porigin_site) '
         '-- if $origin_node(S.SOURCES, porigin_site) = '
         '(NExprStaticPropertyFetch phpType19 phpType31 metadata) '
         '-- if $class_named(S.CLASSNAMES, $ptlc($ptascii("T"))) = '
         '(porigin_t)')
CHECKS = [
    'S.CURRENT = eps',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$class_statics_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$class_static_select(S, porigin_t, $ptascii("x")) = (ppropertydesc)',
    '$class_static_at(S.CLASSSTATICS, ppropertydesc.ORIGIN) = (pclassstatic)',
    '$trait_static_property_deprecation_needed(S, porigin_t, $ptascii("x"))',
    '~$trait_static_property_deprecation_needed(S, porigin_t, '
    '$ptascii("missing"))',
    '~$trait_static_property_deprecation_needed(S[.TODO = [UNSET_ARRAY]], '
    'porigin_t, $ptascii("x"))',
    'S_done = $drive(S, 2000)',
    'S_done.COMPLETION = '
    'UNSUPPORTED "direct trait static-property deprecation continuation"',
    'S_done.CURRENT = eps',
    'S_done.FRAMES = eps',
    '$class_statics_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
]
CASES = {
    'direct-literal-read-reaches-warning-dependency': {
        'source': SOURCES['direct-trait-static-read-deprecated'],
        'stage': STAGE,
        'checks': CHECKS[:8] + [
            'pclassstatic.STATE = PROP_VALUE (DIRECT (PINT 1))',
            '$trait_static_property_deprecation_needed(S[.TODO = '
            '[DIM_FETCH 1]], porigin_t, $ptascii("x"))',
        ] + CHECKS[8:],
    },
    'quiet-uninitialized-reaches-warning-dependency': {
        'source': SOURCES['direct-trait-quiet-uninitialized-still-deprecated'],
        'stage': STAGE,
        'checks': CHECKS[:8] + [
            'pclassstatic.STATE = PROP_INITIAL',
            '~$trait_static_property_deprecation_needed(S[.TODO = '
            '[DIM_FETCH 1]], porigin_t, $ptascii("x"))',
        ] + CHECKS[8:],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
