#!/usr/bin/env python3
"""Independent NULL-left RHS demand, exact tags, and negative-zero transport."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_null_coalesce_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 0', 'PFLOAT n_nan',
          'PNULL', 'PBOOL true', 'PINT 1']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]']
for index, value in enumerate(values):
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = (PNULL)',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])) = ({value})',
            f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = eps',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
            f'S.STORE[n_cell_{index}] = DEFINED ({value})']
raw += ['$pfcast_nan(PFLOAT n_nan)',
        'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_5[.VALUE = PBOOL false])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,5)',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['pfunction.ENV.NAMESPACE = $ptascii("NullCoalesce293")',
                'S.CODE = [pcode]', 'S.SOURCES = [pcunit]',
                '$default_cache_owner(S) = (CACHE_SHARED)']
for index, raw_value, value in [(1, 'PBOOL false', '0'), (2, 'PINT 1', '1')]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
              f'pcpath_coalesce_{index} = pcpath_{index} ++ [PCFIELD 0]',
              f'porigin_coalesce_{index} = PORIGIN n_unit pcpath_coalesce_{index}',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_coalesce_{index} ++ [PCFIELD 0])) = (PNULL)',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_coalesce_{index} ++ [PCFIELD 1])) = ({raw_value})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_coalesce_{index}) = ({raw_value})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
              f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
              f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
              rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1',
              f'S_wrong_rhs_{index} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_coalesce_{index} ++ [PCFIELD 1]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
              f'~$lossy_optional_integer_deferred_bindings(S_wrong_rhs_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
              f'~$lossy_optional_integer_deferred(S_wrong_rhs_{index},pfunction,{index})']
named += ['plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base293"),$ptascii("E_ERROR")),($ptascii("One293"),$ptascii("E_ERROR"))]]',
          '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_2.ORIGIN)',
          'S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
          r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in (1,2):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
selected = f'(!{false} ? NULL : false)'
nan = f'(NAN + ({chain}))'
negative_zero = base + ['|pfunction.SIGNATURE.PARAMETERS| = 1',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault)',
    'pdefault.ORIGIN = PORIGIN n_unit pcpath',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath ++ [PCFIELD 0])) = (PNULL)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath ++ [PCFIELD 1])) = (PFLOAT 9223372036854775808)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PFLOAT 9223372036854775808)',
    '$lossy_optional_integer_deferred(S,pfunction,0)',
    '$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[0].NAME) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (PFLOAT 9223372036854775808)',
    'S_done = $drive_steps(S,3000)', 'S_done.COMPLETION = NORMAL',
    'S_done.EVENTS = eps', '$heap_valid($heap_graph(S_done))']
boundary = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4']
for index in (0,2,3):
    boundary += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
                 f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
                 f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
boundary += ['$default_at(pfunction.DEFAULTS,1) = (pdefault_1)',
             '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_1.ORIGIN) = (PBOOL false)',
             '$lossy_optional_integer_deferred(S,pfunction,1)']
negative_defaults = [f'{selected} ?? (!{nan})', f'{false} ?? (!{nan})',
                     f'{selected} ?? "x"', f'NULL ?? ((int)(!{false}))']
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
         '-- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-null-coalesce-wrapper-raw-tagged-results': {'source': ROWS['deferred-null-coalesce-wrapper-raw-tagged-results']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'deferred-null-coalesce-wrapper-named-independent-boundaries': {'source': ROWS['deferred-null-coalesce-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if pfunction.ENV.NAMESPACE = $ptascii("NullCoalesce293") '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'deferred-null-coalesce-wrapper-derived-negative-zero': {
        'source': f'<?php function negativeZero293($p=({selected} ?? (-((float)(+(E_WARNING === E_ERROR)))))) {{}} negativeZero293();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 1 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': negative_zero},
    'deferred-null-coalesce-wrapper-demand-and-current-boundaries': {
        'source': '<?php function refused293(' + ', '.join(f'$p{i}=({expression})' for i,expression in enumerate(negative_defaults)) + ') {} refused293();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4', 'checks': boundary},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
