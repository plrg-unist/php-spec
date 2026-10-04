#!/usr/bin/env python3
"""Separate active alias identity from historical cold-selection scope."""
from pathlib import Path

import closure_call_protocol as protocol
import trait_method_review_protocol as traits

CASES = {
    'cold-self-selection-keeps-authentic-import-and-source': {
        'source': '<?php trait T{static function f(){$r=&self::$p;$r=7;echo self::$p,";";}}'
                  'class C{use T{f as g;}public static $p=LATE;}'
                  'class D extends C{}const LATE=3;D::g();echo C::$p,";";',
        'stage': (traits.IMPORTED + ' -- if S.TODO = '
                  '(CLASS_CONST_SELECTED pstaticselection ptbytes_member z) :: ptask_tail*'),
        'checks': [
            *traits.VALID,
            'ptbytes_selected = $ptascii("g")',
            'pstaticselection.SCOPE = (porigin_owner)',
            'pstaticselection.ROOT = porigin_owner',
            'pstaticselection.CALLED = (porigin_called)',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            'porigin_owner =/= porigin_called',
            '$class_static_selection_valid(S, pstaticselection)',
            '$class_static_selected_task(S, pstaticselection, ptbytes_member, z)',
            '$class_static_selection_method(S, pstaticselection.SITE) = (pmethoddesc)',
            'pmethoddesc.FUNCTION.ORIGIN = pcallcontext.FUNCTION',
            'pmethoddesc.OWNER = porigin_owner',
            'pstaticselection.SITE = PORIGIN n_unit pcpath_site',
            '$goto_source_owner($all_functions(S), n_unit, pcpath_site) = (pfunction_source)',
            'pfunction_source.ORIGIN = $origin_source(pcallcontext.FUNCTION)',
            '$class_static_selection_scope_method(S, pstaticselection.SITE, porigin_owner) = '
            '(pmethoddesc_history)',
            'pmethoddesc_history.OWNER = porigin_owner',
            '$trait_source_same(pfunction_source, pmethoddesc_history.FUNCTION)',
            '$class_static_selection_method(S[.CURRENT = '
            '(pcallcontext[.LEXICAL_CLASS = (porigin_called)])], pstaticselection.SITE) = eps',
            '$class_static_selection_method(S[.CURRENT = '
            '(pcallcontext[.FUNCTION = TRAIT_ORIGIN porigin_owner porigin_source '
            '$ptascii("f")])], pstaticselection.SITE) = eps',
            '~$class_static_selection_valid(S, pstaticselection[.SCOPE = eps])',
            '~$class_static_selection_valid(S, '
            'pstaticselection[.SCOPE = (PORIGIN 999 eps)])',
            '~$class_static_selection_valid(S, '
            'pstaticselection[.SCOPE = (porigin_called)])',
            '~$class_static_selection_valid(S, '
            'pstaticselection[.SITE = PORIGIN 999 eps])',
            '~$call_task_valid(S, CLASS_CONST_SELECTED '
            'pstaticselection[.ROOT = porigin_called] ptbytes_member z)',
            '~$call_task_valid(S, CLASS_CONST_SELECTED '
            'pstaticselection $ptascii("foreign") z)',
            'S_fetch = $drive_steps(S, 1)',
            'S_fetch.TODO = (PROPERTY_REF_FETCH z) :: ptask_fetch_tail*',
            'S_fetch.ORIGIN = (pstaticselection.SITE)',
            'S_fetch.BASE = BASE_CLASS_STATIC porigin_owner ptbytes_member',
            '$call_task_valid(S_fetch, PROPERTY_REF_FETCH z)',
            '~$call_task_valid(S_fetch[.BASE = BASE_VALUE (KNOWN PNULL)], '
            'PROPERTY_REF_FETCH z)',
            *traits.FINISH,
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), Path(traits.__file__).resolve()))
