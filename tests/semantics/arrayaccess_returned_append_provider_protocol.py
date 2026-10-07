"""Reached file-service rejection and one-step replay on the actual source."""
import base64
import json


def octets(value):
    return '$base64(' + json.dumps(base64.b64encode(value).decode()) + ')'


def guards(state):
    return [f'$call_current_valid({state})',
            f'$call_frames_valid({state}, {state}.FRAMES)',
            f'$call_descriptors_valid({state})',
            f'$heap_valid($heap_graph({state}))']


def render(main_fixture, child_fixture, source, companion, cwd, expected):
    checks = [
        'n_caller* = ' + octets(bytes(source)),
        'n_child_file* = ' + octets(bytes(companion)),
        'n_filebytes* = ' + octets(companion.read_bytes()),
        'S_wait = $php_file_run(' + main_fixture + ', 2000, n_caller*, '
        + octets(bytes(cwd)) + ')',
        'S_wait.COMPLETION = SOURCE_PENDING',
        'S_wait.FILECONTEXTS = pfilecontext_wait :: eps',
        'pfilecontext_wait.PHASE = FILE_RESOLVE_WAIT',
        'pfilecontext_wait.CALLER = n_caller*',
        'pfilecontext_wait.REQUESTED = $ptascii("Array")',
        'n_nonce = pfilecontext_wait.NONCE',
        *guards('S_wait'),
        'pfileopenresponse = FILE_OPENED n_nonce n_caller* $ptascii("Array") '
        'n_child_file* n_child_file* n_filebytes*',
        'S_bad_nonce = $file_open_resume(S_wait, (FILE_OPENED $(n_nonce + 1) '
        'n_caller* $ptascii("Array") n_child_file* n_child_file* n_filebytes*))',
        'S_bad_nonce.COMPLETION = UNSUPPORTED "invalid file resolution response"',
        'S_bad_nonce.TODO = S_wait.TODO',
        'S_bad_caller = $file_open_continue(S_wait, (FILE_OPENED n_nonce '
        '$ptascii("forged") $ptascii("Array") n_child_file* n_child_file* n_filebytes*))',
        'S_bad_caller.COMPLETION = UNSUPPORTED "invalid file resolution response"',
        'S_bad_caller.STORE = S_wait.STORE',
        'S_stale = S_wait[.FILESEQ = $(S_wait.FILESEQ + 1)]',
        '$heap_graph(S_stale) = $heap_graph(S_wait)',
        '~$call_descriptors_valid(S_stale)',
        'S_bad_state = $file_open_resume(S_stale, pfileopenresponse)',
        'S_bad_state.COMPLETION = UNSUPPORTED "invalid file resolution response"',
        'S_bad_state.ALLOCATIONS = S_wait.ALLOCATIONS',
        'S_parse = $file_open_continue(S_wait[.SERVICELEFT = (1)], pfileopenresponse)',
        'S_parse.COMPLETION = SOURCE_PENDING',
        'S_parse.SERVICELEFT = (1)',
        'S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
        'pfilecontext_parse.PHASE = FILE_PARSE_WAIT',
        'pfilecontext_parse.NONCE = n_nonce',
        'pfilecontext_parse.UNIT = (n_unit)',
        'pfilecontext_parse.BYTES = (n_filebytes*)',
        *guards('S_parse'),
        'S_bad_unit = $file_parse_resume(S_parse, (SOURCE_ACCEPT $(n_unit + 1) '
        'n_filebytes* ' + child_fixture + '))',
        'S_bad_unit.COMPLETION = UNSUPPORTED "invalid file parser response"',
        'S_bad_bytes = $file_parse_continue(S_parse, (SOURCE_ACCEPT n_unit '
        '$ptascii("forged") ' + child_fixture + '))',
        'S_bad_bytes.COMPLETION = UNSUPPORTED "invalid file parser response"',
        'S_bad_bytes.TODO = S_parse.TODO',
        'S_budget = $file_parse_continue(S_parse, (SOURCE_ACCEPT n_unit '
        'n_filebytes* ' + child_fixture + '))',
        'S_budget.COMPLETION = BUDGET',
        *guards('S_budget'),
        'S_done = $drive(S_budget[.COMPLETION = NORMAL], 2000)',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        'S_done.FILECONTEXTS = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        *guards('S_done'),
        '$outputs(S_done.EVENTS) = ' + str(list(expected)),
    ]
    fixture = 'dec $main() : bool\ndef $main() = true\n'
    fixture += ''.join('  -- if ' + check + '\n' for check in checks)
    return fixture, checks
