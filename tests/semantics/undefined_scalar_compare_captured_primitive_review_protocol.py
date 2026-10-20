"""Actual primitive snapshots, current aliases and supplied-throw discard."""
import base64
import json

from undefined_scalar_compare_captured_array_review_protocol import PREFIX
from undefined_spaceship_protocol import text


def front(program, path, right, throwing):
    line = 18 if right else 25 if throwing else 22
    operator = 'GREATEREQUAL' if right else 'LESS' if throwing else 'EQUAL'
    original = ('BINARY_RIGHT ' + operator + ' (VARIABLE ($ptascii("missing")) z_missing) ' + str(line)
                if right else 'BINARY_RIGHT ' + operator + ' (KNOWN pvalue_capture) ' + str(line))
    task = 'BINARY_RIGHT ' + operator + ' (KNOWN PNULL) ' + str(line) if right else original
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1600)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        r'S.CURRENT = eps /\ S.FRAMES = eps',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = ' + original,
        'perrorread.INPUT = ' + ('KNOWN pvalue_capture' if right else 'VARIABLE ($ptascii("missing")) z_missing'),
        'S.RESULT = perrorread.INPUT', 'perrorread.TASK = ' + task,
        'perrorread.RESULT = ' + ('KNOWN pvalue_capture' if right else 'KNOWN PNULL'),
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        '$error_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        '$scalar_compare_right_read_shape(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = eps',
        '$scalar_compare_read_other(S,perrorread)', '~$scalar_compare_read_array(S,perrorread)',
        '~$spaceship_read_array(S,perrorread)', '$spaceship_read_scalar(pvalue_capture)',
        '$base_nodes(perrorread.BASE) = eps', '$task_nodes(ERROR_READ_RESULT perrorread) = eps',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        '$lookup(S.ENV,$ptascii("' + ('value' if right else 'source') + '")) = (n_source)',
        'n_source <- S.REFCELLS', '$heap_owners($heap_prune($heap_graph(S)),HCELL n_source) = 2',
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)', 'n_copy =/= n_source',
        '$us_output(S.EVENTS) = ' + text('' if right else 'P;'),
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(17 if right else 24 if throwing else 21) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
    ]
    if right:
        values += [
            'pvalue_capture = PBOOL true',
            '$lookup(S.ENV,$ptascii("old")) = (n_source)',
            'S.STORE[n_source] = DEFINED (PBOOL true)',
            'S.STORE[n_copy] = DEFINED (PBOOL true)',
            '$lookup(S.ENV,$ptascii("saved")) = (n_saved)',
            r'n_saved =/= n_source /\ n_saved =/= n_copy',
            'S.STORE[n_saved] = DEFINED (PBOOL true)',
        ]
    else:
        values += [
            '$string_bytes(pvalue_capture) = ($ptascii("0"))',
            '$lookup(S.ENV,$ptascii("alias")) = (n_source)',
            'S.STORE[n_source] = DEFINED pvalue_source',
            'S.STORE[n_copy] = DEFINED pvalue_copy',
            '$string_bytes(pvalue_source) = ($ptascii("0"))',
            '$string_bytes(pvalue_copy) = ($ptascii("0"))',
        ]
    values += [
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', '$us_guard(S_warn)',
        'S_warn.EVENTS = S.EVENTS',
    ]
    return values


def checks(program, path, name):
    right = name == 'peer-captured-greater-equal-right-default'
    throwing = name == 'peer-captured-less-supplied-throw'
    values = front(program, path, right, throwing)
    if throwing:
        return values + throw_checks()
    line = 18 if right else 22
    operator = 'GREATEREQUAL' if right else 'EQUAL'
    expected = ('H:1:1:18:1;R:1:1:1:1:1:1:1;END;' if right else
                'P;H:1:1:22:1;R:1:1:1:1:1:1;END;')
    values += [
        'S_return_found = $us_seek(S_warn,2,1600)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL ' + ('false' if right else 'true') + ')',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        'S_resume_found = $us_seek(S_return,3,1600)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]', '$us_stage(S_resume,3)',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)', '$scalar_compare_read_other(S_resume,perrorread)',
        '~$scalar_compare_read_array(S_resume,perrorread)', '~$scalar_compare_read_again(S_resume,perrorread)',
        '~$scalar_compare_checked_missing(S_resume,perrorread)',
        '~$scalar_compare_checked_right_missing(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.EVENTS = S_return.EVENTS' + (' ++ [$error_default_event(S_return,WARNING ($ptascii("missing")) 18)]' if right else ''),
        'S_resume.ERRORHANDLER = S.ERRORHANDLER', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = perrorread.TASK :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', '$us_guard(S_compared)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_return,4000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT ' + operator + ' (' + ('VARIABLE ($ptascii("missing")) z_missing' if right else 'KNOWN pvalue_capture') + ') 999][.TASK = BINARY_RIGHT ' + operator + ' (' + ('KNOWN PNULL' if right else 'KNOWN pvalue_capture') + ') 999][.LINE = 999]',
        '$scalar_compare_read_other(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT BITXOR (' + ('VARIABLE ($ptascii("missing")) z_missing' if right else 'KNOWN pvalue_capture') + ') ' + str(line) + '][.TASK = BINARY_RIGHT BITXOR (' + ('KNOWN PNULL' if right else 'KNOWN pvalue_capture') + ') ' + str(line) + ']',
        '~$error_read_source(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
    ]
    for name_value, value in [('object', 'POBJECT 0'), ('undefined', 'PUNDEFINED'),
                              ('array', 'PARRAY 0'), ('integer', 'PINT 1'), ('null', 'PNULL')]:
        changes = ('[.INPUT = KNOWN (' + value + ')][.RESULT = KNOWN (' + value + ')]' if right else
                   '[.ORIGINAL = BINARY_RIGHT EQUAL (KNOWN (' + value + ')) 22][.TASK = BINARY_RIGHT EQUAL (KNOWN (' + value + ')) 22]')
        record = 'perrorread_' + name_value
        values += [record + ' = perrorread' + changes,
                   '$error_read_shape(' + record + '.ORIGINAL,' + record + '.INPUT,' + record + '.BASE) = (' + record + ')']
        if name_value in ('object', 'undefined'):
            values += ['~$error_read_source(S,' + record + ')', '~$error_read_valid(S,' + record + ')']
        else:
            values += ['$error_read_source(S,' + record + ')', '$error_read_valid(S,' + record + ')']
        if name_value in ('integer', 'null'):
            values += ['$scalar_compare_read_other(S,' + record + ')', '~$scalar_compare_read_array(S,' + record + ')']
    values += [
        '~((HARRAY 0) <- S.ALLOCATIONS)', '~$scalar_compare_read_other(S,perrorread_array)',
        '~$scalar_compare_read_array(S,perrorread_array)',
        '$error_read_plan(S[.TODO = perrorread_array.ORIGINAL :: ptask_tail*][.RESULT = perrorread_array.INPUT][.BASE = perrorread_array.BASE]) = eps',
    ]
    if right:
        values += [
            'S_resume.STORE[n_source] = DEFINED (PBOOL false)',
            'S_resume.STORE[n_saved] = DEFINED (PBOOL false)',
            'S_resume.STORE[n_copy] = DEFINED (PBOOL true)',
            'S_resume.STORE[n_missing] = DEFINED (PBOOL true)',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_source) = 2',
        ]
    else:
        values += [
            '$lookup(S_resume.ENV,$ptascii("source")) = eps',
            '$lookup(S_resume.ENV,$ptascii("alias")) = (n_source)',
            'S_resume.STORE[n_source] = DEFINED pvalue_current', '$string_bytes(pvalue_current) = (eps)',
            'S_resume.STORE[n_copy] = DEFINED pvalue_copy',
            'S_resume.STORE[n_missing] = DEFINED pvalue_missing', '$string_bytes(pvalue_missing) = ($ptascii("0"))',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_source) = 1',
        ]
    return values


def throw_checks():
    return [
        'S_throw_found = $us_seek(S_warn,4,2000)',
        r'S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET',
        'S_throw = S_throw_found[.COMPLETION = NORMAL]', '$us_stage(S_throw,4)',
        'S_throw.TODO = (THROW_SEARCH n_exception) :: (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        r'S_throw.CURRENT = eps /\ S_throw.FRAMES = eps', '$us_guard(S_throw)',
        '$lookup(S_throw.ENV,$ptascii("chosen")) = (n_exception_cell)',
        'S_throw.STORE[n_exception_cell] = DEFINED (POBJECT n_exception)',
        '$lookup(S_throw.ENV,$ptascii("source")) = eps',
        '$lookup(S_throw.ENV,$ptascii("alias")) = (n_source)',
        'S_throw.STORE[n_source] = DEFINED pvalue_current', '$string_bytes(pvalue_current) = (eps)',
        'S_throw.STORE[n_copy] = DEFINED pvalue_copy',
        '$lookup(S_throw.ENV,$ptascii("missing")) = (n_missing)',
        'S_throw.STORE[n_missing] = DEFINED pvalue_missing', '$string_bytes(pvalue_missing) = ($ptascii("0"))',
        '$heap_owners($heap_prune($heap_graph(S_throw)),HCELL n_source) = 1',
        'PhpStep: S_throw ~> S_discarded',
        'S_discarded = S_throw[.TODO = (THROW_SEARCH n_exception) :: ptask_tail*][.ERRORHANDLER = S.ERRORHANDLER]',
        'S_pruned = $prune_allocations(S_discarded)', '$us_guard(S_pruned)',
        '$heap_owners($heap_prune($heap_graph(S_pruned)),HCELL n_source) = 1',
        'S_done = $drive_steps(S_pruned,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = $ptascii("P;H:1:1:25:1;C:1:1:1:1:1:1:1;F;END;")',
        '$lookup(S_done.ENV,$ptascii("result")) = (n_result)',
        'S_done.STORE[n_result] = DEFINED (PINT 41)', '$us_guard(S_done)',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_discarded,4000) = S_done',
        'S_zero = $drive_steps(S_throw,0)', 'S_zero = S_throw[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
    ]
