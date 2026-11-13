#!/usr/bin/env python3
"""Check direct untyped trait pairs, raw authority and shared outside cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_hook_pair_review_protocol as pair
peer = pair.peer
header = pair.header
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_trait_hook_pair_review')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = peer.quoted
PREFIX = pair.PREFIX + r'''
dec $tp280_receipt(pcodeexpr,pcpath) : bool
def $tp280_receipt(CODEEXPR pcpath z b,pcpath) = true
def $tp280_receipt(pcodeexpr,pcpath) = false -- otherwise
dec $tp280_without_receipt(pcodeexpr*,pcpath) : pcodeexpr*
def $tp280_without_receipt(eps,pcpath) = eps
def $tp280_without_receipt(pcodeexpr :: pcodeexpr_tail*,pcpath) = $tp280_without_receipt(pcodeexpr_tail*,pcpath)
  -- if $tp280_receipt(pcodeexpr,pcpath)
def $tp280_without_receipt(pcodeexpr :: pcodeexpr_tail*,pcpath) = pcodeexpr :: $tp280_without_receipt(pcodeexpr_tail*,pcpath)
  -- if ~$tp280_receipt(pcodeexpr,pcpath)
'''
SELECTED = pair.SELECTED.replace('B|C|', 'B|Q|C|')


def fields(fixture, source, actual):
    pair.SOURCE = source
    ns = 'Ns280UntypedTrait' + ('Actual' if actual else 'Implicit') + 'PairPeer'
    root = quoted(ns + chr(92) + 'Root280')
    trait = quoted(ns + chr(92) + 'RootPad280')
    oldroot = quoted('Ns275UntypedHookPairPeer' + chr(92) + 'Root275')
    original = pair.fields(fixture)
    stop = original.index('$property_hook_pair_origins(S_raw,ppropertydesc_rootpad) = [porigin_get,porigin_set]')
    checks = []
    for check in original[:stop]:
        if not check.startswith('U = '):
            check = check.replace(oldroot, root).replace('275', '280').replace('B|C|', 'B|Q|C|')
            check = check.replace('[ppropertyslot_rootpad,ppropertyslot_middle,ppropertyslot_tail]',
                                  '[ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_rootpad]')
            check = check.replace('[ppropertydesc_rootpad,ppropertydesc_middle,ppropertydesc_tail]',
                                  '[ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_rootpad]')
            check = check.replace('ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT (PBOOL false))',
                                  'ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT PNULL)')
            check = check.replace('ppropertydesc_rootpad.DEFAULT = PROP_STORED porigin_default',
                                  'ppropertydesc_rootpad.DEFAULT = PROP_NULL')
        checks.append(check)
    checks += [
        '$class_named(S_raw.CLASSNAMES,$ptlc(' + trait + ')) = (porigin_trait)',
        '$class_at(S_raw.CLASSES,porigin_trait) = (pclassdesc_trait)',
        'pclassdesc_trait.KIND = "trait"', 'pclassdesc_trait.PARENT = eps', '~pclassdesc_trait.READONLY',
        'pclassdesc_trait.PROPERTIES = [ppropertydesc_source]',
        'ppropertydesc_source.TYPE = eps', 'ppropertydesc_source.DEFAULT = PROP_NULL',
        'ppropertydesc_source.ORIGIN = PORIGIN n_source pcpath_property',
        'ppropertydesc_rootpad = $trait_data_property(pclassdesc_root,ppropertydesc_source)',
        'ppropertydesc_rootpad.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_root (PORIGIN n_source pcpath_property)',
        '$trait_plan(S_raw,pclassdesc_trait).TRAITS = eps',
        '$trait_plan(S_raw,pclassdesc_root) = {TRAITS ([pclassdesc_trait.NAME]), PRECEDENCES eps, ALIASES eps}',
        '$trait_fetch(S_raw,$trait_plan(S_raw,pclassdesc_root).TRAITS,eps) = TRAITFETCHED ([pclassdesc_trait])',
        '$property_hook_pair_untyped_import(S_raw,pclassdesc_root,ppropertydesc_source,[pclassdesc_trait])',
        '$property_hook_pair_sources(S_raw,pclassdesc_root,ppropertydesc_source) = [(pclassdesc_trait,ppropertydesc_source)]',
        '$property_hook_pair_export(S_raw,pclassdesc_root,ppropertydesc_source) = (ppropertydesc_source)',
        '$property_hook_pair_import(S_raw,pclassdesc_root,ppropertydesc_source,ppropertydesc_source)',
        '$property_hook_pair_origins(S_raw,ppropertydesc_rootpad) = eps',
        '$property_hook_pair_origins(S_raw,ppropertydesc_source) = [porigin_get,porigin_set]',
        '$property_hook_pair_backed(S_raw,ppropertydesc_source)',
        '$property_hook_origin(S_raw,ppropertydesc_source) = (porigin_get)',
        '$property_set_origin(S_raw,ppropertydesc_source) = (porigin_set)',
        'porigin_get = PORIGIN n_source pcpath_get', 'porigin_set = PORIGIN n_source pcpath_set',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
        '$origin_node(S_raw.SOURCES,porigin_set) = (phpType38_set)',
        '$origin_node(S_raw.SOURCES,porigin_get) = (phpType38_get)',
        'phpType38_get = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) phpType39_get metadata_get',
        'phpType38_set = NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_set phpType16_set phpType39_set metadata_set',
        '$hook_parameter_facts(metadata_get) = [false]',
        '$hook_pair_untyped_trait_headers(phpType38_get,phpType38_set,ppropertydesc_source.NAME)',
        '$hook_pair_untyped_trait_get_index(phpType38_set,phpType38_get,ppropertydesc_source.NAME) = (1)',
        '~$hook_pair_untyped_trait_headers(phpType38_set,phpType38_get,ppropertydesc_source.NAME)',
        '$hook_body_backed(phpType39_get,ppropertydesc_source.NAME)',
        '$function_at(S_raw.FUNCTIONS,porigin_get) = (pfunction_get)',
        '$function_at(S_raw.FUNCTIONS,porigin_set) = (pfunction_set)',
        'pfunction_get.NAME = pclassdesc_trait.NAME ++ $ptascii("::$pad::get")',
        'pfunction_set.NAME = pclassdesc_trait.NAME ++ $ptascii("::$pad::set")',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}',
        'pfunction_set.SIGNATURE.RETURNS = [PTBRANCH ([PTBUILTIN "void"])]',
        '~pfunction_set.SIGNATURE.BYREF',
        'pfunction_get.BODY = pcpath_get ++ [PCFIELD 5]',
        'pfunction_set.BODY = pcpath_set ++ [PCFIELD 5]',
        '$hook_pair_untyped_trait_signature(S_raw,pclassdesc_trait,ppropertydesc_source,pfunction_set,phpType16_set,metadata_set)',
        '$property_hook_pair_raw_functions(S_raw,ppropertydesc_source) = [pfunction_get,pfunction_set]',
        'porigin_get_imported = TRAIT_ORIGIN porigin_root porigin_get ($hook_name(ppropertydesc_source.NAME))',
        'porigin_set_imported = TRAIT_ORIGIN porigin_root porigin_set ($property_set_name(ppropertydesc_source.NAME))',
        '$property_hook_trait_origin(S_raw,ppropertydesc_rootpad) = (porigin_get_imported)',
        '$property_set_trait_origin(S_raw,ppropertydesc_rootpad) = (porigin_set_imported)',
        '$property_hook_trait_pair_functions(S_raw,ppropertydesc_rootpad) = [pfunction_get_imported,pfunction_set_imported]',
        'pfunction_get_imported = pfunction_get[.ORIGIN = porigin_get_imported][.NAME = pclassdesc_root.NAME ++ $ptascii("::$pad::get")]',
        'pfunction_set_imported = pfunction_set[.ORIGIN = porigin_set_imported][.NAME = pclassdesc_root.NAME ++ $ptascii("::$pad::set")]',
        '$property_set_signature_at(S_raw,ppropertydesc_rootpad) = (pfunction_set.SIGNATURE)',
        '$function_at($all_functions(S_raw),porigin_get_imported) = (pfunction_get_imported)',
        '$function_at($all_functions(S_raw),porigin_set_imported) = (pfunction_set_imported)',
        '$function_at(S_raw.FUNCTIONS,porigin_get_imported) = eps',
        '$function_at(S_raw.FUNCTIONS,porigin_set_imported) = eps',
        'S_class = $class_constant_selector(S_raw,expression_class,z)', 'S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING pclassdesc_root.NAME)',
        '$class_constant_reference_object_graph(S_class,n_receiver,eps)',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_class.SOURCES = [pcunit]', 'S_class.CODE = [pcode_unit]',
        'S_functions = S_class[.FUNCTIONS = [pfunction_get,pfunction_set]]',
        '$property_hook_pair_origins(S_functions,ppropertydesc_source) = [porigin_get,porigin_set]',
        '$origin_node(S_class.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_set,phpType38_get])) metadata_group)',
        'S_no_file = S_class[.FILES = eps]',
        '$property_hook_pair_raw_functions(S_no_file,ppropertydesc_source) = eps',
        '$property_hook_pair_sources(S_no_file,pclassdesc_root,ppropertydesc_source) = eps',
        '$property_hook_trait_pair_functions(S_no_file,ppropertydesc_rootpad) = eps',
        'pcnode_no_line = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_set,phpType38_get])) eps',
        'S_no_line = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group pcnode_no_line) :: pcunit.OCCURRENCES]]]',
        '$property_hook_pair_raw_functions(S_no_line,ppropertydesc_source) = eps',
        '$property_hook_pair_sources(S_no_line,pclassdesc_root,ppropertydesc_source) = eps',
        '$property_hook_trait_pair_functions(S_no_line,ppropertydesc_rootpad) = eps',
    ]
    if actual:
        checks += [
            'phpType39_get = expression_get', 'phpType39_set = expression_set',
            '$hook_parameter_facts(metadata_set) = [true]',
            'phpType16_set = SEQUENCE ([phpType17_parameter])',
            'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter',
            '$base64(text_parameter) = $ptascii("incoming")',
            'pfunction_set.SIGNATURE.PARAMETERS = [{NAME $ptascii("incoming"), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]',
            '$ptascii("incoming") <- pfunction_set.CVS', '~($ptascii("value") <- pfunction_set.CVS)',
            'pcpath_parameter = pcpath_set ++ [PCFIELD 4,PCINDEX 0]',
            '$origin_node(S_raw.SOURCES,PORIGIN n_source pcpath_parameter) = (phpType17_parameter)',
            '$origin_node(S_raw.SOURCES,PORIGIN n_source (pcpath_parameter ++ [PCFIELD 5])) = (NExprVariable (BYTES text_parameter) metadata_variable)',
            '$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_parameter) = (($psline(metadata_parameter),false))',
            '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get,false))',
            '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get)',
            '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set,false))',
            '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
            '$origin_node(S_raw.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
        ]
    else:
        checks += [
            'phpType39_get = SEQUENCE statement_get*', 'phpType39_set = SEQUENCE statement_set*',
            'phpType16_set = SEQUENCE eps', '$hook_parameter_facts(metadata_set) = [false]',
            'pfunction_set.SIGNATURE = $property_set_signature(ppropertydesc_source)',
            '$ptascii("value") <- pfunction_set.CVS',
            '$origin_node(S_raw.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 4,PCINDEX 0])) = eps',
            '$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_set ++ [PCFIELD 4,PCINDEX 0]) = eps',
        ]
    for exporters in ['eps','[pclassdesc_trait,pclassdesc_trait]']:
        checks += ['~$property_hook_pair_untyped_import(S_class,pclassdesc_root,ppropertydesc_source,' + exporters + ')']
    for change in ['[.KIND = "trait"]', '[.READONLY = true]']:
        checks += ['~$property_hook_pair_untyped_import(S_class,pclassdesc_root' + change + ',ppropertydesc_source,[pclassdesc_trait])']
    checks += [
        'pclassdesc_bad_parent = pclassdesc_root[.PARENT = (pclassdesc_root.NAME)]',
        'S_bad_parent = S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_bad_parent)]',
        '$property_hook_pair_sources(S_bad_parent,pclassdesc_bad_parent,ppropertydesc_source) = eps',
        '$property_hook_trait_pair_functions(S_bad_parent,ppropertydesc_rootpad) = eps',
        '$property_hook_pair_untyped_import(S_class,pclassdesc_root[.READONLY = true],ppropertydesc_source[.TYPE = [PTBRANCH ([PTBUILTIN "int"])]],eps)',
        '~$property_hook_pair_untyped_import(S_class,pclassdesc_root,ppropertydesc_source,[pclassdesc_trait[.PROPERTIES = eps]])',
        'ppropertydesc_shadow = ppropertydesc_source[.ORIGIN = porigin_set]',
        'pclassdesc_shadow = pclassdesc_trait[.PROPERTIES = [ppropertydesc_shadow,ppropertydesc_source]]',
        'S_shadow = S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_shadow)]',
        '$property_hook_pair_raw_functions(S_shadow,ppropertydesc_source) = [pfunction_get,pfunction_set]',
        '$ppproperty_desc_at(pclassdesc_shadow.PROPERTIES,ppropertydesc_source.NAME) = (ppropertydesc_shadow)',
        '$property_hook_pair_sources(S_shadow,pclassdesc_root,ppropertydesc_source) = [(pclassdesc_shadow,ppropertydesc_shadow)]',
        '$property_hook_pair_export(S_shadow,pclassdesc_root,ppropertydesc_source) = eps',
        '$property_hook_trait_pair_functions(S_shadow,ppropertydesc_rootpad) = eps',
        'porigin_root = PORIGIN n_source pcpath_root',
        '$origin_node(S_class.SOURCES,porigin_root) = (NStmtClass phpType14_root phpType24_root phpType3_root ABSENT phpType42_root (SEQUENCE (statement_use :: statement_root_tail*)) metadata_root)',
        'statement_use = NStmtTraitUse (SEQUENCE ([name_trait])) (SEQUENCE eps) metadata_use',
        'pcnode_duplicate = NStmtClass phpType14_root phpType24_root phpType3_root ABSENT phpType42_root (SEQUENCE ((NStmtTraitUse (SEQUENCE ([name_trait,name_trait])) (SEQUENCE eps) metadata_use) :: statement_root_tail*)) metadata_root',
        'pcode_duplicate = pcode_unit[.NAMES = (CODENAME (pcpath_root ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 1]) pclassdesc_trait.NAME eps) :: pcode_unit.NAMES]',
        'S_duplicate = S_class[.CODE = [pcode_duplicate]][.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_root pcnode_duplicate) :: pcunit.OCCURRENCES]]]',
        '$trait_plan(S_duplicate,pclassdesc_root).TRAITS = [pclassdesc_trait.NAME,pclassdesc_trait.NAME]',
        '$trait_fetch(S_duplicate,$trait_plan(S_duplicate,pclassdesc_root).TRAITS,eps) = TRAITFETCHED ([pclassdesc_trait])',
        '~$property_hook_pair_untyped_import(S_duplicate,pclassdesc_root,ppropertydesc_source,[pclassdesc_trait])',
        '$property_hook_pair_sources(S_duplicate,pclassdesc_root,ppropertydesc_source) = eps',
        '$property_hook_pair_export(S_duplicate,pclassdesc_root,ppropertydesc_source) = eps',
        '$property_hook_trait_pair_functions(S_duplicate,ppropertydesc_rootpad) = eps',
        'pcnode_adapted = NStmtClass phpType14_root phpType24_root phpType3_root ABSENT phpType42_root (SEQUENCE ((NStmtTraitUse (SEQUENCE ([name_trait])) (SEQUENCE ([NStmtTraitUseAdaptationAlias ABSENT (NIdentifier (BYTES "eA==") eps) ABSENT ABSENT eps])) metadata_use) :: statement_root_tail*)) metadata_root',
        'S_adapted = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_root pcnode_adapted) :: pcunit.OCCURRENCES]]]',
        '$trait_plan(S_adapted,pclassdesc_root).ALIASES =/= eps',
        '$property_hook_pair_sources(S_adapted,pclassdesc_root,ppropertydesc_source) = eps',
        '$property_hook_trait_pair_functions(S_adapted,ppropertydesc_rootpad) = eps',
        'porigin_trait = PORIGIN n_source pcpath_trait',
        '$origin_node(S_class.SOURCES,porigin_trait) = (NStmtTrait phpType14_trait phpType3_trait (SEQUENCE statement_trait*) metadata_trait)',
        'pcnode_nested = NStmtTrait phpType14_trait phpType3_trait (SEQUENCE (statement_use :: statement_trait*)) metadata_trait',
        'pcode_nested = pcode_unit[.NAMES = (CODENAME (pcpath_trait ++ [PCFIELD 2,PCINDEX 0,PCFIELD 0,PCINDEX 0]) pclassdesc_trait.NAME eps) :: pcode_unit.NAMES]',
        'S_nested = S_class[.CODE = [pcode_nested]][.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_trait pcnode_nested) :: pcunit.OCCURRENCES]]]',
        '$trait_plan(S_nested,pclassdesc_trait).TRAITS = [pclassdesc_trait.NAME]',
        '~$property_hook_pair_untyped_import(S_nested,pclassdesc_root,ppropertydesc_source,[pclassdesc_trait])',
        '$property_hook_pair_origins(S_nested,ppropertydesc_source) = eps',
        '$property_hook_pair_sources(S_nested,pclassdesc_root,ppropertydesc_source) = eps',
        'phpType39_quiet_block = SEQUENCE ([NStmtReturn (NScalarInt (INTEGER 0) eps) eps])',
        '~$hook_pair_untyped_trait_bodies(phpType39_quiet_block,NScalarInt (INTEGER 0) eps,ppropertydesc_source.NAME)',
        '~$hook_pair_untyped_trait_bodies(NScalarInt (INTEGER 0) eps,phpType39_quiet_block,ppropertydesc_source.NAME)',
        '$hook_pair_untyped_trait_bodies(phpType39_get,phpType39_set,ppropertydesc_source.NAME)',
    ]
    for label, change in [('private','[.VISIBILITY = PROPERTY_PRIVATE]'),('static','[.STATIC = true]'),
                          ('readonly','[.READONLY = true]'),('final','[.FINAL = true]'),
                          ('virtual','[.DEFAULT = PROP_UNINITIALIZED]')]:
        prop = 'ppropertydesc_' + label
        state = 'S_property_' + label
        checks += [prop + ' = ppropertydesc_source' + change,
                   state + ' = S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_trait[.PROPERTIES = [' + prop + ']])]',
                   '$property_hook_pair_origins(' + state + ',' + prop + ') = eps']
    for role in ['get', 'set']:
        for label, change in [('missing',''), ('early','[.EARLY = true]'),
                              ('reference','[.SIGNATURE.BYREF = true]'),
                              ('code','[.CODE.EXPRESSIONS = eps]')]:
            if not actual and label == 'code':
                continue
            functions = ['pfunction_' + r + (change if r == role else '') for r in ['get','set']
                         if label != 'missing' or r != role]
            state = 'S_' + role + '_' + label
            checks += [state + ' = S_functions[.FUNCTIONS = [' + ','.join(functions) + ']]',
                       '$property_hook_pair_origins(' + state + ',ppropertydesc_source) = eps',
                       '$property_hook_trait_pair_functions(' + state + ',ppropertydesc_rootpad) = eps',
                       '~$class_constant_reference_object_graph(' + state + ',n_receiver,eps)']
    if actual:
        checks += [
            'pfunction_wrong_parameter = pfunction_set[.CODE.EXPRESSIONS = (CODEEXPR pcpath_parameter $($psline(metadata_parameter) + 1) false) :: $tp280_without_receipt(pfunction_set.CODE.EXPRESSIONS,pcpath_parameter)]',
            'S_parameter_line = S_functions[.FUNCTIONS = [pfunction_get,pfunction_wrong_parameter]]',
            '$property_hook_pair_origins(S_parameter_line,ppropertydesc_source) = eps',
            '$property_hook_trait_pair_functions(S_parameter_line,ppropertydesc_rootpad) = eps',
            'S_parameter_child = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_parameter ++ [PCFIELD 5]) (NExprVariable (BYTES "dmFsdWU=") metadata_variable)) :: pcunit.OCCURRENCES]]]',
            '$property_hook_pair_origins(S_parameter_child,ppropertydesc_source) = eps',
            '$property_hook_trait_pair_functions(S_parameter_child,ppropertydesc_rootpad) = eps',
        ]
    for role in ['get','set']:
        state = 'S_' + role + '_child'
        checks += [state + ' = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_' + role + ' (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]',
                   '$property_hook_pair_origins(' + state + ',ppropertydesc_source) = eps',
                   '$property_hook_trait_pair_functions(' + state + ',ppropertydesc_rootpad) = eps']
    oldroot = quoted('Ns267UntypedSetPeer' + chr(92) + 'Root267')
    original = peer.fields(fixture)
    start = original.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)')
    for check in original[start:]:
        check = check.replace(oldroot,root).replace('267','280').replace('B|C|','B|Q|C|')
        check = check.replace('[ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET]]',
                              '[ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET]]')
        if '.STORE[n_called]' in check:
            checks += [check.replace('n_called','n_set'),check.replace('n_called','n_get')]
        else:
            checks.append(check)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit','actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('nested-untyped-trait-' + args.form + '-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__),Path(pair.__file__),Path(peer.__file__),Path(header.__file__),source,*modules,
             *(ROOT / p for p in ('spec/semantics/modules.json','spec/php.watsup','spec/schema.json',
                 'frontend/worker.php','frontend/SourcePrinter.php','tests/semantics/deprecated_class_constant_fetch_protocol.py',
                 'tests/semantics/deprecated_parameter_default_protocol.py','tests/semantics/deprecated_global_constant_protocol.py',
                 'tests/semantics/recorded_worker.py','tests/semantics/error_handler_run.py','tests/semantics/static_types.py',
                 'tests/semantics/profile.json','.tools/php/bin/php','.tools/php-file.so',
                 '_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)):sha(p) for p in paths}
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report = {'head':head,'inputs':before,'module_count':len(modules),'form':args.form,
              'mode':'fixture-SL','source_agreement_credit':0,'passed':False}
    try:
        frontend = Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')],out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        try:
            parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'],source,args.form == 'actual'); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks,indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
                                           + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',
                                      *map(str,modules),str(out / 'protocol.watsup')],out / 'check',240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)):sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
    assert report['passed'],report.get('stderr','')[:4000]
    print('pass',args.form,report['premises'])


if __name__ == '__main__': main()
