#!/usr/bin/env python3
"""Source-derived terminal __toString callback and saved-frame integrity."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
MODULES = [ROOT / name for name in json.loads(
    (ROOT / 'spec/semantics/modules.json').read_text())]
SIMPLE = b'<?php class M extends Exception { public function __toString(): string { return "OVR"; } } throw new M("m");'
NESTED = (b'<?php class C { public function __toString(): string { return "I"; } } '
          b'class M extends Exception { public function __toString(): string '
          b'{ echo new C; return "OVR"; } } throw new M;')
STAGES = [
    ('pending', SIMPLE,
     'S.TODO = (CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) 0) '
     ':: (STRINGIFY_RESULT n porigin_site 0) :: (TERMINAL_STRING n) :: eps', [
         'S.OBJECTS[n] = INSTANCE porigin_class',
         'porigin_site = porigin_method',
         '$terminal_string_site(S,porigin_site,0)',
         '$call_task_valid(S,CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) 0)',
         '~$call_task_valid(S[.TODO = [CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) 0]],CALL_ARGS (METHOD_TARGET n porigin_method) eps 0 eps (porigin_site) 0)',
         '~$call_task_valid(S,CALL_ARGS (METHOD_TARGET $(n + 1) porigin_method) eps 0 eps (porigin_site) 0)',
         '~$call_task_valid(S,CALL_ARGS (METHOD_TARGET n porigin_class) eps 0 eps (porigin_site) 0)',
         '$throwable_field(S,n,"string") = PSTRING eps',
     ]),
    ('entered', SIMPLE,
     'S.CURRENT = (pcallcontext) -- if S.FRAMES = pframe :: pframe_tail* '
     '-- if pframe.TODO = (STRINGIFY_RESULT n porigin_site 0) :: (TERMINAL_STRING n) :: eps '
     '-- if pcallcontext.RECEIVER = (n)', [
         '$terminal_string_context(S,pcallcontext)',
         '$terminal_string_frame_match(S,(pcallcontext),pframe,porigin_site)',
         '$trace_context(S,eps,(pcallcontext)) = [ptraceframe]',
         'ptraceframe.FILE = eps',
         'ptraceframe.LINE = -1',
         '~$terminal_string_frame_match(S,(pcallcontext[.RECEIVER = (999)]),pframe,porigin_site)',
     ]),
    ('nested-saved', NESTED,
     'S.CURRENT = (pcallcontext_inner) '
     '-- if S.FRAMES = pframe_inner :: pframe_terminal :: pframe_tail* '
     '-- if pframe_inner.CONTEXT = (pcallcontext_terminal) '
     '-- if pcallcontext_terminal.CALLSITE = (porigin_site) '
     '-- if $terminal_string_frame_match(S,(pcallcontext_terminal),pframe_terminal,porigin_site)', [
         '$terminal_string_saved(S,S.CURRENT,S.FRAMES,pcallcontext_terminal)',
         '$terminal_string_active_site(S,S.CURRENT,S.FRAMES,porigin_site)',
         '~$terminal_string_frame_match(S,(pcallcontext_inner),pframe_terminal,porigin_site)',
         '~$terminal_string_saved(S,S.CURRENT,pframe_terminal :: pframe_inner :: pframe_tail*,pcallcontext_terminal)',
         '~$terminal_string_saved(S,S.CURRENT,pframe_inner :: pframe_terminal[.TODO = eps] :: pframe_tail*,pcallcontext_terminal)',
     ]),
    ('rendered', SIMPLE,
     'S.COMPLETION = UNCAUGHT_RENDERED n preqbytes', [
         'preqbytes = $ptascii("OVR")',
         'S.TODO = eps',
         '$throwable_field(S,n,"string") = PSTRING eps',
         '$throwable_field(S,n,"message") = PSTRING $ptascii("m")',
         '(HOBJECT n) <- $heap_graph(S).ROOTS',
         '$property_state_valid(S)',
     ]),
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = Path(tempfile.mkdtemp(prefix='throwable-terminal-protocol-', dir=ROOT / '.tools'))
    profile = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
    flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', *flags, '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                     out / 'adapter')
    try:
        checked = {}
        for source in (SIMPLE, NESTED):
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            result = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert result['ok'], result
            checked[source] = result['fixture']
    finally:
        frontend.close()
        adapter.close()
    inputs = [*MODULES, ROOT / 'spec/semantics/modules.json', Path(__file__),
              ROOT / 'frontend/worker.php', ROOT / 'frontend/wire.php',
              ROOT / '.tools/php/bin/php', ROOT / '.tools/php-file.so',
              ROOT / 'tests/semantics/profile.json',
              ROOT / 'tests/semantics/_build/default/numeric_runner.exe',
              ROOT / '_build/default/adapter/main.exe']
    before = {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    results = []
    for name, source, stage, checks in STAGES:
        directory = out / name
        directory.mkdir()
        source_file = directory / 'source.php'
        source_file.write_bytes(source)
        initial = ('$php_run(' + checked[source] + ', 0, ' +
                   json.dumps(base64.b64encode(str(source_file).encode()).decode()) + ')')
        fixture = directory / 'protocol.watsup'
        fixture.write_text(
            'dec $stage(pstate) : bool\n'
            f'def $stage(S) = true -- if {stage}\n'
            'def $stage(S) = false -- otherwise\n'
            'dec $seek(pstate, nat) : pstate\n'
            'def $seek(S, n) = S -- if $stage(S)\n'
            'def $seek(S, n) = $seek($drive_steps(S[.COMPLETION = NORMAL], 1), '
            '$nabs($(n - 1))) -- if ~$stage(S) -- if $(n > 0)\n'
            'dec $main() : bool\ndef $main() = true\n'
            f'  -- if S_initial = {initial}\n'
            '  -- if S = $seek(S_initial[.COMPLETION = NORMAL], 400)\n'
            f'  -- if {stage}\n'
            '  -- if $call_descriptors_valid(S)\n'
            '  -- if $heap_valid($heap_graph(S))\n'
            + ''.join('  -- if ' + check + '\n' for check in checks))
        result = subprocess.run(
            [str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),
             *map(str, MODULES), str(fixture)], capture_output=True,
            text=True, timeout=300)
        (directory / 'stdout').write_text(result.stdout)
        (directory / 'stderr').write_text(result.stderr)
        passed = result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
        results.append({'id': name, 'assertions': len(checks) + 4,
                        'source_sha256': sha(source_file),
                        'fixture_sha256': sha(fixture), 'pass': passed})
        print(name, passed, flush=True)
        if not passed:
            print(result.stderr[-1600:], flush=True)
    stable = before == {str(path.relative_to(ROOT)): sha(path) for path in inputs}
    report = {'result': 'pass' if stable and all(row['pass'] for row in results) else 'fail',
              'stable': stable, 'inputs': before, 'records': results, 'raw': str(out)}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(out, report['result'])
    assert report['result'] == 'pass'


if __name__ == '__main__':
    main()
