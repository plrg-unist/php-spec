#!/usr/bin/env python3
"""Authenticate a deferred trait NEW receive at its genuine source site."""
from pathlib import Path

import closure_call_protocol as protocol
import trait_method_review_protocol as traits

CASES = {
    'new-self-default-uses-authentic-importing-receive': {
        'source': '<?php trait T{function f($x=new self){echo get_class($x),";";}}'
                  'class C{use T;}class E{use T;}'
                  '(new C)->f();(new E)->f();(new C)->f();',
        'stage': (traits.IMPORTED + ' -- if S.ORIGIN = (porigin_new) '
                  '-- if S.TODO = (EVAL (NExprNew name (SEQUENCE eps) metadata)) :: ptask_tail*'),
        'checks': [
            *traits.VALID,
            '$class_at(S.CLASSES, porigin_owner) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("C")',
            'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
            '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)',
            '$default_at(pfunction.DEFAULTS, 0) = (pdefault)',
            'pdefault.ORIGIN = porigin_new',
            'porigin_new = PORIGIN n_unit pcpath_new',
            '$code_at(S.CODE, n_unit) = (pcode)',
            '$code_name(pcode.NAMES, pcpath_new) = eps',
            '$trait_default_new_site(S, porigin_new)',
            '$new_source_name(S, porigin_new) = ($ptascii("C"))',
            '$class_expr_task_valid(S, NExprNew name (SEQUENCE eps) metadata)',
            '$class_named(S.CLASSNAMES, $ptascii("e")) = (porigin_other)',
            '~$trait_default_new_site(S[.CURRENT = '
            '(pcallcontext[.LEXICAL_CLASS = (porigin_other)])], porigin_new)',
            '$new_source_name(S[.CURRENT = '
            '(pcallcontext[.LEXICAL_CLASS = (porigin_other)])], porigin_new) = eps',
            '~$class_expr_task_valid(S[.CURRENT = '
            '(pcallcontext[.LEXICAL_CLASS = (porigin_other)])], '
            'NExprNew name (SEQUENCE eps) metadata)',
            '~$trait_default_new_site(S[.CURRENT = '
            '(pcallcontext[.FUNCTION = TRAIT_ORIGIN porigin_other porigin_source '
            'ptbytes_selected])], porigin_new)',
            '~$trait_default_new_site(S[.ORIGIN = (PORIGIN 999 eps)], PORIGIN 999 eps)',
            '$new_source_name(S[.ORIGIN = (PORIGIN 999 eps)], PORIGIN 999 eps) = eps',
            *traits.FINISH,
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), Path(traits.__file__).resolve()))
