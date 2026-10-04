#!/usr/bin/env python3
"""Imported static properties retain separate constraints on a shared cell."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_data_state_review_cases.json')
SOURCE = next(row['source'] for row in json.loads(CATALOGUE.read_text())['cases']
              if row['id'] == 'static-reference-keeps-both-import-type-sources')

CASES = {
    'shared-reference-retains-two-authentic-imports': {
        'source': SOURCE,
        'stage': ('S.PROPREFS = [ppropref] '
                  '-- if ppropref.SOURCES = '
                  '[CLASS_PROP_SOURCE porigin_c, CLASS_PROP_SOURCE porigin_e]'),
        'checks': [
            'S.CURRENT = eps',
            '$call_descriptors_valid(S)',
            '$declaration_history_valid(S)',
            '$class_statics_valid(S)',
            '$proprefs_valid(S)',
            '$heap_valid($heap_graph(S))',
            'S.CLASSES = [pclassdesc_t, pclassdesc_c, pclassdesc_e]',
            'pclassdesc_t.PROPERTIES = [ppropertydesc_t]',
            'pclassdesc_c.PROPERTIES = [ppropertydesc_c]',
            'pclassdesc_e.PROPERTIES = [ppropertydesc_e]',
            'ppropertydesc_c.ORIGIN = porigin_c',
            'ppropertydesc_e.ORIGIN = porigin_e',
            'porigin_c =/= porigin_e',
            '$origin_source(porigin_c) = ppropertydesc_t.ORIGIN',
            '$origin_source(porigin_e) = ppropertydesc_t.ORIGIN',
            '$class_static_at(S.CLASSSTATICS, porigin_c) = (pclassstatic_c)',
            '$class_static_at(S.CLASSSTATICS, porigin_e) = (pclassstatic_e)',
            'pclassstatic_c.STATE = PROP_VALUE (ALIAS ppropref.CELL)',
            'pclassstatic_e.STATE = PROP_VALUE (ALIAS ppropref.CELL)',
            'S.STORE[ppropref.CELL] = DEFINED PNULL',
            '$propref_source_valid(S, ppropref.CELL, CLASS_PROP_SOURCE porigin_c)',
            '$propref_source_valid(S, ppropref.CELL, CLASS_PROP_SOURCE porigin_e)',
            '~$propref_source_valid(S, ppropref.CELL, '
            'CLASS_PROP_SOURCE ppropertydesc_t.ORIGIN)',
            '~$propref_source_valid(S, ppropref.CELL, CLASS_PROP_SOURCE '
            '(TRAIT_MEMBER_ORIGIN (PORIGIN 999 eps) ppropertydesc_t.ORIGIN))',
            '~$class_statics_valid(S[.PROPREFS = '
            '[ppropref[.SOURCES = [CLASS_PROP_SOURCE porigin_c]]]])',
            '~$class_statics_valid(S[.PROPREFS = '
            '[ppropref[.SOURCES = [CLASS_PROP_SOURCE porigin_e]]]])',
            '~$proprefs_valid(S[.PROPREFS = [ppropref[.SOURCES = '
            '[CLASS_PROP_SOURCE porigin_c, CLASS_PROP_SOURCE porigin_c]]]])',
            '~$declaration_history_valid(S[.CLASSES = [pclassdesc_t, '
            'pclassdesc_c[.PROPERTIES = [ppropertydesc_e]], pclassdesc_e]])',
            '~$declaration_history_valid(S[.CLASSES = [pclassdesc_t, '
            'pclassdesc_c[.PROPERTIES = [ppropertydesc_c[.DEFAULT = '
            'PROP_DEFERRED (PORIGIN 999 eps)]]], pclassdesc_e]])',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$class_statics_valid(S_done)',
            '$proprefs_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
