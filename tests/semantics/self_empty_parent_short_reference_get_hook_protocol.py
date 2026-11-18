#!/usr/bin/env python3
"""Check own self backing, parent authority and reference-source detachment."""
from pathlib import Path

import self_parentless_short_reference_get_hook_protocol as protocol


def fields(fixture, source, case):
    checks = protocol.fields(fixture, source, case)
    parent = '$base64(' + protocol.quoted(case['parent']) + ')'
    assert checks.count('pclassdesc.PARENT = eps') == 1
    checks[checks.index('pclassdesc.PARENT = eps')] = 'pclassdesc.PARENT = (' + parent + ')'
    checks += [
        '$class_named(S_front.CLASSNAMES,$ptlc(' + parent + ')) = (porigin_parent)',
        '$class_link_at(S_front.LINKEDPARENTS,porigin_root) = (SOURCE_PARENT porigin_parent)',
        '$class_at(S_front.CLASSES,porigin_parent) = (pclassdesc_parent)',
        'pclassdesc_parent.NAME = ' + parent,
        'pclassdesc_parent.KIND = "class"', 'pclassdesc_parent.PARENT = eps',
        'pclassdesc_parent.PROPERTIES = eps', 'pclassdesc_parent.METHODS = eps',
        'pclassdesc_parent.CONSTANTS = eps', 'pclassdesc_parent.INTERFACES = eps',
        '~pclassdesc_parent.ABSTRACT', '~pclassdesc_parent.FINAL', '~pclassdesc_parent.READONLY',
        '$origin_node(S_front.SOURCES,pclassdesc_parent.ORIGIN) = (NStmtClass (SEQUENCE eps) (INTEGER 0) (NIdentifier phpType33_parent metadata_parent_name) ABSENT (SEQUENCE eps) (SEQUENCE eps) metadata_parent)',
        '$property_hook_pair_source_headers(S_front,pclassdesc,pclassdesc_parent)',
        '$property_hook_reference_ancestor(S_front,porigin_root,ppropertydesc)',
        '~$property_hook_reference_decl(S_front[.CLASSNAMES = eps],ppropertydesc)',
        '~$property_hook_reference_decl(S_front[.LINKEDPARENTS = eps],ppropertydesc)',
        'S_renamed_parent = S_front[.CLASSES = (pclassdesc_parent[.NAME = pclassdesc_parent.NAME ++ [88]]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_renamed_parent,ppropertydesc)',
        'S_nonroot_parent = S_front[.CLASSES = (pclassdesc_parent[.PARENT = (pclassdesc.NAME)]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_nonroot_parent,ppropertydesc)',
        'S_parent_slot = S_front[.CLASSES = (pclassdesc_parent[.PROPERTIES = [ppropertydesc]]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_parent_slot,ppropertydesc)',
        'S_parent_interface = S_front[.CLASSES = (pclassdesc_parent[.INTERFACES = [pclassdesc.NAME]]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_parent_interface,ppropertydesc)',
        'S_final_parent = S_front[.CLASSES = (pclassdesc_parent[.FINAL = true]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_final_parent,ppropertydesc)',
        'S_abstract_parent = S_front[.CLASSES = (pclassdesc_parent[.ABSTRACT = true]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_abstract_parent,ppropertydesc)',
        'S_readonly_parent = S_front[.CLASSES = (pclassdesc_parent[.READONLY = true]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_readonly_parent,ppropertydesc)',
    ]
    return checks


def main():
    runner = protocol.runner
    runner.PREFIX = runner.PREFIX.replace('box320', 'box341').replace('a320', 'r341').replace('b320', 's341')
    runner.PREFIX = runner.PREFIX.replace('$property_hook_plan(S) =/= eps', '$property_hook_ref_plan(S) =/= eps')
    runner.PREFIX = runner.PREFIX.replace('(PROPERTY_HOOK_RESULT ppropertyhook)', '(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch")')
    runner.PREFIX = runner.PREFIX.replace('def $lbr_phase(S,z) = false -- otherwise', '''def $lbr_phase(S,z) = true
  -- if $(z < -4)
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $source_line(metadata) = $(0 - z)
def $lbr_phase(S,z) = false -- otherwise''')
    runner.STEM = 'self_empty_parent_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(__file__), Path(protocol.__file__), Path(protocol.names.__file__)])


if __name__ == '__main__':
    main()
