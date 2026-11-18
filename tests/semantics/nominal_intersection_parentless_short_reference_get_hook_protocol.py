#!/usr/bin/env python3
"""Check ordered intersection authority, real conjuncts, aliases and detach."""
from pathlib import Path

import builtin_union_parentless_short_reference_get_hook_protocol as runner
import scoped_class_parentless_short_reference_get_hook_review_protocol as names


quoted = lambda text: names.quoted(text.encode())
value = lambda text: '$base64(' + quoted(text) + ')'


def branch(interfaces):
    return '(PTBRANCH ([' + ','.join('PTCLASS (' + value(name) + ')' for name in interfaces) + ']))'


def fields(fixture, source, case):
    lines = [line.strip() for line in source.read_text().splitlines()]
    line = lambda text: lines.index(text) + 1
    atoms = case['interfaces']; typed = '[' + branch(atoms) + ']'
    reversed_type = '[' + branch(list(reversed(atoms))) + ']'
    raw = '[' + ','.join(kind + ' (BYTES text_type_' + str(i) + ') metadata_type_' + str(i)
                         for i, kind in enumerate(case['raw_kinds'])) + ']'
    states = []

    def seek(state, previous, target):
        states.append(state)
        return [state + ' = $lbr_seek(' + previous + ',' + str(target) + ',30000)',
                '$lbr_phase(' + state + ',' + str(target) + ')', state + '.COMPLETION = NORMAL']

    def payload(state, obj, label, tag):
        return [state + '.OBJECTS[' + obj + '] = INSTANCE porigin_' + label,
                '$class_at(' + state + '.CLASSES,porigin_' + label + ') = (pclassdesc_' + label + ')',
                'pclassdesc_' + label + '.NAME = ' + value(case['payload']),
                '$objectprops_at(' + state + '.OBJECTPROPS,' + obj + ') = ([ppropertyslot_' + label + '])',
                'ppropertyslot_' + label + '.NAME = $ptascii("tag")',
                'ppropertyslot_' + label + '.STATE = PROP_VALUE (DIRECT (PINT ' + str(tag) + '))',
                '$typed_object_exact(' + state + ',' + typed + ',POBJECT ' + obj + ')',
                '$typed_object_exact(' + state + ',' + reversed_type + ',POBJECT ' + obj + ')'] + [
                    '$class_origin_matches(' + state + ',porigin_' + label + ',' + value(name) + ',|' + state + '.CLASSES|)'
                    for name in atoms]

    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')']
    checks += seek('S_front', 'S_start', 0)
    checks += [
        '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box338")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc)',
        'pclassdesc.PARENT = eps', '$trait_plan(S_front,pclassdesc).TRAITS = eps',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.NAME = $ptascii("v")',
        'ppropertydesc.KEY = ppropertydesc.NAME', 'ppropertydesc.TYPE = ' + typed,
        'ppropertydesc.DEFAULT = PROP_UNINITIALIZED',
        'pclassdesc.ORIGIN = PORIGIN n_source pcpath_class',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 ABSENT metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = NIntersectionType (SEQUENCE (' + raw + ')) metadata_type',
        'ppropertydesc.LINE = $nabs($source_line(metadata_group))',
        '$source_unit(S_front.SOURCES,n_source) = (pcunit)', 'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$plclasscontext(pcunit,pcpath_class,' + value(str(source)) + ',pclassdesc.LINE) = (ptcontext_class)',
        'ptcontext_class.NAMESPACE = ' + value(case['namespace']),
        'ptcontext_property = ptcontext_class[.SCOPE = PTKNOWN pclassdesc.NAME pclassdesc.PARENT][.POSITION = PTPROPERTY][.OWNER = pclassdesc.NAME][.MEMBER = ppropertydesc.NAME][.LINE = ppropertydesc.LINE]',
        '$ptype_normalize(phpType18,ptcontext_property) = PTOK ppropertydesc.TYPE eps',
        '$hook_short_reference_nominal_intersection_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~$hook_short_reference_nominal_intersection_header(phpType18,' + reversed_type + ',ptcontext_property)',
        '~$hook_short_reference_nominal_union_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '$property_hook_short_reference_header(S_front,pclassdesc,ppropertydesc,phpType18)',
        '$property_hook_reference_decl(S_front,ppropertydesc)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reversed_type + '])',
        '~$property_hook_reference_decl(S_front[.SOURCES = eps],ppropertydesc)',
        '~$property_hook_reference_decl(S_front[.FILES = eps],ppropertydesc)',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = PROP_VALUE (DIRECT (POBJECT n_initial))',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps,RETURNS ppropertydesc.TYPE,BYREF true}',
        ('pfunction.CODE.STRICT' if case['strict'] else '~pfunction.CODE.STRICT'),
        'pfunction.CODE.UNIT = n_source', 'pfunction.ENV.NAMESPACE = ptcontext_class.NAMESPACE',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$hook_short_reference_body(expression_get,ppropertydesc.NAME)',
        'z_body = $expression_line(expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((z_body,false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (z_body)']
    checks += ['$base64(text_type_' + str(i) + ') = ' + value(name) for i, name in enumerate(case['raw_names'])]
    if any(kind != 'NNameFullyQualified' for kind in case['raw_kinds']):
        checks += ['~$hook_short_reference_nominal_intersection_header(phpType18,ppropertydesc.TYPE,ptcontext_property[.NAMESPACE = ' + value(case['consumer_namespace']) + '][.IMPORTS = eps])']
    checks += payload('S_front', 'n_initial', 'initial', 61)
    checks += seek('S_return', 'S_front', -1)
    checks += ['$reference_return_source(S_return,z_body)', '$reference_return_fetch_valid(S_return,z_body)',
               '$reference_verifies(S_return)',
               'S_wrong = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + reversed_type + ']) :: S_return.FUNCTIONS]',
               '~$reference_return_source(S_wrong,z_body)', '~$call_task_valid(S_wrong,RETURN_REF_FETCH z_body)']
    checks += seek('S_fetch', 'S_return', -2)
    checks += ['S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
               'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
               '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    checks += seek('S_aliases', 'S_fetch', line('$copy338 = $box338->v;'))
    checks += ['$lookup(S_aliases.ENV,$ptascii("r338")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("s338")) = (n_field)',
               '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3', '~$property_state_valid(S_aliases[.PROPREFS = eps])']
    replacement = next(i + 1 for i, text in enumerate(lines) if text.startswith('$s338 = new '))
    checks += seek('S_copy', 'S_aliases', replacement)
    checks += ['$lookup(S_copy.ENV,$ptascii("copy338")) = (n_copy)', 'n_copy =/= n_field',
               'S_copy.STORE[n_copy] = DEFINED (POBJECT n_initial)',
               '$propref_at(S_copy.PROPREFS,n_copy) = eps', '$heap_owners($heap_graph(S_copy),HOBJECT n_initial) = 2']
    checks += payload('S_copy', 'n_initial', 'copied', 67)
    checks += seek('S_replaced', 'S_copy', line('$kept338 = $r338;'))
    checks += ['S_replaced.STORE[n_field] = DEFINED (POBJECT n_next)', 'n_next =/= n_initial',
               'S_replaced.STORE[n_copy] = DEFINED (POBJECT n_initial)']
    checks += payload('S_replaced', 'n_next', 'replacement', 71)
    tries = [i + 1 for i, text in enumerate(lines) if text.startswith('try {')]
    assert len(tries) == len(case['missing']) + 1
    checks += seek('S_kept', 'S_replaced', tries[0])
    checks += ['$lookup(S_kept.ENV,$ptascii("kept338")) = (n_kept)', 'S_kept.STORE[n_kept] = DEFINED (POBJECT n_next)']
    previous = 'S_kept'
    for i, target in enumerate(tries[1:] + [line('$r338 = $copy338;')]):
        state = 'S_rejected' + str(i)
        checks += seek(state, previous, target)
        checks += [state + '.STORE[n_field] = DEFINED (POBJECT n_next)', state + '.STORE[n_copy] = DEFINED (POBJECT n_initial)',
                   state + '.STORE[n_kept] = DEFINED (POBJECT n_next)',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3']
        if i < len(case['missing']):
            row = case['missing'][i]
            checks += ['$class_named(' + state + '.CLASSNAMES,$ptlc(' + value(row['class']) + ')) = (porigin_missing' + str(i) + ')',
                       '~$typed_class_branch_match(' + state + ',' + branch(atoms) + ',porigin_missing' + str(i) + ',|' + state + '.CLASSES|)']
            checks += [('~' if atom.lower() == row['absent'].lower() else '') + '$class_origin_matches(' + state + ',porigin_missing' + str(i) + ',' + value(atom) + ',|' + state + '.CLASSES|)' for atom in atoms]
        previous = state
    checks += seek('S_before', previous, -3)
    checks += ['S_before.STORE[n_field] = DEFINED (POBJECT n_initial)', '$heap_owners($heap_graph(S_before),HCELL n_field) = 3']
    checks += seek('S_detached', 'S_before', line('$s338 = [];'))
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
               'S_detached.STORE[n_field] = DEFINED (POBJECT n_initial)', '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2']
    checks += seek('S_free', 'S_detached', line('$r338 = false;'))
    checks += ['S_free.STORE[n_field] = DEFINED (PARRAY n_free)', 'S_free.ARRAYS[n_free].ITEMS = eps',
               '$propref_at(S_free.PROPREFS,n_field) = eps',
               'S_end = $drive_steps(S_free,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
               '$lbr_output(S_end.EVENTS) = ' + value(case['stdout'])]
    checks += ['~((' + kind + ' ' + item + ') <- S_end.ALLOCATIONS)' for kind, item in [('HOBJECT','n_root'),('HOBJECT','n_initial'),('HOBJECT','n_next'),('HCELL','n_field'),('HCELL','n_rootcell'),('HCELL','n_copy'),('HCELL','n_kept')]]
    for state in states + ['S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')', '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in [('return','S_return'),('cleanup','S_before')]:
        checks += ['S_' + label + '_zero = $drive_steps(' + state + ',0)',
                   'S_' + label + '_zero = ' + state + '[.COMPLETION = BUDGET]',
                   '$drive_steps(S_' + label + '_zero[.COMPLETION = NORMAL],1) = $drive_steps(' + state + ',1)']
    return checks


def main():
    runner.PREFIX = runner.PREFIX.replace('box320', 'box338').replace('a320', 'r338').replace('b320', 's338')
    runner.PREFIX = runner.PREFIX.replace('$property_hook_plan(S) =/= eps', '$property_hook_ref_plan(S) =/= eps')
    runner.PREFIX = runner.PREFIX.replace('(PROPERTY_HOOK_RESULT ppropertyhook)', '(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch")')
    runner.STEM = 'nominal_intersection_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(__file__), Path(names.__file__)])


if __name__ == '__main__':
    main()
