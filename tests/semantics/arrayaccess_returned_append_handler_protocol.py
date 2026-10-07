"""Broad original's reached warning authentication, entry and provider finish."""
import base64
import json

from error_handler_protocol import PREFIX


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
        'n_opened* = ' + octets(bytes(companion)),
        'n_filebytes* = ' + octets(companion.read_bytes()),
        'S_initial = $php_file_run(' + main_fixture + ', 0, n_caller*, '
        + octets(bytes(cwd)) + ')',
        'S_initial.COMPLETION = BUDGET',
        'S_pending = $seek(S_initial, 2000)',
        'S = S_pending[.COMPLETION = NORMAL]',
        'S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand',
        'perrorcall.LEVEL = 2',
        'perrorcall.MESSAGE = $ptascii("Array to string conversion")',
        'perrorcall.TARGET = eps',
        'S.ERRORHANDLER.CALLBACK = (perrorcall.CALLBACK)',
        '$error_call_valid(S, perrorcall)',
        '$call_task_valid(S, ERROR_HANDLER_INVOKE perrorcall)',
        '$error_handler_target(S, perrorcall.CALLBACK) = (pcalltarget)',
        '$target_function(S, pcalltarget) = (pfunction)',
        '~pfunction.SIGNATURE.BYREF',
        *guards('S'),
        'perrorcall_line = perrorcall[.LINE = $(perrorcall.LINE + 1)]',
        'S_line = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_line) :: ptask_tail*]',
        '$heap_graph(S_line) = $heap_graph(S)',
        '~$error_call_valid(S_line, perrorcall_line)',
        '~$call_task_valid(S_line, ERROR_HANDLER_INVOKE perrorcall_line)',
        'perrorcall_site = perrorcall[.SITE = PORIGIN 0 eps]',
        'S_site = S[.ORIGIN = (PORIGIN 0 eps)][.TODO = (ERROR_HANDLER_INVOKE perrorcall_site) :: ptask_tail*]',
        '$heap_graph(S_site) = $heap_graph(S)',
        '~$error_call_valid(S_site, perrorcall_site)',
        '~$call_task_valid(S_site, ERROR_HANDLER_INVOKE perrorcall_site)',
        'perrorcall_resume = perrorcall[.RESUME = SOURCE_ARRAY_RESULT psourceoperand[.LINE = $(psourceoperand.LINE + 1)]]',
        'S_resume = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_resume) :: ptask_tail*]',
        '$heap_graph(S_resume) = $heap_graph(S)',
        '~$error_call_valid(S_resume, perrorcall_resume)',
        '~$call_task_valid(S_resume, ERROR_HANDLER_INVOKE perrorcall_resume)',
        'perrorcall_callback = perrorcall[.CALLBACK = PNULL]',
        'S_callback = S[.TODO = (ERROR_HANDLER_INVOKE perrorcall_callback) :: ptask_tail*]',
        '$error_call_valid(S_callback, perrorcall_callback)',
        '~$call_task_valid(S_callback, ERROR_HANDLER_INVOKE perrorcall_callback)',
        'S_callback_rejected = $drive(S_callback, 0)',
        'S_callback_rejected.COMPLETION = UNSUPPORTED "invalid compiled function descriptor"',
        'S_callback_rejected.TODO = eps',
        'S_callback_rejected.STORE = S.STORE',
        'PhpStep: S ~> S_entered',
        'S_entered.COMPLETION = NORMAL',
        'S_entered.ERRORHANDLER.CALLBACK = eps',
        'S_entered.CURRENT = (pcallcontext)',
        'pcallcontext.TARGET = pcalltarget',
        'pcallcontext.ARGC = 4',
        '$error_context_valid(S_entered, pcallcontext)',
        'S_entered.FRAMES = pframe :: pframe_tail*',
        'pframe.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered = perrorcall[.TARGET = (pcalltarget)]',
        'S_one = $drive(S, 1)',
        'S_one.COMPLETION = BUDGET',
        'S_one.CURRENT = S_entered.CURRENT',
        'S_one.TODO = S_entered.TODO',
        *guards('S_one'),
        'S_wait = $drive(S_one[.COMPLETION = NORMAL], 2000)',
        'S_wait.COMPLETION = SOURCE_PENDING',
        'S_wait.FILECONTEXTS = pfilecontext_wait :: eps',
        'pfilecontext_wait.PHASE = FILE_RESOLVE_WAIT',
        'pfilecontext_wait.REQUESTED = $ptascii("Array")',
        'S_parse = $file_open_continue(S_wait, (FILE_OPENED pfilecontext_wait.NONCE '
        'n_caller* $ptascii("Array") n_opened* n_opened* n_filebytes*))',
        'S_parse.COMPLETION = SOURCE_PENDING',
        'S_parse.FILECONTEXTS = pfilecontext_parse :: eps',
        'pfilecontext_parse.PHASE = FILE_PARSE_WAIT',
        'pfilecontext_parse.UNIT = (n_unit)',
        'S_done = $file_parse_continue(S_parse, (SOURCE_ACCEPT n_unit '
        'n_filebytes* ' + child_fixture + '))',
        'S_done.COMPLETION = NORMAL',
        'S_done.TODO = eps',
        'S_done.FILECONTEXTS = eps',
        'S_done.DESTRUCTION.OPERATIONS = eps',
        *guards('S_done'),
        '$outputs(S_done.EVENTS) = ' + str(list(expected)),
    ]
    stage = ('S.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail* '
             '-- if perrorcall.RESUME = SOURCE_ARRAY_RESULT psourceoperand')
    fixture = PREFIX.replace('STAGE', stage)
    fixture += 'dec $main() : bool\ndef $main() = true\n'
    fixture += ''.join('  -- ' + ('' if check.startswith('PhpStep: ') else 'if ')
                      + check + '\n' for check in checks)
    return fixture, checks
