#!/usr/bin/env python3
"""Primitive reporting masks preserve prior events and conditional restoration."""
from pathlib import Path
import hashlib
import json
import subprocess
import tempfile
import function_scope as scope

ROOT = Path(__file__).resolve().parents[2]
CHECKS = [
    'S = $initial_state(NORMAL)', 'S.REPORTING = 30719', 'S.SILENCES = eps',
    'S_prior = S[.EVENTS = [OUTPUT ([80])]]',
    '$missing(S_prior, [120], 1).EVENTS = [OUTPUT ([80]), WARNING ([120]) 1]',
    '$missing(S_prior[.REPORTING = 4437], [120], 1).EVENTS = [OUTPUT ([80])]',
    '$missing(S[.REPORTING = 0], [120], 1).RESULT = KNOWN PNULL',
    '$diagnostic(S[.REPORTING = 2], "Warning", [87], 1).EVENTS = [DIAGNOSTIC "Warning" ([87]) 1]',
    '$diagnostic(S[.REPORTING = 2], "Notice", [78], 1).EVENTS = eps',
    '$diagnostic(S[.REPORTING = 8], "Notice", [78], 1).EVENTS = [DIAGNOSTIC "Notice" ([78]) 1]',
    '$diagnostic(S[.REPORTING = 8], "Deprecated", [68], 1).EVENTS = eps',
    '$diagnostic(S[.REPORTING = 8192], "Deprecated", [68], 1).EVENTS = [DIAGNOSTIC "Deprecated" ([68]) 1]',
    '$leading_warning(S[.REPORTING = 4437], true, 1).EVENTS = eps',
    '|$leading_warning(S, true, 1).EVENTS| = 1',
    '$stringify(S[.REPORTING = 4437], PFLOAT 9221120237041090560, 1).EVENTS = eps',
    '$stringify(S[.REPORTING = 4437], PFLOAT 9221120237041090560, 1).RESULT = KNOWN (PSTRING ([78,65,78]))',
    '|$stringify(S, PFLOAT 9221120237041090560, 1).EVENTS| = 1',
    'porigin = PORIGIN 0 eps',
    'n_const* = [88]',
    'puserconstant = {NAME n_const*, ORIGIN porigin, VALUE PINT 1, CLASS PVSCALAR}',
    'S_const = S[.USERCONSTANTS = [puserconstant]]',
    '$constant_activate(S_const[.REPORTING = 4437], porigin, [88], PINT 2, PVSCALAR, 1).EVENTS = eps',
    '|$constant_activate(S_const, porigin, [88], PINT 2, PVSCALAR, 1).EVENTS| = 1',
    '$silence_restore(S[.REPORTING = 4437], 30719).REPORTING = 30719',
    '$silence_restore(S[.REPORTING = 2], 30719).REPORTING = 2',
    '$silence_restore(S[.REPORTING = 0], 4437).REPORTING = 0',
    '$silence_restore(S[.REPORTING = 4437], $(-1)).REPORTING = $(-1)',
    'S_entered = $silence_begin(S_prior[.REPORTING = $(-1)], porigin)',
    'S_entered.REPORTING = 4437', 'S_entered.SILENCES = [SILENCE porigin $(-1)]',
    '$silence_unwind(S_entered[.TODO = eps]).REPORTING = $(-1)',
    '$silence_unwind(S_entered[.TODO = eps]).SILENCES = eps',
    '$silence_unwind(S_entered[.TODO = eps]).EVENTS = [OUTPUT ([80])]',
    '$reporting_valid(2147483647)', '$reporting_valid($(-2147483648))',
    '~$reporting_valid(2147483648)', '~$reporting_valid($(-2147483649))',
]

def main():
    before = scope.q.t.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='suppression-reporting-', dir=ROOT / '.tools'))
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    inputs = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in [*modules, runner, Path(__file__)]}
    (out / 'inputs.json').write_text(json.dumps({'fingerprint': before, 'files': inputs}, indent=2))
    for name in inputs:
        path = out / 'original-inputs' / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes((ROOT / name).read_bytes())
    fixture = out / 'reporting.watsup'
    fixture.write_text('dec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + check + '\n' for check in CHECKS))
    command = [str(runner), *map(str, modules), str(fixture)]
    (out / 'runner.command.json').write_text(json.dumps(command))
    try:
        result = subprocess.run(command, capture_output=True, timeout=60)
    except subprocess.TimeoutExpired as error:
        (out / 'runner.stdout').write_bytes(error.stdout or b'')
        (out / 'runner.stderr').write_bytes(error.stderr or b'')
        (out / 'runner.status.json').write_text(json.dumps({'status': 'timeout', 'seconds': 60}))
        raise
    (out / 'runner.stdout').write_bytes(result.stdout)
    (out / 'runner.stderr').write_bytes(result.stderr)
    (out / 'runner.status.json').write_text(json.dumps({'status': 'exit', 'exit_status': result.returncode}))
    assert result.returncode == 0 and result.stdout == b'true\n' and not result.stderr, str(out)
    assert before == scope.q.t.syntax_validation.implementation_fingerprint()
    report = {'result': 'pass', 'fingerprint': before, 'inputs': inputs, 'assertions': len(CHECKS), 'raw': str(out),
              'scope': 'Primitive emission and restoration controls, including TODO-cleared cleanup and signed32 masks. Arbitrary mask states do not assert source support for reporting configuration APIs.'}
    (out / 'report.json').write_text(json.dumps(report, indent=2))
    (ROOT / 'coverage/semantics/suppression-reporting.json').write_text(json.dumps(report, indent=2))
    print(out, len(CHECKS), 'passed')

if __name__ == '__main__':
    main()
