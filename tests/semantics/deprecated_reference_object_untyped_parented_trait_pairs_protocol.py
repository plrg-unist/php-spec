#!/usr/bin/env python3
"""Reach parented untyped trait pair entry, parent authority and first-write resume."""
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
SOURCE_DIR = Path(__file__).with_name('deprecated_reference_object_untyped_parented_trait_pairs')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def fields(fixture, source, kind):
    actual = kind == 'actual'
    name = 'input281sb' if actual else 'value'
    namespace = 'Ns281TraitActualShortBlock' if actual else 'Ns281TraitImplicitBlockShort'
    quoted = lambda value: json.dumps(pair.b64(value.encode()))
    c = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(pair.b64(bytes(source))) + ')',
        'S_get = $pair_pause(S_start[.COMPLETION = NORMAL],"get",30000)', '$pair_phase(S_get,"get")',
        'S_get.CURRENT = (pcallcontext_get)', 'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_get',
        'pcallcontext_get.RECEIVER = (n_object)',
        'ppropertyhook_get.PROPERTY = TRAIT_MEMBER_ORIGIN porigin_owner porigin_property',
        '$class_at(S_get.CLASSES,porigin_owner) = (pclassdesc_consumer)',
        'pclassdesc_consumer.NAME = $base64(' + quoted(namespace + chr(92) + 'Box281') + ')',
        'pclassdesc_consumer.PARENT = (ptbytes_parent)',
        'ptbytes_parent = $base64(' + quoted(namespace + chr(92) + 'Parent281') + ')',
        '$class_named(S_get.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
        '$class_at(S_get.CLASSES,porigin_parent) = (pclassdesc_parent)',
        '$class_link_at(S_get.LINKEDPARENTS,porigin_owner) = (SOURCE_PARENT porigin_parent)',
        'pclassdesc_parent.PARENT = eps', 'pclassdesc_parent.KIND = "class"',
        'pclassdesc_parent.PROPERTIES = [ppropertydesc_pad]',
        'ppropertydesc_pad.NAME = $ptascii("parentPad")',
        '$property_hook_pair_source_header(S_get,pclassdesc_consumer)',
        '$property_hook_pair_source_header(S_get,pclassdesc_parent)',
        '$property_hook_pair_plain_parent(S_get,pclassdesc_parent.PROPERTIES)',
        '$ppproperty_desc_at($property_info_layout(S_get,porigin_parent,|S_get.CLASSES|),$ptascii("tag")) = eps',
        '$property_hook_pair_parent(S_get,pclassdesc_consumer,$ptascii("tag"))',
        '$property_hook_pair_linked(S_get,pclassdesc_consumer,$ptascii("tag"))',
        'pclassdesc_consumer.PROPERTIES = [ppropertydesc_imported]',
        '$trait_property_source_at(S_get.CLASSES,porigin_property) = (ppropertydesc)',
        'ppropertydesc_imported = $trait_data_property(pclassdesc_consumer,ppropertydesc)',
        'porigin_property = PORIGIN n_source pcpath_property',
        '$source_unit(S_get.SOURCES,n_source) = (pcunit)',
        'pcunit = $pcsource(pcunit.ID,pcunit.AST)',
        'S_bad_unit = S_get[.SOURCES = [pcunit[.OCCURRENCES = eps]]]',
        '~$property_hook_pair_source_header(S_bad_unit,pclassdesc_consumer)',
        '~$property_hook_pair_source_headers(S_bad_unit,pclassdesc_consumer,pclassdesc_parent)',
        '$property_declaring_class(S_get.CLASSES,porigin_property) = (porigin_trait)',
        '$class_at(S_get.CLASSES,porigin_trait) = (pclassdesc_trait)',
        'pclassdesc_trait.KIND = "trait"', '$trait_plan(S_get,pclassdesc_trait).TRAITS = eps',
        '|$trait_plan(S_get,pclassdesc_consumer).TRAITS| = 1',
        '$property_hook_pair_sources(S_get,pclassdesc_consumer,ppropertydesc) = [(pclassdesc_trait,ppropertydesc)]',
        'ppropertydesc.TYPE = eps', 'ppropertydesc.NAME = $ptascii("tag")',
        '$property_hook_pair_origins(S_get,ppropertydesc) = [porigin_get,porigin_set]',
        '$property_hook_pair_raw_functions(S_get,ppropertydesc) = [pfunction_get,pfunction_set]',
        '$property_hook_function(S_get,ppropertyhook_get) = (pfunction_get_clone)',
        'pfunction_get_clone = pfunction_get[.ORIGIN = TRAIT_ORIGIN porigin_owner porigin_get ($hook_name(ppropertydesc.NAME))][.NAME = pclassdesc_consumer.NAME ++ $ptascii("::") ++ $hook_name(ppropertydesc.NAME)]',
        'pfunction_set_clone = pfunction_set[.ORIGIN = TRAIT_ORIGIN porigin_owner porigin_set ($property_set_name(ppropertydesc.NAME))][.NAME = pclassdesc_consumer.NAME ++ $ptascii("::") ++ $property_set_name(ppropertydesc.NAME)]',
        '$property_hook_trait_pair_functions(S_get,ppropertydesc_imported) = [pfunction_get_clone,pfunction_set_clone]',
        'pcallcontext_get.FUNCTION = pfunction_get_clone.ORIGIN',
        'pcallcontext_get.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext_get.CALLED_CLASS = (porigin_owner)',
        '$objectprops_at(S_get.OBJECTPROPS,n_object) = ([ppropertyslot_pad,ppropertyslot_get])',
        'ppropertyslot_pad.DECL = (ppropertydesc_pad.ORIGIN)',
        'ppropertyslot_pad.STATE = PROP_VALUE (DIRECT (PINT 31))',
        'ppropertyslot_get.DECL = (ppropertydesc_imported.ORIGIN)',
        'ppropertyslot_get.STATE = PROP_VALUE (DIRECT ' + ('PNULL' if actual else '(PINT 17)') + ')',
        '$call_descriptors_valid(S_get)', '$heap_valid($heap_graph(S_get))',
        'S_bad_link = S_get[.LINKEDPARENTS = eps]',
        '~$property_hook_pair_linked(S_bad_link,pclassdesc_consumer,$ptascii("tag"))',
        '$property_hook_trait_pair_functions(S_bad_link,ppropertydesc_imported) = eps',
        'S_wrong_link = S_get[.LINKEDPARENTS = [CLASSLINK porigin_owner (SOURCE_PARENT porigin_trait)]]',
        '$property_hook_trait_pair_functions(S_wrong_link,ppropertydesc_imported) = eps']
    for suffix, change in [('parent_name','[.NAME = $ptascii("wrong")]'),
                           ('parent_line','[.LINE = 999]'),
                           ('parent_readonly','[.READONLY = true]'),
                           ('parent_hook','[.PROPERTIES = [ppropertydesc]]'),
                           ('parent_overlap','[.PROPERTIES = [ppropertydesc_pad[.NAME = $ptascii("tag")][.KEY = $ptascii("tag")]]]')]:
        c += ['S_' + suffix + ' = S_get[.CLASSES = $trait_class_set(S_get.CLASSES,pclassdesc_parent' + change + ')]',
              '~$property_hook_pair_parent(S_' + suffix + ',pclassdesc_consumer,$ptascii("tag"))',
              '$property_hook_pair_sources(S_' + suffix + ',pclassdesc_consumer,ppropertydesc) = eps',
              '$property_hook_trait_pair_functions(S_' + suffix + ',ppropertydesc_imported) = eps']
    c += ['pclassdesc_bad_parent = pclassdesc_consumer[.PARENT = (pclassdesc_consumer.NAME)]',
        'S_bad_parent = S_get[.CLASSES = $trait_class_set(S_get.CLASSES,pclassdesc_bad_parent)]',
        '$property_hook_pair_sources(S_bad_parent,pclassdesc_bad_parent,ppropertydesc) = eps',
        '$property_hook_trait_pair_functions(S_bad_parent,ppropertydesc_imported) = eps',
        'S_set = $pair_pause(S_get,"set",30000)', '$pair_phase(S_set,"set")',
        'S_set.CURRENT = (pcallcontext_set)', 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook_set',
        '$property_set_function(S_set,ppropertyhook_set) = (pfunction_set_clone)',
        'pcallcontext_set.FUNCTION = pfunction_set_clone.ORIGIN', 'pcallcontext_set.RECEIVER = (n_object)',
        'pcallcontext_set.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext_set.CALLED_CLASS = (porigin_owner)',
        '$lookup(S_set.ENV,$ptascii("' + name + '")) = (n_value)', 'S_set.STORE[n_value] = DEFINED (PBOOL false)',
        '$ptascii("' + name + '") <- pfunction_set_clone.CVS',
        ('$property_set_explicit_origin' if actual else '~$property_set_explicit_origin') + '(S_set,pfunction_set_clone.ORIGIN)',
        '$default_parameter_line(S_set,pfunction_set_clone.ORIGIN,0) = ' + ('6' if actual else '9'),
        '$call_descriptors_valid(S_set)', '$heap_valid($heap_graph(S_set))']
    if actual: c += ['$lookup(S_set.ENV,$ptascii("value")) = eps', '~($ptascii("value") <- pfunction_set_clone.CVS)']
    c += ['S_zero = $drive_steps(S_set,0)', 'S_zero.COMPLETION = BUDGET', 'S_zero[.COMPLETION = NORMAL] = S_set',
        'S_one = $drive_steps(S_set,1)', 'S_one.COMPLETION = BUDGET',
        'S_after = $pair_pause(S_set,"after",30000)', '$pair_phase(S_after,"after")',
        '$pair_pause(S_zero[.COMPLETION = NORMAL],"after",30000) = S_after',
        '$pair_pause(S_one[.COMPLETION = NORMAL],"after",30000) = S_after',
        '$objectprops_at(S_after.OBJECTPROPS,n_object) = ([ppropertyslot_pad,ppropertyslot_after])',
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
    source = SOURCE_DIR / ('parented-trait-actual-short-get-block-set.php' if actual else 'parented-trait-implicit-block-get-short-set.php')
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
        pause = pair.PAUSE.replace('275','281')
        target = 'PROPERTY_HOOK_TARGET' if actual else 'PROPERTY_SET_TARGET'
        pause = pause.replace('pcallcontext.TARGET = ' + target + ' ppropertyhook\n  -- if S.TODO = (STMT statement)', 'pcallcontext.TARGET = ' + target + ' ppropertyhook\n  -- if S.TODO = (EVAL expression)')
        if actual: pause = pause.replace('$ptascii("value")','$ptascii("input281sb")')
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
