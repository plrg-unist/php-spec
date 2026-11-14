#!/usr/bin/env python3
"""Independent exact qualified targets, relative fences and ancestry controls."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_runtime_scalar_named_instanceof_special_concat_leading_key_review_state as prior
import string_offset_request_base_runtime_scalar_qualified_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_scalar_qualified_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
prior.source = source


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    guards = []
    if index == 0:
        for tag, tree in prior.links(source.TREES[index]):
            if tree[0] != 'INSTANCEOF':
                continue
            origin, target = 'porigin_' + tag, 'pcpath_peer_instanceof_' + tag
            for number, (constructor, text) in enumerate((('NNameFullyQualified', 'SeLf'),
                                                         ('NNameFullyQualified', 'PaReNt'),
                                                         ('NNameFullyQualified', 'STATIC'),
                                                         ('NName', '\\Target'), ('NNameFullyQualified', '\\Target'),
                                                         ('NName', 'A\\'), ('NNameFullyQualified', 'A\\\\B'),
                                                         ('NNameFullyQualified', 'A\0B'))):
                name = constructor + ' (BYTES ' + json.dumps(base64.b64encode(text.encode()).decode()) + ') eps'
                node = 'NExprInstanceof expression_' + tag + '_0 (' + name + ') eps'
                state = 'S_peer_qualified_' + str(number)
                guards += [state + ' = S_after[.SOURCES[0] = pcunit_peer_instanceof[.OCCURRENCES = (PCOCCURRENCE ' + target + ' (' + node + ')) :: (PCOCCURRENCE ' + target + '_name (' + name + ')) :: pcunit_peer_instanceof.OCCURRENCES]][.CODE[0] = pcode_peer_instanceof[.NAMES = (CODENAME ' + target + ' (' + str(list(text.encode())) + ') eps) :: pcode_peer_instanceof.NAMES]]',
                           '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                           '$string_read_runtime_bytes(' + state + ', porigin_key) = eps']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    true = '(!0.0)'
    selected = lambda value: '(' + true + '?' + value + ':(1/0))'
    raw = [
        ('fqn_global', '', true, '\\stdClass', True),
        ('fqn_nested', '', true, '\\Missing\\Deep\\Target', True),
        ('qualified_global', '', true, 'Missing\\Target', True),
        ('qualified_case', '', true, 'MiSsInG\\TaRgEt', True),
        ('fqn_namespace', 'namespace Ns;', true, '\\stdClass', True),
        ('qualified_namespace', 'namespace Ns;', true, 'Missing\\Target', True),
        ('relative_global', '', true, 'namespace\\Target', True),
        ('relative_namespace', 'namespace Ns;', true, 'namespace\\Target', True),
        ('renamed_import', 'namespace Ns;use Missing\\Target as Alias;', true, 'Alias', True),
        ('renamed_prefix', 'namespace Ns;use Other as Missing;', true, 'Missing\\Target', True),
        ('identity_prefix', 'namespace Ns;use Missing as Missing;', true, 'Missing\\Target', True),
        ('fqn_bypasses_import', 'namespace Ns;use Other as Missing;', true, '\\Missing\\Target', True),
        ('fqn_null', '', selected('null'), '\\Missing', True),
        ('qualified_float', '', selected('1.5'), 'Missing\\Target', True),
        ('qualified_string', '', selected('"x"'), 'Missing\\Target', True),
        ('fqn_object', '', selected('new stdClass'), '\\stdClass', False),
    ]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, prefix, operand, target, accepted in raw:
        paths[name].write_bytes(('<?php ' + prefix + '$x=(' + operand + ') instanceof ' + target + ';\n').encode())
    root = runner.ROOT
    profile = json.loads((root / 'tests/semantics/profile.json').read_bytes())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = runner.Worker([str(root / '.tools/php/bin/php'), '-n', *flags, '-d', 'extension=' + str(root / '.tools/php-file.so'), str(root / 'frontend/worker.php')], prep / 'frontend')
    try:
        parsed = {name: frontend.request({'op': 'parse', 'source': base64.b64encode(path.read_bytes()).decode()}) for name, path in paths.items()}
        assert all(row['accepted'] for row in parsed.values())
    finally:
        frontend.close()
    adapter = runner.Worker([str(root / '_build/default/adapter/main.exe'), str(root)], prep / 'adapter')
    try:
        checked = {name: adapter.request({'op': 'check', 'ast': row['ast'], 'fixture': True}) for name, row in parsed.items()}
        assert all(row['ok'] for row in checked.values())
    finally:
        adapter.close()
    for name, prefix, operand, target_name, accepted in raw:
        targets = [(path, node) for index, statement in enumerate(parsed[name]['ast']['program'])
                   for path, node in occurrences.expected(statement, [('INDEX', index)]) if node['node'] == 'Expr_Instanceof']
        target, node = min(targets, key=lambda item: len(item[0]))
        prior.CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, accepted))
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parent} | set(paths.values())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += prior.helpers.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    assert report['mode'] == 'fixture SL'
    report['scope'] = 'Current4 histories retain exact source/name/CODE/line/read/precision, scalar/nonNaN/full-state and owner guards through the maintained named reviewer. Only coherent qualified/FQN direct VALUE promotes; unmodified ancestor ASTs still refuse outer VALUE/BYTE/saved receipts, and occurrence-only relative mutations remain refused. Sixteen checked-source source0 controls cover global/nested/case-preserved names, authenticated namespace/relative/simple/prefix-import resolution, FQN namespace/import bypass, admitted same-byte prefix import, scalar NULL/FLOAT/STRING and owning-object refusal. Eight coherent FQN-keyword/leading/trailing/doubled-separator/NUL controls refuse. No old source/native campaign replay, duplicate class-lookup rule, compiler/formatter/owner changes or exact held-boundary expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
