"""Two actual right-first Warnings preserve both captured NULL values."""
import base64
import json

from undefined_spaceship_protocol import PREFIX as COMMON, text

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if pbin = GREATER \\/ pbin = GREATEREQUAL')


def checks(program, path, name):
    default = name == 'second-reversed-greaterequal-false'
    op, answer = ('GREATEREQUAL', 'true') if default else ('GREATER', 'false')
    original = 'BINARY_RIGHT ' + op + ' (VARIABLE ($ptascii("left")) z_left) 10'
    frozen = 'BINARY_RIGHT ' + op + ' (KNOWN PNULL) 10'
    values = [
        'S_initial = $php_run(' + program + ',0,' + json.dumps(base64.b64encode(str(path).encode()).decode()) + ')',
        'S_initial.COMPLETION = BUDGET', 'S_found = $us_seek(S_initial,0,1200)',
        r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
        'S_0 = S_found[.COMPLETION = NORMAL]', '$us_stage(S_0,0)', '$us_guard(S_0)',
        'S_0.TODO = ptask_original :: ptask_tail*', 'ptask_original = ' + original,
        'S_0.RESULT = VARIABLE ($ptascii("right")) z_right',
        '$lookup(S_0.ENV,$ptascii("left")) = eps', '$lookup(S_0.ENV,$ptascii("right")) = eps',
        '$error_read_plan(S_0) = (perrorread_first)',
        '$scalar_compare_right_read_shape(ptask_original,S_0.RESULT,S_0.BASE) = (perrorread_first)',
        '$scalar_compare_missing_pair(S_0,perrorread_first)',
        'perrorread_first.TASK = ptask_original', 'perrorread_first.RESULT = KNOWN PNULL',
        '$scalar_compare_read_again(S_0,perrorread_first)',
        '$error_read_shape(ptask_original,S_0.RESULT,S_0.BASE) = (perrorread_left)',
        'perrorread_left =/= perrorread_first', '$error_read_valid(S_0,perrorread_left)',
        '~$scalar_compare_missing_pair(S_0,perrorread_left)', '~$scalar_compare_read_again(S_0,perrorread_left)',
    ]
    for index, before, record, variable in ((1, 'S_0', 'perrorread_first', 'right'),
                                            (2, 'S_restored_1', 'perrorread_second', 'left')):
        suffix = '_' + str(index)
        warn, returned, resume, restored = ('S_warn' + suffix, 'S_return' + suffix,
                                            'S_resume' + suffix, 'S_restored' + suffix)
        call, entered = 'perrorcall' + suffix, 'perrorcall_entered' + suffix
        values += [
            '$error_read_valid(' + before + ',' + record + ')', record + '.NAME = ' + text(variable),
            record + '.LINE = 10', '$task_nodes(ERROR_READ_RESULT ' + record + ') = eps',
            warn + '_pause = $drive_steps(' + before + ',1)', warn + '_pause.COMPLETION = BUDGET',
            warn + ' = ' + warn + '_pause[.COMPLETION = NORMAL]', '$us_stage(' + warn + ',1)',
            warn + ' = $prune_allocations($error_read_begin(' + before + '))',
            warn + '.TODO = (ERROR_HANDLER_INVOKE ' + call + ') :: ptask_tail*',
            call + '.RESUME = ERROR_READ_RESULT ' + record, call + '.LEVEL = 2', call + '.LINE = 10',
            call + '.MESSAGE = ' + text('Undefined variable $' + variable),
            call + '.EVENT = WARNING (' + text(variable) + ') 10', '$error_call_valid(' + warn + ',' + call + ')',
            warn + '.EVENTS = ' + before + '.EVENTS', '$us_guard(' + warn + ')',
            returned + '_found = $us_seek(' + warn + ',2,1200)',
            returned + '_found.COMPLETION = NORMAL \\/ ' + returned + '_found.COMPLETION = BUDGET',
            returned + ' = ' + returned + '_found[.COMPLETION = NORMAL]',
            returned + '.TODO = (ERROR_HANDLER_RESULT ' + entered + ') :: ptask_tail*',
            entered + '.RESUME = ERROR_READ_RESULT ' + record,
            '$call_task_valid(' + returned + ',ERROR_HANDLER_RESULT ' + entered + ')',
            returned + '.RESULT = KNOWN (PBOOL ' + ('false' if default else 'true') + ')', '$us_guard(' + returned + ')',
            resume + '_found = $us_seek(' + returned + ',3,1200)',
            resume + '_found.COMPLETION = NORMAL \\/ ' + resume + '_found.COMPLETION = BUDGET',
            resume + ' = ' + resume + '_found[.COMPLETION = NORMAL]',
            resume + '.TODO = (ERROR_READ_RESULT ' + record + ') :: ptask_tail*',
            '$error_read_valid(' + resume + ',' + record + ')', resume + '.ERRORHANDLER = S_0.ERRORHANDLER',
            resume + '.BORROWEDREAD = eps', resume + '.CURRENT = eps /\\ ' + resume + '.FRAMES = eps',
            '$us_guard(' + resume + ')', 'PhpStep: ' + resume + ' ~> ' + restored,
            restored + ' = ' + resume + '[.TODO = ' + record + '.TASK :: ptask_tail*][.RESULT = ' + record + '.RESULT][.BASE = ' + record + '.BASE]',
            resume + '.EVENTS = ' + returned + '.EVENTS' + (
                ' ++ [$error_default_event(' + returned + ',WARNING (' + text(variable) + ') 10)]' if default else ''),
        ]
        if index == 1:
            values += [
                '~$scalar_compare_read_other(S_resume_1,perrorread_first)',
                '$scalar_compare_read_again(S_resume_1,perrorread_first)',
                '$error_missing_operand(S_resume_1,VARIABLE ($ptascii("left")) z_left)',
                'S_restored_1.RESULT = KNOWN PNULL', 'S_restored_1.TODO = ptask_original :: ptask_tail*',
                '$error_read_plan(S_restored_1) = (perrorread_second)',
                'perrorread_second.ORIGINAL = perrorread_first.TASK', 'perrorread_second.INPUT = KNOWN PNULL',
                'perrorread_second.RESULT = KNOWN PNULL', 'perrorread_second.TASK = ' + frozen,
                '$scalar_compare_read_other(S_restored_1,perrorread_second)',
                '~$scalar_compare_read_again(S_restored_1,perrorread_second)',
                'perrorread_second =/= perrorread_first', '$error_read_source(S_restored_1,perrorread_second)',
            ]
    values += [
        '$lookup(S_resume_1.ENV,$ptascii("right")) = (n_right)',
        'S_resume_1.STORE[n_right] = DEFINED (PINT 9)',
        '$lookup(S_resume_2.ENV,$ptascii("left")) = (n_left)',
        'S_resume_2.STORE[n_left] = DEFINED pvalue_left', '$string_plain(pvalue_left) = PSTRING ($ptascii("0"))',
        'S_restored_2.RESULT = KNOWN PNULL', 'S_restored_2.TODO = (' + frozen + ') :: ptask_tail*',
        '$error_read_plan(S_restored_2) = eps', 'PhpStep: S_restored_2 ~> S_compared',
        'S_compared = S_restored_2[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL ' + answer + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        '$us_guard(S_compared)', 'S_done = $drive_steps(S_compared,4000)', 'S_done.COMPLETION = NORMAL',
        r'S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
        '$us_output(S_done.EVENTS) = ' + text('H:1::1:10;H:1:1::10;R:1:1:1;END;'), '$us_guard(S_done)',
        'S_done.CODE = S_initial.CODE', 'S_done.POOLS = S_initial.POOLS',
        'S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],4000)',
        'S_zero = $drive_steps(S_resume_1,0)', 'S_zero = S_resume_1[.COMPLETION = BUDGET]',
        '$drive_steps(S_zero[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_warn_2_pause[.COMPLETION = NORMAL],4000) = S_done',
        '$drive_steps(S_resume_2,4000) = S_done',
        '~$error_read_valid(S_resume_1,perrorread_first[.LINE = 999])',
        '~$error_read_valid(S_resume_2,perrorread_second[.LINE = 999])',
        '~$error_read_valid(S_resume_2[.ORIGIN = eps],perrorread_second)',
        '~$error_call_valid(S_warn_2,perrorcall_2[.MESSAGE = eps])',
        '~$error_call_valid(S_warn_2,perrorcall_2[.LEVEL = 8])',
        'perrorread_nonnull = perrorread_second[.INPUT = KNOWN (POBJECT 0)][.RESULT = KNOWN (POBJECT 0)]',
        '$error_read_shape(perrorread_nonnull.ORIGINAL,perrorread_nonnull.INPUT,perrorread_nonnull.BASE) = (perrorread_nonnull)',
        '~$error_read_valid(S_restored_1,perrorread_nonnull)', '~$error_read_source(S_restored_1,perrorread_nonnull)',
        'S_no_code = S_restored_1[.CODE = eps]', '~$error_read_valid(S_no_code,perrorread_second)',
        '~$error_read_source(S_no_code,perrorread_second)',
        'perrorread_forward = perrorread_first[.ORIGINAL = BINARY_RIGHT EQUAL (VARIABLE ($ptascii("left")) z_left) 10][.TASK = BINARY_RIGHT EQUAL (VARIABLE ($ptascii("left")) z_left) 10]',
        '$scalar_compare_right_read_shape(perrorread_forward.ORIGINAL,perrorread_forward.INPUT,perrorread_forward.BASE) = (perrorread_forward)',
        '~$scalar_compare_read_again(S_resume_1,perrorread_forward)', '~$error_read_valid(S_resume_1,perrorread_forward)',
        'S_again = $unset_name(S_resume_2,$ptascii("left"))', '$error_read_valid(S_again,perrorread_second)',
        '~$scalar_compare_read_again(S_again,perrorread_second)', 'PhpStep: S_again ~> S_again_restored',
        'S_again_restored = S_again[.TODO = perrorread_second.TASK :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread_second.BASE]',
        '$error_read_plan(S_again_restored) = eps', 'PhpStep: S_again_restored ~> S_again_compared',
        'S_again_compared = S_again_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL ' + answer + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
    ]
    return values
