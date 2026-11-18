#!/usr/bin/env python3
"""Check defining self authority, typed aliases and physical source detachment."""
from pathlib import Path

import builtin_union_parentless_short_reference_get_hook_protocol as runner
import scoped_class_parentless_short_reference_get_hook_review_protocol as names


def quoted(text):
    return names.quoted(text.encode())


def fields(fixture, source, case):
    lines = [line.strip() for line in source.read_text().splitlines()]
    line = lambda text: lines.index(text) + 1
    get_line = next(i + 1 for i, text in enumerate(lines) if '&get =>' in text)
    body_line = get_line + 1
    nominal = '(PTBRANCH ([PTCLASS ' + names.value(case['class'].encode()) + ']))'
    branches = [nominal]
    if case.get('other'):
        other = case['other']
        alternate = '(PTBRANCH ([PTCLASS ' + names.value(other['class'].encode()) + ']))'
        branches.insert(0 if other['first'] else 1, alternate)
    elif case['nullable']:
        branches.append('(PTBRANCH ([PTBUILTIN "null"]))')
    elif case['builtin']:
        branches.insert(0 if case['builtin_first'] else 1, '(PTBRANCH ([PTBUILTIN "' + case['builtin'] + '"]))')
    typed = '[' + ','.join(branches) + ']'
    raw_self = case['raw_kind'] + ' (BYTES text_self) metadata_self'
    raw = raw_self
    if case.get('other'):
        raw_members = [raw_self]
        raw_members.insert(0 if other['first'] else 1, other['raw_kind'] + ' (BYTES text_other) metadata_other')
        raw = 'NUnionType (SEQUENCE ([' + ','.join(raw_members) + '])) metadata_type'
    elif case['nullable']:
        raw = 'NNullableType (' + raw_self + ') metadata_type'
    elif case['builtin']:
        raw_members = [raw_self]
        raw_members.insert(0 if case['builtin_first'] else 1, 'NIdentifier (BYTES text_builtin) metadata_builtin')
        raw = 'NUnionType (SEQUENCE ([' + ','.join(raw_members) + '])) metadata_type'
    states = []; step_objects = []

    def seek(state, previous, target):
        states.append(state)
        return [f'{state} = $lbr_seek({previous},{target},30000)',
                f'$lbr_phase({state},{target})', f'{state}.COMPLETION = NORMAL']

    def payload(state, obj, label):
        return [state + '.OBJECTS[' + obj + '] = INSTANCE porigin_root',
                '$objectprops_at(' + state + '.OBJECTPROPS,' + obj + ') = ([ppropertyslot_' + label + '])',
                'ppropertyslot_' + label + '.NAME = $ptascii("v")',
                'ppropertyslot_' + label + '.STATE = PROP_INITIAL',
                '$typed_object_exact(' + state + ',' + typed + ',POBJECT ' + obj + ')']

    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')']
    checks += seek('S_seed', 'S_start', line('$box341->v = $seed341;'))
    checks += seek('S_front', 'S_seed', 0)
    checks += [
        '$property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))',
        '$lookup(S_front.ENV,$ptascii("box341")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN n_source pcpath_class',
        'pclassdesc.NAME = $base64(' + quoted(case['class']) + ')',
        'pclassdesc.KIND = "class"', 'pclassdesc.PARENT = eps',
        '$trait_plan(S_front,pclassdesc).TRAITS = eps',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + typed,
        'ppropertydesc.DEFAULT = PROP_UNINITIALIZED',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 ABSENT metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = ' + raw,
        '$base64(text_self) = $base64(' + quoted(case['raw_name']) + ')',
        'ppropertydesc.LINE = $nabs($source_line(metadata_group))',
        '$property_hook_pair_source_header(S_front,pclassdesc)',
        '$source_unit(S_front.SOURCES,n_source) = (pcunit)',
        'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$call_sourcefile(S_front.FILES,pclassdesc.ORIGIN) = $base64(' + quoted(str(source)) + ')',
        '$plclasscontext(pcunit,pcpath_class,$base64(' + quoted(str(source)) + '),pclassdesc.LINE) = (ptcontext_class)',
        'ptcontext_class.NAMESPACE = $base64(' + quoted(case['namespace']) + ')',
        'ptcontext_property = ptcontext_class[.SCOPE = PTKNOWN pclassdesc.NAME pclassdesc.PARENT][.POSITION = PTPROPERTY][.OWNER = pclassdesc.NAME][.MEMBER = ppropertydesc.NAME][.LINE = ppropertydesc.LINE]',
        '$ptype_normalize(phpType18,ptcontext_property) = PTOK ppropertydesc.TYPE eps',
        '$hook_short_reference_scoped_header(' + raw_self + ',[' + nominal + '],ptcontext_property)',
        '~$hook_short_reference_header(' + raw_self + ',[' + nominal + '])',
        '~$hook_short_reference_scoped_header(' + raw_self + ',[(PTBRANCH ([PTCLASS ($ptascii("Wrong341"))]))],ptcontext_property)',
        'ptcontext_consumer = ptcontext_property[.NAMESPACE = $base64(' + quoted(case['consumer_namespace']) + ')][.IMPORTS = eps]',
        '$hook_short_reference_scoped_header(' + raw_self + ',[' + nominal + '],ptcontext_consumer)',
        '$property_hook_short_reference_header(S_front,pclassdesc,ppropertydesc,phpType18)',
        '$property_hook_reference_decl(S_front,ppropertydesc)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = eps])',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.LINE = 0])',
        '~$property_hook_reference_decl(S_front[.FILES = eps],ppropertydesc)',
        '~$property_hook_reference_decl(S_front[.SOURCES = eps],ppropertydesc)',
        '$pttypename(ppropertydesc.TYPE) = $base64(' + quoted(case['typename']) + ')',
        '$objectprops_at(S_seed.OBJECTPROPS,n_root) = ([ppropertyslot_seed])',
        'ppropertyslot_seed.STATE = PROP_INITIAL',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])',
        'ppropertyslot_front.STATE = PROP_VALUE (DIRECT (POBJECT n_first))', 'n_root =/= n_first',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        ('pfunction.CODE.STRICT' if case['strict'] else '~pfunction.CODE.STRICT'),
        'pfunction.ENV.NAMESPACE = ptcontext_class.NAMESPACE',
        'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]', 'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = ' + str(get_line), '$source_line(metadata_expression) = ' + str(body_line),
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((' + str(body_line) + ',false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (' + str(body_line) + ')']
    if case['builtin']:
        checks += ['$base64(text_builtin) = $ptascii("' + case['builtin'] + '")']
    if case.get('other'):
        checks += ['$base64(text_other) = $base64(' + quoted(other['raw_name']) + ')',
                   '$hook_short_reference_nominal_pair_header(phpType18,ppropertydesc.TYPE,ptcontext_property)']
    checks += payload('S_front', 'n_first', 'first')
    checks += seek('S_return', 'S_front', -1)
    checks += ['$reference_return_source(S_return,' + str(body_line) + ')',
               '$reference_return_fetch_valid(S_return,' + str(body_line) + ')', '$reference_verifies(S_return)',
               'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = eps]) :: S_return.FUNCTIONS]',
               '~$reference_return_source(S_wrongreturn,' + str(body_line) + ')',
               '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH ' + str(body_line) + ')']
    checks += seek('S_fetch', 'S_return', -2)
    checks += ['S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
               'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
               '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    checks += seek('S_aliases', 'S_fetch', line('$copy341 = $box341->v;'))
    checks += ['$lookup(S_aliases.ENV,$ptascii("r341")) = (n_field)',
               '$lookup(S_aliases.ENV,$ptascii("s341")) = (n_field)',
               '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
               '~$property_state_valid(S_aliases[.PROPREFS = eps])']
    checks += seek('S_copied', 'S_aliases', line('$s341 = new \\' + case['class'] + '();'))
    checks += ['$lookup(S_copied.ENV,$ptascii("copy341")) = (n_copycell)',
               'S_copied.STORE[n_copycell] = DEFINED (POBJECT n_first)', 'n_copycell =/= n_field',
               '$propref_at(S_copied.PROPREFS,n_copycell) = eps',
               '$heap_owners($heap_graph(S_copied),HOBJECT n_first) = 2']
    checks += seek('S_replaced', 'S_copied', line('$kept341 = $r341;'))
    checks += ['S_replaced.STORE[n_field] = DEFINED (POBJECT n_live)', 'n_live =/= n_first',
               'n_live =/= n_root', 'S_replaced.STORE[n_copycell] = DEFINED (POBJECT n_first)']
    checks += payload('S_replaced', 'n_live', 'live')
    tries = [text for text in lines if text.startswith('try {')]
    checks += seek('S_kept', 'S_replaced', line(tries[0]))
    checks += ['$lookup(S_kept.ENV,$ptascii("kept341")) = (n_keptcell)',
               'S_kept.STORE[n_keptcell] = DEFINED (POBJECT n_live)',
               '$heap_owners($heap_graph(S_kept),HOBJECT n_live) = 2', 'n_wrong = |S_kept.OBJECTS|']
    previous = 'S_kept'
    first_value = case['steps'][0]['statement'] if case['steps'] else '$r341 = $kept341;'
    for i, marker in enumerate(tries[1:] + [first_value]):
        state = 'S_rejected' + str(i); checks += seek(state, previous, line(marker))
        checks += [state + '.STORE[n_field] = DEFINED (POBJECT n_live)',
                   state + '.STORE[n_copycell] = DEFINED (POBJECT n_first)',
                   state + '.STORE[n_keptcell] = DEFINED (POBJECT n_live)',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3',
                   '~((HOBJECT n_wrong) <- ' + state + '.ALLOCATIONS)']
        previous = state
    for i, step in enumerate(case['steps']):
        state = 'S_value' + str(i)
        marker = case['steps'][i + 1]['statement'] if i + 1 < len(case['steps']) else '$r341 = $kept341;'
        checks += seek(state, previous, line(marker))
        checks += [state + '.STORE[n_field] = DEFINED (' + step['value'] + ')',
                   state + '.STORE[n_keptcell] = DEFINED (POBJECT n_live)',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)']; previous = state
        if 'object' in step:
            obj = step['value'].split()[1]; step_objects.append(obj)
            checks += [state + '.OBJECTS[' + obj + '] = INSTANCE porigin_alternate',
                       '$class_at(' + state + '.CLASSES,porigin_alternate) = (pclassdesc_alternate)',
                       'pclassdesc_alternate.NAME = $base64(' + quoted(step['object']) + ')',
                       'pclassdesc_alternate.PROPERTIES = eps', 'pclassdesc_alternate.METHODS = eps',
                       'pclassdesc_alternate.PARENT = eps',
                       '$typed_object_exact(' + state + ',[' + alternate + '],POBJECT ' + obj + ')',
                       '~$typed_object_exact(' + state + ',[' + nominal + '],POBJECT ' + obj + ')',
                       '$heap_owners($heap_graph(' + state + '),HOBJECT ' + obj + ') = 1']
    checks += seek('S_before', previous, -3)
    checks += ['S_before.STORE[n_field] = DEFINED (POBJECT n_live)',
               '$heap_owners($heap_graph(S_before),HCELL n_field) = 3',
               '$heap_owners($heap_graph(S_before),HOBJECT n_live) = 2']
    checks += seek('S_detached', 'S_before', line('$s341 = [];'))
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
               '$propref_at(S_detached.PROPREFS,n_field) = eps',
               'S_detached.STORE[n_field] = DEFINED (POBJECT n_live)',
               '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2']
    checks += seek('S_free', 'S_detached', line('$r341 = false;'))
    checks += ['S_free.STORE[n_field] = DEFINED (PARRAY n_free)', 'S_free.ARRAYS[n_free].ITEMS = eps',
               '(HARRAY n_free) <- $pools_nodes(S_free.POOLS)',
               '$heap_owners($heap_graph(S_free),HARRAY n_free) = $(1 + $heap_count(HARRAY n_free,$pools_nodes(S_free.POOLS)))',
               '$propref_at(S_free.PROPREFS,n_field) = eps',
               'S_end = $drive_steps(S_free,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
               '$lbr_output(S_end.EVENTS) = $base64(' + quoted(case['stdout']) + ')',
               'S_end.POOLS = S_free.POOLS', '(HARRAY n_free) <- S_end.ALLOCATIONS',
               '$heap_owners($heap_graph(S_end),HARRAY n_free) = $heap_count(HARRAY n_free,$pools_nodes(S_end.POOLS))']
    checks += ['~((HOBJECT ' + obj + ') <- S_end.ALLOCATIONS)' for obj in ('n_root', 'n_first', 'n_live')]
    checks += ['~((HOBJECT ' + obj + ') <- S_end.ALLOCATIONS)' for obj in step_objects]
    checks += ['~((HCELL ' + cell + ') <- S_end.ALLOCATIONS)' for cell in ('n_rootcell', 'n_field', 'n_copycell', 'n_keptcell')]
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


def main(stem='self_parentless_short_reference_get_hook'):
    runner.PREFIX = runner.PREFIX.replace('box320', 'box341').replace('a320', 'r341').replace('b320', 's341')
    runner.PREFIX = runner.PREFIX.replace('$property_hook_plan(S) =/= eps', '$property_hook_ref_plan(S) =/= eps')
    runner.PREFIX = runner.PREFIX.replace('(PROPERTY_HOOK_RESULT ppropertyhook)', '(PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch")')
    runner.STEM = stem
    runner.fields = fields
    runner.main(extra_paths=[Path(__file__), Path(names.__file__)])


if __name__ == '__main__':
    main()
