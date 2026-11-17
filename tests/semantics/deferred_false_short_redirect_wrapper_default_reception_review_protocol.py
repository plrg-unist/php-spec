#!/usr/bin/env python3
"""Independent folded-false redirect tags, private conversion and composition."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_false_short_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]', 'S.POOLS = [ppool]']
for index, value in enumerate(values):
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = ((PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2]),expression_right_{index},false,z_{index}))',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = (PBOOL false)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD 0]) = eps',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_0[.VALUE = PBOOL false])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,0)',
    'S_wrong_bits = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_bits,S_wrong_bits.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_bits,pfunction,3)',
    'S_left_pool = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) PNULL)] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_left_pool,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_left_pool,pfunction,0)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['S.SOURCES = [pcunit]', '$default_at(pfunction.DEFAULTS,3) = (pdefault)',
    'pdefault.ORIGIN = PORIGIN n_unit pcpath_default',
    'pcpath_short = pcpath_default ++ [PCFIELD 0]',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit pcpath_short) = (PFLOAT 9223372036854775808)',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault.ORIGIN) = (PINT 0)',
    '$lossy_optional_integer_deferred(S,pfunction,3)', '$default_cache_owner(S) = (CACHE_SHARED)',
    'pdefaultcache = {ORIGIN pdefault.ORIGIN,VALUE PINT 0,CLASS PVSCALAR}',
    '$default_current_cache(S,pdefault.ORIGIN) = (pdefaultcache)',
    '$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[3].NAME) = (n_private)',
    'S.STORE[n_private] = DEFINED (PINT 0)',
    r'~(n_private <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private) = 1',
    '$default_at(pfunction.DEFAULTS,1) = (pdefault_bool)',
    'pdefault_bool.ORIGIN = PORIGIN n_unit pcpath_bool',
    '$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_bool ++ [PCFIELD 0])) = (PBOOL false)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache[.VALUE = PFLOAT 9223372036854775808])]',
    '$default_caches_valid(S_wrong_tag,S_wrong_tag.DEFAULTCACHE)', '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,3)',
    'S_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_short ++ [PCFIELD 2]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_deferred_bindings(S_source,pfunction.ENV,pdefault.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_source,pfunction,3)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,pdefault.ORIGIN) = (pdefaultcache)',
    r'~((HCELL n_private) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private) = 0',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
truth = f'(!{false})'
selected = f'({truth} ? NULL : false)'
nan = f'(NAN + ({chain}))'
quiet_defaults = [(f'false ?: (false ?: {false})', 'PBOOL false'),
                  (f'false ?: (false ?: {nan})', 'PFLOAT n_nan'),
                  (f'false ?: (NULL ?? {selected})', 'PNULL')]
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 3', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, (_, value) in enumerate(quiet_defaults):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
        f'S.STORE[n_quiet_{index}] = DEFINED ({value})']
quiet += ['$pfcast_nan(PFLOAT n_nan)', 'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
    'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
expressions = [f'false ?: (!{nan})', f'false ?: (+{selected})', f'false ?: ((string){false})', f'true ?: {false}']
boundary = base + ['|pfunction.SIGNATURE.PARAMETERS| = 4']
for index in range(4):
    boundary += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ' + ('(PBOOL true)' if index == 3 else 'eps'),
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-false-short-redirect-independent-raw-tags': {'source': ROWS['deferred-false-short-redirect-wrapper-raw-tagged-results']['source'],
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'deferred-false-short-redirect-independent-negative-zero-recipient': {'source': ROWS['deferred-false-short-redirect-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
            '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) -- if pfunction.ENV.NAMESPACE = $ptascii("FalseRedirect296") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 5 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'deferred-false-short-redirect-independent-nested-quiet': {
        'source': '<?php function quietHandler296($e,$m,$f,$l) { echo "unexpected-warning|"; } function quietNull296(' + ', '.join(f'$p{i}=({e})' for i,(e,_) in enumerate(quiet_defaults)) + ') {} set_error_handler("quietHandler296"); quietNull296(); quietNull296();',
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'deferred-false-short-redirect-independent-current-boundaries': {
        'source': '<?php function refused296(' + ', '.join(f'$p{i}=({e})' for i,e in enumerate(expressions)) + ') {} refused296();',
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 4 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': boundary},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
