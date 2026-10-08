#!/usr/bin/env python3
"""Genuine trait REAL cache and selected constructor authority after capture retirement."""
from pathlib import Path
import json

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name("trait_real_constructor_interaction_cases.json")
SOURCE = json.loads(CATALOGUE.read_text())["cases"][0]["source"]
CASES = {'real-birth-authority-survives-selected-constructor-and-capture-retirement': {
    "source": SOURCE,
    "stage": 'S.TODO = (CLASS_CONST_CONSTRUCT_SELECTED pstaticselection phpType7* true z) :: ptask_tail* -- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_capture -- if pcallcontext.LEXICAL_CLASS = (pstaticselection.ROOT) -- if pcallcontext.CALLED_CLASS = (pstaticselection.ROOT) -- if $class_at(S.CLASSES, pstaticselection.ROOT) = (pclassdesc_c) -- if pclassdesc_c.NAME = $ptascii("C") -- if S.CONSTCONTEXT = (pconstantcontext) -- if S.ORIGIN = (pstaticselection.SITE)',
    "checks": ['$call_current_valid(S)',
 '(HOBJECT n_capture) <- S.ALLOCATIONS',
 'pstaticselection.CLOSURE = eps /\\ pstaticselection.SCOPE = (pstaticselection.ROOT) /\\ '
 'pstaticselection.CALLED = (pstaticselection.ROOT)',
 '$class_static_selection_valid(S, pstaticselection)',
 '$class_constant_selected_constructor_task(S, pstaticselection, phpType7*, true, z)',
 'phpType7* = [NArg ABSENT (NScalarInt (INTEGER 7) metadata_value) (BOOLEAN false) (BOOLEAN false) '
 'metadata_arg]',
 'z = pconstantcontext.LINE',
 '$class_static_select(S, pstaticselection.ROOT, $ptascii("x")) = (ppropertydesc)',
 '$class_static_at(S.CLASSSTATICS, ppropertydesc.ORIGIN) = (pclassstatic)',
 'pclassstatic.STATE = PROP_VALUE (DIRECT (POBJECT n_real))',
 'n_real =/= n_capture',
 '(HOBJECT n_real) <- S.ALLOCATIONS',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_real) = (pconstantclosure_real)',
 '$trait_real_birth_at(S.CLASSCONSTANTHISTORY, n_real) = ((pconstantclosure_real.SITE, ptraitcachecause))',
 'ptraitcachecause.CLASS = pstaticselection.ROOT /\\ pconstantclosure_real.PREFIX = ptraitcachecause.PREFIX',
 '$trait_real_cause(S, ptraitcachecause) = (pclassconstantdesc)',
 'pconstantclosure_real.DECL = pclassconstantdesc.ORIGIN',
 '$trait_real_birth_owner(S, pconstantclosure_real) = (pstaticselection.ROOT)',
 '$constant_callable_record_valid(S, pconstantclosure_real)',
 '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = (pdefaultcache)',
 'pdefaultcache.VALUE = POBJECT n_real',
 '$trait_cache_event_at(S.CLASSCONSTANTHISTORY, pclassconstantdesc.ORIGIN) = (ptraitcachecause)',
 'n_prefix = |S.DECLARATIONS|',
 '(CCUPDATESELECT pstaticselection.ROOT pstaticselection n_prefix) <- S.CLASSCONSTANTHISTORY',
 '$class_constant_history_valid(S)',
 'PhpStep: S ~> S_allocated',
 'S_allocated.COMPLETION = NORMAL',
 'S_allocated.TODO = (DEFAULT_NEW_ARGS pdefaultnew) :: ptask_tail*',
 'pdefaultnew.SITE = pstaticselection.SITE /\\ pdefaultnew.CLASS = pclassdesc_c.NAME /\\ '
 'pdefaultnew.ARGUMENTS = phpType7* /\\ pdefaultnew.LINE = z',
 'pdefaultnew.INDEX = 0 /\\ pdefaultnew.VALUES = eps',
 'S_allocated.OBJECTS[pdefaultnew.OBJECT] = INSTANCE pstaticselection.ROOT',
 '(HOBJECT pdefaultnew.OBJECT) <- S_allocated.ALLOCATIONS',
 'S_end = $drive_steps(S_allocated, 2000)',
 'S_end.COMPLETION = NORMAL /\\ S_end.TODO = eps /\\ S_end.CURRENT = eps',
 '~((HOBJECT n_capture) <- S_end.ALLOCATIONS)',
 '$closure_scope_at(S_end.CLOSURESCOPES, n_capture) = eps',
 '$lookup(S_end.ENV, $ptascii("f")) = eps',
 '(HOBJECT n_real) <- S_end.ALLOCATIONS',
 'S_end.CLASSCONSTANTHISTORY[0:|S.CLASSCONSTANTHISTORY|] = S.CLASSCONSTANTHISTORY',
 '$trait_real_birth_at(S_end.CLASSCONSTANTHISTORY, n_real) = ((pconstantclosure_real.SITE, '
 'ptraitcachecause))',
 '$trait_real_birth_owner(S_end, pconstantclosure_real) = (pstaticselection.ROOT)',
 '$constant_callable_record_valid(S_end, pconstantclosure_real)',
 '$default_cache_at(S_end.CLASSCONSTANTCACHE, pclassconstantdesc.ORIGIN) = (pdefaultcache)',
 '$class_constant_history_valid(S_end)',
 '$class_static_at(S_end.CLASSSTATICS, ppropertydesc.ORIGIN) = (pclassstatic)',
 '~$class_static_selection_valid(S, pstaticselection[.SITE = pconstantclosure_real.SITE])'],
}}

if __name__ == "__main__":
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE))
