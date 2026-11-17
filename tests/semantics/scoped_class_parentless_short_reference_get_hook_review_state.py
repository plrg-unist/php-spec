#!/usr/bin/env python3
"""Independent scoped-source authority, real references and retirement checks."""
from pathlib import Path
import builtin_union_parentless_short_reference_get_hook_protocol as runner
import scoped_class_parentless_short_reference_get_hook_review_protocol as headers


def quoted(text):
    return headers.quoted(text.encode())


def fields(fixture, source, case):
    assert case['strict']
    runner.PREFIX = runner.PREFIX.replace('box320', 'box322')
    lines = [line.strip() for line in source.read_text().splitlines()]
    line = lambda statement: lines.index(statement) + 1
    body_line = next(i + 2 for i, text in enumerate(lines) if '&get =>' in text)
    property_line = next(i + 1 for i, text in enumerate(lines) if text.startswith('public ') and '$v' in text)
    token = '(MstartLine (' + str(property_line) + '))'
    assert token in fixture
    negative_fixture = fixture.replace(token, '(MstartLine (-' + str(property_line) + '))')
    z = str(body_line)
    branches = headers.mask(case['class_name'].encode(), case['nullable'])
    wrong = headers.mask(case['class_name'].swapcase().encode(), case['nullable'])
    def seek(state, previous, target):
        return [state + ' = $lbr_seek(' + previous + ',' + str(target) + ',30000)',
                '$lbr_phase(' + state + ',' + str(target) + ')', state + '.COMPLETION = NORMAL']
    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')']
    checks += seek('S_begin', 'S_start', line('$first322 = $box322->v;'))
    checks += seek('S_front', 'S_begin', 0)
    checks += ['$property_hook_plan(S_front) = (ppropertyhook)',
        '$lookup(S_front.ENV,$ptascii("box322")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)', 'ppropertyhook.OBJECT = n_root',
        'S_front.OBJECTS[n_root] = INSTANCE porigin_root', '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN n_source pcpath_class', 'pclassdesc.KIND = "class"', 'pclassdesc.PARENT = eps',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + branches,
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = ' + ('NNullableType (' if case['nullable'] else '') + case['raw_kind'] + ' (BYTES text_raw) metadata_raw' + (') metadata_nullable' if case['nullable'] else ''),
        '$base64(text_raw) = $base64(' + quoted(case['raw_class_name']) + ')',
        'ppropertydesc.LINE = $nabs($source_line(metadata_group))',
        '$property_hook_pair_source_header(S_front,pclassdesc)', '$source_unit(S_front.SOURCES,n_source) = (pcunit)',
        'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$call_sourcefile(S_front.FILES,pclassdesc.ORIGIN) = $base64(' + quoted(str(source)) + ')',
        '$plclasscontext(pcunit,pcpath_class,$base64(' + quoted(str(source)) + '),pclassdesc.LINE) = (ptcontext_class)',
        'ptcontext_class.NAMESPACE = $base64(' + quoted(case['namespace']) + ')',
        'ptcontext_property = ptcontext_class[.SCOPE = PTKNOWN pclassdesc.NAME pclassdesc.PARENT][.POSITION = PTPROPERTY][.OWNER = pclassdesc.NAME][.MEMBER = ppropertydesc.NAME][.LINE = ppropertydesc.LINE]',
        'ptcontext_consumer = ptcontext_property[.NAMESPACE = $base64(' + quoted(case['consumer_namespace']) + ')][.IMPORTS = eps]',
        'ptcontext_consumer.NAMESPACE =/= ptcontext_class.NAMESPACE',
        '~$hook_short_reference_scoped_header(phpType18,ppropertydesc.TYPE,ptcontext_consumer)',
        '$hook_short_reference_scoped_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~$hook_short_reference_header(phpType18,ppropertydesc.TYPE)',
        '$property_hook_short_reference_header(S_front,pclassdesc,ppropertydesc,phpType18)',
        '$property_hook_reference_decl(S_front,ppropertydesc)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + wrong + '])',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.LINE = 0])',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.LINE = $nabs($(ppropertydesc.LINE + 1))])',
        'S_consumer = S_front[.ENV = eps]',
        '$property_hook_reference_decl(S_consumer,ppropertydesc)',
        'S_badname = S_front[.CLASSES = (pclassdesc[.NAME = pclassdesc.NAME ++ [88]]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_badname,ppropertydesc)',
        'S_badline = S_front[.CLASSES = (pclassdesc[.LINE = $nabs($(pclassdesc.LINE + 1))]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_badline,ppropertydesc)',
        '~$property_hook_reference_decl(S_front[.FILES = eps],ppropertydesc)',
        '~$property_hook_reference_decl(S_front[.SOURCES = eps],ppropertydesc)',
        '$origin_node(S_front.SOURCES,pclassdesc.ORIGIN) = (pcnode_class)',
        'S_noncanonical = S_front[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_class pcnode_class) :: pcunit.OCCURRENCES]]]',
        '$origin_node(S_noncanonical.SOURCES,pclassdesc.ORIGIN) = (pcnode_class)',
        '$origin_node(S_noncanonical.SOURCES,PORIGIN n_source pcpath_group) = $origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group)',
        '~$property_hook_reference_decl(S_noncanonical,ppropertydesc)',
        'U_negative = ' + negative_fixture,
        'pcunit_negative = $pcsource(n_source,U_negative)',
        'S_negative = S_front[.SOURCES = [pcunit_negative]]',
        '$origin_node(S_negative.SOURCES,PORIGIN n_source pcpath_group) = (pcnode_negative)',
        '(MstartLine (-' + str(property_line) + ')) <- $pcmetadata(pcnode_negative)',
        '$source_line($pcmetadata(pcnode_negative)) = 0',
        'ppropertydesc.LINE = $nabs(-' + str(property_line) + ')',
        '$property_hook_pair_source_header(S_negative,pclassdesc)',
        '~$property_hook_short_reference_header(S_negative,pclassdesc,ppropertydesc,phpType18)',
        '~$property_hook_reference_decl(S_negative,ppropertydesc)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        'pfunction.CODE.STRICT', 'pfunction.ENV.NAMESPACE = ptcontext_class.NAMESPACE',
        'S_functionenv = S_front[.FUNCTIONS = (pfunction[.ENV = pfunction.ENV[.NAMESPACE = $base64(' + quoted(case['consumer_namespace']) + ')][.CLASSES = eps]]) :: S_front.FUNCTIONS]',
        '$property_hook_reference_decl(S_functionenv,ppropertydesc)']
    checks += seek('S_return', 'S_front', -1)
    checks += ['$reference_return_source(S_return,' + z + ')', '$reference_return_fetch_valid(S_return,' + z + ')',
        '$reference_verifies(S_return)',
        'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + wrong + ']) :: S_return.FUNCTIONS]',
        '~$reference_return_source(S_wrongreturn,' + z + ')', '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH ' + z + ')',
        '~$reference_return_source(S_return[.FILES = eps],' + z + ')']
    checks += seek('S_fetch', 'S_return', -2)
    checks += ['S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
        'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
        '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    checks += seek('S_aliases', 'S_fetch', line('$copy322 = $box322->v;'))
    checks += ['$lookup(S_aliases.ENV,$ptascii("r322")) = (n_field)', '$lookup(S_aliases.ENV,$ptascii("s322")) = (n_field)',
        'S_aliases.STORE[n_field] = DEFINED (POBJECT n_first)', '$typed_object_exact(S_aliases,ppropertydesc.TYPE,POBJECT n_first)',
        '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
        '~$property_state_valid(S_aliases[.PROPREFS = eps])']
    checks += seek('S_detached', 'S_aliases', line('$s322 = 211;'))
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)', '$propref_at(S_detached.PROPREFS,n_field) = eps',
        'S_detached.STORE[n_field] = DEFINED (POBJECT n_live)', '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2',
        'S_end = $drive_steps(S_detached,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
        '$lbr_output(S_end.EVENTS) = $base64(' + quoted(case['stdout']) + ')',
        '~((HOBJECT n_first) <- S_end.ALLOCATIONS)', '~((HOBJECT n_live) <- S_end.ALLOCATIONS)',
        '~((HCELL n_rootcell) <- S_end.ALLOCATIONS)', '~((HCELL n_field) <- S_end.ALLOCATIONS)']
    for state in ('S_front', 'S_return', 'S_fetch', 'S_aliases', 'S_detached', 'S_end'):
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')', '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('detach', 'S_detached')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
            f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)', f'S_{label}_one = $drive_steps({state},1)',
            f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


if __name__ == '__main__':
    runner.STEM = 'scoped_class_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.header_fields = lambda: [row['premise'] for row in headers.assertions()]
    runner.main(header_report={'independent_scoped_header_assertions': len(headers.assertions())}, extra_paths=[Path(headers.__file__)])
