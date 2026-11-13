#!/usr/bin/env python3
"""Check a direct untyped trait SET import and nested outside-owner release."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_set_explicit_review_protocol as peer
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_trait_set_explicit_review') / 'nested-untyped-trait-set-explicit-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = peer.block.quoted


def fields(fixture):
    root = quoted('Ns271UntypedTraitSetExplicitPeer\\Root271')
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_raw = $hook_peer_pause(S_start[.COMPLETION = NORMAL],0,0,30000)', '$hook_peer_ready(S_raw,0,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_receiver)',
        'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps', 'S_raw.PROPREFS = eps',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_root', '$class_at(S_raw.CLASSES,porigin_root) = (pclassdesc_root)',
        'pclassdesc_root.NAME = ' + root,
        '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_rootpad])',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        'ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT (PBOOL false))',
        'S_raw.OBJECTS[n_middle] = INSTANCE porigin_middle', '$class_at(S_raw.CLASSES,porigin_middle) = (pclassdesc_middle)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_middle) = ([ppropertyslot_middlepad,ppropertyslot_edge])',
        'ppropertyslot_middlepad.STATE = PROP_VALUE (DIRECT (PBOOL true))',
        'ppropertyslot_edge.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        'S_raw.OBJECTS[n_leaf] = INSTANCE porigin_leaf', '$objectprops_at(S_raw.OBJECTPROPS,n_leaf) = (eps)',
        '$object_table_at(S_raw.OBJECTTABLES,n_receiver) = eps', '$object_table_at(S_raw.OBJECTTABLES,n_middle) = eps',
        '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_receiver]',
        '$node_children(S_raw,HOBJECT n_receiver) = [HOBJECT n_middle,HOBJECT n_leaf]',
        '$node_children(S_raw,HOBJECT n_middle) = [HOBJECT n_leaf]', '$node_children(S_raw,HOBJECT n_leaf) = eps',
        '$heap_owners($heap_graph(S_raw),HCELL n_reference) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1', '$heap_owners($heap_graph(S_raw),HOBJECT n_middle) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_leaf) = 3',
        'S_global = $global_table_view(S_raw)', '$lookup(S_global.ENV,$ptascii("outside271peer")) = (n_outside)',
        'S_global.STORE[n_outside] = DEFINED (POBJECT n_leaf)',
        '$lookup(S_global.ENV,$ptascii("called271peer")) = (n_called)', 'S_global.STORE[n_called] = DEFINED (PBOOL false)',
        '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")']
    for field, owner, name, value in [('middle','n_receiver','middle','POBJECT n_middle'),
        ('tail','n_receiver','tail','POBJECT n_leaf'), ('rootpad','n_receiver','pad','PBOOL false'),
        ('middlepad','n_middle','pad','PBOOL true'), ('edge','n_middle','edge','POBJECT n_leaf')]:
        prop = 'ppropertydesc_' + field; slot = 'ppropertyslot_' + field
        checks += ['$property_slot_descriptor(S_raw,' + owner + ',' + slot + ') = (' + prop + ')',
            slot + '.DECL = (' + prop + '.ORIGIN)', slot + '.NAME = ' + prop + '.KEY',
            prop + '.NAME = $ptascii("' + name + '")', prop + '.KEY = ' + prop + '.NAME', prop + '.TYPE = eps',
            prop + '.VISIBILITY = PROPERTY_PUBLIC', prop + '.SETVISIBILITY = eps',
            '~' + prop + '.STATIC', '~' + prop + '.READONLY', '~' + prop + '.FINAL',
            '$class_constant_reference_object_field_type(S_raw,' + prop + ',' + slot + ')',
            '$property_hook_origin(S_raw,' + prop + ') = eps',
            '$property_slot_release_job(S_raw,' + owner + ',' + slot + ') = ' +
                ('[DESTRUCTION_VALUE (HOBJECT ' + value.split()[1] + ')]' if value.startswith('POBJECT') else 'eps')]
        if field != 'rootpad':
            checks += ['$property_set_origin(S_raw,' + prop + ') = eps', '~$property_hook_source_declared(S_raw,' + prop + ')']
    checks += ['pclassdesc_root.PROPERTIES = [ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_rootpad]',
        'pclassdesc_middle.PROPERTIES = [ppropertydesc_middlepad,ppropertydesc_edge]',
        'ppropertydesc_rootpad.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_root porigin_property_source',
        '$trait_property_source_at(S_raw.CLASSES,porigin_property_source) = (ppropertydesc_source)',
        'ppropertydesc_rootpad = $trait_data_property(pclassdesc_root,ppropertydesc_source)',
        '$property_declaring_class(S_raw.CLASSES,porigin_property_source) = (porigin_trait)',
        '$property_declaring_class(S_raw.CLASSES,ppropertydesc_rootpad.ORIGIN) = (porigin_root)',
        '$class_at(S_raw.CLASSES,porigin_trait) = (pclassdesc_trait)',
        'pclassdesc_trait.NAME = ' + quoted('Ns271UntypedTraitSetExplicitPeer\\RootPad271'),
        'pclassdesc_trait.KIND = "trait"', 'pclassdesc_trait.PROPERTIES = [ppropertydesc_source]',
        'pclassdesc_trait.METHODS = eps', '$trait_plan(S_raw,pclassdesc_trait).TRAITS = eps',
        '$trait_plan(S_raw,pclassdesc_root).TRAITS = [pclassdesc_trait.NAME]',
        '$trait_plan(S_raw,pclassdesc_root).ALIASES = eps', '$trait_plan(S_raw,pclassdesc_root).PRECEDENCES = eps',
        'ppropertydesc_source.DEFAULT = PROP_STORED porigin_default',
        '$property_set_origin(S_raw,ppropertydesc_source) = (porigin_hook_source)',
        '$property_set_origin(S_raw,ppropertydesc_rootpad) = (porigin_hook)',
        'porigin_hook = TRAIT_ORIGIN porigin_root porigin_hook_source ($property_set_name(ppropertydesc_rootpad.NAME))',
        'porigin_hook_source = PORIGIN n_source pcpath_hook',
        '$origin_node(S_raw.SOURCES,porigin_hook_source) = (NPropertyHook phpType14_hook phpType24_hook phpType4_hook phpType11_hook phpType16_hook (SEQUENCE statement_set*) metadata_hook)',
        'phpType16_hook = SEQUENCE ([phpType17_parameter])',
        'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) metadata_parameter_name) ABSENT (SEQUENCE eps) metadata_parameter',
        '$base64(text_parameter) = $ptascii("traitValue271")', '~$property_set_parameters(phpType16_hook)',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source (pcpath_hook ++ [PCFIELD 4,PCINDEX 0])) = (phpType17_parameter)',
        '$function_at(S_raw.FUNCTIONS,porigin_hook_source) = (pfunction_source)',
        'pfunction_source.NAME = pclassdesc_trait.NAME ++ $ptascii("::$pad::set")',
        'pfunction_source.SIGNATURE.PARAMETERS = [psparam]',
        'psparam.NAME = $ptascii("traitValue271")', 'psparam.TYPE = eps', '~psparam.BYREF', '~psparam.VARIADIC',
        'psparam.REQUIRED', 'psparam.DEFAULT = PSNONE', '~pfunction_source.SIGNATURE.BYREF',
        'pfunction_source.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]',
        'pfunction_source.BODY = pcpath_hook ++ [PCFIELD 5]', 'pfunction_source.DEFAULTS = eps', '~pfunction_source.EARLY',
        '$property_hook_trait_selected(S_raw,ppropertydesc_rootpad,porigin_hook) = (pfunction_imported)',
        '$function_at($all_functions(S_raw),porigin_hook) = (pfunction_imported)',
        'pfunction_imported = pfunction_source[.ORIGIN = porigin_hook][.NAME = pclassdesc_root.NAME ++ $ptascii("::$pad::set")]',
        '$property_set_signature_at(S_raw,ppropertydesc_rootpad) = (pfunction_source.SIGNATURE)',
        '$default_parameter_origin(S_raw,porigin_hook,0) = PORIGIN n_source (pcpath_hook ++ [PCFIELD 4,PCINDEX 0])',
        '$default_parameter_line(S_raw,porigin_hook,0) = $psline(metadata_parameter)',
        '$function_body_tasks(S_raw,pfunction_imported) = $statement_tasks(statement_set*,(PORIGIN n_source pfunction_imported.BODY),0) ++ [$function_fallthrough(S_raw,pfunction_imported)]',
        '$hook_body_backed(SEQUENCE statement_set*,ppropertydesc_source.NAME)',
        '$class_constant_reference_object_hook_backed(S_raw,ppropertydesc_rootpad)',
        '$class_constant_reference_object_untyped_hook_field(S_raw,n_receiver,ppropertydesc_rootpad,ppropertyslot_rootpad)',
        '$property_set_expression(S_raw,porigin_hook) = eps',
        'S_class = $class_constant_selector(S_raw,expression_class,z)', 'S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING pclassdesc_root.NAME)',
        '$class_constant_reference_object_graph(S_class,n_receiver,eps)',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_function_base = S_class[.FUNCTIONS = [pfunction_source]]',
        '$property_set_origin(S_function_base,ppropertydesc_source) = (porigin_hook_source)',
        '$property_set_origin(S_function_base,ppropertydesc_rootpad) = (porigin_hook)',
        '$class_constant_reference_object_graph(S_function_base,n_receiver,eps)']
    for tag, change in [('name','.NAME = $ptascii("wrong")'), ('param','.SIGNATURE.PARAMETERS = [psparam[.NAME = $ptascii("value")]]'),
        ('type','.SIGNATURE.PARAMETERS = [psparam[.TYPE = [PTBRANCH ([PTBUILTIN "int"])]]]'),
        ('byref','.SIGNATURE.PARAMETERS = [psparam[.BYREF = true]]'), ('body','.BODY = eps'), ('returns','.SIGNATURE.RETURNS = eps')]:
        state = 'S_function_' + tag
        checks += [state + ' = S_function_base[.FUNCTIONS = [pfunction_source[' + change + ']]]',
            '$property_set_origin(' + state + ',ppropertydesc_source) = eps',
            '$property_set_origin(' + state + ',ppropertydesc_rootpad) = eps',
            '~$class_constant_reference_object_graph(' + state + ',n_receiver,eps)']
    checks += ['S_raw.SOURCES = [pcunit]',
        'S_parameter = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE (pcpath_hook ++ [PCFIELD 4,PCINDEX 0]) (NScalarInt (INTEGER 0) eps)) :: pcunit.OCCURRENCES]]]',
        '$property_set_origin(S_parameter,ppropertydesc_source) = eps',
        '$property_set_origin(S_parameter,ppropertydesc_rootpad) = eps',
        '~$class_constant_reference_object_graph(S_parameter,n_receiver,eps)',
        'S_missing = S_class[.FUNCTIONS = eps]', '$property_set_origin(S_missing,ppropertydesc_rootpad) = eps',
        '~$call_descriptors_valid(S_missing)', '~$class_constant_reference_object_graph(S_missing,n_receiver,eps)']
    for state in ['PROP_INITIAL','PROP_UNSET','PROP_VALUE UNINITIALIZED','PROP_VALUE (ALIAS n_reference)']:
        slot = 'ppropertyslot_rootpad[.STATE = ' + state + ']'
        view = 'S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_receiver,[ppropertyslot_middle,ppropertyslot_tail,' + slot + '])]'
        checks += ['~$class_constant_reference_object_untyped_hook_field(' + view + ',n_receiver,ppropertydesc_rootpad,' + slot + ')',
            '~$class_constant_reference_object_graph(' + view + ',n_receiver,eps)']
    peer.SOURCE = SOURCE
    inherited = peer.fields(fixture)
    start = inherited.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)')
    for check in inherited[start:]:
        check = check.replace(quoted('Ns270UntypedSetExplicitPeer\\Root270'), root).replace('270','271')
        check = check.replace('ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET]',
            'ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET]')
        checks.append(check)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(peer.__file__), Path(peer.block.__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', 'tests/semantics/profile.json',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(peer.block.PREFIX + peer.block.SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
