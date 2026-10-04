#!/usr/bin/env python3
"""Unimplemented instance templates are reached dependencies, not PHP agreement."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_scalar_review_cases.json')
SOURCES = {row['id']: row['source']
           for row in json.loads(CATALOGUE.read_text())['cases']}
COMMON = [
    'S.CURRENT = eps',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_statics_valid(S)',
    '$class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) = (porigin_c)',
    '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
    '$ppproperty_desc_at(pclassdesc_c.PROPERTIES, $ptascii("x")) '
    '= (ppropertydesc_x)',
    'ppropertydesc_x.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_source',
    'ppropertydesc_x.DEFAULT = PROP_DEFERRED porigin_initializer',
    '$constant_expression_root(S, TRAIT_MEMBER_ORIGIN porigin_c '
    'porigin_source) = (porigin_initializer)',
    '~$trait_instance_default_ready(S, ppropertydesc_x)',
    '~$trait_instance_named_ready(S, $ptascii("C"))',
    'S_done = $drive(S, 2000)',
    'S_done.COMPLETION = '
    'UNSUPPORTED "deferred trait instance-default templates"',
    'S_done.CURRENT = eps',
    'S_done.FRAMES = eps',
    '$class_statics_valid(S_done)',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
]
CASES = {
    'new-reaches-instance-template-dependency': {
        'source': SOURCES['imported-instance-scalar-rejects-wrong-type'],
        'stage': ('S.TODO = (EVAL (NExprNew phpType28 phpType6 metadata)) '
                  ':: ptask_tail*'),
        'checks': COMMON,
    },
    'static-read-reaches-instance-template-dependency': {
        'source': SOURCES['imported-instance-scalar-checked-by-static-table-use'],
        'stage': ('S.TODO = (EVAL (NExprStaticPropertyFetch phpType19 '
                  'phpType31 metadata)) :: ptask_tail*'),
        'checks': COMMON[:11] + [
            '~$trait_instance_selected_ready(S, KNOWN (PSTRING '
            '$ptascii("C")), $ptascii("y"))',
            '$trait_instance_selected_ready(S, KNOWN (PSTRING '
            '$ptascii("C")), $ptascii("missing"))',
        ] + COMMON[11:],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
