#!/usr/bin/env python3
"""Independent integer truth and warm alias-default reentry checks."""
import base64
import hashlib
import json
from pathlib import Path


def node(tag, *children):
    return tag + ''.join(f' ({child})' for child in children) + ' eps'


def constant(name, qualified=False):
    encoded = base64.b64encode(name.encode()).decode()
    return node('NExprConstFetch', node('NNameFullyQualified' if qualified else 'NName', f'BYTES "{encoded}"'))


def integer(value):
    return node('NScalarInt', f'INTEGER {value}')


checks = [
    '$function_at(S.FUNCTIONS,porigin) = (pfunction)',
    'pfunction.ENV.NAMESPACE = $ptascii("TruthAlias226")',
    'pfunction.ENV.CONSTANTS = [($ptascii("Word226"),$ptascii("PHP_INT_SIZE"))]',
    'pfunction.SIGNATURE.PARAMETERS = [psparam_first,psparam_later]',
    r'psparam_first.REQUIRED /\ ~psparam_first.BYREF /\ ~psparam_later.BYREF',
    'S.CURRENT = (pcallcontext)',
    r'pcallcontext.FUNCTION = porigin /\ pcallcontext.TARGET = porigin',
    r'pcallcontext.ARGC = 1 /\ pcallcontext.HOLES = eps',
    r'pcallcontext.CACHE = eps /\ pcallcontext.WRAPPER = eps /\ pcallcontext.INSTANCE = eps',
    r'pcallcontext.DEFAULTRECEIVE = eps /\ S.CONSTCONTEXT = eps',
    '$default_cache_owner(S) = (CACHE_SHARED)',
    '$lookup(S.ENV,psparam_first.NAME) = (n_cell)',
    r'S.STORE[n_cell] = DEFINED (PFLOAT 4609434218613702656) /\ ~(n_cell <- S.REFCELLS)',
    '$heap_owners($heap_graph(S),HCELL n_cell) = 1',
    r'n_bits = 4609434218613702656 /\ i = 1',
    'z = $default_parameter_line(S,porigin,0)',
    '$lossy_mixed_parameter_source_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$lossy_mixed_parameter_ready(S,0,n_cell,n_bits)',
    '$call_task_valid(S,LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    '$task_nodes(LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z) = eps',
    'S.GLOBALTABLE = (psymboltable_global)',
    '$lookup(psymboltable_global.ENV,$ptascii("xAlias226")) = (n_global)',
    r'n_global =/= n_cell /\ S.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    'psparam_later.DEFAULT = PSDEFAULT expression_later "deferred"',
    '$default_parameter_origin(S,porigin,1) = PORIGIN n_unit pcpath_later',
    'porigin_later = PORIGIN n_unit (pcpath_later ++ [PCFIELD 6])',
    '$default_at(pfunction.DEFAULTS,1) = ({INDEX 1,ORIGIN porigin_later,KIND PDDEFERRED})',
    '$origin_node(S.SOURCES,porigin_later) = (expression_later)',
    r'$compiled_read(S,porigin_later) = eps /\ $pool_value(S.POOLS,porigin_later) = eps',
    '$lossy_optional_integer_default_in(pfunction.ENV,expression_later) = (37)',
    '$lossy_optional_integer_condition(pfunction.ENV,expression_later) = (true)',
    '$lossy_optional_integer_selection_shape(expression_later)',
    '$lossy_optional_integer_deferred_value(pfunction.ENV,expression_later) = (PINT 37)',
    '$lossy_optional_integer_deferred_bindings(S,pfunction.ENV,porigin_later)',
    'pdefaultcache_good = {ORIGIN porigin_later,VALUE PINT 37,CLASS PVSCALAR}',
    '$default_current_cache(S,porigin_later) = (pdefaultcache_good)',
    '$lossy_optional_integer_deferred(S,pfunction,1)',
    '$lossy_optional_integer_header(S,pfunction,pfunction.SIGNATURE.PARAMETERS,0)',
    '$lookup(S.ENV,psparam_later.NAME) = eps',
    '$origin_node(S.SOURCES,PORIGIN n_unit (pcpath_later ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0])) = (NExprConstFetch name_word metadata_word)',
    '$pnresolve(pfunction.ENV,PLCONSTANT,name_word) = PNRESOLVED pnreference_word',
    r'pnreference_word.RESOLVED = $ptascii("PHP_INT_SIZE") /\ pnreference_word.FALLBACK = eps',
    r'$call_descriptors_valid(S) /\ $heap_valid($heap_graph(S)) /\ $default_caches_valid(S,S.DEFAULTCACHE)',
    'S_cold = S[.DEFAULTCACHE = eps]',
    '$lossy_optional_integer_deferred(S_cold,pfunction,1)',
    'S_wrong_value = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PINT 17])]',
    '$default_caches_valid(S_wrong_value,S_wrong_value.DEFAULTCACHE)',
    '~$lossy_optional_integer_deferred(S_wrong_value,pfunction,1)',
    'S_wrong_tag = S[.DEFAULTCACHE = $default_cache_put(S.DEFAULTCACHE,pdefaultcache_good[.VALUE = PFLOAT 4630404104378646528])]',
    '~$lossy_optional_integer_deferred(S_wrong_tag,pfunction,1)',
    'S_duplicate = S[.DEFAULTCACHE = (S.DEFAULTCACHE ++ [pdefaultcache_good])]',
    '~$lossy_optional_integer_deferred(S_duplicate,pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.SOURCES = eps],pfunction,1)',
    '~$lossy_optional_integer_deferred(S[.FUNCTIONS = eps],pfunction,1)',
    'S.CODE = [pcode]',
    '~$lossy_optional_integer_deferred(S[.CODE = ([pcode[.NAMES = eps]])],pfunction,1)',
    'pcodename_duplicate = CODENAME (pcpath_later ++ [PCFIELD 6,PCFIELD 0,PCFIELD 0]) ($ptascii("PHP_INT_SIZE")) eps',
    'S_duplicate_name = S[.CODE = ([pcode[.NAMES = (pcode.NAMES ++ [pcodename_duplicate])]])]',
    '~$lossy_optional_integer_deferred_bindings(S_duplicate_name,pfunction.ENV,porigin_later)',
    'plenv_wrong = pfunction.ENV[.CONSTANTS = ([($ptascii("Word226"),$ptascii("PHP_INT_MAX"))])]',
    '$lossy_optional_integer_default_in(plenv_wrong,expression_later) = (17)',
    '~$lossy_optional_integer_deferred_bindings(S,plenv_wrong,porigin_later)',
    '~$lossy_optional_integer_deferred(S,pfunction[.ENV = plenv_wrong],1)',
    '$lossy_mixed_parameter_capture(S[.TODO = [TYPE_RECEIVE porigin 0]][.ORIGIN = (porigin)]) = (LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z)',
    'S_budget = $drive_steps(S,0)',
    'S_budget = S[.COMPLETION = BUDGET]',
    '$drive_steps(S_budget[.COMPLETION = NORMAL],1) = $drive_steps(S,1)',
    'PhpStep: S ~> S_first',
    r'S_first.TODO = [TYPE_RECEIVE porigin 1] /\ S_first.STORE[n_cell] = DEFINED (PINT 1)',
    r'S_first.STORE[n_global] = S.STORE[n_global] /\ S_first.DEFAULTCACHE = S.DEFAULTCACHE',
    'PhpStep: S_first ~> S_wait',
    'S_wait.TODO = [DEFAULT_RECEIVE porigin 1]',
    r'S_wait.STORE = S_first.STORE /\ S_wait.DEFAULTCACHE = S.DEFAULTCACHE /\ S_wait.EVENTS = S_first.EVENTS',
    'PhpStep: S_wait ~> S_later',
    '$lookup(S_later.ENV,psparam_later.NAME) = (n_later)',
    'S_later.STORE[n_later] = DEFINED (PINT 37)',
    'S_later.TODO = $call_receive_body(S_wait,pfunction)',
    r'S_later.DEFAULTCACHE = S.DEFAULTCACHE /\ S_later.EVENTS = S_wait.EVENTS /\ S_later.PARAMETERRECEIVES = S.PARAMETERRECEIVES',
    r'~(n_later <- S_later.REFCELLS) /\ $heap_owners($heap_graph(S_later),HCELL n_later) = 1',
    'S_done = $drive_steps(S_later,3000)',
    r'S_done.COMPLETION = NORMAL /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps /\ S_done.TODO = eps',
    '$default_cache_at(S_done.DEFAULTCACHE,porigin_later) = (pdefaultcache_good)',
    '$lookup(S_done.ENV,$ptascii("xAlias226")) = (n_global)',
    'S_done.STORE[n_global] = DEFINED (PFLOAT 4615063718147915776)',
    r'~((HCELL n_cell) <- S_done.ALLOCATIONS) /\ ~((HCELL n_later) <- S_done.ALLOCATIONS)',
    r'$heap_owners($heap_graph(S_done),HCELL n_cell) = 0 /\ $heap_owners($heap_graph(S_done),HCELL n_later) = 0',
    r'$call_descriptors_valid(S_done) /\ $heap_valid($heap_graph(S_done)) /\ $default_caches_valid(S_done,S_done.DEFAULTCACHE)',
]

root = '$plempty(false)'
word = constant('Word226')
zero = node('NExprBinaryOpMinus', word, integer(8))
unknown = constant('Unselected226')
for environment, expression, expected in [
    (root, constant('PHP_INT_MAX'), 'true'), (root, constant('PHP_INT_MIN'), 'true'),
    ('pfunction.ENV', word, 'true'), ('pfunction.ENV', zero, 'false'),
    ('pfunction.ENV', node('NExprCastBool', zero), 'false'),
    ('pfunction.ENV', node('NExprBooleanNot', word), 'false'),
]:
    checks.append(f'$lossy_optional_integer_condition({environment},{expression}) = ({expected})')
for kind, left, right, expected in [
    ('BooleanAnd', zero, unknown, '(false)'), ('BooleanOr', word, unknown, '(true)'),
    ('LogicalAnd', word, unknown, 'eps'), ('LogicalOr', zero, unknown, 'eps'),
    ('LogicalXor', zero, word, '(true)'),
]:
    checks.append(f'$lossy_optional_integer_condition(pfunction.ENV,{node("NExprBinaryOp" + kind,left,right)}) = {expected}')
selected = node('NExprTernary', zero, unknown, integer(37))
reached = node('NExprTernary', word, unknown, integer(37))
coalesce = node('NExprBinaryOpCoalesce', zero, unknown)
elvis = node('NExprTernary', word, 'ABSENT', integer(0))
checks.extend([
    f'$lossy_optional_integer_condition(pfunction.ENV,{selected}) = (true)',
    f'$lossy_optional_integer_default_in(pfunction.ENV,{selected}) = (37)',
    f'$lossy_optional_integer_condition(pfunction.ENV,{reached}) = eps',
    f'$lossy_optional_integer_condition(pfunction.ENV,{coalesce}) = (false)',
    f'$lossy_optional_integer_default_in(pfunction.ENV,{coalesce}) = eps',
    f'$lossy_optional_integer_condition(pfunction.ENV,{elvis}) = (true)',
    f'$lossy_optional_integer_default_in(pfunction.ENV,{elvis}) = eps',
    f'$lossy_optional_integer_condition(pfunction.ENV,{constant("PHP_INT_SIZE")}) = eps',
    f'$lossy_optional_integer_condition(pfunction.ENV,{constant("PHP_INT_SIZE",True)}) = (true)',
    f'$lossy_optional_integer_condition({root},{constant("php_int_size")}) = eps',
    f'$lossy_optional_integer_condition({root},{constant("NAN")}) = eps',
    f'$lossy_optional_integer_condition({root},{node("NExprBooleanNot",constant("NAN"))}) = eps',
    f'$lossy_optional_integer_condition({root},{integer("9223372036854775808")}) = eps',
])
dimension = node('NExprArrayDimFetch', node('NScalarString', 'BYTES "MTI="'), integer(0))
skipped_dimension = node('NExprTernary', zero, dimension, integer(37))
checks.extend([
    f'$lossy_optional_integer_default_in(pfunction.ENV,{skipped_dimension}) = (37)',
    f'~$lossy_optional_integer_quiet_shape({skipped_dimension})',
])

CATALOGUE = Path(__file__).with_name('immutable_integer_truth_default_reception_cases.json')
rows = {row['id']: row for row in json.loads(CATALOGUE.read_text())}
for row in rows.values():
    assert hashlib.sha256(row['source'].encode()).hexdigest() == row['source_sha256']
CASES = {
    'immutable-integer-truth-alias-reentry': {
        'source': rows['immutable-integer-truth-default-alias-reentry']['source'],
        'stage': 'S.TODO = [LOSSY_MIXED_PARAMETER_RECEIVE porigin 0 n_cell n_bits i z]',
        'checks': checks,
    },
}

if __name__ == '__main__':
    import closure_call_protocol as protocol
    protocol.run(CASES, extra_inputs=(Path(__file__), CATALOGUE), runner_flags=('--sl',))
