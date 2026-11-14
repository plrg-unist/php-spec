#!/usr/bin/env python3
"""Check named FCC clone ancestry without owning function static storage."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_namedclosure_quiet_get_protocol as named

CATALOGUE = Path(__file__).with_name('magic_property_namedclosure_clone_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

FRONT = []
for check in named.FRONT:
    if check == 'pclosurecache = {OBJECT n_closure,FUNCTION porigin_named,SOURCE eps,SCOPE (BIND_UNSCOPED),CACHE (CACHE_SHARED)}':
        FRONT += [
            r'pclosurecache.OBJECT = n_closure /\ pclosurecache.FUNCTION = porigin_named',
            'pclosurecache.SOURCE = (n_source)',
            r'pclosurecache.SCOPE = (BIND_UNSCOPED) /\ pclosurecache.CACHE = (CACHE_SHARED)',
        ]
    else:
        FRONT.append(check)
assert len(FRONT) == len(named.FRONT) + 2

HISTORY = r'''
$property_magic_cv_named_clone_history(S,n_closure,porigin_named)
$(n_source < n_closure)
S.OBJECTS[n_source] = NAMEDCLOSURE porigin_named
~((HOBJECT n_source) <- S.ALLOCATIONS)
$closure_cache_at(S.CLOSURECACHES,n_source) = (pclosurecache_source)
pclosurecache_source.OBJECT = n_source /\ pclosurecache_source.FUNCTION = porigin_named
pclosurecache_source.SCOPE = (BIND_UNSCOPED) /\ pclosurecache_source.CACHE = (CACHE_SHARED)
n_current_cache = $nabs($(|S.CLOSURECACHES| - 1))
pclosurecache_prefix* = S.CLOSURECACHES[0:n_current_cache]
S.CLOSURECACHES = pclosurecache_prefix* ++ [pclosurecache]
~$property_magic_cv_named_clone_history(S,|S.OBJECTS|,porigin_named)
~$property_magic_cv_named_clone_history(S,n_closure,pmethoddesc.FUNCTION.ORIGIN)
S_wrapped = S[.OBJECTS[n_source] = CONSTANTCLOSURE porigin_named (NAMEDCLOSURE porigin_named)]
$closure_cache_records_valid(S_wrapped)
~$property_magic_cv_named_clone_history(S_wrapped,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_wrapped,n_closure)
S_real = S[.OBJECTS[n_source] = REALCLOSURE porigin_named eps eps]
~$property_magic_cv_named_clone_history(S_real,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_real,n_closure)
S_wrong = S[.OBJECTS[n_source] = NAMEDCLOSURE pmethoddesc.FUNCTION.ORIGIN]
~$property_magic_cv_named_clone_history(S_wrong,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_wrong,n_closure)
S_missing = S[.CLOSURECACHES = [pclosurecache]]
~$property_magic_cv_named_clone_history(S_missing,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_missing,n_closure)
S_reordered = S[.CLOSURECACHES = [pclosurecache] ++ pclosurecache_prefix*]
$property_magic_cv_named_clone_history(S_reordered,n_closure,porigin_named)
~$closure_cache_records_valid(S_reordered)
~$property_magic_cv_namedclosure(S_reordered,n_closure)
S_duplicate = S[.CLOSURECACHES = S.CLOSURECACHES ++ [pclosurecache]]
$property_magic_cv_named_clone_history(S_duplicate,n_closure,porigin_named)
~$closure_cache_records_valid(S_duplicate)
~$property_magic_cv_namedclosure(S_duplicate,n_closure)
S_forward = S[.CLOSURECACHES = pclosurecache_prefix* ++ [pclosurecache[.SOURCE = (n_closure)]]]
~$property_magic_cv_named_clone_history(S_forward,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_forward,n_closure)
S_private = S[.CLOSURECACHES = pclosurecache_prefix* ++ [pclosurecache[.CACHE = (CACHE_PRIVATE n_closure)]]]
$closure_cache_at(S_private.CLOSURECACHES,n_closure) = (pclosurecache_private)
pclosurecache_private.CACHE = (CACHE_PRIVATE n_closure)
~$property_magic_cv_named_clone_history(S_private,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_private,n_closure)
S_scoped = S[.CLOSURECACHES = pclosurecache_prefix* ++ [pclosurecache[.SCOPE = (BIND_CLASS pmethoddesc.OWNER)]]]
~$property_magic_cv_named_clone_history(S_scoped,n_closure,porigin_named)
~$property_magic_cv_namedclosure(S_scoped,n_closure)
'''.strip().splitlines()

CHAIN = r'''
$lookup(S.ENV,$ptascii("seed")) = (n_seed_cell)
$lookup(S.ENV,$ptascii("middle")) = (n_middle_cell)
S.STORE[n_seed_cell] = DEFINED PNULL /\ S.STORE[n_middle_cell] = DEFINED PNULL
pclosurecache_source.SOURCE = (n_seed)
$closure_cache_at(S.CLOSURECACHES,n_seed) = (pclosurecache_seed)
pclosurecache_seed.SOURCE = eps
S.CLOSURECACHES = [pclosurecache_seed,pclosurecache_source,pclosurecache]
~((HOBJECT n_seed) <- S.ALLOCATIONS)
S.OBJECTS[n_seed] = NAMEDCLOSURE porigin_named
~$property_magic_cv_named_clone_history(S,n_seed,porigin_named)
$property_magic_cv_named_clone_history(S,n_source,porigin_named)
'''.strip().splitlines()

SINGLE = r'''
$lookup(S.ENV,$ptascii("seed")) = (n_seed_cell)
S.STORE[n_seed_cell] = DEFINED PNULL
pclosurecache_source.SOURCE = eps
S.CLOSURECACHES = [pclosurecache_source,pclosurecache]
~$property_magic_cv_named_clone_history(S,n_source,porigin_named)
'''.strip().splitlines()

CASES = {
    row['id']: {
        'source': row['source'],
        'stage': named.CASES[named.ROWS[index]['id']]['stage'],
        'checks': FRONT + HISTORY + (CHAIN if index == 0 else SINGLE) + named.LIFETIME
            + named.CASES[named.ROWS[index]['id']]['checks'][-(4 if index == 0 else 5):],
    }
    for index, row in enumerate(ROWS)
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(named.__file__), named.CATALOGUE), runner_flags=('--sl',))
