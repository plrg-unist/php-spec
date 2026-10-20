"""Independent forward quiet folds with fresh and surviving reference aliases."""
import re

from undefined_spaceship_checked_unset_review_protocol import (
    PREFIX as COMMON, checks as spaceship_checks, text)

PREFIX = COMMON.replace('BINARY_RIGHT SPACESHIP poperand z',
                        'BINARY_RIGHT pbin poperand z\n  -- if '
                        + r'pbin = EQUAL \/ pbin = NOTEQUAL \/ pbin = LESS \/ pbin = LESSEQUAL')


def checks(program, path, name):
    target = name == 'peer-checked-less-unset-target-default'
    previous = ('peer-checked-reference-unset-default' if target
                else 'peer-checked-left-unset-multiline')
    operator, boolean = ('LESS', 'false') if target else ('EQUAL', 'true')
    values = spaceship_checks(program, path, previous)
    # Preserve the actual parsed program; only the reached consumer changes.
    result = [values[0]]
    for condition in values[1:]:
        if condition.startswith('perrorread_equal = '):
            condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT GREATER ')
        condition = condition.replace('perrorread_equal', 'perrorread_foreign')
        condition = condition.replace('BINARY_RIGHT SPACESHIP ', 'BINARY_RIGHT ' + operator + ' ')
        condition = condition.replace('$spaceship_right_read_shape(', '$scalar_compare_right_read_shape(')
        condition = condition.replace('$spaceship_read_other(', '$scalar_compare_read_other(')
        condition = condition.replace('$spaceship_read_again(', '$scalar_compare_read_again(')
        condition = condition.replace('$spaceship_checked_missing(', '$scalar_compare_checked_missing(')
        if condition.startswith('S_compared = '):
            condition = condition.replace('KNOWN (PINT 0)', 'KNOWN (PBOOL ' + boolean + ')')
        if condition.startswith('$us_output('):
            expected = ('H:1:1:15:1;R:1:1:1:1:1;A:1:1;END;' if target else
                        'H:1:1:16:1;R:1:1:1:1:1;A:1:1:1;END;')
            condition = '$us_output(S_done.EVENTS) = ' + text(expected)
        elif not target:
            condition = re.sub(r'\b15\b', '16', condition)
            if condition.startswith('$code_expression_at_source(S,porigin,[PCFIELD 0])'):
                condition = '$code_expression_at_source(S,porigin,[PCFIELD 0]) = (15)'
        if not target and condition == '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 0':
            condition = '$heap_owners($heap_prune($heap_graph(S_resume)),HCELL n_original) = 1'
        result.append(condition)
    if not target:
        result += [
            '$lookup(S_resume.ENV,$ptascii("alias")) = (n_original)',
            'n_original <- S_resume.REFCELLS',
            'S_resume.STORE[n_original] = DEFINED pvalue_original',
            '$lookup(S_done.ENV,$ptascii("alias")) = (n_original)',
            'S_done.STORE[n_original] = DEFINED (PINT 5)',
            '$heap_owners($heap_prune($heap_graph(S_done)),HCELL n_original) = 1',
        ]
    return result
