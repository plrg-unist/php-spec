#!/usr/bin/env python3
"""Check class/false type identity, canonical source authority and real aliases."""
from pathlib import Path
import class_null_union_parentless_short_reference_get_hook_protocol as prior


def fields(fixture, source, case):
    # Reuse the retained source/alias recipe; substitute only the exact type arm.
    reference_case = {**case, 'nullable': True, 'raw_order': case['raw_order'].replace('false', 'null')}
    rows = []
    for check in prior.fields(fixture, source, reference_case):
        check = check.replace('$hook_short_reference_class_null_header(', '$hook_short_reference_class_false_header(')
        check = check.replace('text_null', 'text_false')
        check = check.replace('PTBUILTIN "null"', 'PTBUILTIN "false"').replace('$ptascii("null")', '$ptascii("false")')
        rows.append(check)
        if check == '$hook_short_reference_class_false_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows += ['~$hook_short_reference_class_null_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                     '$pttypename(ppropertydesc.TYPE) = $base64(' + prior.prior.quoted(case['typename']) + ')']
        if check == 'S_fetch.RESULT = REFERENCE n_field':
            rows.append('S_fetch.STORE[n_field] = DEFINED (PBOOL false)')
    return rows


if __name__ == '__main__':
    prior.runner.STEM = 'class_false_union_parentless_short_reference_get_hook'
    prior.runner.fields = fields
    prior.runner.main(extra_paths=[Path(prior.__file__), Path(prior.prior.__file__), Path(prior.headers.__file__)])
