#!/usr/bin/env python3
"""Independent canonical lexical authority and preserved raw-name trust."""
import base64
import hashlib
import json
from pathlib import Path
import sys

import source_occurrences as occurrences
import string_offset_request_base_runtime_scalar_qualified_instanceof_special_concat_leading_key_review_state as prior
import string_offset_request_base_runtime_scalar_resolved_instanceof_special_concat_leading_key_cases as cases
import string_offset_request_base_runtime_scalar_resolved_instanceof_special_concat_leading_key_protocol as source

runner = source.runner
prior.source = prior.prior.source = source


def conditions(program, path, index):
    checks, derived = prior.conditions(program, path, index)
    guards = []
    if index == 0:
        for tag, tree in prior.prior.links(source.TREES[index]):
            if tree[0] != 'INSTANCEOF':
                continue
            origin, target = 'porigin_' + tag, 'pcpath_peer_instanceof_' + tag
            name = 'name_' + tag
            requested, resolved = ('$ptascii(' + json.dumps(text) + ')' for text in (tree[2], tree[4]))
            guards += ['$string_read_runtime_named_target(S_after, ' + origin + ', ' + name + ', ' + resolved + ', 5)',
                       '$call_sourcefile(S_after.FILES, ' + origin + ') =/= eps']
            for number, replacement in enumerate(('S_after[.FILES = eps]',
                                                   'S_after[.FILES = [SOURCEFILE 0 eps]]',
                                                   'S_after[.SOURCES[0] = pcunit_peer_instanceof[.AST = PROGRAM eps]]',
                                                   'S_after[.SOURCES[0] = pcunit_peer_instanceof[.OCCURRENCES = pcunit_peer_instanceof.OCCURRENCES ++ [(PCOCCURRENCE ([(PCINDEX 12345)]) (NScalarInt (INTEGER 0) eps))]]]')):
                state = 'S_peer_resolved_' + str(number)
                guards += [state + ' = ' + replacement,
                           '~$string_read_runtime_named_target(' + state + ', ' + origin + ', ' + name + ', ' + resolved + ', 5)',
                           '$string_read_runtime_value(' + state + ', ' + origin + ') = eps',
                           '$string_read_runtime_bytes(' + state + ', porigin_key) = eps']
            fast = 'S_peer_resolved_fast'
            guards += [fast + ' = S_after[.FILES = eps][.CODE[0] = pcode_peer_instanceof[.NAMES = (CODENAME ' + target + ' (' + requested + ') eps) :: pcode_peer_instanceof.NAMES]]',
                       '$string_read_runtime_named_target(' + fast + ', ' + origin + ', ' + name + ', ' + requested + ', 5)',
                       '$string_read_runtime_value(' + fast + ', ' + origin + ') = (PBOOL false)']
    return checks + guards, derived + len(guards)


if __name__ == '__main__':
    output = Path(sys.argv[sys.argv.index('--output') + 1]).resolve()
    prep = output.with_name(output.name + '-control-prep')
    prep.mkdir(parents=True)
    true = '(!0.0)'
    selected = lambda value: '(' + true + '?' + value + ':(1/0))'
    raw = [
        ('namespace_simple', 'namespace Ns;', true, 'Target', True),
        ('namespace_qualified', 'namespace Ns;', true, 'Missing\\Target', True),
        ('namespace_relative', 'namespace Ns;', true, 'namespace\\Target', True),
        ('global_relative', '', true, 'namespace\\Target', True),
        ('alias_simple', 'use stdClass as Alias;', true, 'Alias', True),
        ('alias_case', 'use stdClass as Alias;', true, 'aLiAs', True),
        ('alias_prefix', 'namespace Ns;use Missing as Alias;', true, 'Alias\\Target', True),
        ('alias_prefix_case', 'namespace Ns;use Missing\\Deep as Alias;', true, 'aLiAs\\Target', True),
        ('group_alias', 'namespace Ns;use Missing\\{Target as Alias};', true, 'Alias', True),
        ('namespace_block', 'namespace Ns {', true, 'Target', True),
        ('namespace_resume', 'namespace A {use Wrong as Alias;$a=0;} namespace B {', true, 'Alias', True),
        ('alias_null', 'namespace Ns;use Missing as Alias;', selected('null'), 'Alias', True),
        ('alias_float', 'namespace Ns;use Missing as Alias;', selected('1.5'), 'Alias', True),
        ('alias_string', 'namespace Ns;use Missing as Alias;', selected('"x"'), 'Alias', True),
        ('alias_object', 'namespace Ns;use stdClass as Alias;', selected('new \\stdClass'), 'Alias', False),
        ('dynamic', 'namespace Ns;$left=' + true + ';', '$left', '$right', False),
    ]
    paths = {name: prep / (name + '.php') for name, *_ in raw}
    for name, prefix, operand, target, accepted in raw:
        closing = '}' if name in ('namespace_block', 'namespace_resume') else ''
        paths[name].write_bytes(('<?php ' + prefix + '$x=(' + operand + ') instanceof ' + target + ';' + closing + '\n').encode())
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
        prior.prior.CONTROLS.append((name, checked[name]['fixture'], paths[name], target, node, accepted))
    watched = {Path(module.__file__).resolve() for module in tuple(sys.modules.values()) if getattr(module, '__file__', None)
               and Path(module.__file__).resolve().parent == Path(__file__).resolve().parents[0]} | set(paths.values())
    before = {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    runner.PREFIX += prior.prior.helpers.HELPERS
    runner.cases, runner.OUTPUTS, runner.conditions = cases, tuple(cases.OUTPUTS.values()), conditions
    passed = runner.main()
    assert before == {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in watched}
    path = output / 'report.json'
    report = json.loads(path.read_bytes())
    report['inputs'].update(before)
    assert report['mode'] == 'fixture SL'
    report['scope'] = 'Fresh resolved current4 histories reuse maintained named/qualified guards without old campaign replay. Sixteen new checked-source source0 controls cover plain/qualified/relative namespaces, simple/prefix/case/group imports, braced namespace entry/reset, scalar NULL/FLOAT/STRING, owning-object and dynamic refusal. New lexical authority refuses absent/empty files and AST/occurrence noncanonical units while the previous raw-name equality route still admits matching CODE with absent file metadata. Occurrence-only coherent relative mutations remain refused; genuine earlier namespace/import/relative source-control expectations promote through this selection. Source/CODE/line/precision/scalar/nonNaN/full-state and REQUEST warning/throw/bounds/cleanup/budget fences remain. No fresh native observations, compiler/formatter/owner changes or exact held-boundary expansion.'
    path.write_text(json.dumps(report, indent=2) + '\n')
    raise SystemExit(0 if passed else 1)
