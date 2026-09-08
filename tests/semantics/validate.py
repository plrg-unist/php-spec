#!/usr/bin/env python3
"""Fresh-process, original-byte differential tests for the checked machine."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import tempfile
import random
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests'))
import validate as syntax_validation

PROFILE = json.loads((ROOT / 'tests/semantics/profile.json').read_text())
PHP = ROOT / '.tools/php/bin/php'
ENV = dict(os.environ, LC_ALL='C', TZ='UTC')
ENV.pop('PHP_SPEC_SCRIPT_ENCODING', None)
FLAGS = [flag for key, value in PROFILE.items() for flag in ('-d', key + '=' + value)]
CASES = {
    'empty': b'<?php ;',
    'bytes': b'<?php echo "a\\x00\\xff", "", "BC", "DEF";',
    'integers': b'<?php echo 0, 42, 9223372036854775807;',
    'constants': b'<?php echo true, false, NULL, TrUe, FaLsE;',
    'blocks': b'outside<?php { echo "inside"; { echo 73; } } ?>end',
    'discard': b'<?php "unused"; 72; true; echo "end";',
    'undefined': b'<?php\necho "prefix", UNKNOWN_CONST; echo "unreachable";',
    'static-break': b'<?php echo "unreachable";\nbreak;',
    'assignment-chain': b'<?php $a=$b=42; echo $a,$b;',
    'assignment-copy': b'<?php $a=1; $b=$a; $a=7; echo $a,$b;',
    'alias-write': b'<?php $a=1; $b=&$a; $c=&$b; $a=7; echo $a,$b,$c;',
    'alias-rebind': b'<?php $a=1; $b=&$a; $c=&$b; $d=2; $b=&$d; $b=3; echo $a,$b,$c,$d;',
    'reference-initialize': b'<?php $a=&$missing; echo $a,$missing; $a=9; echo $missing;',
    'unset-reference': b'<?php $a=1; $b=&$a; unset($a); $a=7; echo $a,$b;',
    'missing-read': b'<?php\necho "before",$missing,"after"; $missing;',
    'dynamic-name': b'<?php $name="a"; $$name=4; $b=&$$name; $name="b"; $$name=7; echo $a,$b;',
    'dynamic-delayed-name': b'<?php $a="unchanged"; $n="a"; $$n=($n="b"); echo $a,$b;',
    'dynamic-captured-name': b'<?php $a="old-a";$b="old-b"; ${($n="a")}=($n="b"); echo $a,$b;',
    'dynamic-unset': b'<?php $name="a"; $a=3; unset($$name); echo $a;',
    'dynamic-numeric-name': b'<?php ${42}=7; ${true}=8; ${null}=9; echo ${42},${true},${null};',
    'dynamic-write-initialize': b'<?php $n="missing"; $$n=$missing; echo $missing;',
    'cv-write-missing': b'<?php $missing=$missing; echo $missing;',
    'discard-variable': b'<?php $missing; ${"missing"}; $name="missing"; $$name;',
    'assignment-source-lines': b'<?php\n$a=\n$missing;\necho\n$missing;\n$n="b";\n$$n=\n$missing;',
    'dynamic-captured-nested': b'<?php $n="a";$a=1;$b="OLD"; ${$$n}=($a="b"); echo $b,${1};',
    'dynamic-ref-rhs-changes-name': b'<?php $n="a"; $$n =& ${($n="b")}; $a="A"; $b="B"; echo $a,$b,$n;',
    'captured-ref-rhs-changes-name': b'<?php ${($n="a")} =& ${($n="b")}; $a="A"; echo $a,$b,$n;',
    'dynamic-nul-name': b'<?php ${"a\\0b"}=3;echo ${"a\\0b"};',
    'dynamic-source-lines': b'<?php\necho ${\n$missing\n};\n${\n$missing\n}=\n$other;\nunset(${\n$missing\n});\n$a=&${\n$missing\n};',
    'dynamic-reference': b'<?php $n="x"; $a=&$$n; $a=7; echo $x;',
    'dynamic-reference-rebind': b'<?php $a=1; $b=2; $n="a"; $$n=&$b; $a=7; echo $a,$b;',

}


# Independent review-authored witnesses keep their original provenance.
CONFORMANCE = ['reference-rebind', 'dynamic-variable']
for identifier in CONFORMANCE:
    CASES['conformance-' + identifier] = (ROOT / 'tests/semantics/conformance' / (identifier + '.php')).read_bytes()

# Deterministic alias interactions vary mutations rather than mirroring rules.
rng = random.Random(85010)
for number in range(20):
    statements = ['<?php', '$a=1;', '$b=2;', '$c=3;']
    for _ in range(20):
        left, right = rng.choice('abc'), rng.choice('abc')
        operation = rng.randrange(5)
        if operation == 0:
            statements.append(f'${left}={rng.randrange(10)};')
        elif operation == 1:
            statements.append(f'${left}=&${right};')
        elif operation == 2:
            statements.append(f'${left}=${right};')
        elif operation == 3:
            statements.append(f'unset(${left});')
        else:
            statements.append(f'$n="{left}"; $$n=${right};')
        statements.append('echo $a,$b,$c,";";')
    CASES[f'generated-alias-{number:02}'] = '\n'.join(statements).encode()


def fingerprint():
    return syntax_validation.implementation_fingerprint()


def main():
    before = fingerprint()
    results = []
    negatives = []
    with tempfile.TemporaryDirectory(prefix='php-semantics-') as directory:
        for name, source in CASES.items():
            path = Path(directory) / (name + '.php')
            path.write_bytes(source)
            semantic = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path)],
                                      capture_output=True, env=ENV, timeout=35, cwd=directory)
            actual = json.loads(semantic.stdout)
            oracle = subprocess.run([str(PHP), '-n', *FLAGS, str(path)], cwd=directory,
                                    capture_output=True, env=ENV, timeout=30)
            expected = {'stdout': base64.b64encode(oracle.stdout).decode(),
                        'stderr': base64.b64encode(oracle.stderr).decode(),
                        'exit_status': oracle.returncode}
            assert semantic.returncode == 0, (name, actual)
            assert actual['status'] in {'normal', 'php_error', 'static_rejection'}, (name, actual)
            assert all(actual[k] == v for k, v in expected.items()), (name, actual, expected)
            results.append({'id': name, 'source_sha256': hashlib.sha256(source).hexdigest(),
                            'source_base64': base64.b64encode(source).decode(),
                            'context': {'file': str(path), 'cwd': directory},
                            'provenance': ('tests/semantics/conformance/' + name.removeprefix('conformance-') + '.php') if name.startswith('conformance-') else 'authored/generated in tests/semantics/validate.py',
                            'semantic': actual, 'oracle': expected, 'comparison': 'pass'})
        path = Path(directory) / 'unsupported.php'
        path.write_bytes(b'<?php strlen("a");')
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path)], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({"source": base64.b64encode(path.read_bytes()).decode(), "command": result.args,
                          "exit_status": result.returncode, "observation": json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'unsupported'
        path.write_bytes(b'<?php echo PHP_INT_MAX;')
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path)], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({'source': base64.b64encode(path.read_bytes()).decode(), 'command': result.args, 'exit_status': result.returncode, 'observation': json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'unsupported'
        path.write_bytes(b'<?php echo "x";')
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path), '--steps', '0'], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({"source": base64.b64encode(path.read_bytes()).decode(), "command": result.args,
                          "exit_status": result.returncode, "observation": json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'budget_exhausted'
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path), '--timeout', '0.000001'], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({"source": base64.b64encode(path.read_bytes()).decode(), "command": result.args,
                          "exit_status": result.returncode, "observation": json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'timeout'
        result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path) + '.missing'], capture_output=True, env=ENV, timeout=35, cwd=directory)
        negatives.append({"source": base64.b64encode(path.read_bytes()).decode(), "command": result.args,
                          "exit_status": result.returncode, "observation": json.loads(result.stdout)})
        assert result.returncode != 0 and json.loads(result.stdout)['status'] == 'runner_failure'
        for source in [b'<?php echo $argc;', b'<?php $a=&$argc;',
                       b'<?php $n="argc"; $a=&$$n;', b'<?php unset($GLOBALS);',
                       b'<?php $n="GLOBALS"; unset($$n);']:
            path.write_bytes(source)
            result = subprocess.run([str(ROOT / 'bin/php-semantics'), str(path)], capture_output=True,
                                    env=ENV, timeout=35, cwd=directory)
            response = json.loads(result.stdout)
            assert result.returncode != 0 and response['status'] == 'unsupported', response
            negatives.append({'source': base64.b64encode(source).decode(), 'exit_status': result.returncode,
                              'observation': response})
        # Edited checked values cannot invent source positions for diagnostics.
        for line in (None, -1):
            meta = {} if line is None else {'startLine': {'int': str(line)}}
            expression = {'node': 'Expr_ConstFetch', 'fields': [
                {'node': 'Name', 'fields': [{'bytes': base64.b64encode(b'UNKNOWN_CONST').decode()}], 'meta': {}}], 'meta': meta}
            ast = {'version': 1, 'program': [{'node': 'Stmt_Expression', 'fields': [expression], 'meta': {}}]}
            payload = {'op': 'execute', 'ast': ast, 'steps': 100}
            result = subprocess.run([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                                    input=syntax_validation.wire.dumps(payload), text=True,
                                    capture_output=True, timeout=35, env=ENV, cwd=directory)
            response = syntax_validation.wire.loads(result.stdout)
            assert response.get('ok') and response['state']['COMPLETION']['tag'] == 'UNSUPPORTED', response
            negatives.append({'input': payload, 'exit_status': result.returncode, 'observation': response})
    oracle_info = subprocess.run([str(PHP), '-n', *FLAGS, '-r',
        'echo json_encode(["version"=>PHP_VERSION,"sapi"=>PHP_SAPI,"int_size"=>PHP_INT_SIZE,"zts"=>PHP_ZTS,"extensions"=>get_loaded_extensions()]);'],
        capture_output=True, check=True, env=ENV, timeout=30)
    assert before == fingerprint(), 'implementation changed during run'
    oracle_identity = json.loads(oracle_info.stdout)
    assert (oracle_identity['version'], oracle_identity['sapi'], oracle_identity['int_size'], oracle_identity['zts']) == ('8.5.10', 'cli', 8, False)
    oracle_identity['binary_sha256'] = hashlib.sha256(PHP.read_bytes()).hexdigest()
    oracle_identity['source_commit'] = '34308a6666b2d489c509541ea9befea9e2b42348'
    report = {'budgets': {'transitions': 100000, 'worker_seconds': 30, 'process_seconds': 35}, 'seed': 85010, 'scope': 'authored scalar and variable-storage checked execution fixtures', 'profile': PROFILE,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC'}, 'oracle': oracle_identity,
              'fingerprints': before, 'results': results, 'negative_checks': negatives}
    raw = ROOT / 'coverage/results-semantic-source.jsonl'
    raw.write_text(''.join(json.dumps(result) + '\n' for result in results))
    report['raw_results'] = {'path': str(raw.relative_to(ROOT)),
                             'sha256': hashlib.sha256(raw.read_bytes()).hexdigest(), 'records': len(results)}
    report['results'] = [{'id': result['id'], 'source_sha256': result['source_sha256'],
                          'semantic_status': result['semantic']['status'], 'comparison': result['comparison']}
                         for result in results]
    output = ROOT / 'coverage/semantics/source.json' 
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2) + '\n')
    print(f'{len(results)} differential cases and {len(negatives)} outcome negatives passed')


if __name__ == '__main__':
    main()
