#!/usr/bin/env python3
"""Check mixed DNF Get conjuncts, coercions, COW and real detach."""
from pathlib import Path

import builtin_union_parentless_short_reference_get_hook_protocol as runner
import scoped_class_parentless_short_reference_get_hook_review_protocol as names

HELPER = '$hook_short_reference_mixed_nominal_dnf_header'
MEMBERS = '$hook_short_reference_mixed_nominal_dnf_members'


def quoted(text):
    return names.quoted(text.encode())


def branches(parts):
    return '[' + ','.join('(PTBRANCH ([' + ','.join('PTCLASS ' + names.value(atom.encode()) for atom in part['classes']) + ']))'
                          if 'classes' in part else '(PTBRANCH ([PTBUILTIN "' + part['builtin'] + '"]))'
                          for part in parts) + ']'


def fields(fixture, source, case):
    assert case['body'] in ('identifier', 'literal')
    lines = [line.strip() for line in source.read_text().splitlines()]
    line = lambda text, last=False: ([i + 1 for i, found in enumerate(lines) if found == text][-1 if last else 0])
    get_line = next(i + 1 for i, text in enumerate(lines) if '&get =>' in text)
    body_line = get_line + 1
    typed = branches(case['resolved'])
    reversed_type = branches(list(reversed(case['resolved'])))
    atom_reversed_type = branches([{'classes': list(reversed(part['classes']))} if 'classes' in part else part
                                   for part in case['resolved']])
    intersections = sum(len(part.get('classes', [])) >= 2 for part in case['resolved'])
    builtins = sum('builtin' in part for part in case['resolved'])
    atoms = list(dict.fromkeys(atom for part in case['resolved'] for atom in part.get('classes', [])))
    states = []

    def seek(state, previous, target):
        states.append(state)
        return [f'{state} = $lbr_seek({previous},{target},30000)',
                f'$lbr_phase({state},{target})', f'{state}.COMPLETION = NORMAL']

    def payload(state, obj, label, name, tag):
        return [state + '.OBJECTS[' + obj + '] = INSTANCE porigin_' + label,
                '$class_at(' + state + '.CLASSES,porigin_' + label + ') = (pclassdesc_' + label + ')',
                'pclassdesc_' + label + '.NAME = $base64(' + quoted(name) + ')',
                'pclassdesc_' + label + '.PARENT = eps', 'pclassdesc_' + label + '.METHODS = eps',
                '$objectprops_at(' + state + '.OBJECTPROPS,' + obj + ') = ([ppropertyslot_' + label + '])',
                'ppropertyslot_' + label + '.NAME = $ptascii("tag")',
                'ppropertyslot_' + label + '.STATE = PROP_VALUE (DIRECT (PINT ' + str(tag) + '))',
                '$typed_object_exact(' + state + ',' + typed + ',POBJECT ' + obj + ')',
                '$typed_object_exact(' + state + ',' + reversed_type + ',POBJECT ' + obj + ')',
                '$typed_object_exact(' + state + ',' + atom_reversed_type + ',POBJECT ' + obj + ')'] + [
                ('' if atom.lower() in {implemented.lower() for implemented in case['payload_interfaces'][name]} else '~') +
                '$class_origin_matches(' + state + ',porigin_' + label + ',' + names.value(atom.encode()) + ',|' + state + '.CLASSES|)'
                for atom in atoms] + [
                ('' if 'classes' in part and all(atom.lower() in {x.lower() for x in case['payload_interfaces'][name]} for atom in part['classes']) else '~') +
                '$typed_class_branch_match(' + state + ',' + branches([part])[1:-1] + ',porigin_' + label + ',|' + state + '.CLASSES|)'
                for part in case['resolved']]

    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')']
    checks += seek('S_seed', 'S_start', line('$box340->v = $seed340;'))
    checks += seek('S_front', 'S_seed', 0)
    raw_parts = []
    for i, group in enumerate(case['raw_branches']):
        members = [row['kind'] + ' (BYTES text_type_' + str(i) + '_' + str(j) + ') metadata_type_' + str(i) + '_' + str(j)
                   for j, row in enumerate(group)]
        raw_parts.append(members[0] if len(members) == 1 else 'NIntersectionType (SEQUENCE ([' + ','.join(members) + '])) metadata_branch_' + str(i))
    raw_nodes = '[' + ','.join(raw_parts) + ']'
    raw = 'NUnionType (SEQUENCE (' + raw_nodes + ')) metadata_union'
    checks += [
        '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box340")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN n_source pcpath_class',
        'pclassdesc.KIND = "class"', 'pclassdesc.PARENT = eps',
        '$trait_plan(S_front,pclassdesc).TRAITS = eps',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + typed,
        'ppropertydesc.DEFAULT = PROP_UNINITIALIZED',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 ABSENT metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = ' + raw, 'ppropertydesc.LINE = $nabs($source_line(metadata_group))',
        '$property_hook_pair_source_header(S_front,pclassdesc)',
        '$source_unit(S_front.SOURCES,n_source) = (pcunit)',
        'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$call_sourcefile(S_front.FILES,pclassdesc.ORIGIN) = $base64(' + quoted(str(source)) + ')',
        '$plclasscontext(pcunit,pcpath_class,$base64(' + quoted(str(source)) + '),pclassdesc.LINE) = (ptcontext_class)',
        'ptcontext_class.NAMESPACE = $base64(' + quoted(case['namespace']) + ')',
        'ptcontext_property = ptcontext_class[.SCOPE = PTKNOWN pclassdesc.NAME pclassdesc.PARENT][.POSITION = PTPROPERTY][.OWNER = pclassdesc.NAME][.MEMBER = ppropertydesc.NAME][.LINE = ppropertydesc.LINE]',
        '$ptype_normalize(phpType18,ptcontext_property) = PTOK ppropertydesc.TYPE eps',
        HELPER + '(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        MEMBERS + '(' + raw_nodes + ',ppropertydesc.TYPE,ptcontext_property) = ((' + str(intersections) + ',' + str(builtins) + '))',
        '~' + HELPER + '(phpType18,' + reversed_type + ',ptcontext_property)',
        '~' + HELPER + '(phpType18,' + atom_reversed_type + ',ptcontext_property)',
        '~$hook_short_reference_nominal_dnf_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~$hook_short_reference_mixed_nominal_union_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~$hook_short_reference_nominal_union_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~$hook_short_reference_nominal_pair_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~$hook_short_reference_class_builtin_union_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '$property_hook_short_reference_header(S_front,pclassdesc,ppropertydesc,phpType18)',
        '$property_hook_reference_decl(S_front,ppropertydesc)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reversed_type + '])',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.LINE = 0])',
        '~$property_hook_reference_decl(S_front[.FILES = eps],ppropertydesc)',
        '~$property_hook_reference_decl(S_front[.SOURCES = eps],ppropertydesc)',
        '$pttypename(ppropertydesc.TYPE) = $base64(' + quoted(case['typename']) + ')',
        '$objectprops_at(S_seed.OBJECTPROPS,n_root) = ([ppropertyslot_seed])',
        'ppropertyslot_seed.STATE = PROP_INITIAL',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = PROP_VALUE (DIRECT (POBJECT n_first))',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        ('pfunction.CODE.STRICT' if case['strict'] else '~pfunction.CODE.STRICT'),
        'pfunction.ENV.NAMESPACE = ptcontext_class.NAMESPACE',
        'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]', 'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (' + ('NIdentifier' if case['body'] == 'identifier' else 'NScalarString') + ' (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = ' + str(get_line), '$source_line(metadata_expression) = ' + str(body_line),
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((' + str(body_line) + ',false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (' + str(body_line) + ')']
    checks += ['$base64(text_type_' + str(i) + '_' + str(j) + ') = $base64(' + quoted(row['name']) + ')'
               for i, group in enumerate(case['raw_branches']) for j, row in enumerate(group)]
    if any(row['kind'] in ('NName', 'NNameRelative') for group in case['raw_branches'] for row in group):
        checks += ['ptcontext_consumer = ptcontext_property[.NAMESPACE = $base64(' + quoted(case['consumer_namespace']) + ')][.IMPORTS = eps]',
                   '~' + HELPER + '(phpType18,ppropertydesc.TYPE,ptcontext_consumer)']
    checks += payload('S_front', 'n_first', 'initial', case['first_object'], 61)
    checks += seek('S_return', 'S_front', -1)
    checks += ['$reference_return_source(S_return,' + str(body_line) + ')',
               '$reference_return_fetch_valid(S_return,' + str(body_line) + ')', '$reference_verifies(S_return)',
               'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + reversed_type + ']) :: S_return.FUNCTIONS]',
               '~$reference_return_source(S_wrongreturn,' + str(body_line) + ')',
               '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH ' + str(body_line) + ')']
    checks += seek('S_fetch', 'S_return', -2)
    checks += ['S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
               'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
               '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    checks += seek('S_aliases', 'S_fetch', line('$copy340 = $box340->v;'))
    checks += ['$lookup(S_aliases.ENV,$ptascii("r340")) = (n_field)',
               '$lookup(S_aliases.ENV,$ptascii("s340")) = (n_field)',
               'S_aliases.STORE[n_field] = DEFINED (POBJECT n_first)',
               '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
               '~$property_state_valid(S_aliases[.PROPREFS = eps])']
    checks += seek('S_copied', 'S_aliases', line(case['assignments'][0]['statement']))
    checks += ['$lookup(S_copied.ENV,$ptascii("copy340")) = (n_copycell)',
               'S_copied.STORE[n_copycell] = DEFINED (POBJECT n_first)', 'n_copycell =/= n_field',
               '$propref_at(S_copied.PROPREFS,n_copycell) = eps',
               '$heap_owners($heap_graph(S_copied),HOBJECT n_first) = 2']
    checks += payload('S_copied', 'n_first', 'copied', case['first_object'], 67)
    previous = 'S_copied'; objects = ['n_first']
    for i, assignment in enumerate(case['assignments']):
        state, obj = 'S_object' + str(i), 'n_object' + str(i); objects.append(obj)
        target = case['assignments'][i + 1]['statement'] if i + 1 < len(case['assignments']) else '$kept340 = $r340;'
        checks += seek(state, previous, line(target))
        checks += [state + '.STORE[n_field] = DEFINED (POBJECT ' + obj + ')', obj + ' =/= n_first',
                   state + '.STORE[n_copycell] = DEFINED (POBJECT n_first)',
                   '$typed_object_exact(' + state + ',' + typed + ',POBJECT ' + obj + ')',
                   '~$typed_object_exact(' + state + ',' + branches([part for part in case['resolved'] if 'classes' not in part or not all(atom.lower() in {name.lower() for name in case['payload_interfaces'][assignment['object']]} for atom in part['classes'])]) + ',POBJECT ' + obj + ')',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3']
        checks += payload(state, obj, 'object' + str(i), assignment['object'], assignment['tag']); previous = state
    live = objects[-1]
    tries = [text for text in lines if text.startswith('try {')]
    checks += seek('S_kept', previous, line(tries[0]))
    checks += ['$lookup(S_kept.ENV,$ptascii("kept340")) = (n_keptcell)',
               'S_kept.STORE[n_keptcell] = DEFINED (POBJECT ' + live + ')',
               '$heap_owners($heap_graph(S_kept),HOBJECT ' + live + ') = 2', 'n_wrong = |S_kept.OBJECTS|']
    previous = 'S_kept'
    first_value = '$arrayseed340 = 3;' if case.get('array') else case['steps'][0]['statement']
    for i, marker in enumerate(tries[1:] + [first_value]):
        state = 'S_rejected' + str(i); checks += seek(state, previous, line(marker))
        checks += [state + '.STORE[n_field] = DEFINED (POBJECT ' + live + ')',
                   state + '.STORE[n_copycell] = DEFINED (POBJECT n_first)',
                   state + '.STORE[n_keptcell] = DEFINED (POBJECT ' + live + ')',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3',
                   '~((HOBJECT n_wrong) <- ' + state + '.ALLOCATIONS)']
        if i < len(case['missing']):
            row = case['missing'][i]; present = {name.lower() for name in row['present']}
            checks += ['$class_named(' + state + '.CLASSNAMES,$ptlc($base64(' + quoted(row['class']) + '))) = (porigin_missing' + str(i) + ')',
                       '~$typed_class_chain(' + state + ',' + typed + ',porigin_missing' + str(i) + ',|' + state + '.CLASSES|)']
            checks += ['~$typed_class_branch_match(' + state + ',' + branches([part])[1:-1] + ',porigin_missing' + str(i) + ',|' + state + '.CLASSES|)' for part in case['resolved']]
            checks += [('' if atom.lower() in present else '~') + '$class_origin_matches(' + state + ',porigin_missing' + str(i) + ',' + names.value(atom.encode()) + ',|' + state + '.CLASSES|)' for atom in atoms]
        previous = state
    if case.get('array'):
        checks += seek('S_array', previous, line(case['steps'][0]['statement']))
        checks += ['S_array.STORE[n_field] = DEFINED (PARRAY n_arraylive)',
                   '$lookup(S_array.ENV,$ptascii("arraycopy340")) = (n_arraycopycell)',
                   'S_array.STORE[n_arraycopycell] = DEFINED (PARRAY n_arraycopy)', 'n_arraylive =/= n_arraycopy',
                   '$lookup(S_array.ENV,$ptascii("arrayseed340")) = (n_arrayseed)',
                   'S_array.STORE[n_arrayseed] = DEFINED (PINT 11)',
                   'S_array.ARRAYS[n_arraylive].ITEMS = [ENTRY (KINT 0) (ALIAS n_arrayseed),ENTRY (KINT 1) (DIRECT (PARRAY n_innerlive))]',
                   'S_array.ARRAYS[n_arraycopy].ITEMS = [ENTRY (KINT 0) (ALIAS n_arrayseed),ENTRY (KINT 1) (DIRECT (PARRAY n_innercopy))]',
                   'n_innerlive =/= n_innercopy',
                   'S_array.ARRAYS[n_innerlive].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 7))]',
                   'S_array.ARRAYS[n_innercopy].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 5))]',
                   '$propref_at(S_array.PROPREFS,n_arraycopycell) = eps',
                   '$heap_owners($heap_graph(S_array),HCELL n_arrayseed) = 3',
                   '$heap_owners($heap_graph(S_array),HARRAY n_arraylive) = 1',
                   '$heap_owners($heap_graph(S_array),HARRAY n_arraycopy) = 1']
        previous = 'S_array'
    for i, step in enumerate(case['steps']):
        state = 'S_value' + str(i)
        marker = case['steps'][i + 1]['statement'] if i + 1 < len(case['steps']) else '$r340 = $kept340;'
        checks += seek(state, previous, line(marker))
        checks += [state + '.STORE[n_field] = DEFINED (' + step['value'] + ')',
                   state + '.STORE[n_keptcell] = DEFINED (POBJECT ' + live + ')',
                   state + '.STORE[n_copycell] = DEFINED (POBJECT n_first)',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3']; previous = state
    checks += seek('S_before', previous, -3)
    checks += ['S_before.STORE[n_field] = DEFINED (POBJECT ' + live + ')',
               '$heap_owners($heap_graph(S_before),HCELL n_field) = 3',
               '$heap_owners($heap_graph(S_before),HOBJECT ' + live + ') = 2',
               '$heap_owners($heap_graph(S_before),HOBJECT n_first) = 1']
    checks += seek('S_detached', 'S_before', line('$s340 = ' + case['free'] + ';'))
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
               '$propref_at(S_detached.PROPREFS,n_field) = eps',
               'S_detached.STORE[n_field] = DEFINED (POBJECT ' + live + ')',
               '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2']
    checks += seek('S_free', 'S_detached', line('$r340 = false;', last=True))
    if case['free'] == '[]':
        checks += ['S_free.STORE[n_field] = DEFINED (PARRAY n_free)', 'S_free.ARRAYS[n_free].ITEMS = eps']
    elif case['free'] == 'false':
        checks += ['S_free.STORE[n_field] = DEFINED (PBOOL false)']
    else:
        checks += ['S_free.STORE[n_field] = DEFINED (PINT 149)']
    checks += ['$propref_at(S_free.PROPREFS,n_field) = eps',
               'S_free.STORE[n_keptcell] = DEFINED (POBJECT ' + live + ')',
               'S_end = $drive_steps(S_free,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
               '$lbr_output(S_end.EVENTS) = $base64(' + quoted(case['stdout']) + ')']
    checks += ['~((HOBJECT ' + obj + ') <- S_end.ALLOCATIONS)' for obj in objects + ['n_root']]
    checks += ['~((HCELL ' + cell + ') <- S_end.ALLOCATIONS)' for cell in ('n_rootcell', 'n_field', 'n_copycell', 'n_keptcell')]
    if case.get('array'):
        checks += ['~((HARRAY n_arraylive) <- S_end.ALLOCATIONS)', '~((HARRAY n_arraycopy) <- S_end.ALLOCATIONS)',
                   '~((HARRAY n_innerlive) <- S_end.ALLOCATIONS)', '~((HCELL n_arrayseed) <- S_end.ALLOCATIONS)',
                   '~((HCELL n_arraycopycell) <- S_end.ALLOCATIONS)']
    for state in states + ['S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    checks += ['S_return_zero = $drive_steps(S_return,0)', 'S_return_zero = S_return[.COMPLETION = BUDGET]',
               'S_return_one = $drive_steps(S_return_zero[.COMPLETION = NORMAL],1)',
               'S_return_one = $drive_steps(S_return,1)',
               '$drive_steps(S_return_one[.COMPLETION = NORMAL],30000) = S_end',
               'S_cleanup_zero = $drive_steps(S_before,0)', 'S_cleanup_zero = S_before[.COMPLETION = BUDGET]',
               '$drive_steps(S_cleanup_zero[.COMPLETION = NORMAL],1) = $drive_steps(S_before,1)']
    return checks


def main():
    runner.PREFIX = runner.PREFIX.replace('box320', 'box340').replace('a320', 'r340').replace('b320', 's340')
    runner.PREFIX = runner.PREFIX.replace('$property_hook_plan(S) =/= eps', '$property_hook_ref_plan(S) =/= eps')
    runner.PREFIX = runner.PREFIX.replace('(PROPERTY_HOOK_RESULT ppropertyhook)', '(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch")')
    runner.STEM = 'mixed_nominal_dnf_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(__file__), Path(names.__file__)])


if __name__ == '__main__':
    main()
