#!/usr/bin/env python3
"""Check absent source Params, implicit value signatures and trait release."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_trait_set_explicit_review_protocol as trait
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_trait_implicit_set_review') / 'nested-untyped-trait-implicit-set-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = trait.quoted


def fields(fixture):
    trait.SOURCE = SOURCE
    replacements = {quoted('Ns271UntypedTraitSetExplicitPeer' + chr(92) + name + '271'):
        quoted('Ns273UntypedTraitImplicitSetPeer' + chr(92) + name + '273') for name in ('Root', 'RootPad')}
    checks = []
    for check in trait.fields(fixture):
        if check.startswith('U = '):
            checks.append(check)
            continue
        if check.startswith(('phpType17_parameter = ', '$base64(text_parameter) = ',
            '$default_parameter_origin(S_raw,', '$default_parameter_line(S_raw,')) or 'S_parameter' in check:
            continue
        for old, new in replacements.items(): check = check.replace(old, new)
        check = check.replace('271', '273')
        check = check.replace('phpType16_hook = SEQUENCE ([phpType17_parameter])', 'phpType16_hook = SEQUENCE eps')
        check = check.replace('~$property_set_parameters(phpType16_hook)', '$property_set_parameters(phpType16_hook)')
        check = check.replace('= (phpType17_parameter)', '= eps')
        check = check.replace('psparam.NAME = $ptascii("traitValue273")', 'psparam.NAME = $ptascii("value")')
        if check.startswith('S_function_param = '):
            check = check.replace('psparam[.NAME = $ptascii("value")]', 'psparam[.NAME = $ptascii("wrong")]')
        checks.append(check)
    extra = ['~$property_set_untyped_parameters(phpType16_hook)',
        '$code_expression(pfunction_source.CODE.EXPRESSIONS,pcpath_hook ++ [PCFIELD 4,PCINDEX 0]) = eps',
        '$ptascii("value") <- pfunction_source.CVS',
        '~($ptascii("traitValue273") <- pfunction_source.CVS)']
    at = checks.index('S_class = $class_constant_selector(S_raw,expression_class,z)')
    checks[at:at] = extra
    assert not any('metadata_parameter' in c or 'phpType17_parameter' in c for c in checks)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(trait.__file__), Path(trait.peer.__file__), Path(trait.peer.block.__file__), SOURCE, *modules, *(ROOT / p for p in (
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
        (out / 'protocol.watsup').write_text(trait.peer.block.PREFIX + trait.peer.block.SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
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
