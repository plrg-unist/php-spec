#!/usr/bin/env python3
"""Independent string-union authority, exact string backing and alias retirement."""
from pathlib import Path

import class_false_union_parentless_short_reference_get_hook_review_state as prior
import class_string_union_parentless_short_reference_get_hook_review_protocol as headers

runner = prior.runner


def fields(fixture, source, case):
    adapted = {**case, 'raw_order': case['raw_order'].replace('string', 'false')}
    rows = []
    for check in prior.fields(fixture, source, adapted):
        check = check.replace('PTBUILTIN "false"', 'PTBUILTIN "string"')
        check = check.replace('$hook_short_reference_class_false_header(', '$hook_short_reference_class_string_header(')
        check = check.replace('text_false', 'text_string').replace('$ptascii("false")', '$ptascii("string")')
        check = check.replace('PBOOL false', 'PSTRING eps')
        rows.append(check)
        if check == 'S_fetch.RESULT = REFERENCE n_field':
            rows.append('S_fetch.STORE[n_field] = DEFINED (PSTRING eps)')
        if check == '$hook_short_reference_class_string_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows += [
                '~$hook_short_reference_class_false_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_true_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_bool_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_int_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_float_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
            ]
            for kind in ('true', 'false'):
                branches = headers.mask(case['class_name'].encode(), case['raw_order'] == 'string-class').replace('PTBUILTIN "string"', 'PTBUILTIN "' + kind + '"')
                rows += [
                    '~$hook_short_reference_class_string_header(phpType18,' + branches + ',ptcontext_property)',
                    '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + branches + '])',
                ]
    lines = [line.strip() for line in source.read_text().splitlines()]
    at = rows.index('~$property_state_valid(S_aliases[.PROPREFS = eps])') + 1
    checks = []
    for state, previous, target, value in (
        ('S_string_one', 'S_aliases', lines.index("$s322 = '0';") + 1, '1'),
        ('S_string_zero', 'S_string_one', next(i + 1 for i, line in enumerate(lines) if line.startswith('$box322->v = new ')), '0'),
    ):
        checks += [state + ' = $lbr_seek(' + previous + ',' + str(target) + ',30000)',
                   '$lbr_phase(' + state + ',' + str(target) + ')', state + '.COMPLETION = NORMAL',
                   state + '.STORE[n_field] = DEFINED (PSTRING_CARRIER INTERNED_STRING ($ptascii("' + value + '")))',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$property_state_valid(' + state + ')']
    rows[at:at] = checks
    assert any('text_string' in row for row in rows)
    assert 'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PSTRING eps))' in rows
    return rows


if __name__ == '__main__':
    runner.STEM = 'class_string_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__), Path(prior.headers.__file__),
                            Path(prior.prior.headers.__file__), Path(prior.prior.prior.__file__),
                            Path(prior.prior.prior.headers.__file__), Path(headers.__file__)])
