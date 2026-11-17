#!/usr/bin/env python3
"""NULL Boolean consumers preserve tags and refuse redirected certificates."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_null_truth_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
results = ['false', 'true', 'false', 'true', 'true', 'false', 'true', 'true']
null_paths = [[0], [0], [0, 2], [0, 2], [0, 0, 0], [0, 0], [0, 0], [0, 0]]
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]']
for index, (result, path) in enumerate(zip(results, null_paths)):
    fields = ','.join(f'PCFIELD {field}' for field in path)
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
            f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
            f'porigin_null_{index} = PORIGIN n_unit (pcpath_{index} ++ [{fields}])',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_null_{index}) = (PNULL)',
            (f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps' if index in (2,3) else
             f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {result})'),
            (f'~$lossy_optional_integer_deferred(S,pfunction,{index})' if index in (2,3) else
             f'$lossy_optional_integer_deferred(S,pfunction,{index})'),
            f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PBOOL {result},CLASS PVSCALAR}}',
            f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
            f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
            f'S.STORE[n_cell_{index}] = DEFINED (PBOOL {result})']
    if index in (2,3):
        raw += [f'porigin_short_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
                f'$compiled_redirect(S,porigin_short_{index}) = ((porigin_null_{index},expression_selected_{index},false,z_redirect_{index}))',
                f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_short_{index}) = eps']
raw += ['S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PINT 0])]',
        '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)',
        '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
        'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
        '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
        'S_done = $drive_steps(S,3000)',
        r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
        r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['pfunction.ENV.NAMESPACE = $ptascii("NullTruth292")',
                'S.CODE = [pcode]', 'S.SOURCES = [pcunit]',
                '$default_cache_owner(S) = (CACHE_SHARED)']
for index, raw_value, value in [(3, 'false', '0'), (4, 'true', '1')]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
              f'porigin_bool_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
              f'pcpath_null_{index} = pcpath_{index} ++ [PCFIELD 0,PCFIELD 0]',
              f'porigin_null_{index} = PORIGIN n_unit pcpath_null_{index}',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_null_{index}) = (PNULL)',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_bool_{index}) = (PBOOL {raw_value})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT {value})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
              f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
              f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
              rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
named += ['$compiled_redirect(S,porigin_null_3) = eps',
          'pcpath_unused_4 = pcpath_null_4 ++ [PCFIELD 2]',
          'porigin_unused_4 = PORIGIN n_unit pcpath_unused_4',
          '$call_name_count(pcode.NAMES,pcpath_unused_4) = 1',
          '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_unused_4)',
          '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_unused_4) = eps',
          'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base292"),$ptascii("E_ERROR")),($ptascii("One292"),$ptascii("E_ERROR"))]]',
          '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_4.ORIGIN)',
          'S_wrong_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_null_4 (NScalarInt (INTEGER 0) eps))] ++ pcunit.OCCURRENCES)]]]',
          '~$lossy_optional_integer_deferred_bindings(S_wrong_source,pfunction.ENV,pdefault_4.ORIGIN)',
          '~$lossy_optional_integer_deferred(S_wrong_source,pfunction,4)',
          'S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
          r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in (3,4):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
              rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
truth = f'(!{false})'
selected = f'({truth} ? NULL : false)'
nan = f'(NAN + ({chain}))'
quiet_defaults = [(f'(bool){selected}', 'false'), (f'!{selected}', 'true'),
                  (f'(bool)({false} ?: {selected})', 'false'), (f'!(!{selected})', 'false')]
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, (_, value) in enumerate(quiet_defaults):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
              f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PBOOL {value})',
              f'$lossy_optional_integer_deferred(S,pfunction,{index})',
              f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
              f'S.STORE[n_quiet_{index}] = DEFINED (PBOOL {value})']
quiet += ['S_done = $drive_steps(S,3000)',
          r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
          'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
refused = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4']
for index in range(4):
    refused += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
                f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
                f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
negative_defaults = [f'(bool){nan}', f'!{nan}', f'+{selected}', f'-{selected}']
stage = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 '
         '-- if pcallcontext.FUNCTION = porigin_function '
         '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-null-truth-wrapper-raw-tagged-results': {'source': ROWS['deferred-null-truth-wrapper-raw-tagged-results']['source'],
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'deferred-null-truth-wrapper-named-remaining-recipients': {'source': ROWS['deferred-null-truth-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
                  '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) '
                  '-- if pfunction.ENV.NAMESPACE = $ptascii("NullTruth292") '
                  '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'deferred-null-truth-wrapper-derived-quiet-handler': {
        'source': ('<?php function quietHandler292($errno,$message,$file,$line) { echo "unexpected-warning|"; } '
                   'function quietDefaults292(' + ', '.join(f'$p{i}=({expression})' for i,(expression,_) in enumerate(quiet_defaults)) + ') {} '
                   'set_error_handler("quietHandler292"); quietDefaults292();'),
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'deferred-null-truth-wrapper-current-unprojected-kinds': {
        'source': '<?php function refused292(' + ', '.join(f'$p{i}=({expression})' for i,expression in enumerate(negative_defaults)) + ') {} refused292();',
        'stage': stage + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4', 'checks': refused},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
