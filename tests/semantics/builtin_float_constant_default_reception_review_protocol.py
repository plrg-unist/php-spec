#!/usr/bin/env python3
"""Independent genuine deferred-default reentry and cache boundary checks."""
import base64
import hashlib
import json
from pathlib import Path

metadata_index = 0


def node(tag, *children):
    global metadata_index
    metadata_index += 1
    return tag + ''.join(f' ({child})' for child in children) + f' metadata_extra_{metadata_index}'


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


def constant(value):
    return node('NExprConstFetch', node('NName', f'BYTES "{base64.b64encode(value.encode()).decode()}"'))


def string(value):
    return node('NScalarString', f'BYTES "{base64.b64encode(value.encode()).decode()}"')


def floating():
    return node('NScalarFloat', 'FLOAT "3fe0000000000000"')


def cast(value):
    return node('NExprCastInt', value)


def binary(kind, left, right):
    return node('NExprBinaryOp' + kind, left, right)


def finite_not():
    return cast(node('NExprBooleanNot', floating()))


pattern_b = finite_not()
yes_c = constant('YesReentry221')
pattern_c = cast(node('NExprBooleanNot', binary('Div', cast(yes_c), integer(2))))
inf_d = constant('InfinityReentry221')
pattern_d = node('NExprTernary', inf_d, integer(17), constant('UnselectedReentry221'))
pattern_e = integer(9)
negative_patterns = [
    ('builtin', 'directIntegerBuiltinReentry221', constant('PHP_INT_SIZE'), 'eps'),
    ('dimfinite', 'trailingFloatNotOffsetReentry221', cast(node('NExprArrayDimFetch', string('12'), binary('Concat', node('NExprCastString', binary('Plus', integer(1), finite_not())), string('tail')))), '(2)'),
    ('dimnan', 'trailingNanOffsetReentry221', cast(node('NExprArrayDimFetch', string('12'), binary('Concat', node('NExprCastString', cast(binary('NotIdentical', constant('NAN'), constant('NAN')))), string('tail')))), '(2)'),
]

values = {'b': '0', 'c': '0', 'd': '17'}
checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.NAME = $ptascii("receiveReentry221")',
    'plenv_source = pfunction.ENV',
    r'plenv_source.NAMESPACE = eps /\ plenv_source.CONSTANTS = [($ptascii("YesReentry221"),$ptascii("true")),($ptascii("NoReentry221"),$ptascii("false")),($ptascii("InfinityReentry221"),$ptascii("INF"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_a,psparam_b,psparam_c,psparam_d,psparam_e]',
    r'psparam_a.REQUIRED /\ psparam_a.DEFAULT = PSNONE /\ ~psparam_a.BYREF',
    '$default_at(pfunction.DEFAULTS,0) = eps',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps /\ pcallcontext.NAMED = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$default_caches_valid(S,S.DEFAULTCACHE)',
]
for index, letter, pattern, projection in [
    (1, 'b', pattern_b, '(0)'), (2, 'c', pattern_c, '(0)'), (3, 'd', pattern_d, '(17)'),
]:
    checks.extend([
        rf'~psparam_{letter}.REQUIRED /\ ~psparam_{letter}.VARIADIC /\ $ptmasks(psparam_{letter}.TYPE) = ["int"]',
        f'psparam_{letter}.DEFAULT = PSDEFAULT expression_{letter} "deferred"',
        f'expression_{letter} = {pattern}',
        f'$default_parameter_origin(S,porigin,{index}) = PORIGIN n_unit pcpath_{letter}',
        f'porigin_{letter} = PORIGIN n_unit (pcpath_{letter} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{letter}) = (expression_{letter})',
        f'$default_at(pfunction.DEFAULTS,{index}) = ({{INDEX {index},ORIGIN porigin_{letter},KIND PDDEFERRED}})',
        rf'$compiled_read(S,porigin_{letter}) = eps /\ $pool_value(S.POOLS,porigin_{letter}) = eps',
        f'$lossy_optional_integer_default_in(plenv_source,expression_{letter}) = {projection}',
        f'$default_current_cache(S,porigin_{letter}) = ({{ORIGIN porigin_{letter},VALUE PINT {values[letter]},CLASS PVSCALAR}})',
        f'~$default_scope_dependent(S,porigin_{letter})',
        f'$default_at(pfunction.DEFAULTS,{index}) = (pdefault_{letter})',
        f'$default_receive_recipient(S,pfunction,pdefault_{letter})',
        f'$lookup(S.ENV,psparam_{letter}.NAME) = eps',
    ])
checks.extend([
    r'psparam_b.BYREF /\ ~psparam_c.BYREF /\ psparam_d.BYREF',
    'psparam_e.DEFAULT = PSDEFAULT expression_e "int"',
    f'expression_e = {pattern_e}',
    '$default_parameter_origin(S,porigin,4) = PORIGIN n_unit pcpath_e',
    'porigin_e = PORIGIN n_unit (pcpath_e ++ [PCFIELD 6])',
    '$origin_node(S.SOURCES,porigin_e) = (expression_e)',
    '$default_at(pfunction.DEFAULTS,4) = ({INDEX 4,ORIGIN porigin_e,KIND PDSTORED})',
    '$compiled_read(S,porigin_e) = (PINT 9)',
    '$lossy_optional_integer_default_in(plenv_source,expression_e) = (9)',
    '$lookup(S.ENV,psparam_e.NAME) = eps',
    'porigin_inf_d = PORIGIN n_unit (pcpath_d ++ [PCFIELD 6,PCFIELD 0])',
    f'$origin_node(S.SOURCES,porigin_inf_d) = ({inf_d})',
    '$code_at(S.CODE,n_unit) = (pcode)',
    '$code_name(pcode.NAMES,pcpath_d ++ [PCFIELD 6,PCFIELD 0]) = (($ptascii("INF"),eps))',
    '$call_name_count(pcode.NAMES,pcpath_d ++ [PCFIELD 6,PCFIELD 0]) = 1',
    'porigin_yes_c = PORIGIN n_unit (pcpath_c ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0])',
    f'$origin_node(S.SOURCES,porigin_yes_c) = ({yes_c})',
    r'$pool_value(S.POOLS,porigin_yes_c) = (PBOOL true) /\ $compiled_read(S,porigin_yes_c) = eps /\ $code_name(pcode.NAMES,pcpath_c ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) = eps',
])
for suffix, name, pattern, projection in negative_patterns:
    checks.extend([
        f'$call_target(S,$ptascii("{name}"),eps) = (pfunction_{suffix})',
        f'pfunction_{suffix}.SIGNATURE.PARAMETERS = [psparam_{suffix}]',
        f'psparam_{suffix}.DEFAULT = PSDEFAULT expression_{suffix} "deferred"',
        f'expression_{suffix} = {pattern}',
        f'$default_parameter_origin(S,pfunction_{suffix}.ORIGIN,0) = PORIGIN n_unit pcpath_{suffix}',
        f'porigin_{suffix} = PORIGIN n_unit (pcpath_{suffix} ++ [PCFIELD 6])',
        f'$origin_node(S.SOURCES,porigin_{suffix}) = (expression_{suffix})',
        f'pfunction_{suffix}.DEFAULTS = [{{INDEX 0,ORIGIN porigin_{suffix},KIND PDDEFERRED}}]',
        rf'$compiled_read(S,porigin_{suffix}) = eps /\ $pool_value(S.POOLS,porigin_{suffix}) = eps',
        f'$lossy_optional_integer_default_in(pfunction_{suffix}.ENV,expression_{suffix}) = {projection}',
        f'~$lossy_optional_integer_header(S,pfunction_{suffix},[psparam_{suffix}],0)',
    ])
checks.extend([
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_a.NAME) = (n_a)',
    'S.STORE[n_a] = DEFINED (PFLOAT 4609434218613702656)',
    '~(n_a <- S.REFCELLS)',
    '$heap_owners($heap_graph(S),HCELL n_a) = 1',
    'z = $default_parameter_line(S,porigin,0)',
    r'$typed_receive_valid(S[.TODO = [TYPE_RECEIVE porigin 0]][.ORIGIN = (porigin)],porigin,0) /\ ~$typed_caller_strict(S)',
    '$lossy_mixed_parameter_ready(S,0,n_a,4609434218613702656)',
    '$lossy_mixed_parameter_metadata(S,porigin,0,z)',
    '$lossy_mixed_parameter_capture(S) = eps',
    r'S.EVENTS =/= eps /\ $call_descriptors_valid(S) /\ $heap_valid($heap_graph(S))',
])



# This is a new post-handler view. The same native-once original reentered its
# actual receiving function and filled the real future default cache.
checks.extend([
    r'n_cell = n_a /\ n_bits = 4609434218613702656 /\ i = 1',
    '$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$call_task_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
    '$lossy_mixed_parameter_capture(S[.TODO = [TYPE_RECEIVE porigin 0]][.ORIGIN = (porigin)]) = (LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '~$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits 2 z)',
    '~$lossy_mixed_parameter_source_valid(S[.ORIGIN = (porigin_e)],LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xReentry221")) = (n_x)',
    '$lookup(psymboltable_global.ENV,$ptascii("depthReentry221")) = (n_depth)',
    'S.STORE[n_x] = DEFINED (PFLOAT 4615063718147915776)',
    'S.STORE[n_depth] = DEFINED (PINT 0)',
    '$default_current_cache(S,porigin_e) = eps',
])
for index, letter in [(1, 'b'), (2, 'c'), (3, 'd')]:
    checks.extend([
        f'$lossy_optional_integer_quiet_shape(expression_{letter})',
        f'$lossy_optional_integer_deferred_bindings(S,plenv_source,porigin_{letter})',
        f'$lossy_optional_integer_deferred(S,pfunction,{index})',
    ])
checks.extend([
    '~$lossy_optional_integer_deferred(S,pfunction,0)',
    '~$lossy_optional_integer_deferred(S,pfunction,4)',
    '~$lossy_optional_integer_deferred(S,pfunction,5)',
    '~$lossy_optional_integer_quiet_shape(expression_dimfinite)',
    '~$lossy_optional_integer_quiet_shape(expression_dimnan)',
    '$lossy_optional_integer_default_in(plenv_source,expression_dimfinite) = (2)',
    '$lossy_optional_integer_default_in(plenv_source,expression_dimnan) = (2)',
    'S_cold = S[.DEFAULTCACHE = eps]',
    '$lossy_optional_integer_deferred(S_cold,pfunction,1)',
    '$lossy_optional_integer_header(S_cold,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'pdefaultcache_good = {ORIGIN porigin_b,VALUE PINT 0,CLASS PVSCALAR}',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 8])]',
    '$default_caches_valid(S_wrong_value,S_wrong_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    '~$lossy_optional_integer_header(S_wrong_value,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PBOOL false])]',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_wrong_class = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.CLASS = PVSTRING false])]',
    '~$lossy_optional_integer_deferred(S_wrong_class,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_good])]',
    '~$default_caches_valid(S_duplicate,S_duplicate.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    'S_unknown_owner = S_cold[.CURRENT = (pcallcontext[.CACHE = (CACHE_SHARED)])]',
    r'$default_cache_owner(S_unknown_owner) = eps /\ $default_current_cache(S_unknown_owner,porigin_b) = eps',
    '~$lossy_optional_integer_deferred(S_unknown_owner,pfunction,1)',
    'S_private_owner = S_cold[.CURRENT = (pcallcontext[.CACHE = (CACHE_PRIVATE 0)])]',
    '~$lossy_optional_integer_deferred(S_private_owner,pfunction,1)',
    'S_call_owner = S_cold[.CURRENT = (pcallcontext[.CACHE = (CACHE_CALL 0)])]',
    '~$lossy_optional_integer_deferred(S_call_owner,pfunction,1)',
    'S_wrong_context = S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin)])]',
    '~$lossy_optional_integer_deferred(S_wrong_context,pfunction,1)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = $plempty(false)],1)',
    'plenv_wrong = plenv_source[.CONSTANTS = ([($ptascii("InfinityReentry221"),$ptascii("NAN"))])]',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_inf_d)',
    'S.CODE = [pcode]',
    'S_no_names = S[.CODE = ([pcode[.NAMES = eps]])]',
    '~$lossy_optional_integer_deferred_bindings(S_no_names,plenv_source,porigin_inf_d)',
    'pcodename_duplicate = CODENAME (pcpath_d ++ [PCFIELD 6,PCFIELD 0]) ($ptascii("INF")) eps',
    'S_duplicate_name = S[.CODE = ([pcode[.NAMES = (pcode.NAMES ++ [pcodename_duplicate])]])]',
    '~$lossy_optional_integer_deferred_bindings(S_duplicate_name,plenv_source,porigin_inf_d)',
])

# A contradictory late name on a folded special is outside the existing
# compiler-consistency boundary. The local borrowed fact is not a new parser.
checks.extend([
    'pcodename_forged = CODENAME (pcpath_c ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0,PCFIELD 0,PCFIELD 0]) ($ptascii("false")) eps',
    'S_forged = S[.CODE = ([pcode[.NAMES = (pcode.NAMES ++ [pcodename_forged])]])]',
    '~$call_descriptors_valid(S_forged)',
])

def literal_node(tag, *children):
    return tag + ''.join(f' ({child})' for child in children) + ' eps'


def literal_constant(value, qualified=False):
    return literal_node('NExprConstFetch', literal_node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{base64.b64encode(value.encode()).decode()}"'))


checks.extend([
    'plenv_root = $plempty(false)',
    'plenv_namespace = plenv_root[.NAMESPACE = $ptascii("Other")]',
    'plenv_import = plenv_namespace[.CONSTANTS = ([($ptascii("Alias"),$ptascii("NAN"))])]',
])
for environment, name, qualified, expected in [
    ('plenv_root', 'INF', False, '(NFLOAT 9218868437227405312)'),
    ('plenv_root', 'NAN', False, '(NFLOAT 9221120237041090560)'),
    ('plenv_root', 'inf', False, 'eps'),
    ('plenv_root', 'nan', False, 'eps'),
    ('plenv_root', 'INFX', False, 'eps'),
    ('plenv_root', 'PHP_INT_SIZE', False, 'eps'),
    ('plenv_root', 'PHP_OUTPUT_HANDLER_START', False, 'eps'),
    ('plenv_namespace', 'NAN', False, 'eps'),
    ('plenv_namespace', 'INF', True, '(NFLOAT 9218868437227405312)'),
    ('plenv_import', 'Alias', False, '(NFLOAT 9221120237041090560)'),
    ('plenv_import', 'alias', False, 'eps'),
    ('plenv_import', 'Other\\NAN', True, 'eps'),
]:
    checks.append(f'$lossy_optional_integer_numeric({environment},{literal_constant(name,qualified)}) = {expected}')
nan = literal_constant('NAN', True)
inf = literal_constant('INF', True)
for expression, helper, expected in [
    (nan, 'default_in', 'eps'), (inf, 'default_in', 'eps'),
    (nan, 'condition', 'eps'), (inf, 'condition', '(true)'),
    (literal_node('NExprCastInt', nan), 'default_in', 'eps'),
    (literal_node('NExprCastInt', inf), 'default_in', 'eps'),
    (literal_node('NExprCastDouble', nan), 'numeric', 'eps'),
    (literal_node('NExprBinaryOpIdentical', nan, nan), 'condition', '(false)'),
    (literal_node('NExprBinaryOpGreaterOrEqual', nan, inf), 'condition', '(false)'),
]:
    checks.append(f'$lossy_optional_integer_{helper}(plenv_root,{expression}) = {expected}')
checks.extend([
    '$builtin_value_bytes([73,78,70]) = (PFLOAT 9218868437227405312)',
    '$builtin_value_bytes([78,65,78]) = (PFLOAT 9221120237041090560)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_next',
    r'S_next.TODO = [TYPE_RECEIVE porigin 1] /\ S_next.STORE[n_a] = DEFINED (PINT 1)',
    r'S_next.EVENTS = S.EVENTS /\ S_next.DEFAULTCACHE = S.DEFAULTCACHE',
    'S_done = $drive_steps(S_next,2000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '~((HCELL n_a) <- S_done.ALLOCATIONS)',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_b) = ({ORIGIN porigin_b,VALUE PINT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_c) = ({ORIGIN porigin_c,VALUE PINT 0,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_d) = ({ORIGIN porigin_d,VALUE PINT 17,CLASS PVSCALAR})',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_e) = eps',
    '$lookup(S_done.ENV,$ptascii("gotReentry221")) = (n_got)',
    'S_done.STORE[n_got] = DEFINED (PINT 0)',
    'S_done.STORE[n_x] = DEFINED (PFLOAT 4615063718147915776)',
    'S_done.STORE[n_depth] = DEFINED (PINT 0)',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done))',
])

CATALOGUE = Path(__file__).with_name('builtin_float_constant_default_reception_cases.json')
row = next(row for row in json.loads(CATALOGUE.read_text()) if row['id'] == 'quiet-deferred-default-cache-reentry')
assert row['source_sha256'] == '2f336ff72b29f078a8233679d1067903c67d571c0d5961656ce15e8c8522fc5d'
assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
source = row['source'][:row['source'].index('$xReentry221 = 1.5;', row['source'].index("echo 'first-result:"))]
CASES = {'quiet-deferred-default-reentry-review': {
    'source': source,
    'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
    'checks': checks,
}}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
