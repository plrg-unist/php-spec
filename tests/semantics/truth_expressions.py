#!/usr/bin/env python3
"""Checked-source truth expressions, compiler redirects, and value ownership."""
import base64, json, re, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types

NORMAL_CASES = {
    'not-truth': b'<?php $x="0";echo !$x;$x="00";echo !$x;$x=[];echo !$x;',
    'not-nan': b'<?php echo !NAN;',
    'and-skip': b'<?php $x=false;echo $x && ($y=1);echo $y;',
    'or-skip': b'<?php $x=true;echo $x || ($y=1);echo $y;',
    'and-right': b'<?php $x=true;echo $x && ($y=1);echo $y;',
    'or-right': b'<?php $x=false;echo $x || ($y=1);echo $y;',
    'word-logical': b'<?php $x=false;echo ($x or ($y=1));echo $y;echo ($y and ($x=2));echo $x;',
    'dynamic-nan-and': b'<?php $x=NAN;echo $x && true;',
    'dynamic-nan-or': b'<?php $x=NAN;echo $x || false;',
    'dynamic-nan-right': b'<?php $x=false;echo $x || NAN;',
    'ternary-capture': b'<?php $x=1;$c=true;echo ($c ? $x : 9)+($x=2);',
    'ternary-false-capture': b'<?php $x=1;$c=false;echo ($c ? 9 : $x)+($x=2);',
    'ternary-short-capture': b'<?php $x=1;echo ($x ?: 9)+($x=2);',
    'ternary-nan': b'<?php echo NAN ? 1 : 2;',
    'ternary-short-nan': b'<?php echo NAN ?: 2;',
    'ternary-array-cow': b'<?php $a=[1];$c=true;$b=$c ? $a : []; $b[0]=2;echo $a[0],$b[0];',
    'ternary-reference-copy': b'<?php $x=1;$a=[&$x];$c=true;echo ($c ? $a[0] : 9)+($x=2);',
    'ternary-short-false': b'<?php $a=[];echo ($a ?: [1])[0];',
    'xor-delayed': b'<?php $a=false;echo ($a xor ($a=true));',
    'xor-nan-dynamic': b'<?php $a=NAN;$b=NAN;echo ($a xor $b);',
    'xor-array': b'<?php $a=[1];echo ($a xor []);',
    'ternary-refassign-copy': b'<?php $x=1;$c=true;echo ($c ? ($r=&$x) : 9)+($x=2);echo $r;',
    'ternary-short-refassign-copy': b'<?php $x=1;echo (($r=&$x) ?: 9)+($x=2);echo $r;',
    'ternary-dynamic-key': b'<?php $a=[1];$c=true;echo ($c ? $a[0] : 9)+($a[0]=2);',
    'ternary-short-dimension': b'<?php $a=[1];echo ($a[0] ?: 9)+($a[0]=2);',
    'ternary-skips-unset-value': b'<?php $x=true;echo $x ? 7 : $missing;',
    'ternary-short-false-missing': b'<?php $x=false;echo $x ?: $missing;',
    'xor-delayed-nan': b'<?php $x=false;echo ($x xor ($x=NAN));',
    'not-dimension-reference': b'<?php $x=0;$a=[&$x];echo !$a[0];',
    'loop-truth-roots': b'<?php $x=0;$a=[1];while($x!==3){$c=$x!==1;$b=$c ? $a : [];echo ($c && ($y=$x+1));echo ($b ?: [9])[0];$a[0]=$x;$x=$x+1;}',
    'loop-truth-nan': b'<?php $x=0;$nan=NAN;while($x!==3){echo ($nan && ($x!==1));echo ($nan ? $x : 9);$x=$x+1;}',
    'runtime-phase-skip-and': b'<?php echo false && [&$x[]];',
    'runtime-phase-skip-or': b'<?php echo true || [&$x[]];',
    'runtime-phase-skip-import-warning': b'<?php echo false && [${NAN}=1];',
    'runtime-phase-nan-and': b'<?php echo NAN && true;',
    'runtime-phase-nan-or': b'<?php echo NAN || false;',
    'runtime-phase-dynamic-nan': b'<?php namespace N;echo NAN && true;',
    'runtime-phase-constant-expression-left': b'<?php echo (1-1) && [&$x[]];',
    'independent-prepass-false-and-bare': b'<?php\necho "before";\necho (false && [&$q[]]);',
    'independent-prepass-false-and-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(false && [&$q[]]))];echo $a[0];',
    'independent-prepass-true-or-bare': b'<?php\necho "before";\necho (true || [&$q[]]);',
    'independent-prepass-true-or-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(true || [&$q[]]))];echo $a[0];',
    'independent-prepass-true-ternary-array': b'<?php\necho "before";\n$a=[(true ? 1 : [&$q[]])];echo $a[0];',
    'independent-prepass-true-short-array': b'<?php\necho "before";\n$a=[(true ?: [&$q[]])];echo $a[0];',
    'independent-prepass-nonconstant-selected-array': b'<?php\necho "before";\n$a=[(true ? $x : [&$q[]])];echo $a[0];',
    'independent-prepass-false-nonconstant-selected-array': b'<?php\necho "before";\n$a=[(false ? [&$q[]] : $x)];echo $a[0];',
    'independent-prepass-nan-and-bare': b'<?php\necho "before";\necho (NAN && true);',
    'independent-prepass-nan-and-array': b'<?php\necho "before";\n$a=[(NAN && true)];echo $a[0];',
    'independent-prepass-nan-and-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(NAN && true))];echo $a[0];',
    'independent-prepass-nan-or-bare': b'<?php\necho "before";\necho (NAN || false);',
    'independent-prepass-nan-or-array': b'<?php\necho "before";\n$a=[(NAN || false)];echo $a[0];',
    'independent-prepass-nan-or-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(NAN || false))];echo $a[0];',
    'independent-prepass-nan-not-bare': b'<?php\necho "before";\necho (!NAN);',
    'independent-prepass-nan-not-array': b'<?php\necho "before";\n$a=[(!NAN)];echo $a[0];',
    'independent-prepass-nan-not-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(!NAN))];echo $a[0];',
    'independent-prepass-nan-ternary-bare': b'<?php\necho "before";\necho (NAN ? 1 : 2);',
    'independent-prepass-nan-ternary-array': b'<?php\necho "before";\n$a=[(NAN ? 1 : 2)];echo $a[0];',
    'independent-prepass-nan-ternary-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(NAN ? 1 : 2))];echo $a[0];',
    'independent-prepass-nan-short-bare': b'<?php\necho "before";\necho (NAN ?: 2);',
    'independent-prepass-nan-short-array': b'<?php\necho "before";\n$a=[(NAN ?: 2)];echo $a[0];',
    'independent-prepass-nan-short-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(NAN ?: 2))];echo $a[0];',
    'independent-copy-ordinary-cv': b'<?php $x=1;echo (true?$x:0)+($x=2);',
    'independent-copy-prepass-cv': b'<?php $x=1;$a=[(true?$x:0)+($x=2)];echo $a[0];',
    'independent-copy-ordinary-ref': b'<?php $x=1;echo (true?($r=&$x):0)+($x=2);',
    'independent-copy-prepass-ref': b'<?php $x=1;$a=[(true?($r=&$x):0)+($x=2)];echo $a[0];',
    'independent-copy-ordinary-shorthand-cv': b'<?php $x=1;echo ($x?:0)+($x=2);',
    'independent-copy-prepass-selected-array': b'<?php $x=[NAN];$a=[(true?$x:0)===($x=[NAN])];echo $a[0];',
    'independent-copy-ordinary-selected-array': b'<?php $x=[NAN];echo (true?$x:0)===($x=[NAN]);',
    'independent-copy-prepass-short-assign': b'<?php $x=1;$a=[(true?($r=&$x):0)+(($r=2)+($x=3))];echo $a[0];',
    'independent-grouping-1': b'<?php echo [true?1:2?3:4][0];',
    'independent-grouping-3': b'<?php echo false && (true?1:2?3:4);',
}
CASES = {
    'truth-not-truth': b'<?php $x="0";echo !$x;$x="00";echo !$x;$x=[];echo !$x;',
    'truth-not-nan': b'<?php echo !NAN;',
    'truth-and-skip': b'<?php $x=false;echo $x && ($y=1);echo $y;',
    'truth-or-skip': b'<?php $x=true;echo $x || ($y=1);echo $y;',
    'truth-and-right': b'<?php $x=true;echo $x && ($y=1);echo $y;',
    'truth-or-right': b'<?php $x=false;echo $x || ($y=1);echo $y;',
    'truth-word-logical': b'<?php $x=false;echo ($x or ($y=1));echo $y;echo ($y and ($x=2));echo $x;',
    'truth-dynamic-nan-and': b'<?php $x=NAN;echo $x && true;',
    'truth-dynamic-nan-or': b'<?php $x=NAN;echo $x || false;',
    'truth-dynamic-nan-right': b'<?php $x=false;echo $x || NAN;',
    'truth-ternary-capture': b'<?php $x=1;$c=true;echo ($c ? $x : 9)+($x=2);',
    'truth-ternary-false-capture': b'<?php $x=1;$c=false;echo ($c ? 9 : $x)+($x=2);',
    'truth-ternary-short-capture': b'<?php $x=1;echo ($x ?: 9)+($x=2);',
    'truth-ternary-nan': b'<?php echo NAN ? 1 : 2;',
    'truth-ternary-short-nan': b'<?php echo NAN ?: 2;',
    'truth-ternary-array-cow': b'<?php $a=[1];$c=true;$b=$c ? $a : []; $b[0]=2;echo $a[0],$b[0];',
    'truth-ternary-reference-copy': b'<?php $x=1;$a=[&$x];$c=true;echo ($c ? $a[0] : 9)+($x=2);',
    'truth-ternary-short-false': b'<?php $a=[];echo ($a ?: [1])[0];',
    'truth-xor-delayed': b'<?php $a=false;echo ($a xor ($a=true));',
    'truth-xor-nan-dynamic': b'<?php $a=NAN;$b=NAN;echo ($a xor $b);',
    'truth-xor-array': b'<?php $a=[1];echo ($a xor []);',
    'truth-ternary-refassign-copy': b'<?php $x=1;$c=true;echo ($c ? ($r=&$x) : 9)+($x=2);echo $r;',
    'truth-ternary-short-refassign-copy': b'<?php $x=1;echo (($r=&$x) ?: 9)+($x=2);echo $r;',
    'truth-ternary-dynamic-key': b'<?php $a=[1];$c=true;echo ($c ? $a[0] : 9)+($a[0]=2);',
    'truth-ternary-short-dimension': b'<?php $a=[1];echo ($a[0] ?: 9)+($a[0]=2);',
    'truth-ternary-skips-unset-value': b'<?php $x=true;echo $x ? 7 : $missing;',
    'truth-ternary-short-false-missing': b'<?php $x=false;echo $x ?: $missing;',
    'truth-xor-delayed-nan': b'<?php $x=false;echo ($x xor ($x=NAN));',
    'truth-not-dimension-reference': b'<?php $x=0;$a=[&$x];echo !$a[0];',
    'truth-loop-truth-roots': b'<?php $x=0;$a=[1];while($x!==3){$c=$x!==1;$b=$c ? $a : [];echo ($c && ($y=$x+1));echo ($b ?: [9])[0];$a[0]=$x;$x=$x+1;}',
    'truth-loop-truth-nan': b'<?php $x=0;$nan=NAN;while($x!==3){echo ($nan && ($x!==1));echo ($nan ? $x : 9);$x=$x+1;}',
    'truth-runtime-phase-skip-and': b'<?php echo false && [&$x[]];',
    'truth-runtime-phase-skip-or': b'<?php echo true || [&$x[]];',
    'truth-runtime-phase-visit-and': b'<?php echo true && [&$x[]];',
    'truth-runtime-phase-visit-or': b'<?php echo false || [&$x[]];',
    'truth-runtime-phase-skip-import-warning': b'<?php echo false && [${NAN}=1];',
    'truth-runtime-phase-nan-and': b'<?php echo NAN && true;',
    'truth-runtime-phase-nan-or': b'<?php echo NAN || false;',
    'truth-runtime-phase-full-ternary-static': b'<?php echo true ? 1 : [&$x[]];',
    'truth-runtime-phase-shorthand-ternary-static': b'<?php echo true ?: [&$x[]];',
    'truth-runtime-phase-dynamic-nan': b'<?php namespace N;echo NAN && true;',
    'truth-runtime-phase-constant-expression-left': b'<?php echo (1-1) && [&$x[]];',
    'truth-runtime-phase-dynamic-left': b'<?php $x=false;echo $x && [&$y[]];',
    'truth-independent-prepass-false-and-bare': b'<?php\necho "before";\necho (false && [&$q[]]);',
    'truth-independent-prepass-false-and-array': b'<?php\necho "before";\n$a=[(false && [&$q[]])];echo $a[0];',
    'truth-independent-prepass-false-and-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(false && [&$q[]]))];echo $a[0];',
    'truth-independent-prepass-true-or-bare': b'<?php\necho "before";\necho (true || [&$q[]]);',
    'truth-independent-prepass-true-or-array': b'<?php\necho "before";\n$a=[(true || [&$q[]])];echo $a[0];',
    'truth-independent-prepass-true-or-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(true || [&$q[]]))];echo $a[0];',
    'truth-independent-prepass-true-ternary-bare': b'<?php\necho "before";\necho (true ? 1 : [&$q[]]);',
    'truth-independent-prepass-true-ternary-array': b'<?php\necho "before";\n$a=[(true ? 1 : [&$q[]])];echo $a[0];',
    'truth-independent-prepass-true-ternary-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(true ? 1 : [&$q[]]))];echo $a[0];',
    'truth-independent-prepass-true-short-bare': b'<?php\necho "before";\necho (true ?: [&$q[]]);',
    'truth-independent-prepass-true-short-array': b'<?php\necho "before";\n$a=[(true ?: [&$q[]])];echo $a[0];',
    'truth-independent-prepass-true-short-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(true ?: [&$q[]]))];echo $a[0];',
    'truth-independent-prepass-nonconstant-selected-bare': b'<?php\necho "before";\necho (true ? $x : [&$q[]]);',
    'truth-independent-prepass-nonconstant-selected-array': b'<?php\necho "before";\n$a=[(true ? $x : [&$q[]])];echo $a[0];',
    'truth-independent-prepass-nonconstant-selected-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(true ? $x : [&$q[]]))];echo $a[0];',
    'truth-independent-prepass-false-nonconstant-selected-bare': b'<?php\necho "before";\necho (false ? [&$q[]] : $x);',
    'truth-independent-prepass-false-nonconstant-selected-array': b'<?php\necho "before";\n$a=[(false ? [&$q[]] : $x)];echo $a[0];',
    'truth-independent-prepass-false-nonconstant-selected-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(false ? [&$q[]] : $x))];echo $a[0];',
    'truth-independent-prepass-dynamic-condition-bare': b'<?php\necho "before";\necho ($x ? 1 : [&$q[]]);',
    'truth-independent-prepass-dynamic-condition-array': b'<?php\necho "before";\n$a=[($x ? 1 : [&$q[]])];echo $a[0];',
    'truth-independent-prepass-dynamic-condition-assignment-barrier': b'<?php\necho "before";\n$a=[($z=($x ? 1 : [&$q[]]))];echo $a[0];',
    'truth-independent-prepass-nan-and-bare': b'<?php\necho "before";\necho (NAN && true);',
    'truth-independent-prepass-nan-and-array': b'<?php\necho "before";\n$a=[(NAN && true)];echo $a[0];',
    'truth-independent-prepass-nan-and-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(NAN && true))];echo $a[0];',
    'truth-independent-prepass-nan-or-bare': b'<?php\necho "before";\necho (NAN || false);',
    'truth-independent-prepass-nan-or-array': b'<?php\necho "before";\n$a=[(NAN || false)];echo $a[0];',
    'truth-independent-prepass-nan-or-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(NAN || false))];echo $a[0];',
    'truth-independent-prepass-nan-not-bare': b'<?php\necho "before";\necho (!NAN);',
    'truth-independent-prepass-nan-not-array': b'<?php\necho "before";\n$a=[(!NAN)];echo $a[0];',
    'truth-independent-prepass-nan-not-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(!NAN))];echo $a[0];',
    'truth-independent-prepass-nan-ternary-bare': b'<?php\necho "before";\necho (NAN ? 1 : 2);',
    'truth-independent-prepass-nan-ternary-array': b'<?php\necho "before";\n$a=[(NAN ? 1 : 2)];echo $a[0];',
    'truth-independent-prepass-nan-ternary-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(NAN ? 1 : 2))];echo $a[0];',
    'truth-independent-prepass-nan-short-bare': b'<?php\necho "before";\necho (NAN ?: 2);',
    'truth-independent-prepass-nan-short-array': b'<?php\necho "before";\n$a=[(NAN ?: 2)];echo $a[0];',
    'truth-independent-prepass-nan-short-assignment-barrier': b'<?php\necho "before";\n$a=[($z=(NAN ?: 2))];echo $a[0];',
    'truth-independent-copy-ordinary-cv': b'<?php $x=1;echo (true?$x:0)+($x=2);',
    'truth-independent-copy-prepass-cv': b'<?php $x=1;$a=[(true?$x:0)+($x=2)];echo $a[0];',
    'truth-independent-copy-ordinary-ref': b'<?php $x=1;echo (true?($r=&$x):0)+($x=2);',
    'truth-independent-copy-prepass-ref': b'<?php $x=1;$a=[(true?($r=&$x):0)+($x=2)];echo $a[0];',
    'truth-independent-copy-ordinary-shorthand-cv': b'<?php $x=1;echo ($x?:0)+($x=2);',
    'truth-independent-copy-prepass-selected-array': b'<?php $x=[NAN];$a=[(true?$x:0)===($x=[NAN])];echo $a[0];',
    'truth-independent-copy-ordinary-selected-array': b'<?php $x=[NAN];echo (true?$x:0)===($x=[NAN]);',
    'truth-independent-copy-prepass-short-assign': b'<?php $x=1;$a=[(true?($r=&$x):0)+(($r=2)+($x=3))];echo $a[0];',
    'truth-independent-grouping-0': b'<?php echo true?1:2?3:4;',
    'truth-independent-grouping-1': b'<?php echo [true?1:2?3:4][0];',
    'truth-independent-grouping-2': b'<?php $x=true;echo [$x?1:2?3:4][0];',
    'truth-independent-grouping-3': b'<?php echo false && (true?1:2?3:4);',
}

# Preserve the extra compiler-order/error sources beside the archived witnesses.
CASES.update({
    'truth-compiler-warnings-before-later-failure': b'<?php use A; echo NAN || false; echo [&$x[]]; use B;',
    'truth-compiler-warnings-after-earlier-failure': b'<?php use A; echo [&$x[]]; echo NAN || false; use B;',
    'truth-compiler-constant-left-dynamic-right': b'<?php $x=1;echo NAN && $x;',
    'truth-compiler-constant-left-late-right': b'<?php namespace N; echo true && NAN;',
    'truth-compiler-prepass-logical-constant-left-dynamic-right': b'<?php $a=[NAN && $x];',
    'truth-compiler-prepass-short-nan': b'<?php $a=[NAN ?: $x];',
    'truth-compiler-prepass-ternary-line': b'<?php $a=[\n NAN\n ?\n $x\n :\n $y\n ];',
    'truth-compiler-ordinary-logical-line': b'<?php echo NAN\n ||\n false;',
    'truth-compiler-ordinary-logical-right-line': b'<?php echo true\n &&\n NAN;',
    'truth-compiler-prepass-logical-line': b'<?php $a=[\n NAN\n ||\n false\n ];',
    'truth-compiler-ordinary-xor-line': b'<?php echo (NAN\n xor\n NAN);',
    'truth-compiler-prepass-xor-line': b'<?php $a=[\n NAN\n xor\n NAN\n ];',
    'truth-compiler-ordinary-not-finite-float': b'<?php echo !1.0;',
    'truth-compiler-prepass-not-finite-float': b'<?php $a=[!1.0];',
    'truth-compiler-prepass-grouping-erased-dynamic-child': b'<?php echo [(true ? $x : 0) ? $y : 0];',
    'truth-compiler-prepass-grouping-erased-invalid-unselected': b'<?php echo [true ? $x : (true ? 1 : 2 ? 3 : 4)];',
})

PREFIX = '''
var U : pcunit
dec $outputs(pevent*) : nat*
def $outputs(eps) = eps
def $outputs((OUTPUT n*) :: pevent*) = n* ++ $outputs(pevent*)
def $outputs((WARNING n* z) :: pevent*) = $outputs(pevent*)
def $outputs((DIAGNOSTIC text n* z) :: pevent*) = $outputs(pevent*)
dec $messages(pevent*) : pevent*
def $messages(eps) = eps
def $messages((OUTPUT n*) :: pevent*) = $messages(pevent*)
def $messages((WARNING n* z) :: pevent*) = (WARNING n* z) :: $messages(pevent*)
def $messages((DIAGNOSTIC text n* z) :: pevent*) = (DIAGNOSTIC text n* z) :: $messages(pevent*)
'''

def byte_sequence(value):
    return '(['+','.join(map(str,value))+'])'

def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(ROOT/'tests/semantics'),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    specs=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    before=types.syntax_validation.implementation_fingerprint()
    frontend=types.Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    records=[]; assertions=[]
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            source_path=Path(tmp)/'truth.php'
            for name,source in NORMAL_CASES.items():
                source_path.write_bytes(source)
                native=subprocess.run([str(types.PHP),'-n',*types.FLAGS,str(source_path)],capture_output=True,env=types.ENV,timeout=10)
                assert native.returncode==0,(name,native.stdout,native.stderr)
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],parsed
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok'],checked
                events=[]
                for severity,message,line in re.findall(rb'(Warning|Deprecated): (.*?) in .*? on line (\d+)',native.stderr):
                    if message.startswith(b'Undefined variable $'):
                        events.append('WARNING '+byte_sequence(message.removeprefix(b'Undefined variable $'))+' '+line.decode())
                    else:
                        events.append('DIAGNOSTIC "'+severity.decode()+'" '+byte_sequence(message)+' '+line.decode())
                checks=['U = $pcsource(0, '+checked['fixture']+')',
                        'S_initial = $php_run('+checked['fixture']+', 0, '+json.dumps(base64.b64encode(str(source_path).encode()).decode())+')',
                        'S_initial.COMPLETION = BUDGET','S = S_initial[.COMPLETION = NORMAL]',
                        'S.SOURCES = [U]','S_out = $drive(S, 10000)',
                        '$outputs(S_out.EVENTS) = '+byte_sequence(native.stdout),
                        '$messages(S_out.EVENTS) = ['+', '.join(events)+']',
                        'S_out.COMPLETION = NORMAL','S_out.ORIGIN = eps','S_out.HELD = eps',
                        'S_out.POOLS = S.POOLS','S_out.CODE = S.CODE',
                        '$heap_valid($heap_graph(S_out))']
                if name.startswith('loop-') or name.startswith('independent-copy-'):
                    for budget in (1,2,5,9,17,31,63):
                        checks += [f'S_budget{budget} = $drive(S, {budget})',
                                   f'$drive(S_budget{budget}[.COMPLETION = NORMAL], 10000) = S_out',
                                   f'S_budget{budget}.POOLS = S.POOLS',
                                   f'S_budget{budget}.CODE = S.CODE',
                                   f'$heap_valid($heap_graph(S_budget{budget}))']
                assertions.append(checks)
                records.append({'id':name,'source_base64':base64.b64encode(source).decode(),'ast':checked['ast'],
                                'oracle_stdout':base64.b64encode(native.stdout).decode(),
                                'oracle_stderr':base64.b64encode(native.stderr).decode()})
            for index,checks in enumerate(assertions):
                fixture=Path(tmp)/'truth.watsup'
                fixture.write_text(PREFIX+'dec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks))
                run=subprocess.run([str(runner),*map(str,specs),str(fixture)],capture_output=True,text=True,cwd=ROOT,timeout=120)
                if run.returncode or run.stdout.strip()!='true':
                    (ROOT/'.tools/truth-expressions-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((index,run.stdout,run.stderr))
    finally:
        frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'inputs changed during truth gate'
    report={'result':'pass','classification':'checked-source truth operators and ternary; compiled redirects, phase warnings, selected values and budget resumption',
            'source_cases':len(records),'state_cases':len(assertions),'assertions':sum(map(len,assertions)),
            'records':records,'fingerprint':before}
    (ROOT/'coverage/semantics/truth-expressions.json').write_text(json.dumps(report,indent=2)+'\n')
    print({key:report[key] for key in ('result','source_cases','state_cases','assertions')})

if __name__=='__main__':
    main()
