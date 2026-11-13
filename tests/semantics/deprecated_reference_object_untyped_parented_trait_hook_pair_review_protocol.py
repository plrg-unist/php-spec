#!/usr/bin/env python3
"""Check linked-parent trait pairs, inherited storage and shared outside cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_trait_hook_pair_review_protocol as base
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_parented_trait_hook_pair_review')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PREFIX = base.PREFIX.replace('280', '281')
SELECTED = base.SELECTED.replace('B|Q|C|D|', 'B|Q|C|R|D|')
assert SELECTED.count('pinstancestorage.NEXT = 3') == 1
SELECTED = SELECTED.replace('pinstancestorage.NEXT = 3', 'pinstancestorage.NEXT = 4')


def fields(fixture, source, actual):
    form = 'Actual' if actual else 'Implicit'
    old = 'Ns280UntypedTrait' + form + 'PairPeer' + chr(92)
    new = 'Ns281ParentedTrait' + form + 'PairPeer' + chr(92)
    parent = base.quoted(new + 'Parent281')
    checks = []
    for check in base.fields(fixture, source, actual):
        if check.startswith('U = '):
            checks.append(check)
            continue
        for name in ('Root', 'RootPad'):
            check = check.replace(base.quoted(old + name + '280'), base.quoted(new + name + '281'))
        check = check.replace('280', '281').replace('B|Q|C|D|', 'B|Q|C|R|D|')
        check = check.replace('$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_rootpad])',
                              '$objectprops_at(S_raw.OBJECTPROPS,n_receiver) = ([ppropertyslot_anchor,ppropertyslot_middle,ppropertyslot_tail,ppropertyslot_rootpad])')
        check = check.replace('pinstancestorage_root.NEXT = 1', 'pinstancestorage_root.NEXT = 2')
        check = check.replace('[ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET]]',
                              '[ppropertyslot_anchor[.STATE = PROP_UNSET],ppropertyslot_middle[.STATE = PROP_UNSET],ppropertyslot_tail[.STATE = PROP_UNSET],ppropertyslot_rootpad[.STATE = PROP_UNSET]]')
        if check == 'pclassdesc_root.PARENT = eps':
            checks += [
                'pclassdesc_root.PARENT = (ptbytes_parent)', 'ptbytes_parent = ' + parent,
                '$class_named(S_raw.CLASSNAMES,$ptlc(ptbytes_parent)) = (porigin_parent)',
                '$class_at(S_raw.CLASSES,porigin_parent) = (pclassdesc_parent)',
                'pclassdesc_parent.NAME = ptbytes_parent', 'pclassdesc_parent.PARENT = eps',
                'pclassdesc_parent.KIND = "class"', '~pclassdesc_parent.READONLY',
                'pclassdesc_parent.METHODS = eps', 'pclassdesc_parent.PROPERTIES = [ppropertydesc_anchor]',
                '$class_link_at(S_raw.LINKEDPARENTS,porigin_root) = (SOURCE_PARENT porigin_parent)',
                '$property_hook_pair_source_headers(S_raw,pclassdesc_root,pclassdesc_parent)',
                '$property_hook_pair_plain_parent(S_raw,pclassdesc_parent.PROPERTIES)',
                '$ppproperty_desc_at($property_info_layout(S_raw,porigin_parent,|S_raw.CLASSES|),$ptascii("pad")) = eps',
                '$property_hook_pair_parent(S_raw,pclassdesc_root,$ptascii("pad"))',
                '$property_hook_pair_linked(S_raw,pclassdesc_root,$ptascii("pad"))',
                '$property_slot_descriptor(S_raw,n_receiver,ppropertyslot_anchor) = (ppropertydesc_anchor)',
                'ppropertyslot_anchor.DECL = (ppropertydesc_anchor.ORIGIN)',
                'ppropertyslot_anchor.NAME = $ptascii("anchor")',
                'ppropertyslot_anchor.STATE = PROP_VALUE (DIRECT (PINT 31))',
                'ppropertydesc_anchor.NAME = $ptascii("anchor")',
                'ppropertydesc_anchor.KEY = ppropertydesc_anchor.NAME', 'ppropertydesc_anchor.TYPE = eps',
                'ppropertydesc_anchor.VISIBILITY = PROPERTY_PUBLIC', 'ppropertydesc_anchor.SETVISIBILITY = eps',
                '~ppropertydesc_anchor.STATIC', '~ppropertydesc_anchor.READONLY', '~ppropertydesc_anchor.FINAL',
                'ppropertydesc_anchor.DEFAULT = PROP_STORED porigin_default_anchor',
                '~$property_hook_source_declared(S_raw,ppropertydesc_anchor)',
                '$class_constant_reference_object_field_type(S_raw,ppropertydesc_anchor,ppropertyslot_anchor)',
                '$property_slot_release_job(S_raw,n_receiver,ppropertyslot_anchor) = eps',
            ]
            continue
        checks.append(check)
    at = checks.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)')
    checks[at:at] = [
        '$property_layout(S_class,porigin_root,|S_class.CLASSES|) = [ppropertydesc_anchor,ppropertydesc_middle,ppropertydesc_tail,ppropertydesc_rootpad]',
        'S_no_link = S_class[.LINKEDPARENTS = eps]',
        '$property_hook_pair_sources(S_no_link,pclassdesc_root,ppropertydesc_source) = [(pclassdesc_trait,ppropertydesc_source)]',
        '~$property_hook_pair_linked(S_no_link,pclassdesc_root,ppropertydesc_source.NAME)',
        '$property_hook_trait_pair_functions(S_no_link,ppropertydesc_rootpad) = eps',
        'S_wrong_link = S_class[.LINKEDPARENTS = [CLASSLINK porigin_root (SOURCE_PARENT porigin_trait)]]',
        '$property_hook_trait_pair_functions(S_wrong_link,ppropertydesc_rootpad) = eps',
        'S_noncanonical = S_class[.SOURCES = [pcunit[.OCCURRENCES = eps]]]',
        '~$property_hook_pair_source_headers(S_noncanonical,pclassdesc_root,pclassdesc_parent)',
        '$property_hook_trait_pair_functions(S_noncanonical,ppropertydesc_rootpad) = eps',
    ]
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit', 'actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('parented-untyped-trait-' + args.form + '-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(base.__file__), Path(base.pair.__file__), Path(base.peer.__file__),
             Path(base.header.__file__), source, *modules, *(ROOT / p for p in (
                 'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
                 'frontend/SourcePrinter.php', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
                 'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
                 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
                 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
                 '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
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
