#!/usr/bin/env python3
"""Native-positive anonymous-owner source boundaries and promoted closures."""
import base64
import hashlib
import json
import os
from pathlib import Path
import tempfile

import typed_static_ini_prefix_protocol as cross
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
SOURCES = {
    'method-owned-closure': ('<?php\n$owner = new class { public function make() { $f = function() { return new class {}; }; return $f(); } };\n$owner->make(); echo "OK;";\n', b'OK;'),
    'method-owned-named-function': ('<?php\n$owner = new class { public function make() { function nested180() { return new class {}; } return nested180(); } };\n$owner->make(); echo "OK;";\n', b'OK;'),
    'method-owned-arrow': ('<?php\n$owner = new class { public function make() { $f = fn() => new class {}; return $f(); } };\n$owner->make(); echo "OK;";\n', b'OK;'),
    'tostring-body-child': ('<?php\n$owner = new class { public function __toString(): string { $child = new class { public function value(): string { return "MAGIC;"; } }; return $child->value(); } };\necho (string)$owner;\n', b'MAGIC;'),
    'class-constant-sibling': ('<?php\n$owner = new class { public const VALUE = 7; public function make() { return new class {}; } };\n$owner->make(); echo $owner::VALUE, ";";\n', b'7;'),
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    os.environ.update(LC_ALL='C', TZ='UTC', GIT_OPTIONAL_LOCKS='0')
    raw = Path(tempfile.mkdtemp(prefix='class180-boundaries-', dir=ROOT / '.tools'))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, ROOT / 'spec/semantics/modules.json', Path(__file__),
               ROOT / 'frontend/worker.php', ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe']
    before = {str(path): sha(path) for path in watched}
    report = {'passed': False, 'raw': str(raw), 'inputs_before': before, 'native': {}}
    frontend = adapter = None
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *cross.invoke.types.FLAGS,
                           '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], raw / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], raw / 'adapter')
        code, calls = '', []
        for index, (name, (source_text, expected)) in enumerate(SOURCES.items()):
            source = raw / (name + '.php')
            source.write_text(source_text)
            native = cross.invoke.process([str(ROOT / '.tools/php/bin/php'), '-n',
                                           *cross.invoke.types.FLAGS, str(source)], raw / ('native-' + name), 30, raw)
            report['native'][name] = {'source_sha256': sha(source), 'exit': native.returncode,
                                      'stdout_base64': base64.b64encode(native.stdout).decode(),
                                      'stderr_base64': base64.b64encode(native.stderr).decode()}
            assert native.returncode == 0 and native.stdout == expected and not native.stderr
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
            assert parsed['accepted'] is True
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'] is True
            filename = json.dumps(base64.b64encode(os.fsencode(source)).decode())
            group = '$owner180_boundary' + str(index)
            code += 'dec ' + group + '() : bool\ndef ' + group + '() = true\n'
            code += '  -- if P = $ppstart(0,' + checked['fixture'] + ',$base64(' + filename + '))\n'
            code += '  -- if $source_unit([P.FOLD.SOURCE],0) = (pcunit)\n'
            code += '  -- if $origin_node([pcunit],PORIGIN 0 ([PCINDEX 0,PCFIELD 0,PCFIELD 1,PCFIELD 0])) = (pcnode_owner)\n'
            code += '  -- if $anonymous_class_node(pcnode_owner)\n'
            promoted = name in ('method-owned-closure', 'method-owned-arrow')
            code += '  -- if ' + ('' if promoted else '~') + '$anonymous_owner_factory_node(pcnode_owner)\n'
            code += '  -- if ~$anonymous_no_classes($pcwalk($pcchildren(pcnode_owner,eps)))\n'
            code += '  -- if ' + ('' if promoted else '~') + '$anonymous_unit(pcunit)\n'
            calls.append(group + '()')
        fixture = raw / 'protocol.watsup'
        fixture.write_text(code + 'dec $main() : bool\ndef $main() = ' + r' /\ '.join(calls) + '\n')
        result = cross.invoke.process([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
                                       '--sl', *map(str, modules), str(fixture)], raw / 'numeric', 180, ROOT)
        report.update(exit=result.returncode, stdout=result.stdout.decode(errors='replace'),
                      stderr=result.stderr.decode(errors='replace'), fixture_sha256=sha(fixture),
                      conditions={name: 7 for name in SOURCES})
        report['passed'] = result.returncode == 0 and result.stdout == b'true\n' and not result.stderr
    finally:
        try:
            if adapter: adapter.close()
        finally:
            if frontend: frontend.close()
        report['inputs_after'] = {str(path): sha(path) for path in watched}
        report['passed'] = report['passed'] and before == report['inputs_after']
        (raw / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
        print(raw / 'report.json', report['passed'], flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
