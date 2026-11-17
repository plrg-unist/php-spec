#!/usr/bin/env python3
"""Independent NULL tags, quiet comparisons, and operand-domain boundaries."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_null_equality_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']

base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
siblings = ['PINT 0', 'PINT 0', 'PINT 1', 'PINT 1', 'PFLOAT 0',
            'PFLOAT 9223372036854775808', 'PFLOAT 9218868437227405312',
            'PFLOAT 18442240474082181120', 'PFLOAT n_bits_8', 'PFLOAT n_bits_9',
            'PBOOL false', 'PBOOL false', 'PBOOL true', 'PBOOL true', 'PNULL', 'PFLOAT n_bits_15']
results = ['true', 'false', 'true', 'false', 'true', 'false', 'false', 'true',
           'false', 'true', 'true', 'false', 'true', 'false', 'true', 'false']
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
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {result})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PBOOL {result},CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
            f'S.STORE[n_cell_{index}] = DEFINED (PBOOL {result})']
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

named = base + ['pfunction.ENV.NAMESPACE = $ptascii("NullEquality288")', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, side, sibling, truth, value in [(3, 1, 'PBOOL false', 'true', '1'),
                                         (4, 0, 'PFLOAT n_bits_nan', 'false', '0')]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
              f'porigin_compare_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
              f'porigin_null_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD {side}])',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_null_{index}) = (PNULL)',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD {1-side}])) = ({sibling})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_compare_{index}) = (PBOOL {truth})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT {value})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
              f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
              f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
              rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
named += ['$pfcast_nan(PFLOAT n_bits_nan)',
          'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base288"),$ptascii("E_WARNING")),($ptascii("One288"),$ptascii("E_ERROR")),($ptascii("Nan288"),$ptascii("Other288"))]]',
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
quiet_defaults = [(f'NULL == {zero}', 'true'), (f'({chain}) == NULL', 'true'),
                  (f'NULL != (-({chain}))', 'false'), (f'((bool)({chain})) == NULL', 'true'),
                  (f'NULL != {truth}', 'true'), (f'NULL == {nan}', 'false'),
                  (f'{nan} != NULL', 'true'), (f'NULL == ({truth} ? NULL : true)', 'true')]
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, (_, result) in enumerate(quiet_defaults):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {result})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
              f'S.STORE[n_quiet_{index}] = DEFINED (PBOOL {result})']
quiet += ['S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
          'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
refused = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6']
for index in range(6):
    admitted = {0: 'PBOOL false', 1: 'PINT 1', 2: 'PBOOL false', 4: 'PBOOL true'}.get(index)
    refused += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
                (f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({admitted})'
                 if admitted is not None else
                 f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps'),
                (f'$lossy_optional_integer_deferred(S,pfunction,{index})' if admitted is not None else
                 f'~$lossy_optional_integer_deferred(S,pfunction,{index})')]
negative_defaults = [f'NULL < {zero}', f'{truth} <=> NULL', f'NULL === {zero}',
                     f'NULL != ("0" ?? false)', f'(true ? NULL : false) == {zero}', f'NULL == (!{nan})']
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
         '-- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-null-equality-wrapper-raw-tagged-results': {
        'source': ROWS['deferred-null-equality-wrapper-raw-tagged-results']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 16 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'deferred-null-equality-wrapper-named-remaining-recipients': {
        'source': ROWS['deferred-null-equality-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if pfunction.ENV.NAMESPACE = $ptascii("NullEquality288") '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'deferred-null-equality-wrapper-derived-quiet-handler': {
        'source': ('<?php function quietHandler288($errno,$message,$file,$line) { echo "unexpected-warning|"; } '
                   'function quietDefaults288(' + ', '.join(f'$p{i}=({expression})' for i,(expression,_) in enumerate(quiet_defaults)) + ') {} '
                   'set_error_handler("quietHandler288"); quietDefaults288();'),
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'deferred-null-equality-wrapper-current-unprojected-kinds-operators': {
        'source': '<?php function refused288(' + ', '.join(f'$p{i}=({expression})' for i,expression in enumerate(negative_defaults)) + ') {} refused288();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 6', 'checks': refused},
}

if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
