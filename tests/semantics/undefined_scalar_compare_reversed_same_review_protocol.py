"""Independent right-frozen entry and two-NULL same-CV continuations."""
import re

from undefined_scalar_compare_both_reversed_review_protocol import PREFIX as COMMON, checks as old_entry, text
from undefined_scalar_compare_second_reversed_review_protocol import checks as old_chain

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if '
                        + r'pbin = GREATER \/ pbin = GREATEREQUAL')


def same_names(condition):
    condition = condition.replace('$ptascii("left")', '$ptascii("x")')
    condition = condition.replace('$ptascii("right")', '$ptascii("x")')
    condition = condition.replace('$ptascii("missing")', '$ptascii("x")')
    condition = condition.replace('Undefined variable $left', 'Undefined variable $x')
    condition = condition.replace('Undefined variable $right', 'Undefined variable $x')
    return condition.replace('Undefined variable $missing', 'Undefined variable $x')


def entry_checks(program, path):
    values = old_entry(program, path, 'peer-both-missing-greater-left-fresh-reference')
    result = [values[0]]
    for condition in values[1:]:
        # Removing the first name also removes the current opposing read here.
        if 'S_right_' in condition or 'perrorread_same' in condition:
            continue
        if (condition == '$lookup(S_resume.ENV,$ptascii("missing")) = (n_missing)'
                or condition == 'S_resume.STORE[n_missing] = DEFINED (PINT 9)'):
            continue
        condition = same_names(condition)
        if condition.startswith('$us_output('):
            condition = '$us_output(S_done.EVENTS) = ' + text(
                'H:1:1:15:1;R:1:1:1:1;A:1:1;END;')
        else:
            condition = re.sub(r'\b13\b', '15', condition)
        if condition == '$scalar_compare_right_read_shape(perrorread_other.ORIGINAL,perrorread_other.INPUT,perrorread_other.BASE) = (perrorread_other)':
            condition = '$scalar_compare_right_read_shape(perrorread_other.ORIGINAL,perrorread_other.INPUT,perrorread_other.BASE) = eps'
        if condition.startswith('S = S_found['):
            result.append(r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET')
        if condition.startswith('S_resume = S_resume_found['):
            result.append(r'S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET')
        result.append(condition)
    result += [
        '$error_read_source(S,perrorread)',
        '~$error_read_valid(S,perrorread_left)',
        'S.ORIGIN = (porigin_same)',
        '$code_expression_at_source(S,porigin_same,[PCFIELD 0]) = (13)',
        '$code_expression_at_source(S,porigin_same,[PCFIELD 1]) = (15)',
        '~$error_read_valid(S[.CODE = eps],perrorread)',
        '$error_read_plan(S_without_restored) = (perrorread_second)',
        'perrorread_second.INPUT = KNOWN PNULL',
        'perrorread_second.RESULT = KNOWN PNULL',
        'perrorread_second.NAME = perrorread.NAME',
        '$error_read_source(S_without_restored,perrorread_second)',
        '$error_read_valid(S_without_restored,perrorread_second)',
        'perrorread_foreign = perrorread[.INPUT = VARIABLE ($ptascii("foreign")) z_right][.NAME = $ptascii("foreign")]',
        '$scalar_compare_right_read_shape(perrorread_foreign.ORIGINAL,perrorread_foreign.INPUT,perrorread_foreign.BASE) = (perrorread_foreign)',
        '$scalar_compare_missing_pair(S,perrorread_foreign)',
        '~$error_read_source(S,perrorread_foreign)',
        '~$error_read_valid(S,perrorread_foreign)',
        '$error_read_plan(S_resume[.TODO = perrorread.ORIGINAL :: ptask_resume*][.RESULT = perrorread.INPUT][.BASE = perrorread.BASE]) = eps',
    ]
    return list(dict.fromkeys(result))


def chain_checks(program, path):
    values = old_chain(program, path, 'peer-second-warning-greaterequal-unset-left-target-reference')
    result = [values[0]]
    skip_left_record = False
    for condition in values[1:]:
        if condition.startswith('$error_read_shape(ptask_original,'):
            skip_left_record = True
        if skip_left_record:
            if condition.startswith('S_wrong_denied = '):
                skip_left_record = False
            continue
        if (condition.startswith('$lookup(S.ENV,$ptascii("left")) = (n_old)')
                or condition.startswith('S.STORE[n_old] = ')
                or condition == '$scalar_compare_read_other(S,perrorread_first)'
                or condition == '~$scalar_compare_missing_pair(S,perrorread_first)'
                or condition == 'n_old =/= n_current'
                or 'HCELL n_old)' in condition):
            continue
        condition = same_names(condition).replace('BINARY_RIGHT GREATEREQUAL ', 'BINARY_RIGHT GREATER ')
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PBOOL true)', 'KNOWN (PBOOL false)')
        if condition.startswith('$us_output('):
            condition = '$us_output(S_done.EVENTS) = ' + text(
                'H:1:1:15:1;H:1:1:15:2;R:1:1:1;A:1:1;END;')
        else:
            condition = re.sub(r'\b13\b', '15', condition)
        if condition == '$scalar_compare_right_read_shape(perrorread_equal.ORIGINAL,perrorread_equal.INPUT,perrorread_equal.BASE) = (perrorread_equal)':
            condition = '$scalar_compare_right_read_shape(perrorread_equal.ORIGINAL,perrorread_equal.INPUT,perrorread_equal.BASE) = eps'
        result.append(condition)
    result += [
        '$lookup(S.ENV,$ptascii("x")) = eps',
        '~$scalar_compare_read_other(S,perrorread_first)',
        '$scalar_compare_missing_pair(S,perrorread_first)',
        '$lookup(S_first_resume.ENV,$ptascii("x")) = eps',
        'perrorread_first.NAME = perrorread_second.NAME',
        '$code_expression_at_source(S,porigin_second,[PCFIELD 0]) = (15)',
        '~$error_read_valid(S_first_restored[.CODE = eps],perrorread_second)',
        '~$error_read_valid(S_first_resume,perrorread_equal)',
        '$error_read_shape(ptask_original,S.RESULT,S.BASE) = (perrorread_left)',
        '~$error_read_valid(S_first_resume,perrorread_left)',
        '~$scalar_compare_read_again(S_first_resume,perrorread_left)',
        'S_absent = $unset_name(S_second_resume,$ptascii("x"))',
        '$error_read_valid(S_absent,perrorread_second)',
        '~$scalar_compare_read_again(S_absent,perrorread_second)',
        'PhpStep: S_absent ~> S_absent_restored',
        'S_absent_restored = S_absent[.TODO = perrorread_second.TASK :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = perrorread_second.BASE]',
        '$error_read_plan(S_absent_restored) = eps',
        'PhpStep: S_absent_restored ~> S_absent_compared',
        'S_absent_compared = S_absent_restored[.TODO = ptask_tail*][.RESULT = KNOWN (PBOOL false)][.BASE = BASE_VALUE (KNOWN PNULL)]',
        'S_absent_compared.EVENTS = S_absent.EVENTS',
    ]
    return list(dict.fromkeys(result))


def checks(program, path, name):
    if name == 'peer-same-reversed-greater-fresh-reference':
        return entry_checks(program, path)
    return chain_checks(program, path)
