#!/usr/bin/env python3
"""Pure R-fetch helper comparisons; source string dispatch/prepass is not integrated."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
loader = importlib.util.spec_from_file_location('source_validation', HERE/'validate.py')
source_validation = importlib.util.module_from_spec(loader)
loader.loader.exec_module(source_validation)


def seq(values):
    return '[' + ', '.join(map(str, values)) + ']' if values else 'eps'


def value(item):
    kind, data = item
    if kind == 'n': return 'PNULL'
    if kind == 'b': return 'PBOOL ' + str(bool(data)).lower()
    if kind == 'i': return 'PINT $(' + str(data) + ')'
    if kind == 'f': return 'PFLOAT ' + str(int(data, 16))
    if kind == 's': return 'PSTRING (' + seq(bytes.fromhex(data)) + ')'
    if kind == 'a': return 'PARRAY 0'
    raise AssertionError(item)


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'), 'dune', 'build', '--root', str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True, timeout=120)
    runner = HERE/'_build/default/numeric_runner.exe'
    specs = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    specs += [ROOT/'spec/semantics/44-dimension-read.watsup']
    specs = list(dict.fromkeys(specs))
    def fingerprint():
        return {'closure': source_validation.fingerprint(),
                'runner': hashlib.sha256(runner.read_bytes()).hexdigest()}
    before = fingerprint()
    containers = [['s', data.hex()] for data in (b'', b'abc', b'a\x00\xff\xc3\xa9')]
    containers += [['n', ''], ['b', 0], ['b', 1], ['i', 17], ['f', '3ff8000000000000'],
                   ['f', '7ff8000000000000'], ['a', ''], ['u', '']]
    keys = [['i', n] for n in (-2**63, -6, -5, -4, -3, -1, 0, 1, 2, 3, 4, 5, 2**63-1)]
    keys += [['s', data.hex()] for data in (b'', b'0', b'-0', b'00', b'+1', b' 1', b'1 ', b'1x',
              b'-1x', b'1\x00tail', b'1\xff', b'1.0', b'1e0', b'1.5x', b'x', b'\xff1',
              b'9223372036854775808', b'-9223372036854775809', b'0x1', b'\t2\r\n')]
    keys += [['s', data.hex()] for data in (b'-9223372036854775808tail',
              b'-9223372036854775808 ', b'-9223372036854775808\0',
              b'9223372036854775808e+', b'-9223372036854775809e+',
              b'9999999999999999999e+', b'-0009223372036854775808 ')]
    keys += [['f', bits] for bits in ('0000000000000000', '8000000000000000', '3ff8000000000000',
             'bff8000000000000', '7ff0000000000000', 'fff0000000000000', '7ff8000000000000',
             '43f0000000000000')]
    keys += [['n', ''], ['b', 0], ['b', 1], ['a', ''], ['u', '']]
    cases = [[container, key] for container in containers for key in keys]
    php = r'''<?php
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8 || PHP_ZTS || PHP_SAPI !== 'cli') exit(91);
function operand($x) { return match($x[0]) {'n'=>null,'b'=>(bool)$x[1],'i'=>(int)$x[1], 'f'=>unpack('E',hex2bin($x[1]))[1], 's'=>hex2bin($x[1]),'a'=>[7]}; }
$events=[];
set_error_handler(function($level,$message,$file,$line) use (&$events) { $events[]=[$level,bin2hex($message),$line]; });
foreach (json_decode(stream_get_contents(STDIN),true) as [$cv,$kv]) {
    $events=[]; if($cv[0]==='u')unset($c);else$c=operand($cv); if($kv[0]==='u')unset($k);else$k=operand($kv);
    try {
        $r=$c[$k];
        $payload=match(gettype($r)) {'NULL'=>'','string'=>bin2hex($r),'integer'=>(string)$r};
        echo json_encode(['value',gettype($r),$payload,$events]),"\n";
    } catch(Throwable $e) { echo json_encode(['throw',get_class($e),bin2hex($e->getMessage()),$events,$e->getLine()]),"\n"; }
}
'''
    line = php[:php.index('$r=$c[$k]')].count('\n') + 1
    stdin = json.dumps(cases).encode()
    checks = []
    with tempfile.TemporaryDirectory(prefix='dimension-read-', dir=ROOT/'.tools') as tmp:
        oracle_path = Path(tmp)/'oracle.php'
        oracle_path.write_text(php)
        oracle = subprocess.run([str(source_validation.PHP), '-n', *source_validation.FLAGS, str(oracle_path)],
                                input=stdin, capture_output=True, env=source_validation.ENV, timeout=30)
        assert oracle.returncode == 0 and not oracle.stderr, (oracle.returncode, oracle.stderr)
        results = [json.loads(row) for row in oracle.stdout.splitlines()]
        assert len(results) == len(cases)
        initial = '($initial_state(NORMAL))[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (DIRECT (PINT 7))]), NEXT 1}]][.ALLOCATIONS = [HARRAY 0]]'
        for (container, key), result in zip(cases, results):
            cp = 'VARIABLE ([99]) ' + str(line) if container[0] == 'u' else 'KNOWN (' + value(container) + ')'
            kp = 'VARIABLE ([107]) ' + str(line) if key[0] == 'u' else 'KNOWN (' + value(key) + ')'
            events = []
            for level, message_hex, observed_line in result[3]:
                message = bytes.fromhex(message_hex)
                assert observed_line == line
                if message in (b'Undefined variable $c', b'Undefined variable $k'):
                    events.append(f'WARNING ({seq(message[-1:])}) {line}')
                else:
                    severity = {2: 'Warning', 8192: 'Deprecated'}[level]
                    events.append(f'DIAGNOSTIC "{severity}" ({seq(message)}) {line}')
            assertions = [f'S_out = $probe({initial}, {cp}, {kp}, {line})', f'S_out.EVENTS = {seq(events)}']
            if result[0] == 'throw':
                assert result[4] == line
                assertions.append(f'S_out.COMPLETION = THROWN "{result[1]}" ({seq(bytes.fromhex(result[2]))}) {line}')
            else:
                if result[1] == 'NULL': expected = 'PNULL'
                elif result[1] == 'string': expected = 'PSTRING (' + seq(bytes.fromhex(result[2])) + ')'
                elif result[1] == 'integer': expected = 'PINT $(' + result[2] + ')'
                else: raise AssertionError(result)
                assertions += ['S_out.COMPLETION = NORMAL', f'S_out.RESULT = KNOWN ({expected})']
            checks.append(assertions)
        leaf_cases = [('PINT 1', '(PSTRING ([98]))'), ('PINT (-1)', 'eps'), ('PINT 3', 'eps'),
                      ('PSTRING ([49,120])', '(PSTRING ([98]))'), ('PSTRING ([45,49,120])', 'eps'),
                      ('PSTRING ([49,46,48])', 'eps'), ('PFLOAT 4607182418800017408', 'eps'),
                      ('PBOOL true', 'eps'), ('PNULL', 'eps'), ('PARRAY 0', 'eps')]
        checks += [[f'$string_constant_read([97,98,99], {key}) = {expected}'] for key, expected in leaf_cases]
        for container, key in [('PSTRING ([97])', 'PNULL'), ('PSTRING ([97])', 'PINT 3'),
                               ('PSTRING ([97])', 'PARRAY 0'), ('PINT 1', 'PNULL')]:
            checks.append([f'S_out = $dimension_read({initial}[.HELD = [HARRAY 0]], {container}, KNOWN ({key}), 0)',
                           'S_out.COMPLETION = UNSUPPORTED "missing source line"', 'S_out.HELD = [HARRAY 0]'])
        checks.append([f'S_out = $dimension_read({initial}[.STORE = [DEFINED (PINT (-1))]][.HELD = [HARRAY 0]], PSTRING ([97,98]), REFERENCE 0, 1)',
                       'S_out.RESULT = KNOWN (PSTRING ([98]))', 'S_out.HELD = [HARRAY 0]', 'S_out.EVENTS = eps'])
        declarations = 'dec $probe(pstate, poperand, poperand, int) : pstate\ndef $probe(S, poperand_c, poperand_k, z) = $dimension_read(S_c, pvalue, poperand_k, z)\n  -- if S_c = $resolve_at(S, poperand_c, z)\n  -- if S_c.RESULT = KNOWN pvalue\n'
        for start in range(0, len(checks), 48):
            batch = checks[start:start+48]
            fixture = Path(tmp)/'checks.watsup'
            fixture.write_text(declarations + '\n'.join(f'dec $case{start+i}() : bool\ndef $case{start+i}() = true\n' + ''.join(f'  -- if {a}\n' for a in assertions) for i, assertions in enumerate(batch)) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{start+i}()\n' for i in range(len(batch))))
            run = subprocess.run([str(runner), *map(str,specs), str(fixture)], cwd=ROOT, capture_output=True, text=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT/'.tools/dimension-read-failure.watsup').write_text(fixture.read_text())
                raise AssertionError(f'dimension batch {start}: {run.stdout}{run.stderr}')
        assert before == fingerprint(), 'implementation changed during dimension helper validation'
        report = {'result': 'pass', 'classification': 'runtime R-fetch helpers and explicit compiler leaf only; source string dispatch/prepass remains pending',
                  'runtime_cases': len(cases), 'constant_leaf_cases': len(leaf_cases), 'boundary_cases': 5,
                  'assertions': sum(map(len,checks)), 'fingerprint': before,
                  'cases': [{'input': item, 'oracle': result} for item, result in zip(cases,results)],
                  'oracle': {'source_base64': base64.b64encode(php.encode()).decode(), 'source_sha256': hashlib.sha256(php.encode()).hexdigest(),
                             'stdin_base64': base64.b64encode(stdin).decode(), 'stdout_base64': base64.b64encode(oracle.stdout).decode(),
                             'stderr_base64': base64.b64encode(oracle.stderr).decode(), 'exit_status': oracle.returncode,
                             'command': oracle.args, 'context': {'file': str(oracle_path), 'cwd': str(ROOT)}}}
    (ROOT/'coverage/semantics/dimension-read.json').write_text(json.dumps(report, indent=2)+'\n')
    print({k: report[k] for k in ('result','runtime_cases','constant_leaf_cases','boundary_cases','assertions')})


if __name__ == '__main__':
    main()
