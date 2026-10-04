#!/usr/bin/env python3
"""Keep imported lexical scope in copied source Closure cold selections."""
from pathlib import Path

import closure_call_protocol as protocol
import trait_method_review_protocol as traits

CASES = {
    'retired-imported-maker-closure-cold-scope': {
        'source': '<?php trait T{static function maker(){return function(){$r=&self::$p;$r=9;};}}'
                  'class C{use T{maker as g;}public static $p=LATE;}'
                  'class D extends C{}class E{}const LATE=2;$f=D::g();$f();echo C::$p,";";',
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = CLOSURE_TARGET n_closure '
                  '-- if S.TODO = (CLASS_CONST_SELECTED pstaticselection ptbytes_member z) '
                  ':: ptask_tail* '
                  '-- if pstaticselection.CLOSURE = (CLOSURE_SCOPE pclosurescope)'),
        'checks': [
            *traits.VALID,
            'pclosurescope.OBJECT = n_closure',
            '$closure_evidence_body(S, n_closure) = (porigin_function)',
            'pcallcontext.FUNCTION = porigin_function',
            '$closure_source_class(S, porigin_function) = (porigin_trait)',
            'pclosurescope.LEXICAL =/= porigin_trait',
            'pcallcontext.LEXICAL_CLASS = (pclosurescope.LEXICAL)',
            'pcallcontext.CALLED_CLASS = (pclosurescope.CALLED)',
            '$class_at(S.CLASSES, pclosurescope.LEXICAL) = (pclassdesc_lexical)',
            'pclassdesc_lexical.NAME = $ptascii("C")',
            '$class_at(S.CLASSES, pclosurescope.CALLED) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("D")',
            '$trait_closure_method(S, porigin_function) = (porigin_maker_source)',
            '$trait_class_owns_source(S, pclosurescope.LEXICAL, porigin_maker_source)',
            '$closure_scope_classes_valid(S, porigin_function, pclosurescope)',
            '$closure_evidence_valid(S, CLOSURE_SCOPE pclosurescope)',
            'pclosurescope.CREATION = eps',
            'pstaticselection.SCOPE = (pclosurescope.LEXICAL)',
            'pstaticselection.ROOT = pclosurescope.LEXICAL',
            'pstaticselection.CALLED = (pclosurescope.CALLED)',
            '$class_static_selection_valid(S, pstaticselection)',
            '$class_static_selection_method(S, pstaticselection.SITE) = eps',
            '$class_named(S.CLASSNAMES, $ptascii("e")) = (porigin_unrelated)',
            '~$closure_scope_classes_valid(S, porigin_function, '
            'pclosurescope[.LEXICAL = pclosurescope.CALLED])',
            '~$closure_scope_classes_valid(S, porigin_function, '
            'pclosurescope[.LEXICAL = porigin_unrelated][.CALLED = porigin_unrelated])',
            '~$closure_evidence_valid(S, CLOSURE_SCOPE '
            'pclosurescope[.LEXICAL = PORIGIN 999 eps])',
            '~$class_static_selection_valid(S, pstaticselection[.CLOSURE = eps])',
            '~$class_static_selection_valid(S, pstaticselection[.SCOPE = eps])',
            '~$class_static_selection_valid(S, '
            'pstaticselection[.SCOPE = (pclosurescope.CALLED)])',
            '~$class_static_selection_valid(S, '
            'pstaticselection[.CLOSURE = (CLOSURE_SCOPE '
            'pclosurescope[.LEXICAL = porigin_unrelated][.CALLED = porigin_unrelated])])',
            *traits.FINISH,
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), Path(traits.__file__).resolve()))
