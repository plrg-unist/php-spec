#!/usr/bin/env python3
"""Check repeated raw-trait deduplication and shared outside cleanup."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_parented_trait_hook_pair_review_protocol as base
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('deprecated_reference_object_untyped_repeated_trait_hook_pair_review')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
PREFIX = base.PREFIX.replace('281', '282')
SELECTED = base.SELECTED


def fields(fixture, source, actual):
    form = 'Actual' if actual else 'Implicit'
    old = 'Ns281ParentedTrait' + form + 'PairPeer' + chr(92)
    new = 'Ns282RepeatedTrait' + form + 'PairPeer' + chr(92)
    quoted = base.base.quoted
    checks = []
    for check in base.fields(fixture, source, actual):
        if check.startswith('U = '):
            checks.append(check)
            continue
        for name in ('Root', 'RootPad', 'Parent'):
            check = check.replace(quoted(old + name + '281'), quoted(new + name + '282'))
        check = check.replace('281', '282')
        check = check.replace('{TRAITS ([pclassdesc_trait.NAME]), PRECEDENCES eps, ALIASES eps}',
                              '{TRAITS ([pclassdesc_trait.NAME,pclassdesc_trait.NAME]), PRECEDENCES eps, ALIASES eps}')
        if not actual:
            check = check.replace('statement_use = NStmtTraitUse (SEQUENCE ([name_trait]))',
                                  'statement_use = NStmtTraitUse (SEQUENCE ([name_trait,name_repeat]))')
            check = check.replace('(SEQUENCE (statement_use :: statement_trait*))',
                                  '(SEQUENCE ((NStmtTraitUse (SEQUENCE ([name_trait])) (SEQUENCE eps) metadata_use) :: statement_trait*))')
        checks.append(check)
    # Fresh canonical originals prove repetition; this old derived unit is noncanonical.
    start = next(i for i, c in enumerate(checks) if c.startswith('pcnode_duplicate = '))
    end = next(i for i, c in enumerate(checks) if c.startswith('pcnode_adapted = '))
    del checks[start:end]
    checks = [c for c in checks if 'S_duplicate' not in c]
    at = next(i for i, c in enumerate(checks) if c.startswith('statement_use = '))
    resolved = ['$trait_name(pcode_unit,pcpath_root ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 0]) = pclassdesc_trait.NAME']
    if actual:
        resolved += [
            'statement_root_tail* = statement_repeat :: statement_after_uses*',
            'statement_repeat = NStmtTraitUse (SEQUENCE ([name_alias])) (SEQUENCE eps) metadata_repeat',
            '$trait_name(pcode_unit,pcpath_root ++ [PCFIELD 5,PCINDEX 1,PCFIELD 0,PCINDEX 0]) = pclassdesc_trait.NAME',
        ]
    else:
        resolved += ['$trait_name(pcode_unit,pcpath_root ++ [PCFIELD 5,PCINDEX 0,PCFIELD 0,PCINDEX 1]) = pclassdesc_trait.NAME']
    checks[at + 1:at + 1] = resolved
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--form', required=True, choices=['implicit', 'actual'])
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    source = SOURCES / ('repeated-untyped-trait-actual-alias-pair-shared.php' if args.form == 'actual' else 'repeated-untyped-trait-implicit-pair-shared.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(base.__file__), Path(base.base.__file__), Path(base.base.pair.__file__),
             Path(base.base.peer.__file__), Path(base.base.header.__file__), source, *modules, *(ROOT / p for p in (
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
