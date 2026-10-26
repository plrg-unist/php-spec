"""Pinned Grandchild reference Get sources and reached state certificates."""
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import untyped_reference_get_hook_protocol as base
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PREFIX = base.hook.PREFIX + r'''
def $bh_stage(S,50) = ($property_hook_ref_plan(S) =/= eps)
def $bh_stage(S,51) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (PROPERTY_BASE_PREP (NIdentifier (BYTES text) metadata) z) :: ptask*
  -- if $base64(text) = $ptascii("value")
  -- if ~$property_hook_pending(S)
def $bh_stage(S,52) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook text) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,53) = true
  -- if S.TODO = (UNSET (NExprVariable (BYTES text) metadata)) :: ptask*
  -- if $base64(text) = $ptascii("child")
  -- if S.CURRENT = eps /\ S.FRAMES = eps
dec $gr_without(pclasslink*, porigin) : pclasslink*
def $gr_without(eps, porigin) = eps
def $gr_without((CLASSLINK porigin pclassparent) :: pclasslink_tail*, porigin) = pclasslink_tail*
def $gr_without((CLASSLINK porigin_other pclassparent) :: pclasslink_tail*, porigin) = (CLASSLINK porigin_other pclassparent) :: $gr_without(pclasslink_tail*,porigin)
  -- if porigin_other =/= porigin
'''


def lines(value):
    return base.lines(value)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def conditions(case, program, path):
    checks = [f'S_initial = $php_run({program},0,{json.dumps(base64.b64encode(str(path).encode()).decode())})',
              'S_initial.COMPLETION = BUDGET']
    checks += base.seek('S_initial',50,'S_front') + lines(r'''
    $property_hook_ref_plan(S_front) = ((ppropertyhook,text_mode))
    $lookup(S_front.ENV,$ptascii("child")) = (n_receiver_cv)
    S_front.STORE[n_receiver_cv] = DEFINED (POBJECT n_object)
    ppropertyhook.OBJECT = n_object
    S_front.OBJECTS[n_object] = INSTANCE porigin_grandchild
    $class_at(S_front.CLASSES,porigin_grandchild) = (pclassdesc_grandchild)
    pclassdesc_grandchild.PROPERTIES = eps
    pclassdesc_grandchild.INTERFACES = eps
    pclassdesc_grandchild.CONSTANTS = eps
    $class_link_at(S_front.LINKEDPARENTS,porigin_grandchild) = (SOURCE_PARENT porigin_child)
    $class_at(S_front.CLASSES,porigin_child) = (pclassdesc_child)
    pclassdesc_child.PROPERTIES = [ppropertydesc_child]
    $class_link_at(S_front.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)
    $class_at(S_front.CLASSES,porigin_parent) = (pclassdesc_parent)
    pclassdesc_parent.PARENT = eps
    $property_effective_desc(S_front,n_object,$ptascii("value")) = (ppropertydesc_child)
    ppropertydesc_child.ORIGIN = porigin_child_property
    $property_declaring_class(S_front.CLASSES,porigin_child_property) = (porigin_child)
    $property_hook_getter(S_front,ppropertydesc_child) = (ppropertydesc_parent)
    $property_declaring_class(S_front.CLASSES,ppropertydesc_parent.ORIGIN) = (porigin_parent)
    $property_hook_plain_child_reference(S_front,porigin_child,porigin_parent,ppropertydesc_child,ppropertydesc_parent)
    $property_hook_plain_grandchild_reference(S_front,porigin_grandchild,porigin_parent,ppropertydesc_child,ppropertydesc_parent)
    $property_hook_reference_decl(S_front,ppropertydesc_parent)
    $property_hook_function(S_front,ppropertyhook) = (pfunction_hook)
    pfunction_hook.SIGNATURE = {PARAMETERS eps,RETURNS ppropertydesc_parent.TYPE,BYREF true}
    $target_lexical_class(S_front,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_parent)
    $target_called_class(S_front,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_grandchild)
    $objectprops_at(S_front.OBJECTPROPS,n_object) = (ppropertyslot*)
    $property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_child)
    ppropertyslot_child.DECL = (ppropertydesc_child.ORIGIN)
    S_no_grand = S_front[.LINKEDPARENTS = $gr_without(S_front.LINKEDPARENTS,porigin_grandchild)]
    ~$property_hook_plain_grandchild_reference(S_no_grand,porigin_grandchild,porigin_parent,ppropertydesc_child,ppropertydesc_parent)
    S_no_child = S_front[.LINKEDPARENTS = $gr_without(S_front.LINKEDPARENTS,porigin_child)]
    ~$property_hook_plain_grandchild_reference(S_no_child,porigin_grandchild,porigin_parent,ppropertydesc_child,ppropertydesc_parent)
    $bh_guard(S_front)
    ''')
    typed = case == 'typed-grandchild-alias'
    bind = case == 'untyped-grandchild-rebind-write'
    null = case == 'untyped-grandchild-null'
    checks += lines('text_mode = "bind"' if bind else 'text_mode = "fetch"')
    if bind:
        checks += lines('ppropertyhook.LINE = 18')
    checks += lines('ppropertydesc_child.TYPE = [PTBRANCH ([PTBUILTIN "int"])]' if typed else 'ppropertydesc_child.TYPE = eps')
    checks += lines('ppropertydesc_parent.TYPE = ppropertydesc_child.TYPE')
    if null:
        checks += lines('ppropertydesc_child.DEFAULT = PROP_NULL\nppropertyslot_child.STATE = PROP_VALUE (DIRECT PNULL)')
    elif bind:
        checks += lines(r'''
        ppropertyslot_child.STATE = PROP_VALUE (DIRECT pvalue_own)
        $string_bytes(pvalue_own) = ($ptascii("own"))
        $lookup(S_front.ENV,$ptascii("replacement")) = (n_rhs)
        S_front.STORE[n_rhs] = DEFINED (PINT 17)
        ''')
    else:
        checks += lines('ppropertyslot_child.STATE = PROP_VALUE (DIRECT (PINT 11))')
    checks += base.seek('S_front',51,'S_backing') + lines(r'''
    S_backing.CURRENT = (pcallcontext_backing)
    pcallcontext_backing.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
    pcallcontext_backing.RECEIVER = (n_object)
    pcallcontext_backing.LEXICAL_CLASS = (porigin_parent)
    pcallcontext_backing.CALLED_CLASS = (porigin_grandchild)
    $property_effective_desc(S_backing,n_object,$ptascii("value")) = (ppropertydesc_child)
    $property_hook_backing(S_backing,n_object,ppropertydesc_child)
    ~$property_hook_read_needed(S_backing,n_object,$ptascii("value"))
    $bh_guard(S_backing)
    ''')
    checks += base.seek('S_backing',52,'S_result') + lines(r'''
    S_result.RESULT = REFERENCE n_value
    $objectprops_at(S_result.OBJECTPROPS,n_object) = (ppropertyslot_result*)
    $property_slot_at(ppropertyslot_result*,$ptascii("value")) = (ppropertyslot_child_result)
    ppropertyslot_child_result.DECL = (ppropertydesc_child.ORIGIN)
    ppropertyslot_child_result.STATE = PROP_VALUE (ALIAS n_value)
    $property_hook_result_tail(S_result,ppropertyhook,S_result.TODO)
    $bh_guard(S_result)
    ''')
    if typed:
        checks += lines(r'''
        S_result.STORE[n_value] = DEFINED (PINT 11)
        $propref_at(S_result.PROPREFS,n_value) = (ppropref)
        ppropref.SOURCES = [OBJECT_PROP_SOURCE n_object ($ptascii("value")) ppropertydesc_child.ORIGIN]
        $proprefs_valid(S_result)
        ''')
    else:
        checks += lines('$propref_at(S_result.PROPREFS,n_value) = eps')
    if bind:
        checks += lines(r'''
        S_result.STORE[n_value] = DEFINED pvalue_own_result
        $string_bytes(pvalue_own_result) = ($ptascii("own"))
        S_result.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "bind") :: ptask_result_tail*
        $bh_output(S_result.EVENTS) = $ptascii("R:G|")
        PhpStep: S_result ~> S_error_raw
        S_error_raw = S_result[.COMPLETION = THROWN "Error" ($ptascii("Cannot assign by reference to overloaded object")) 18]
        S_error = $bh_after(S_result,S_error_raw)
        ''')
        checks += base.budget('S_result','S_error_budget')
        checks += lines(r'''
        S_done = $drive(S_error,4000)
        S_done.COMPLETION = NORMAL
        S_done.EXITSTATUS = 0
        S_done.TODO = eps
        $bh_output(S_done.EVENTS) = $ptascii("R:G|blocked|line|file|G|kept-own|G|separate-own|rhs19|D|Z|")
        $bh_guard(S_done)
        ''')
    else:
        checks += lines(r'''
        S_result.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask_result_tail*
        PhpStep: S_result ~> S_alias_raw
        S_alias_raw = S_result[.TODO = ptask_result_tail*][.CELL = n_value][.BASE = BASE_VALUE (KNOWN PNULL)]
        S_alias = $bh_after(S_result,S_alias_raw)
        ''')
        checks += base.budget('S_result','S_result_budget')
        checks += base.seek('S_alias',53,'S_before_unset') + lines(r'''
        $lookup(S_before_unset.ENV,$ptascii("alias")) = (n_value)
        $lookup(S_before_unset.ENV,$ptascii("copy")) = (n_copy)
        n_copy =/= n_value
        ''')
        if typed:
            checks += lines(r'''
            S_before_unset.STORE[n_value] = DEFINED (PINT 13)
            S_before_unset.STORE[n_copy] = DEFINED (PINT 12)
            $propref_at(S_before_unset.PROPREFS,n_value) = (ppropref)
            ppropref.SOURCES = [OBJECT_PROP_SOURCE n_object ($ptascii("value")) ppropertydesc_child.ORIGIN]
            ''')
        elif null:
            checks += lines(r'''
            S_before_unset.STORE[n_value] = DEFINED pvalue_set
            $string_bytes(pvalue_set) = ($ptascii("set"))
            S_before_unset.STORE[n_copy] = DEFINED PNULL
            $propref_at(S_before_unset.PROPREFS,n_value) = eps
            ''')
        else:
            checks += lines(r'''
            S_before_unset.STORE[n_value] = DEFINED (PINT 13)
            S_before_unset.STORE[n_copy] = DEFINED pvalue_word
            $string_bytes(pvalue_word) = ($ptascii("word"))
            $propref_at(S_before_unset.PROPREFS,n_value) = eps
            ''')
        checks += lines(r'''
        $bh_guard(S_before_unset)
        S_done = $drive(S_before_unset,4000)
        S_done.COMPLETION = NORMAL
        S_done.EXITSTATUS = 0
        S_done.TODO = eps
        $bh_guard(S_done)
        ''')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--group', choices=['untyped-grandchild-alias','untyped-grandchild-null','untyped-grandchild-rebind-write','typed-grandchild-alias'])
    args = parser.parse_args()
    data = json.loads((HERE/'grandchild_reference_get_hook_cases.json').read_text())
    profile = json.loads((HERE/'profile.json').read_text())
    assert data['native_profile'] == profile
    php = ROOT/'.tools/php/bin/php'
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    modules = [ROOT/name for name in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    out = Path(tempfile.mkdtemp(prefix='grandchild-reference-get-',dir=ROOT/'.tools'))
    report = {'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
              'dirty':bool(subprocess.check_output(['git','status','--short'],cwd=ROOT)),
              'inputs':{str(p.relative_to(ROOT)):sha(p) for p in [php,ROOT/'.tools/php-file.so',
                  ROOT/'.tools/spectec/bin/p4spectec',ROOT/'_build/default/adapter/main.exe',
                  HERE/'_build/default/numeric_runner.exe',ROOT/'spec/semantics/modules.json',
                  ROOT/'spec/semantics/382-backed-get-hooks.watsup',
                  HERE/'grandchild_reference_get_hook_cases.json',Path(__file__)]},
              'profile':profile,'module_count':len(modules),'groups':[],
              'unsupported_controls':[],'passed':False}
    print(out,flush=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    flags = [part for key,value in profile.items() for part in ('-d',key+'='+value)]
    for case in data['cases']:
        if args.group and case['id'] != args.group: continue
        source = out/(case['id']+'.php')
        source.write_bytes(case['source'].encode())
        assert sha(source) == case['source_sha256']
        native = base.run([str(php),'-n',*flags,str(source)],out/(case['id']+'-native'),20)
        assert native.returncode == case['native']['exit_status']
        assert base64.b64encode(native.stdout).decode() == case['native']['stdout_base64']
        assert base64.b64encode(native.stderr).decode() == case['native']['stderr_base64']
        model = base.run([str(ROOT/'bin/php-semantics'),str(source),'--steps','100000','--timeout','75'],out/(case['id']+'-model'),90)
        outcome = json.loads(model.stdout)
        assert model.returncode == 0 and model.stderr == b''
        assert outcome['status'] == 'normal' and outcome['exit_status'] == native.returncode
        assert base64.b64decode(outcome['stdout']) == native.stdout
        assert base64.b64decode(outcome['stderr']) == native.stderr
        row = {'group':case['id'],'source_sha256':sha(source),'source_agreement':True,'state':None}
        if not args.source_only:
            frontend = Worker([str(php),'-n',*flags,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/(case['id']+'-frontend'))
            try:
                parsed = frontend.request({'op':'parse','source':base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
            finally: frontend.close()
            adapter = Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/(case['id']+'-adapter'))
            try:
                checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally: adapter.close()
            checks = conditions(case['id'],checked['fixture'],source)
            fixture = out/(case['id']+'-state.watsup')
            fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- '+('' if line.startswith('PhpStep:') else 'if ')+line+'\n' for line in checks))
            compiler = base.run([str(ROOT/'.tools/spectec/bin/p4spectec'),'algo',*map(str,modules),str(fixture)],out/(case['id']+'-algo'),120)
            assert compiler.returncode == 0 and compiler.stderr == b'' and b'\ndef $main : bool =\n' in compiler.stdout
            state = base.run([str(HERE/'_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(fixture)],out/(case['id']+'-state'),120)
            assert state.returncode == 0 and state.stderr == b'' and state.stdout == b'true\n'
            row['state'] = {'premises':len(checks),'raw_steps':sum(line.startswith('PhpStep:') for line in checks),
                            'fixture_sha256':sha(fixture),'result':'true'}
        report['groups'].append(row)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(case['id'],row,flush=True)
    if not args.group:
        for case in data['unsupported_controls']:
            source = out/(case['id']+'.php')
            source.write_bytes(case['source'].encode())
            assert sha(source) == case['source_sha256']
            native = base.run([str(php),'-n',*flags,str(source)],out/(case['id']+'-native'),20)
            assert native.returncode == case['native']['exit_status']
            assert base64.b64encode(native.stdout).decode() == case['native']['stdout_base64']
            assert base64.b64encode(native.stderr).decode() == case['native']['stderr_base64']
            model = base.run([str(ROOT/'bin/php-semantics'),str(source),'--steps','100000','--timeout','75'],out/(case['id']+'-model'),90)
            outcome = json.loads(model.stdout)
            assert model.returncode == 1 and model.stderr == b''
            assert outcome['status'] == case['model']['status'] and outcome['reason'] == case['model']['reason']
            assert outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
            assert outcome['stdout'] == case['model']['stdout_base64'] and outcome['stderr'] == case['model']['stderr_base64']
            report['unsupported_controls'].append({'group':case['id'],'source_sha256':sha(source),
                'model_status':'unsupported','source_agreement':False})
            (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            print(case['id'],'Unsupported control',flush=True)
    report['passed'] = True
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__': main()
