#!/usr/bin/env python3
"""Independent selected NULL tags, receipt authority, and quiet boundaries."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_null_selection_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
siblings = ['PINT 0', 'PINT 1', 'PINT $(-1)', 'PBOOL false', 'PFLOAT n_bits_4',
            'PFLOAT n_bits_5', 'PBOOL true', 'PFLOAT 0', 'PBOOL false',
            'PINT $(-1)', 'PNULL', 'PINT 0']
results = ['PBOOL true', 'PBOOL true', 'PBOOL true', 'PBOOL true', 'PINT $(-1)',
           'PINT 1', 'PBOOL false', 'PBOOL true', 'PBOOL false', 'PBOOL false',
           'PBOOL true', 'PBOOL true']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 12', 'S.CODE = [pcode]',
              'S.SOURCES = [pcunit]', 'S.POOLS = [ppool]']
for index, (sibling, result) in enumerate(zip(siblings, results)):
    side = 0 if index == 11 else index % 2
    selected = 'PBOOL false' if index == 11 else 'PNULL'
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
            f'porigin_selection_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {side}])',
            f'$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_selection_{index})',
            f'$compiled_read(S,porigin_selection_{index}) = ({selected})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selection_{index}) = ({selected})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD {1-side}])) = ({sibling})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({result})',
            f'$lossy_optional_integer_deferred(S,pfunction,{index})',
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {result},CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
            f'S.STORE[n_cell_{index}] = DEFINED ({result})']
    if 'n_bits_' in sibling:
        raw.append(f'$pfcast_nan({sibling})')
raw += ['S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 1])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(12):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['pfunction.ENV.NAMESPACE = $ptascii("NullSelection290")',
                'S.CODE = [pcode]', 'S.SOURCES = [pcunit]', 'S.POOLS = [ppool]',
                '$default_cache_owner(S) = (CACHE_SHARED)']
for index, side, chosen, condition in [(1, 0, 1, 'true'), (2, 1, 2, 'false'), (3, 0, 2, 'false')]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_default_{index}',
              f'pcpath_selection_{index} = pcpath_default_{index} ++ [PCFIELD 0,PCFIELD {side}]',
              f'porigin_selection_{index} = PORIGIN n_unit pcpath_selection_{index}',
              f'porigin_condition_{index} = PORIGIN n_unit (pcpath_selection_{index} ++ [PCFIELD 0])',
              f'pcpath_chosen_{index} = pcpath_selection_{index} ++ [PCFIELD {chosen}]',
              f'porigin_chosen_{index} = PORIGIN n_unit pcpath_chosen_{index}',
              f'$compiled_read(S,porigin_selection_{index}) = (PNULL)',
              f'$pool_value(S.POOLS,porigin_chosen_{index}) = (PNULL)',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selection_{index}) = (PNULL)',
              f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selection_{index}) = ((porigin_condition_{index},porigin_chosen_{index}))',
              f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})']
    for tag, forged in [('false', 'PBOOL false'), ('zero', 'PINT 0')]:
        named += [f'S_leaf_{tag}_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_chosen_{index} ({forged}))] ++ ppool.CONSTANTS)]]]',
                  f'$lossy_optional_integer_deferred_value_at(S_leaf_{tag}_{index},pfunction.ENV,porigin_chosen_{index}) = (PNULL)',
                  f'$lossy_optional_integer_pruned_ternary(S_leaf_{tag}_{index},pfunction.ENV,porigin_selection_{index}) = eps']
        if index < 3:
            named += [f'~$lossy_optional_integer_deferred_bindings(S_leaf_{tag}_{index},pfunction.ENV,pdefault_{index}.ORIGIN)',
                      f'~$lossy_optional_integer_deferred(S_leaf_{tag}_{index},pfunction,{index})']
    if index < 3:
        skipped = 3 - chosen
        named += [f'pcpath_unused_{index} = pcpath_selection_{index} ++ [PCFIELD {skipped}]',
                  f'$call_name_count(pcode.NAMES,pcpath_unused_{index}) = 0',
                  f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,PORIGIN n_unit pcpath_unused_{index})']
    else:
        named += ['S_absent = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_selection_3 ++ [PCFIELD 1]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
                  '$lossy_optional_integer_pruned_ternary(S_absent,pfunction.ENV,porigin_selection_3) = eps']
named += ['$default_at(pfunction.DEFAULTS,4) = (pdefault_4)',
          'pdefault_4.ORIGIN = PORIGIN n_unit pcpath_default_4',
          'porigin_selection_4 = PORIGIN n_unit (pcpath_default_4 ++ [PCFIELD 0,PCFIELD 1])',
          '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selection_4) = (PNULL)',
          '$lossy_optional_integer_deferred(S,pfunction,4)',
          'pdefaultcache_4 = {ORIGIN pdefault_4.ORIGIN,VALUE PINT 1,CLASS PVSCALAR}',
          '$default_current_cache(S,pdefault_4.ORIGIN) = (pdefaultcache_4)',
          '$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[4].NAME) = (n_private_4)',
          'S.STORE[n_private_4] = DEFINED (PINT 1)',
          r'~(n_private_4 <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_4) = 1',
          'S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
          '$default_cache_at(S_done.DEFAULTCACHE,pdefault_4.ORIGIN) = (pdefaultcache_4)',
          r'~((HCELL n_private_4) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_4) = 0',
          r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
zero = f'((int)({chain}))'
nan = f'(NAN + ({chain}))'
quiet_defaults = [f'(true ? NULL : NAN) == {zero}', f'{nan} <=> (false ?: NULL)',
                  f'(false ? NAN : NULL) < {zero}']
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 3', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, value in enumerate(['PBOOL true', 'PINT 1', 'PBOOL false']):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
              f'S.STORE[n_quiet_{index}] = DEFINED ({value})']
quiet += ['S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
          'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
boundary = base + ['|pfunction.SIGNATURE.PARAMETERS| = 3']
for index in range(2):
    boundary += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
                 f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
                 f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
boundary += ['$default_at(pfunction.DEFAULTS,2) = (pdefault_2)',
             'pdefault_2.ORIGIN = PORIGIN n_unit pcpath_2',
             'porigin_selection_2 = PORIGIN n_unit (pcpath_2 ++ [PCFIELD 0])',
             '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selection_2) = (PINT 1)',
             '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_selection_2) = eps',
             '~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_2.ORIGIN)',
             '~$lossy_optional_integer_deferred(S,pfunction,2)']
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
         '-- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-null-selection-wrapper-raw-tagged-results': {'source': ROWS['deferred-null-selection-wrapper-raw-tagged-results']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 12 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'deferred-null-selection-wrapper-named-receipt-boundaries': {'source': ROWS['deferred-null-selection-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if pfunction.ENV.NAMESPACE = $ptascii("NullSelection290") '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'deferred-null-selection-wrapper-derived-quiet-handler': {
        'source': ('<?php function quietHandler290($errno,$message,$file,$line) { echo "unexpected-warning|"; } '
                   'function quietDefaults290(' + ', '.join(f'$p{i}=({expression})' for i,expression in enumerate(quiet_defaults)) + ') {} '
                   'set_error_handler("quietHandler290"); quietDefaults290();'),
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'deferred-null-selection-wrapper-current-unprojected-kinds': {
        'source': f'<?php function refused290($p0=((true ? "0" : NULL) == {zero}),$p1=((!{nan}) ? NULL : false),$p2=((true ? 1 : Missing290) == {zero})) {{}} refused290();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3', 'checks': boundary},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
