#!/usr/bin/env python3
"""Reach genuine NULL backing through implicit GET/SET entry and resumption."""
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
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_implicit_default') / 'untyped-pair-implicit-default-execution.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PAUSE = pair.PAUSE.replace('275', '276')


def fields(fixture):
    pair.SOURCE = SOURCE
    old_name = pair.b64(b'Ns275UntypedPairExecution\\Box275')
    new_name = pair.b64(b'Ns276UntypedPairImplicitDefaultExecution\\Box276')
    checks = [check.replace(old_name, new_name).replace('275', '276')
        .replace('PROP_VALUE (DIRECT (PINT 17))', 'PROP_VALUE (DIRECT PNULL)')
        for check in pair.fields(fixture)]
    checks += ['ppropertydesc.DEFAULT = PROP_NULL',
        'ppropertydesc.ORIGIN = PORIGIN n_source pcpath_property',
        'pcpath_property = pcpath_group ++ [PCFIELD 3,PCINDEX 0]',
        '$origin_node(S_get.SOURCES,PORIGIN n_source pcpath_property) = (NPropertyItem (NVarLikeIdentifier (BYTES text_property) metadata_property_name) ABSENT metadata_property_item)',
        '$base64(text_property) = $ptascii("tag")',
        '$origin_node(S_get.SOURCES,PORIGIN n_source (pcpath_property ++ [PCFIELD 1])) = eps',
        '$pool_value(S_get.POOLS,PORIGIN n_source (pcpath_property ++ [PCFIELD 1])) = eps',
        '$property_default_state(S_get,ppropertydesc) = (PROP_VALUE (DIRECT PNULL))',
        '$property_hook_pair_backed(S_get,ppropertydesc)',
        '~$property_hook_virtual(S_get,ppropertydesc)',
        'pfunction_get.LINE = 5', 'pfunction_get.ENDLINE = 8',
        'pfunction_set.LINE = 9', 'pfunction_set.ENDLINE = 12',
        'S_get.OBJECTS[n_object] = INSTANCE porigin_owner',
        '$node_children(S_get,HOBJECT n_object) = eps',
        'P = $ppstart(n_source,U,$base64(' + json.dumps(pair.b64(bytes(SOURCE))) + '))',
        'P.COMPLETION = PPCNORMAL',
        '$class_at(P.CLASSES,porigin_owner) = (pclassdesc_compiler)',
        'pclassdesc_compiler.PROPERTIES = [ppropertydesc]',
        '$function_at(P.FUNCTIONS,porigin_get) = (pfunction_get_compiler)',
        '$function_at(P.FUNCTIONS,porigin_set) = (pfunction_set_compiler)',
        'pfunction_get_compiler.SIGNATURE = pfunction_get.SIGNATURE',
        'pfunction_set_compiler.SIGNATURE = pfunction_set.SIGNATURE',
        'pfunction_get_compiler.BODY = pfunction_get.BODY',
        'pfunction_set_compiler.BODY = pfunction_set.BODY',
        'PPCCONSTANTS (pcpath_constant,pvalue_constant)* = $ppconstants(P)',
        '$ppconstant_at((pcpath_constant,pvalue_constant)*,pcpath_property ++ [PCFIELD 1]) = eps']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(pair.__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': pair.b64(SOURCE.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(pair.PREFIX + pair.SELECTED + PAUSE + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
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
