#!/usr/bin/env python3
"""Checked declaration signatures against pinned compilation; no call/activation claims."""
import base64
import copy
import hashlib
import json
from pathlib import Path
import re
import signal
import subprocess
import tempfile

import static_types as types
ROOT, HERE, PHP = types.ROOT, types.HERE, types.PHP
SPECS = types.SPECS + [ROOT / 'spec/semantics/17-signatures.watsup']


def main():
    def expired(signum, frame):
        raise TimeoutError('signature worker exceeded 30 seconds')
    signal.signal(signal.SIGALRM, expired)
    subprocess.run([str(ROOT / 'scripts/opam-exec.sh'), 'dune', 'build', '--root', str(HERE), 'numeric_runner.exe'], cwd=ROOT, check=True, timeout=120)
    runner = HERE / '_build/default/numeric_runner.exe'
    watched = SPECS + [Path(__file__), PHP, runner, HERE/'numeric_runner.ml', HERE/'dune', HERE/'profile.json', HERE/'static_types.py']
    def fingerprint():
        return {'closure':types.syntax_validation.implementation_fingerprint(),
                'direct':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in watched},
                'sources':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['vendor/php-src/Zend/zend_compile.c','vendor/php-src/Zend/zend_API.c','vendor/php-src/Zend/zend_ast.c','vendor/php-src/Zend/zend_operators.c','vendor/php-src/main/php_variables.c']}}
    before = fingerprint()
    probe = subprocess.run([str(PHP), '-n', *types.FLAGS, '-r', 'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false),get_loaded_extensions()]);'], capture_output=True, text=True, timeout=10, env=types.ENV, check=True)
    identity = json.loads(probe.stdout)
    assert identity[:4] == ['8.5.10','cli',8,False]
    assert all(identity[4][k] == v for k,v in types.PROFILE.items())
    assert 'session' not in identity[5], 'the parameter autoglobal profile excludes the session extension'
    frontend = types.Worker([str(PHP), '-n', *types.FLAGS, '-d', 'extension='+str(ROOT/'.tools/php-file.so'), str(ROOT/'frontend/worker.php')])
    adapter = types.Worker([str(ROOT/'_build/default/adapter/main.exe'), str(ROOT)])
    declarations = []
    records = []
    types_list = ['', 'int ', 'float ', 'string ', 'bool ', 'true ', 'false ', 'null ', 'mixed ', 'array ', 'iterable ', 'A ', '?A ', 'A&B ', '(A&B)|null ', 'int|float ', 'never ']
    params = [f'{t}$x{d}' for t in types_list for d in ['', '=null', '=true', '=false', '=1', '=1.5', '=-1', '=+1', '=-1.5', '=-9223372036854775808', '=-(-9223372036854775808)', '="s"', '=[]', '=UNKNOWN']]
    params += ['$x,$x', '$X,$x', '...$x,$y', '...$x,$x', '$x,...$y', '$x=1,...$y', 'int $x=null,$y', '?int $x=null,$y', '$x=null,$y', 'int $x=1,$y', 'A&B $x=null,$y', '$a=1,$b=2,$c', '$a=1,$b=2,$c,$d=3', 'integer $x=null,$y', 'bool $x=true,$y', '$GLOBALS', '$_GET', '$_POST', '$_SESSION', '$_SERVER', '$_ENV', '$_COOKIE', '$_FILES', '$_REQUEST', '$this', '$x=1,$_GET', '$x=1,$x', '...$x,$_GET', '$x=1,int $y="s"', '...$x,$this', 'float $x=1,$y', 'int|float $x=1', '&$x', 'int &$x', '&...$x','$x=UNKNOWN,$y']
    params += [t+'$x='+d for t in ['', 'int ', 'float '] for d in ['-(-1)', '+(-1)', '-(+1)', '-(-(-1))', '9223372036854775807', '9223372036854775808', '-(-(-9223372036854775808))', '-(0x8000000000000000)', '1e1000', '-0.0']]
    params += [t+'$x='+d for t in ['object ', 'int ', 'bool '] for d in [r'namespace\null',r'namespace\NULL',r'namespace\true',r'namespace\TRUE',r'namespace\false',r'namespace\FALSE',r'\null',r'\TRUE',r'\false']]
    cases = [(p,'','',False) for p in params]
    cases += [(p,r,'',byref) for p,r,byref in [('$x=1,$y','void',True),('integer $x=null,$y','void',True),('int $x="s"','int|INT',False),('$x,$x','?mixed',False),('$x,$x','void',True)]]
    cases += [('int $x=null,$y','','C',False),('float $x=1','','C',False),('self $x=null','','C',False),('','void','C',True)]
    cases += [('','int','',True),('','int','',False)]
    namespaced = {'namespace-'+d: '<?php namespace Ns; function f(object $x=namespace\\'+d+') {}' for d in ['null','NULL','true','TRUE','false','FALSE']}
    multiline = {
        'multiline-nullable': ('<?php\nfunction f(\n int $x=null,\n $y\n):\n void\n{}', 2),
        'multiline-default': ('<?php\nfunction f(\n int $x =\n 1.5\n) {}', 2),
        'multiline-variadic': ('<?php\nfunction f(\n ...$x,\n $y\n) {}', 2),
        'multiline-constant': ('<?php\nfunction f(\n int $x=\n UNKNOWN,\n $y) {}', 2),
        'multiline-constant-type': ('<?php\nfunction f(\n integer $x=\n UNKNOWN,\n $y) {}', 2),
        'multiline-constant-null': ('<?php\nfunction f(\n int $x=\n namespace\\null,\n $y) {}', 2),
        'multiline-literal-null': ('<?php\nfunction f(\n int $x=\n null,\n $y) {}', 2),
        'multiline-ordered': ('<?php\nfunction &f(\n integer $x=null,\n $y\n): void {}', 2),
    }
    cases += [(name,'','',False) for name in multiline]
    cases += [(name,'','',False) for name in namespaced]
    cases += [('magic-tostring','','C',False)]
    pending = {'$x=1+2':'nonliteral parameter default requires constant-expression compilation', '$x=[1]':'nonliteral parameter default requires constant-expression compilation', '$x=new A':'nonliteral parameter default requires constant-expression compilation', '$x=-true':'nonnumeric unary parameter default requires constant-expression compilation', '#[A] $x':'parameter attributes, promotion or hooks', 'public $x':'parameter attributes, promotion or hooks'}
    restrictions = {'void $x':'void cannot be used as a parameter type', '...$x=1':'Variadic parameter cannot have a default value'}
    cases += [(p,'','',False) for p in [*pending,*restrictions]]
    descriptors = {
        'float $x=1': [('x','float',False,False,False,'float')],
        'int|float $x=1': [('x','int|float',False,False,False,'int')],
        'int $x=null,$y': [('x','?int',False,False,True,'none'),('y','',False,False,True,'none')],
        '$x=1,...$y': [('x','',False,False,False,'int'),('y','',False,True,False,'none')],
        'int &$x': [('x','int',True,False,True,'none')],
        '&...$x': [('x','',True,True,False,'none')],
        'A&B $x=null,$y': [('x','(A&B)|null',False,False,True,'none'),('y','',False,False,True,'none')],
        'null $x=null': [('x','null',False,False,False,'null')],
        'mixed $x=null': [('x','mixed',False,False,False,'null')],
        'float $x=UNKNOWN': [('x','float',False,False,False,'deferred')],
        '$x=UNKNOWN,$y': [('x','',False,False,True,'none'),('y','',False,False,True,'none')],
        'self $x=null': [('x','?C',False,False,False,'null')],
        'magic-tostring': [],
        '$x=-(-1)': [('x','',False,False,False,'int')],
        '$x=-9223372036854775808': [('x','',False,False,False,'float')],
        'float $x=-(-1)': [('x','float',False,False,False,'float')],
    }
    descriptors[r'object $x=namespace\null'] = [('x','?object',False,False,False,'null')]
    descriptors[r'bool $x=namespace\true'] = [('x','bool',False,False,False,'true')]
    descriptors[r'bool $x=namespace\false'] = [('x','bool',False,False,False,'false')]
    descriptors.update({name:[('x','object',False,False,False,'deferred')] for name in namespaced})
    descriptor_checks = return_reference_checks = 0
    prefix = '''
 dec $psfixture(program, ptcontext) : psresult
 def $psfixture(PROGRAM ([(NStmtFunction phpType14 (BOOLEAN bool) phpType11 phpType16 phpType18 phpType23 metadata)]), ptcontext) = $pscompile(phpType16, phpType18, bool, ptcontext)
 def $psfixture(PROGRAM ([(NStmtNamespace phpType44 (SEQUENCE statement*) metadata)]), ptcontext) = $psfixture(PROGRAM statement*,ptcontext)
 def $psfixture(PROGRAM ([(NStmtClass phpType14 phpType24 phpType3 phpType44 phpType42 (SEQUENCE statement*) metadata)]), ptcontext) = $psmethodfixture(statement*,ptcontext)
 dec $psmethodfixture(statement*,ptcontext) : psresult
 def $psmethodfixture([(NStmtClassMethod phpType14 phpType24 (BOOLEAN bool) phpType11 phpType16 phpType18 phpType47 metadata)],ptcontext) = $pscompile(phpType16,phpType18,bool,ptcontext)
 dec $pstest_params(psresult) : (ptbytes,ptbytes,bool,bool,bool,text)*
 def $pstest_params(PSOK pssignature psdiagnostic*) = ($pstest_param(psparam))*
   -- if psparam* = pssignature.PARAMETERS
 dec $pstest_param(psparam) : (ptbytes,ptbytes,bool,bool,bool,text)
 def $pstest_param(psparam) = (psparam.NAME,$pttypename(psparam.TYPE),psparam.BYREF,psparam.VARIADIC,psparam.REQUIRED,$pstest_defaultkind(psparam.DEFAULT))
 dec $pstest_defaultkind(psdefault) : text
 def $pstest_defaultkind(PSNONE) = "none"
 def $pstest_defaultkind(PSDEFAULT phpType5 text) = text
 dec $pstest_defaults(program) : phpType5*
 def $pstest_defaults(PROGRAM ([(NStmtFunction phpType14 (BOOLEAN bool) phpType11 (SEQUENCE phpType17*) phpType18 phpType23 metadata)])) = ($pstest_defaultast(phpType17))*
 dec $pstest_defaultast(phpType17) : phpType5
 def $pstest_defaultast(NParam phpType14 phpType24 phpType18 phpType4 phpType4_var phpType10 phpType5 phpType37 metadata) = phpType5
 dec $pstest_keptdefaults(psresult) : phpType5*
 def $pstest_keptdefaults(PSOK pssignature psdiagnostic*) = ($pstest_keptdefault(psparam.DEFAULT))*
   -- if psparam* = pssignature.PARAMETERS
 dec $pstest_keptdefault(psdefault) : phpType5
 def $pstest_keptdefault(PSNONE) = ABSENT
 def $pstest_keptdefault(PSDEFAULT phpType5 text) = phpType5
 dec $pstest_byref(psresult) : bool
 def $pstest_byref(PSOK pssignature psdiagnostic*) = pssignature.BYREF
 dec $pstest_return(psresult) : ptbytes
 def $pstest_return(PSOK pssignature psdiagnostic*) = $pttypename(pssignature.RETURNS)
 dec $pstest_ok(psresult) : bool
 def $pstest_ok(PSOK pssignature psdiagnostic*) = true
 def $pstest_ok(PSERROR psdiagnostic*) = false
 dec $pstest_events(psresult) : (text, ptbytes, ptbytes, nat)*
 def $pstest_events(PSOK pssignature psdiagnostic*) = ($pstest_event(psdiagnostic))*
 def $pstest_events(PSERROR psdiagnostic*) = ($pstest_event(psdiagnostic))*
 dec $pstest_event(psdiagnostic) : (text, ptbytes, ptbytes, nat)
 def $pstest_event(PSTYPEDIAGNOSTIC (PTDIAGNOSTIC text_level text_code ptbranch* ptcontext)) = (text_level,$ptmessage(PTDIAGNOSTIC text_level text_code ptbranch* ptcontext),ptcontext.FILE,ptcontext.LINE)
 def $pstest_event(PSDIAGNOSTIC text_level text_code ptbytes* ptcontext) = (text_level,$psmessage(PSDIAGNOSTIC text_level text_code ptbytes* ptcontext),ptcontext.FILE,ptcontext.LINE)
'''
    # Fixture signatures are declared before mutually dependent fixture clauses.
    lines=prefix.splitlines(); prefix='\n'.join([x for x in lines if x.strip().startswith('dec ')] + [x for x in lines if not x.strip().startswith('dec ')])+'\n'
    try:
        with tempfile.TemporaryDirectory(prefix='signatures-',dir=ROOT/'.tools') as tmp:
            file = Path(tmp)/'input.php'
            for i,(params,returns,owner,byref) in enumerate(cases):
                member = '__toString' if params == 'magic-tostring' else 'f'
                emitted_params = '' if params == 'magic-tostring' else params
                compiler_line = 1
                source = '<?php '+('class C { ' if owner else '')+'function '+('&' if byref else '')+member+'('+emitted_params+')'+(': '+returns if returns else '')+' {}'+(' }' if owner else '')
                if params in namespaced:
                    source = namespaced[params]
                if params in multiline:
                    source,compiler_line = multiline[params]
                encoded=base64.b64encode(source.encode()).decode()
                parsed=frontend.request({'op':'parse','source':encoded})
                native=frontend.request({'op':'oracle','source':encoded})
                assert native['accepted'], (source,native)
                file.write_text(source)
                oracle=subprocess.run([str(PHP),'-n',*types.FLAGS,'-l',str(file)],capture_output=True,text=True,timeout=10,env=types.ENV)
                assert oracle.returncode in (0,255), (source,oracle.returncode,oracle.stderr)
                assert parsed['accepted'], (source,parsed)
                checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
                events=[]
                for line in oracle.stderr.splitlines():
                    if not line or line=='Stack trace:' or re.match(r'#\d+ ',line): continue
                    match=re.fullmatch(r'(?:PHP )?(Warning|Deprecated|Fatal error): (.*) in (.*) on line (\d+)',line)
                    assert match, (source,line)
                    level,message,path,lineno=match.groups()
                    events.append(({'Warning':'warning','Deprecated':'deprecated','Fatal error':'fatal'}[level],message,path,int(lineno)))
                context='{NAMESPACE ('+types.byte_expr('Ns' if params in namespaced else '')+'),IMPORTS eps,SCOPE '+('(PTKNOWN ([67]) eps)' if owner else 'PTGLOBAL')+',POSITION PTRETURN,OWNER ('+types.byte_expr(owner)+'),MEMBER ('+types.byte_expr(member)+'),FILE ('+types.byte_expr(str(file))+'),LINE '+str(compiler_line)+'}'
                expected='['+','.join('('+json.dumps(level)+','+types.byte_expr(message)+','+types.byte_expr(path)+','+str(line)+')' for level,message,path,line in events)+']'
                if params in pending:
                    declarations.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if $psfixture({checked["fixture"]},{context}) = PSUNSUPPORTED {json.dumps(pending[params])}\n')
                    records.append({'source':source,'classification':'unsupported','reason':pending[params],'exit':oracle.returncode,'stdout':oracle.stdout,'stderr':oracle.stderr})
                    continue
                declarations.append(f'dec $case{i}() : bool\ndef $case{i}() = true\n  -- if psresult = $psfixture({checked["fixture"]},{context})\n  -- if $pstest_ok(psresult) = {str(oracle.returncode == 0).lower()}\n  -- if $pstest_events(psresult) = {expected}\n')
                if oracle.returncode == 0:
                    expected_ref = byref or params == 'multiline-ordered'
                    declarations[-1] += f'  -- if $pstest_byref(psresult) = {str(expected_ref).lower()}\n'
                    return_reference_checks += 1
                if params in ['float $x=1','float $x=UNKNOWN','int|float $x=1','$x=-(-1)','$x=-9223372036854775808'] and not owner:
                    declarations[-1] += f'  -- if $pstest_keptdefaults(psresult) = $pstest_defaults({checked["fixture"]})\n'
                if params in descriptors and not returns:
                    expected_params = '['+','.join('('+types.byte_expr(name)+','+types.byte_expr(t)+','+str(ref).lower()+','+str(var).lower()+','+str(required).lower()+','+json.dumps(kind)+')' for name,t,ref,var,required,kind in descriptors[params])+']'
                    declarations[-1] += f'  -- if $pstest_params(psresult) = {expected_params}\n'
                    if params == 'magic-tostring':
                        declarations[-1] += f'  -- if $pstest_return(psresult) = {types.byte_expr("string")}\n'
                    descriptor_checks += 1
                records.append({'source':source,'classification':'compared','exit':oracle.returncode,'stdout':oracle.stdout,'stderr':oracle.stderr,'sha256':hashlib.sha256(source.encode()).hexdigest(),'context':{'file':str(file),'compiler_line':compiler_line}})
            seed = frontend.request({'op':'parse','source':base64.b64encode(b'<?php function f($x) {}').decode()})['ast']
            negative_context = '{NAMESPACE eps,IMPORTS eps,SCOPE PTGLOBAL,POSITION PTRETURN,OWNER eps,MEMBER ([102]),FILE ([102]),LINE 1}'
            negatives = [
                ('missing-parameter-line','missing parameter compiler line'),
                ('missing-default-line','missing deferred default compiler line'),
                ('negative-parameter-line','missing parameter compiler line'),
                ('invalid-parameter-name','edited invalid parameter name'),
                ('dynamic-parameter-name','edited dynamic parameter name'),
                ('missing-member','missing declaration display name'),
                ('missing-file','missing source file or compiler line'),
                ('missing-line','missing source file or compiler line'),
            ]
            for name,reason in negatives:
                ast,context = copy.deepcopy(seed),negative_context
                param = ast['program'][0]['fields'][3][0]
                if name == 'missing-default-line': param['fields'][6]={'node':'Expr_ConstFetch','fields':[{'node':'Name','fields':[{'bytes':'VU5LTk9XTg=='}],'meta':{}}],'meta':{}}
                if name == 'missing-parameter-line': del param['meta']['startLine']
                if name == 'negative-parameter-line': param['meta']['startLine']={'int':'-1'}
                if name == 'invalid-parameter-name': param['fields'][5]['fields'][0]={'bytes':base64.b64encode(b'bad\\name').decode()}
                if name == 'dynamic-parameter-name': param['fields'][5]['fields'][0]={'node':'Scalar_String','fields':[{'bytes':'eA=='}],'meta':{}}
                if name == 'missing-member': context=context.replace('MEMBER ([102])','MEMBER eps')
                if name == 'missing-file': context=context.replace('FILE ([102])','FILE eps')
                if name == 'missing-line': context=context.replace('LINE 1','LINE 0')
                checked = adapter.request({'op':'check','ast':ast,'fixture':True})
                declarations.append(f'dec $case{len(cases)+len(records)}() : bool\ndef $case{len(cases)+len(records)}() = true\n  -- if $psfixture({checked["fixture"]},{context}) = PSUNSUPPORTED {json.dumps(reason)}\n')
                records.append({'classification':'edited-unsupported','name':name,'reason':reason,'ast':ast,'context':context})
            for operators,kind in [([], 'int'),(['Expr_UnaryPlus'],'int'),(['Expr_UnaryMinus'],'float'),(['Expr_UnaryMinus','Expr_UnaryMinus'],'float')]:
                ast = copy.deepcopy(seed)
                expr = {'node':'Scalar_Int','fields':[{'int':'-9223372036854775808'}],'meta':{}}
                for operator in operators: expr={'node':operator,'fields':[expr],'meta':{}}
                ast['program'][0]['fields'][3][0]['fields'][6] = expr
                checked = adapter.request({'op':'check','ast':ast,'fixture':True})
                declarations.append(f'dec $case{len(cases)+len(records)}() : bool\ndef $case{len(cases)+len(records)}() = true\n  -- if psresult = $psfixture({checked["fixture"]},{negative_context})\n  -- if $pstest_params(psresult) = [([120],eps,false,false,false,"{kind}")]\n  -- if $pstest_keptdefaults(psresult) = $pstest_defaults({checked["fixture"]})\n')
                records.append({'classification':'edited-numeric-descriptor','operators':operators,'expected_kind':kind,'ast':ast,'context':negative_context})
            for params,message in restrictions.items():
                ast = copy.deepcopy(seed)
                param = ast['program'][0]['fields'][3][0]
                if params.startswith('void'):
                    param['fields'][2] = {'node':'Identifier','fields':[{'bytes':'dm9pZA=='}],'meta':{}}
                else:
                    param['fields'][4] = True
                    param['fields'][6] = {'node':'Scalar_Int','fields':[{'int':'1'}],'meta':{}}
                checked = adapter.request({'op':'check','ast':ast,'fixture':True})
                declarations.append(f'dec $case{len(cases)+len(records)}() : bool\ndef $case{len(cases)+len(records)}() = true\n  -- if psresult = $psfixture({checked["fixture"]},{negative_context})\n  -- if $pstest_ok(psresult) = false\n  -- if $pstest_events(psresult) = [("fatal",{types.byte_expr(message)},[102],1)]\n')
                records.append({'classification':'edited-compiler-restriction','source':'<?php function f('+params+') {}','ast':ast,'context':negative_context})
            for start in range(0,len(declarations),40):
                batch=declarations[start:start+40]
                fixture=Path(tmp)/'cases.watsup'
                fixture.write_text(prefix+'\n'.join(batch)+'\ndec $main() : bool\ndef $main() = true\n'+'\n'.join('  -- if '+re.search(r'\$case\d+',x).group()+'()' for x in batch)+'\n')
                r=subprocess.run([str(runner),*map(str,SPECS),str(fixture)],capture_output=True,text=True,timeout=120)
                if r.returncode or r.stdout.strip()!='true':
                    (ROOT/'.tools/signatures-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((start,r.stdout,r.stderr))
    finally:
        frontend.close(); adapter.close()
    assert before==fingerprint(),'inputs changed during validation'
    report={'target':'PHP 8.5.10 CLI NTS signed64','result':'pass','comparisons':sum(r['classification']=='compared' for r in records),'descriptor_checks':descriptor_checks,'return_reference_checks':return_reference_checks,'edited_numeric_descriptors':4,'explicit_unsupported':len(pending)+len(negatives),'edited_compiler_restrictions':len(restrictions),'frontend_compile_restrictions':0,'parser_rejected':0,'environment':{'LC_ALL':'C','TZ':'UTC'},'budgets':{'request_seconds':30,'shutdown_seconds':5,'lint_seconds':10,'batch_seconds':120},'comparison':'ordered severity, exact message bytes, original file and compiler line; descriptor fields and retained checked default AST; pending outcomes separate','identity':identity,'profile':types.PROFILE,'fingerprints':before,'cases':records}
    (ROOT/'coverage/semantics/signatures.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['cases','identity','fingerprints','profile']}))

if __name__=='__main__': main()
