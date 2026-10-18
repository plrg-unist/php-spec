"""Fresh !=/<= sources with independent complete reference-cell state checks."""
from undefined_scalar_compare_review_protocol import PREFIX as COMMON, checks as left_checks, text
from undefined_scalar_compare_right_review_protocol import checks as right_checks

PREFIX = COMMON.replace(r'pbin = EQUAL \/ pbin = LESS',
                        r'pbin = NOTEQUAL \/ pbin = LESSEQUAL')


def checks(program, path, name):
    left = name == 'peer-missing-left-reference-both-operators'
    values = (left_checks(program, path, 'peer-plain-right-becomes-reference-string')
              if left else right_checks(program, path, 'peer-reference-left-rebinds-new-zero-cell'))
    # The checked source program and its path remain untouched. Adapt only the
    # reached consumer, result predicate and independently selected source data.
    result = [values[0]]
    for condition in values[1:]:
        if left:
            if condition.startswith('perrorread_other = '):
                condition = condition.replace('BINARY_RIGHT NOTEQUAL ', 'BINARY_RIGHT EQUAL ')
            else:
                condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT NOTEQUAL ')
            condition = condition.replace(') 13', ') 11').replace(' = 13', ' = 11')
            if condition.startswith('S_compared = '):
                condition = condition.replace('KNOWN (PBOOL false)', 'KNOWN (PBOOL true)')
            if condition.startswith('$us_output('):
                condition = '$us_output(S_done.EVENTS) = ' + text(
                    'H:1:1:11;N:1:1:1;H:1:1:14;P:1:1:1;A:1;END;')
        else:
            condition = condition.replace('BINARY_RIGHT EQUAL ', 'BINARY_RIGHT LESSEQUAL ')
            if condition.startswith(('S_compared = ', 'S_right_compared = ')):
                condition = condition.replace('KNOWN (PBOOL true)', 'KNOWN (PBOOL false)')
            if condition == '$string_plain(pvalue_original) = PSTRING ($ptascii("0"))':
                continue
            condition = condition.replace('DEFINED pvalue_original', 'DEFINED (PINT 0)')
            if condition == 'S_resume.STORE[n_target] = DEFINED (PINT 0)':
                result.extend(['S_resume.STORE[n_target] = DEFINED pvalue_string',
                               '$string_plain(pvalue_string) = PSTRING ($ptascii("0"))'])
                continue
        result.append(condition)
    return result
