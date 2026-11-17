#!/usr/bin/env python3
"""Independent falsey-condition certificates, raw tags and recipient cleanup."""
import hashlib
import json
from pathlib import Path

import closure_call_protocol as protocol

CATALOGUE = Path(__file__).with_name('deferred_falsey_short_redirect_wrapper_default_reception_cases.json')
ROWS = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in ROWS.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
base = ['S.CURRENT = (pcallcontext)', 'pcallcontext.FUNCTION = porigin_function',
        '$function_at(S.FUNCTIONS,porigin_function) = (pfunction)']
values = ['PINT 0', 'PBOOL true', 'PFLOAT 0', 'PFLOAT 9223372036854775808',
          'PFLOAT n_nan', 'PNULL', 'PBOOL true', 'PINT 1']
conditions = ['PBOOL false', 'PINT 0', 'PNULL', 'PFLOAT 0',
              'PFLOAT 9223372036854775808', 'PNULL', 'PFLOAT 0', 'PFLOAT 9223372036854775808']
raw = base + ['|pfunction.SIGNATURE.PARAMETERS| = 8', 'S.CODE = [pcode]',
              'S.POOLS = [ppool]', 'S.SOURCES = [pcunit]']
for index, (value, condition) in enumerate(zip(values, conditions)):
    raw += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index}) = ((z_{index},false))',
        f'$compiled_redirect(S,pdefault_{index}.ORIGIN) = ((PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2]),expression_right_{index},false,z_{index}))',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({condition})',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({condition})',
        f'$code_expression(pcode.EXPRESSIONS,pcpath_{index} ++ [PCFIELD 0]) = eps',
        f'$compiled_read(S,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = eps',
        f'$lossy_optional_integer_redirect_count(pcode.REDIRECTS,pcpath_{index} ++ [PCFIELD 0]) = 0',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 2])) = ({value})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({value})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {value},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_cell_{index})',
        f'S.STORE[n_cell_{index}] = DEFINED ({value})']
raw += ['$pfcast_nan(PFLOAT n_nan)',
    'S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_3[.VALUE = PFLOAT 0])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,3)']
for index, wrong in [(1, 'PBOOL false'), (2, 'PINT 0'), (3, 'PFLOAT 9223372036854775808'),
                     (4, 'PFLOAT 0'), (6, 'PBOOL false'), (7, 'PFLOAT 0')]:
    raw += [f'S_pool_{index} = S[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_{index} ++ [PCFIELD 0]) ({wrong}))] ++ ppool.CONSTANTS)]]]',
        f'$lossy_optional_integer_deferred_value_at(S_pool_{index},pfunction.ENV,pdefault_{index}.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_pool_{index},pfunction,{index})']
raw += ['$origin_node(S.SOURCES,pdefault_1.ORIGIN) = (NExprTernary expression_cond_1 ABSENT expression_right_1 metadata_1)',
    'S_nonzero_source = S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE pcpath_1 (NExprTernary (NScalarInt (INTEGER 1) eps) ABSENT expression_right_1 metadata_1)), (PCOCCURRENCE (pcpath_1 ++ [PCFIELD 0]) (NScalarInt (INTEGER 1) eps))] ++ pcunit.OCCURRENCES)]]]',
    'S_nonzero = S_nonzero_source[.POOLS = [ppool[.CONSTANTS = ([(PCONSTANT (pcpath_1 ++ [PCFIELD 0]) (PINT 1))] ++ ppool.CONSTANTS)]]]',
    '$lossy_optional_integer_deferred_value_at(S_nonzero,pfunction.ENV,PORIGIN n_unit (pcpath_1 ++ [PCFIELD 0])) = (PINT 1)',
    '$pool_value(S_nonzero.POOLS,PORIGIN n_unit (pcpath_1 ++ [PCFIELD 0])) = (PINT 1)',
    '$compiled_redirect(S_nonzero,pdefault_1.ORIGIN) = ((PORIGIN n_unit (pcpath_1 ++ [PCFIELD 2]),expression_right_1,false,z_1))',
    '$lossy_optional_integer_deferred_value_at(S_nonzero,pfunction.ENV,pdefault_1.ORIGIN) = eps',
    '~$lossy_optional_integer_deferred(S_nonzero,pfunction,1)']
mutations = {
    'duplicate': 'S[.CODE = [pcode[.REDIRECTS = (pcode.REDIRECTS ++ pcode.REDIRECTS)]]]',
    'copyflag': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_1 (pcpath_1 ++ [PCFIELD 2]) true)]]]]',
    'condcode': 'S[.CODE = [pcode[.EXPRESSIONS = ([(CODEEXPR (pcpath_1 ++ [PCFIELD 0]) z_1 false)] ++ pcode.EXPRESSIONS)]]]',
    'condredirect': 'S[.CODE = [pcode[.REDIRECTS = ([(CODEREDIRECT (pcpath_1 ++ [PCFIELD 0]) (pcpath_1 ++ [PCFIELD 2]) false)] ++ pcode.REDIRECTS)]]]',
    'target': 'S[.CODE = [pcode[.REDIRECTS = [(CODEREDIRECT pcpath_1 (pcpath_1 ++ [PCFIELD 2,PCFIELD 0]) false)]]]]',
    'source': 'S[.SOURCES = [pcunit[.OCCURRENCES = ([(PCOCCURRENCE (pcpath_1 ++ [PCFIELD 0]) (NScalarInt (INTEGER 1) eps))] ++ pcunit.OCCURRENCES)]]]',
}
for name, expression in mutations.items():
    raw += [f'S_{name} = {expression}',
        f'$lossy_optional_integer_deferred_value_at(S_{name},pfunction.ENV,pdefault_1.ORIGIN) = eps',
        f'~$lossy_optional_integer_deferred(S_{name},pfunction,1)']
raw += ['S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(8):
    raw.append(f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})')

named = base + ['|pfunction.SIGNATURE.PARAMETERS| = 6', '$default_cache_owner(S) = (CACHE_SHARED)']
for index, condition, before, after in [(1, 'PINT 0', 'PBOOL false', 'PINT 0'),
        (2, 'PNULL', 'PINT 1', 'PINT 1'), (3, 'PFLOAT 0', 'PFLOAT 0', 'PINT 0'),
        (4, 'PFLOAT 9223372036854775808', 'PFLOAT 9223372036854775808', 'PINT 0')]:
    named += [f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{index})',
        f'pdefault_{index}.ORIGIN = PORIGIN n_unit pcpath_{index}',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 0])) = ({condition})',
        f'$pool_value(S.POOLS,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0,PCFIELD 0])) = ({condition})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,PORIGIN n_unit (pcpath_{index} ++ [PCFIELD 0])) = ({before})',
        f'$lossy_optional_integer_deferred_value_at(S,pfunction.ENV,pdefault_{index}.ORIGIN) = ({after})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'pdefaultcache_{index} = {{ORIGIN pdefault_{index}.ORIGIN,VALUE {after},CLASS PVSCALAR}}',
        f'$default_current_cache(S,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        f'$lookup(S.ENV,pfunction.SIGNATURE.PARAMETERS[{index}].NAME) = (n_private_{index})',
        f'S.STORE[n_private_{index}] = DEFINED ({after})',
        rf'~(n_private_{index} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_private_{index}) = 1']
named += ['S_wrong_cache = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_4[.VALUE = PFLOAT 9223372036854775808])]',
    '$default_caches_valid(S_wrong_cache,S_wrong_cache.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache,pfunction,4)',
    'S_done = $drive_steps(S,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    r'$heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)']
for index in range(1, 5):
    named += [f'$default_cache_at(S_done.DEFAULTCACHE,pdefault_{index}.ORIGIN) = (pdefaultcache_{index})',
        rf'~((HCELL n_private_{index}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_private_{index}) = 0']
chain = '+(-((float)(+(E_WARNING === E_ERROR))))'
false = f'((bool)({chain}))'
truth = f'(!{false})'
selected = f'({truth} ? NULL : false)'
nan = f'(NAN + ({chain}))'
quiet_defaults = [(f'0 ?: (NULL ?: {false})', 'PBOOL false'),
                  (f'-0.0 ?: (0.0 ?: {nan})', 'PFLOAT n_nan'),
                  (f'NULL ?: (0 ?: {selected})', 'PNULL')]
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
expressions = [f'1 ?: {false}', f'-1 ?: {false}', f'NAN ?: {false}',
               f'"" ?: {false}', f'"0" ?: {false}', f'[] ?: {false}',
               f'0 ?: (!{nan})', f'NULL ?: (+{selected})', f'0.0 ?: ((string){false})']
boundary = base + [f'|pfunction.SIGNATURE.PARAMETERS| = {len(expressions)}']
for index in range(len(expressions)):
    boundary += [f'$lossy_optional_integer_deferred(S,pfunction,{index})'
                 if index in (3, 4)
                 else f'~$lossy_optional_integer_deferred(S,pfunction,{index})']
context = ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 0 -- if pcallcontext.FUNCTION = porigin_function '
    '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) ')
CASES = {
    'deferred-falsey-short-redirect-independent-conditions-tags': {'source': ROWS['deferred-falsey-short-redirect-wrapper-raw-tagged-results']['source'],
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 8 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': raw},
    'deferred-falsey-short-redirect-independent-private-recipients': {'source': ROWS['deferred-falsey-short-redirect-wrapper-alias-named-reentry']['source'],
        'stage': ('S.CURRENT = (pcallcontext) -- if pcallcontext.ARGC = 1 -- if pcallcontext.FUNCTION = porigin_function '
            '-- if $function_at(S.FUNCTIONS,porigin_function) = (pfunction) -- if pfunction.ENV.NAMESPACE = $ptascii("FalseyRedirect297") '
            '-- if |pfunction.SIGNATURE.PARAMETERS| = 6 -- if S.TODO = $function_tasks(S,pfunction)'), 'checks': named},
    'deferred-falsey-short-redirect-independent-nested-quiet': {
        'source': '<?php function quietHandler297($e,$m,$f,$l) { echo "unexpected-warning|"; } function quietFalsey297(' + ', '.join(f'$p{i}=({e})' for i,(e,_) in enumerate(quiet_defaults)) + ') {} set_error_handler("quietHandler297"); quietFalsey297(); quietFalsey297();',
        'stage': context + '-- if |pfunction.SIGNATURE.PARAMETERS| = 3 -- if S.TODO = $function_tasks(S,pfunction)', 'checks': quiet},
    'deferred-falsey-short-redirect-independent-current-boundaries': {
        'source': '<?php function refused297(' + ', '.join(f'$p{i}=({e})' for i,e in enumerate(expressions)) + ') {} refused297();',
        'stage': context + f'-- if |pfunction.SIGNATURE.PARAMETERS| = {len(expressions)} -- if S.TODO = $function_tasks(S,pfunction)', 'checks': boundary},
}
if __name__ == '__main__':
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
