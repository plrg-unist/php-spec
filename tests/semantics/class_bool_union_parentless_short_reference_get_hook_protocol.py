#!/usr/bin/env python3
"""Check class/bool headers, weak Boolean conversion and real aliases."""
from pathlib import Path
import class_false_union_parentless_short_reference_get_hook_protocol as prior


def fields(fixture, source, case):
    adapted = {**case, 'raw_order': case['raw_order'].replace('bool', 'false')}
    rows = []
    for check in prior.fields(fixture, source, adapted):
        check = check.replace('$hook_short_reference_class_false_header(', '$hook_short_reference_class_bool_header(')
        check = check.replace('text_false', 'text_bool')
        check = check.replace('PTBUILTIN "false"', 'PTBUILTIN "bool"').replace('$ptascii("false")', '$ptascii("bool")')
        rows.append(check)
        if check == '$hook_short_reference_class_bool_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows += ['~$hook_short_reference_class_false_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                     '~$hook_short_reference_class_true_header(phpType18,ppropertydesc.TYPE,ptcontext_property)']
    return rows


if __name__ == '__main__':
    prior.prior.runner.STEM = 'class_bool_union_parentless_short_reference_get_hook'
    prior.prior.runner.fields = fields
    prior.prior.runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__),
                                        Path(prior.prior.prior.__file__), Path(prior.prior.headers.__file__)])
