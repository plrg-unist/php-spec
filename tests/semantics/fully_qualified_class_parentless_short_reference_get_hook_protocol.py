#!/usr/bin/env python3
"""Check authentic FQ class headers, object aliases, failed writes and detach."""
from pathlib import Path
import fully_qualified_class_parentless_short_reference_get_hook_review_protocol as headers
import builtin_union_parentless_short_reference_get_hook_protocol as prior
import parentless_short_reference_get_hook_review_protocol as peer

PREFIX = prior.PREFIX


def mask(name, nullable=False):
    return '[(PTBRANCH ([PTCLASS ($base64(' + peer.quoted(name) + '))]))' + (',(PTBRANCH ([PTBUILTIN "null"]))]' if nullable else ']')


def raw(name, nullable=False):
    value = 'NNameFullyQualified (BYTES ' + peer.quoted(name) + ') eps'
    return 'NNullableType (' + value + ') eps' if nullable else value


def fields(fixture, source, case):
    strict = case['strict']; nullable = case['nullable']; name = case['class_name']
    suffix = '322' if strict else '320'; root = 'box' + suffix
    a = 'r322' if strict else 'a320'; b = 's322' if strict else 'b320'
    first = 'first322' if strict else 'initial320'; copy = 'copy' + suffix; kept = 'kept' + suffix
    copied_tag, second_tag, free = (107, 113, 211) if strict else (67, 71, 149)
    lines = [line.strip() for line in source.read_text().splitlines()]
    line = lambda statement: lines.index(statement) + 1
    first_line = line('$' + first + ' = $' + root + '->v;')
    copy_line = line('$' + copy + ' = $' + root + '->v;')
    get_line = next(i + 1 for i, text in enumerate(lines) if '&get =>' in text)
    body_line = get_line + 1
    tries = [text for text in lines if text.startswith('try {')]
    retarget_line = next(i + 1 for i, text in enumerate(lines) if text.startswith('$' + b + ' = new '))
    free_line = next(i + 1 for i, text in enumerate(lines) if text == '$' + (b if strict else a) + ' = ' + str(free) + ';')
    array_line = line('$' + a + ' = [];')
    prior.PREFIX = PREFIX.replace('box320', root)
    branches = mask(name, nullable); wrong = mask(name.swapcase(), nullable)
    def seek(state, previous, z):
        return [state + ' = $lbr_seek(' + previous + ',' + str(z) + ',30000)', '$lbr_phase(' + state + ',' + str(z) + ')', state + '.COMPLETION = NORMAL']
    def target(state, obj, label, tag):
        rows = ['$objectprops_at(' + state + '.OBJECTPROPS,' + obj + ') = ([ppropertyslot_' + label + '])',
                'ppropertyslot_' + label + '.NAME = $ptascii("tag")',
                'ppropertyslot_' + label + '.STATE = PROP_VALUE (DIRECT (PINT ' + str(tag) + '))',
                '$typed_object_exact(' + state + ',' + branches + ',POBJECT ' + obj + ')']
        if name.lower() == 'stdclass':
            rows += [state + '.OBJECTS[' + obj + '] = STDINSTANCE']
        else:
            rows += [state + '.OBJECTS[' + obj + '] = INSTANCE porigin_' + label,
                     '$class_at(' + state + '.CLASSES,porigin_' + label + ') = (pclassdesc_' + label + ')',
                     'pclassdesc_' + label + '.PARENT = eps', 'pclassdesc_' + label + '.METHODS = eps',
                     '$ptlc(pclassdesc_' + label + '.NAME) = $ptlc($base64(' + peer.quoted(name) + '))']
        return rows
    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + peer.quoted(str(source)) + ')']
    checks += seek('S_begin', 'S_start', first_line)
    checks += seek('S_front', 'S_begin', 0)
    checks += ['$property_hook_plan(S_front) = (ppropertyhook)', '$lookup(S_front.ENV,$ptascii("' + root + '")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc)',
        'pclassdesc.KIND = "class"', 'pclassdesc.PARENT = eps', '$trait_plan(S_front,pclassdesc).TRAITS = eps',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.NAME = $ptascii("v")', 'ppropertydesc.KEY = ppropertydesc.NAME',
        'ppropertydesc.TYPE = ' + branches, '$property_hook_reference_decl(S_front,ppropertydesc)',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property', 'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = ' + ('NNullableType (' if nullable else '') + 'NNameFullyQualified (BYTES text_type) metadata_type' + (') metadata_nullable' if nullable else ''),
        '$base64(text_type) = $base64(' + peer.quoted(name) + ')', '$hook_short_reference_header(phpType18,ppropertydesc.TYPE)',
        '~$hook_short_reference_header(phpType18,' + wrong + ')', '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + wrong + '])',
        '$pttypename(ppropertydesc.TYPE) = $base64(' + peer.quoted(case['typename']) + ')',
        'phpType5 = ' + ('NExprConstFetch (NName (BYTES text_default) metadata_default_name) metadata_default' if nullable else 'ABSENT'),
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)', '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        ('pfunction.CODE.STRICT' if strict else '~pfunction.CODE.STRICT'), 'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]', 'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (' + ('NScalarString' if case['body'] == 'literal' else 'NIdentifier') + ' (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = ' + str(get_line), '$source_line(metadata_expression) = ' + str(body_line),
        '$origin_node(S_front.SOURCES,PORIGIN n_source pfunction.BODY) = (expression_get)',
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((' + str(body_line) + ',false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (' + str(body_line) + ')',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_front])', 'ppropertyslot_front.STATE = PROP_VALUE pitem_front']
    if nullable:
        checks += ['$base64(text_default) = $ptascii("null")', '$entry_value(S_front,pitem_front) = PNULL']
    else:
        checks += ['$entry_value(S_front,pitem_front) = POBJECT n_initial', '$typed_object_exact(S_front,ppropertydesc.TYPE,POBJECT n_initial)']
    checks += seek('S_return', 'S_front', -1)
    z = str(body_line)
    checks += ['$reference_return_source(S_return,' + z + ')', '$reference_return_fetch_valid(S_return,' + z + ')', '$reference_verifies(S_return)',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + wrong + ']) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,' + z + ')', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH ' + z + ')',
        'S_noarrow = S_return[.FUNCTIONS = (pfunction[.CODE.EXPRESSIONS = $lbr_noarrow(pfunction.CODE.EXPRESSIONS,pfunction.BODY)]) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_noarrow,' + z + ')', '$property_current_line(S_noarrow) = 0',
        '$source_unit(S_return.SOURCES,n_source) = (pcunit)',
        'statement_badraw = NStmtProperty (SEQUENCE eps) (INTEGER 1) (' + raw(name.swapcase(), nullable) + ') (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group',
        'S_badraw = S_return[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_badraw) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_reference_decl(S_badraw,ppropertydesc)', '~$reference_return_source(S_badraw,' + z + ')']
    checks += seek('S_fetch', 'S_return', -2)
    checks += ['S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
               'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]', '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    checks += seek('S_aliases', 'S_fetch', copy_line)
    checks += ['$lookup(S_aliases.ENV,$ptascii("' + a + '")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("' + b + '")) = (n_field)',
        'S_aliases.STORE[n_field] = DEFINED (POBJECT n_first)', '$propref_at(S_aliases.PROPREFS,n_field) = (ppropref)',
        '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3', '$heap_owners($heap_graph(S_aliases),HOBJECT n_first) = 1',
        'S_missing = S_aliases[.PROPREFS = eps]', '~$property_state_valid(S_missing)']
    checks += seek('S_copied', 'S_aliases', retarget_line)
    checks += ['$lookup(S_copied.ENV,$ptascii("' + copy + '")) = (n_copycell)', 'n_copycell =/= n_field',
        'S_copied.STORE[n_copycell] = DEFINED (POBJECT n_first)', '$propref_at(S_copied.PROPREFS,n_copycell) = eps',
        '$heap_owners($heap_graph(S_copied),HOBJECT n_first) = 2', '$heap_owners($heap_graph(S_copied),HCELL n_field) = 3']
    checks += target('S_copied', 'n_first', 'copied', copied_tag)
    checks += seek('S_retarget', 'S_copied', line(tries[0]))
    checks += ['S_retarget.STORE[n_field] = DEFINED (POBJECT n_second)', 'n_second =/= n_first',
        '$heap_owners($heap_graph(S_retarget),HOBJECT n_first) = 1', '$heap_owners($heap_graph(S_retarget),HOBJECT n_second) = 1',
        'n_wrong = |S_retarget.OBJECTS|']
    checks += target('S_retarget', 'n_second', 'second', second_tag)
    states = ['S_front', 'S_return', 'S_fetch', 'S_aliases', 'S_copied', 'S_retarget']; previous = 'S_retarget'
    last_marker = '$' + (b if strict else a) + ' = null;' if nullable else '$' + kept + ' = $' + a + ';'
    for i in range(len(tries)):
        state = 'S_rejected_' + str(i); marker = tries[i + 1] if i + 1 < len(tries) else last_marker
        checks += seek(state, previous, line(marker))
        checks += [state + '.STORE[n_field] = DEFINED (POBJECT n_second)', '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3', '$heap_owners($heap_graph(' + state + '),HOBJECT n_second) = 1',
                   '~((HOBJECT n_wrong) <- ' + state + '.ALLOCATIONS)']
        if i == 0:
            if case['wrong_class'].lower() == 'stdclass':
                checks += [state + '.OBJECTS[n_wrong] = STDINSTANCE']
            else:
                checks += [state + '.OBJECTS[n_wrong] = INSTANCE porigin_wrong',
                           '$class_at(' + state + '.CLASSES,porigin_wrong) = (pclassdesc_wrong)',
                           '$ptlc(pclassdesc_wrong.NAME) = $ptlc($base64(' + peer.quoted(case['wrong_class']) + '))']
        states.append(state); previous = state
    if nullable:
        restore_line = next(i + 1 for i, text in enumerate(lines) if text.startswith('$' + root + '->v = new '))
        checks += seek('S_null', previous, restore_line)
        checks += ['S_null.STORE[n_field] = DEFINED PNULL', '$propref_at(S_null.PROPREFS,n_field) = (ppropref)',
                   '~((HOBJECT n_second) <- S_null.ALLOCATIONS)', '$heap_owners($heap_graph(S_null),HCELL n_field) = 3']
        states.append('S_null'); previous = 'S_null'
    checks += seek('S_before', previous, -3)
    checks += ['S_before.STORE[n_field] = DEFINED (POBJECT n_live)', 'n_live =/= n_first',
        '$lookup(S_before.ENV,$ptascii("' + kept + '")) = (n_keptcell)', 'S_before.STORE[n_keptcell] = DEFINED (POBJECT n_live)',
        '$heap_owners($heap_graph(S_before),HOBJECT n_live) = 2', '$heap_owners($heap_graph(S_before),HOBJECT n_first) = 1',
        '$heap_owners($heap_graph(S_before),HCELL n_field) = 3', '$propref_at(S_before.PROPREFS,n_field) = (ppropref)']
    checks += target('S_before', 'n_live', 'live', case['final_tag'])
    checks += seek('S_detached', 'S_before', free_line)
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
               'S_detached.STORE[n_field] = DEFINED (POBJECT n_live)', '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2']
    checks += seek('S_written', 'S_detached', array_line)
    checks += ['S_written.STORE[n_field] = DEFINED (PINT ' + str(free) + ')', '$heap_owners($heap_graph(S_written),HOBJECT n_live) = 1']
    checks += seek('S_pooled', 'S_written', line('$' + copy + ' = false;'))
    checks += ['S_pooled.STORE[n_field] = DEFINED (PARRAY n_free)', '(HARRAY n_free) <- $pools_nodes(S_pooled.POOLS)', 'S_pooled.ARRAYS[n_free].ITEMS = eps',
        '$heap_owners($heap_graph(S_pooled),HARRAY n_free) = $(1 + $heap_count(HARRAY n_free,$pools_nodes(S_pooled.POOLS)))',
        'S_end = $drive_steps(S_pooled,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $base64(' + peer.quoted(case['stdout']) + ')', 'S_end.POOLS = S_pooled.POOLS',
        '(HARRAY n_free) <- S_end.ALLOCATIONS', '$heap_owners($heap_graph(S_end),HARRAY n_free) = $heap_count(HARRAY n_free,$pools_nodes(S_end.POOLS))',
        '~((HOBJECT n_first) <- S_end.ALLOCATIONS)', '~((HOBJECT n_live) <- S_end.ALLOCATIONS)']
    checks += ['~((HCELL ' + cell + ') <- S_end.ALLOCATIONS)' for cell in ('n_rootcell', 'n_field', 'n_copycell', 'n_keptcell')]
    for state in states + ['S_before', 'S_detached', 'S_written', 'S_pooled', 'S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')', '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)', f'S_{label}_one = $drive_steps({state},1)',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


if __name__ == '__main__':
    prior.STEM = 'fully_qualified_class_parentless_short_reference_get_hook'
    prior.fields = fields
    prior.header_fields = lambda: [row['premise'] for row in headers.assertions()]
    prior.main(header_report={'fully_qualified_class_header_assertions': len(headers.assertions())},
               extra_paths=[Path(headers.__file__)])
