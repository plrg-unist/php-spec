"""Pinned source and reached-state checks for untyped backed reference Get."""
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace

import backed_get_hook_protocol as hook
import error_handler_run as recorder
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PREFIX = hook.PREFIX + r'''
def $bh_stage(S,10) = ($property_hook_ref_plan(S) =/= eps)
def $bh_stage(S,11) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,12) = true
  -- if $bh_output(S.EVENTS) = $ptascii("A:G|alias7|untyped8|")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,13) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("object")
  -- if $bh_output(S.EVENTS) = $ptascii("A:G|alias7|untyped8|G|copy8|alias9|")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,14) = true
  -- if S.TODO = (STMT (NStmtExpression (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NScalarString (BYTES text_value) metadata_value) metadata_assign) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias") /\ $base64(text_value) = $ptascii("free")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,20) = true
  -- if S.TODO = (PROPERTY_PREP phpType20 12) :: (ORIGIN_RETURN porigin?) :: (PROPERTY_REF_PREP expression 12) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,21) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "bind") :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,22) = true
  -- if $bh_output(S.EVENTS) = $ptascii("R:G|blocked|line|file|")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,30) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("object")
  -- if $bh_output(S.EVENTS) = $ptascii("N:G|null|G|copy|alias|")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,31) = true
  -- if S.TODO = (STMT (NStmtExpression (NExprAssign (NExprVariable (BYTES text_name) metadata_name) (NScalarString (BYTES text_value) metadata_value) metadata_assign) metadata)) :: ptask*
  -- if $base64(text_name) = $ptascii("alias") /\ $base64(text_value) = $ptascii("after")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
'''


def lines(source):
    return [line.strip() for line in source.strip().splitlines() if line.strip()]


def seek(start, stage, finish):
    return [
        f'{finish}_found = $bh_seek({start},{stage},3000)',
        rf'{finish}_found.COMPLETION = NORMAL \/ {finish}_found.COMPLETION = BUDGET',
        f'{finish} = {finish}_found[.COMPLETION = NORMAL]',
        f'$bh_stage({finish},{stage})',
    ]


def budget(start, label):
    return [
        f'{label}_zero = $drive_steps({start},0)',
        f'{label}_zero = {start}[.COMPLETION = BUDGET]',
        f'{label}_one = $drive_steps({start},1)',
        f'{label}_one.COMPLETION = BUDGET',
        f'{label}_two = $drive_steps({start},2)',
        f'{label}_split = $drive_steps({label}_one[.COMPLETION = NORMAL],1)',
        f'{label}_split = {label}_two',
    ]


def conditions(group, program, path):
    checks = [
        f'S_initial = $php_run({program},0,{json.dumps(base64.b64encode(str(path).encode()).decode())})',
        'S_initial.COMPLETION = BUDGET',
    ]
    if group == 'forbidden-rebind':
        checks += seek('S_initial', 20, 'S_front') + lines(r'''
        $property_hook_ref_plan(S_front) = ((ppropertyhook,"bind"))
        ppropertyhook.LINE = 12
        S_front.TODO = (PROPERTY_PREP phpType20 12) :: ptask_tail*
        $property_hook_ref_tail(S_front,ppropertyhook,"bind",ptask_tail*)
        $lookup(S_front.ENV,$ptascii("object")) = (n_object_cell)
        S_front.STORE[n_object_cell] = DEFINED (POBJECT n_object)
        $lookup(S_front.ENV,$ptascii("replacement")) = (n_rhs)
        S_front.STORE[n_rhs] = DEFINED (PINT 11)
        $property_effective_desc(S_front,n_object,$ptascii("value")) = (ppropertydesc)
        ppropertydesc.TYPE = eps
        $property_hook_reference_decl(S_front,ppropertydesc)
        $bh_slot(S_front,n_object,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 7)))
        $bh_guard(S_front)
        ''')
        checks += seek('S_front', 21, 'S_result') + lines(r'''
        S_result.RESULT = REFERENCE n_value
        S_result.STORE[n_value] = DEFINED (PINT 7)
        $bh_slot(S_result,n_object,$ptascii("value")) = (PROP_VALUE (ALIAS n_value))
        $propref_at(S_result.PROPREFS,n_value) = eps
        $heap_owners($heap_graph(S_result),HCELL n_value) = 2
        $property_hook_result_tail(S_result,ppropertyhook,S_result.TODO)
        $bh_output(S_result.EVENTS) = $ptascii("R:G|")
        $bh_guard(S_result)
        PhpStep: S_result ~> S_error_raw
        S_error_raw = S_result[.COMPLETION = THROWN "Error" ($ptascii("Cannot assign by reference to overloaded object")) 12]
        S_error = $bh_after(S_result,S_error_raw)
        ''')
        checks += budget('S_result', 'S_error_budget')
        checks += seek('S_error', 22, 'S_caught') + lines(r'''
        $lookup(S_caught.ENV,$ptascii("error")) = (n_error_cv)
        S_caught.STORE[n_error_cv] = DEFINED (POBJECT n_error)
        S_caught.OBJECTS[n_error] = THROWABLE pthrowable
        pthrowable.KIND = "Error"
        $string_bytes($throwable_field(S_caught,n_error,"message")) = ($ptascii("Cannot assign by reference to overloaded object"))
        $throwable_field(S_caught,n_error,"line") = PINT 12
        $string_bytes($throwable_field(S_caught,n_error,"file")) = ($call_sourcefile(S_caught.FILES,ppropertyhook.SITE))
        S_caught.STORE[n_rhs] = DEFINED (PINT 11)
        S_caught.STORE[n_value] = DEFINED (PINT 7)
        $propref_at(S_caught.PROPREFS,n_value) = eps
        $bh_guard(S_caught)
        S_done = $drive(S_caught,4000)
        S_done.COMPLETION = NORMAL
        S_done.EXITSTATUS = 0
        S_done.TODO = eps
        $bh_output(S_done.EVENTS) = $ptascii("R:G|blocked|line|file|G|kept7|G|separate7|rhs13|D|Z|")
        $bh_guard(S_done)
        ''')
        return checks

    checks += seek('S_initial', 10, 'S_front') + lines(r'''
    $property_hook_ref_plan(S_front) = ((ppropertyhook,"fetch"))
    $lookup(S_front.ENV,$ptascii("object")) = (n_object_cell)
    S_front.STORE[n_object_cell] = DEFINED (POBJECT n_object)
    $property_effective_desc(S_front,n_object,$ptascii("value")) = (ppropertydesc)
    ppropertydesc.TYPE = eps
    $property_hook_reference_decl(S_front,ppropertydesc)
    $property_hook_function(S_front,ppropertyhook) = (pfunction_hook)
    pfunction_hook.SIGNATURE = {PARAMETERS eps,RETURNS eps,BYREF true}
    $heap_owners($heap_graph(S_front),HOBJECT n_object) = 1
    $bh_guard(S_front)
    ''')
    if group == 'default-null':
        checks += lines(r'''
        ppropertydesc.DEFAULT = PROP_NULL
        $bh_slot(S_front,n_object,$ptascii("value")) = (PROP_VALUE (DIRECT PNULL))
        $bh_output(S_front.EVENTS) = $ptascii("N:")
        ''')
    else:
        checks += lines(r'''
        $bh_slot(S_front,n_object,$ptascii("value")) = (PROP_VALUE (DIRECT (PINT 7)))
        $bh_output(S_front.EVENTS) = $ptascii("A:")
        ''')
    checks += seek('S_front', 11, 'S_result') + lines(r'''
    S_result.RESULT = REFERENCE n_value
    S_result.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask_result_tail*
    $bh_slot(S_result,n_object,$ptascii("value")) = (PROP_VALUE (ALIAS n_value))
    $propref_at(S_result.PROPREFS,n_value) = eps
    $call_reference_operand_valid(S_result,S_result.RESULT)
    $property_hook_result_tail(S_result,ppropertyhook,S_result.TODO)
    $heap_owners($heap_graph(S_result),HCELL n_value) = 2
    $bh_guard(S_result)
    PhpStep: S_result ~> S_alias_raw
    S_alias_raw = S_result[.TODO = ptask_result_tail*][.CELL = n_value][.BASE = BASE_VALUE (KNOWN PNULL)]
    S_alias = $bh_after(S_result,S_alias_raw)
    ''')
    checks += budget('S_result', 'S_result_budget')
    if group == 'default-null':
        checks += lines(r'''
        S_result.STORE[n_value] = DEFINED PNULL
        $bh_output(S_result.EVENTS) = $ptascii("N:G|")
        ''')
        checks += seek('S_alias', 30, 'S_before_unset') + lines(r'''
        $lookup(S_before_unset.ENV,$ptascii("alias")) = (n_value)
        S_before_unset.STORE[n_value] = DEFINED pvalue_second
        $string_bytes(pvalue_second) = ($ptascii("second"))
        $lookup(S_before_unset.ENV,$ptascii("copy")) = (n_copy)
        n_copy =/= n_value
        S_before_unset.STORE[n_copy] = DEFINED pvalue_first
        $string_bytes(pvalue_first) = ($ptascii("first"))
        $propref_at(S_before_unset.PROPREFS,n_value) = eps
        $bh_guard(S_before_unset)
        ''')
        checks += seek('S_before_unset', 31, 'S_detached') + lines(r'''
        $lookup(S_detached.ENV,$ptascii("object")) = eps
        ~((HOBJECT n_object) <- S_detached.ALLOCATIONS)
        S_detached.STORE[n_value] = DEFINED pvalue_second_detached
        $string_bytes(pvalue_second_detached) = ($ptascii("second"))
        S_detached.STORE[n_copy] = DEFINED pvalue_first_detached
        $string_bytes(pvalue_first_detached) = ($ptascii("first"))
        $propref_at(S_detached.PROPREFS,n_value) = eps
        $heap_owners($heap_graph(S_detached),HCELL n_value) = 1
        $bh_guard(S_detached)
        S_done = $drive(S_detached,4000)
        S_done.COMPLETION = NORMAL
        S_done.EXITSTATUS = 0
        S_done.TODO = eps
        $bh_output(S_done.EVENTS) = $ptascii("N:G|null|G|copy|alias|D|after|Z|")
        $bh_guard(S_done)
        ''')
    else:
        checks += lines(r'''
        S_result.STORE[n_value] = DEFINED (PINT 7)
        $bh_output(S_result.EVENTS) = $ptascii("A:G|")
        ''')
        checks += seek('S_alias', 12, 'S_string') + lines(r'''
        $lookup(S_string.ENV,$ptascii("alias")) = (n_value)
        S_string.STORE[n_value] = DEFINED pvalue_eight
        $string_bytes(pvalue_eight) = ($ptascii("8"))
        $propref_at(S_string.PROPREFS,n_value) = eps
        $bh_guard(S_string)
        ''')
        checks += seek('S_string', 13, 'S_before_unset') + lines(r'''
        S_before_unset.STORE[n_value] = DEFINED (PINT 9)
        $lookup(S_before_unset.ENV,$ptascii("copy")) = (n_copy)
        n_copy =/= n_value
        S_before_unset.STORE[n_copy] = DEFINED pvalue_copy
        $string_bytes(pvalue_copy) = ($ptascii("8"))
        $propref_at(S_before_unset.PROPREFS,n_value) = eps
        $bh_guard(S_before_unset)
        ''')
        checks += seek('S_before_unset', 14, 'S_detached') + lines(r'''
        $lookup(S_detached.ENV,$ptascii("object")) = eps
        ~((HOBJECT n_object) <- S_detached.ALLOCATIONS)
        S_detached.STORE[n_value] = DEFINED (PINT 9)
        S_detached.STORE[n_copy] = DEFINED pvalue_copy_detached
        $string_bytes(pvalue_copy_detached) = ($ptascii("8"))
        $propref_at(S_detached.PROPREFS,n_value) = eps
        $heap_owners($heap_graph(S_detached),HCELL n_value) = 1
        $bh_guard(S_detached)
        S_done = $drive(S_detached,4000)
        S_done.COMPLETION = NORMAL
        S_done.EXITSTATUS = 0
        S_done.TODO = eps
        $bh_output(S_done.EVENTS) = $ptascii("A:G|alias7|untyped8|G|copy8|alias9|D|free|copy-still8|Z|")
        $bh_guard(S_done)
        ''')
    return checks


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(command, out, timeout):
    process = recorder.recorded(command, out, timeout)
    assert not process['timeout'] and not process['interruption'] and not process['group_after']
    return SimpleNamespace(returncode=process['exit'], stdout=out.with_suffix('.stdout').read_bytes(),
                           stderr=out.with_suffix('.stderr').read_bytes())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--group', choices=['backing-alias','forbidden-rebind','default-null'])
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--control-only', action='store_true')
    args = parser.parse_args()
    assert not (args.group and args.control_only)
    data = json.loads((HERE/'untyped_reference_get_hook_cases.json').read_text())
    profile = json.loads((HERE/'profile.json').read_text())
    assert profile == data['native_profile']
    php = ROOT/'.tools/php/bin/php'
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    modules = [ROOT/name for name in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    out = Path(tempfile.mkdtemp(prefix='untyped-reference-get-', dir=ROOT/'.tools'))
    report = {'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
              'dirty':bool(subprocess.check_output(['git','status','--short'],cwd=ROOT)),
              'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [
                  php, ROOT/'.tools/php-file.so', ROOT/'.tools/spectec/bin/p4spectec',
                  ROOT/'_build/default/adapter/main.exe', HERE/'_build/default/numeric_runner.exe',
                  ROOT/'spec/semantics/modules.json', ROOT/'spec/semantics/382-backed-get-hooks.watsup',
                  HERE/'untyped_reference_get_hook_cases.json', Path(__file__)]},
              'profile':profile,'module_count':len(modules),'groups':[],
              'unsupported_controls':[],'passed':False}
    print(out, flush=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    for case in data['cases']:
        if args.control_only:
            break
        if args.group and case['id'] != args.group:
            continue
        group = case['id']
        source = out/(group+'.php')
        source.write_bytes(case['source'].encode())
        assert sha(source) == case['source_sha256']
        flags = [part for key,value in profile.items() for part in ('-d',key+'='+value)]
        native = run([str(php),'-n',*flags,str(source)], out/(group+'-native'),20)
        assert native.returncode == case['native']['exit_status']
        assert base64.b64encode(native.stdout).decode() == case['native']['stdout_base64']
        assert base64.b64encode(native.stderr).decode() == case['native']['stderr_base64']
        model = run([str(ROOT/'bin/php-semantics'),str(source),'--steps','100000','--timeout','75'],out/(group+'-model'),90)
        outcome = json.loads(model.stdout)
        assert model.returncode == 0 and model.stderr == b''
        assert outcome['status'] == 'normal' and outcome['exit_status'] == native.returncode
        assert base64.b64decode(outcome['stdout']) == native.stdout
        assert base64.b64decode(outcome['stderr']) == native.stderr
        row = {'group':group,'source_sha256':sha(source),'native_exit':native.returncode,
               'model_status':outcome['status'],'source_agreement':True,'state':None}
        if not args.source_only:
            frontend = Worker([str(php),'-n',*flags,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/(group+'-frontend'))
            try:
                parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
            finally:
                frontend.close()
            adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/(group+'-adapter'))
            try:
                checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                adapter.close()
            checks = conditions(group, checked['fixture'], source)
            fixture = out/(group+'-state.watsup')
            fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- '+('' if line.startswith('PhpStep:') else 'if ')+line+'\n' for line in checks))
            compiler = run([str(ROOT/'.tools/spectec/bin/p4spectec'),'algo',*map(str,modules),str(fixture)],out/(group+'-algo'),120)
            assert compiler.returncode == 0 and compiler.stderr == b'' and b'\ndef $main : bool =\n' in compiler.stdout
            state = run([str(HERE/'_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(fixture)],out/(group+'-state'),120)
            assert state.returncode == 0 and state.stderr == b'' and state.stdout == b'true\n'
            row['state'] = {'premises':len(checks),'raw_steps':sum(line.startswith('PhpStep:') for line in checks),
                            'fixture_sha256':sha(fixture),'result':'true'}
        report['groups'].append(row)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(group,row,flush=True)
    if not args.group:
        flags = [part for key,value in profile.items() for part in ('-d',key+'='+value)]
        for case in data['unsupported_controls']:
            group = case['id']
            source = out/(group+'.php')
            source.write_bytes(case['source'].encode())
            assert sha(source) == case['source_sha256']
            native = run([str(php),'-n',*flags,str(source)],out/(group+'-native'),20)
            assert native.returncode == case['native']['exit_status']
            assert base64.b64encode(native.stdout).decode() == case['native']['stdout_base64']
            assert base64.b64encode(native.stderr).decode() == case['native']['stderr_base64']
            model = run([str(ROOT/'bin/php-semantics'),str(source),'--steps','100000','--timeout','75'],out/(group+'-model'),90)
            outcome = json.loads(model.stdout)
            assert model.returncode == 1 and model.stderr == b''
            assert outcome['status'] == 'unsupported' and outcome['reason'] == case['model_reason']
            assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
            assert outcome['stdout'] == '' and outcome['stderr'] == ''
            row = {'group':group,'source_sha256':sha(source),'native_exit':native.returncode,
                   'model_status':'unsupported','source_agreement':False}
            report['unsupported_controls'].append(row)
            (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            print(group,row,flush=True)
    report['passed'] = True
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__':
    main()
