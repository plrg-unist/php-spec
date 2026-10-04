#!/usr/bin/env python3
"""A contextual type shortcut requires the genuine physical member group."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_raw_identity_review_cases.json')
SOURCE = next(row['source'] for row in json.loads(CATALOGUE.read_text())['cases']
              if row['id'] == 'same-raw-uppercase-self-retains-pointer-shortcut')

CASES = {
    'raw-keyword-proof-keeps-the-authentic-member-group': {
        'source': SOURCE,
        'stage': ('S.TODO = (EVAL (NExprNew phpType28 phpType6 metadata)) '
                  ':: ptask_tail* '
                  '-- if $class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) '
                  '= (porigin_c)'),
        'checks': [
            'S.CURRENT = eps',
            '$call_descriptors_valid(S)',
            '$declaration_history_valid(S)',
            '$class_statics_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S.CLASSES = [pclassdesc_t, pclassdesc_u, pclassdesc_c]',
            'pclassdesc_t.PROPERTIES = [ppropertydesc_t]',
            'pclassdesc_u.PROPERTIES = [ppropertydesc_u]',
            'pclassdesc_c.PROPERTIES = [ppropertydesc_c]',
            'ppropertydesc_t.ORIGIN = porigin_t',
            'ppropertydesc_u.ORIGIN = porigin_u',
            'ppropertydesc_c.ORIGIN = porigin_import',
            '$trait_property_keyword_spelling(S, ppropertydesc_t) '
            '= ($ptascii("Self"))',
            '$trait_property_keyword_spelling(S, ppropertydesc_u) '
            '= ($ptascii("Self"))',
            '$trait_property_source_fast_equal(S, ppropertydesc_t, '
            'ppropertydesc_u)',
            '~$trait_property_source_fast_equal(S[.SOURCES = eps], '
            'ppropertydesc_t, ppropertydesc_u)',
            '~$trait_property_source_fast_equal(S, '
            'ppropertydesc_t[.ORIGIN = PORIGIN 999 eps], '
            'ppropertydesc_u[.ORIGIN = PORIGIN 999 eps])',
            '~$trait_property_source_fast_equal(S, '
            'ppropertydesc_t[.ORIGIN = porigin_c], '
            'ppropertydesc_u[.ORIGIN = porigin_c])',
            '~$declaration_history_valid(S[.CLASSES = [pclassdesc_t, '
            'pclassdesc_u, pclassdesc_c[.PROPERTIES = '
            '[ppropertydesc_t]]]])',
            '$origin_source(porigin_import) = porigin_t',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$class_statics_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
