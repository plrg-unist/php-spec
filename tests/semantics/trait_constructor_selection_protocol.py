#!/usr/bin/env python3
"""Genuine deferred trait constructor scope and history after capture retirement."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('trait_constructor_selection_cases.json')
SOURCE = json.loads(CATALOGUE.read_text())['cases'][0]['source']
CASES = {'ordinary-pure-capture-keeps-selected-constructor-history-after-retirement': {
    'source': SOURCE,
    'stage': 'S.TODO = (CLASS_CONST_CONSTRUCT_SELECTED pstaticselection phpType7* true z) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_capture -- if pcallcontext.LEXICAL_CLASS = (pstaticselection.ROOT) -- if pcallcontext.CALLED_CLASS = (pstaticselection.ROOT) -- if $class_at(S.CLASSES, pstaticselection.ROOT) = (pclassdesc_c) -- if pclassdesc_c.NAME = $ptascii("C") -- if S.CONSTCONTEXT = (pconstantcontext) -- if S.ORIGIN = (pstaticselection.SITE)',
    'checks': ['$call_current_valid(S)',
 '(HOBJECT n_capture) <- S.ALLOCATIONS',
 'pstaticselection.CLOSURE = eps',
 'pstaticselection.SCOPE = (pstaticselection.ROOT) /\\ pstaticselection.CALLED = '
 '(pstaticselection.ROOT)',
 '$closure_evidence_current(S) = (CLOSURE_SCOPE pclosurescope)',
 'pclosurescope.OBJECT = n_capture',
 '$trait_default_selection_evidence(S, pstaticselection.SITE) = eps',
 '$class_static_selection_at(S.TODO) = (pstaticselection)',
 '$class_static_selection_valid(S, pstaticselection)',
 '$class_constant_selected_constructor_task(S, pstaticselection, phpType7*, true, z)',
 'phpType7* = [NArg ABSENT (NScalarInt (INTEGER 7) metadata_value) (BOOLEAN false) (BOOLEAN false) '
 'metadata_arg]',
 'z = pconstantcontext.LINE',
 'n_prefix = |S.DECLARATIONS|',
 'n_last = $nabs($(|S.CLASSCONSTANTHISTORY| - 1))',
 'S.CLASSCONSTANTHISTORY[n_last] = CCUPDATESELECT pstaticselection.ROOT pstaticselection n_prefix',
 'PhpStep: S ~> S_allocated',
 'S_allocated.COMPLETION = NORMAL',
 'S_allocated.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*',
 'pdefaultnew.SITE = pstaticselection.SITE /\\ pdefaultnew.CLASS = pclassdesc_c.NAME /\\ '
 'pdefaultnew.ARGUMENTS = phpType7* /\\ pdefaultnew.LINE = z',
 'pdefaultnew.INDEX = 0 /\\ pdefaultnew.VALUES = eps',
 'S_allocated.OBJECTS[pdefaultnew.OBJECT] = INSTANCE pstaticselection.ROOT',
 '(HOBJECT pdefaultnew.OBJECT) <- S_allocated.ALLOCATIONS',
 'S_end = $drive_steps(S_allocated, 2000)',
 'S_end.COMPLETION = NORMAL',
 'S_end.CURRENT = eps',
 '~((HOBJECT n_capture) <- S_end.ALLOCATIONS)',
 '$closure_scope_at(S_end.CLOSURESCOPES, n_capture) = eps',
 '$lookup(S_end.ENV, $ptascii("f")) = eps',
 'S_end.CLASSCONSTANTHISTORY[0:|S.CLASSCONSTANTHISTORY|] = S.CLASSCONSTANTHISTORY',
 '$class_static_selection_valid(S_end, pstaticselection)',
 '$class_constant_history_valid(S_end)',
 '$class_constant_table_done(S_end, pstaticselection.ROOT)',
 '$class_static_select(S_end, pstaticselection.ROOT, $ptascii("x")) = (ppropertydesc)',
 '$class_static_at(S_end.CLASSSTATICS, ppropertydesc.ORIGIN) = (pclassstatic)',
 'pclassstatic.STATE = PROP_VALUE (DIRECT (PARRAY n_array))',
 'S_end.TODO = eps',
 '$lookup(S_end.ENV, $ptascii("value")) = (n_value)',
 'S_end.STORE[n_value] = DEFINED (PINT 7)'],
}}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
