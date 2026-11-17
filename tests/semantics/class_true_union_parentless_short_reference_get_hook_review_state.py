#!/usr/bin/env python3
"""Independent true-only source authority, real cells and alias retirement."""
from pathlib import Path

import class_false_union_parentless_short_reference_get_hook_review_state as prior
import class_true_union_parentless_short_reference_get_hook_review_protocol as headers

runner = prior.runner


def fields(fixture, source, case):
    adapted = {**case, 'raw_order': case['raw_order'].replace('true', 'false')}
    rows = []
    for check in prior.fields(fixture, source, adapted):
        check = check.replace('PTBUILTIN "false"', 'PTBUILTIN "true"')
        check = check.replace('$hook_short_reference_class_false_header(', '$hook_short_reference_class_true_header(')
        check = check.replace('text_false', 'text_true').replace('$ptascii("false")', '$ptascii("true")')
        check = check.replace('PBOOL false', 'PBOOL true')
        rows.append(check)
        if check == '$hook_short_reference_class_true_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows.append('~$hook_short_reference_class_false_header(phpType18,ppropertydesc.TYPE,ptcontext_property)')
    assert any('text_true' in row for row in rows)
    assert not any('$ptascii("false")' in row for row in rows)
    return rows


if __name__ == '__main__':
    runner.STEM = 'class_true_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__), Path(prior.headers.__file__),
                            Path(prior.prior.headers.__file__), Path(prior.prior.prior.__file__),
                            Path(prior.prior.prior.headers.__file__), Path(headers.__file__)])
