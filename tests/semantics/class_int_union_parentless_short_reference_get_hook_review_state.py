#!/usr/bin/env python3
"""Independent int-union authority, exact integer backing and alias retirement."""
from pathlib import Path

import class_false_union_parentless_short_reference_get_hook_review_state as prior
import class_int_union_parentless_short_reference_get_hook_review_protocol as headers

runner = prior.runner


def fields(fixture, source, case):
    adapted = {**case, 'raw_order': case['raw_order'].replace('int', 'false')}
    rows = []
    for check in prior.fields(fixture, source, adapted):
        check = check.replace('PTBUILTIN "false"', 'PTBUILTIN "int"')
        check = check.replace('$hook_short_reference_class_false_header(', '$hook_short_reference_class_int_header(')
        check = check.replace('text_false', 'text_int').replace('$ptascii("false")', '$ptascii("int")')
        check = check.replace('PBOOL false', 'PINT 0')
        rows.append(check)
        if check == '$hook_short_reference_class_int_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows += [
                '~$hook_short_reference_class_false_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_true_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_bool_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
            ]
            for kind in ('true', 'false'):
                branches = headers.mask(case['class_name'].encode(), case['raw_order'] == 'int-class').replace('PTBUILTIN "int"', 'PTBUILTIN "' + kind + '"')
                rows += [
                    '~$hook_short_reference_class_int_header(phpType18,' + branches + ',ptcontext_property)',
                    '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + branches + '])',
                ]
    assert any('text_int' in row for row in rows)
    assert 'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PINT 0))' in rows
    return rows


if __name__ == '__main__':
    runner.STEM = 'class_int_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__), Path(prior.headers.__file__),
                            Path(prior.prior.headers.__file__), Path(prior.prior.prior.__file__),
                            Path(prior.prior.prior.headers.__file__), Path(headers.__file__)])
