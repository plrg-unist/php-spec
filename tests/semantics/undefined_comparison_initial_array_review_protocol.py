"""Initial array roots remain in CVs; missing-read records save no table."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
    'BINARY_RIGHT pbin poperand z\n  -- if pbin = SPACESHIP \\/ pbin = EQUAL')


def checks(program, path, name):
    checked = name == 'peer-initial-array-checked-left-unset-default'
    operator, line = ('EQUAL', 15) if checked else ('SPACESHIP', 18)
    current = 'left' if checked else 'right'
    left, right = ('left', 'missing') if checked else ('missing', 'right')
    family = 'scalar_compare' if checked else 'spaceship'
    shape = 'scalar_compare_right_read_shape' if checked else 'error_read_shape'
    original = 'BINARY_RIGHT ' + operator + ' (VARIABLE (' + text(left) + ') z_left) ' + str(line)
    task = original if checked else 'BINARY_RIGHT SPACESHIP (KNOWN PNULL) 18'
    expected = ('H:1:1:15:1;R:1:1:1:1:1:1;A:1:1:1;END;' if checked else
                'H:1:1:18:1;R:1:1:1:1:1:1:1;A:1:1:1:1;END;')
    items = '[ENTRY (KINT 0) (DIRECT (PBOOL false))]' if checked else 'eps'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S = S_found[.COMPLETION = NORMAL]', '$us_stage(S,0)', '$us_guard(S)',
        '$error_read_plan(S) = (perrorread)', '$error_read_valid(S,perrorread)',
        'S.TODO = perrorread.ORIGINAL :: ptask_tail*',
        'perrorread.ORIGINAL = ' + original,
        'perrorread.INPUT = VARIABLE (' + text(right) + ') z_right',
        'S.RESULT = perrorread.INPUT',
        '$' + shape + '(perrorread.ORIGINAL,perrorread.INPUT,perrorread.BASE) = (perrorread)',
        'perrorread.NAME = $ptascii("missing")', 'perrorread.LINE = ' + str(line),
        'perrorread.TASK = ' + task,
        'perrorread.RESULT = ' + ('KNOWN PNULL' if checked else 'perrorread.INPUT'),
        '~$' + family + '_read_other(S,perrorread)', '$' + family + '_read_array(S,perrorread)',
        '$task_nodes(ERROR_READ_RESULT perrorread) = eps', 'S.BORROWEDREAD = eps',
        '$lookup(S.ENV,' + text(current) + ') = (n_original)',
        '$lookup(S.ENV,$ptascii("target")) = (n_original)', 'n_original <- S.REFCELLS',
        'S.STORE[n_original] = DEFINED (PARRAY n_initial)',
        '$lookup(S.ENV,$ptascii("copy")) = (n_copy)',
        'S.STORE[n_copy] = DEFINED (PARRAY n_initial)', 'n_copy =/= n_original',
        '(HARRAY n_initial) <- S.ALLOCATIONS', 'S.ARRAYS[n_initial].ITEMS = ' + items,
        ('$array_immutable' if not checked else '~$array_immutable') + '(S,n_initial)',
        'n_pool = $heap_count(HARRAY n_initial,$pools_nodes(S.POOLS))',
        '$heap_owners($heap_prune($heap_graph(S)),HARRAY n_initial) = $(2 + n_pool)',
        '$heap_owners($heap_prune($heap_graph(S)),HCELL n_original) = 2',
        '$lookup(S.ENV,$ptascii("missing")) = eps',
        'S.ORIGIN = (porigin)',
        '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (' + str(line if checked else 17) + ')',
        '$code_expression_at_source(S,porigin,[PCFIELD 1]) = (' + str(line) + ')',
        'S_dead = S[.ALLOCATIONS = $destruction_node_delete(S.ALLOCATIONS,HARRAY n_initial)]',
        '~$' + family + '_read_array(S_dead,perrorread)', '$error_read_plan(S_dead) = eps',
        '$error_read_valid(S_dead,perrorread)',
        'S_warn_pause = $drive_steps(S,1)', 'S_warn_pause.COMPLETION = BUDGET',
        'S_warn = S_warn_pause[.COMPLETION = NORMAL]', '$us_stage(S_warn,1)',
        'S_warn = $prune_allocations($error_read_begin(S))',
        'S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*',
        'perrorcall.RESUME = ERROR_READ_RESULT perrorread',
        'perrorcall.LEVEL = 2', 'perrorcall.LINE = ' + str(line),
        'perrorcall.MESSAGE = $ptascii("Undefined variable $missing")',
        'perrorcall.EVENT = WARNING ($ptascii("missing")) ' + str(line),
        '$error_call_valid(S_warn,perrorcall)', 'S_warn.EVENTS = S.EVENTS', '$us_guard(S_warn)',
        'S_return_found = $us_seek(S_warn,2,1200)',
        r'S_return_found.COMPLETION = NORMAL \/ S_return_found.COMPLETION = BUDGET',
        'S_return = S_return_found[.COMPLETION = NORMAL]',
        'S_return.TODO = (ERROR_HANDLER_RESULT perrorcall_entered) :: ptask_tail*',
        'perrorcall_entered.RESUME = ERROR_READ_RESULT perrorread',
        '$call_task_valid(S_return,ERROR_HANDLER_RESULT perrorcall_entered)',
        'S_return.RESULT = KNOWN (PBOOL ' + ('false' if checked else 'true') + ')',
        r'S_return.CURRENT = eps /\ S_return.FRAMES = eps', '$us_guard(S_return)',
        'S_resume_found = $us_seek(S_return,3,1200)',
        r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET',
        'S_resume = S_resume_found[.COMPLETION = NORMAL]', '$us_stage(S_resume,3)',
        'S_resume.TODO = (ERROR_READ_RESULT perrorread) :: ptask_tail*',
        '$error_read_valid(S_resume,perrorread)',
        '$lookup(S_resume.ENV,$ptascii("target")) = (n_original)',
        'S_resume.STORE[n_original] = DEFINED (PARRAY n_initial)',
        '$lookup(S_resume.ENV,$ptascii("copy")) = (n_copy)',
        'S_resume.STORE[n_copy] = DEFINED (PARRAY n_initial)',
        'S_resume.ARRAYS[n_initial] = S.ARRAYS[n_initial]',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 1',
        '$heap_owners($heap_prune($heap_graph(S_resume)),HARRAY n_initial) = $(2 + n_pool)',
        '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)',
        'S_resume.STORE[n_missing] = DEFINED (PINT 9)',
        '~$' + family + '_read_array(S_resume,perrorread)',
        '~$' + family + '_read_again(S_resume,perrorread)',
        'S_resume.EVENTS = S_return.EVENTS' + (' ++ [$error_default_event(S_return,WARNING ($ptascii("missing")) 15)]' if checked else ''),
        'S_resume.ERRORHANDLER = S.ERRORHANDLER',
        r'S_resume.CURRENT = eps /\ S_resume.FRAMES = eps', '$us_guard(S_resume)',
        'PhpStep: S_resume ~> S_restored',
        'S_restored = S_resume[.TODO = ' + ('(BINARY_RIGHT EQUAL (KNOWN PNULL) 15)' if checked else 'perrorread.TASK') + ' :: ptask_tail*][.RESULT = perrorread.RESULT][.BASE = perrorread.BASE]',
        '$error_read_plan(S_restored) = eps',
        'PhpStep: S_restored ~> S_compared',
        'S_compared = S_restored[.TODO = ptask_tail*][.RESULT = KNOWN (' + ('PBOOL true' if checked else 'PINT $(-1)') + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_compared.EVENTS = S_resume.EVENTS', 'S_compared.ARRAYS = S_resume.ARRAYS', '$us_guard(S_compared)',
        'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text(expected), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        '$lookup(S_done.ENV,$ptascii("target")) = (n_original)',
        'S_done.STORE[n_original] = DEFINED (PARRAY n_final)', 'n_final =/= n_initial',
        'S_done.ARRAYS[n_final].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
        'S_done.ARRAYS[n_initial] = S.ARRAYS[n_initial]',
        'S_done.STORE[n_copy] = DEFINED (PARRAY n_initial)',
        '$heap_owners($heap_prune($heap_graph(S_done)),HCELL n_original) = 1',
        '$heap_owners($heap_prune($heap_graph(S_done)),HARRAY n_initial) = $(1 + n_pool)',
        '$heap_owners($heap_prune($heap_graph(S_done)),HARRAY n_final) = 1',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        '$drive_steps(S_warn_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_return,4000) = S_done',
        'S_zero = $drive_steps(S_resume,0)', 'S_zero = S_resume[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        'perrorread_bad = perrorread[.ORIGINAL = BINARY_RIGHT ' + operator + ' (VARIABLE (' + text(left) + ') z_left) 999][.TASK = BINARY_RIGHT ' + operator + ' (' + ('VARIABLE (' + text(left) + ') z_left' if checked else 'KNOWN PNULL') + ') 999][.LINE = 999]',
        '$' + family + '_read_array(S,perrorread_bad)', '~$error_read_valid(S,perrorread_bad)',
        '~$error_call_valid(S_warn,perrorcall[.RESUME = ERROR_READ_RESULT perrorread_bad])',
        '~$error_read_valid(S[.CODE = eps],perrorread)', '~$error_read_valid(S[.ORIGIN = eps],perrorread)',
        'perrorread_foreign = perrorread[.ORIGINAL = BINARY_RIGHT ' + ('SPACESHIP' if checked else 'EQUAL') + ' (VARIABLE (' + text(left) + ') z_left) ' + str(line) + '][.TASK = BINARY_RIGHT ' + ('SPACESHIP' if checked else 'EQUAL') + ' (' + ('VARIABLE (' + text(left) + ') z_left' if checked else 'KNOWN PNULL') + ') ' + str(line) + ']',
        '~$' + family + '_read_array(S,perrorread_foreign)', '~$error_read_valid(S,perrorread_foreign)',
    ]
    if checked:
        values += [
            '$lookup(S_resume.ENV,$ptascii("left")) = eps',
            '~$scalar_compare_read_other(S_resume,perrorread)',
            '$scalar_compare_checked_missing(S_resume,perrorread)',
            '$lookup(S_done.ENV,$ptascii("left")) = eps',
            'ptask_known = BINARY_RIGHT EQUAL (KNOWN (PARRAY n_initial)) 15',
            '$error_read_plan(S[.TODO = ptask_known :: ptask_tail*]) = eps',
        ]
    else:
        values += [
            '$lookup(S_resume.ENV,$ptascii("right")) = (n_current)',
            '$lookup(S_resume.ENV,$ptascii("replacement")) = (n_current)',
            'n_current =/= n_original', 'n_current <- S_resume.REFCELLS',
            'S_resume.STORE[n_current] = DEFINED pvalue_current',
            '$string_plain(pvalue_current) = PSTRING ($ptascii("0"))',
            '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_current) = 2',
            '$spaceship_read_other(S_resume,perrorread)', '~$spaceship_checked_missing(S_resume,perrorread)',
            '$lookup(S_done.ENV,$ptascii("right")) = (n_current)',
            '$lookup(S_done.ENV,$ptascii("replacement")) = (n_current)',
            'S_done.STORE[n_current] = DEFINED (PINT 6)',
            '$heap_owners($heap_prune($heap_graph(S_done)),HCELL n_current) = 2',
            '$error_read_plan(S[.RESULT = KNOWN (PARRAY n_initial)]) = eps',
        ]
    return values
