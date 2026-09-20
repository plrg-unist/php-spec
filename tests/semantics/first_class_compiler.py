"""First-class call compilation, line projections and direct-site integrity."""
from pathlib import Path
import base64
import json
import subprocess
import sys
import tempfile

R = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(R / "tests/semantics"))
from recorded_worker import Worker

CASES = [
    (b'<?php function f(){} $c=f(...);', '[PCINDEX 1, PCFIELD 0, PCFIELD 1]', 1, False),
    (b'<?php function f(){} $c="f"(...);', '[PCINDEX 1, PCFIELD 0, PCFIELD 1]', 1, False),
    (b'<?php function f(){} $name="f"; $c=$name(...);', '[PCINDEX 2, PCFIELD 0, PCFIELD 1]', 1, True),
    (b'<?php namespace N; function f(){} $c=f(...);', '[PCINDEX 0, PCFIELD 1, PCINDEX 1, PCFIELD 0, PCFIELD 1]', 1, False),
    (b'<?php function f(){}\n$c=($name=\n"f")(...);', '[PCINDEX 1, PCFIELD 0, PCFIELD 1]', 2, True),
    (b'<?php\nfunction f(){}\nfunction n($x){return "f";}\n$c=n(\n 1\n)(...);', '[PCINDEX 2, PCFIELD 0, PCFIELD 1]', 5, True),
    (b'<?php\nfunction n($x) { return "missing"; }\nn(\n 1\n)(...);\n', '[PCINDEX 1, PCFIELD 0]', 4, True),
    (b'<?php function f1(){return "F";} $c=("f".(1+0))(...); echo $c();\n', '[PCINDEX 1, PCFIELD 0, PCFIELD 1]', 1, True),
]
run_dir = Path(tempfile.mkdtemp(prefix='first-class-compiler-', dir=R / '.tools'))
f = Worker([str(R / '.tools/php/bin/php'), '-n', '-d', 'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], run_dir / 'frontend')
a = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], run_dir / 'adapter')
try:
    with tempfile.TemporaryDirectory(dir=R / '.tools') as directory:
        tests = []
        for i, (source, path, line, evaluated) in enumerate(CASES):
            parsed = f.request({'op': 'parse', 'source': base64.b64encode(source).decode()})
            assert parsed['accepted'], parsed
            checked = a.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
            assert checked['ok'], checked
            test = f'''dec $case{i}() : bool
def $case{i}() = true
  -- if P = $ppstart(91, {checked['fixture']}, [116,101,115,116,46,112,104,112])
  -- if P.COMPLETION = PPCNORMAL
  -- if (CODECALL_INIT ({path}) {line}) <- $ppfunction_code(P).EXPRESSIONS
  -- if (CODEEXPR ({path}) {line} false) <- $ppfunction_code(P).EXPRESSIONS
  -- if $ppaccess(P, {path}) = (PPR)
  -- if $ppaccess(P, {path} ++ [PCFIELD 1]) = eps
'''
            if evaluated:
                test += f'  -- if $ppaccess(P, {path[:-1]}, PCFIELD 0]) = (PPR)\n'
            if i == 0:
                test += '  -- if pcode = $ppfunction_code(P)\n  -- if $dynamic_unit_code_valid(P, pcode[.EXPRESSIONS = $forge_init(pcode.EXPRESSIONS)]) = false\n'
            if i == 7:
                test += f'  -- if $code_name($ppfunction_code(P).NAMES, {path}) = (([102,49], eps))\n'
            tests.append(test)
        fixture = Path(directory) / 'compiler.watsup'
        forge = '''dec $forge_head(pcodeexpr) : pcodeexpr
def $forge_head(CODECALL_INIT pcpath z) = CODECALL_INIT pcpath 99
def $forge_head(pcodeexpr) = pcodeexpr -- otherwise
dec $forge_init(pcodeexpr*) : pcodeexpr*
def $forge_init(eps) = eps
def $forge_init(pcodeexpr :: pcodeexpr_tail*) = $forge_head(pcodeexpr) :: $forge_init(pcodeexpr_tail*)
'''
        fixture.write_text(forge + '\n'.join(tests) + '\ndec $main() : bool\ndef $main() = true\n' + ''.join(f'  -- if $case{i}()\n' for i in range(len(tests))))
        modules = [str(R / path) for path in json.loads((R / 'spec/semantics/modules.json').read_text())]
        command = [str(R / 'tests/semantics/_build/default/numeric_runner.exe'), *modules, str(fixture)]
        result = subprocess.run(command, capture_output=True, text=True, timeout=120)
        print(result.stdout, end='')
        print(result.stderr, file=sys.stderr, end='')
        assert result.returncode == 0 and result.stdout == 'true\n' and not result.stderr
finally:
    f.close()
    a.close()
