#!/usr/bin/env python3
"""Full falsey redirects authenticate skipped source and selected raw values."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_falsey_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
conditions = ['PBOOL false', 'PNULL', 'PINT 0', 'PFLOAT 0',
              'PFLOAT 9223372036854775808', 'PSTRING (eps)', 'PSTRING ([48])', 'PSTRING ([48])']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]',
              'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]']
for index, (value, condition) in enumerate(zip(values, conditions)):
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'porigin_cond_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_skip_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'porigin_selected_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_skip_{index} expression_selected_{index} metadata_{index})',
        f'$origin_node(S.SOURCES,porigin_cond_{index}) = (expression_cond_{index})',
        f'$origin_node(S.SOURCES,porigin_skip_{index}) = (expression_skip_{index})',
        f'$origin_node(S.SOURCES,porigin_selected_{index}) = (expression_selected_{index})',
        f'$lossy_optional_integer_falsey_full_redirect(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_skip_{index})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_selected_{index})',
        f'$call_name_count(pcode.NAMES,pcpath_{index} ++ [PCFIELD 1]) = 0',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD 1]) = eps',
        rf'$pool_value(S.POOLS,porigin_skip_{index}) = eps /\ $compiled_read(S,porigin_skip_{index}) = eps',
        f'$pool_value(S.POOLS,porigin_cond_{index}) = ({condition})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})']
    if index < 5:
        raw += [f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_cond_{index}) = ({condition})']
    else:
        byte_sequence = 'eps' if index == 5 else '[48]'
        raw += [f'expression_cond_{index} = NScalarString (BYTES text_{index}) metadata_cond_{index}',
            f'$base64(text_{index}) = {byte_sequence}',
            f'$compiled_precision(S,(porigin_cond_{index})) = (14)',
            f'$compiled_string_value(S,porigin_cond_{index},{condition}) = PSTRING_CARRIER INTERNED_STRING ({byte_sequence})',
            f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_cond_{index}) = eps']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,3)']
for name, expression, value in [
        ('one', 'NScalarInt (INTEGER 1) eps', 'PINT 1'),
        ('nan', 'NExprConstFetch (NName (BYTES "TkFO") eps) eps', 'PFLOAT 9221120237041090560'),
        ('doublezero', 'NScalarString (BYTES "MDA=") eps', 'PSTRING ([48,48])')]:
    raw += [f'expression_{name} = {expression}',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_2 (NExprTernary expression_{name} expression_skip_2 expression_selected_2 metadata_2)), (PCOCCURRENCE (pcpath_2 ++ [PCFIELD 0]) expression_{name})] ++ $pcwalk($pcchildren(expression_{name},pcpath_2 ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_2 ++ [PCFIELD 0]) ({value}))] ++ ppool.CONSTANTS)]]]',
        f'$pool_value(S_{name}.POOLS,porigin_cond_2) = ({value})',
        f'$compiled_redirect(S_{name},pdefault_2.ORIGIN) = ((porigin_selected_2,expression_selected_2,false,z_{name}))',
        f'$lossy_optional_integer_falsey_full_redirect(S_{name},pfunction.ENV,pdefault_2.ORIGIN) = eps',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_2.ORIGIN) = eps']
    if name == 'doublezero':
        raw.append(f'$compiled_string_value(S_{name},porigin_cond_2,{value}) = PSTRING_CARRIER INTERNED_STRING ([48,48])')
    else:
        raw.append(f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_2) = ({value})')
raw += [
    'pcoccurrence_kept* = [(PCOCCURRENCE pcpath_2 (NExprTernary expression_cond_2 expression_skip_2 expression_selected_2 metadata_2)), (PCOCCURRENCE (pcpath_2 ++ [PCFIELD 0]) expression_cond_2)] ++ $pcwalk($pcchildren(expression_cond_2,pcpath_2 ++ [PCFIELD 0])) ++ [(PCOCCURRENCE (pcpath_2 ++ [PCFIELD 2]) expression_selected_2)] ++ $pcwalk($pcchildren(expression_selected_2,pcpath_2 ++ [PCFIELD 2]))',
    'S_missing = S[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_kept*]]]',
    '$origin_node(S_missing.SOURCES,porigin_skip_2) = eps',
    '$lossy_optional_integer_deferred_value_at(S_missing,pfunction.ENV,porigin_cond_2) = (PINT 0)',
    '$lossy_optional_integer_deferred_value_at(S_missing,pfunction.ENV,porigin_selected_2) = (PFLOAT 0)',
    '$lossy_optional_integer_falsey_full_redirect(S_missing,pfunction.ENV,pdefault_2.ORIGIN) = eps',
    'S_restored = S_missing[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_2 ++ [PCFIELD 1]) expression_skip_2)] ++ pcoccurrence_kept*)]]]',
    '$lossy_optional_integer_falsey_full_redirect(S_restored,pfunction.ENV,pdefault_2.ORIGIN) = ((porigin_cond_2,porigin_selected_2))',
    '$lossy_optional_integer_deferred_value_at(S_restored,pfunction.ENV,pdefault_2.ORIGIN) = (PFLOAT 0)',
    '$constant_precision_at(ppool.CONSTANTS,pcpath_6 ++ [PCFIELD 0]) = eps',
    'S_no_precision = S[.DECLARATIONS = eps]',
    '$compiled_string_value(S_no_precision,porigin_cond_6,PSTRING ([48])) = PSTRING ([48])',
    '$lossy_optional_integer_falsey_full_redirect(S_no_precision,pfunction.ENV,pdefault_6.ORIGIN) = eps']
for name, value in [('bytes', 'PSTRING (eps)'),
                    ('interned', 'PSTRING_CARRIER INTERNED_STRING ([48])'),
                    ('request', 'PSTRING_CARRIER (REQUEST_STRING (|S.STRINGDATA|)) ([48])')]:
    raw += [f'S_pool_{name} = S[.STRINGDATA = (S.STRINGDATA ++ [[48]])][.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_6 ++ [PCFIELD 0]) ({value}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_falsey_full_redirect(S_pool_{name},pfunction.ENV,pdefault_6.ORIGIN) = eps']
for field in (0, 1, 2):
    raw += [f'S_source_{field} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_2 ++ [PCFIELD {field}]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
        f'$lossy_optional_integer_falsey_full_redirect(S_source_{field},pfunction.ENV,pdefault_2.ORIGIN) = eps']
raw += ['S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6', '$default_cache_owner(S) = (CACHE_SHARED)',
                'S.SOURCES = [pcunit]', 'S.CODE = [pcode]']
for index, before, value in [(1, 'PBOOL false', 0), (2, 'PINT 1', 1),
        (3, 'PFLOAT 9223372036854775808', 0), (4, 'PNULL', 0)]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({before})',
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
    '$origin_node(S.SOURCES,pdefault_4.ORIGIN) = (NExprCastInt expression_null metadata_null)',
    'S_alias = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_4 (NExprCastInt expression_null ((Mkind 2) :: metadata_null)))] ++ pcunit.OCCURRENCES)]]]',
    '$lossy_optional_integer_deferred_value_at(S_alias,pfunction.ENV,pdefault_4.ORIGIN) = eps',
    'S_null_code = S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR pcpath_4 12 true)] ++ pcode.EXPRESSIONS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_null_code,pfunction.ENV,pdefault_4.ORIGIN) = eps',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base299"),$ptascii("E_ERROR")),($ptascii("One299"),$ptascii("E_ERROR")),($ptascii("Skipped299"),$ptascii("Unavailable299") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps']
for index in (1, 2, 3, 4):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
named += ['$lookup(S_done.ENV,$ptascii("x299")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']

chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
truth = f'(!{false})'
nan = f'(NAN + ({chain}))'
null = f'({truth} ? NULL : false)'
quiet_defaults = [(f'0 ? Missing299 : ("0" ? Missing299 : {nan})', 'PFLOAT n_nan'),
                  (f'\'\' ? Missing299 : (int)(NULL ? Missing299 : {null})', 'PINT 0'),
                  (f'(int)(0.0 ? Missing299 : {truth})', 'PINT 1')]
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
expressions = [f'"00" ? Missing299 : {false}', f'1 ? Missing299 : {false}',
               f'NAN ? Missing299 : {false}', f'("" . "") ? Missing299 : {false}',
               f'((string)false) ? Missing299 : {false}', f'0 ? Missing299 : ((string){false})',
               'NULL ? Missing299 : []', f'0 ? Missing299 : (!{nan})']
boundary = base + [f'|pfunction.SIGNATURE.PARAMETERS| = {len(expressions)}']
for index in range(len(expressions)):
    boundary += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'falsey-full-independent-skipped-source-tags': {'source': ROWS['deferred-falsey-full-ternary-redirect-wrapper-raw-tagged-results']['source'],
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'falsey-full-independent-private-null-cast-recipients': {'source': ROWS['deferred-falsey-full-ternary-redirect-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
            '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) -- if pfunction.ENV.NAMESPACE = $ptascii("FullRedirect299") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'falsey-full-independent-nested-quiet': {'source': '<?php function quietHandler299($e,$m,$f,$l) { echo "unexpected-warning|"; } function quietFull299(' + ', '.join(f'$p{i}=({e})' for i,(e,_) in enumerate(quiet_defaults)) + ') {} set_error_handler("quietHandler299"); quietFull299(); quietFull299();',
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'falsey-full-independent-current-boundaries': {'source': '<?php function refused299(' + ', '.join(f'$p{i}=({e})' for i,e in enumerate(expressions)) + ') {} refused299(' + ','.join('0' for _ in expressions) + ');',
        'stage': context.replace('pcallcontext.ARGC = 0', f'pcallcontext.ARGC = {len(expressions)}') + f'-- if |pfunction.SIGNATURE.PARAMETERS| = {len(expressions)} -- if S.TODO = $function_tasks(S,pfunction)', 'checks': boundary},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
