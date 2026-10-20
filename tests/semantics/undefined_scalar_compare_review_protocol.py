"""Independent live-right references, frozen NULL and source-domain controls."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as SHARED_PREFIX, text

PREFIX = SHARED_PREFIX + r'''
dec $uc_stage(pstate, nat) : bool
def $uc_stage(S, 0) = true
  -- if $error_read_plan(S) = (perrorread)
  -- if perrorread.ORIGINAL = BINARY_RIGHT pbin poperand z
  -- if pbin = EQUAL \/ pbin = LESS
def $uc_stage(S, n) = $us_stage(S, n) -- if n =/= 0
def $uc_stage(S, n) = false -- otherwise
dec $uc_seek(pstate, nat, nat) : pstate
def $uc_seek(S, n_stage, n) = S
  -- if $uc_stage(S, n_stage) \/ n = 0
def $uc_seek(S, n_stage, n) = $uc_seek($drive_steps(S[.COMPLETION = NORMAL], 1), n_stage, $nabs($(n - 1)))
  -- if ~$uc_stage(S, n_stage) /\ $(n > 0)
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
def $uc_seek(S, n_stage, n) = S -- otherwise
'''


def checks(program, path, name):
    rebound = name == 'peer-reference-right-rebinds-new-string-cell'
    line = 12 if rebound else 13
    op = 'LESS' if rebound else 'EQUAL'
    result = 'true' if rebound else 'false'
    expected = f'H:1:1:{line};R:1:1:1:1;A:1:1;END;'
    original = f'BINARY_RIGHT {op} (VARIABLE ($ptascii("missing")) z_left) {line}'
    task = f'BINARY_RIGHT {op} (KNOWN PNULL) {line}'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $uc_seek(S_initial,0,1200)',
        'S = S_found[.COMPLETION = NORMAL]', '$uc_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        '$error_read_state_shape(S,perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$spaceship_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        'perrorread.ORIGINAL = ' + original, 'perrorread.TASK = ' + task,
        'perrorread.INPUT = VARIABLE ($ptascii("right")) z_right',
        'perrorread.RESULT = perrorread.INPUT', 'perrorread.NAME = $ptascii("missing")',
        'perrorread.LINE = ' + str(line), '$error_missing_operand(S,$error_read_operand(perrorread))',
        '$scalar_compare_read_other(S,perrorread)', 'S.BORROWEDREAD = eps',
        '$task_nodes(ERROR_READ_RESULT perrorread) = eps',
        '$lookup(S.ENV,$ptascii("right")) = (n_original)',
        'S.STORE[n_original] = DEFINED (PINT 0)',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$uc_stage(S_warn,1)',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread', '$error_call_valid(S_warn,perrorcall)',
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.LINE = ' + str(line), 'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        'S_resume_found = $uc_seek(S_warn,3,1200)',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]', '$uc_stage(S_resume,3)',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_resume*',
        '$error_read_valid(S_resume,perrorread)', '$scalar_compare_read_other(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        'S_resume.BORROWEDREAD = eps', 'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_resume*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_resume*][.RESULT = KNOWN (PBOOL ' + result + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$us_guard(S_compared)', 'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("missing")) 999) ' + str(line) + ']',
        '$error_read_state_shape(S_resume,perrorread_bad.ORIGINAL,perrorread_bad.INPUT,perrorread_bad.BASE) = (perrorread_bad)',
        '~$error_read_valid(S_resume,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(S_resume[.ORIGIN = eps],perrorread)',
        'perrorread_other = perrorread[.ORIGINAL = BINARY_RIGHT NOTEQUAL (VARIABLE ($ptascii("missing")) z_left) ' + str(line) + '][.TASK = BINARY_RIGHT NOTEQUAL (KNOWN PNULL) ' + str(line) + ']',
        '$error_read_state_shape(S_resume,perrorread_other.ORIGINAL,perrorread_other.INPUT,perrorread_other.BASE) = (perrorread_other)',
        '~$error_read_valid(S_resume,perrorread_other)',
        'S_both = $unset_name(S,$ptascii("right"))', '$us_guard(S_both)',
        '$error_read_valid(S_both,perrorread)', '~$scalar_compare_read_other(S_both,perrorread)',
        '$error_read_plan(S_both) = (perrorread)',
        'S_without = $unset_name(S_resume,$ptascii("right"))', '$us_guard(S_without)',
        '$error_read_valid(S_without,perrorread)', '~$scalar_compare_read_other(S_without,perrorread)',
        'PhpStep: S_without ~> S_without_restored',
        'S_without_restored = S_without[.TODO = perrorread.TASK :: ptask_resume*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
    ]
    if rebound:
        values += [
            '$lookup(S.ENV,$ptascii("old")) = (n_original)', 'n_original <- S.REFCELLS',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 2',
            '$lookup(S_resume.ENV,$ptascii("right")) = (n_target)',
            '$lookup(S_resume.ENV,$ptascii("target")) = (n_target)', 'n_target =/= n_original',
            '$lookup(S_resume.ENV,$ptascii("old")) = (n_original)',
            'S_resume.STORE[n_original] = DEFINED (PINT 0)', 'n_target <- S_resume.REFCELLS',
            'S_resume.STORE[n_target] = DEFINED pvalue_string',
            '$string_plain(pvalue_string) = PSTRING ($ptascii("0"))',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 1',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_target) = 2',
            '$lookup(S_done.ENV,$ptascii("right")) = (n_target)',
            'S_done.STORE[n_original] = DEFINED (PINT 0)', 'S_done.STORE[n_target] = DEFINED (PINT 5)',
        ]
    else:
        values += [
            '~(n_original <- S.REFCELLS)',
            '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 1',
            '$lookup(S_resume.ENV,$ptascii("right")) = (n_original)',
            '$lookup(S_resume.ENV,$ptascii("alias")) = (n_original)', 'n_original <- S_resume.REFCELLS',
            'S_resume.STORE[n_original] = DEFINED pvalue_string',
            '$string_plain(pvalue_string) = PSTRING ($ptascii("0"))',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 2',
            'S_done.STORE[n_original] = DEFINED (PINT 5)',
        ]
    return values
