"""Same-name reads keep two NULLs despite the second callback's late aliases."""
import re

from undefined_scalar_compare_second_review_protocol import PREFIX, checks as previous_checks
from undefined_spaceship_protocol import text


def checks(program, path, name):
    target = name == 'peer-same-second-less-target-reference-default'
    previous = ('peer-second-warning-less-unset-right-target-reference' if target else
                'peer-second-warning-equal-fresh-reference')
    answer = 'false' if target else 'true'
    values = previous_checks(program, path, previous)
    result = [values[0]]
    skip_right_record = False
    for condition in values[1:]:
        if condition.startswith('$scalar_compare_right_read_shape(ptask_original,'):
            skip_right_record = True
        if skip_right_record:
            if condition.startswith('S_wrong_denied = '):
                skip_right_record = False
            continue
        if (condition.startswith('$lookup(S.ENV,$ptascii("right")) = (n_old)')
                or condition.startswith('S.STORE[n_old] = ')
                or condition == '$scalar_compare_read_other(S,perrorread_first)'
                or condition == '~$scalar_compare_missing_pair(S,perrorread_first)'
                or condition == 'n_old =/= n_current'
                or 'HCELL n_old)' in condition
                or condition == '$lookup(S_first_resume.ENV,$ptascii("left")) = (n_left)'
                or condition.startswith('S_first_resume.STORE[n_left] = ')):
            continue
        condition = condition.replace('$ptascii("left")', '$ptascii("x")')
        condition = condition.replace('$ptascii("right")', '$ptascii("x")')
        condition = condition.replace('Undefined variable $left', 'Undefined variable $x')
        condition = condition.replace('Undefined variable $right', 'Undefined variable $x')
        if condition.startswith('$us_output('):
            expected = ('H:1:1:15:1;H:1:1:15:2;R:1:1:1;A:1:1;END;' if target else
                        'H:1:1:15:1;H:1:1:15:2;R:1:1:1:1;A:1:1;END;')
            condition = '$us_output(S_done.EVENTS) = ' + text(expected)
        else:
            condition = re.sub(r'\b(?:13|16)\b', '15', condition)
        if condition not in result:
            result.append(condition)
    result += [
        '$lookup(S.ENV,$ptascii("x")) = eps',
        '~$scalar_compare_read_other(S,perrorread_first)',
        '$scalar_compare_missing_pair(S,perrorread_first)',
        '$lookup(S_first_resume.ENV,$ptascii("x")) = eps',
        '$scalar_compare_right_read_shape(ptask_original,S.RESULT,S.BASE) = eps',
        'perrorread_first.NAME = perrorread_second.NAME',
        'S.ORIGIN = (porigin_same)',
        '$code_expression_at_source(S,porigin_same,[PCFIELD 0]) = (' + str(15 if target else 13) + ')',
        '$code_expression_at_source(S,porigin_same,[PCFIELD 1]) = (15)',
        '~$error_read_valid(S_first_restored[.CODE = eps],perrorread_second)',
        '$error_read_plan(S_second_resume[.TODO = ptask_original :: ptask_tail*][.RESULT = perrorread_first.INPUT][.BASE = perrorread_first.BASE]) = eps',
        'S_absent = $unset_name(S_second_resume,$ptascii("x"))',
        '$error_read_valid(S_absent,perrorread_second)',
        '$scalar_compare_read_other(S_absent,perrorread_second)',
        '~$scalar_compare_read_again(S_absent,perrorread_second)',
        'PhpStep: S_absent ~> S_absent_restored',
        'S_absent_restored = S_absent[.TODO = perrorread_second.TASK :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread_second.BASE]',
        '$error_read_plan(S_absent_restored) = eps',
        'PhpStep: S_absent_restored ~> S_absent_compared',
        'S_absent_compared = S_absent_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL ' + answer + ')][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_absent_compared.EVENTS = S_absent.EVENTS',
    ]
    return list(dict.fromkeys(result))
