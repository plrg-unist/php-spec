#!/usr/bin/env python3
"""Independent bool-union authority, literal tags and real alias retirement."""
from pathlib import Path

import class_false_union_parentless_short_reference_get_hook_review_state as prior
import class_bool_union_parentless_short_reference_get_hook_review_protocol as headers

runner = prior.runner


def fields(fixture, source, case):
    adapted = {**case, 'raw_order': case['raw_order'].replace('bool', 'false')}
    rows = []
    for check in prior.fields(fixture, source, adapted):
        check = check.replace('PTBUILTIN "bool"', 'PTBUILTIN "true"')
        check = check.replace('PTBUILTIN "false"', 'PTBUILTIN "bool"')
        check = check.replace('$hook_short_reference_class_false_header(', '$hook_short_reference_class_bool_header(')
        check = check.replace('text_false', 'text_bool').replace('$ptascii("false")', '$ptascii("bool")')
        rows.append(check)
        if check == '$hook_short_reference_class_bool_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            false_branches = headers.mask(case['class_name'].encode(), case['raw_order'] == 'bool-class').replace('PTBUILTIN "bool"', 'PTBUILTIN "false"')
            rows += [
                '~$hook_short_reference_class_false_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_true_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_bool_header(phpType18,' + false_branches + ',ptcontext_property)',
                '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + false_branches + '])',
            ]
    assert any('text_bool' in row for row in rows)
    assert 'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PBOOL false))' in rows
    return rows


if __name__ == '__main__':
    runner.STEM = 'class_bool_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__), Path(prior.headers.__file__),
                            Path(prior.prior.headers.__file__), Path(prior.prior.prior.__file__),
                            Path(prior.prior.prior.headers.__file__), Path(headers.__file__)])
