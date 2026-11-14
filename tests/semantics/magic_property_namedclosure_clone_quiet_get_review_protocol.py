#!/usr/bin/env python3
"""Check raw named clone ancestry and borrowed function statics at quiet Empty."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_namedclosure_quiet_get_review_protocol as named

CATALOGUE = Path(__file__).with_name('magic_property_namedclosure_clone_quiet_get_review_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def warmed(checks):
    return [check.replace('(PINT 1)', '(PINT 2)').replace('WARM;', 'WARM;SHARED;')
            for check in checks]


FRONT = warmed([check for check in named.FRONT
                if check != 'S.CLOSURECACHES = [pclosurecache]'
                and not check.startswith('pclosurecache.OBJECT = ')])

ROOT = r'''
$lookup(S.ENV,$ptascii("seed")) = (n_seed_cell)
S.STORE[n_seed_cell] = DEFINED PNULL
$closure_cache_at(S.CLOSURECACHES,n_seed) = (pclosurecache_seed)
pclosurecache_seed.OBJECT = n_seed /\ pclosurecache_seed.FUNCTION = porigin_named /\ pclosurecache_seed.SOURCE = eps
pclosurecache_seed.SCOPE = (BIND_UNSCOPED) /\ pclosurecache_seed.CACHE = (CACHE_SHARED)
S.OBJECTS[n_seed] = NAMEDCLOSURE porigin_named
~((HOBJECT n_seed) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S),HOBJECT n_seed) = 0
$node_children(S,HOBJECT n_seed) = eps /\ $destruction_child_jobs(S,HOBJECT n_seed) = eps
~$property_magic_cv_named_clone_history(S,n_seed,porigin_named)
pclosurecache.OBJECT = n_closure /\ pclosurecache.FUNCTION = porigin_named
n_current_cache = $nabs($(|S.CLOSURECACHES| - 1))
$property_magic_cv_named_clone_history(S,n_closure,porigin_named)
~$property_magic_cv_named_clone_history(S,|S.OBJECTS|,porigin_named)
~$property_magic_cv_named_clone_history(S,n_closure,pmethoddesc.FUNCTION.ORIGIN)
~$property_magic_cv_named_clone_history(S[.CLOSURECACHES = eps],n_closure,porigin_named)
S_wrapped_seed = S[.OBJECTS[n_seed] = CONSTANTCLOSURE porigin_named (NAMEDCLOSURE porigin_named)]
$closure_cache_records_valid(S_wrapped_seed)
~$property_magic_cv_named_clone_history(S_wrapped_seed,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_wrapped_seed,n_closure)
S_real_seed = S[.OBJECTS[n_seed] = REALCLOSURE porigin_named eps eps]
~$property_magic_cv_named_clone_history(S_real_seed,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_real_seed,n_closure)
S_wrong_origin = S[.OBJECTS[n_seed] = NAMEDCLOSURE pmethoddesc.FUNCTION.ORIGIN]
~$property_magic_cv_named_clone_history(S_wrong_origin,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_wrong_origin,n_closure)
S_self_source = S[.CLOSURECACHES[n_current_cache] = pclosurecache[.SOURCE = (n_closure)]]
~$property_magic_cv_named_clone_history(S_self_source,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_self_source,n_closure)
S_forward_source = S[.CLOSURECACHES[n_current_cache] = pclosurecache[.SOURCE = (|S.OBJECTS|)]]
~$property_magic_cv_named_clone_history(S_forward_source,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_forward_source,n_closure)
S_wrong_source = S[.CLOSURECACHES[n_current_cache] = pclosurecache[.SOURCE = (n_receiver)]]
~$property_magic_cv_named_clone_history(S_wrong_source,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_wrong_source,n_closure)
S_missing_seed = S[.CLOSURECACHES = S.CLOSURECACHES[1:n_current_cache]]
~$property_magic_cv_named_clone_history(S_missing_seed,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_missing_seed,n_closure)
S_private_seed = S[.CLOSURECACHES[0] = pclosurecache_seed[.CACHE = (CACHE_PRIVATE n_seed)]]
~$property_magic_cv_named_clone_history(S_private_seed,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_private_seed,n_closure)
S_scoped_seed = S[.CLOSURECACHES[0] = pclosurecache_seed[.SCOPE = (BIND_CLASS pmethoddesc.OWNER)]]
~$property_magic_cv_named_clone_history(S_scoped_seed,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_scoped_seed,n_closure)
S_unknown_seed = S[.CLOSURECACHES[0] = pclosurecache_seed[.CACHE = eps]]
~$property_magic_cv_named_clone_history(S_unknown_seed,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_unknown_seed,n_closure)
S_duplicate_seed = S[.CLOSURECACHES = [pclosurecache_seed] ++ S.CLOSURECACHES]
~$property_magic_cv_namedclosure(S_duplicate_seed,n_closure)
S_reordered = S[.CLOSURECACHES = [pclosurecache] ++ S.CLOSURECACHES[0:n_current_cache]]
~$property_magic_cv_namedclosure(S_reordered,n_closure)
~$property_empty_rv_kind(S[.RESULT = KNOWN (POBJECT n_seed)],S.OBJECTS[n_closure])
~$property_empty_rv_kind(S_wrapped_seed,S.OBJECTS[n_closure])
~$property_empty_rv_ready(S_wrapped_seed,ppropertyempty)
'''.strip().splitlines()

SINGLE = r'''
pclosurecache.SOURCE = (n_seed)
S.CLOSURECACHES = [pclosurecache_seed,pclosurecache]
'''.strip().splitlines()

CHAIN = r'''
pclosurecache.SOURCE = (n_middle)
$closure_cache_at(S.CLOSURECACHES,n_middle) = (pclosurecache_middle)
pclosurecache_middle.OBJECT = n_middle /\ pclosurecache_middle.FUNCTION = porigin_named
pclosurecache_middle.SOURCE = (n_seed)
pclosurecache_middle.SCOPE = (BIND_UNSCOPED) /\ pclosurecache_middle.CACHE = (CACHE_SHARED)
S.OBJECTS[n_middle] = NAMEDCLOSURE porigin_named
~((HOBJECT n_middle) <- S.ALLOCATIONS)
$heap_owners($heap_graph(S),HOBJECT n_middle) = 0
$lookup(S.ENV,$ptascii("middle")) = (n_middle_cell)
S.STORE[n_middle_cell] = DEFINED PNULL
$property_magic_cv_named_clone_history(S,n_middle,porigin_named)
'''.strip().splitlines()

CHAIN_TAIL = r'''
S.CLOSURECACHES = [pclosurecache_seed,pclosurecache_middle,pclosurecache]
S_wrapped_middle = S[.OBJECTS[n_middle] = CONSTANTCLOSURE porigin_named (NAMEDCLOSURE porigin_named)]
$closure_cache_records_valid(S_wrapped_middle)
~$property_magic_cv_named_clone_history(S_wrapped_middle,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_wrapped_middle,n_closure)
S_middle_self = S[.CLOSURECACHES[1] = pclosurecache_middle[.SOURCE = (n_middle)]]
~$property_magic_cv_named_clone_history(S_middle_self,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_middle_self,n_closure)
'''.strip().splitlines()

AUTHORITY = [check for check in named.AUTHORITY
             if check.lstrip('~') != '$property_magic_cv_namedclosure(S_clone,n_clone)'
             and not check.lstrip('~').startswith('$property_empty_rv_kind(S_clone,')]
AUTHORITY += [
    '$property_magic_cv_namedclosure(S_clone,n_clone)',
    '$property_empty_rv_kind(S_clone,S_clone.OBJECTS[n_clone]) /\\ $property_empty_rv_ready(S_clone,ppropertyempty)',
]

CASES = {}
for index, row in enumerate(ROWS):
    checks = FRONT + (CHAIN if index == 0 else [SINGLE[0]]) + ROOT
    checks += CHAIN_TAIL if index == 0 else [SINGLE[1]]
    checks += AUTHORITY + ([
        '$property_magic_cv_empty_source(S,ppropertyempty.SITE,ppropertyempty.LINE)',
        '$property_magic_cv_result_supported(S,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)',
        '~$property_magic_cv_result_supported(S_wrapped_seed,ppropertyempty.SITE,ppropertyempty.LINE,true,S.RESULT)',
    ] if index == 0 else ['~$property_magic_cv_source(S,ppropertyempty.SITE,ppropertyempty.LINE)'])
    checks += warmed(named.LIFETIME)
    if index == 1:
        checks += warmed(named.THROW)
    checks += [check.replace('(PINT 2)', '(PINT 3)') for check in named.DONE]
    checks += [
        'S_done.STORE[n_destination] = DEFINED (PBOOL false)' if index == 0
        else 'S_done.STORE[n_destination] = DEFINED (PINT 42)',
        '$owning_review_output(S_done.EVENTS) = $ptascii("' + base64.b64decode(row['stdout_template_base64']).decode() + '")',
    ]
    CASES[row['id']] = {'source': row['source'], 'stage': named.STAGE, 'checks': checks}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(named.__file__), named.CATALOGUE,
                  Path(named.owning.__file__), named.owning.CATALOGUE,
                  Path(named.literal.__file__), named.literal.CATALOGUE),
                 runner_flags=('--sl',), fixture_renderer=named.literal.render)
