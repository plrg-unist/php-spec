#!/usr/bin/env python3
"""Preserve the authentic imported receive across a default constructor."""
from pathlib import Path

import closure_call_protocol as protocol
import trait_method_review_protocol as traits

CASES = {
    'trait-default-constructor-retains-authentic-import-frame': {
        'source': '<?php trait T{static function f($x=new self){'
                  'echo get_class($x),":",get_called_class(),";";}}'
                  'class C{use T{f as g;}function __construct(){'
                  'echo get_called_class(),":C;";}}class D extends C{}D::g();',
        'stage': ('S.CURRENT = (pcallcontext_ctor) '
                  '-- if $default_ctor_context_kind(S, pcallcontext_ctor) '
                  '-- if S.FRAMES = pframe :: pframe_tail* '
                  '-- if pframe.TODO = (DEFAULT_CTOR_RESULT pdefaultctor) :: ptask_tail* '
                  '-- if pframe.CONTEXT = (pcallcontext_maker) '
                  '-- if pcallcontext_maker.FUNCTION = '
                  'TRAIT_ORIGIN porigin_owner porigin_source ptbytes_selected'),
        'checks': [
            *traits.VALID,
            'ptbytes_selected = $ptascii("g")',
            'pcallcontext_maker.LEXICAL_CLASS = (porigin_owner)',
            'pcallcontext_maker.CALLED_CLASS = (porigin_called)',
            'porigin_owner =/= porigin_called',
            'pcallcontext_ctor.LEXICAL_CLASS = (porigin_owner)',
            'pcallcontext_ctor.CALLED_CLASS = (porigin_owner)',
            'pcallcontext_ctor.FUNCTION = pdefaultctor.FUNCTION',
            '$default_ctor_context_valid(S, pcallcontext_ctor)',
            'S_owner = $constant_frame_scope(S, pframe, pframe_tail*)',
            '$call_current_valid(S_owner)',
            '$default_new_valid(S_owner, pdefaultctor.NEW)',
            '$default_ctor_valid(S_owner, pdefaultctor)',
            'pdefaultctor.NEW.CLASS = $ptascii("C")',
            'pdefaultctor.NEW.SITE = PORIGIN n_unit pcpath_new',
            '$code_at(S.CODE, n_unit) = (pcode)',
            '$code_name(pcode.NAMES, pcpath_new) = eps',
            '$new_source_name(S_owner, pdefaultctor.NEW.SITE) = ($ptascii("C"))',
            '~$default_new_valid(S_owner, pdefaultctor.NEW[.CLASS = $ptascii("T")])',
            '~$default_ctor_context_valid(S[.FRAMES = '
            'pframe[.CONTEXT = (pcallcontext_maker[.LEXICAL_CLASS = (porigin_called)])] '
            ':: pframe_tail*], pcallcontext_ctor)',
            '~$default_ctor_context_valid(S[.FRAMES = '
            'pframe[.CONTEXT = (pcallcontext_maker[.FUNCTION = '
            'TRAIT_ORIGIN porigin_owner porigin_source $ptascii("f")])] '
            ':: pframe_tail*], pcallcontext_ctor)',
            'pframe.LOCALS = (psymboltable_owner)',
            '~$default_ctor_context_valid(S[.FRAMES = '
            'pframe[.LOCALS = (psymboltable_owner[.CVS = eps])] :: pframe_tail*], '
            'pcallcontext_ctor)',
            *traits.FINISH,
        ],
    },
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), Path(traits.__file__).resolve()))
