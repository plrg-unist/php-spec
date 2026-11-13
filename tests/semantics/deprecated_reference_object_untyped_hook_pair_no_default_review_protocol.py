#!/usr/bin/env python3
"""Check omitted pair initializers, implicit NULL and later outside ownership."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_hook_pair_no_default_review') / 'nested-untyped-hook-pair-no-default-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = peer.quoted
PREFIX = pair.PREFIX
SELECTED = pair.SELECTED.replace('B|C|','B|Q|C|')


def fields(fixture):
    pair.SOURCE = SOURCE
    oldroot = quoted('Ns275UntypedHookPairPeer' + chr(92) + 'Root275')
    root = quoted('Ns276UntypedHookPairNoDefaultPeer' + chr(92) + 'Root276')
    checks = []
    for check in pair.fields(fixture):
        if check.startswith('U = '):
            checks.append(check); continue
        check = check.replace(oldroot,root).replace('275','276').replace('B|C|','B|Q|C|')
        check = check.replace('ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT (PBOOL false))',
            'ppropertyslot_rootpad.STATE = PROP_VALUE (DIRECT PNULL)')
        check = check.replace('ppropertydesc_rootpad.DEFAULT = PROP_STORED porigin_default',
            'ppropertydesc_rootpad.DEFAULT = PROP_NULL')
        checks.append(check)
    extra = ['$origin_node(S_class.SOURCES,PORIGIN n_source pcpath_property) = (NPropertyItem phpType40_name ABSENT metadata_item)',
        '$property_default_state(S_class,ppropertydesc_rootpad) = (PROP_VALUE (DIRECT PNULL))']
    for kind, default in [('uninitialized','PROP_UNINITIALIZED'), ('stored','PROP_STORED porigin_get')]:
        prop = 'ppropertydesc_default_' + kind; state = 'S_default_' + kind
        extra += [prop + ' = ppropertydesc_rootpad[.DEFAULT = ' + default + ']',
            state + ' = S_class[.CLASSES = $trait_class_set(S_class.CLASSES,pclassdesc_root[.PROPERTIES = [' + prop + ',ppropertydesc_middle,ppropertydesc_tail]])]',
            '$property_hook_pair_origins(' + state + ',' + prop + ') = eps',
            '~$class_constant_reference_object_graph(' + state + ',n_receiver,eps)']
    for name, value in [('bool','PBOOL true'), ('int','PINT 23')]:
        state = 'S_live_' + name
        extra += [state + ' = S_class[.OBJECTPROPS = $objectprops_set(S_class.OBJECTPROPS,n_receiver,[ppropertyslot_rootpad[.STATE = PROP_VALUE (DIRECT (' + value + '))],ppropertyslot_middle,ppropertyslot_tail])]',
            '$property_hook_pair_origins(' + state + ',ppropertydesc_rootpad) = [porigin_get,porigin_set]',
            '$class_constant_reference_object_graph(' + state + ',n_receiver,eps)']
    at = checks.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)')
    checks[at:at] = extra
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(pair.__file__), Path(peer.__file__), Path(header.__file__), SOURCE, *modules, *(ROOT / p for p in (
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
