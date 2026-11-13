#!/usr/bin/env python3
"""Reach imported trait pair entries, real setter CVs and first-write resumption."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_pair_implicit_set_protocol as pair
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).with_name('deprecated_reference_object_untyped_trait_pairs')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def fields(fixture, source, kind):
    actual = kind == 'actual'
    name = 'input280ss' if actual else 'value'
    namespace = 'Ns280TraitActualShortShort' if actual else 'Ns280TraitImplicitShortBlock'
    set_body = 'expression_set' if actual else '(SEQUENCE statement_set*)'
    c = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(pair.b64(bytes(source))) + ')',
        'S_get = $pair_pause(S_start[.COMPLETION = NORMAL],"get",30000)', '$pair_phase(S_get,"get")',
        'S_get.CURRENT = (pcallcontext_get)', 'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_get',
        'pcallcontext_get.RECEIVER = (n_object)',
        'ppropertyhook_get.PROPERTY = TRAIT_MEMBER_ORIGIN porigin_owner porigin_property',
        '$class_at(S_get.CLASSES,porigin_owner) = (pclassdesc_consumer)',
        'pclassdesc_consumer.NAME = $base64(' + json.dumps(pair.b64((namespace + '\\Box280').encode())) + ')',
        'pclassdesc_consumer.PARENT = eps', 'pclassdesc_consumer.PROPERTIES = [ppropertydesc_imported]',
        '$trait_property_source_at(S_get.CLASSES,porigin_property) = (ppropertydesc)',
        'ppropertydesc_imported = $trait_data_property(pclassdesc_consumer,ppropertydesc)',
        'ppropertydesc.ORIGIN = porigin_property', 'porigin_property = PORIGIN n_source pcpath_property',
        '$property_declaring_class(S_get.CLASSES,porigin_property) = (porigin_trait)',
        '$class_at(S_get.CLASSES,porigin_trait) = (pclassdesc_trait)',
        'pclassdesc_trait.KIND = "trait"', 'pclassdesc_trait.NAME = $base64(' + json.dumps(pair.b64((namespace + '\\Pair280').encode())) + ')',
        '$trait_plan(S_get,pclassdesc_trait).TRAITS = eps',
        '|$trait_plan(S_get,pclassdesc_consumer).TRAITS| = 1',
        '$trait_plan(S_get,pclassdesc_consumer).PRECEDENCES = eps', '$trait_plan(S_get,pclassdesc_consumer).ALIASES = eps',
        '$trait_fetch(S_get,$trait_plan(S_get,pclassdesc_consumer).TRAITS,eps) = TRAITFETCHED ([pclassdesc_trait])',
        '$property_hook_pair_untyped_import(S_get,pclassdesc_consumer,ppropertydesc,[pclassdesc_trait])',
        '$property_hook_pair_sources(S_get,pclassdesc_consumer,ppropertydesc) = [(pclassdesc_trait,ppropertydesc)]',
        'ppropertydesc.TYPE = eps', 'ppropertydesc.NAME = $ptascii("tag")', 'ppropertydesc.DEFAULT = PROP_NULL',
        '$property_hook_pair_origins(S_get,ppropertydesc) = [porigin_get,porigin_set]',
        '$property_hook_pair_raw_functions(S_get,ppropertydesc) = [pfunction_get,pfunction_set]',
        '$property_hook_function(S_get,ppropertyhook_get) = (pfunction_get_clone)',
        'pfunction_get_clone = pfunction_get[.ORIGIN = TRAIT_ORIGIN porigin_owner porigin_get ($hook_name(ppropertydesc.NAME))][.NAME = pclassdesc_consumer.NAME ++ $ptascii("::") ++ $hook_name(ppropertydesc.NAME)]',
        'pcallcontext_get.FUNCTION = pfunction_get_clone.ORIGIN',
        'pcallcontext_get.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext_get.CALLED_CLASS = (porigin_owner)',
        'porigin_get = PORIGIN n_source pcpath_get', '$(|pcpath_get| >= 2)',
        'pcpath_group = pcpath_get[0:$nabs($( |pcpath_get| - 2))]',
        'pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'porigin_set = PORIGIN n_source pcpath_set', 'pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}',
        'pfunction_set.SIGNATURE.PARAMETERS = [{NAME $ptascii("' + name + '"), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]',
        'pfunction_set.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]', '~pfunction_set.SIGNATURE.BYREF',
        '$origin_node(S_get.SOURCES,porigin_get) = (NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) expression_get metadata_get)',
        '$origin_node(S_get.SOURCES,porigin_set) = (NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_set phpType16_set ' + set_body + ' metadata_set)',
        '$hook_parameter_facts(metadata_get) = [false]', '$hook_parameter_facts(metadata_set) = [' + ('true' if actual else 'false') + ']',
        'pfunction_get.DEFAULTS = eps', 'pfunction_set.DEFAULTS = eps', '~pfunction_get.EARLY', '~pfunction_set.EARLY',
        'pfunction_get.BODY = pcpath_get ++ [PCFIELD 5]', 'pfunction_set.BODY = pcpath_set ++ [PCFIELD 5]',
        'pfunction_get.LINE = 5', 'pfunction_get.ENDLINE = 8', 'pfunction_set.LINE = 9',
        'pfunction_set.ENDLINE = ' + ('14' if actual else '12'),
        '$origin_node(S_get.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get_expr,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get_arrow)',
        r'$(z_get_expr >= 5 /\ z_get_expr <= 8)', r'$(z_get_arrow >= 5 /\ z_get_arrow <= 8)',
        '$property_hook_pair_backed(S_get,ppropertydesc)', '~$property_hook_virtual(S_get,ppropertydesc_imported)',
        '$objectprops_at(S_get.OBJECTPROPS,n_object) = ([ppropertyslot_get])',
        'ppropertyslot_get.DECL = (ppropertydesc_imported.ORIGIN)', 'ppropertyslot_get.STATE = PROP_VALUE (DIRECT PNULL)',
        '$call_descriptors_valid(S_get)', '$heap_valid($heap_graph(S_get))',
        'pcpath_param = pcpath_set ++ [PCFIELD 4,PCINDEX 0]']
    if actual:
        c += ['phpType16_set = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_param) metadata_var) ABSENT (SEQUENCE eps) metadata_param])',
            '$base64(text_param) = $ptascii("' + name + '")',
            '$origin_node(S_get.SOURCES,PORIGIN n_source pcpath_param) = (NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_param) metadata_var) ABSENT (SEQUENCE eps) metadata_param)',
            '$origin_node(S_get.SOURCES,PORIGIN n_source (pcpath_param ++ [PCFIELD 5])) = (NExprVariable (BYTES text_param) metadata_var)',
            '$psline(metadata_param) = 10', '$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_param) = ((10,false))',
            '$origin_node(S_get.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
            '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set_rhs,false))',
            r'$(z_set_rhs >= 12 /\ z_set_rhs <= 14)']
    else:
        c += ['phpType16_set = SEQUENCE eps', '$origin_node(S_get.SOURCES,PORIGIN n_source pcpath_param) = eps',
            '$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_param) = eps']
    c += ['S_set = $pair_pause(S_get,"set",30000)', '$pair_phase(S_set,"set")',
        'S_set.CURRENT = (pcallcontext_set)', 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook_set',
        '$property_set_function(S_set,ppropertyhook_set) = (pfunction_set_clone)',
        'pfunction_set_clone = pfunction_set[.ORIGIN = TRAIT_ORIGIN porigin_owner porigin_set ($property_set_name(ppropertydesc.NAME))][.NAME = pclassdesc_consumer.NAME ++ $ptascii("::") ++ $property_set_name(ppropertydesc.NAME)]',
        'pcallcontext_set.FUNCTION = pfunction_set_clone.ORIGIN', 'pcallcontext_set.RECEIVER = (n_object)',
        'pcallcontext_set.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext_set.CALLED_CLASS = (porigin_owner)',
        '$lookup(S_set.ENV,$ptascii("' + name + '")) = (n_value)', 'S_set.STORE[n_value] = DEFINED (PBOOL false)',
        '$ptascii("' + name + '") <- pfunction_set_clone.CVS',
        ('$property_set_explicit_origin' if actual else '~$property_set_explicit_origin') + '(S_set,pfunction_set_clone.ORIGIN)',
        '$default_parameter_line(S_set,pfunction_set_clone.ORIGIN,0) = ' + ('10' if actual else '9'),
        '$call_descriptors_valid(S_set)', '$heap_valid($heap_graph(S_set))']
    if actual: c += ['$lookup(S_set.ENV,$ptascii("value")) = eps', '~($ptascii("value") <- pfunction_set_clone.CVS)']
    c += ['S_zero = $drive_steps(S_set,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_set',
        'S_one = $drive_steps(S_set,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = $pair_pause(S_set,"after",30000)', '$pair_phase(S_after,"after")',
        '$pair_pause(S_zero[.COMPLETION = NORMAL],"after",30000) = S_after',
        '$pair_pause(S_one[.COMPLETION = NORMAL],"after",30000) = S_after',
        '$objectprops_at(S_after.OBJECTPROPS,n_object) = ([ppropertyslot_after])',
        'ppropertyslot_after.DECL = (ppropertydesc_imported.ORIGIN)', 'ppropertyslot_after.STATE = PROP_VALUE (DIRECT (PBOOL true))',
        '$lookup(S_after.ENV,$ptascii("' + name + '")) = eps',
        'S_after.CURRENT = eps', 'S_after.FRAMES = eps', 'S_after.HELD = eps',
        '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))']
    return c


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--kind', required=True, choices=('implicit','actual'))
    args = parser.parse_args(); actual = args.kind == 'actual'
    source = SOURCE_DIR / ('trait-actual-short-get-short-set.php' if actual else 'trait-implicit-short-get-block-set.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(pair.__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php','frontend/SourcePrinter.php',
        'tests/semantics/recorded_worker.py','tests/semantics/error_handler_run.py','tests/semantics/static_types.py',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py','tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py','tests/semantics/profile.json','.tools/php/bin/php','.tools/php-file.so',
        '_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report = {'head':head,'inputs':before,'module_count':len(modules),'source_agreement_credit':0,'kind':args.kind,'mode':'fixture-SL','passed':False}
    try:
        frontend = Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        try:
            parsed = frontend.request({'op':'parse','source':pair.b64(source.read_bytes())}); assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'],source,args.kind); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks,indent=2) + '\n')
        pause = pair.PAUSE.replace('275','280').replace('pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)','pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)')
        if actual:
            pause = pause.replace('$ptascii("value")','$ptascii("input280ss")').replace('pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)','pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)')
        (out / 'protocol.watsup').write_text(pair.PREFIX + pair.SELECTED + pause + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out / 'protocol.watsup')],out / 'check',240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally: (out / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
    if not report['passed']: print(report.get('stdout','')[:2000],report.get('stderr','')[:4000])
    assert report['passed']; print('pass',report['premises'])


if __name__ == '__main__': main()
