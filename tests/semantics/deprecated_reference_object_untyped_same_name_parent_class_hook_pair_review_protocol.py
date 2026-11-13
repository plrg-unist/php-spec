#!/usr/bin/env python3
"""Check same-name parent pairs, child-slot identity and ordered cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_parented_class_hook_pair_review_protocol as parented
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_same_name_parent_class_hook_pair_review')
base = parented.base
actual_pair = parented.actual_pair
sha = parented.sha


def fields(fixture, source, actual):
    form = 'Actual' if actual else 'Implicit'
    old = 'Ns287ParentedClass' + form + 'PairPeer' + chr(92)
    new = 'Ns288SameNameParentClass' + form + 'PairPeer' + chr(92)
    checks = []
    for check in parented.fields(fixture, source, actual):
        if check.startswith(('U = ', 'S_start = ')):
            checks.append(check)
            continue
        for name in ('Root', 'Parent'):
            check = check.replace(base.quoted(old + name + '287'), base.quoted(new + name + '288'))
        check = check.replace('287', '288')
        check = check.replace('pclassdesc_parent.PROPERTIES = [ppropertydesc_anchor]',
                              'pclassdesc_parent.PROPERTIES = [ppropertydesc_anchor,ppropertydesc_parentpad]')
        check = check.replace('$property_info_layout(S_raw,porigin_parent,|S_raw.CLASSES|) = [ppropertydesc_anchor]',
                              '$property_info_layout(S_raw,porigin_parent,|S_raw.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_parentpad]')
        check = check.replace('$property_hook_pair_plain_parent(S_raw,[ppropertydesc_anchor])',
                              '$property_hook_pair_plain_parent(S_raw,[ppropertydesc_anchor,ppropertydesc_parentpad])')
        check = check.replace('$ppproperty_desc_at([ppropertydesc_anchor],$ptascii("pad")) = eps',
                              '$ppproperty_desc_at([ppropertydesc_anchor,ppropertydesc_parentpad],$ptascii("pad")) = (ppropertydesc_parentpad)')
        check = check.replace('$property_hook_parent_overlap(S_functions,pclassdesc_root.PROPERTIES,[ppropertydesc_anchor])',
                              '$property_hook_parent_overlap(S_functions,pclassdesc_root.PROPERTIES,[ppropertydesc_anchor,ppropertydesc_parentpad])')
        checks.append(check)
    at = checks.index('S_step = $drive_steps(S_raw,1)')
    checks[at:at] = [
        'ppropertydesc_parentpad.NAME = $ptascii("pad")', 'ppropertydesc_parentpad.KEY = ppropertydesc_parentpad.NAME',
        'ppropertydesc_parentpad.TYPE = eps', 'ppropertydesc_parentpad.VISIBILITY = PROPERTY_PUBLIC',
        'ppropertydesc_parentpad.SETVISIBILITY = eps', '~ppropertydesc_parentpad.STATIC',
        '~ppropertydesc_parentpad.READONLY', '~ppropertydesc_parentpad.FINAL',
        'ppropertydesc_parentpad.ORIGIN = PORIGIN n_source pcpath_parentpad',
        '$property_declaring_class(S_raw.CLASSES,PORIGIN n_source pcpath_parentpad) = (porigin_parent)',
        '$property_default_state(S_raw,ppropertydesc_parentpad) = (PROP_VALUE (DIRECT (PINT 99)))',
        '$property_default_state(S_raw,ppropertydesc_rootpad) = (PROP_VALUE (DIRECT PNULL))',
        '$property_hook_reference_plain_parent(S_raw,ppropertydesc_parentpad,ppropertydesc_rootpad)',
        '$property_hook_child_own_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_rootpad)',
        '$property_layout_parent(S_raw,[ppropertydesc_anchor,ppropertydesc_parentpad],pclassdesc_root.PROPERTIES) = [ppropertydesc_anchor]',
        '$property_hook_pair_over_ordinary(S_functions,ppropertydesc_parentpad,ppropertydesc_rootpad)',
        '~$property_hook_parent_match(S_functions,ppropertydesc_rootpad,(ppropertydesc_parentpad))',
        '~$property_hook_child_own_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_middlepad)',
        '$property_layout_parent(S_raw,[ppropertydesc_anchor,ppropertydesc_parentpad],[ppropertydesc_middlepad]) = [ppropertydesc_anchor,ppropertydesc_parentpad]',
        '~$property_hook_child_own_slot(S_raw,ppropertydesc_rootpad,ppropertydesc_middlepad)',
        '$property_layout_parent(S_raw,[ppropertydesc_rootpad],[ppropertydesc_middlepad]) = [ppropertydesc_rootpad]',
        '~$property_hook_child_own_slot(S_raw,ppropertydesc_parentpad,ppropertydesc_rootpad[.TYPE = [(PTBRANCH ([PTBUILTIN "int"]))]])',
        'statement_virtual = NStmtProperty phpType14_group phpType24_group ABSENT phpType56_group (SEQUENCE ([phpType38_get])) metadata_group',
        'S_virtual = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_group statement_virtual) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_own_slot(S_virtual,ppropertydesc_parentpad,ppropertydesc_rootpad)',
        '$property_layout_parent(S_virtual,[ppropertydesc_anchor,ppropertydesc_parentpad],pclassdesc_root.PROPERTIES) = [ppropertydesc_anchor,ppropertydesc_parentpad]',
        'pclassdesc_parented = pclassdesc_parent[.PARENT = (pclassdesc_root.NAME)]',
        'S_parented = S_class[.CLASSES = [pclassdesc_root,pclassdesc_parented]]',
        '~$property_hook_child_own_slot(S_parented,ppropertydesc_parentpad,ppropertydesc_rootpad)',
        '$property_layout_parent(S_parented,[ppropertydesc_anchor,ppropertydesc_parentpad],pclassdesc_root.PROPERTIES) = [ppropertydesc_anchor,ppropertydesc_parentpad]',
        'pclassdesc_parent.ORIGIN = PORIGIN n_source pcpath_parent',
        '$origin_node(S_class.SOURCES,pclassdesc_parent.ORIGIN) = (NStmtClass phpType14_parent phpType24_parent phpType3_parent ABSENT phpType42_parent phpType23_parent metadata_parent)',
        '$origin_node(S_class.SOURCES,pclassdesc_root.ORIGIN) = (NStmtClass phpType14_root phpType24_root phpType3_root phpType44_root phpType42_root phpType23_root metadata_root)',
        'phpType44_root =/= ABSENT',
        'statement_parented = NStmtClass phpType14_parent phpType24_parent phpType3_parent phpType44_root phpType42_parent phpType23_parent metadata_parent',
        'S_parent_header = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE pcpath_parent statement_parented) :: pcunit.OCCURRENCES]]]',
        '~$property_hook_child_own_slot(S_parent_header,ppropertydesc_parentpad,ppropertydesc_rootpad)',
        '$property_layout_parent(S_parent_header,[ppropertydesc_anchor,ppropertydesc_parentpad],pclassdesc_root.PROPERTIES) = [ppropertydesc_anchor,ppropertydesc_parentpad]',
        'ppropertyslot_parentpad = ppropertyslot_rootpad[.DECL = (ppropertydesc_parentpad.ORIGIN)]',
        '$property_slot_descriptor(S_raw,n_receiver,ppropertyslot_parentpad) = eps',
        'S_parent_slot = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_receiver,[ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_parentpad])]',
        '~$class_constant_reference_object_graph(S_parent_slot,n_receiver,eps)',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit', 'actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('same-name-parent-class-' + args.form + '-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(parented.__file__), Path(base.__file__), Path(parented.automatic.__file__),
             Path(actual_pair.__file__), Path(actual_pair.implicit.__file__), Path(actual_pair.block.__file__),
             Path(actual_pair.pair.__file__), Path(actual_pair.peer.__file__), Path(actual_pair.header.__file__), source, *modules,
             *(ROOT / p for p in ('spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
                 'frontend/SourcePrinter.php', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
                 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
                 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
                 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
                 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'form': args.form,
              'mode': 'fixture-SL', 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'], source, args.form == 'actual'); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(parented.PREFIX + parented.SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
                                           + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                                      *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
                            and not report['process']['group_after'] and report['stdout'] == 'true\n'
                            and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:4000]
    print('pass', args.form, report['premises'])


if __name__ == '__main__': main()
