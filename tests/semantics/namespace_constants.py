#!/usr/bin/env python3
"""Source namespace constants and retained compiler lookup/context descriptors."""
import base64, hashlib, json, subprocess, sys, tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'tests/semantics'))
import static_types as types, source_occurrences as occurrences
CASES = {
 'namespace-dynamic-nan-name': b'<?php namespace N;${NAN}=1;echo ${NAN};',
 'namespace-dynamic-nan-name-in-array': b'<?php namespace N;$a=[${NAN}=1];echo $a[0];',
 'namespace-int-fallback': b'<?php namespace N;echo PHP_INT_MAX;',
 'namespace-nan-fallback': b'<?php namespace N;echo NAN;',
 'namespace-inf-fallback': b'<?php namespace N;echo INF;',
 'namespace-special': b'<?php namespace N;echo true;echo false;echo null;echo TrUe;',
 'namespace-special-array': b'<?php namespace N;echo [true] === [true];',
 'namespace-global-qualified': b'<?php namespace N;echo \\PHP_INT_MIN;echo \\NAN;echo \\true;',
 'namespace-qualified-no-fallback': b'<?php namespace N;echo A\\NAN;',
 'namespace-relative-no-fallback': b'<?php namespace N;echo namespace\\NAN;',
 'namespace-relative-special': b'<?php namespace N;echo namespace\\true;',
 'namespace-fq-special-namespaced': b'<?php namespace N;echo \\N\\true;',
 'namespace-undefined': b'<?php namespace N;echo Missing;',
 'namespace-wrong-case-builtin': b'<?php namespace N;echo Nan;',
 'namespace-const-alias': b'<?php namespace N;use const PHP_INT_MAX as Max;echo Max;',
 'namespace-const-alias-case': b'<?php namespace N;use const PHP_INT_MAX as Max;echo max;',
 'namespace-const-alias-nan-array': b'<?php namespace N;use const NAN as X;$a=[X];echo $a === $a;',
 'namespace-class-alias-constant': b'<?php namespace N;use Vendor\\Package as A;echo A\\Missing;',
 'namespace-class-alias-case': b'<?php namespace N;use Vendor\\Package as Alias;echo aLIAS\\Missing;',
 'namespace-class-alias-plain': b'<?php namespace N;use Vendor\\Package as A;echo A;',
 'namespace-class-alias-unmatched': b'<?php namespace N;use Vendor\\Package as A;echo B\\Missing;',
 'namespace-function-alias-plain': b'<?php namespace N;use function Vendor\\f as NAN;echo NAN;',
 'namespace-function-alias-compound': b'<?php namespace N;use function Vendor\\f as A;echo A\\Missing;',
 'namespace-const-alias-compound': b'<?php namespace N;use const Vendor\\X as A;echo A\\Missing;',
 'namespace-three-alias-tables': b'<?php namespace N;use Vendor\\ClassName as X;use function Vendor\\f as X;use const NAN as X;echo X;',
 'namespace-class-prefix-beats-other-kinds': b'<?php namespace N;use Vendor\\ClassName as X;use function Vendor\\f as X;use const NAN as X;echo x\\Missing;',
 'namespace-partial-array-fold': b'<?php namespace N;$u=7;$a=[$u,NAN,"abc"["1x"]];echo $a[2];',
 'namespace-nan-array-not-constant': b'<?php namespace N;$a=[NAN];$b=[NAN];echo $a === $a;echo $a === $b;',
 'namespace-empty-array': b'<?php namespace N;$a=[];echo $a === [];',
 'namespace-const-import-array': b'<?php namespace N;use const PHP_INT_SIZE as X;$a=[X+1];echo $a[0];',
 'namespace-compilation-before-output': b'<?php namespace N;echo "before";$a=[&$u[]];',
 'namespace-alias-output-before-error': b'<?php use Vendor\\Package as A;echo "before";echo A\\Missing;',
 'namespace-alias-array-error': b'<?php use Vendor\\Package as A;$u=1;echo [$u,A\\Missing];',
 'namespace-block-import-reset': b'<?php namespace N {use const PHP_INT_SIZE as X;echo X;} namespace N {echo X;}',
 'namespace-global-block-reset': b'<?php namespace N {echo PHP_INT_SIZE;} namespace {echo PHP_INT_SIZE;}',
 'namespace-name-byte-alias': b'<?php namespace N;use Vendor\\Package as X\xff;echo X\xff\\Missing;',
 'namespace-name-byte-namespace': b'<?php namespace N\xff;echo Missing;',
 'namespace-name-unicode-separator': b'<?php namespace N;use Vendor\\Package as X\xc2\x85\xe2\x80\xa8;echo X\xc2\x85\xe2\x80\xa8\\Missing;',
 'namespace-multiline-lookup-line': b'<?php namespace N;\necho\n Missing\n;',
 'namespace-multiline-array-lookup-line': b'<?php namespace N;\n$u=7;\necho [\n $u,\n Missing\n];',
}

PREFIX="""
dec $pntest_name((pcpath, pnreference)*, pcpath) : pnreference?
def $pntest_name(eps, pcpath) = eps
def $pntest_name((pcpath, pnreference) :: (pcpath_tail, pnreference_tail)*, pcpath) = (pnreference)
def $pntest_name((pcpath_other, pnreference) :: (pcpath_tail, pnreference_tail)*, pcpath) = $pntest_name((pcpath_tail, pnreference_tail)*, pcpath)
  -- if pcpath_other =/= pcpath
"""
NAMES={
 'namespace-int-fallback':(b'N\\PHP_INT_MAX',b'PHP_INT_MAX'),
 'namespace-nan-fallback':(b'N\\NAN',b'NAN'),
 'namespace-relative-no-fallback':(b'N\\NAN',None),
 'namespace-const-alias-case':(b'N\\max',b'max'),
 'namespace-class-alias-case':(b'Vendor\\Package\\Missing',None),
}

def selected(ast,kind):
    return [(path,node) for i,statement in enumerate(ast['program']) for path,node in occurrences.expected(statement,[('INDEX',i)]) if node['node']==kind]

def fixture_checks(checked):
    checks=[]
    for key,(resolved,fallback) in NAMES.items():
        ast=checked[key];path,node=selected(ast['ast'],'Expr_ConstFetch')[0];term=occurrences.path_term(path)
        fallback_term='eps' if fallback is None else '('+types.byte_expr(fallback.decode())+')'
        checks.append([f'P = $ppstart(71, {ast["fixture"]}, ([120]))','P.COMPLETION = PPCNORMAL',f'$pntest_name(P.NAMES, {term}) = (pnreference)',f'pnreference.RESOLVED = {types.byte_expr(resolved.decode())}',f'pnreference.FALLBACK = {fallback_term}',f'$pffact(P.FOLD.FACTS, {term}) = eps'])
    for key,folded in [('namespace-nan-array-not-constant',False),('namespace-const-alias-nan-array',True),('namespace-special-array',True),('namespace-empty-array',True)]:
        ast=checked[key];path,node=selected(ast['ast'],'Expr_Array')[0];term=occurrences.path_term(path)
        checks.append([f'P = $ppstart(71, {ast["fixture"]}, ([120]))','P.COMPLETION = PPCNORMAL',f'$pffact(P.FOLD.FACTS, {term}) = '+('(PARRAY n)' if folded else 'eps')])
    ast=checked['namespace-nan-array-not-constant'];path,node=selected(ast['ast'],'Expr_Array')[0];term=occurrences.path_term(path);expression=occurrences.node_term(node)
    for initial,changed in [('$plempty(false)','$plempty(false)[.NAMESPACE = [78]]'),('$plempty(false)[.NAMESPACE = [78]]','$plempty(false)'),('$plempty(false)','$plempty(false)[.CONSTANTS = [([78,65,78],[73,78,70])]]')]:
        checks.append([f'F = $pfprepare($pfbegin(71, {ast["fixture"]}), {term}, {expression}, {initial}, 1)','F.MEMORY.COMPLETION = NORMAL',f'$pfprepare(F, {term}, {expression}, {initial}, 99) = F',f'$pfprepare(F, {term}, {expression}, {changed}, 99).MEMORY.COMPLETION = UNSUPPORTED "constant occurrence lexical context changed"'])
    checks.extend([
        ['$constant_fetch(([80,72,80,95,86,69,82,83,73,79,78]), ([78,65,78]), 9) = ABRUPT (UNSUPPORTED "initial constant")'],
        ['$constant_fetch(([77,105,115,115,105,110,103]), ([78,65,78]), 9) = VALUE (PFLOAT 9221120237041090560)'],
        ['$constant_fetch(([78,97,78]), eps, 9) = ABRUPT (PHPERROR ([78,97,78]) 9)'],
    ])
    return checks

def main():
    subprocess.run([str(ROOT/'scripts/opam-exec.sh'),'dune','build','--root',str(ROOT/'tests/semantics'),'numeric_runner.exe'],cwd=ROOT,check=True,timeout=120)
    runner=ROOT/'tests/semantics/_build/default/numeric_runner.exe'
    specs=[ROOT/p for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    before=types.syntax_validation.implementation_fingerprint()
    frontend=types.Worker([str(types.PHP),'-n','-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    adapter=types.Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    checked={};records=[]
    identity_command=[str(types.PHP),'-n',*types.FLAGS,'-r','echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);']
    identity=json.loads(subprocess.run(identity_command,capture_output=True,env=types.ENV,cwd=ROOT,check=True,timeout=10).stdout)
    assert identity[:4]==['8.5.10','cli',8,False] and all(identity[4][key]==value for key,value in types.PROFILE.items())
    try:
        with tempfile.TemporaryDirectory(dir=ROOT/'.tools') as tmp:
            file=Path(tmp)/'input.php'
            for name,source in CASES.items():
                parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()});assert parsed['accepted'],(name,parsed)
                checked[name]=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked[name]['ok'],checked[name]
                file.write_bytes(source)
                native_command=[str(types.PHP),'-n',*types.FLAGS,str(file)]
                semantic_command=[str(ROOT/'bin/php-semantics'),str(file)]
                native=subprocess.run(native_command,capture_output=True,env=types.ENV,cwd=ROOT,timeout=10)
                semantic=subprocess.run(semantic_command,capture_output=True,env=types.ENV,cwd=ROOT,timeout=35)
                actual=json.loads(semantic.stdout)
                expected={'stdout':base64.b64encode(native.stdout).decode(),'stderr':base64.b64encode(native.stderr).decode(),'exit_status':native.returncode}
                assert semantic.returncode==0 and actual['status'] in ('normal','php_error','static_rejection'),(name,actual)
                assert all(actual[key]==value for key,value in expected.items()),(name,actual,expected)
                def observation(command,run):
                    return {'command':command,'status':run.returncode,'stdout_base64':base64.b64encode(run.stdout).decode(),'stderr_base64':base64.b64encode(run.stderr).decode()}
                records.append({'id':name,'source_base64':base64.b64encode(source).decode(),'ast_sha256':hashlib.sha256(json.dumps(checked[name]['ast'],sort_keys=True).encode()).hexdigest(),'cwd':str(ROOT),'oracle':observation(native_command,native),'semantic':observation(semantic_command,semantic),'comparison':'pass'})
            checks=fixture_checks(checked)
            file=Path(tmp)/'checks.watsup'
            file.write_text(PREFIX+'\n'.join(f'dec $case{i}() : bool\ndef $case{i}() = true\n'+''.join('  -- if '+condition+'\n' for condition in conditions) for i,conditions in enumerate(checks))+'\ndec $main() : bool\ndef $main() = true\n'+''.join(f'  -- if $case{i}()\n' for i in range(len(checks))))
            run=subprocess.run([str(runner),*map(str,specs),str(file)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                (ROOT/'.tools/namespace-constant-failure.watsup').write_text(file.read_text());raise AssertionError((run.returncode,run.stdout,run.stderr))
    finally:frontend.close();adapter.close()
    assert before==types.syntax_validation.implementation_fingerprint(),'watched inputs changed'
    report={'scope':'source constant resolution, compile substitution, late fallback and lexical cache binding','profile':types.PROFILE,'oracle_identity':identity,'fingerprint':before,'source_cases':len(CASES),'descriptor_cases':len(checks),'cases':records}
    (ROOT/'coverage/semantics/namespace-constants.json').write_text(json.dumps(report,indent=2)+'\n')
    print(len(CASES),'original-source comparisons;',len(checks),'lookup/fold/cache descriptor cases passed')

if __name__=='__main__':main()
