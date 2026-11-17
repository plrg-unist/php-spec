#!/usr/bin/env python3
"""Check defining class contexts through actual reference Get alias lifetimes."""
from pathlib import Path
import fully_qualified_class_parentless_short_reference_get_hook_protocol as prior

def fields(fixture, source, case):
    checks = prior.fields(fixture, source, case)
    name, raw_name = case['class_name'], case['raw_class_name']
    raw_kind = case['raw_kind']
    context = [
        'pclassdesc.ORIGIN = PORIGIN n_source pcpath_owner',
        '$source_unit(S_front.SOURCES,n_source) = (pcunit_front)',
        'pcunit_front = $pcsource(pcunit_front.ID,pcunit_front.AST)',
        'ptbytes_file = $call_sourcefile(S_front.FILES,pclassdesc.ORIGIN)',
        '$property_hook_pair_source_header(S_front,pclassdesc)',
        '$plclasscontext(pcunit_front,pcpath_owner,ptbytes_file,pclassdesc.LINE) = (ptcontext_owner)',
        'ptcontext_owner.NAMESPACE = $base64(' + prior.peer.quoted(case['namespace']) + ')',
        'ppropertydesc.LINE = $nabs($source_line(metadata_group))',
        'ptcontext_property = ptcontext_owner[.SCOPE = PTKNOWN pclassdesc.NAME pclassdesc.PARENT][.POSITION = PTPROPERTY][.OWNER = pclassdesc.NAME][.MEMBER = ppropertydesc.NAME][.LINE = ppropertydesc.LINE]',
        '$ptype_normalize(phpType18,ptcontext_property) = PTOK ppropertydesc.TYPE eps',
        '~$hook_short_reference_header(phpType18,ppropertydesc.TYPE)',
        '$property_hook_short_reference_header(S_front,pclassdesc,ppropertydesc,phpType18)',
        '$property_hook_short_reference_header(S_front[.ENV = eps][.FUNCTIONS = eps],pclassdesc,ppropertydesc,phpType18)',
        '~$property_hook_short_reference_header(S_front[.FILES = eps],pclassdesc,ppropertydesc,phpType18)',
        '~$property_hook_short_reference_header(S_front[.SOURCES = eps],pclassdesc,ppropertydesc,phpType18)',
        '~$property_hook_short_reference_header(S_front,pclassdesc[.NAME = $ptascii("Other323")],ppropertydesc,phpType18)',
        '~$property_hook_short_reference_header(S_front,pclassdesc[.LINE = $(pclassdesc.LINE + 1)],ppropertydesc,phpType18)',
        '~$property_hook_short_reference_header(S_front,pclassdesc,ppropertydesc[.LINE = $(ppropertydesc.LINE + 1)],phpType18)',
    ]
    if case['namespace']:
        context += [
            'ptcontext_consumer = ptcontext_property[.NAMESPACE = $base64(' + prior.peer.quoted(case['consumer_namespace']) + ')][.IMPORTS = eps]',
            '~$hook_short_reference_scoped_header(phpType18,ppropertydesc.TYPE,ptcontext_consumer)',
        ] if case['consumer_namespace'] != case['namespace'] else [
            '~$hook_short_reference_scoped_header(phpType18,ppropertydesc.TYPE,ptcontext_property[.NAMESPACE = eps][.IMPORTS = eps])',
        ]
    rows = []
    for check in checks:
        if check.startswith('phpType18 = '):
            check = check.replace('NNameFullyQualified', raw_kind)
        elif check == '$base64(text_type) = $base64(' + prior.peer.quoted(name) + ')':
            check = '$base64(text_type) = $base64(' + prior.peer.quoted(raw_name) + ')'
            rows += [check, *context]
            continue
        elif check.lstrip('~').startswith('$hook_short_reference_header('):
            check = check.replace('$hook_short_reference_header(', '$hook_short_reference_scoped_header(')[:-1] + ',ptcontext_property)'
        elif check.startswith('statement_badraw = '):
            check = check.replace('NNameFullyQualified', raw_kind).replace(prior.peer.quoted(name.swapcase()), prior.peer.quoted(raw_name.swapcase()))
        rows.append(check)
    assert any(row.startswith('ptcontext_property = ') for row in rows)
    return rows


if __name__ == '__main__':
    prior.prior.STEM = 'scoped_class_parentless_short_reference_get_hook'
    prior.prior.fields = fields
    prior.prior.main(extra_paths=[Path(__file__), Path(prior.__file__)])
