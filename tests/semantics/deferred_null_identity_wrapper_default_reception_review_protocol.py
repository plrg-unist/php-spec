#!/usr/bin/env python3
"""Independent NULL identity tags, selected roots, and quiet boundaries."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_null_identity_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
siblings = ['PINT 0', 'PINT 0', 'PBOOL false', 'PBOOL true', 'PFLOAT 0',
            'PFLOAT 9223372036854775808', 'PFLOAT n_nan_6', 'PFLOAT n_nan_7',
            'PNULL', 'PNULL', 'PBOOL false', 'PBOOL false']
results = ['false', 'true', 'true', 'false', 'false', 'true', 'false', 'true',
           'true', 'false', 'false', 'true']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 12', 'S.CODE = [pcode]',
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
    if 'n_nan_' in sibling:
        raw.append(f'$pfcast_nan({sibling})')
raw += ['S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 0])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
        'S_wrong_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) (NScalarInt (INTEGER 0) eps))] ++ pcunit.OCCURRENCES)]]]',
        '$lossy_optional_integer_deferred_value_at(S_wrong_source,pfunction.ENV,pdefault_0.ORIGIN) = eps',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(12):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['pfunction.ENV.NAMESPACE = $ptascii("NullIdentity291")',
                'S.CODE = [pcode]', 'S.SOURCES = [pcunit]', 'S.POOLS = [ppool]',
                '$default_cache_owner(S) = (CACHE_SHARED)']
for index, side, sibling in [(3, 0, 'PNULL'), (4, 1, 'PBOOL false')]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
              f'porigin_compare_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
              f'pcpath_null_{index} = pcpath_{index} ++ [PCFIELD 0,PCFIELD {side}]',
              f'porigin_null_{index} = PORIGIN n_unit pcpath_null_{index}',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_null_{index}) = (PNULL)',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD {1-side}])) = ({sibling})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_compare_{index}) = (PBOOL true)',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT 1)',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT 1,CLASS PVSCALAR}}',
              f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
              f'S.STORE[n_private_{index}] = DEFINED (PINT 1)',
              rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
named += ['$compiled_read(S,porigin_null_4) = (PNULL)',
          '$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,porigin_null_4) = ((porigin_cond,porigin_chosen))',
          '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_4.ORIGIN)',
          'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base291"),$ptascii("E_ERROR")),($ptascii("One291"),$ptascii("E_ERROR")),($ptascii("Nan291"),$ptascii("NAN"))]]',
          '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_4.ORIGIN)']
for tag, value in [('false', 'PBOOL false'), ('zero', 'PINT 0')]:
    named += [f'S_root_{tag} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_null_4 ({value}))] ++ ppool.CONSTANTS)]]]',
              f'$lossy_optional_integer_deferred_value_at(S_root_{tag},pfunction.ENV,porigin_null_4) = eps',
              f'~$lossy_optional_integer_deferred_bindings(S_root_{tag},pfunction.ENV,pdefault_4.ORIGIN)',
              f'~$lossy_optional_integer_deferred(S_root_{tag},pfunction,4)']
named += ['S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
          r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in (3, 4):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
zero = f'((int)({chain}))'
truth = f'(!((bool)({chain})))'
nan = f'(NAN + ({chain}))'
quiet_defaults = [(f'NULL === {zero}', 'false'), (f'{nan} !== NULL', 'true'),
                  (f'NULL === ({truth} ? NULL : false)', 'true'),
                  (f'({truth} ? NULL : false) !== NULL', 'false')]
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, (_, result) in enumerate(quiet_defaults):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {result})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
              f'S.STORE[n_quiet_{index}] = DEFINED (PBOOL {result})']
quiet += ['S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
          'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
refused = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4']
for index in range(4):
    refused += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
                f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
                f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
negative_defaults = [f'NULL === ("0" ?? false)', f'("0" ?? false) !== NULL',
                     f'NULL === (!{nan})', f'(!{nan}) !== NULL']
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
         '-- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-null-identity-wrapper-raw-tagged-results': {'source': ROWS['deferred-null-identity-wrapper-raw-tagged-results']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 12 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'deferred-null-identity-wrapper-named-remaining-recipients': {'source': ROWS['deferred-null-identity-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if pfunction.ENV.NAMESPACE = $ptascii("NullIdentity291") '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'deferred-null-identity-wrapper-derived-quiet-handler': {
        'source': ('<?php function quietHandler291($errno,$message,$file,$line) { echo "unexpected-warning|"; } '
                   'function quietDefaults291(' + ', '.join(f'$p{i}=({expression})' for i,(expression,_) in enumerate(quiet_defaults)) + ') {} '
                   'set_error_handler("quietHandler291"); quietDefaults291();'),
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'deferred-null-identity-wrapper-current-unprojected-kinds': {
        'source': '<?php function refused291(' + ', '.join(f'$p{i}=({expression})' for i,expression in enumerate(negative_defaults)) + ') {} refused291();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4', 'checks': refused},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
