#!/usr/bin/env python3
"""Final source operand destruction retains genuine opcode and keyword traces."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

import error_handler_run as recorder

ROOT = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source-stringable-retirement')
CASES = {'regular': 'deferred-regular.php',
         'regular-multiline': 'deferred-regular-multiline.php',
         'regular-binary': 'deferred-regular-binary.php',
         'fast': 'deferred-compile-only.php', 'empty-eval': None,
         'once-skip': 'helper-skip-body.php', 'missing-include': 'helper-missing-file.php',
         'first-echo': 'first-echo-child.php', 'first-assignment': 'first-assignment-child.php',
         'first-eval': None, 'generator-source': 'generator-source-child.php',
         'expression-cv': 'cv-child.php', 'expression-property': 'property-child.php',
         'expression-call-property': 'call-property-child.php',
         'expression-generator': 'generator-expression-child.php',
         'expression-cycle-collection': 'generator-expression-child.php',
         'expression-cycle-direct': 'generator-expression-child.php'}

b64 = lambda value: base64.b64encode(value).decode()


def source_inputs(out, source, provider):
    header = out / 'startup.json'
    header.write_text(json.dumps({'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}) + '\n')
    arguments = ['--startup-ini', str(header)]
    if provider is not None:
        facts = out / 'files.json'
        entry = {'caller': b64(bytes(source)), 'requested': b64(bytes(provider)),
                 'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:')}
        if provider.name == 'helper-missing-file.php':
            assert not provider.exists()
            entry.update(status='missing', stream_error=b64(b'No such file or directory'))
        else:
            entry.update(status='opened', resolved=b64(bytes(provider)), opened=b64(bytes(provider)),
                         source=b64(provider.read_bytes()))
        facts.write_text(json.dumps({'version': 2, 'main': b64(bytes(source)),
            'cwd': b64(bytes(ROOT)), 'include_path': b64(b'.:'), 'entries': [entry],
            'chdir_entries': []}) + '\n')
        arguments += ['--file-snapshot', str(facts)]
    return arguments


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--semantic-root', type=Path, default=ROOT)
    args = parser.parse_args()
    semantic = args.semantic_root.resolve()
    selected = (args.case,) if args.case else tuple(name for name in CASES if not name.startswith(('first-', 'expression-')) and name != 'generator-source')
    recorder.ROOT = ROOT
    out = Path(tempfile.mkdtemp(prefix='source-stringable-retirement-sources-', dir=ROOT / '.tools'))
    print(out, flush=True)
    manifest = semantic / 'spec/semantics/modules.json'
    modules = [semantic / name for name in json.loads(manifest.read_bytes())]
    assert any(path.name == '298-source-stringable-lifetime.watsup' for path in modules)
    watched = [*modules, manifest, semantic / 'spec/schema.json', semantic / 'bin/php-semantics',
               ROOT / 'frontend/worker.php', ROOT / 'frontend/target.php',
               ROOT / '_build/default/adapter/main.exe', ROOT / '.tools/php/bin/php',
               ROOT / '.tools/php-file.so', ROOT / 'tests/semantics/profile.json',
               ROOT / 'tests/semantics/error_handler_run.py', Path(__file__)]
    for name in selected:
        watched.append(SOURCES / (name + '.php'))
        if CASES[name] is not None and name != 'missing-include':
            watched.append(SOURCES / CASES[name])
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    snapshot = lambda: {str(path): digest(path) for path in watched}
    before = snapshot()
    git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    profile = dict(json.loads((ROOT / 'tests/semantics/profile.json').read_bytes()), include_path='.:')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    report = {'revision': revision, 'working_tree_status': status, 'semantic_root': str(semantic),
              'inputs': before, 'profile': profile, 'selected': selected, 'rows': [],
              'application_evaluations': 0, 'passed': False,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1},
              'scope': 'Final-release trace witnesses. Ordinary constant returns, echo and static-variable '
                       'assignments use their first emitted opcode line; fast and no-unit helpers '
                       'retain keyword frames with no filename argument during operand destruction.'}
    try:
        for name in selected:
            directory = out / name
            directory.mkdir()
            source = SOURCES / (name + '.php')
            provider = SOURCES / CASES[name] if CASES[name] is not None else None
            model_args = source_inputs(directory, source, provider)
            native = recorder.recorded([str(ROOT / '.tools/php/bin/php'), '-n', *flags, str(source)],
                                       directory / 'native', 30)
            model = recorder.recorded([str(semantic / 'bin/php-semantics'), str(source), *model_args,
                                       '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
            report['application_evaluations'] += 1
            outcome = json.loads((directory / 'model.stdout').read_bytes())
            expected_exit = 0
            expected_status = 'normal'
            stdout_equal = ('stdout' in outcome and base64.b64decode(outcome['stdout']) ==
                            (directory / 'native.stdout').read_bytes())
            stderr_equal = ('stderr' in outcome and base64.b64decode(outcome['stderr']) ==
                            (directory / 'native.stderr').read_bytes())
            passed = (native['exit'] == expected_exit and model['exit'] == 0
                      and not native['timeout'] and not model['timeout']
                      and not native['group_after'] and not model['group_after']
                      and not (directory / 'model.stderr').read_bytes()
                      and outcome.get('frontend') == 'accepted' and outcome.get('checked') == 'program'
                      and outcome.get('status') == expected_status and outcome.get('exit_status') == expected_exit
                      and outcome.get('reason') is None and stdout_equal and stderr_equal)
            report['rows'].append({'id': name, 'passed': passed, 'native': native, 'model': model,
                                   'outcome': outcome, 'stdout_equal': stdout_equal, 'stderr_equal': stderr_equal})
            print(name, passed, flush=True)
            if not passed:
                break
        report['passed'] = len(report['rows']) == len(selected) and all(row['passed'] for row in report['rows'])
    finally:
        report['inputs_stable'] = before == snapshot() and not (SOURCES / 'helper-missing-file.php').exists()
        report['head_stable'] = revision == git('rev-parse', 'HEAD')
        report['status_stable'] = status == git('status', '--short')
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return all(report[k] for k in ('passed', 'inputs_stable', 'head_stable', 'status_stable'))


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
