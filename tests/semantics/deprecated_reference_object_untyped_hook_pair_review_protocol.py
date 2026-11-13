#!/usr/bin/env python3
"""Check untyped class pair roles, header authority and physical outside release."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_set_review_protocol as peer
import property_hook_header_presence_review_protocol as header
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_hook_pair_review') / 'nested-untyped-hook-pair-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = peer.quoted
PREFIX = peer.PREFIX + header.PREFIX.replace('var U : program', '')
SELECTED = peer.SELECTED


def fields(fixture):
    peer.SOURCE = SOURCE
    root = quoted('Ns275UntypedHookPairPeer' + chr(92) + 'Root275')
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(base64.b64encode(bytes(SOURCE)).decode()) + ')',
        'S_raw = $hook_peer_pause(S_start[.COMPLETION = NORMAL],0,0,30000)', '$hook_peer_ready(S_raw,0,0)',
        'S_raw.TODO = (CLASS_CONST_CLASS expression_class expression_member z) :: ptask_tail*',
        'S_raw.ORIGIN = (porigin_site)', 'S_raw.RESULT = REFERENCE n_reference',
        'S_raw.STORE[n_reference] = DEFINED (POBJECT n_receiver)', 'S_raw.CURRENT = eps', 'S_raw.FRAMES = eps', 'S_raw.HELD = eps',
        'S_raw.OBJECTS[n_receiver] = INSTANCE porigin_root', '$class_at(S_raw.CLASSES,porigin_root) = (pclassdesc_root)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot_rootpad,ppropertyslot_middle,ppropertyslot_tail])',
        'ppropertyslot_middle.STATE = PROP_VALUE (DIRECT (POBJECT n_middle))',
        'ppropertyslot_tail.STATE = PROP_VALUE (DIRECT (POBJECT n_leaf))',
        'S_raw.OBJECTS[n_middle] = INSTANCE porigin_middle', '$class_at(S_raw.CLASSES,porigin_middle) = (pclassdesc_middle)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_middle) = ([ppropertyslot_middlepad,ppropertyslot_edge])',
        'S_raw.OBJECTS[n_leaf] = INSTANCE porigin_leaf', '$class_at(S_raw.CLASSES,porigin_leaf) = (pclassdesc_leaf)',
        '$objectprops_at(S_raw.OBJECTPROPS,n_leaf) = (eps)', 'pclassdesc_root.NAME = ' + root,
        'pclassdesc_root.KIND = "class"', 'pclassdesc_root.PARENT = eps', '~pclassdesc_root.READONLY',
        'pclassdesc_root.PROPERTIES = [ppropertydesc_rootpad,ppropertydesc_middle,ppropertydesc_tail]',
        'pclassdesc_middle.PROPERTIES = [ppropertydesc_middlepad,ppropertydesc_edge]',
        '$node_children(S_raw,HCELL n_reference) = [HOBJECT n_receiver]',
        '$node_children(S_raw,HOBJECT n_receiver) = [HOBJECT n_middle,HOBJECT n_leaf]',
        '$node_children(S_raw,HOBJECT n_middle) = [HOBJECT n_leaf]', '$node_children(S_raw,HOBJECT n_leaf) = eps',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_receiver) = 1', '$heap_owners($heap_graph(S_raw),HOBJECT n_middle) = 1',
        '$heap_owners($heap_graph(S_raw),HOBJECT n_leaf) = 3', 'S_global = $global_table_view(S_raw)',
        '$lookup(S_global.ENV,$ptascii("outside275peer")) = (n_outside)', 'S_global.STORE[n_outside] = DEFINED (POBJECT n_leaf)',
        '$lookup(S_global.ENV,$ptascii("set275peer")) = (n_set)', 'S_global.STORE[n_set] = DEFINED (PBOOL false)',
        '$lookup(S_global.ENV,$ptascii("get275peer")) = (n_get)', 'S_global.STORE[n_get] = DEFINED (PBOOL false)',
        'S_raw.PROPREFS = eps', '$call_descriptors_valid(S_raw)', '$ccn_output(S_raw.EVENTS) = $ptascii("B|C|")']
    for field, owner, name, value in [('rootpad','n_receiver','pad','PBOOL false'),
        ('middle','n_receiver','middle','POBJECT n_middle'), ('tail','n_receiver','tail','POBJECT n_leaf'),
        ('middlepad','n_middle','pad','PBOOL true'), ('edge','n_middle','edge','POBJECT n_leaf')]:
        prop, slot = 'ppropertydesc_' + field, 'ppropertyslot_' + field
        if field not in ('middle', 'tail'):
            checks += [slot + '.STATE = PROP_VALUE (DIRECT (' + value + '))']
        checks += ['$property_slot_descriptor(S_raw,' + owner + ',' + slot + ') = (' + prop + ')',
            slot + '.DECL = (' + prop + '.ORIGIN)', slot + '.NAME = ' + prop + '.KEY',
            prop + '.NAME = $ptascii("' + name + '")', prop + '.KEY = ' + prop + '.NAME',
            prop + '.TYPE = eps', prop + '.VISIBILITY = PROPERTY_PUBLIC', prop + '.SETVISIBILITY = eps',
            '~' + prop + '.STATIC', '~' + prop + '.READONLY', '~' + prop + '.FINAL',
            '$class_constant_reference_object_field_type(S_raw,' + prop + ',' + slot + ')']
        if field == 'rootpad':
            checks += ['$property_hook_source_declared(S_raw,' + prop + ')',
                '$property_hook_declared(S_raw,' + owner + ',' + slot + '.NAME)',
                '$class_constant_reference_object_untyped_hook_field(S_raw,' + owner + ',' + prop + ',' + slot + ')',
                prop + '.DEFAULT = PROP_STORED porigin_default', '$property_slot_release_job(S_raw,' + owner + ',' + slot + ') = eps']
        else:
            checks += ['~$property_hook_source_declared(S_raw,' + prop + ')',
                '~$property_hook_declared(S_raw,' + owner + ',' + slot + '.NAME)',
                '$property_hook_origin(S_raw,' + prop + ') = eps', '$property_set_origin(S_raw,' + prop + ') = eps']
            checks += [prop + '.DEFAULT = ' + ('PROP_NULL' if value.startswith('POBJECT') else 'PROP_STORED porigin_default_middle')]
    checks += ['$property_hook_pair_origins(S_raw,ppropertydesc_rootpad) = [porigin_get,porigin_set]',
        '$property_hook_origin(S_raw,ppropertydesc_rootpad) = (porigin_get)',
        '$property_set_origin(S_raw,ppropertydesc_rootpad) = (porigin_set)',
        '$property_hook_pair_backed(S_raw,ppropertydesc_rootpad)', '~$property_hook_virtual(S_raw,ppropertydesc_rootpad)',
        '~$property_hook_backing(S_raw,n_receiver,ppropertydesc_rootpad)',
        '$property_hook_override_backed(S_raw,ppropertydesc_rootpad)',
        'porigin_set = PORIGIN n_source pcpath_set', 'porigin_get = PORIGIN n_source pcpath_get',
        'ppropertydesc_rootpad.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_group = pcpath_property[0:$nabs($( |pcpath_property| - 2))]',
        'pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 0]', 'pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
        '$origin_node(S_raw.SOURCES,porigin_set) = (phpType38_set)', '$origin_node(S_raw.SOURCES,porigin_get) = (phpType38_get)',
        'phpType38_set = NPropertyHook phpType14_set phpType24_set phpType4_set phpType11_set (SEQUENCE eps) (SEQUENCE statement_set*) metadata_set',
        'phpType38_get = NPropertyHook phpType14_get phpType24_get phpType4_get phpType11_get (SEQUENCE eps) (SEQUENCE statement_get*) metadata_get',
        '$hook_parameter_facts(metadata_set) = [false]', '$hook_parameter_facts(metadata_get) = [false]',
        '$hook_pair_backed_headers(phpType38_get,phpType38_set,ppropertydesc_rootpad.NAME)',
        '$hook_pair_get_index(phpType38_set,phpType38_get,ppropertydesc_rootpad.NAME,"class") = (1)',
        '$hook_body_backed(SEQUENCE statement_set*,ppropertydesc_rootpad.NAME)', '$hook_body_backed(SEQUENCE statement_get*,ppropertydesc_rootpad.NAME)',
        '$function_at(S_raw.FUNCTIONS,porigin_get) = (pfunction_get)', '$function_at(S_raw.FUNCTIONS,porigin_set) = (pfunction_set)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}',
        'pfunction_set.SIGNATURE = $property_set_signature(ppropertydesc_rootpad)',
        'pfunction_get.DEFAULTS = eps', 'pfunction_set.DEFAULTS = eps', '~pfunction_get.EARLY', '~pfunction_set.EARLY',
        'pfunction_get.BODY = pcpath_get ++ [PCFIELD 5]', 'pfunction_set.BODY = pcpath_set ++ [PCFIELD 5]',
        'pfunction_get.NAME = ' + root + ' ++ $ptascii("::$pad::get")',
        'pfunction_set.NAME = ' + root + ' ++ $ptascii("::$pad::set")',
        '$function_body_tasks(S_raw,pfunction_get) = $statement_tasks(statement_get*,(PORIGIN n_source pfunction_get.BODY),0) ++ [$function_fallthrough(S_raw,pfunction_get)]',
        '$function_body_tasks(S_raw,pfunction_set) = $statement_tasks(statement_set*,(PORIGIN n_source pfunction_set.BODY),0) ++ [$function_fallthrough(S_raw,pfunction_set)]',
        '$origin_node(S_raw.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 4,PCINDEX 0])) = eps',
        '$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_set ++ [PCFIELD 4,PCINDEX 0]) = eps',
        '$ptascii("value") <- pfunction_set.CVS', '~($ptascii("value") <- pfunction_get.CVS)',
        'S_class = $class_constant_selector(S_raw,expression_class,z)', 'S_class.COMPLETION = NORMAL',
        'S_class.RESULT = KNOWN (PSTRING pclassdesc_root.NAME)',
        '$class_constant_reference_object_graph(S_class,n_receiver,eps)', '$class_constant_reference_object_graph(S_class,n_middle,[n_receiver])',
        '$class_constant_reference_object_capture_entry(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)',
        'S_class.SOURCES = [pcunit]',
        '$origin_node(S_class.SOURCES,PORIGIN n_source pcpath_group) = (NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_set,phpType38_get])) metadata_group)']
    checks += ['S_functions = S_class[.FUNCTIONS = [pfunction_get,pfunction_set]]',
        '$property_hook_pair_origins(S_functions,ppropertydesc_rootpad) = [porigin_get,porigin_set]']
    for role in ['get', 'set']:
        for name, change in [('early', '[.EARLY = true]'),
            ('defaults', '[.DEFAULTS = [{INDEX 0, ORIGIN porigin_set, KIND PDSTORED}]]')]:
            state = 'S_function_' + role + '_' + name
            pair = '[pfunction_get' + (change if role == 'get' else '') + ',pfunction_set' + (change if role == 'set' else '') + ']'
            checks += [state + ' = S_functions[.FUNCTIONS = ' + pair + ']',
                '$property_hook_pair_origins(' + state + ',ppropertydesc_rootpad) = eps',
                '$property_hook_origin(' + state + ',ppropertydesc_rootpad) = eps',
                '$property_set_origin(' + state + ',ppropertydesc_rootpad) = eps']
    for role, facts in [('set_empty','(MhookParameterList true) :: eps'), ('set_unknown','eps'), ('get_empty','(MhookParameterList true) :: eps')]:
        changed = 'set' if role.startswith('set') else 'get'
        changednode = 'phpType38_' + role
        checks += ['metadata_' + role + ' = (' + facts + ') ++ $hpr_without_fact(metadata_' + changed + ')',
            changednode + ' = NPropertyHook phpType14_' + changed + ' phpType24_' + changed + ' phpType4_' + changed + ' phpType11_' + changed + ' (SEQUENCE eps) (SEQUENCE statement_' + changed + '*) metadata_' + role]
        pair = '[' + (changednode + ',phpType38_get' if changed == 'set' else 'phpType38_set,' + changednode) + ']'
        checks += ['pcnode_' + role + ' = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE (' + pair + ')) metadata_group',
            'S_' + role + ' = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group pcnode_' + role + ') :: (PCOCCURRENCE pcpath_' + changed + ' ' + changednode + ') :: pcunit.OCCURRENCES]]]',
            '$property_hook_pair_origins(S_' + role + ',ppropertydesc_rootpad) = eps',
            '$property_hook_origin(S_' + role + ',ppropertydesc_rootpad) = eps',
            '$property_set_origin(S_' + role + ',ppropertydesc_rootpad) = eps',
            '~$class_constant_reference_object_graph(S_' + role + ',n_receiver,eps)']
    original = peer.fields(fixture)
    tail = original[original.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)'):]
    oldroot = peer.quoted('Ns267UntypedSetPeer' + chr(92) + 'Root267')
    for check in tail:
        check = check.replace(oldroot,root).replace('267','275')
        check = check.replace('[ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET]]', '[ppropertyslot_rootpad[.STATE = PROP_UNSET],ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET]]')
        check = check.replace('pinstancestorage_root.NEXT = 1','pinstancestorage_root.NEXT = 2')
        if '.STORE[n_called]' in check:
            checks += [check.replace('n_called','n_set'),check.replace('n_called','n_get')]
        else: checks.append(check)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(peer.__file__), Path(header.__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php', 'frontend/SourcePrinter.php',
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
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
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
