#!/usr/bin/env python3
"""Check shared literal-clone history and quiet Get ownership transfers."""
import argparse
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol
import magic_property_realclosure_quiet_get_protocol as literal
import magic_property_arrow_quiet_get_protocol as arrow

CATALOGUE = Path(__file__).with_name('magic_property_clone_quiet_get_cases.json')
ROWS = json.loads(CATALOGUE.read_text())['cases']
for row in ROWS:
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']


def clone_checks(checks):
    result = []
    replaced = 0
    for check in checks:
        if check == 'pclosurecache.OBJECT = n_closure /\\ pclosurecache.FUNCTION = porigin_closure /\\ pclosurecache.SOURCE = eps':
            replaced += 1
            result += ['pclosurecache.OBJECT = n_closure /\\ pclosurecache.FUNCTION = porigin_closure',
                       'pclosurecache.SOURCE = (n_source)']
        else:
            result.append(check)
    assert replaced == 1
    return result


HISTORY = r'''
$property_magic_cv_literal_history(S,n_closure,porigin_closure)
$closure_cache_at(S.CLOSURECACHES,n_source) = (pclosurecache_source)
S.OBJECTS[n_source] = REALCLOSURE porigin_closure pitem_source* pstaticcell_source*
~((HOBJECT n_source) <- S.ALLOCATIONS)
$(n_source < n_closure)
n_current_cache = $nabs($(|S.CLOSURECACHES| - 1))
pclosurecache_prefix* = S.CLOSURECACHES[0:n_current_cache]
S.CLOSURECACHES = pclosurecache_prefix* ++ [pclosurecache]
~$property_magic_cv_literal_history(S,|S.OBJECTS|,porigin_closure)
~$property_magic_cv_literal_history(S,n_closure,pmethoddesc.FUNCTION.ORIGIN)
S_named = S[.OBJECTS[n_source] = NAMEDCLOSURE porigin_closure]
$closure_cache_records_valid(S_named)
~$property_magic_cv_literal_history(S_named,n_closure,porigin_closure)
~$quiet(S_named,n_closure)
S_wrapped = S[.OBJECTS[n_source] = CONSTANTCLOSURE porigin_closure (REALCLOSURE porigin_closure pitem_source* pstaticcell_source*)]
$closure_cache_records_valid(S_wrapped)
~$property_magic_cv_literal_history(S_wrapped,n_closure,porigin_closure)
~$quiet(S_wrapped,n_closure)
S_empty = S[.OBJECTS[n_source] = REALCLOSURE porigin_closure eps eps]
$closure_cache_records_valid(S_empty)
$property_magic_cv_literal_history(S_empty,n_closure,porigin_closure)
$quiet(S_empty,n_closure)
S_missing = S[.CLOSURECACHES = [pclosurecache]]
~$property_magic_cv_literal_history(S_missing,n_closure,porigin_closure)
~$quiet(S_missing,n_closure)
S_reordered = S[.CLOSURECACHES = [pclosurecache] ++ pclosurecache_prefix*]
$property_magic_cv_literal_history(S_reordered,n_closure,porigin_closure)
~$closure_cache_records_valid(S_reordered)
~$quiet(S_reordered,n_closure)
S_duplicate = S[.CLOSURECACHES = S.CLOSURECACHES ++ [pclosurecache]]
$property_magic_cv_literal_history(S_duplicate,n_closure,porigin_closure)
~$closure_cache_records_valid(S_duplicate)
~$quiet(S_duplicate,n_closure)
S_forward = S[.CLOSURECACHES = pclosurecache_prefix* ++ [pclosurecache[.SOURCE = (n_closure)]]]
~$property_magic_cv_literal_history(S_forward,n_closure,porigin_closure)
~$quiet(S_forward,n_closure)
'''.strip().splitlines()

FN_CHAIN = r'''
$lookup(S.ENV,$ptascii("seed")) = (n_seed_cell)
$lookup(S.ENV,$ptascii("middle")) = (n_middle_cell)
S.STORE[n_seed_cell] = DEFINED PNULL /\ S.STORE[n_middle_cell] = DEFINED PNULL
pclosurecache_source.SOURCE = (n_seed)
$closure_cache_at(S.CLOSURECACHES,n_seed) = (pclosurecache_seed)
pclosurecache_seed.SOURCE = eps
S.CLOSURECACHES = [pclosurecache_seed,pclosurecache_source,pclosurecache]
~((HOBJECT n_seed) <- S.ALLOCATIONS)
S.OBJECTS[n_seed] = REALCLOSURE porigin_closure eps eps
$property_magic_cv_literal_history(S,n_seed,porigin_closure)
'''.strip().splitlines()

ARROW_CHAIN = r'''
$lookup(S.ENV,$ptascii("seed")) = (n_seed_cell)
S.STORE[n_seed_cell] = DEFINED PNULL
pclosurecache_source.SOURCE = eps
S.CLOSURECACHES = [pclosurecache_source,pclosurecache]
'''.strip().splitlines()

CASES = {
    ROWS[0]['id']: {
        'source': ROWS[0]['source'],
        'stage': literal.CASES['realclosure-cv-coalesce-literal-result-owner']['stage'],
        'checks': clone_checks(literal.BINARY) + [
            check.replace('$quiet', '$property_magic_cv_realclosure') for check in HISTORY
        ] + FN_CHAIN,
    },
    ROWS[1]['id']: {
        'source': ROWS[1]['source'],
        'stage': arrow.CASES['arrow-private-coalesce-assignment-implicit-captured-owner']['stage'],
        'checks': clone_checks(arrow.ASSIGN) + [
            check.replace('$quiet', '$property_magic_cv_arrow') for check in HISTORY
        ] + ARROW_CHAIN,
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append', choices=sorted(CASES))
    args = parser.parse_args()
    protocol.run({name: case for name, case in CASES.items() if not args.case or name in args.case},
                 (Path(__file__), CATALOGUE, Path(literal.__file__), literal.CATALOGUE,
                  Path(arrow.__file__), arrow.CATALOGUE), runner_flags=('--sl',))
