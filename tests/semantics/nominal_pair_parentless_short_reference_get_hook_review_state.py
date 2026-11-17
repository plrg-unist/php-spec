#!/usr/bin/env python3
"""Independent strict nominal-arm identities, atomic refusals and owner detach."""
from pathlib import Path

import builtin_union_parentless_short_reference_get_hook_protocol as runner
import nominal_pair_parentless_short_reference_get_hook_review_protocol as headers


def quoted(text):
    return headers.names.quoted(text.encode())


def fields(fixture, source, case):
    assert case['strict'] and case['body'] == 'literal'
    lines = [line.strip() for line in source.read_text().splitlines()]
    line = lambda statement: lines.index(statement) + 1
    get_line = next(i + 1 for i, text in enumerate(lines) if '&get =>' in text)
    body_line = get_line + 1
    branches = headers.branches(*(name.encode() for name in case['class_names']))
    reversed_branches = headers.branches(*(name.encode() for name in reversed(case['class_names'])))
    raw = 'NUnionType (SEQUENCE ([' + ','.join(
        kind + ' (BYTES text_type_' + str(i) + ') metadata_type_' + str(i)
        for i, kind in enumerate(case['raw_kinds'])) + '])) metadata_union'
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
                'ppropertyslot_' + label + '.STATE = PROP_VALUE (DIRECT (PINT ' + str(tag) + '))']

    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')']
    checks += seek('S_seed', 'S_start', line('$box333->v = $seed333;'))
    checks += seek('S_begin', 'S_seed', line('$first333 = $box333->v;'))
    checks += seek('S_front', 'S_begin', 0)
    checks += [
        '$property_hook_plan(S_front) = (ppropertyhook)',
        '$lookup(S_front.ENV,$ptascii("box333")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN n_source pcpath_class',
        'pclassdesc.KIND = "class"', 'pclassdesc.PARENT = eps',
        '$trait_plan(S_front,pclassdesc).TRAITS = eps',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + branches,
        'ppropertydesc.DEFAULT = PROP_UNINITIALIZED',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 ABSENT metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = ' + raw,
        'ppropertydesc.LINE = $nabs($source_line(metadata_group))',
        '$property_hook_pair_source_header(S_front,pclassdesc)',
        '$source_unit(S_front.SOURCES,n_source) = (pcunit)',
        'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$call_sourcefile(S_front.FILES,pclassdesc.ORIGIN) = $base64(' + quoted(str(source)) + ')',
        '$plclasscontext(pcunit,pcpath_class,$base64(' + quoted(str(source)) + '),pclassdesc.LINE) = (ptcontext_class)',
        'ptcontext_class.NAMESPACE = $base64(' + quoted(case['namespace']) + ')',
        'ptcontext_property = ptcontext_class[.SCOPE = PTKNOWN pclassdesc.NAME pclassdesc.PARENT][.POSITION = PTPROPERTY][.OWNER = pclassdesc.NAME][.MEMBER = ppropertydesc.NAME][.LINE = ppropertydesc.LINE]',
        '$ptype_normalize(phpType18,ptcontext_property) = PTOK ppropertydesc.TYPE eps',
        headers.HELPER + '(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~' + headers.HELPER + '(phpType18,' + reversed_branches + ',ptcontext_property)',
        '~$hook_short_reference_class_builtin_union_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '$property_hook_short_reference_header(S_front,pclassdesc,ppropertydesc,phpType18)',
        '$property_hook_reference_decl(S_front,ppropertydesc)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + reversed_branches + '])',
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
        'pfunction.CODE.STRICT', 'pfunction.ENV.NAMESPACE = ptcontext_class.NAMESPACE',
        'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]',
        'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NScalarString (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = ' + str(get_line),
        '$source_line(metadata_expression) = ' + str(body_line),
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((' + str(body_line) + ',false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (' + str(body_line) + ')',
    ]
    checks += ['$base64(text_type_' + str(i) + ') = $base64(' + quoted(name) + ')'
               for i, name in enumerate(case['raw_names'])]
    if case['raw_kinds'] != ['NNameFullyQualified', 'NNameFullyQualified']:
        checks += ['ptcontext_consumer = ptcontext_property[.NAMESPACE = $base64(' + quoted(case['consumer_namespace']) + ')][.IMPORTS = eps]',
                   '~' + headers.HELPER + '(phpType18,ppropertydesc.TYPE,ptcontext_consumer)']
    checks += payload('S_front', 'n_first', 'initial', case['first_object'], 97)
    checks += ['$typed_object_exact(S_front,' + branches + ',POBJECT n_first)',
               '~$typed_object_exact(S_front,' + headers.branches(case['second_object'].encode()) + ',POBJECT n_first)']
    checks += seek('S_return', 'S_front', -1)
    checks += ['$reference_return_source(S_return,' + str(body_line) + ')',
               '$reference_return_fetch_valid(S_return,' + str(body_line) + ')', '$reference_verifies(S_return)',
               'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + reversed_branches + ']) :: S_return.FUNCTIONS]',
               '~$reference_return_source(S_wrongreturn,' + str(body_line) + ')',
               '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH ' + str(body_line) + ')']
    checks += seek('S_fetch', 'S_return', -2)
    checks += ['S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
               'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
               '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    checks += seek('S_aliases', 'S_fetch', line('$copy333 = $box333->v;'))
    checks += ['$lookup(S_aliases.ENV,$ptascii("r333")) = (n_field)',
               '$lookup(S_aliases.ENV,$ptascii("s333")) = (n_field)',
               'S_aliases.STORE[n_field] = DEFINED (POBJECT n_first)',
               '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
               '~$property_state_valid(S_aliases[.PROPREFS = eps])']
    checks += seek('S_copied', 'S_aliases', line('$s333 = new \\' + case['second_object'] + '();'))
    checks += ['$lookup(S_copied.ENV,$ptascii("copy333")) = (n_copycell)',
               'S_copied.STORE[n_copycell] = DEFINED (POBJECT n_first)', 'n_copycell =/= n_field',
               '$propref_at(S_copied.PROPREFS,n_copycell) = eps',
               '$heap_owners($heap_graph(S_copied),HOBJECT n_first) = 2']
    checks += payload('S_copied', 'n_first', 'copied', case['first_object'], 103)
    tries = [text for text in lines if text.startswith('try {')]
    checks += seek('S_retarget', 'S_copied', line(tries[0]))
    checks += ['S_retarget.STORE[n_field] = DEFINED (POBJECT n_second)', 'n_second =/= n_first',
               'n_wrong = |S_retarget.OBJECTS|', '$typed_object_exact(S_retarget,' + branches + ',POBJECT n_second)',
               '~$typed_object_exact(S_retarget,' + headers.branches(case['first_object'].encode()) + ',POBJECT n_second)',
               '$typed_conversion_at(S_retarget,ppropertydesc.TYPE,PBOOL true,true) = TYPEREJECT']
    checks += payload('S_retarget', 'n_second', 'second', case['second_object'], 107)
    previous = 'S_retarget'
    for i, marker in enumerate(tries[1:] + ['$box333->v = new \\' + case['first_object'] + '();']):
        state = 'S_rejected' + str(i)
        checks += seek(state, previous, line(marker))
        checks += [state + '.STORE[n_field] = DEFINED (POBJECT n_second)',
                   state + '.STORE[n_copycell] = DEFINED (POBJECT n_first)',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3',
                   '~((HOBJECT n_wrong) <- ' + state + '.ALLOCATIONS)']
        previous = state
    checks += seek('S_before', previous, -3)
    checks += ['S_before.STORE[n_field] = DEFINED (POBJECT n_live)', 'n_live =/= n_first',
               '$lookup(S_before.ENV,$ptascii("kept333")) = (n_keptcell)',
               'S_before.STORE[n_keptcell] = DEFINED (POBJECT n_live)',
               '$heap_owners($heap_graph(S_before),HCELL n_field) = 3',
               '$heap_owners($heap_graph(S_before),HOBJECT n_live) = 2',
               '$heap_owners($heap_graph(S_before),HOBJECT n_first) = 1',
               '~((HOBJECT n_second) <- S_before.ALLOCATIONS)']
    checks += payload('S_before', 'n_live', 'live', case['first_object'], 113)
    checks += seek('S_detached', 'S_before', line('$s333 = new \\' + case['third_object'] + '();'))
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
               '$propref_at(S_detached.PROPREFS,n_field) = eps',
               'S_detached.STORE[n_field] = DEFINED (POBJECT n_live)',
               '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2']
    checks += seek('S_free', 'S_detached', line('$r333 = [];'))
    checks += ['S_free.STORE[n_field] = DEFINED (POBJECT n_free)',
               '$propref_at(S_free.PROPREFS,n_field) = eps',
               '~$typed_object_exact(S_free,' + branches + ',POBJECT n_free)']
    checks += payload('S_free', 'n_free', 'free', case['third_object'], 151)
    checks += ['S_end = $drive_steps(S_free,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
               '$lbr_output(S_end.EVENTS) = $base64(' + quoted(case['stdout']) + ')']
    checks += ['~((HOBJECT ' + obj + ') <- S_end.ALLOCATIONS)'
               for obj in ('n_first', 'n_second', 'n_live', 'n_free')]
    checks += ['~((HCELL ' + cell + ') <- S_end.ALLOCATIONS)'
               for cell in ('n_rootcell', 'n_field', 'n_copycell', 'n_keptcell')]
    for state in states + ['S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)',
                   f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


if __name__ == '__main__':
    runner.PREFIX = runner.PREFIX.replace('box320', 'box333').replace('a320', 'r333').replace('b320', 's333')
    runner.STEM = 'nominal_pair_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(headers.__file__), Path(headers.names.__file__)])
