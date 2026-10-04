#!/usr/bin/env python3
"""Main/include deprecated interpolation notices with live handler state."""
from pathlib import Path
import base64
import hashlib
import json
import subprocess
import tempfile
from error_handler_run import recorded

R = Path(__file__).resolve().parents[2]
P = Path(__file__).with_name('dollar-curly')
b64 = lambda value: base64.b64encode(value).decode()


def main():
    out = Path(tempfile.mkdtemp(prefix='dollar-curly-sources-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'spec/schema.json',
               R / 'frontend/worker.php', R / 'frontend/SourcePrinter.php',
               R / 'vendor/php-parser/lib/PhpParser/Parser/Php8.php',
               R / '_build/default/adapter/main.exe', R / '.tools/php/bin/php',
               R / 'tests/semantics/profile.json', R / 'bin/php-semantics', Path(__file__), *sorted(P.glob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    profile = json.loads((R / 'tests/semantics/profile.json').read_text())
    cases = [('main-default', 'main-modern', profile),
             ('main-off', 'main-modern', dict(profile, error_reporting='0')),
             ('main-stdout', 'main-modern', dict(profile, display_errors='stdout')),
             ('include-effects', 'include-effects', profile), ('private-publication', 'main', profile)]
    rows = []
    for name, file, selected in cases:
        case = out / name; case.mkdir(); source = P / (file + '.php'); args = []
        if name == 'main-off':
            # The pinned binary's registered default include_path is observed .:.
            startup = {key: b64(value.encode()) for key, value in
                       (('error_reporting', '0'), ('include_path', '.:'), ('display_errors', 'stderr'))}
            path = case / 'startup.json'; path.write_text(json.dumps(startup) + '\n'); args = ['--startup-ini', str(path)]
        if name == 'main-stdout':
            path = case / 'startup.json'; path.write_text(json.dumps({'display_errors': b64(b'stdout')}) + '\n')
            args = ['--startup-ini', str(path)]
        if name in {'include-effects', 'private-publication'}:
            child = P / ('included-multiline.php' if name == 'include-effects' else 'warned.php')
            snapshot = {'version': 2, 'main': b64(bytes(source)), 'cwd': b64(bytes(R)), 'include_path': b64(b'.:'),
                        'chdir_entries': [], 'entries': [{'caller': b64(bytes(source)), 'requested': b64(bytes(child)),
                        'cwd': b64(bytes(R)), 'include_path': b64(b'.:'), 'status': 'opened',
                        'resolved': b64(bytes(child)), 'opened': b64(bytes(child)), 'source': b64(child.read_bytes())}]}
            path = case / 'snapshot.json'; path.write_text(json.dumps(snapshot) + '\n'); args = ['--file-snapshot', str(path)]
        flags = [a for key, value in selected.items() for a in ('-d', key + '=' + value)]
        native = recorded([str(R / '.tools/php/bin/php'), '-n', *flags, str(source)], case / 'native', 30)
        model = recorded([str(R / 'bin/php-semantics'), str(source), *args, '--steps', '100000', '--timeout', '60'], case / 'model', 90)
        outcome = json.loads((case / 'model.stdout').read_bytes())
        passed = (native['exit'] == model['exit'] == 0 and not native['timeout'] and not model['timeout']
                  and not (case / 'model.stderr').read_bytes() and outcome.get('frontend') == 'accepted'
                  and outcome.get('checked') == 'program' and outcome.get('status') == 'normal'
                  and outcome.get('exit_status') == 0 and outcome.get('reason') is None
                  and base64.b64decode(outcome['stdout']) == (case / 'native.stdout').read_bytes()
                  and base64.b64decode(outcome['stderr']) == (case / 'native.stderr').read_bytes())
        rows.append({'id': name, 'profile': selected, 'native': native, 'model': model, 'pass': passed})
        print(name, passed, flush=True)
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps({'revision': revision, 'inputs': before, 'rows': rows,
        'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'},
        'scope': 'Five main/include source profiles; early eval notices remain required follow-on.'}, indent=2) + '\n')
    return all(row['pass'] for row in rows)


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
