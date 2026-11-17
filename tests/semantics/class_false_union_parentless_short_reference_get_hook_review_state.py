#!/usr/bin/env python3
"""Independent false-only union authority, real cells and alias retirement."""
from pathlib import Path

import class_null_union_parentless_short_reference_get_hook_review_state as prior
import class_false_union_parentless_short_reference_get_hook_review_protocol as headers

runner = prior.prior.runner


def fields(fixture, source, case):
    adapted = {**case, 'nullable': True, 'raw_order': case['raw_order'].replace('false', 'null')}
    checks = prior.fields(fixture, source, adapted)
    rows = []
    for check in checks:
        check = check.replace('PTBUILTIN "null"', 'PTBUILTIN "false"')
        check = check.replace('$hook_short_reference_class_null_header(', '$hook_short_reference_class_false_header(')
        check = check.replace('text_null', 'text_false').replace('$ptascii("null")', '$ptascii("false")')
        rows.append(check)
        if check == '$hook_short_reference_class_false_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            branches = headers.mask(case['class_name'].encode(), case['raw_order'] == 'false-class')
            bool_branches = branches.replace('PTBUILTIN "false"', 'PTBUILTIN "bool"')
            rows += [
                '~$hook_short_reference_class_null_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '$pttypename(ppropertydesc.TYPE) = $base64(' + prior.prior.quoted(case['typename']) + ')',
                '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initial])',
                'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PBOOL false))',
                '~$hook_short_reference_class_false_header(phpType18,' + bool_branches + ',ptcontext_property)',
                '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + bool_branches + '])',
            ]
    assert any('text_false' in row for row in rows)
    assert not any('$ptascii("null")' in row for row in rows)
    return rows


if __name__ == '__main__':
    runner.STEM = 'class_false_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.headers.__file__),
                            Path(prior.prior.__file__), Path(prior.prior.headers.__file__), Path(headers.__file__)])
