#!/usr/bin/env python3
"""Literal TRUE preserves FIELD1 values without widening condition authority."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_true_full_ternary_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]',
              'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]']
for index, value in enumerate(values):
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'porigin_cond_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])',
        f'porigin_selected_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 1])',
        f'porigin_skip_{index} = PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])',
        f'$origin_node(S.SOURCES,pdefault_{index}.ORIGIN) = (NExprTernary expression_cond_{index} expression_selected_{index} expression_skip_{index} metadata_{index})',
        f'$origin_node(S.SOURCES,porigin_cond_{index}) = (expression_cond_{index})',
        f'$origin_node(S.SOURCES,porigin_selected_{index}) = (expression_selected_{index})',
        f'$origin_node(S.SOURCES,porigin_skip_{index}) = (expression_skip_{index})',
        f'$lossy_optional_integer_special(pfunction.ENV,expression_cond_{index}) = (PBOOL true)',
        f'$pool_value(S.POOLS,porigin_cond_{index}) = (PBOOL true)',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        rf'$pool_value(S.POOLS,pdefault_{index}.ORIGIN) = eps /\ $compiled_read(S,pdefault_{index}.ORIGIN) = eps',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = ((porigin_selected_{index},expression_selected_{index},false,z_{index}))',
        f'$lossy_optional_integer_pruned_ternary(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ((porigin_cond_{index},porigin_selected_{index}))',
        f'~$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_skip_{index})',
        f'$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,pdefault_{index}.ORIGIN)',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,porigin_selected_{index}) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    '~$lossy_optional_integer_phase_safe(S,pfunction.ENV,porigin_selected_0)',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,3)']
for name, expression, value in [
        ('false', 'NExprConstFetch (NName (BYTES "ZmFsc2U=") eps) eps', 'PBOOL false'),
        ('one', 'NScalarInt (INTEGER 1) eps', 'PINT 1'),
        ('nan', 'NExprConstFetch (NName (BYTES "TkFO") eps) eps', 'PFLOAT 9221120237041090560'),
        ('computed', 'NExprBooleanNot (NExprConstFetch (NName (BYTES "ZmFsc2U=") eps) eps) eps', 'PBOOL true')]:
    child_fact = ', (PCONSTANT (pcpath_0 ++ [PCFIELD 0,PCFIELD 0]) (PBOOL false))' if name == 'computed' else ''
    raw += [f'expression_{name} = {expression}',
        f'S_source_{name} = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_0 (NExprTernary expression_{name} expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_{name})] ++ $pcwalk($pcchildren(expression_{name},pcpath_0 ++ [PCFIELD 0])) ++ pcunit.OCCURRENCES)]]]',
        f'S_{name} = S_source_{name}[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) ({value})){child_fact}] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,porigin_cond_0) = ({value})',
        f'$compiled_redirect(S_{name},pdefault_0.ORIGIN) = ((porigin_selected_0,expression_selected_0,false,z_0))',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = ' + ('(PINT 0)' if name in ('computed', 'one') else 'eps'),
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
raw += ['$lossy_optional_integer_deferred_bindings(S_computed,pfunction.ENV,pdefault_0.ORIGIN)',
    'S_no_redirect = S[.CODE = [pcode[.REDIRECTS = eps]]]',
    '$lossy_optional_integer_deferred_value_at(S_no_redirect,pfunction.ENV,pdefault_0.ORIGIN) = (PINT 0)',
    '~$lossy_optional_integer_deferred_bindings(S_no_redirect,pfunction.ENV,pdefault_0.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_no_redirect,pfunction,0)',
    'S_wrong_target = S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_0 (pcpath_0 ++ [PCFIELD 2]) false)]]]]',
    '$compiled_redirect(S_wrong_target,pdefault_0.ORIGIN) = ((porigin_skip_0,expression_skip_0,false,z_0))',
    '~$lossy_optional_integer_deferred_bindings(S_wrong_target,pfunction.ENV,pdefault_0.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_wrong_target,pfunction,0)',
    'S_wrong_selected = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 1]) (NScalarInt (INTEGER 7) eps))] ++ pcunit.OCCURRENCES)]]]',
    '~$lossy_optional_integer_deferred_bindings(S_wrong_selected,pfunction.ENV,pdefault_0.ORIGIN)',
    '~$lossy_optional_integer_deferred(S_wrong_selected,pfunction,0)',
    'pcoccurrence_kept* = [(PCOCCURRENCE pcpath_0 (NExprTernary expression_cond_0 expression_selected_0 expression_skip_0 metadata_0)), (PCOCCURRENCE (pcpath_0 ++ [PCFIELD 0]) expression_cond_0)] ++ $pcwalk($pcchildren(expression_cond_0,pcpath_0 ++ [PCFIELD 0])) ++ [(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 1]) expression_selected_0)] ++ $pcwalk($pcchildren(expression_selected_0,pcpath_0 ++ [PCFIELD 1]))',
    'S_missing = S[.SOURCES = [pcunit[.OCCURRENCES = pcoccurrence_kept*]]]',
    '$origin_node(S_missing.SOURCES,porigin_skip_0) = eps',
    '$lossy_optional_integer_deferred_bindings(S_missing,pfunction.ENV,pdefault_0.ORIGIN)',
    '$lossy_optional_integer_deferred_value_at(S_missing,pfunction.ENV,pdefault_0.ORIGIN) = eps',
    'S_restored = S_missing[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_0 ++ [PCFIELD 2]) expression_skip_0)] ++ pcoccurrence_kept*)]]]',
    '$lossy_optional_integer_deferred_value_at(S_restored,pfunction.ENV,pdefault_0.ORIGIN) = (PINT 0)']
mutations = {
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'pool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT pcpath_0 (PINT 0))] ++ ppool.CONSTANTS)]]]',
    'condition_pool': 'S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_0 ++ [PCFIELD 0]) (PBOOL false))] ++ ppool.CONSTANTS)]]]',
    'condition_code': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_0 ++ [PCFIELD 0]) z_0 true)] ++ pcode.EXPRESSIONS)]]]',
}
for name, expression in mutations.items():
    raw += [f'S_{name} = {expression}',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_0.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,0)']
raw += ['S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6', '$default_cache_owner(S) = (CACHE_SHARED)']
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
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base300"),$ptascii("E_ERROR")),($ptascii("One300"),$ptascii("E_ERROR")),($ptascii("Skipped300"),$ptascii("Unavailable300") ++ [92] ++ $ptascii("Payload"))]]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,pdefault_1.ORIGIN)',
    'S_budget = $drive_steps(S,0)', 'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps']
for index in (1, 2, 3, 4):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
named += ['$lookup(S_done.ENV,$ptascii("x300")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
truth = f'(!{false})'
nan = f'(NAN + ({chain}))'
null = f'({truth} ? NULL : false)'
quiet_defaults = [(f'true ? {false} : Missing300', 'PBOOL false'),
                  (f'true ? (true ? {nan} : Missing300) : Missing300', 'PFLOAT n_nan'),
                  (f'(int)(true ? (NULL ? Missing300 : {null}) : Missing300)', 'PINT 0')]
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
expressions = [f'1 ? {false} : Missing300', f'(!false) ? {false} : Missing300',
               f'"1" ? {false} : Missing300', f'NAN ? {false} : Missing300',
               f'true ? ((string){false}) : Missing300', 'true ? [] : Missing300']
boundary = base + [f'|pfunction.SIGNATURE.PARAMETERS| = {len(expressions)}']
for index in range(len(expressions)):
    boundary += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ' + ('(PBOOL false)' if index in (0, 1, 2) else 'eps'),
        ('' if index in (0, 1, 2) else '~') + f'$lossy_optional_integer_deferred(S,pfunction,{index})']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'true-full-independent-source-tags-and-forgeries': {'source': ROWS['deferred-true-full-ternary-redirect-wrapper-raw-tagged-results']['source'],
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'true-full-independent-private-recipients': {'source': ROWS['deferred-true-full-ternary-redirect-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
            '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) -- if pfunction.ENV.NAMESPACE = $ptascii("TrueRedirect300") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'true-full-independent-nested-quiet': {'source': '<?php function quietHandler300($e,$m,$f,$l) { echo "unexpected-warning|"; } function quietTrue300(' + ', '.join(f'$p{i}=({e})' for i,(e,_) in enumerate(quiet_defaults)) + ') {} set_error_handler("quietHandler300"); quietTrue300(); quietTrue300();',
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'true-full-independent-current-boundaries': {'source': '<?php function refused300(' + ', '.join(f'$p{i}=({e})' for i,e in enumerate(expressions)) + ') {} refused300(' + ','.join('0' for _ in expressions) + ');',
        'stage': context.replace('pcallcontext.ARGC = 0', f'pcallcontext.ARGC = {len(expressions)}') + f'-- if |pfunction.SIGNATURE.PARAMETERS| = {len(expressions)} -- if S.TODO = $function_tasks(S,pfunction)', 'checks': boundary},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
