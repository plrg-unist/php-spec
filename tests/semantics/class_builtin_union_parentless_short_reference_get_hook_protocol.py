#!/usr/bin/env python3
"""Check multi-builtin class headers, reached coercion ranks and real owners."""
from pathlib import Path

import scoped_class_parentless_short_reference_get_hook_review_state as prior

runner, quoted = prior.runner, prior.quoted


def branches(case, name=None):
    name = case['class_name'] if name is None else name
    return '[' + ','.join(
        '(PTBRANCH ([PTCLASS ($base64(' + quoted(name) + '))]))' if member == 'class'
        else '(PTBRANCH ([PTBUILTIN "' + member + '"]))'
        for member in case['members']) + ']'


def fields(fixture, source, case):
    lines = [line.strip() for line in source.read_text().splitlines()]
    line = lambda statement: lines.index(statement) + 1
    get_line = next(i + 1 for i, text in enumerate(lines) if '&get =>' in text)
    body_line = get_line if '$this' in lines[get_line - 1] else get_line + 1
    z = str(body_line)
    mask, wrong = branches(case), branches(case, case['class_name'].swapcase())
    nodes = [case['raw_kind'] + ' (BYTES text_raw) metadata_raw' if member == 'class'
             else 'NIdentifier (BYTES text_' + member + ') metadata_' + member
             for member in case['members']]
    raw = 'NUnionType (SEQUENCE ([' + ','.join(nodes) + '])) metadata_union'
    states = []

    def seek(state, previous, target):
        states.append(state)
        return [f'{state} = $lbr_seek({previous},{target},30000)',
                f'$lbr_phase({state},{target})', f'{state}.COMPLETION = NORMAL']

    checks = ['U = ' + fixture, 'S_start = $php_run(U,0,' + quoted(str(source)) + ')']
    checks += seek('S_begin', 'S_start', line('$first322 = $box322->v;'))
    checks += seek('S_front', 'S_begin', 0)
    checks += [
        '$property_hook_plan(S_front) = (ppropertyhook)',
        '$lookup(S_front.ENV,$ptascii("box322")) = (n_rootcell)',
        'S_front.STORE[n_rootcell] = DEFINED (POBJECT n_root)',
        'ppropertyhook.OBJECT = n_root', 'S_front.OBJECTS[n_root] = INSTANCE porigin_root',
        '$class_at(S_front.CLASSES,porigin_root) = (pclassdesc)',
        'pclassdesc.ORIGIN = PORIGIN n_source pcpath_class',
        'pclassdesc.KIND = "class"', 'pclassdesc.PARENT = eps',
        '$trait_plan(S_front,pclassdesc).TRAITS = eps',
        'pclassdesc.PROPERTIES = [ppropertydesc]', 'ppropertydesc.TYPE = ' + mask,
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_front.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty (SEQUENCE eps) (INTEGER 1) phpType18 (SEQUENCE ([NPropertyItem phpType40 phpType5 metadata_item])) (SEQUENCE ([phpType38])) metadata_group)',
        'phpType18 = ' + raw,
        '$base64(text_raw) = $base64(' + quoted(case['raw_class_name']) + ')',
        'ppropertydesc.LINE = $nabs($source_line(metadata_group))',
        '$property_hook_pair_source_header(S_front,pclassdesc)',
        '$source_unit(S_front.SOURCES,n_source) = (pcunit)',
        'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        '$call_sourcefile(S_front.FILES,pclassdesc.ORIGIN) = $base64(' + quoted(str(source)) + ')',
        '$plclasscontext(pcunit,pcpath_class,$base64(' + quoted(str(source)) + '),pclassdesc.LINE) = (ptcontext_class)',
        'ptcontext_class.NAMESPACE = $base64(' + quoted(case['namespace']) + ')',
        'ptcontext_property = ptcontext_class[.SCOPE = PTKNOWN pclassdesc.NAME pclassdesc.PARENT][.POSITION = PTPROPERTY][.OWNER = pclassdesc.NAME][.MEMBER = ppropertydesc.NAME][.LINE = ppropertydesc.LINE]',
        '$ptype_normalize(phpType18,ptcontext_property) = PTOK ppropertydesc.TYPE eps',
        '$hook_short_reference_class_builtin_union_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~$hook_short_reference_header(phpType18,ppropertydesc.TYPE)',
        '~$hook_short_reference_scoped_header(phpType18,ppropertydesc.TYPE,ptcontext_property)',
        '~$hook_short_reference_class_builtin_union_header(phpType18,' + wrong + ',ptcontext_property)',
        '$property_hook_short_reference_header(S_front,pclassdesc,ppropertydesc,phpType18)',
        '$property_hook_reference_decl(S_front,ppropertydesc)',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.TYPE = ' + wrong + '])',
        '~$property_hook_reference_decl(S_front,ppropertydesc[.LINE = 0])',
        '~$property_hook_reference_decl(S_front[.FILES = eps],ppropertydesc)',
        '~$property_hook_reference_decl(S_front[.SOURCES = eps],ppropertydesc)',
        'S_badname = S_front[.CLASSES = (pclassdesc[.NAME = pclassdesc.NAME ++ [88]]) :: S_front.CLASSES]',
        '~$property_hook_reference_decl(S_badname,ppropertydesc)',
        '$pttypename(ppropertydesc.TYPE) = $base64(' + quoted(case['typename']) + ')',
        '$objectprops_at(S_front.OBJECTPROPS,n_root) = ([ppropertyslot_initial])',
        '$property_hook_origin(S_front,ppropertydesc) = (ppropertyhook.HOOK)',
        '$property_hook_function(S_front,ppropertyhook) = (pfunction)',
        'pfunction.SIGNATURE = {PARAMETERS eps, RETURNS ppropertydesc.TYPE, BYREF true}',
        '~pfunction.CODE.STRICT', 'pfunction.DEFAULTS = eps', '~pfunction.EARLY',
        'pfunction.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX 0,PCFIELD 5]',
        'pfunction.CODE.UNIT = n_source',
        'phpType38 = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN true) phpType11 (SEQUENCE eps) expression_get metadata_hook',
        '$hook_parameter_facts(metadata_hook) = [false]',
        'expression_get = NExprPropertyFetch (NExprVariable (BYTES text_this) metadata_this) (NIdentifier (BYTES text_field) metadata_field) metadata_expression',
        '$base64(text_this) = $ptascii("this")', '$base64(text_field) = $ptascii("v")',
        '$source_line(metadata_hook) = ' + str(get_line),
        '$source_line(metadata_expression) = ' + z,
        '$code_expression(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = ((' + z + ',false))',
        '$arrow_line(pfunction.CODE.EXPRESSIONS,pfunction.BODY) = (' + z + ')',
    ]
    checks += ['$ptlc($base64(text_' + member + ')) = $ptascii("' + member + '")'
               for member in case['members'] if member != 'class']
    if case['default'] == '0':
        checks += ['phpType5 = NScalarInt (INTEGER 0) metadata_default',
                   'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PINT 0))']
    elif case['default'] == '[]':
        checks += ['phpType5 = NExprArray (SEQUENCE eps) metadata_default',
                   'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT (PARRAY n_initial))',
                   'S_front.ARRAYS[n_initial].ITEMS = eps']
    else:
        assert case['default'] == 'null'
        checks += ['phpType5 = NExprConstFetch (NName (BYTES text_default) metadata_default_name) metadata_default',
                   '$base64(text_default) = $ptascii("null")',
                   'ppropertyslot_initial.STATE = PROP_VALUE (DIRECT PNULL)']
    checks += seek('S_return', 'S_front', -1)
    checks += ['$reference_return_source(S_return,' + z + ')',
               '$reference_return_fetch_valid(S_return,' + z + ')', '$reference_verifies(S_return)',
               'S_wrongreturn = S_return[.FUNCTIONS = (pfunction[.SIGNATURE.RETURNS = ' + wrong + ']) :: S_return.FUNCTIONS]',
               '~$reference_return_source(S_wrongreturn,' + z + ')',
               '~$call_task_valid(S_wrongreturn,RETURN_REF_FETCH ' + z + ')']
    checks += seek('S_fetch', 'S_return', -2)
    checks += ['S_fetch.RESULT = REFERENCE n_field', '$propref_at(S_fetch.PROPREFS,n_field) = (ppropref)',
               'ppropref.SOURCES = [OBJECT_PROP_SOURCE n_root ($ptascii("v")) ppropertydesc.ORIGIN]',
               '$heap_owners($heap_graph(S_fetch),HCELL n_field) = 2']
    checks += seek('S_aliases', 'S_fetch', line('$copy322 = $box322->v;'))
    checks += ['$lookup(S_aliases.ENV,$ptascii("r322")) = (n_field)',
               '$lookup(S_aliases.ENV,$ptascii("s322")) = (n_field)',
               'S_aliases.STORE[n_field] = DEFINED (POBJECT n_first)',
               '$typed_object_exact(S_aliases,ppropertydesc.TYPE,POBJECT n_first)',
               '$heap_owners($heap_graph(S_aliases),HCELL n_field) = 3',
               '~$property_state_valid(S_aliases[.PROPREFS = eps])']
    previous = 'S_aliases'
    tries = [text for text in lines if text.startswith('try {')]
    if case['arity'] == 3:
        ranks = [("$s322 = '37.0';", 'PINT 37'), ('$r322 = true;', 'PFLOAT 4630404104378646528'),
                 ('$s322 = 37.0;', 'PINT 1'), (next(text for text in lines if text.startswith('$box322->v = new ')), 'PFLOAT 4630404104378646528')]
        first_rank = "$r322 = '37';"
    elif case['arity'] == 5:
        ranks = [('unset($arraycopy322);', None), ('$s322 = true;', 'PNULL'), ('$r322 = 37;', 'PBOOL true'),
                 ("$s322 = '0';", 'PSTRING_CARRIER (REQUEST_STRING n_rank_string) ($ptascii("37"))'),
                 (next(text for text in lines if text.startswith('$box322->v = new ')), 'PSTRING_CARRIER INTERNED_STRING ($ptascii("0"))')]
        first_rank = '$s322 = [193];'
    else:
        assert case['arity'] == 7
        ranks = [('$s322 = true;', 'PBOOL false'), ("$r322 = '37.0';", 'PINT 1'),
                 ('$s322 = 37.0;', 'PSTRING_CARRIER INTERNED_STRING ($ptascii("37.0"))'),
                 ('$r322 = 37;', 'PFLOAT 4630404104378646528'), ('$s322 = [193];', 'PINT 37'),
                 ('$r322 = null;', None), (next(text for text in lines if text.startswith('$box322->v = new ')), 'PNULL')]
        first_rank = '$r322 = false;'
    for i, marker in enumerate(tries[1:] + [first_rank]):
        state = 'S_rejected' + str(i)
        checks += seek(state, previous, line(marker))
        checks += [state + '.STORE[n_field] = DEFINED (POBJECT n_second)',
                   '$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3']
        previous = state
    for i, (marker, value) in enumerate(ranks):
        state = 'S_rank' + str(i)
        checks += seek(state, previous, line(marker))
        if value is not None:
            checks += [state + '.STORE[n_field] = DEFINED (' + value + ')']
            if 'n_rank_string' in value:
                checks += [state + '.STRINGDATA[n_rank_string] = $ptascii("37")',
                           '$string_carrier_valid(' + state + ',' + value + ')']
        else:
            checks += [state + '.STORE[n_field] = DEFINED (PARRAY n_fieldarray)',
                       state + '.ARRAYS[n_fieldarray].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 193))]']
            if case['arity'] == 5:
                checks += ['$lookup(' + state + '.ENV,$ptascii("arraycopy322")) = (n_copyarraycell)',
                           state + '.STORE[n_copyarraycell] = DEFINED (PARRAY n_copyarray)',
                           'n_copyarray =/= n_fieldarray',
                           state + '.ARRAYS[n_copyarray].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 197))]',
                           '$propref_at(' + state + '.PROPREFS,n_copyarraycell) = eps']
        checks += ['$propref_at(' + state + '.PROPREFS,n_field) = (ppropref)',
                   '$heap_owners($heap_graph(' + state + '),HCELL n_field) = 3']
        previous = state
    checks += seek('S_before', previous, -3)
    checks += ['S_before.STORE[n_field] = DEFINED (POBJECT n_live)',
               '$lookup(S_before.ENV,$ptascii("kept322")) = (n_keptcell)',
               'S_before.STORE[n_keptcell] = DEFINED (POBJECT n_live)',
               '$lookup(S_before.ENV,$ptascii("copy322")) = (n_copycell)',
               'S_before.STORE[n_copycell] = DEFINED (POBJECT n_first)',
               'n_copycell =/= n_field', '$propref_at(S_before.PROPREFS,n_copycell) = eps',
               '$heap_owners($heap_graph(S_before),HOBJECT n_live) = 2',
               '$heap_owners($heap_graph(S_before),HOBJECT n_first) = 1',
               '$heap_owners($heap_graph(S_before),HCELL n_field) = 3']
    checks += seek('S_detached', 'S_before', lines.index('unset($box322);') + 2)
    checks += ['~((HOBJECT n_root) <- S_detached.ALLOCATIONS)',
               '$propref_at(S_detached.PROPREFS,n_field) = eps',
               'S_detached.STORE[n_field] = DEFINED (POBJECT n_live)',
               '$heap_owners($heap_graph(S_detached),HCELL n_field) = 2']
    checks += seek('S_free', 'S_detached', line('$r322 = 0;'))
    if case['arity'] == 3:
        checks += ['S_free.STORE[n_field] = DEFINED (PARRAY n_free)', 'S_free.ARRAYS[n_free].ITEMS = eps']
    elif case['arity'] == 5:
        checks += ['S_free.STORE[n_field] = DEFINED (POBJECT n_free)', 'S_free.OBJECTS[n_free] = STDINSTANCE']
    else:
        checks += ['S_free.STORE[n_field] = DEFINED (PBOOL true)']
    checks += ['S_end = $drive_steps(S_free,30000)', 'S_end.COMPLETION = NORMAL', 'S_end.TODO = eps',
               '$lbr_output(S_end.EVENTS) = $base64(' + quoted(case['stdout']) + ')',
               '~((HOBJECT n_first) <- S_end.ALLOCATIONS)', '~((HOBJECT n_live) <- S_end.ALLOCATIONS)']
    checks += ['~((HCELL ' + cell + ') <- S_end.ALLOCATIONS)' for cell in ('n_rootcell', 'n_field', 'n_copycell', 'n_keptcell')]
    for state in states + ['S_end']:
        checks += ['$property_state_valid(' + state + ')', '$call_descriptors_valid(' + state + ')',
                   '$heap_valid($heap_prune($heap_graph(' + state + ')))']
    for label, state in (('return', 'S_return'), ('cleanup', 'S_before')):
        checks += [f'S_{label}_zero = $drive_steps({state},0)', f'S_{label}_zero = {state}[.COMPLETION = BUDGET]',
                   f'S_{label}_one = $drive_steps(S_{label}_zero[.COMPLETION = NORMAL],1)',
                   f'S_{label}_one = $drive_steps({state},1)',
                   f'$drive_steps(S_{label}_one[.COMPLETION = NORMAL],30000) = S_end']
    return checks


if __name__ == '__main__':
    runner.PREFIX = runner.PREFIX.replace('box320', 'box322').replace(
        'def $lbr_phase(S,z) = false -- otherwise', r'''def $lbr_phase(S,z) = true
  -- if $(z > 0)
  -- if S.TODO = (UNSET (NExprVariable (BYTES text_name) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("arraycopy322")
  -- if $source_line(metadata) = z
def $lbr_phase(S,z) = false -- otherwise''')
    runner.STEM = 'class_builtin_union_parentless_short_reference_get_hook'
    runner.fields = fields
    runner.main(extra_paths=[Path(prior.__file__), Path(prior.headers.__file__)])
