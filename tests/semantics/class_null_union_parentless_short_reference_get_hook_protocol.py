#!/usr/bin/env python3
"""Check ordered nominal/null headers through source authority and real aliases."""
from pathlib import Path
import scoped_class_parentless_short_reference_get_hook_review_state as prior

runner, headers = prior.runner, prior.headers


def mask(name, order):
    if order == 'class-null':
        return headers.mask(name.encode(), True)
    assert order == 'null-class'
    return '[(PTBRANCH ([PTBUILTIN "null"])),(PTBRANCH ([PTCLASS ' + headers.value(name.encode()) + ']))]'


def fields(fixture, source, case):
    # The shared recipe uses these fixtures' 322 symbols; mode is checked below.
    checks = prior.fields(fixture, source, {**case, 'strict': True})
    branches = headers.mask(case['class_name'].encode(), True)
    wrong = headers.mask(case['class_name'].swapcase().encode(), True)
    class_node = case['raw_kind'] + ' (BYTES text_raw) metadata_raw'
    null_node = 'NIdentifier (BYTES text_null) metadata_null'
    members = [class_node, null_node] if case['raw_order'] == 'class-null' else [null_node, class_node]
    opposite = 'null-class' if case['raw_order'] == 'class-null' else 'class-null'
    rows = []
    for check in checks:
        check = check.replace(branches, mask(case['class_name'], case['raw_order']))
        check = check.replace(wrong, mask(case['class_name'].swapcase(), case['raw_order']))
        if check.startswith('phpType18 = '):
            check = 'phpType18 = NUnionType (SEQUENCE ([' + ','.join(members) + '])) metadata_union'
        elif check == 'pfunction.CODE.STRICT' and not case['strict']:
            check = '~pfunction.CODE.STRICT'
        elif check.startswith('~$hook_short_reference_scoped_header(') and case['raw_kind'] == 'NNameFullyQualified':
            continue
        elif check.startswith('$hook_short_reference_scoped_header('):
            rows += ['$ptlc($base64(text_null)) = $ptascii("null")',
                     '$ptype_normalize(phpType18,ptcontext_property) = PTOK ppropertydesc.TYPE eps',
                     '~$hook_short_reference_scoped_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
                     '~$hook_short_reference_class_null_header(phpType18,' + mask(case['class_name'], opposite) + ',ptcontext_property)',
                     '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + mask(case['class_name'], opposite) + '])']
        check = check.replace('$hook_short_reference_scoped_header(', '$hook_short_reference_class_null_header(')
        rows.append(check)
    return rows


if __name__ == '__main__':
    runner.STEM = 'class_null_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(headers.__file__)])
