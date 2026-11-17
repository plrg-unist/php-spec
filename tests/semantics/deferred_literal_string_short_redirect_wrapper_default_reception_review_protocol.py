#!/usr/bin/env python3
"""Literal condition headers, exact cached tags and private recipients."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_literal_string_short_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
bytes_by_index = ['eps', '[48]', 'eps', '[48]', '[48]', 'eps', '[48]', '[48]']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]',
              'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]']
for index, (value, byte_sequence) in enumerate(zip(values, bytes_by_index)):
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'porigin_cond_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} ABSENT expression_right_{index} metadata_{index})',
        f'$origin_node(S.SOURCES,porigin_cond_{index}) = (expression_cond_{index})',
        f'expression_cond_{index} = NScalarString (BYTES text_{index}) metadata_cond_{index}',
        f'$base64(text_{index}) = {byte_sequence}',
        f'$pool_value(S.POOLS,porigin_cond_{index}) = (PSTRING ({byte_sequence}))',
        f'$compiled_precision(S,(porigin_cond_{index})) = (z_precision_{index})',
        f'$compiled_string_value(S,porigin_cond_{index},PSTRING ({byte_sequence})) = PSTRING_CARRIER INTERNED_STRING ({byte_sequence})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD 0]) = eps',
        f'$compiled_read(S,porigin_cond_{index}) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_{index} ++ [PCFIELD 0]) = 0',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_{index}) = 1',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = ((PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2]),expression_right_{index},false,z_{index}))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    '$constant_precision_at(ppool.CONSTANTS,pcpath_1 ++ [PCFIELD 0]) = eps',
    'S_no_precision = S[.DECLARATIONS = eps]',
    '$compiled_precision(S_no_precision,(porigin_cond_1)) = eps',
    '$compiled_string_value(S_no_precision,porigin_cond_1,PSTRING ([48])) = PSTRING ([48])',
    '$lossy_optional_integer_deferred_value_at(S_no_precision,pfunction.ENV,pdefault_1.ORIGIN) = eps',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,3)']
for name, value in [('bytes', 'PSTRING (eps)'),
                    ('interned', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
                    ('request', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([48])')]:
    raw += [f'S_pool_{name} = S[.STRINGDATA = (S.STRINGDATA ++ [[48]])][.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_1 ++ [PCFIELD 0]) ({value}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_pool_{name},pfunction.ENV,pdefault_1.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_pool_{name},pfunction,1)']
for name, text, byte_sequence in [('doublezero', 'MDA=', '[48,48]'), ('nul', 'AA==', '[0]')]:
    raw += [f'expression_{name} = NScalarString (BYTES "{text}") metadata_cond_1',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_1 (NExprTernary expression_{name} ABSENT expression_right_1 metadata_1)), (PCOCCURRENCE (pcpath_1 ++ [PCFIELD 0]) expression_{name})] ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_1 ++ [PCFIELD 0]) (PSTRING ({byte_sequence})))] ++ ppool.CONSTANTS)]]]',
        f'$compiled_string_value(S_{name},porigin_cond_1,PSTRING ({byte_sequence})) = PSTRING_CARRIER INTERNED_STRING ({byte_sequence})',
        f'$compiled_redirect(S_{name},pdefault_1.ORIGIN) = ((PORIGIN n_unit (pcpath_1 ++ [PCFIELD 2]),expression_right_1,false,z_1))',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_1.ORIGIN) = eps']
mutations = {
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'copyflag': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_1 (pcpath_1 ++ [PCFIELD 2]) true)]]]]',
    'condcode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_1 ++ [PCFIELD 0]) z_1 false)] ++ pcode.EXPRESSIONS)]]]',
    'condredirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT (pcpath_1 ++ [PCFIELD 0]) (pcpath_1 ++ [PCFIELD 2]) false)] ++ pcode.REDIRECTS)]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_1 (pcpath_1 ++ [PCFIELD 2,PCFIELD 0]) false)]]]]',
    'source': 'S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_1 ++ [PCFIELD 0]) (NScalarString (BYTES "") metadata_cond_1))] ++ pcunit.OCCURRENCES)]]]',
}
for name, expression in mutations.items():
    raw += [f'S_{name} = {expression}',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_1.ORIGIN) = eps']
raw += ['S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['|pfunction.SIGNATURE.PARAMETERS| = 5', '$default_cache_owner(S) = (CACHE_SHARED)',
                'S.POOLS = [ppool]']
for index, byte_sequence, before, value, valueclass in [(1, 'eps', 'PBOOL false', 0, 'true'),
        (2, '[48]', 'PINT 1', 1, 'true'),
        (3, '[48]', 'PFLOAT 9223372036854775808', 0, 'false')]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'porigin_cond_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 0])',
        f'$pool_value(S.POOLS,porigin_cond_{index}) = (PSTRING ({byte_sequence}))',
        f'$constant_class_at(ppool.CONSTANTS,pcpath_{index} ++ [PCFIELD 0,PCFIELD 0]) = (PVSTRING {valueclass})',
        f'$compiled_string_value(S,porigin_cond_{index},PSTRING ({byte_sequence})) = PSTRING_CARRIER INTERNED_STRING ({byte_sequence})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({before})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT {value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
named += [r'n_private_1 =/= n_private_2 /\ n_private_1 =/= n_private_3 /\ n_private_2 =/= n_private_3',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 9223372036854775808])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,3)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps']
for index in (1, 2, 3):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
named += ['$lookup(S_done.ENV,$ptascii("x298")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
nan = f'(NAN + ({chain}))'
quiet_defaults = [(f'\'\' ?: ("0" ?: {false})', 'PBOOL false'),
                  (f'"0" ?: (\'\' ?: {nan})', 'PFLOAT n_nan')]
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 2', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, (_, value) in enumerate(quiet_defaults):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
        f'S.STORE[n_quiet_{index}] = DEFINED ({value})']
quiet += ['$pfcast_nan(PFLOAT n_nan)', 'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
    'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
expressions = [f'"00" ?: {false}', f'"0.0" ?: {false}', f'"\\0" ?: {false}',
               f'("" . "") ?: {false}', f'((string)false) ?: {false}',
               f'"0" ?: ((string){false})', f'"" ?: []', f'NAN ?: {false}',
               f'"0" ?: (!{nan})']
boundary = base + [f'|pfunction.SIGNATURE.PARAMETERS| = {len(expressions)}']
for index in range(len(expressions)):
    boundary.append(f'~$lossy_optional_integer_deferred(S,pfunction,{index})')
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'literal-string-short-independent-headers-tags': {
        'source': ROWS['deferred-literal-string-short-redirect-wrapper-raw-tagged-results']['source'],
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'literal-string-short-independent-private-recipients': {
        'source': ROWS['deferred-literal-string-short-redirect-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
            '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) -- if pfunction.ENV.NAMESPACE = $ptascii("StringRedirect298") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 5 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'literal-string-short-independent-nested-quiet': {
        'source': '<?php function quietHandler298($e,$m,$f,$l) { echo "unexpected-warning|"; } function quietLiteral298(' + ', '.join(f'$p{i}=({e})' for i,(e,_) in enumerate(quiet_defaults)) + ') {} set_error_handler("quietHandler298"); quietLiteral298(); quietLiteral298();',
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 2 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'literal-string-short-independent-current-boundaries': {
        'source': '<?php function refused298(' + ', '.join(f'$p{i}=({e})' for i,e in enumerate(expressions)) + ') {} refused298();',
        'stage': context + f'-- if |pfunction.SIGNATURE.PARAMETERS| = {len(expressions)} -- if S.TODO = $function_tasks(S,pfunction)', 'checks': boundary},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
