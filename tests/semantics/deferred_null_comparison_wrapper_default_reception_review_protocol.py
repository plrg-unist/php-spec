#!/usr/bin/env python3
"""Independent NULL order, raw result tags, and quiet comparison boundaries."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_null_comparison_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
siblings = ['PINT $(-1)', 'PINT $(-1)', 'PINT 0', 'PFLOAT 0', 'PBOOL true',
            'PBOOL false', 'PBOOL false', 'PBOOL true', 'PFLOAT n_bits_8', 'PFLOAT n_bits_9',
            'PFLOAT 9223372036854775808', 'PINT $(-1)', 'PFLOAT 9218868437227405312',
            'PFLOAT 18442240474082181120', 'PNULL', 'PFLOAT n_bits_15']
results = ['PBOOL true', 'PBOOL false', 'PBOOL true', 'PBOOL true', 'PBOOL false',
           'PBOOL false', 'PBOOL true', 'PBOOL false', 'PINT $(-1)', 'PINT 1',
           'PINT 0', 'PINT 1', 'PBOOL true', 'PBOOL true', 'PINT 0', 'PBOOL true']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 16', 'S.CODE = [pcode]',
              'S.SOURCES = [pcunit]', 'S.POOLS = [ppool]']
for index, (sibling, result) in enumerate(zip(siblings, results)):
    side = index % 2
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
            f'porigin_null_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {side}])',
            f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_null_{index})',
            f'$compiled_read(S,porigin_null_{index}) = (PNULL)',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_null_{index}) = (PNULL)',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {1-side}])) = ({sibling})',
            f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {result},CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
            f'S.STORE[n_cell_{index}] = DEFINED ({result})']
    if 'n_bits_' in sibling:
        raw.append(f'$pfcast_nan({sibling})')
raw += [
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_14 ++ [PCFIELD 1])) = (NExprTernary expression_cond_14 expression_chosen_14 expression_unused_14 metadata_14)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,PORIGIN n_unit (pcpath_14 ++ [PCFIELD 1]))',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_14 ++ [PCFIELD 1,PCFIELD 0])) = (PBOOL true)',
    'S_false_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PBOOL false))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_false_pool,pfunction.ENV,porigin_null_0) = eps',
    '$lossy_optional_integer_deferred_value_at(S_false_pool,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_zero_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PINT 0))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_zero_pool,pfunction.ENV,porigin_null_0) = eps',
    '$lossy_optional_integer_deferred_value_at(S_zero_pool,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_wrong_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) (NScalarInt (INTEGER 0) eps))] ++ pcunit.OCCURRENCES)]]]',
    '$lossy_optional_integer_deferred_value_at(S_wrong_source,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 1])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,0)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]
for index in range(16):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['pfunction.ENV.NAMESPACE = $ptascii("NullComparison289")', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, side, sibling, raw_value, value in [(3, 0, 'PFLOAT n_bits_nan', 'PINT $(-1)', '$(-1)'),
                                             (4, 1, 'PFLOAT n_bits_nan', 'PBOOL true', '1')]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
              f'porigin_compare_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
              f'porigin_null_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD {side}])',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_null_{index}) = (PNULL)',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD {1-side}])) = ({sibling})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_compare_{index}) = ({raw_value})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT {value})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
              f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
              f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
              rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
named += ['$pfcast_nan(PFLOAT n_bits_nan)',
          'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base289"),$ptascii("E_WARNING")),($ptascii("One289"),$ptascii("E_ERROR")),($ptascii("Nan289"),$ptascii("Other289"))]]',
          '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_4.ORIGIN)',
          '$lossy_optional_integer_deferred_value_at(S,plenv_wrong,pdefault_4.ORIGIN) = eps',
          'S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
          r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in (3, 4):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
truth = f'(!((bool)({chain})))'
zero = f'((int)({chain}))'
nan = f'(NAN + ({chain}))'
negative = f'(-((int)({truth})))'
quiet_defaults = [(f'NULL < {negative}', 'PBOOL true'), (f'{negative} > NULL', 'PBOOL true'),
                  (f'NULL <= {zero}', 'PBOOL true'), (f'(-({chain})) >= NULL', 'PBOOL true'),
                  (f'NULL >= {nan}', 'PBOOL false'), (f'{nan} <= NULL', 'PBOOL false'),
                  (f'NULL <=> {nan}', 'PINT $(-1)'), (f'{nan} <=> NULL', 'PINT 1')]
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, (_, result) in enumerate(quiet_defaults):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
              f'S.STORE[n_quiet_{index}] = DEFINED ({result})']
quiet += ['S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
          'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
refused = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4']
for index in range(4):
    refused += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
                f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
                f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
negative_defaults = [f'NULL < ("0" ?? false)', f'("0" ?? false) <=> NULL',
                     f'NULL >= (!{nan})', f'(!{nan}) > NULL']
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
         '-- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-null-comparison-wrapper-raw-tagged-results': {
        'source': ROWS['deferred-null-comparison-wrapper-raw-tagged-results']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 16 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'deferred-null-comparison-wrapper-named-remaining-recipients': {
        'source': ROWS['deferred-null-comparison-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if pfunction.ENV.NAMESPACE = $ptascii("NullComparison289") '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'deferred-null-comparison-wrapper-derived-quiet-handler': {
        'source': ('<?php function quietHandler289($errno,$message,$file,$line) { echo "unexpected-warning|"; } '
                   'function quietDefaults289(' + ', '.join(f'$p{i}=({expression})' for i,(expression,_) in enumerate(quiet_defaults)) + ') {} '
                   'set_error_handler("quietHandler289"); quietDefaults289();'),
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'deferred-null-comparison-wrapper-current-unprojected-kinds-operators': {
        'source': '<?php function refused289(' + ', '.join(f'$p{i}=({expression})' for i,expression in enumerate(negative_defaults)) + ') {} refused289();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4', 'checks': refused},
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
