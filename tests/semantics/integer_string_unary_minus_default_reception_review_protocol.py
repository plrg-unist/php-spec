#!/usr/bin/env python3
"""Independent stored integer-string certificates and deferred composition checks."""
import base64
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_name('integer_string_unary_minus_default_reception_cases.json')


def node(constructor, *children):
    return constructor + ' ' + ' '.join(f'({child})' for child in children) + ' eps'


def constant(name):
    return f'NExprConstFetch (NName (BYTES "{base64.b64encode(name.encode()).decode()}") eps) eps'


def string(text):
    return f'NScalarString (BYTES "{base64.b64encode(text.encode()).decode()}") eps'


def binary(operator, left, right):
    return node('NExprBinaryOp' + operator, left, right)


checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = ($ptascii("StoredStringAlias247") ++ [92] ++ $ptascii("defaults247"))',
    'pfunction.ENV.NAMESPACE = $ptascii("StoredStringAlias247")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Base247"),$ptascii("E_WARNING")),($ptascii("One247"),$ptascii("E_ERROR"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_integer,psparam_joined,psparam_nested,psparam_last]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ psparam_integer.BYREF /\ ~psparam_joined.BYREF /\ ~psparam_nested.BYREF /\ ~psparam_last.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 5 /\ pcallcontext.HOLES = [1,2,3]',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    r'~(n_cell <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_cell) = 1',
    'S.STORE[n_cell] = DEFINED (PFLOAT 4609434218613702656)',
    r'n_bits = 4609434218613702656 /\ i = 1',
    'z = $default_parameter_line(S,porigin,0)',
    'ptask_resume = LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z',
    '$lossy_mixed_parameter_source_valid(S,ptask_resume)',
    '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
    '$call_task_valid(S,ptask_resume)',
    '$task_nodes(ptask_resume) = eps',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_last.NAME) = (n_last)',
    'S.STORE[n_last] = DEFINED (PINT 8)',
    'S.CODE = [pcode]',
]
for index, label, integer in [(1, 'integer', '$(-22)'), (3, 'nested', '22')]:
    checks.extend([
        f'psparam_{label}.DEFAULT = PSDEFAULT expression_{label} "int"',
        f'$lossy_optional_integer_default_in(pfunction.ENV,expression_{label}) = ({integer})',
        f'$lossy_optional_integer_numeric(pfunction.ENV,expression_{label}) = (NINT {integer})',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_source_unit pcpath_{label}',
        f'porigin_{label} = PORIGIN n_source_unit (pcpath_{label} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{label}) = (expression_{label})',
        f'pdefault_{label} = {{INDEX {index},ORIGIN porigin_{label},KIND PDSTORED}}',
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{label})',
        f'$pool_value(S.POOLS,porigin_{label}) = (PINT {integer})',
        f'$compiled_read(S,porigin_{label}) = (PINT {integer})',
        f'$default_current_cache(S,porigin_{label}) = eps',
        f'~$lossy_optional_integer_deferred(S,pfunction,{index})',
        f'$lossy_optional_integer_tail(S,pfunction,[psparam_{label}],{index})',
        f'$lookup(S.ENV,psparam_{label}.NAME) = (n_local_{label})',
        f'S.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'~(n_local_{label} <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_local_{label}) = 1',
    ])
checks.extend([
    'expression_integer = NExprUnaryMinus expression_integer_string metadata_integer_parent',
    '$lossy_optional_integer_quiet_shape(expression_integer_string)',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_integer_string) = ([50,50])',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_integer_string) = eps',
    '$coerce_number(PSTRING ([50,50])) = COERCED (NINT 22) false',
    'expression_nested = NExprUnaryMinus expression_nested_child metadata_nested_parent',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_nested_child) = ($(-22))',
    'psparam_joined.DEFAULT = PSDEFAULT expression_joined "deferred"',
    '$default_parameter_origin(S,porigin,2) = PORIGIN n_source_unit pcpath_joined',
    'porigin_joined = PORIGIN n_source_unit (pcpath_joined ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES,porigin_joined) = (expression_joined)',
    '$default_at(pfunction.DEFAULTS,2) = ({INDEX 2,ORIGIN porigin_joined,KIND PDDEFERRED})',
    r'$pool_value(S.POOLS,porigin_joined) = eps /\ $compiled_read(S,porigin_joined) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_joined) = ($(-21))',
    '$lossy_optional_integer_numeric(pfunction.ENV,expression_joined) = (NINT $(-21))',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_joined) = (PINT $(-21))',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_joined)',
    '$lossy_optional_integer_deferred(S,pfunction,2)',
    'pdefaultcache_joined = {ORIGIN porigin_joined,VALUE PINT $(-21),CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_joined) = (pdefaultcache_joined)',
    '$lookup(S.ENV,psparam_joined.NAME) = (n_local_joined)',
    'S.STORE[n_local_joined] = DEFINED (PINT $(-21))',
    r'~(n_local_joined <- S.REFCELLS) /\ $heap_owners($heap_graph(S),HCELL n_local_joined) = 1',
    'expression_joined = NExprCastInt expression_concat metadata_joined_parent',
    'expression_concat = NExprBinaryOpConcat expression_prefix expression_suffix metadata_joined_concat',
    'expression_prefix = NExprCastString expression_inner metadata_joined_prefix',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_inner) = ($(-2))',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_prefix) = ([45,50])',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_suffix) = ([49])',
    '$lossy_optional_integer_string_in(pfunction.ENV,expression_concat) = ([45,50,49])',
    'S_no_pool = S[.POOLS = eps]',
    '$compiled_read(S_no_pool,porigin_integer) = eps',
    '~$lossy_optional_integer_tail(S_no_pool,pfunction,[psparam_integer],1)',
    'S_wrong_tag = S[.POOLS = [{UNIT n_source_unit,CONSTANTS ([(PCONSTANT (pcpath_integer ++ [PCFIELD 6]) (PBOOL false))])}]]',
    '$compiled_read(S_wrong_tag,porigin_integer) = (PBOOL false)',
    '~$lossy_optional_integer_tail(S_wrong_tag,pfunction,[psparam_integer],1)',
    'S_wrong_value = S[.POOLS = [{UNIT n_source_unit,CONSTANTS ([(PCONSTANT (pcpath_integer ++ [PCFIELD 6]) (PINT $(-21)))])}]]',
    '$compiled_read(S_wrong_value,porigin_integer) = (PINT $(-21))',
    '~$lossy_optional_integer_tail(S_wrong_value,pfunction,[psparam_integer],1)',
    'expression_same_value = NScalarInt (INTEGER $(-22)) eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_same_value) = ($(-22))',
    '~$lossy_optional_integer_tail(S,pfunction,[psparam_integer[.DEFAULT = PSDEFAULT expression_same_value "int"]],1)',
    '~$lossy_optional_integer_tail(S,pfunction[.DEFAULTS = [pdefault_integer[.KIND = PDDEFERRED]]],[psparam_integer],1)',
    '~$lossy_optional_integer_tail(S[.SOURCES = eps],pfunction,[psparam_integer],1)',
    'S_wrong_cache_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_joined[.VALUE = PFLOAT $hex_bits("c035000000000000",0)])]',
    '$default_caches_valid(S_wrong_cache_tag,S_wrong_cache_tag.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_cache_tag,pfunction,2)',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,2)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = [($ptascii("Base247"),$ptascii("E_ERROR")),($ptascii("One247"),$ptascii("E_WARNING"))]]',
    '$lossy_optional_integer_default_in(plenv_wrong,expression_integer) = ($(-22))',
    '$lossy_optional_integer_default_in(plenv_wrong,expression_joined) = ($(-2))',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_joined)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],2)',
    '~$lossy_mixed_parameter_source_valid(S[.CURRENT = (pcallcontext[.HOLES = [1,2]])],ptask_resume)',
    'S_two_owners = S[.ENV = (BIND $ptascii("extraStoredStringOwner247") n_cell) :: S.ENV]',
    '$heap_owners($heap_graph(S_two_owners),HCELL n_cell) = 2',
    '~$lossy_mixed_parameter_ready(S_two_owners,0,n_cell,n_bits)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    'S_first.TODO = [TYPE_RECEIVE porigin 1]',
])
previous = 'S_first'
for index, label, integer in [(1, 'integer', '$(-22)'), (2, 'joined', '$(-21)'), (3, 'nested', '22')]:
    checks.extend([
        f'PhpStep: {previous} ~> S_{label}',
        rf'S_{label}.TODO = [TYPE_RECEIVE porigin {index + 1}] /\ S_{label}.STORE[n_local_{label}] = DEFINED (PINT {integer})',
        rf'S_{label}.DEFAULTCACHE = S.DEFAULTCACHE /\ S_{label}.EVENTS = {previous}.EVENTS',
    ])
    previous = f'S_{label}'
checks.extend([
    'S_done = $drive_steps(S_nested,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$lookup(S_done.ENV,$ptascii("xAlias247")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_integer) = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_nested) = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_joined) = (pdefaultcache_joined)',
])
for label in ('integer', 'joined', 'nested'):
    checks.append(rf'~((HCELL n_local_{label}) <- S_done.ALLOCATIONS) /\ $heap_owners($heap_graph(S_done),HCELL n_local_{label}) = 0')
checks.extend([
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_last) <- S_done.ALLOCATIONS)',
    r'$heap_valid($heap_graph(S_done)) /\ $call_descriptors_valid(S_done) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
])

# Pure certificates expose the new domain and preserve all FLOAT distinctions.
negate = lambda expression: node('NExprUnaryMinus', expression)
stored = [(string('22'), '$(-22)'), (string('-22'), '22'), (string('0'), '0'),
          (string('-0'), '0'), (string(' 22 '), '$(-22)'),
          (string('9223372036854775807'), '$(-9223372036854775807)'),
          (binary('Concat', string('2'), string('2')), '$(-22)'),
          (node('NExprCastString', node('NExprCastInt', constant('E_WARNING'))), '$(-2)')]
derived = []
for child, integer in stored:
    parent = negate(child)
    derived.extend([
        f'$lossy_optional_integer_default_in($plempty(false),{parent}) = ({integer})',
        f'$lossy_optional_integer_numeric($plempty(false),{parent}) = (NINT {integer})',
    ])
for child, number in [(string('2.0'), 'NFLOAT $hex_bits("c000000000000000",0)'),
                      (string('2e0'), 'NFLOAT $hex_bits("c000000000000000",0)'),
                      (string('-0.0'), 'NFLOAT 0'),
                      (string('0.0'), 'NFLOAT 9223372036854775808'),
                      (string('-2.5'), 'NFLOAT 4612811918334230528'),
                      (string('-9223372036854775808'), 'NFLOAT 4890909195324358656')]:
    parent = negate(child)
    derived.extend([
        f'$lossy_optional_integer_default_in($plempty(false),{parent}) = eps',
        f'$lossy_optional_integer_numeric($plempty(false),{parent}) = ({number})',
    ])
for child in [string('2tail'), string('bad'), string(''), constant('true'), constant('null')]:
    derived.append(f'$lossy_optional_integer_default_in($plempty(false),{negate(child)}) = eps')
inner = negate(string('2'))
cast_inner = node('NExprCastString', inner)
concat = binary('Concat', cast_inner, string('1'))
dimension = node('NExprArrayDimFetch', string('12'), 'NScalarInt (INTEGER 0) eps')
derived.extend([
    f'$lossy_optional_integer_string_in($plempty(false),{cast_inner}) = ([45,50])',
    f'$lossy_optional_integer_default_in($plempty(false),{node("NExprCastInt", concat)}) = ($(-21))',
    f'$lossy_optional_integer_default_in($plempty(false),{binary("Plus", negate(string("22")), "NScalarInt (INTEGER 1) eps")}) = ($(-21))',
    f'$lossy_optional_integer_default_in($plempty(false),{negate(negate(string("22")))}) = (22)',
    f'$lossy_optional_integer_default_in($plempty(false),{node("NExprUnaryPlus", inner)}) = ($(-2))',
    f'$lossy_optional_integer_default_in($plempty(false),{node("NExprUnaryPlus", string("2"))}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{node("NExprUnaryPlus", string("2"))}) = eps',
    f'$lossy_optional_integer_string_in($plempty(false),{dimension}) = ([49])',
    f'~$lossy_optional_integer_quiet_shape({dimension})',
    f'$lossy_optional_integer_default_in($plempty(false),{negate(dimension)}) = eps',
    f'$lossy_optional_integer_numeric($plempty(false),{negate(dimension)}) = (NINT $(-1))',
    '$lossy_optional_integer_default_in($plempty(false),NExprUnaryMinus (NScalarString (BYTES "MgA=") eps) eps) = eps',
])


if __name__ == '__main__':
    import closure_call_protocol as protocol

    rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
    for row in rows.values():
        assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
    cases = {
        'integer-string-unary-minus-named-stored-deferred-front': {
            'source': rows['integer-string-unary-minus-alias-composition-reentry']['source'],
            'stage': ('S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z] '
                      '-- if S.CURRENT = (pcallcontext) -- if pcallcontext.HOLES = [1,2,3]'),
            'checks': checks,
        },
        'integer-string-unary-minus-derived-boundaries': {
            'source': '<?php ;',
            'stage': r'S.COMPLETION = NORMAL /\ S.TODO = eps',
            'checks': derived,
        },
    }
    protocol.run(cases, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
