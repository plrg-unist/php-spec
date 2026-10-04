#!/usr/bin/env python3
"""A genuine imported constant initializer retains its using-class scope."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_scope_review_cases.json')
SOURCE = next(row['source'] for row in json.loads(CATALOGUE.read_text())['cases']
              if row['id'] == 'nested-property-class-magic-per-final-import')

CASES = {
    'using-class-is-from-authentic-imported-constant-binding': {
        'source': SOURCE,
        'stage': ('S.TODO = (EVAL (NScalarMagicConstClass metadata)) :: ptask_tail* '
                  '-- if S.CONSTCONTEXT = (pconstantcontext) '
                  '-- if pconstantcontext.ORIGIN = '
                  'TRAIT_MEMBER_ORIGIN porigin_owner porigin_source'),
        'checks': [
            'S.CURRENT = eps',
            '$call_descriptors_valid(S)',
            '$declaration_history_valid(S)',
            '$class_constant_state_valid(S)',
            '$class_statics_valid(S)',
            '$heap_valid($heap_graph(S))',
            '$class_at(S.CLASSES, porigin_owner) = (pclassdesc)',
            'pclassdesc.NAME = $ptascii("C")',
            '$class_constant_origin(S.CLASSES, pconstantcontext.ORIGIN) '
            '= (pclassconstantdesc)',
            'pclassconstantdesc.OWNER = porigin_owner',
            '$origin_source(pclassconstantdesc.ORIGIN) = '
            '$origin_source(porigin_source)',
            'S.ORIGIN = (porigin_site)',
            '$constant_expression_below(S, pconstantcontext.ORIGIN, porigin_site)',
            '$trait_initializer_scope(S) = (porigin_owner)',
            '~pclassconstantdesc.FOLDED',
            '$compiled_read(S, porigin_site) = eps',
            'S.CLASSCONSTANTINIT = pclassconstantcontext :: '
            'pclassconstantcontext_tail*',
            'pclassconstantcontext.DECL = pconstantcontext.ORIGIN',
            '$trait_initializer_scope(S[.CONSTCONTEXT = eps]) = eps',
            '$trait_initializer_scope(S[.CONSTCONTEXT = '
            '(pconstantcontext[.ORIGIN = porigin_source])]) = eps',
            '$trait_initializer_scope(S[.CONSTCONTEXT = '
            '(pconstantcontext[.ORIGIN = TRAIT_MEMBER_ORIGIN '
            '(PORIGIN 999 eps) porigin_source])]) = eps',
            '$trait_initializer_scope(S[.CLASSCONSTANTINIT = eps]) = eps',
            '$trait_initializer_scope(S[.CLASSCONSTANTINIT = '
            'pclassconstantcontext[.DECL = porigin_source] :: '
            'pclassconstantcontext_tail*]) = eps',
            '$trait_initializer_scope(S[.TODO = eps]) = eps',
            '$trait_initializer_scope(S[.ORIGIN = '
            '(PORIGIN 999 eps)]) = eps',
            '~$class_constant_state_valid(S[.CLASSCONSTANTINIT = '
            'pclassconstantcontext[.DECL = porigin_source] :: '
            'pclassconstantcontext_tail*])',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$class_constant_state_valid(S_done)',
            '$class_statics_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
