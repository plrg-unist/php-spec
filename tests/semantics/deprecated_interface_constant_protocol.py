#!/usr/bin/env python3
"""Check declaring-interface cache replacement and original eval prefixes."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

from deprecated_global_constant_protocol import PREFIX, nodes
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SELECTIONS = {name: ROOT / 'tests/semantics/deprecated_interface_constant' / source for name,source in [('computed','computed-reentry.php'),('prefix','eval-prefix.php')]}
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
SELECTED = r'''
dec $ic_parent_ready(pstate,pclassconstantcontext) : bool
def $ic_parent_ready(S,pclassconstantcontext) = true
  -- if S.TODO = (CLASS_CONST_BIND pclassconstantcontext.DECL) :: ptask*
  -- if S.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*
def $ic_parent_ready(S,pclassconstantcontext) = false -- otherwise
dec $ic_parent_pause(pstate,pclassconstantcontext,nat) : pstate
def $ic_parent_pause(S,pclassconstantcontext,n) = S -- if $ic_parent_ready(S,pclassconstantcontext)
def $ic_parent_pause(S,pclassconstantcontext,n) = $ic_parent_pause(S_next[.COMPLETION = NORMAL],pclassconstantcontext,$nabs($(n - 1)))
  -- if ~$ic_parent_ready(S,pclassconstantcontext)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $ic_parent_pause(S,pclassconstantcontext,n) = S -- otherwise
dec $ic_publish_ready(pstate) : bool
def $ic_publish_ready(S) = true -- if S.TODO = (CLASS_CACHE_PUBLISH pclassreplacement) :: ptask*
def $ic_publish_ready(S) = false -- otherwise
dec $ic_publish_pause(pstate,nat) : pstate
def $ic_publish_pause(S,n) = S -- if $ic_publish_ready(S)
def $ic_publish_pause(S,n) = $ic_publish_pause(S_next[.COMPLETION = NORMAL],$nabs($(n - 1)))
  -- if ~$ic_publish_ready(S)
  -- if S.COMPLETION = NORMAL /\ $(n > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $ic_publish_pause(S,n) = S -- otherwise
dec $ic_output_item(pevent) : ptbytes
def $ic_output_item(OUTPUT ptbytes) = ptbytes
def $ic_output_item(pevent) = eps -- otherwise
dec $ic_output(pevent*) : ptbytes
def $ic_output(eps) = eps
def $ic_output(pevent :: pevent_tail*) = $ic_output_item(pevent) ++ $ic_output(pevent_tail*)
'''


def data(value):
    return '$base64('+json.dumps(base64.b64encode(value.encode()).decode())+')'


def start(fixture,path,namespace):
    return ['U = '+fixture,'S_start = $php_run(U,0,'+json.dumps(base64.b64encode(bytes(path)).decode())+')',
        'S_start.COMPLETION = BUDGET','S_warn = $dep_pause(S_start[.COMPLETION = NORMAL],20000)',
        'S_warn.COMPLETION = NORMAL','S_warn.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_warn*',
        'perrorcall.RESUME = DEPRECATED_CONSTANT_RESULT pdeprecatedconstant',
        'S_warn.CONSTCONTEXT = (pconstantcontext)',
        'S_warn.CLASSCONSTANTINIT = pclassconstantcontext :: pclassconstantcontext_tail*',
        'pclassconstantcontext.DECL = pconstantcontext.ORIGIN',
        '$class_constant_origin(S_warn.CLASSES,pclassconstantcontext.DECL) = (pclassconstantdesc)',
        '$class_at(S_warn.CLASSES,pclassconstantdesc.OWNER) = (pclassdesc)','pclassdesc.KIND = "interface"',
        '$owned_class_constant_source(S_warn,pclassconstantdesc)',
        '~$owned_class_constant_source(S_warn,pclassconstantdesc[.VISIBILITY = PROPERTY_PRIVATE])',
        '$deprecated_constant_class_ast(S_warn,pdeprecatedconstant.SITE)',
        '$class_constant_pending_cache(S_warn,pclassconstantcontext)',
        '$default_cache_at(S_warn.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = eps',
        '$class_named(S_warn.CLASSNAMES,$ptlc('+data(namespace+'\\Child210')+')) = (porigin_child)',
        '$class_named(S_warn.CLASSNAMES,$ptlc('+data(namespace+'\\Impl210')+')) = (porigin_impl)',
        '$class_constant_lookup(S_warn,porigin_child,$ptascii("C"),|S_warn.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_lookup(S_warn,porigin_impl,$ptascii("C"),|S_warn.CLASSES|) = (pclassconstantdesc)',
        '$call_descriptors_valid(S_warn)']


def finish(path,state):
    expected=json.loads((path.parent/'cases.json').read_text())[path.stem]['stdout'].encode()
    return ['S_done = $drive_steps('+state+',30000)','S_done.COMPLETION = NORMAL',
        '$ic_output(S_done.EVENTS) = $base64('+json.dumps(base64.b64encode(expected).decode())+')',
        '|S_done.CLASSCONSTANTCACHE| = 1',
        '$class_constant_lookup(S_done,porigin_child,$ptascii("C"),|S_done.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_lookup(S_done,porigin_impl,$ptascii("C"),|S_done.CLASSES|) = (pclassconstantdesc)',
        '$class_constant_history_valid(S_done)',
        '$machine_roots(S_done[.CLASSCONSTANTHISTORY = eps]) = $machine_roots(S_done)']


def computed(fixture,path,responses):
    return start(fixture,path,'Ns210Cache')+[
        'S_bind = $ic_parent_pause(S_warn,pclassconstantcontext,20000)','$ic_parent_ready(S_bind,pclassconstantcontext)',
        '$default_cache_at(S_bind.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_old)',
        'pdefaultcache_old.VALUE = PARRAY n_old','S_bind.ARRAYS[n_old].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        'S_bind.RESULT = KNOWN (PARRAY n_new)','n_old =/= n_new',
        '$heap_owners($heap_graph(S_bind),HARRAY n_old) = 1','$heap_owners($heap_graph(S_bind),HARRAY n_new) = 1',
        '$call_descriptors_valid(S_bind)',
        'S_stage = $drive_steps(S_bind,1)','S_stage.COMPLETION = BUDGET',
        'S_stage.CLASSCONSTANTWRITES = [pclassreplacement]',
        'pclassreplacement.OLD = pdefaultcache_old','pclassreplacement.CONTEXT.DECL = pclassconstantdesc.ORIGIN',
        '$class_write_live(S_stage,pclassreplacement)',
        'S_stage.CLASSCONSTANTCACHE = S_bind.CLASSCONSTANTCACHE','S_stage.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY',
        '$heap_owners($heap_graph(S_stage),HARRAY n_old) = 1',
        '~((HARRAY n_old) <- $class_constant_machine_roots(S_stage))',
        '$heap_owners($heap_graph(S_stage),HARRAY n_new) = 1','(HARRAY n_new) <- $tasks_nodes(S_stage.TODO)',
        '~$class_constant_cache_readable(S_stage,pclassconstantcontext.DECL)',
        '$class_image_valid(pclassreplacement.IMAGE)','$call_descriptors_valid(S_stage)',
        'S_ready = $ic_publish_pause(S_stage[.COMPLETION = NORMAL],20000)','$ic_publish_ready(S_ready)',
        '~((HARRAY n_old) <- S_ready.ALLOCATIONS)','(HARRAY n_new) <- S_ready.ALLOCATIONS',
        'S_ready.CLASSCONSTANTHISTORY = S_bind.CLASSCONSTANTHISTORY','$class_write_live(S_ready,pclassreplacement)',
        '$call_descriptors_valid(S_ready)',
    ]+finish(path,'S_ready')+[
        'S_done.CLASSCONSTANTWRITES = eps',
        '$default_cache_at(S_done.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_new)',
        'pdefaultcache_new.VALUE = PARRAY n_new',
        'S_done.ARRAYS[n_new].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_donor))]','S_done.ARRAYS[n_donor].ITEMS = eps',
        '$owned_class_last_write(S_done.CLASSCONSTANTHISTORY,pclassconstantcontext.DECL) = (pclassconstantevent)',
        'pclassconstantevent = CCREPLACE_IMAGE pdefaultcache_old pclassreplacement.IMAGE pclassreplacement.TRIGGER n_prefix pclassreplacement.FACTS',
        '~((HARRAY n_old) <- S_done.ALLOCATIONS)',
        '$class_constant_state_valid(S_done)',
    ]


def prefix(fixture,path,responses):
    early,late=responses
    return start(fixture,path,'Ns210Prefix')+[
        'S_early = $drive_steps(S_warn,30000)','S_early.COMPLETION = SOURCE_PENDING',
        '$default_cache_at(S_early.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_early)',
        'pdefaultcache_early.VALUE = PARRAY n_early','S_early.ARRAYS[n_early].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$eval_response_valid(S_early,'+early+')',
        'S_entered = $eval_resume(S_early,'+early+')','S_entered.COMPLETION = NORMAL',
        'S_late = $drive_steps(S_entered,30000)','S_late.COMPLETION = SOURCE_PENDING',
        '$ic_output(S_late.EVENTS) = $ptascii("H|9|P|9|E|")',
        '$default_cache_at(S_late.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_late)',
        'pdefaultcache_late.VALUE = PARRAY n_late','n_late =/= n_early',
        'S_late.ARRAYS[n_late].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_donor))]','S_late.ARRAYS[n_donor].ITEMS = eps',
        '$class_constant_compile_entry(S_late,1) = (S_projection_early)',
        '$default_cache_at(S_projection_early.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_projection_early)',
        'pdefaultcache_projection_early.VALUE = PARRAY n_projection_early',
        'S_projection_early.ARRAYS[n_projection_early].ITEMS = [ENTRY (KINT 0) (DIRECT (PINT 9))]',
        '$constant_value_class_valid(S_projection_early,pdefaultcache_projection_early.VALUE,pdefaultcache_projection_early.CLASS)',
        '$class_constant_lookup(S_projection_early,porigin_impl,$ptascii("C"),|S_projection_early.CLASSES|) = (pclassconstantdesc)',
        '$eval_response_valid(S_late,'+late+')','S_after = $eval_resume(S_late,'+late+')','S_after.COMPLETION = NORMAL',
    ]+finish(path,'S_after')+[
        '$class_constant_compile_entry(S_done,2) = (S_projection_late)',
        '$default_cache_at(S_projection_late.CLASSCONSTANTCACHE,pclassconstantcontext.DECL) = (pdefaultcache_projection_late)',
        'pdefaultcache_projection_late.VALUE = PARRAY n_projection_late',
        'S_projection_late.ARRAYS[n_projection_late].ITEMS = [ENTRY (KINT 0) (DIRECT (PARRAY n_projection_inner))]',
        'S_projection_late.ARRAYS[n_projection_inner].ITEMS = eps',
        '$constant_value_class_valid(S_projection_late,pdefaultcache_projection_late.VALUE,pdefaultcache_projection_late.CLASS)',
    ]


def prepare(out,group):
    path=SELECTIONS[group]
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    responses=[]
    try:
        parsed=frontend.request({'op':'parse','source':base64.b64encode(path.read_bytes()).decode()});assert parsed['accepted'] and not parsed['diagnostics']
        checked=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True});assert checked['ok']
        if group=='prefix':
            codes=[base64.b64decode(node['fields'][0]['bytes']) for node,_ in nodes(parsed['ast']['program']) if node['node']=='Scalar_String' and base64.b64decode(node['fields'][0]['bytes']).startswith((b'echo "P|";',b'echo "Q|";'))]
            assert len(codes)==2
            for index,code in enumerate(codes,1):
                parsed_eval=frontend.request({'op':'parse-eval','id':str(index),'mode':'eval','profile':'cli-raw-85','source':base64.b64encode(code).decode()});assert parsed_eval['accepted'] and not parsed_eval['diagnostics']
                checked_eval=adapter.request({'op':'check','ast':parsed_eval['ast'],'fixture':True});assert checked_eval['ok']
                responses.append('SOURCE_ACCEPT '+str(index)+' ('+data(code.decode())+') '+checked_eval['fixture'])
                (out/('eval'+str(index)+'.php')).write_bytes(code)
    finally:
        try:adapter.close()
        finally:frontend.close()
    checks=globals()[group](checked['fixture'],path,responses)
    (out/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
    (out/'protocol.watsup').write_text(PREFIX+SELECTED+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+c+'\n' for c in checks))
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--group', required=True, choices=tuple(SELECTIONS))
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SELECTIONS[args.group], SELECTIONS[args.group].parent / 'cases.json', *modules, *(ROOT / path for path in (
        'spec/semantics/modules.json', 'spec/schema.json', 'frontend/worker.php',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py',
        'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'group': args.group, 'inputs': before, 'module_count': len(modules),
        'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out, args.group)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in paths}
        report['passed'] = report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable']
    finally: (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
