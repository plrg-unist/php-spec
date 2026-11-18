#!/usr/bin/env python3
"""Independent relative-self qualifier, scope and exact promotion controls."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import self_parentless_short_reference_get_hook_review_protocol as prior
from error_handler_run import recorded

ROOT = Path(__file__).resolve().parents[2]
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()


def assertions():
    rows = []
    # Reuse the established constructors while exercising the new qualifier.
    keywords = (b'self', b'SeLf', b'SELF', b'parent', b'static', b'int', b'array', b'iterable', b'callable')
    for original in prior.assertions():
        if original['id'].startswith('promoted-old323-NName-'):
            continue
        row = dict(original)
        for keyword in keywords:
            ordinary = prior.names.raw(keyword)
            relative = prior.names.raw(keyword, 'NNameRelative')
            row['premise'] = row['premise'].replace(ordinary, relative)
        if row['id'] == 'other-raw-kind-NNameRelative':
            row.update({'id': 'promoted-old341-relative-self', 'expected': True,
                        'premise': row['premise'].removeprefix('~')})
        if row['id'] == 'other-keyword-parent':
            owner_mask = ',' + prior.names.mask(b'Def341\\Box341') + ','
            assert row['premise'].count(owner_mask) == 1
            row['premise'] = row['premise'].replace(owner_mask, ',' + prior.names.mask(b'Def341\\Parent341') + ',')
        rows.append(row)
    for nullable in (False, True):
        rows.append({'id': 'promoted-old323-NNameRelative-' + str(nullable), 'expected': True,
            'premise': '$hook_short_reference_scoped_header(' + prior.names.raw(b'SeLf', 'NNameRelative', nullable)
                       + ',' + prior.names.mask(b'Def323\\Box323', nullable) + ',' + prior.names.context() + ')'})
    owner = b'Box342Global'
    for label, namespace, nullable in (('global-single', b'', False), ('global-nullable', b'', True),
                                     ('global-owner-ignores-consumer-namespace', b'Consumer342', False)):
        rows.append({'id': label, 'expected': True,
            'premise': '$hook_short_reference_scoped_header(' + prior.names.raw(b'SeLf', 'NNameRelative', nullable)
                       + ',' + prior.names.mask(owner, nullable) + ','
                       + prior.context(namespace=namespace, owner=owner, file=b'original342.php') + ')'})
    assert len({row['id'] for row in rows}) == len(rows)
    assert sum(row['id'].startswith('promoted-old323-NNameRelative-') for row in rows) == 2
    assert sum(row['id'] == 'promoted-old341-relative-self' for row in rows) == 1
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(prior.__file__), Path(prior.names.__file__), ROOT / 'tests/semantics/error_handler_run.py',
             ROOT / 'spec/semantics/modules.json', ROOT / 'tests/semantics/_build/default/numeric_runner.exe', *modules]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'mode': 'fixture-SL',
              'source_agreement_credit': 0, 'native_observations': 0,
              'promoted_old323_queries': 2, 'promoted_old341_queries': 1, 'passed': False}
    try:
        rows = assertions(); report['premises'] = len(rows)
        (out / 'assertions.json').write_text(json.dumps(rows, indent=2) + '\n')
        fixture = out / 'protocol.watsup'
        fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + row['premise'] + '\n' for row in rows))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(fixture)], out / 'check', 60)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
                            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed'], report.get('stderr', '')[:2000]
    print('pass', report['premises'], 'independent relative-self header assertions, source0')


if __name__ == '__main__':
    main()
