#!/usr/bin/env python3
"""Check genuine clone histories and capture disposal before receiver cleanup."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_owning_quiet_empty_get_review_protocol as owning
import magic_property_realclosure_quiet_get_review_protocol as literal
import magic_property_arrow_quiet_get_review_protocol as arrow

CATALOGUE = Path(__file__).with_name('magic_property_clone_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def clone_front(front):
    return [check for check in front
            if check != 'S.CLOSURECACHES = [pclosurecache]'
            and not check.startswith('pclosurecache.OBJECT = ')]


HISTORY = r'''
pclosurecache.OBJECT = n_closure /\ pclosurecache.FUNCTION = porigin_closure /\ pclosurecache.SOURCE = (n_source)
$lookup(S.ENV,$ptascii("seed")) = (n_seed_cell)
S.STORE[n_seed_cell] = DEFINED PNULL
$closure_cache_at(S.CLOSURECACHES,n_seed) = (pclosurecache_seed)
pclosurecache_seed.OBJECT = n_seed /\ pclosurecache_seed.FUNCTION = porigin_closure /\ pclosurecache_seed.SOURCE = eps
pclosurecache_seed.SCOPE = (BIND_UNSCOPED) /\ pclosurecache_seed.CACHE = (CACHE_SHARED)
S.OBJECTS[n_seed] = REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) eps
~((HOBJECT n_seed) <- S.ALLOCATIONS)
$property_magic_cv_literal_history(S,n_seed,porigin_closure)
$property_magic_cv_literal_history(S,n_closure,porigin_closure)
~$property_magic_cv_literal_history(S,|S.OBJECTS|,porigin_closure)
~$property_magic_cv_literal_history(S,n_closure,pmethoddesc.FUNCTION.ORIGIN)
~$property_magic_cv_literal_history(S[.CLOSURECACHES = eps],n_closure,porigin_closure)
S_named_seed = S[.OBJECTS[n_seed] = NAMEDCLOSURE porigin_closure]
$closure_cache_records_valid(S_named_seed)
~$property_magic_cv_literal_history(S_named_seed,n_closure,porigin_closure)
S_wrapped_seed = S[.OBJECTS[n_seed] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) eps)]
$closure_cache_records_valid(S_wrapped_seed)
~$property_magic_cv_literal_history(S_wrapped_seed,n_closure,porigin_closure)
S_empty_seed = S[.OBJECTS[n_seed] = REALCLOSURE porigin_closure eps eps]
$closure_cache_records_valid(S_empty_seed)
$property_magic_cv_literal_history(S_empty_seed,n_closure,porigin_closure)
$closure_live_object_valid(S_empty_seed,n_closure)
$closure_state_valid(S_empty_seed)
n_current_cache = $nabs($(|S.CLOSURECACHES| - 1))
S_self_source = S[.CLOSURECACHES[n_current_cache] = pclosurecache[.SOURCE = (n_closure)]]
~$property_magic_cv_literal_history(S_self_source,n_closure,porigin_closure)
S_wrong_source = S[.CLOSURECACHES[n_current_cache] = pclosurecache[.SOURCE = (n_receiver)]]
~$property_magic_cv_literal_history(S_wrong_source,n_closure,porigin_closure)
S_missing_seed = S[.CLOSURECACHES = S.CLOSURECACHES[1:n_current_cache]]
~$property_magic_cv_literal_history(S_missing_seed,n_closure,porigin_closure)
S_private_seed = S[.CLOSURECACHES[0] = pclosurecache_seed[.CACHE = (CACHE_PRIVATE n_seed)]]
~$property_magic_cv_literal_history(S_private_seed,n_closure,porigin_closure)
S_scoped_seed = S[.CLOSURECACHES[0] = pclosurecache_seed[.SCOPE = (BIND_CLASS pmethoddesc.OWNER)]]
~$property_magic_cv_literal_history(S_scoped_seed,n_closure,porigin_closure)
S_unknown_seed = S[.CLOSURECACHES[0] = pclosurecache_seed[.CACHE = eps]]
~$property_magic_cv_literal_history(S_unknown_seed,n_closure,porigin_closure)
'''.strip().splitlines()

FN_CHAIN = r'''
pclosurecache.SOURCE = (n_seed)
n_source = n_seed
$closure_cache_at(S.CLOSURECACHES,n_seed) = (pclosurecache_seed)
S.CLOSURECACHES = [pclosurecache_seed,pclosurecache]
'''.strip().splitlines()

ARROW_CHAIN = r'''
pclosurecache.SOURCE = (n_middle)
n_source = n_middle
$lookup(S.ENV,$ptascii("middle")) = (n_middle_cell)
S.STORE[n_middle_cell] = DEFINED PNULL
$closure_cache_at(S.CLOSURECACHES,n_middle) = (pclosurecache_middle)
pclosurecache_middle.SOURCE = (n_seed)
$closure_cache_at(S.CLOSURECACHES,n_seed) = (pclosurecache_seed)
pclosurecache_middle.OBJECT = n_middle /\ pclosurecache_middle.FUNCTION = porigin_closure /\ pclosurecache_middle.SOURCE = (n_seed)
pclosurecache_middle.SCOPE = (BIND_UNSCOPED) /\ pclosurecache_middle.CACHE = (CACHE_SHARED)
S.OBJECTS[n_middle] = REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) eps
~((HOBJECT n_middle) <- S.ALLOCATIONS)
S.CLOSURECACHES = [pclosurecache_seed,pclosurecache_middle,pclosurecache]
$property_magic_cv_literal_history(S,n_middle,porigin_closure)
S_named_middle = S[.OBJECTS[n_middle] = NAMEDCLOSURE porigin_closure]
$closure_cache_records_valid(S_named_middle)
~$property_magic_cv_literal_history(S_named_middle,n_closure,porigin_closure)
'''.strip().splitlines()

AUTHORITY = r'''
$quiet(S,n_closure)
~$quiet(S,|S.OBJECTS|)
~$quiet(S[.SOURCES = eps],n_closure)
~$quiet(S[.CLOSURETEMPLATES = eps],n_closure)
~$quiet(S[.OBJECTS[n_closure] = NAMEDCLOSURE porigin_closure],n_closure)
~$quiet(S[.OBJECTS[n_closure] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) eps)],n_closure)
~$quiet(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure eps eps],n_closure)
~$quiet(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([ALIAS n_payload_cell]) eps],n_closure)
~$quiet(S[.OBJECTS[n_closure] = REALCLOSURE porigin_closure ([DIRECT (POBJECT n_payload)]) ([{ORIGIN porigin_closure,CELL n_payload_cell}])],n_closure)
~$quiet(S[.TODO = (AT porigin_closure (CLOSURE_CAPTURE n_closure 1)) :: S.TODO],n_closure)
~$quiet(S[.CLOSURESCOPES = [{OBJECT n_closure,LEXICAL pmethoddesc.OWNER,CALLED pmethoddesc.OWNER,RECEIVER eps,CREATION eps}]],n_closure)
~$quiet(S[.CLOSUREBINDINGS = [{OBJECT n_closure,SITE ppropertyempty.SITE,SOURCE n_receiver,LEXICAL eps,CALLED eps,RECEIVER eps}]],n_closure)
~$quiet(S_named_seed,n_closure)
~$quiet(S_wrapped_seed,n_closure)
$quiet(S_empty_seed,n_closure)
~$quiet(S_self_source,n_closure)
~$quiet(S_wrong_source,n_closure)
~$quiet(S_missing_seed,n_closure)
~$quiet(S_private_seed,n_closure)
~$quiet(S_scoped_seed,n_closure)
~$quiet(S_unknown_seed,n_closure)
S_reordered = S[.CLOSURECACHES = [pclosurecache] ++ S.CLOSURECACHES[0:n_current_cache]]
~$quiet(S_reordered,n_closure)
'''.strip().splitlines()

CV_FRONT = r'''
$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)
~$property_empty_capture(S,ppropertyempty)
$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,false,S.RESULT)
~$property_magic_cv_result_supported(S_named_seed,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
~$property_magic_cv_result_supported(S_wrapped_seed,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)
'''.strip().splitlines()

STAGE = ('S.TODO = (PROPERTY_EMPTY_RESULT ppropertyempty true) :: ptask_tail* '
         '-- if S.RESULT = KNOWN (POBJECT n_closure)')
CASES = {
    ROWS[0]['id']: {
        'source': ROWS[0]['source'], 'stage': STAGE,
        'checks': clone_front(literal.FRONT) + FN_CHAIN + HISTORY + [
            check.replace('$quiet', '$property_magic_cv_realclosure') for check in AUTHORITY
        ] + CV_FRONT + literal.LIFETIME + literal.NORMAL + literal.DONE + [
            'S_done.STORE[n_destination] = DEFINED (PBOOL false)',
            '$owning_review_output(S_done.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;RECEIVER;FALSE;CAPTURE;RECEIVER_GONE;DONE;")',
        ],
    },
    ROWS[1]['id']: {
        'source': ROWS[1]['source'], 'stage': STAGE,
        'checks': clone_front(arrow.FRONT) + ARROW_CHAIN + HISTORY + [
            check.replace('$quiet', '$property_magic_cv_arrow') for check in AUTHORITY
        ] + literal.LITERAL_FRONT + literal.LIFETIME + literal.THROW + literal.DONE + [
            r'S_done.STORE[n_destination] = DEFINED (PINT 42) /\ $lookup(S_done.ENV,$ptascii("failure")) = eps',
            '$owning_review_output(S_done.EVENTS) = $ptascii("I;G;PAYLOAD;CLOSURE_GONE;RECEIVER_LIVE;RECEIVER;CAUGHT;KEEP;CAPTURE;RECEIVER_GONE;DONE;")',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(owning.__file__), owning.CATALOGUE,
                  Path(literal.__file__), literal.CATALOGUE, Path(arrow.__file__), arrow.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=literal.render)
