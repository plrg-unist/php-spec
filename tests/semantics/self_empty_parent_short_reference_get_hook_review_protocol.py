#!/usr/bin/env python3
"""Review the strict child slot, parent authority and retained self constraint."""
import self_empty_parent_short_reference_get_hook_protocol as author

original_fields = author.fields


def fields(fixture, source, case):
    checks = original_fields(fixture, source, case)
    checks += [
        'porigin_root =/= porigin_parent',
        '$class_origin_matches(S_front,porigin_root,pclassdesc_parent.NAME,|S_front.CLASSES|)',
        '~$class_origin_matches(S_front,porigin_parent,pclassdesc.NAME,|S_front.CLASSES|)',
        'S_wrong_link = S_front[.LINKEDPARENTS = [CLASSLINK porigin_root (SOURCE_PARENT porigin_root)]]',
        '~$property_hook_reference_decl(S_wrong_link,ppropertydesc)',
        'S_wrong_names = S_front[.CLASSNAMES = [($ptlc(pclassdesc_parent.NAME),porigin_root),($ptlc(pclassdesc.NAME),porigin_root)]]',
        '~$property_hook_reference_decl(S_wrong_names,ppropertydesc)',
        'pclassdesc_parent.ORIGIN = PORIGIN n_source pcpath_parent',
        'pcnode_parent = NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier phpType33_parent metadata_parent_name) ABSENT (SEQUENCE eps) (SEQUENCE ([NStmtNop metadata_parent])) metadata_parent',
        'S_parent_body = S_front[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent pcnode_parent) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_pair_source_headers(S_parent_body,pclassdesc,pclassdesc_parent)',
        '~$property_hook_reference_decl(S_parent_body,ppropertydesc)',
    ]
    for label, change in (
        ('parent_kind', '.KIND = "interface"'),
        ('parent_origin', '.ORIGIN = pclassdesc.ORIGIN'),
        ('parent_line', '.LINE = 0'),
        ('owner_name', '.NAME = pclassdesc.NAME ++ [88]'),
        ('owner_readonly', '.READONLY = true'),
    ):
        descriptor = 'pclassdesc_parent' if label.startswith('parent_') else 'pclassdesc'
        state = 'S_' + label
        checks += [state + ' = S_front[.CLASSES = (' + descriptor + '[' + change + ']) :: S_front.CLASSES]',
                   '~$property_hook_reference_decl(' + state + ',ppropertydesc)']
    for label, change in (
        ('parent_type', '.TYPE = [(PTBRANCH ([PTCLASS pclassdesc_parent.NAME]))]'),
        ('nullable_type', '.TYPE = ppropertydesc.TYPE ++ [(PTBRANCH ([PTBUILTIN "null"]))]'),
        ('intersection_type', '.TYPE = [(PTBRANCH ([PTCLASS pclassdesc.NAME,PTCLASS pclassdesc_parent.NAME]))]'),
        ('static_slot', '.STATIC = true'),
        ('readonly_slot', '.READONLY = true'),
        ('foreign_origin', '.ORIGIN = pclassdesc_parent.ORIGIN'),
    ):
        prop = 'ppropertydesc_' + label
        state = 'S_' + label
        checks += [prop + ' = ppropertydesc[' + change + ']',
                   state + ' = S_front[.CLASSES = (pclassdesc[.PROPERTIES = [' + prop + ']]) :: S_front.CLASSES]',
                   '~$property_hook_reference_decl(' + state + ',' + prop + ')']
    return checks


if __name__ == '__main__':
    author.fields = fields
    author.main()
