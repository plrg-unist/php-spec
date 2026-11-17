#!/usr/bin/env python3
"""Independent ordered raw unions, defining authority and real alias retirement."""
from pathlib import Path

import scoped_class_parentless_short_reference_get_hook_review_state as prior
import class_null_union_parentless_short_reference_get_hook_review_protocol as headers


def fields(fixture, source, case):
    checks = prior.fields(fixture, source, case)
    null_first = case['raw_order'] == 'null-class'
    branches = headers.mask(case['class_name'].encode(), null_first)
    wrong = headers.mask(case['class_name'].swapcase().encode(), null_first)
    cls = case['raw_kind'] + ' (BYTES text_raw) metadata_raw'
    null = 'NIdentifier (BYTES text_null) metadata_null'
    raw_union = 'NUnionType (SEQUENCE ([' + ','.join((null, cls) if null_first else (cls, null)) + '])) metadata_union'
    rows = []
    for check in checks:
        check = check.replace(prior.headers.mask(case['class_name'].encode(), True), branches)
        check = check.replace(prior.headers.mask(case['class_name'].swapcase().encode(), True), wrong)
        if check.startswith('phpType18 = '):
            check = 'phpType18 = ' + raw_union
        if '$hook_short_reference_scoped_header(' in check:
            check = check.replace('$hook_short_reference_scoped_header(', '$hook_short_reference_class_null_header(')
            if 'ptcontext_consumer)' in check and case['raw_kind'] == 'NNameFullyQualified':
                assert check.startswith('~')
                check = check[1:]
        rows.append(check)
        if check == '$hook_short_reference_class_null_header(phpType18,ppropertydesc.TYPE,ptcontext_property)':
            rows += [
                '$ptlc($base64(text_null)) = $ptascii("null")',
                '$ptype_normalize(phpType18,ptcontext_property) = PTOK ppropertydesc.TYPE eps',
                '~$hook_short_reference_scoped_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                '~$hook_short_reference_class_null_header(phpType18,' + headers.mask(case['class_name'].encode(), not null_first) + ',ptcontext_property)',
                '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + headers.mask(case['class_name'].encode(), not null_first) + '])',
                '~$hook_short_reference_class_null_header(phpType18,ppropertydesc.TYPE,ptcontext_property[.FILE = eps])',
                '~$hook_short_reference_class_null_header(phpType18,ppropertydesc.TYPE,ptcontext_property[.LINE = 0])',
                '$trait_plan(S_front,pclassdesc).TRAITS = eps',
                r'~ppropertydesc.STATIC /\ ~ppropertydesc.READONLY /\ ~ppropertydesc.FINAL',
            ]
    assert 'phpType18 = ' + raw_union in rows
    return rows


if __name__ == '__main__':
    prior.runner.STEM = 'class_null_union_parentless_short_reference_get_hook'
    prior.runner.fields = fields
    prior.runner.main(extra_paths=[Path(prior.__file__), Path(prior.headers.__file__), Path(headers.__file__)])
