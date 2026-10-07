#!/usr/bin/env python3
"""Stringable source ownership, reference mutation and successful post-cast throw."""
from pathlib import Path
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile

from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
SOURCES = Path(__file__).with_name('source-stringable')
CASES = ('eval-lifetime', 'reference-unpromoted', 'pending-empty-unpromoted', 'borrowed-throw-direct')
b64 = lambda value: base64.b64encode(value).decode()


def source_inputs(out):
    header = out / 'startup.json'
    header.write_text(json.dumps({'error_reporting': b64(b'30719'), 'include_path': b64(b'.:')}) + '\n')
    return ['--startup-ini', str(header)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', choices=CASES)
    parser.add_argument('--semantic-root', type=Path, default=R)
    args = parser.parse_args()
    semantic = args.semantic_root.resolve()
    selected = (args.case,) if args.case else CASES
    out = Path(tempfile.mkdtemp(prefix='source-stringable-sources-', dir=R / '.tools'))
    print(out, flush=True)
    modules = [semantic / name for name in json.loads((semantic / 'spec/semantics/modules.json').read_bytes())]
    assert any(path.name == '298-source-stringable-lifetime.watsup' for path in modules)
    watched = [*modules, semantic / 'spec/semantics/modules.json', semantic / 'spec/schema.json',
               semantic / 'bin/php-semantics', R / 'frontend/worker.php', R / 'frontend/target.php',
               R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php', R / '.tools/php-file.so',
               R / 'tests/semantics/profile.json', R / 'tests/semantics/error_handler_run.py',
               Path(__file__), *sorted(SOURCES.glob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    profile = dict(json.loads((R / 'tests/semantics/profile.json').read_bytes()), include_path='.:')
    flags = [arg for key, value in profile.items() for arg in ('-d', key + '=' + value)]
    rows = []
    for name in selected:
        directory = out / name
        directory.mkdir()
        source = SOURCES / (name + '.php')
        model_args = source_inputs(directory)
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], directory / 'native', 30)
        model = recorded([str(semantic / 'bin/php-semantics'), str(source), *model_args,
                          '--steps', '100000', '--timeout', '60'], directory / 'model', 90)
        outcome = json.loads((directory / 'model.stdout').read_bytes())
        passed = (native['exit'] == model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (directory / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                  and outcome.get('checked') == 'program' and outcome.get('status') == 'normal'
                  and outcome.get('exit_status') == 0 and outcome.get('reason') is None
                  and base64.b64decode(outcome['stdout']) == (directory / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (directory / 'native.stderr').read_bytes())
        rows.append({'id': name, 'profile': profile, 'passed': passed, 'native': native, 'model': model})
        print(name, passed, flush=True)
        if not passed:
            break
    assert before == {str(path): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
        'selected': selected,
        'semantic_root': str(semantic), 'scope': 'One original eval lifetime source and three explicit companions: unpromoted REF/empty constructors and direct callable publication in place of the outside-core function_exists observer. No provider facts are needed. These do not confer agreement on the promotion/observer originals.'}, indent=2) + '\n')
    return len(rows) == len(selected) and all(row['passed'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
