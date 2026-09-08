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
    'numeric-types': b'<?php echo (6/3)===2,":",(5/2)===2.5,":",(6.0/3)===2.0,":",(6.0/3)!==2,":",(PHP_INT_MAX+1)===9223372036854775808.0;',
    'numeric-special-identity': b'<?php echo 0.0===-0.0,":",NAN===NAN,":",NAN!==NAN,":",INF===INF;',
    'scalar-strict-identity': b'<?php echo false===null,":",false!==null,":",1!==true,":","1"!==1,":","a"==="a";',
    'numeric-lines-binary': b'<?php\n$a="2x";\n$b="3x";\necho $a\n+\n$b;',
    'numeric-lines-unary': b'<?php\n$a="2x";\necho -\n$a;',
    'numeric-lines-both-missing': b'<?php\necho $a\n+\n$b;',
    'numeric-lines-unary-missing': b'<?php\necho -\n$a;',
    'numeric-lines-division': b'<?php\necho 1\n/\n0;',
    'numeric-lines-rhs-assignment': b'<?php\necho $missing+($a=\n2);',
    'numeric-basic': b'<?php echo 6/3,":",5/2,":",6.0/3,":",(2+3)*4;',
    'numeric-overflow': b'<?php echo PHP_INT_MAX+1,":",PHP_INT_MIN/-1,":",PHP_INT_MAX*PHP_INT_MAX;',
    'numeric-strings': b'<?php echo "01"+1,":"," 1e2 "+1,":","2tail"+3;',
    'numeric-string-error': b'<?php echo "prefix","x"+1;',
    'numeric-string-order': b'<?php echo "2tail"+"x";',
    'numeric-zero-divisor': b'<?php echo "prefix",1/0;',
    'numeric-unary': b'<?php $a="2tail"; echo -$a,":",+true,":",-0.0,":",+null;',
    'numeric-unary-error': b'<?php $a="x"; echo -$a;',
    'numeric-float-literals': b'<?php echo 1.2345678901234567,":",1e-300,":",5e-324,":",1e309;',
    'numeric-nan-output': b'<?php echo NAN,":",INF,":",-INF;',
    'numeric-nan-variable-name': b'<?php $n=NAN; $$n=1; echo $$n; unset($$n);',
    'numeric-nan-reference-name': b'<?php $n=NAN; $a=&$$n; $a=7; echo $$n;',
    'numeric-delayed-read': b'<?php $a=1;echo $a+($a=2),":",$a;',
    'numeric-captured-read': b'<?php $a=1;$n="a";echo $$n+($a=2),":",$a;',
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


CASES.update({
    'array-nested-key-delayed': b'<?php $a=[[1],[2]];$i=0;echo $a[$i][(($i=1)===1)-1];',
    'array-nested-key-captured': b'<?php $a=[[1],[2]];$i=0;$n="i";echo $a[$$n][(($i=1)===1)-1];',
    'array-nested-root-delayed': b'<?php $a=[[1]];echo $a[0][($a=[[2]])[0][0]-2];',
    'array-nested-root-captured': b'<?php echo ($a=[[1]])[0][($a=[[2]])[0][0]-2];',

    'array-dynamic-base-delayed': b'<?php $a=[1];$n="a";echo $$n[($a=[2])[0]-2];',
    'array-dynamic-base-name-delayed': b'<?php $a=[1];$b=[2];$n="a";echo $$n[(($n="b")==="b")-1];',
    'array-dynamic-base-name-captured': b'<?php $a=[1];$b=[2];$n="a";echo ${($n="a")}[ (($n="b")==="b")-1 ];',
    'array-captured-name-base-delayed': b'<?php $a=[1];$n="a";echo ${($n="a")}[($a=[2])[0]-2];',

    'array-unary-fold-line': b'<?php\necho [\n-\n1,\n2\n];',
    'array-nan-shared-identity': b'<?php $a=[NAN];$b=$a;echo $a===$a,$a===$b;echo [NAN]===[NAN];$b=$a+[];echo $a===$b;',
    'array-nested-fold-line': b'<?php\necho [\n[3][0]-1,\n9\n];',
    'array-basic': b'<?php\n$a=[1,2];echo $a[0],$a[1];',
    'array-identity': b'<?php\necho [1] === [1], [1]!==[1.0], [1,2]!==[1=>2,0=>1], [[1]] === [[1]];',
    'array-union': b'<?php\n$a=[1,2]+[0=>3,2=>4,"x"=>5];echo $a[0],$a[1],$a[2],$a["x"];',
    'array-keydelayed': b'<?php\n$k=0;$a=[$k=>($k=1)];echo $a[1];',
    'array-keycaptured': b'<?php\n$k=0;$n="k";$a=[$$n=>($k=1)];echo $a[0];',
    'array-keymissing': b'<?php\n$a=[$missing=>1];echo $a[""];',
    'array-keydynamicmissing': b'<?php\n$n="missing";$a=[$$n=>1];echo $a[""];',
    'array-keynull': b'<?php\n$a=[null=>1];echo $a[null];',
    'array-floatkey': b'<?php\n$a=[1.5=>1,INF=>2,NAN=>3];echo $a[1],$a[0];',
    'array-negative': b'<?php\n$a=[-5=>1,2,3];echo $a[-5],$a[-4],$a[-3];',
    'array-max': b'<?php\n$a=[PHP_INT_MAX=>1,2];',
    'array-missing': b'<?php\n$a=[];echo $a["a"],$a[1];',
    'array-arrayecho': b'<?php\necho [\n1,\n2\n];',
    'array-arrayechodynamic': b'<?php\n$a=1;echo [\n1,\n$a\n];',
    'array-keyline': b'<?php\n$a=[\nnull=>\n1\n];echo $a[\nnull\n];',
    'array-keyfloatline': b'<?php\n$a=[\n1.5=>\n1\n];',
    'array-nestedline': b'<?php\necho [\n[\n1\n]\n];',
    'array-dimline': b'<?php\n$a=[];echo $a[\n"a"\n];',
    'array-dimdelayed': b'<?php\n$a=[1,2];echo $a[($a=[3,4])[0]-3];',
    'array-missing-nul': b'<?php\n$a=[];echo $a["a\\0b"],$a["a\\nb"];',
    'array-missing-cv-dimension': b'<?php\n$a=[];echo $a[$missing];',
    'array-missing-both': b'<?php\n$a=[$missingkey=>$missingvalue];echo $a[""];',
    'array-key-by-value-copy': b'<?php\n$a=[1,2];$b=$a;$a=[3];echo $b[0],$b[1],$a[0];',
    'array-key-collision-types': b'<?php\n$a=[1=>"a","1"=>"b",true=>"c",1.0=>"d",null=>"e",false=>"f",0=>"g"];echo $a[1],$a[0],$a[""];',
    'array-key-canonical-strings': b'<?php\n$a=["01"=>1,"+1"=>2,"-0"=>3,"1 "=>4,"-1"=>5,"9223372036854775808"=>6];echo $a["01"],$a["+1"],$a["-0"],$a["1 "],$a[-1],$a["9223372036854775808"];',
    'array-key-int-min': b'<?php\n$a=[PHP_INT_MIN=>1,2];echo $a[PHP_INT_MIN],$a[PHP_INT_MIN+1];',
    'array-key-int-max-replace': b'<?php\n$a=[PHP_INT_MAX=>1,PHP_INT_MAX=>2];echo $a[PHP_INT_MAX];',
    'array-array-mixed-operators': b'<?php\necho []===null,":",[]!==false,":",[]===[],":",[]+[1];',
    'array-array-type-error': b'<?php\necho "prefix",[1]-[1];',
    'array-array-scalar-type-error': b'<?php\necho "prefix",1+[1];',
    'array-array-unary-type-error': b'<?php\necho "prefix",-[1];',
    'array-array-name-runtime': b'<?php\n$a=[];$$a=1;echo $$a;',
    'array-array-name-dynamic-literal': b'<?php\n$a=1;${[$a]}=2;echo $Array;',
    'array-array-name-nonfold-key': b'<?php\n${[null=>1]}=2;echo $Array;',
    'array-empty-array-line': b'<?php\necho [\n\n];',
    'array-keyed-array-line': b'<?php\necho [\n"key"=>\n1\n];',
    'array-nested-constant-arithmetic-line': b'<?php\necho [\n[1]+[2],\n3\n];',
    'array-nested-constant-dim-line': b'<?php\necho [\n[1][0],\n3\n];',
    'array-nested-dynamic-array-line': b'<?php\n$x=1;echo [\n[\n$x\n]\n];',
    'array-literal-captured-array': b'<?php\n$a=[1];$n="a";$b=[$$n,($a=[2])];echo $b[0][0],$b[1][0];',
    'array-literal-delayed-array': b'<?php\n$a=[1];$b=[$a,($a=[2])];echo $b[0][0],$b[1][0];',
    'array-dimension-key-mutation': b'<?php\n$a=["x"=>1];$k="x";echo $a[($k="x")];',
    'array-nested-dimension-lookup-line': b'<?php\n$a=[[]];echo $a[\n0\n][\n"missing"\n];',
})

CASES.update({
    'array-write-basic': b'<?php\n$a=[];$a[0]=1;$a["x"]=2;echo $a[0],$a["x"];',
    'array-write-nested': b'<?php\n$a=[];$a[0][1]=2;echo $a[0][1];',
    'array-write-append': b'<?php\n$a[]=1;$a[]=2;echo $a[0],$a[1];',
    'array-write-nestedappend': b'<?php\n$a[][]=1;$a[][]=2;echo $a[0][0],$a[1][0];',
    'array-write-copy': b'<?php\n$a=[1];$b=$a;$a[0]=2;echo $a[0],$b[0];',
    'array-write-nestedcopy': b'<?php\n$a=[[1]];$b=$a;$a[0][0]=2;echo $a[0][0],$b[0][0];',
    'array-write-rootrefs': b'<?php\n$a=[1];$b=&$a;$c=$a;$b[0]=2;echo $a[0],$b[0],$c[0];',
    'array-write-nestedrootrefs': b'<?php\n$a=[[1]];$b=&$a;$c=$a;$b[0][0]=2;echo $a[0][0],$b[0][0],$c[0][0];',
    'array-write-false': b'<?php\n$a=false;$a[0]=1;echo $a[0];',
    'array-write-falseinner': b'<?php\n$a=[false];$a[0][0]=1;echo $a[0][0];',
    'array-write-null': b'<?php\n$a=null;$a[0]=1;echo $a[0];',
    'array-write-nullkey': b'<?php\n$a[null]=1;echo $a[""];',
    'array-write-floatkey': b'<?php\n$a[1.5]=1;echo $a[1];',
    'array-write-keyerror': b'<?php\n$a[[]]=1;',
    'array-write-scalarerror': b'<?php\n$a=true;$a[$missing]=$value;',
    'array-write-keyrhswarnings': b'<?php\n$a[$missing]=$value;',
    'array-write-appendrhswarning': b'<?php\n$a[]=$missing;echo $a[0];',
    'array-write-overflowrhswarning': b'<?php\n$a=[PHP_INT_MAX=>1];$a[]=$missing;',
    'array-write-negativehistory': b'<?php\n$a=[-5=>1];$a[]=2;echo $a[-5],$a[-4];',
    'array-write-selfmissing': b'<?php\n$a[0]=$a;echo $a[0]===null;',
    'array-write-selfappendmissing': b'<?php\n$a[]=$a;echo $a[0]===null;',
    'array-write-selfexisting': b'<?php\n$a=[];$a[0]=$a;echo $a[0]===[];',
    'array-write-selfappendexisting': b'<?php\n$a=[];$a[]=$a;echo $a[0]===[];',
    'array-write-aliasself': b'<?php\n$a=[];$b=&$a;$a[0]=$b;echo $a===$a[0];',
    'array-write-dynamicself': b'<?php\n$a=[];$n="a";$$n[0]=$a;echo $a===$a[0];',
    'array-write-cycliccomparison': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$c=[];$d=&$c;$c[0]=$d;echo $a===$c;',
    'array-write-cyclelength': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$c=[];$d=&$c;$c[0]=$d;$c[1]=1;echo $a===$c;',
    'array-write-cyclemutation': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$a[1]=2;echo $a[0]===$a,$a[0]===$a[0][0];',
    'array-write-keydelayed': b'<?php\n$a=[];$i=0;$a[$i]=($i=1);echo $a[1];',
    'array-write-keycaptured': b'<?php\n$a=[];$i=0;$n="i";$a[$$n]=($i=1);echo $a[0];',
    'array-write-rootchanged': b'<?php\n$a=[1];$a[0]=($a=[2]);echo $a[0][0];',
    'array-write-linewrite': b'<?php\n$a[\nnull\n]=\n$missing;',
    'array-write-lineself': b'<?php\n$a[\n0\n]=\n$a;',
    'array-write-linefalse': b'<?php\n$a=false;$a[\n0\n]=\n1;',
    'array-write-lineechoassignment': b'<?php\necho ($a[\n0\n]=\n[]);',
    'array-write-nestedkeyeffects': b'<?php\n$a=[];$i=0;$a[$i][(($i=1)===1)-1]=2;echo $a[1][0];',
    'array-write-nestedrhseffects': b'<?php\n$a=[];$i=0;$a[$i][0]=($i=1);echo $a[1][0];',
})

CASES.update({
    'array-write-review-cycle-write-after': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$a[1]=1;echo $a[0]===$a, $a[0][0]===$a[0];',
    'array-write-review-cycle-nested-write': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$a[0][1]=1;echo $a[0][0]===$a[0],$a[0][1];',
    'array-write-review-cycle-count-shortcircuit': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$c=[];$d=&$c;$c[0]=$d;$c[1]=1;echo $a===$c;',
    'array-write-review-cycle-key-shortcircuit': b'<?php\n$a=[];$b=&$a;$a[0]=$b;$c=[];$d=&$c;$c[1]=$d;echo $a===$c;',
    'array-write-review-self-key-aliases-root': b'<?php\n$a=[1];$b=[2];$a[($a=&$b)[0]]=$a;echo $a[0],$a[2][0],$b[2][0];',
    'array-write-review-nested-rhs-assign-root': b'<?php\n$a=[[1]];$a[0][0]=($a=[[2]]);echo $a[0][0][0][0];',
    'array-write-review-nan-nested-identical-overwrite': b'<?php\n$x=[NAN];$a=[$x];$b=$a;$a[0]=$x;echo $a===$b;',
    'array-write-review-key-error-rhs-throw': b'<?php\n$a=[];$a[[]]=1/0;',
})

# Independent review-authored witnesses keep their original provenance.
CONFORMANCE = ['reference-rebind', 'dynamic-variable', 'delayed-read', 'array-alias-self-cycle', 'array-captured-lhs-key', 'array-captured-lhs-name', 'array-delayed-lhs-key', 'array-delayed-lhs-name', 'array-distinct-cycle-comparison', 'array-dynamic-self-cycle', 'array-nested-self-index', 'array-rhs-overwrites-root', 'array-self-append', 'array-self-index', 'array-self-key-side-effect']
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


# Review-authored scalar cross-product seed, independent of evaluator clauses.
scalar_values = ['null', 'false', 'true', '0', '-1', 'PHP_INT_MAX', 'PHP_INT_MIN',
                 '0.0', '-0.0', '1.5', 'INF', 'NAN', '""', '"x"', '"2tail"', '" 3 "', '"1e999"']
rng = random.Random(6614)
for number in range(80):
    left, right = rng.choice(scalar_values), rng.choice(scalar_values)
    operator = rng.choice(['+', '-', '*', '/', '===', '!=='])
    CASES[f'generated-scalar-{number:02}'] = f'<?php\n$a={left};$b={right};echo $a {operator} $b;'.encode()


# Independent reviewer key-collision seed exercises canonicalization and ordering.
array_keys = ['0', '-1', '1.2', 'null', 'true', 'false', '"1"', '"01"',
              '"+1"', '"-0"', 'PHP_INT_MIN', 'PHP_INT_MAX']
rng = random.Random(7116)
for number in range(40):
    first, second, third = [rng.choice(array_keys) for _ in range(3)]
    CASES[f'generated-array-keys-{number:02}'] = (
        f'<?php\n$a=[{first}=>1,{second}=>2,{third}=>3];'
        f'echo $a[{first}],$a[{second}],$a[{third}];').encode()


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
        path.write_bytes(b'<?php echo PHP_VERSION;')
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
                       b'<?php $n="GLOBALS"; unset($$n);', b'<?php echo $missing; ${NAN}=1;',
                       b'<?php echo $missing; ${INF-INF}=1;',
                       b'<?php echo MISSING; ${[]}=1;', b'<?php echo MISSING; ${[1]+[2]}=1;',
                       b'<?php $x=1;$a=[&$x];', b'<?php $a=[];unset($a[0]);',
                       b'<?php $a=[...[]];', b'<?php $a=[[]=>1];']:
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
    # Numeric warnings/errors also require source context on edited checked ASTs.
    for expression in [
        {'node': 'Scalar_Float', 'fields': [{'float': '7ff8000000000000'}], 'meta': {}},
        {'node': 'Expr_BinaryOp_Div', 'fields': [
            {'node': 'Scalar_Int', 'fields': [{'int': '1'}], 'meta': {}},
            {'node': 'Scalar_Int', 'fields': [{'int': '0'}], 'meta': {}}], 'meta': {}}]:
        payload = {'op': 'execute', 'steps': 100, 'ast': {'version': 1, 'program': [
            {'node': 'Stmt_Echo', 'fields': [[expression]], 'meta': {}}]}}
        result = subprocess.run([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)],
                                input=syntax_validation.wire.dumps(payload), text=True,
                                capture_output=True, timeout=35, env=ENV)
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
    report = {'budgets': {'transitions': 100000, 'worker_seconds': 30, 'process_seconds': 35}, 'seeds': {'alias': 85010, 'scalar': 6614, 'array_keys': 7116}, 'scope': 'authored scalar, variable storage and ordinary array literal/read/write checked execution fixtures', 'profile': PROFILE,
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
