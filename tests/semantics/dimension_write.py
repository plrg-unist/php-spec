#!/usr/bin/env python3
"""Pure string write and reference/nested fetch comparisons; source dispatch is also integrated."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = ROOT/'tests/semantics'
from dimension_read import seq, value, source_validation


def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'), 'dune', 'build', '--root', str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True, timeout=120)
    runner = HERE/'_build/default/numeric_runner.exe'
    specs = [ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    specs += [ROOT/'spec/semantics/44-dimension-read.watsup', ROOT/'spec/semantics/45-dimension-write.watsup']
    specs = list(dict.fromkeys(specs))
    def fingerprint():
        return {'closure': source_validation.fingerprint(),
                'runner': hashlib.sha256(runner.read_bytes()).hexdigest()}
    before = fingerprint()
    containers = [data.hex() for data in (b'', b'a', b'abc', b'a\x00\xff\xc3\xa9')]
    keys = [['i', n] for n in (-2**63, -6, -5, -4, -3, -1, 0, 1, 2, 3, 5, 8)]
    keys += [['s', data.hex()] for data in (b'', b'0', b'-0', b'+1', b' 1 ', b'1x',
        b'-1x', b'1\0tail', b'1.0', b'1e0', b'x', b'-9223372036854775808tail',
        b'9223372036854775808e+', b'-9223372036854775808\0')]
    keys += [['f', bits] for bits in ('3ff8000000000000', 'bff8000000000000',
        '7ff0000000000000', 'fff0000000000000', '7ff8000000000000')]
    keys += [['n', ''], ['b', 0], ['b', 1], ['a', ''], ['u', ''], ['append', '']]
    values = [['s', data.hex()] for data in (b'', b'Z', b'xyz', b'\0', b'\xff\xc3\xa9')]
    values += [['n', ''], ['b', 0], ['b', 1], ['i', 123], ['f', '3ff8000000000000'],
               ['f', '7ff8000000000000'], ['a', ''], ['u', '']]
    cases = [['write', container, key, val] for container in containers for key in keys for val in values]
    cases += [[mode, container, key, ['i', 7]] for mode in ('reference', 'nested') for container in containers for key in keys]
    php = r'''<?php
if (PHP_VERSION !== '8.5.10' || PHP_INT_SIZE !== 8 || PHP_ZTS || PHP_SAPI !== 'cli') exit(91);
function operand($x) { return match($x[0]) {'n'=>null,'b'=>(bool)$x[1],'i'=>(int)$x[1], 'f'=>unpack('E',hex2bin($x[1]))[1], 's'=>hex2bin($x[1]),'a'=>[7]}; }
$events=[];
set_error_handler(function($level,$message,$file,$line) use (&$events) { $events[]=[$level,bin2hex($message),$line]; });
foreach (json_decode(stream_get_contents(STDIN),true) as [$mode,$cv,$kv,$vv]) {
    $events=[]; unset($r); $c=hex2bin($cv); if($kv[0]==='u'||$kv[0]==='append')unset($k);else$k=operand($kv); if($vv[0]==='u')unset($v);else$v=operand($vv);
    try {
        if($mode==='write') { if($kv[0]==='append')$r=($c[]=$v);else$r=($c[$k]=$v); } elseif($mode==='reference') { if($kv[0]==='append')$r=&$c[];else$r=&$c[$k]; } else { if($kv[0]==='append')$c[][0]=7;else$c[$k][0]=7; }
        $payload=match(gettype($r)) {'NULL'=>'','string'=>bin2hex($r)};
        echo json_encode(['value',gettype($r),$payload,$events,bin2hex($c)]),"\n";
    } catch(Throwable $e) { echo json_encode(['throw',get_class($e),bin2hex($e->getMessage()),$events,bin2hex($c),$e->getLine()]),"\n"; }
}
'''
    line = php[:php.index("if($mode==='write')")].count('\n') + 1
    stdin = json.dumps(cases).encode()
    checks = []
    with tempfile.TemporaryDirectory(prefix='dimension-write-', dir=ROOT/'.tools') as tmp:
        oracle_path = Path(tmp)/'oracle.php'
        oracle_path.write_text(php)
        oracle = subprocess.run([str(source_validation.PHP), '-n', *source_validation.FLAGS, str(oracle_path)],
            input=stdin, capture_output=True, env=source_validation.ENV, timeout=30)
        assert oracle.returncode == 0 and not oracle.stderr, (oracle.returncode, oracle.stderr)
        results = [json.loads(row) for row in oracle.stdout.splitlines()]
        assert len(results) == len(cases)
        initial = '($initial_state(NORMAL))[.ARRAYS = [{ITEMS ([ENTRY (KINT 0) (DIRECT (PINT 7))]), NEXT 1}]][.ALLOCATIONS = [HARRAY 0]][.HELD = [HARRAY 0]]'
        for (mode, container, key, val), result in zip(cases, results):
            kp = 'eps' if key[0] == 'append' else ('(VARIABLE ([107]) ' + str(line) + ')' if key[0] == 'u' else '(KNOWN (' + value(key) + '))')
            vp = 'VARIABLE ([118]) ' + str(line) if val[0] == 'u' else 'KNOWN (' + value(val) + ')'
            events = []
            for level, message_hex, observed_line in result[3]:
                message = bytes.fromhex(message_hex)
                assert observed_line == line
                if message in (b'Undefined variable $k', b'Undefined variable $v'):
                    events.append(f'WARNING ({seq(message[-1:])}) {line}')
                else:
                    severity = {2: 'Warning', 8192: 'Deprecated'}[level]
                    events.append(f'DIAGNOSTIC "{severity}" ({seq(message)}) {line}')
            if mode == 'write':
                call = f'(S_out, n_out*) = $string_dimension_write({initial}, {seq(bytes.fromhex(container))}, {kp}, {vp}, {line})'
                assertions = [call, f'n_out* = {seq(bytes.fromhex(result[4]))}']
            else:
                operation = 'STRINGREFERENCE' if mode == 'reference' else 'STRINGNESTED'
                assertions = [f'S_out = $string_dimension_fetch({initial}, {kp}, {operation}, {line})']
                assert result[4] == container
            assertions += [f'S_out.EVENTS = {seq(events)}', 'S_out.HELD = [HARRAY 0]']
            if result[0] == 'throw':
                assert result[5] == line
                assertions.append(f'S_out.COMPLETION = THROWN "{result[1]}" ({seq(bytes.fromhex(result[2]))}) {line}')
            else:
                expected = 'PNULL' if result[1] == 'NULL' else 'PSTRING (' + seq(bytes.fromhex(result[2])) + ')'
                assertions += ['S_out.COMPLETION = NORMAL', f'S_out.RESULT = KNOWN ({expected})']
            checks.append(assertions)
        boundaries = [
            ('eps', 'KNOWN (PSTRING ([90]))'),
            ('(KNOWN PNULL)', 'KNOWN (PSTRING ([90]))'),
            ('(KNOWN (PINT (-9)))', 'VARIABLE ([118]) 1'),
            ('(KNOWN (PINT 0))', 'KNOWN (PSTRING eps)'),
            ('(KNOWN (PINT 0))', 'KNOWN (PSTRING ([90,90]))'),
            ('(KNOWN (PINT 0))', 'KNOWN (PFLOAT 9221120237041090560)'),
            ('(VARIABLE ([107]) 1)', 'KNOWN (PSTRING ([90]))'),
            ('(KNOWN (PINT 0))', 'VARIABLE ([118]) 1')]
        for kp, vp in boundaries:
            checks.append([f'(S_out, n_out*) = $string_dimension_write({initial}, [97], {kp}, {vp}, 0)',
                'n_out* = [97]', 'S_out.COMPLETION = UNSUPPORTED "missing source line"', 'S_out.HELD = [HARRAY 0]'])
        checks.append([f'(S_out, n_out*) = $string_dimension_write({initial}, [97], (KNOWN (PINT 0)), VARIABLE ([95,71,69,84]) 1, 1)',
            'n_out* = [97]', 'S_out.COMPLETION = UNSUPPORTED "request environment variable"', 'S_out.HELD = [HARRAY 0]'])
        checks.append([f'(S_out, n_out*) = $string_dimension_write({initial}[.STORE = [DEFINED (PINT (-1)), DEFINED (PSTRING ([90]))]][.HELD = [HCELL 0, HCELL 1, HARRAY 0]], [97,98], (REFERENCE 0), REFERENCE 1, 1)',
            'n_out* = [97,90]', 'S_out.RESULT = KNOWN (PSTRING ([90]))', 'S_out.COMPLETION = NORMAL',
            'S_out.EVENTS = eps', 'S_out.HELD = [HCELL 0, HCELL 1, HARRAY 0]'])
        for mode in ('STRINGREFERENCE', 'STRINGNESTED'):
            checks.append([f'S_out = $string_dimension_fetch({initial}, (KNOWN PNULL), {mode}, 0)',
                'S_out.COMPLETION = UNSUPPORTED "missing source line"', 'S_out.HELD = [HARRAY 0]'])
        for start in range(0, len(checks), 48):
            batch = checks[start:start+48]
            fixture = Path(tmp)/'checks.watsup'
            fixture.write_text('\n'.join(f'dec $case{start+i}() : bool\ndef $case{start+i}() = true\n' + ''.join(f'  -- if {a}\n' for a in assertions) for i, assertions in enumerate(batch)) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{start+i}()\n' for i in range(len(batch))))
            run = subprocess.run([str(runner), *map(str,specs), str(fixture)], cwd=ROOT, capture_output=True, text=True, timeout=120)
            if run.returncode or run.stdout.strip() != 'true':
                (ROOT/'.tools/dimension-write-failure.watsup').write_text(fixture.read_text())
                raise AssertionError(f'dimension batch {start}: {run.stdout}{run.stderr}')
        assert before == fingerprint(), 'implementation changed during dimension helper validation'
        report = {'result': 'pass', 'classification': 'callback-free string W-fetch and reference/nested error helpers only; source dispatch pending',
            'runtime_cases': len(cases), 'boundary_cases': len(checks)-len(cases), 'assertions': sum(map(len,checks)), 'fingerprint': before,
            'cases': [{'input': item, 'oracle': result} for item, result in zip(cases,results)],
            'oracle': {'source_base64': base64.b64encode(php.encode()).decode(),
                'stdin_base64': base64.b64encode(stdin).decode(), 'stdout_base64': base64.b64encode(oracle.stdout).decode(),
                'stderr_base64': base64.b64encode(oracle.stderr).decode(), 'exit_status': oracle.returncode,
                'command': oracle.args, 'context': {'file': str(oracle_path), 'cwd': str(ROOT)}}}
    (ROOT/'coverage/semantics/dimension-write.json').write_text(json.dumps(report, indent=2)+'\n')
    print({k: report[k] for k in ('result','runtime_cases','boundary_cases','assertions')})


if __name__ == '__main__':
    main()
