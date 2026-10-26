"""Frozen source comparisons and reached checks for inherited reference Get chains."""
import argparse
import base64
import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

import grandchild_reference_get_hook_protocol as old
from recorded_worker import Worker

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CATALOGUE_HASH = "7ec6a17e1e781751687abd9f9940466692cbcd50a040d03d3e3bd93784bcafdd"
CONFIG = {
    "greatgrandchild-promoted": ("DeepGreatgrandchild137", "DeepChild137", "DeepParent137", 11, False, ["DeepGrandchild137", "DeepGreatgrandchild137"]),
    "untyped-latest-redeclaration": ("ChainLeaf138", "ChainLeaf138", "ChainParent138", 21, False, ["ChainMiddle138", "ChainLeaf138"]),
    "typed-latest-type-source": ("TypedLeaf138", "TypedLeaf138", "TypedParent138", 21, True, ["TypedMiddle138", "TypedLeaf138"]),
    "mixed-unchanged-redeclaration": ("MixedLeaf138", "MixedMiddle138", "MixedParent138", 31, False, ["MixedChild138", "MixedLeaf138"]),
    "deep-rebind-error": ("RebindLeaf138", "RebindMiddle138", "RebindParent138", 41, False, ["RebindChild138", "RebindLeaf138"]),
}
PREFIX = old.base.hook.PREFIX + r'''
def $bh_stage(S,60) = ($property_hook_ref_plan(S) =/= eps)
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $bh_stage(S,61) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $property_hook_context_kind(pcallcontext)
  -- if S.TODO = (PROPERTY_BASE_PREP (NIdentifier (BYTES text) metadata) z) :: ptask*
  -- if $base64(text) = $ptascii("value")
  -- if ~$property_hook_pending(S)
def $bh_stage(S,62) = true
  -- if S.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook text) :: ptask*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
dec $rc_without(pclasslink*, porigin) : pclasslink*
def $rc_without(eps, porigin) = eps
def $rc_without((CLASSLINK porigin pclassparent) :: pclasslink_tail*, porigin) = pclasslink_tail*
def $rc_without((CLASSLINK porigin_other pclassparent) :: pclasslink_tail*, porigin) = (CLASSLINK porigin_other pclassparent) :: $rc_without(pclasslink_tail*,porigin)
  -- if porigin_other =/= porigin
'''


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lines(source):
    return old.base.lines(source)


def quote(value):
    return json.dumps(value)


def conditions(case, program, path, expected):
    receiver, storage, getter, initial, typed, gaps = CONFIG[case]
    mode = "bind" if case == "deep-rebind-error" else "fetch"
    object_cv = "child" if case == "greatgrandchild-promoted" else "object"
    checks = [f'S_initial = $php_run({program},0,{quote(base64.b64encode(str(path).encode()).decode())})',
              'S_initial.COMPLETION = BUDGET']
    checks += old.base.seek('S_initial', 60, 'S_front') + lines(r'''
    $property_hook_ref_plan(S_front) = ((ppropertyhook,TEXT_MODE))
    $lookup(S_front.ENV,$ptascii("OBJECT_CV")) = (n_receiver_cv)
    S_front.STORE[n_receiver_cv] = DEFINED (POBJECT n_object)
    ppropertyhook.OBJECT = n_object
    S_front.OBJECTS[n_object] = INSTANCE porigin_receiver
    $class_named(S_front.CLASSNAMES,$ptlc($ptascii("RECEIVER"))) = (porigin_receiver)
    $class_named(S_front.CLASSNAMES,$ptlc($ptascii("STORAGE"))) = (porigin_storage)
    $class_named(S_front.CLASSNAMES,$ptlc($ptascii("GETTER"))) = (porigin_getter)
    $class_at(S_front.CLASSES,porigin_storage) = (pclassdesc_storage)
    $property_effective_desc(S_front,n_object,$ptascii("value")) = (ppropertydesc_storage)
    ppropertydesc_storage.ORIGIN = porigin_storage_property
    $property_declaring_class(S_front.CLASSES,porigin_storage_property) = (porigin_storage)
    $hook_property_at(pclassdesc_storage.PROPERTIES,porigin_storage_property) = (ppropertydesc_storage)
    $property_desc_at($property_layout(S_front,porigin_receiver,|S_front.CLASSES|),$ptascii("value")) = (ppropertydesc_storage)
    $property_hook_getter(S_front,ppropertydesc_storage) = (ppropertydesc_getter)
    $property_declaring_class(S_front.CLASSES,ppropertydesc_getter.ORIGIN) = (porigin_getter)
    $property_hook_reference_decl(S_front,ppropertydesc_getter)
    $property_hook_reference_plain_chain(S_front,ppropertydesc_storage,ppropertydesc_getter,|S_front.CLASSES|)
    $property_hook_reference_receiver_chain(S_front,porigin_receiver,ppropertydesc_storage,ppropertydesc_getter,|S_front.CLASSES|)
    ~$property_hook_plain_grandchild_reference(S_front,porigin_receiver,porigin_getter,ppropertydesc_storage,ppropertydesc_getter)
    $property_hook_function(S_front,ppropertyhook) = (pfunction_hook)
    pfunction_hook.SIGNATURE = {PARAMETERS eps,RETURNS ppropertydesc_getter.TYPE,BYREF true}
    $target_lexical_class(S_front,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_getter)
    $target_called_class(S_front,PROPERTY_HOOK_TARGET ppropertyhook) = (porigin_receiver)
    $objectprops_at(S_front.OBJECTPROPS,n_object) = (ppropertyslot*)
    $property_slot_at(ppropertyslot*,$ptascii("value")) = (ppropertyslot_storage)
    ppropertyslot_storage.DECL = porigin_storage_property
    ppropertyslot_storage.STATE = PROP_VALUE (DIRECT (PINT INITIAL))
    $property_default_state(S_front,ppropertydesc_storage) = (PROP_VALUE (DIRECT (PINT INITIAL)))
    $bh_guard(S_front)
    '''.replace('TEXT_MODE',quote(mode)).replace('OBJECT_CV',object_cv).replace('RECEIVER',receiver).replace('STORAGE',storage).replace('GETTER',getter).replace('INITIAL',str(initial)))
    for index, gap in enumerate(gaps):
        checks += lines(f'''
        $class_named(S_front.CLASSNAMES,$ptlc($ptascii({quote(gap)}))) = (porigin_gap_{index})
        S_gap_{index} = S_front[.LINKEDPARENTS = $rc_without(S_front.LINKEDPARENTS,porigin_gap_{index})]
        ~$property_hook_reference_receiver_chain(S_gap_{index},porigin_receiver,ppropertydesc_storage,ppropertydesc_getter,|S_gap_{index}.CLASSES|)
        ''')
    if case in ("untyped-latest-redeclaration", "typed-latest-type-source"):
        child = "ChainChild138" if not typed else "TypedChild138"
        checks += lines(f'''
        $class_named(S_front.CLASSNAMES,$ptlc($ptascii({quote(child)}))) = (porigin_old_child)
        $class_at(S_front.CLASSES,porigin_old_child) = (pclassdesc_old_child)
        pclassdesc_old_child.PROPERTIES = [ppropertydesc_old_child]
        ppropertydesc_old_child.ORIGIN =/= porigin_storage_property
        $property_default_state(S_front,ppropertydesc_old_child) = (PROP_VALUE (DIRECT (PINT 11)))
        ''')
    checks += lines('ppropertydesc_storage.TYPE = [PTBRANCH ([PTBUILTIN "int"])]' if typed else 'ppropertydesc_storage.TYPE = eps')
    checks += old.base.seek('S_front', 61, 'S_backing') + lines(r'''
    S_backing.CURRENT = (pcallcontext_backing)
    pcallcontext_backing.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
    pcallcontext_backing.RECEIVER = (n_object)
    pcallcontext_backing.LEXICAL_CLASS = (porigin_getter)
    pcallcontext_backing.CALLED_CLASS = (porigin_receiver)
    $property_effective_desc(S_backing,n_object,$ptascii("value")) = (ppropertydesc_storage)
    $property_hook_backing(S_backing,n_object,ppropertydesc_storage)
    ~$property_hook_read_needed(S_backing,n_object,$ptascii("value"))
    $bh_guard(S_backing)
    ''')
    checks += old.base.seek('S_backing', 62, 'S_result') + lines(r'''
    S_result.RESULT = REFERENCE n_value
    S_result.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook TEXT_MODE) :: ptask_result_any*
    S_result.STORE[n_value] = DEFINED (PINT INITIAL)
    $objectprops_at(S_result.OBJECTPROPS,n_object) = (ppropertyslot_result*)
    $property_slot_at(ppropertyslot_result*,$ptascii("value")) = (ppropertyslot_storage_result)
    ppropertyslot_storage_result.DECL = porigin_storage_property
    ppropertyslot_storage_result.STATE = PROP_VALUE (ALIAS n_value)
    $property_hook_result_tail(S_result,ppropertyhook,S_result.TODO)
    $bh_guard(S_result)
    '''.replace('TEXT_MODE',quote(mode)).replace('INITIAL',str(initial)))
    if typed:
        checks += lines(r'''
        $propref_at(S_result.PROPREFS,n_value) = (ppropref)
        ppropref.SOURCES = [OBJECT_PROP_SOURCE n_object ($ptascii("value")) porigin_storage_property]
        $proprefs_valid(S_result)
        ''')
    else:
        checks += lines('$propref_at(S_result.PROPREFS,n_value) = eps')
    if mode == 'bind':
        checks += lines(r'''
        ppropertyhook.LINE = 16
        $lookup(S_result.ENV,$ptascii("replacement")) = (n_rhs)
        S_result.STORE[n_rhs] = DEFINED (PINT 17)
        PhpStep: S_result ~> S_raw
        S_raw = S_result[.COMPLETION = THROWN "Error" ($ptascii("Cannot assign by reference to overloaded object")) 16]
        S_after = $bh_after(S_result,S_raw)
        ''')
    else:
        checks += lines(r'''
        S_result.TODO = (PROPERTY_HOOK_REF_RESULT ppropertyhook "fetch") :: (PROPERTY_REF_FETCH z) :: ptask_result_tail*
        PhpStep: S_result ~> S_raw
        S_raw = S_result[.TODO = ptask_result_tail*][.CELL = n_value][.BASE = BASE_VALUE (KNOWN PNULL)]
        S_after = $bh_after(S_result,S_raw)
        ''')
    checks += old.base.budget('S_result','S_result_budget')
    output = base64.b64decode(expected['stdout_base64']).decode('ascii')
    checks += lines(f'''
    S_done = $drive(S_after,4000)
    S_done.COMPLETION = NORMAL
    S_done.EXITSTATUS = 0
    S_done.TODO = eps
    $bh_output(S_done.EVENTS) = $ptascii({quote(output)})
    $bh_guard(S_done)
    ''')
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-only', action='store_true')
    parser.add_argument('--group', choices=list(CONFIG) + ['hook-bearing-intermediate-control', 'changed-type-static-control'])
    args = parser.parse_args()
    catalogue = HERE/'reference_get_chain_cases.json'
    expectations = HERE/'reference_get_chain_expectations.json'
    data = json.loads(catalogue.read_text())
    expected = json.loads(expectations.read_text())
    assert sha(catalogue) == CATALOGUE_HASH == expected['frozen_catalogue_sha256']
    php = ROOT/'.tools/php/bin/php'
    assert sha(php) == expected['oracle_sha256']
    profile = json.loads((HERE/'profile.json').read_text())
    assert sha(HERE/'profile.json') == expected['native_profile_sha256']
    modules = [ROOT/name for name in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    out = Path(tempfile.mkdtemp(prefix='reference-get-chain-',dir=ROOT/'.tools'))
    report = {'revision':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
              'dirty':bool(subprocess.check_output(['git','status','--short'],cwd=ROOT)),
              'catalogue_sha256':sha(catalogue),'expectations_sha256':sha(expectations),
              'semantic_sha256':sha(ROOT/'spec/semantics/382-backed-get-hooks.watsup'),
              'protocol_sha256':sha(Path(__file__)),'groups':[],'passed':False}
    print(out,flush=True)
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    flags = [part for key,value in profile.items() for part in ('-d',key+'='+value)]
    for case in data['cases']:
        if args.group and case['id'] != args.group: continue
        source = out/(case['id']+'.php')
        source.write_bytes(case['source'].encode())
        assert sha(source) == case['source_sha256']
        native = old.base.run([str(php),'-n',*flags,str(source)],out/(case['id']+'-native'),20)
        entry = expected['cases'][case['id']]
        assert native.returncode == entry['exit_status']
        if case['id'] == 'changed-type-static-control':
            assert b'Type of TypeChild138::$value must be int (as in class TypeParent138)' in native.stderr
            assert str(source).encode()+b' on line 7' in native.stderr
        else:
            assert base64.b64encode(native.stdout).decode() == entry['stdout_base64']
            assert base64.b64encode(native.stderr).decode() == entry['stderr_base64']
        model = old.base.run([str(ROOT/'bin/php-semantics'),str(source),'--steps','100000','--timeout','75'],out/(case['id']+'-model'),90)
        outcome = json.loads(model.stdout)
        row = {'group':case['id'],'source_sha256':sha(source),'native_exit':native.returncode,
               'model_status':outcome['status'],'source_agreement':False,'state':None}
        if case['kind'] == 'boundary':
            assert model.stderr == b'' and outcome['frontend'] == 'accepted' and outcome['checked'] == 'program'
            if case['id'] == 'changed-type-static-control':
                assert model.returncode == 0 and outcome['status'] == 'static_rejection'
                assert outcome['exit_status'] == 255 and outcome['stdout'] == ''
                assert outcome['diagnostic']['class'] == 'CompileError'
                assert base64.b64decode(outcome['diagnostic']['message']) == b'Type of TypeChild138::$value must be int (as in class TypeParent138)'
                assert outcome['diagnostic']['line'] == 7
                assert base64.b64decode(outcome['stderr']) == native.stderr
            else:
                assert model.returncode == 1 and outcome['status'] == 'unsupported'
                assert outcome['reason'] == 'set, by-reference, attributed or defaulted virtual property hook'
                assert outcome['stdout'] == '' and outcome['stderr'] == ''
            report['groups'].append(row)
            (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
            print(case['id'],row,flush=True)
            continue
        assert model.returncode == 0 and model.stderr == b'' and outcome['status'] == 'normal'
        assert outcome['exit_status'] == native.returncode
        assert base64.b64decode(outcome['stdout']) == native.stdout
        assert base64.b64decode(outcome['stderr']) == native.stderr
        row['source_agreement'] = True
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
            checks = conditions(case['id'],checked['fixture'],source,entry)
            fixture = out/(case['id']+'-state.watsup')
            fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- '+('' if line.startswith('PhpStep:') else 'if ')+line+'\n' for line in checks))
            compiler = old.base.run([str(ROOT/'.tools/spectec/bin/p4spectec'),'algo',*map(str,modules),str(fixture)],out/(case['id']+'-algo'),120)
            assert compiler.returncode == 0 and compiler.stderr == b'' and b'\ndef $main : bool =\n' in compiler.stdout
            state = old.base.run([str(HERE/'_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(fixture)],out/(case['id']+'-state'),120)
            assert state.returncode == 0 and state.stderr == b'' and state.stdout == b'true\n'
            row['state'] = {'premises':len(checks),'raw_steps':sum(line.startswith('PhpStep:') for line in checks),
                            'fixture_sha256':sha(fixture),'result':'true'}
        report['groups'].append(row)
        (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(case['id'],row,flush=True)
    report['passed'] = True
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n')


if __name__ == '__main__': main()
