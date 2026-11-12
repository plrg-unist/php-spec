#!/usr/bin/env python3
"""Check empty-name CV admission and fresh capture in fixture SL_mode."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('anonymous_missing_empty_name_cases.json')
row = json.loads(CATALOGUE.read_text())['cases'][1]
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

CASES = {
    'empty-name-cv-entry': {
        'source': row['source'],
        'stage': ('S.CURRENT = eps /\\ S.FRAMES = eps '
                  '-- if S.TODO = (PROPERTY_NAME (POBJECT n_receiver) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT false z) :: ptask_tail* '
                  '-- if S.ORIGIN = (porigin) '
                  '-- if $property_magic_cv_name(S,porigin,z) = (eps)'),
        'checks': [
            '$lookup(S.ENV,$ptascii("name")) = (n_selector)',
            'S.STORE[n_selector] = DEFINED (PSTRING_CARRIER INTERNED_STRING eps)',
            '$property_hook_plain_name(PSTRING_CARRIER INTERNED_STRING eps)',
            '$property_magic_cv_source(S,porigin,z) /\\ ~$property_hook_literal_site(S,porigin)',
            '$property_magic_name_capture(S,porigin,z,eps)',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            '$property_isset_method(S,n_receiver) = (pmethoddesc_isset)',
            '$property_magic_method_source(S,pmethoddesc_isset,"__isset")',
            '$property_get_method(S,n_receiver) = (pmethoddesc_get)',
            'pmethoddesc_get.OWNER = pmethoddesc_isset.OWNER',
            '$property_empty_get_source(S,pmethoddesc_get)',
            'ppropertyisset = {SITE porigin, NAME eps, LINE z, OBJECT n_receiver, CLASS porigin_class, METHOD pmethoddesc_isset.FUNCTION.ORIGIN, PROPERTY eps}',
            '$property_isset_source(S,ppropertyisset) /\\ ~$property_isset_empty(S,ppropertyisset)',
            '$property_isset_missing_source(S,ppropertyisset)',
            '$property_effective_desc(S,n_receiver,eps) = eps',
            '$property_resolve_scope(S,n_receiver,eps,$closure_source_class(S,porigin)) = PROPERTY_ACCESS eps',
            '$property_isset_storage_capture(S,ppropertyisset)',
            '$property_isset_bool_pair(S,ppropertyisset)',
            '$property_isset_valid(S,ppropertyisset) /\\ $property_isset_capture(S,ppropertyisset)',
            '$property_isset_plan(S) = (ppropertyisset)',
            'S_plain = S[.STORE[n_selector] = DEFINED (PSTRING eps)]',
            '$property_isset_capture(S_plain,ppropertyisset) /\\ $property_isset_plan(S_plain) = (ppropertyisset)',
            'S_renamed = S[.STORE[n_selector] = DEFINED (PSTRING ($ptascii("changed")))]',
            '~$property_isset_capture(S_renamed,ppropertyisset)',
            '$property_isset_capture(S_renamed,ppropertyisset[.NAME = $ptascii("changed")])',
            '$property_isset_plan(S_renamed) = (ppropertyisset[.NAME = $ptascii("changed")])',
            '$property_isset_capture(S_renamed[.STORE = S.STORE],ppropertyisset)',
            'S_nul = S[.STORE[n_selector] = DEFINED (PSTRING ([0]))]',
            '$property_magic_cv_name(S_nul,porigin,z) = eps /\\ $property_isset_plan(S_nul) = eps',
            '$property_isset_plan(S[.STORE[n_selector] = DEFINED (PINT 9)]) = eps',
            '$property_isset_plan(S[.STORE[n_selector] = UNDEFINED]) = eps',
            '$property_isset_plan(S[.SOURCES = eps]) = eps',
            '~$property_isset_valid(S,ppropertyisset[.PROPERTY = (porigin)])',
            '$call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S)',
            '$heap_valid($heap_prune($heap_graph(S)))',
            'PhpStep: S ~> S_call',
            '$property_isset_pending_call(S_call,ppropertyisset)',
            '$task_nodes(PROPERTY_ISSET_RESULT ppropertyisset) = [HOBJECT n_receiver]',
            '$target_nodes(PROPERTY_ISSET_TARGET ppropertyisset) = eps',
            '$heap_owners($heap_graph(S),HOBJECT n_receiver) = 2',
            '$heap_owners($heap_graph(S_call),HOBJECT n_receiver) = 2',
            '$call_descriptors_valid(S_call) /\\ $property_state_valid(S_call)',
            '$heap_valid($heap_prune($heap_graph(S_call)))',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE), runner_flags=('--sl',))
