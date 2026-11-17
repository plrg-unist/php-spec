#!/usr/bin/env python3
"""Literal string receipts preserve byte truth, scalar tags and private cells."""
import base64
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_truthy_literal_string_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
conditions = [b'00', b'0.0', b'false', b' ', b'0e0', b'x', b'-0', b'1']


def bytes_term(value):
    return '[' + ','.join(str(byte) for byte in value) + ']' if value else 'eps'


raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]',
              'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, (value, condition) in enumerate(zip(values, conditions)):
    data = bytes_term(condition)
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'porigin_cond_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_selected_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'porigin_skip_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
        f'$origin_node(S.SOURCES,porigin_cond_{index}) = (expression_cond_{index})',
        f'expression_cond_{index} = NScalarString (BYTES text_cond_{index}) metadata_cond_{index}',
        f'$base64(text_cond_{index}) = {data}',
        f'$origin_node(S.SOURCES,porigin_selected_{index}) = (expression_selected_{index})',
        f'$origin_node(S.SOURCES,porigin_skip_{index}) = (expression_skip_{index})',
        f'$pool_value(S.POOLS,porigin_cond_{index}) = (PSTRING ({data}))',
        f'$compiled_string_value(S,porigin_cond_{index},PSTRING ({data})) = PSTRING_CARRIER INTERNED_STRING ({data})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_cond_{index}) = eps',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD 0]) = eps',
        f'$compiled_read(S,porigin_cond_{index}) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_{index} ++ [PCFIELD 0]) = 0',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_{index}) = 1',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = ((porigin_selected_{index},expression_selected_{index},false,z_{index}))',
        f'$lossy_optional_integer_truthy_literal_string_full_redirect(S,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_cond_{index})',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_skip_{index})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_selected_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selected_{index}) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})',
        rf'~(n_cell_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell_{index}) = 1']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,3)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_cell_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_cell_{index}) = 0']

forgeries = base + ['S.CODE = [pcode]', 'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]',
    '$default_at(pfunction.DEFAULTS,0) = (pdefault_0)',
    'pdefault_0.ORIGIN = PORIGIN n_unit pcpath_0',
    'porigin_cond_0 = PORIGIN n_unit (pcpath_0 ++ [PCFIELD 0])',
    'porigin_selected_0 = PORIGIN n_unit (pcpath_0 ++ [PCFIELD 1])',
    'porigin_skip_0 = PORIGIN n_unit (pcpath_0 ++ [PCFIELD 2])',
    '$origin_node(S.SOURCES,pdefault_0.ORIGIN) = (NExprTernary expression_cond_0 expression_selected_0 expression_skip_0 metadata_0)',
    '$code_expression(pcode.EXPRESSIONS,pcpath_0) = ((z_0,false))',
    '$lossy_optional_integer_truthy_literal_string_full_redirect(S,pdefault_0.ORIGIN) = ((porigin_cond_0,porigin_selected_0))']
for name, data in [('empty', b''), ('zero', b'0'), ('nul', b'\0'),
                   ('zero_nul', b'0\0'), ('high_byte', b'\xff'), ('two_zero', b'00')]:
    encoded, decoded = base64.b64encode(data).decode(), bytes_term(data)
    forgeries += [f'expression_{name} = NScalarString (BYTES "{encoded}") eps',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PSTRING ({decoded})))] ++ ppool.CONSTANTS)]]]',
        f'$compiled_string_value(S_{name},porigin_cond_0,PSTRING ({decoded})) = PSTRING_CARRIER INTERNED_STRING ({decoded})',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = eps',
        f'$lossy_optional_integer_truthy_literal_string_full_redirect(S_{name},pdefault_0.ORIGIN) = ' + ('eps' if name in ('empty', 'zero') else '((porigin_cond_0,porigin_selected_0))'),
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
    if name in ('empty', 'zero'):
        forgeries += [f'S_falsey_{name} = S_{name}[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_0 (pcpath_0 ++ [PCFIELD 2]) false)]]]]',
            f'$lossy_optional_integer_falsey_full_redirect(S_falsey_{name},pfunction.ENV,pdefault_0.ORIGIN) = ((porigin_cond_0,porigin_skip_0))']
    else:
        forgeries.append(f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = (PINT 0)')
mutations = {
    'no_redirect': 'S[.CODE = [pcode[.REDIRECTS = eps]]]',
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'copy': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_0 (pcpath_0 ++ [PCFIELD 1]) true)]]]]',
    'wrong_target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_0 (pcpath_0 ++ [PCFIELD 2]) false)]]]]',
    'self_target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_0 pcpath_0 false)]]]]',
    'own_pool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_0 (PINT 0))] ++ ppool.CONSTANTS)]]]',
    'own_code': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_0 z_0 true)] ++ pcode.EXPRESSIONS)]]]',
    'condition_pool_bytes': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PSTRING ([48])))] ++ ppool.CONSTANTS)]]]',
    'condition_pool_truthy_bytes': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PSTRING ([32])))] ++ ppool.CONSTANTS)]]]',
    'condition_pool_interned': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PSTRING_CARRIER INTERNED_STRING ([48,48])))] ++ ppool.CONSTANTS)]]]',
    'condition_pool_request': 'S[.STRINGDATA = (S.STRINGDATA ++ [[48,48]])][.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([48,48])))] ++ ppool.CONSTANTS)]]]',
    'condition_code': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_0 ++ [PCFIELD 0]) z_0 true)] ++ pcode.EXPRESSIONS)]]]',
    'condition_redirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT (pcpath_0 ++ [PCFIELD 0]) (pcpath_0 ++ [PCFIELD 1]) false)] ++ pcode.REDIRECTS)]]]',
    'no_precision': 'S[.DECLARATIONS = eps][.POOLS = [ppool[.CONSTANTS = [(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PSTRING ([48,48])))]]]]',
}
for name, expression in mutations.items():
    forgeries += [f'S_{name} = {expression}',
        f'$lossy_optional_integer_truthy_literal_string_full_redirect(S_{name},pdefault_0.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred_bindings(S_{name},pfunction.ENV,pdefault_0.ORIGIN)',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
for field in range(3):
    forgeries += [f'S_source_arm_{field} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD {field}]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_truthy_literal_string_full_redirect(S_source_arm_{field},pdefault_0.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_source_arm_{field},pfunction,0)']
forgeries += ['pcoccurrence_kept* = [(PCOCCURRENCE pcpath_0 (NExprTernary expression_cond_0 expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_cond_0), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 1]) expression_selected_0)] ++ $pcwalk($pcchildren(expression_selected_0,pcpath_0 ++ [PCFIELD 1]))',
    'S_missing = S[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_kept*]]]',
    '$origin_node(S_missing.SOURCES,porigin_skip_0) = eps',
    '$lossy_optional_integer_truthy_literal_string_full_redirect(S_missing,pdefault_0.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_missing,pfunction,0)']

named = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, before, value in [(1, 'PBOOL false', 0), (2, 'PINT 1', 1),
                              (3, 'PFLOAT 9223372036854775808', 0), (4, 'PNULL', 0)]:
    data = bytes_term(conditions[index - 1])
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'porigin_full_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_cond_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 0])',
        f'porigin_selected_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 1])',
        f'$pool_value(S.POOLS,porigin_cond_{index}) = (PSTRING ({data}))',
        f'$compiled_string_value(S,porigin_cond_{index},PSTRING ({data})) = PSTRING_CARRIER INTERNED_STRING ({data})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_cond_{index}) = eps',
        f'$lossy_optional_integer_truthy_literal_string_full_redirect(S,porigin_full_{index}) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selected_{index}) = ({before})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_full_{index}) = ({before})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = (PINT {value})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
named += ['S_wrong_null = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_4[.VALUE = PNULL])]',
    '$default_caches_valid(S_wrong_null,S_wrong_null.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_null,pfunction,4)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base304"),$ptascii("E_ERROR")),($ptascii("One304"),$ptascii("E_ERROR")),($ptascii("Skipped304"),$ptascii("Unavailable304") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)']
lifecycle = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, value in [(1, 0), (2, 1), (3, 0), (4, 0)]:
    lifecycle += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE PINT {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED (PINT {value})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
lifecycle += ['S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps']
for index in (1, 2, 3, 4):
    lifecycle += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
lifecycle += ['$lookup(S_done.ENV,$ptascii("x304")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
truth = f'(!{false})'
nan = f'(NAN + ({chain}))'
null = f'({truth} ? NULL : false)'
quiet_defaults = [(f'"00" ? ("0" ? Missing304 : {nan}) : Missing304', 'PFLOAT n_nan'),
                  (f'"\\0" ? (1.0 ? {false} : Missing304) : Missing304', 'PBOOL false'),
                  (f'(int)("0.0" ? ("" ? Missing304 : {null}) : Missing304)', 'PINT 0')]
quiet = base + ['|pfunction.SIGNATURE.PARAMETERS| = 3', 'S.ERRORHANDLER.CALLBACK =/= eps']
for index, (_, value) in enumerate(quiet_defaults):
    quiet += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_quiet_{index})',
        f'S.STORE[n_quiet_{index}] = DEFINED ({value})']
quiet += ['pdefault_1.ORIGIN = PORIGIN n_unit pcpath_nul',
    'porigin_nul_cond = PORIGIN n_unit (pcpath_nul ++ [PCFIELD 0])',
    '$pool_value(S.POOLS,porigin_nul_cond) = (PSTRING ([0]))',
    '$compiled_string_value(S,porigin_nul_cond,PSTRING ([0])) = PSTRING_CARRIER INTERNED_STRING ([0])',
    '$lossy_optional_integer_truthy_literal_string_full_redirect(S,pdefault_1.ORIGIN) = ((porigin_nul_cond,PORIGIN n_unit (pcpath_nul ++ [PCFIELD 1])))',
    '$pfcast_nan(PFLOAT n_nan)', 'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.TODO = eps',
    'S_done.EVENTS = eps', 'S_done.ERRORHANDLER = S.ERRORHANDLER', '$heap_valid($heap_graph(S_done))']
expressions = [f'("" . "00") ? {false} : Missing304', f'((string)1) ? {false} : Missing304',
               f'"1" ? ((string){false}) : Missing304', '"1" ? [] : Missing304',
               f'"00" ?: {false}']
boundary = base + [f'|pfunction.SIGNATURE.PARAMETERS| = {len(expressions)}']
for index in range(len(expressions)):
    boundary += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
raw_source = ROWS['deferred-truthy-literal-string-full-ternary-redirect-wrapper-raw-tagged-results']['source']
named_source = ROWS['deferred-truthy-literal-string-full-ternary-redirect-wrapper-alias-named-reentry']['source']
CASES = {
    'truthy-literal-string-full-independent-raw-tags': {'source': raw_source,
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'truthy-literal-string-full-independent-forgeries': {'source': raw_source,
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': forgeries},
    'truthy-literal-string-full-independent-private-recipients': {'source': named_source,
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
            '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) -- if pfunction.ENV.NAMESPACE = $ptascii("LiteralStringRedirect304") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'truthy-literal-string-full-independent-nested-quiet': {'source': '<?php function quietHandler304($e,$m,$f,$l) { echo "unexpected-warning|"; } function quietLiteralString304(' + ', '.join(f'$p{i}=({e})' for i,(e,_) in enumerate(quiet_defaults)) + ') {} set_error_handler("quietHandler304"); quietLiteralString304(); quietLiteralString304();',
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'truthy-literal-string-full-independent-current-boundaries': {'source': '<?php function refused304(' + ', '.join(f'$p{i}=({e})' for i,e in enumerate(expressions)) + ') {} refused304(' + ','.join('0' for _ in expressions) + ');',
        'stage': context.replace('pcallcontext.ARGC = 0', f'pcallcontext.ARGC = {len(expressions)}') + f'-- if |pfunction.SIGNATURE.PARAMETERS| = {len(expressions)} -- if S.TODO = $function_tasks(S,pfunction)', 'checks': boundary},
}
CASES['truthy-literal-string-full-independent-private-lifecycle'] = dict(CASES['truthy-literal-string-full-independent-private-recipients'], checks=lifecycle)
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
