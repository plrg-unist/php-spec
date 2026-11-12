"""Check literal-base source permission at one existing Warning continuation."""
import json

PREFIX = r'''
dec $literal_base_review_stage(pstate) : bool
def $literal_base_review_stage(S) = true
  -- if S.TODO = (STRING_READ_RESULT pstringread) :: ptask*
  -- if pstringread.PHASE = STRING_CAST
def $literal_base_review_stage(S) = false -- otherwise
dec $literal_base_review_seek(pstate, nat) : pstate
def $literal_base_review_seek(S, n) = S
  -- if $literal_base_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $literal_base_review_seek(S, n) = $literal_base_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$literal_base_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $literal_base_review_seek(S, n) = S
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
'''


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def render(program, filename_b64):
    checks = [
        'S_initial = $php_run(' + program + ', 0, ' + json.dumps(filename_b64) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_paused = $literal_base_review_seek(S_initial[.COMPLETION = NORMAL], 1000)',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = (STRING_READ_RESULT pstringread) :: ptask_tail*',
        'pstringread.PHASE = STRING_CAST',
        'pstringread.READ.MODE = KEY_R',
        'pstringread.READ.BASE = PSTRING_CARRIER INTERNED_STRING n_bytes*',
        'n_bytes* = $ptascii("abc")',
        'pstringread.READ.OWNERS = BASE_VALUE (KNOWN pstringread.READ.BASE)',
        'pstringread.BASECELL = eps',
        'pstringread.KEYCELL = (n_key)',
        'pstringread.READ.INPUT = VARIABLE ($ptascii("offset")) pstringread.READ.LINE',
        '$lookup(S.ENV, $ptascii("offset")) = (n_key)',
        'S.STORE[n_key] = DEFINED pstringread.READ.VALUE',
        'pstringread.READ.VALUE = PFLOAT n_float',
        '~(n_key <- S.REFCELLS)',
        '$heap_owners($heap_graph(S), HCELL n_key) = 1',
        '~$key_base_cv_source(S, pstringread.READ.SITE)',
        '$origin_child((pstringread.READ.SITE), [PCFIELD 0]) = (porigin_base)',
        '$compiled_read(S, porigin_base) = (PSTRING n_bytes*)',
        '$compiled_precision(S, (porigin_base)) = (z_precision)',
        '$origin_node(S.SOURCES, porigin_base) = (expression_base)',
        '$parser_literal_at(expression_base, z_precision) = (PSTRING n_bytes*)',
        '$compiled_string_value(S, porigin_base, PSTRING n_bytes*) = pstringread.READ.BASE',
        '$key_read_owners_source(S, pstringread.READ)',
        'pkeyread_raw = pstringread.READ[.BASE = PSTRING n_bytes*][.OWNERS = BASE_VALUE (KNOWN (PSTRING n_bytes*))]',
        '$key_read_owners_source(S, pkeyread_raw)',
        'pvalue_wrong = PSTRING_CARRIER INTERNED_STRING (n_bytes* ++ [120])',
        'pkeyread_wrong = pstringread.READ[.BASE = pvalue_wrong][.OWNERS = BASE_VALUE (KNOWN pvalue_wrong)]',
        '~$key_read_owners_source(S, pkeyread_wrong)',
        '~$key_read_owners_source(S, pstringread.READ[.GLOBAL = true])',
        'pkeyread_cv = pstringread.READ[.OWNERS = BASE_VALUE (VARIABLE ($ptascii("offset")) pstringread.READ.LINE)]',
        '~$key_read_owners_source(S, pkeyread_cv)',
        'n_request = |S.STRINGDATA|',
        'S_request = S[.STRINGDATA = S.STRINGDATA ++ [n_bytes*]]',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) n_bytes*',
        '$string_carrier_valid(S_request, pvalue_request)',
        '$heap_graph(S_request) = $heap_graph(S)',
        'pkeyread_request = pstringread.READ[.BASE = pvalue_request][.OWNERS = BASE_VALUE (KNOWN pvalue_request)]',
        '~$key_read_owners_source(S_request, pkeyread_request)',
        '$string_read_provider_ready(S_request, pstringread[.READ = pkeyread_request])',
        '~$string_read_source(S_request, pstringread[.READ = pkeyread_request])',
        'S_originless = S[.SOURCES = eps]',
        '$compiled_read(S_originless, porigin_base) = (PSTRING n_bytes*)',
        '$compiled_string_value(S_originless, porigin_base, PSTRING n_bytes*) = PSTRING n_bytes*',
        '~$key_read_owners_source(S_originless, pstringread.READ)',
        '$string_read_source(S, pstringread)',
        '$string_read_provider_ready(S, pstringread)',
        '$string_read_key_current(S, pstringread) = (pstringread.READ.VALUE)',
        '$string_read_ready(S, pstringread)',
        '$string_read_offset(pstringread.READ.VALUE) = (1)',
        '$base_nodes(pstringread.READ.OWNERS) = eps',
        '$task_nodes(STRING_READ_RESULT pstringread) = eps',
        'S.CURRENT = eps',
        'S.FRAMES = eps',
        *guards('S'),
        'pstringread_line = pstringread[.READ.LINE = $(pstringread.READ.LINE + 1)]',
        '~$call_task_valid(S, STRING_READ_RESULT pstringread_line)',
        'PhpStep: S ~> S_next',
        'S_next.COMPLETION = NORMAL',
        'S_next.TODO = ptask_tail*',
        'S_next.RESULT = KNOWN (PSTRING_CARRIER INTERNED_STRING ($ptascii("b")))',
        'S_next.EVENTS = S.EVENTS',
        'S_next.STORE = S.STORE',
        'S_next.ALLOCATIONS = S.ALLOCATIONS',
        'S_next.SOURCES = S.SOURCES',
        'S_next.POOLS = S.POOLS',
        '$heap_owners($heap_graph(S_next), HCELL n_key) = 1',
        *guards('S_next'),
        'S_zero = $drive_steps(S, 0)',
        'S_zero = S[.COMPLETION = BUDGET]',
        'S_one = $drive_steps(S, 1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.RESULT = S_next.RESULT',
        'S_one.TODO = S_next.TODO',
        'S_one.CURRENT = S_next.CURRENT',
        'S_one.FRAMES = S_next.FRAMES',
        'S_one.EVENTS = S_next.EVENTS',
        'S_one.STORE[n_key] = S.STORE[n_key]',
        'S_one.SOURCES = S.SOURCES',
        'S_one.POOLS = S.POOLS',
        '$heap_owners($heap_graph(S_one), HCELL n_key) = 1',
        *guards('S_one'),
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
