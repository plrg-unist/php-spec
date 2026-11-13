#!/usr/bin/env python3
"""Check own parented pairs, authenticated plain layout and ordered cleanup."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_set_backed_class_hook_pair_review_protocol as base
import deprecated_reference_object_untyped_automatic_short_set_class_hook_pair_review_protocol as automatic
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_parented_class_hook_pair_review')
sha = base.sha
actual_pair = base.actual_pair
PREFIX = base.PREFIX
SELECTED = base.SELECTED


def fields(fixture, source, actual):
    form = 'Actual' if actual else 'Implicit'
    old = ('Ns285SetBackedClass' if actual else 'Ns286AutomaticShortSetClass') + form + 'PairPeer' + chr(92) + ('Root285' if actual else 'Root286')
    new = 'Ns287ParentedClass' + form + 'PairPeer' + chr(92)
    source_fields = base.fields if actual else automatic.fields
    checks = []
    for check in source_fields(fixture, source, actual):
        if check.startswith('U = '):
            checks.append(check)
            continue
        check = check.replace(base.quoted(old), base.quoted(new + 'Root287'))
        check = check.replace('285' if actual else '286', '287')
        if check == 'pclassdesc_root.PARENT = eps':
            checks += [
                'pclassdesc_root.PARENT = (ptbytes_parent)',
                'ptbytes_parent = ' + base.quoted(new + 'Parent287'),
                '$class_named(S_raw.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
                '$class_at(S_raw.CLASSES,porigin_parent) = (pclassdesc_parent)',
                'pclassdesc_parent.NAME = ptbytes_parent', 'pclassdesc_parent.KIND = "class"',
                'pclassdesc_parent.PARENT = eps', '~pclassdesc_parent.READONLY',
                'pclassdesc_parent.METHODS = eps', 'pclassdesc_parent.PROPERTIES = [ppropertydesc_anchor]',
                '$trait_plan(S_raw,pclassdesc_parent).TRAITS = eps',
                '$class_link_at(S_raw.LINKEDPARENTS,porigin_root) = (SOURCE_PARENT porigin_parent)',
                '$property_hook_pair_source_headers(S_raw,pclassdesc_root,pclassdesc_parent)',
                '$property_info_layout(S_raw,porigin_parent,|S_raw.CLASSES|) = [ppropertydesc_anchor]',
                '$property_hook_pair_plain_parent(S_raw,[ppropertydesc_anchor])',
                '$ppproperty_desc_at([ppropertydesc_anchor],$ptascii("pad")) = eps',
                '$property_hook_pair_parent(S_raw,pclassdesc_root,$ptascii("pad"))',
                '$property_hook_pair_linked(S_raw,pclassdesc_root,$ptascii("pad"))',
            ]
            continue
        check = check.replace('pclassdesc_root.PROPERTIES = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_rootpad]',
                              'pclassdesc_root.PROPERTIES = [ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_rootpad]')
        checks.append(check)
    at = checks.index('S_step = $drive_steps(S_raw,1)')
    checks[at:at] = [
        'ppropertydesc_anchor.ORIGIN = PORIGIN n_anchor pcpath_anchor',
        '$property_declaring_class(S_raw.CLASSES,PORIGIN n_anchor pcpath_anchor) = (porigin_parent)',
        'ppropertydesc_anchor.DEFAULT = PROP_STORED porigin_default_anchor',
        '$property_slot_release_job(S_raw,n_receiver,ppropertyslot_anchor) = eps',
        '$property_layout(S_raw,porigin_root,|S_raw.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_rootpad]',
        '$property_info_layout(S_raw,porigin_root,|S_raw.CLASSES|) = [ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_rootpad,ppropertydesc_anchor]',
        '~$property_hook_pair_plain_parent(S_functions,[ppropertydesc_rootpad])',
        '$property_hook_pair_own_parented(S_functions,ppropertydesc_rootpad)',
        '~$property_hook_pair_own_parented(S_functions,ppropertydesc_anchor)',
        '~$property_hook_parent_match(S_functions,ppropertydesc_rootpad,eps)',
        '~$property_hook_parent_overlap(S_functions,pclassdesc_root.PROPERTIES,[ppropertydesc_anchor])',
        'S_no_link = S_class[.LINKEDPARENTS = eps]',
        '~$property_hook_pair_linked(S_no_link,pclassdesc_root,$ptascii("pad"))',
        '~$property_hook_pair_own_parented(S_no_link,ppropertydesc_rootpad)',
        '$property_hook_pair_origins(S_no_link,ppropertydesc_rootpad) = eps',
        '~$class_constant_reference_object_graph(S_no_link,n_receiver,eps)',
        'S_wrong_link = S_class[.LINKEDPARENTS = [CLASSLINK porigin_root (SOURCE_PARENT porigin_leaf)]]',
        '$property_hook_pair_origins(S_wrong_link,ppropertydesc_rootpad) = eps',
        '~$class_constant_reference_object_graph(S_wrong_link,n_receiver,eps)',
        'S_no_names = S_class[.CLASSNAMES = eps]',
        '~$property_hook_pair_parent(S_no_names,pclassdesc_root,$ptascii("pad"))',
        '$property_hook_pair_origins(S_no_names,ppropertydesc_rootpad) = eps',
        'S_no_file = S_class[.FILES = eps]',
        '~$property_hook_pair_source_headers(S_no_file,pclassdesc_root,pclassdesc_parent)',
        '$property_hook_pair_origins(S_no_file,ppropertydesc_rootpad) = eps',
        'S_noncanonical = S_class[.SOURCES = [pcunit[.OCCURRENCES = eps]]]',
        '~$property_hook_pair_source_headers(S_noncanonical,pclassdesc_root,pclassdesc_parent)',
        '$property_hook_pair_origins(S_noncanonical,ppropertydesc_rootpad) = eps',
        'pclassdesc_bad_parent = pclassdesc_parent[.NAME = $ptascii("Forged287")]',
        'S_parent_name = S_class[.CLASSES = [pclassdesc_root,pclassdesc_bad_parent]]',
        '~$property_hook_pair_source_headers(S_parent_name,pclassdesc_root,pclassdesc_bad_parent)',
        '$property_hook_pair_origins(S_parent_name,ppropertydesc_rootpad) = eps',
        'pclassdesc_bad_child = pclassdesc_root[.FINAL = true]',
        'S_child_header = S_class[.CLASSES = [pclassdesc_bad_child,pclassdesc_parent]]',
        '~$property_hook_pair_source_headers(S_child_header,pclassdesc_bad_child,pclassdesc_parent)',
        '$property_hook_pair_origins(S_child_header,ppropertydesc_rootpad) = eps',
        'pclassdesc_same_name = pclassdesc_parent[.PROPERTIES = [ppropertydesc_anchor[.NAME = $ptascii("pad")][.KEY = $ptascii("pad")]]]',
        'S_same_name = S_class[.CLASSES = [pclassdesc_root,pclassdesc_same_name]]',
        '$property_hook_pair_source_headers(S_same_name,pclassdesc_root,pclassdesc_same_name)',
        '~$property_hook_pair_parent(S_same_name,pclassdesc_root,$ptascii("pad"))',
        '$property_hook_pair_origins(S_same_name,ppropertydesc_rootpad) = eps',
        'ppropertyslot_bad_decl = ppropertyslot_anchor[.DECL = (ppropertydesc_rootpad.ORIGIN)]',
        '$property_slot_descriptor(S_raw,n_receiver,ppropertyslot_bad_decl) = eps',
        'S_bad_slots = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_receiver,[ppropertyslot_bad_decl,ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_rootpad])]',
        '~$class_constant_reference_object_graph(S_bad_slots,n_receiver,eps)',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit', 'actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('parented-untyped-class-' + args.form + '-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(base.__file__), Path(automatic.__file__), Path(actual_pair.__file__), Path(actual_pair.implicit.__file__), Path(actual_pair.block.__file__),
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
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n'
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
