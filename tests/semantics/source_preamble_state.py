#!/usr/bin/env python3
"""Checked source-reached tick plans for file preambles and an ordinary program."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import sys

from error_handler_run import recorded
from recorded_worker import Worker
import tick_sources

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source_preamble')


def b64(value):
    return base64.b64encode(value).decode()


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    output = Path(sys.argv[1]).resolve(); output.mkdir(parents=True, exist_ok=False)
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    flags = [piece for key, value in profile.items() for piece in ('-d', key + '=' + value)]
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    watched = [Path(__file__), ROOT / 'spec/semantics/393-ticks.watsup',
               ROOT / 'spec/semantics/modules.json', ROOT / 'frontend/worker.php',
               ROOT / '.tools/php-file.so', ROOT / '.tools/php/bin/php',
               ROOT / '_build/default/adapter/main.exe',
               ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
               ROOT / 'tests/semantics/profile.json', ROOT / 'tests/semantics/tick_sources.py',
               *(SOURCES / name for name in ('main-shebang.php', 'main-bom.php',
                                              'ticks-shebang.php', 'ticks-bom.php'))]
    inputs = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    report = {'revision': revision, 'inputs': inputs, 'profile': profile,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'premises': 0,
              'passed': False}
    try:
        frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
                           'extension=' + str(ROOT / '.tools/php-file.so'),
                           str(ROOT / 'frontend/worker.php')], output / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], output / 'adapter')
        fixtures = {}
        try:
            for name in ('main-shebang', 'main-bom', 'ticks-shebang', 'ticks-bom'):
                path = SOURCES / (name + '.php')
                encoded = b64(path.read_bytes()); identity = b64(bytes(path))
                parsed = frontend.request({'op': 'parse-file', 'id': '0', 'mode': 'file',
                    'profile': 'cli-raw-85', 'source': encoded, 'requested': identity,
                    'resolved': identity, 'opened': identity})
                assert parsed['accepted'] and parsed['source'] == encoded
                checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                fixtures[name] = checked['fixture']
                kind = 'ENCODEDPROGRAM' if name.endswith('shebang') else 'PROGRAM'
                assert fixtures[name].startswith('(' + kind + ' '), name
            program = tick_sources.CASES['straight'][0]
            parsed = frontend.request({'op': 'parse', 'source': b64(program)})
            assert parsed['accepted']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            fixtures['program'] = checked['fixture']
            assert fixtures['program'].startswith('(PROGRAM ')
        finally:
            adapter.close(); frontend.close()
        checks = []
        for name in ('main-shebang', 'main-bom', 'ticks-shebang', 'ticks-bom'):
            tag = name.replace('-', '_')
            checks += [f'W_{tag} = {fixtures[name]}',
                       f'T_{tag} = $tick_plan(W_{tag}, eps)',
                       f'T_{tag}.DEPENDENCY = eps']
            if name.endswith('shebang'):
                checks.append(f'$preamble_plan_matches(W_{tag})')
            checks += [f'T_{tag}.MARKERS {"=/=" if name.startswith("ticks") else "="} eps']
        checks += [
            '$tick_marker_at(T_ticks_shebang.MARKERS, [PCINDEX 1]) = (M_s1)',
            '$tick_marker_at(T_ticks_shebang.MARKERS, [PCINDEX 2]) = (M_s2)',
            '$tick_marker_at(T_ticks_shebang.MARKERS, [PCINDEX 3]) = (M_s3)',
            'M_s1.FREQUENCY = 1 /\\ M_s2.FREQUENCY = 1 /\\ M_s3.FREQUENCY = 1',
            'M_s1.LINE = 4 /\\ M_s2.LINE = 5 /\\ M_s3.LINE = 6',
            '$tick_marker_at(T_ticks_bom.MARKERS, [PCINDEX 2]) = (M_b1)',
            '$tick_marker_at(T_ticks_bom.MARKERS, [PCINDEX 3]) = (M_b2)',
            '$tick_marker_at(T_ticks_bom.MARKERS, [PCINDEX 4]) = (M_b3)',
            'M_b1.FREQUENCY = 1 /\\ M_b2.FREQUENCY = 1 /\\ M_b3.FREQUENCY = 1',
            'M_b1.LINE = 3 /\\ M_b2.LINE = 4 /\\ M_b3.LINE = 5',
        ]
        checks += [f'W_program = {fixtures["program"]}',
                   'T_program = $tick_plan(W_program, eps)',
                   'T_program.MARKERS =/= eps', 'T_program.DEPENDENCY = eps']
        fixture = output / 'state.watsup'
        variables = 'var W : program\nvar M : ptickmarker\n'
        fixture.write_text(variables + 'dec $preamble_plan_matches(program) : bool\n'
                           'def $preamble_plan_matches(ENCODEDPROGRAM text_1 text_2 text_3 text_4 text? statement*) = '
                           '($tick_plan(ENCODEDPROGRAM text_1 text_2 text_3 text_4 text? statement*, eps) = '
                           '$tick_plan(PROGRAM statement*, eps))\n'
                           'dec $main() : bool\ndef $main() = true\n' +
                           ''.join('  -- if ' + check + '\n' for check in checks))
        report['premises'] = len(checks)
        report['fixture_sha256'] = sha(fixture)
        modules = json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())
        command = [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
                   *[str(ROOT / name) for name in modules], str(fixture)]
        process = recorded(command, output / 'state', 150)
        report['process'] = process
        assert process['exit'] == 0 and not process['timeout'] and not process['group_after']
        assert (output / 'state.stdout').read_bytes() == b'true\n'
        assert (output / 'state.stderr').read_bytes() == b''
        report['passed'] = True
    finally:
        report['inputs_stable'] = inputs == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['head_stable'] = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['passed'] = report['passed'] and report['inputs_stable'] and report['head_stable']
        (output / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']


if __name__ == '__main__':
    main()
