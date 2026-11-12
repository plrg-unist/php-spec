"""Authenticate the first literal carrier in the preserved failing original."""
import json

PREFIX = r'''
dec $aaliteral_review_stage(pstate) : bool
def $aaliteral_review_stage(S) = true
  -- if S.TODO = (ACCESS_RESULT paccess) :: ptask*
  -- if paccess.PHASE = ACCESS_CALL $ptascii("offsetExists")
def $aaliteral_review_stage(S) = false -- otherwise
dec $aaliteral_review_seek(pstate, nat) : pstate
def $aaliteral_review_seek(S, n) = S
  -- if $aaliteral_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $aaliteral_review_seek(S, n) = $aaliteral_review_seek($drive_steps(S[.COMPLETION = NORMAL], 1), $nabs($(n - 1)))
  -- if ~$aaliteral_review_stage(S)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $(n > 0)
def $aaliteral_review_seek(S, n) = S
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
        'S_paused = $aaliteral_review_seek(S_initial[.COMPLETION = NORMAL], 1000)',
        'S = S_paused[.COMPLETION = NORMAL]',
        'S.TODO = (ACCESS_RESULT paccess) :: ptask_tail*',
        'paccess.MODE = ACCESS_READ (KEY_TEST false)',
        'paccess.PHASE = ACCESS_CALL $ptascii("offsetExists")',
        'paccess.INPUT = KNOWN (PSTRING_CARRIER INTERNED_STRING n_bytes*)',
        'paccess.OFFSET = PSTRING_CARRIER INTERNED_STRING n_bytes*',
        'n_bytes* = $ptascii("a")',
        '$origin_child((paccess.TARGET), [PCFIELD 1]) = (porigin_key)',
        '$compiled_read(S, porigin_key) = (PSTRING n_bytes*)',
        '$compiled_precision(S, (porigin_key)) = (z_precision)',
        '$origin_node(S.SOURCES, porigin_key) = (expression_key)',
        '$parser_literal_at(expression_key, z_precision) = (PSTRING n_bytes*)',
        '$compiled_string_value(S, porigin_key, PSTRING n_bytes*) = PSTRING_CARRIER INTERNED_STRING n_bytes*',
        '$key_write_input_source(S, paccess.TARGET, paccess.INPUT, paccess.KEYLINE, false)',
        'pkeyread = {SITE paccess.TARGET, GLOBAL false, MODE KEY_R, INPUT paccess.INPUT, VALUE PNULL, BASE PNULL, OWNERS BASE_VALUE (KNOWN PNULL), LINE paccess.KEYLINE, PHASE KEY_CV, KEY KSTRING eps, NAME eps}',
        '$key_read_input_source(S, pkeyread)',
        '$key_read_input_source(S, pkeyread[.INPUT = KNOWN (PSTRING n_bytes*)])',
        '~$key_read_input_source(S, pkeyread[.INPUT = KNOWN (PSTRING_CARRIER INTERNED_STRING (n_bytes* ++ [120]))])',
        '~$key_read_input_source(S, pkeyread[.GLOBAL = true])',
        'n_request = |S.STRINGDATA|',
        'S_request = S[.STRINGDATA = S.STRINGDATA ++ [n_bytes*]]',
        'pvalue_request = PSTRING_CARRIER (REQUEST_STRING n_request) n_bytes*',
        '$string_carrier_valid(S_request, pvalue_request)',
        '$heap_graph(S_request) = $heap_graph(S)',
        '~$key_read_input_source(S_request, pkeyread[.INPUT = KNOWN pvalue_request])',
        'S_originless = S[.SOURCES = eps]',
        '$compiled_read(S_originless, porigin_key) = (PSTRING n_bytes*)',
        '$compiled_string_value(S_originless, porigin_key, PSTRING n_bytes*) = PSTRING n_bytes*',
        '~$key_read_input_source(S_originless, pkeyread)',
        '$access_source(S, paccess)',
        '$access_valid(S, paccess)',
        'S.CURRENT = eps',
        'S.FRAMES = eps',
        'S.RESULT = REFERENCE n_return',
        'S.STORE[n_return] = DEFINED (PBOOL true)',
        '$heap_owners($heap_graph(S), HCELL n_return) = 2',
        *guards('S'),
        'PhpStep: S ~> S_next',
        'S_next.COMPLETION = NORMAL',
        'S_next.RESULT = KNOWN (PINT 1)',
        'S_next.TODO = ptask_tail*',
        'S_next.EVENTS = S.EVENTS',
        'S_next.STORE = S.STORE',
        'S_next.ALLOCATIONS = S.ALLOCATIONS',
        'S_next.SOURCES = S.SOURCES',
        'S_next.POOLS = S.POOLS',
        '$heap_owners($heap_graph(S_next), HCELL n_return) = 1',
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
        'S_one.SOURCES = S.SOURCES',
        'S_one.POOLS = S.POOLS',
        '$heap_owners($heap_graph(S_one), HCELL n_return) = 1',
        *guards('S_one'),
    ]
    return (PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(
        '  -- ' + (check if check.startswith('PhpStep:') else 'if ' + check) + '\n'
        for check in checks), len(checks))
