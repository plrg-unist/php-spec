#!/usr/bin/env python3
"""Paused goto continuation, task authentication, and owner cleanup checks."""
from pathlib import Path
import base64, hashlib, json, subprocess, sys, tempfile

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
from recorded_worker import Worker
import request_environment as q

PREFIX = '''
dec $goto_paused(pstate) : bool
def $goto_paused(S) = true
  -- if S.TODO = (STMT (NStmtGoto phpType11 metadata)) :: ptask*
def $goto_paused(S) = false -- otherwise
dec $goto_pause(pstate, nat) : pstate
def $goto_pause(S, n) = S -- if $goto_paused(S)
def $goto_pause(S, n) = $goto_pause($drive_steps(S[.COMPLETION = NORMAL], 1), n_next)
  -- if ~$goto_paused(S)
  -- if $(n > 0)
  -- if n_next = $(n - 1)
dec $goto_outputs(pevent*) : nat*
def $goto_outputs(eps) = eps
def $goto_outputs((OUTPUT n*) :: pevent*) = n* ++ $goto_outputs(pevent*)
def $goto_outputs((WARNING n* z) :: pevent*) = $goto_outputs(pevent*)
def $goto_outputs((DIAGNOSTIC text n* z) :: pevent*) = $goto_outputs(pevent*)
dec $forge_foreach(ptask*, statement) : ptask*
def $forge_foreach(eps, statement) = eps
def $forge_foreach((FOREACH_NEXT n pnode statement_old porigin? z) :: ptask_tail*, statement) = (FOREACH_NEXT n pnode statement porigin? z) :: ptask_tail*
def $forge_foreach(ptask :: ptask_tail*, statement) = ptask :: $forge_foreach(ptask_tail*, statement)
  -- if ~$goto_foreach_task(ptask)
dec $saved_foreach(ptask*) : ptask?
def $saved_foreach((FOREACH_NEXT n pnode statement porigin? z) :: ptask*) = (FOREACH_NEXT n pnode statement porigin? z)
def $saved_foreach(ptask :: ptask_tail*) = $saved_foreach(ptask_tail*)
  -- if ~$goto_foreach_task(ptask)
dec $switch_task(ptask) : bool
def $switch_task(SWITCH_NEXT statement porigin poperand) = true
def $switch_task(ptask) = false -- otherwise
dec $saved_switch(ptask*) : ptask?
def $saved_switch(eps) = eps
def $saved_switch((SWITCH_NEXT statement porigin poperand) :: ptask*) = (SWITCH_NEXT statement porigin poperand)
def $saved_switch(ptask :: ptask_tail*) = $saved_switch(ptask_tail*)
  -- if ~$switch_task(ptask)
'''

def fixture_for(path, out):
    frontend = Worker([str(ROOT / '.tools/php/bin/php'), '-n', '-d',
                       'extension=' + str(ROOT / '.tools/php-file.so'),
                       str(ROOT / 'frontend/worker.php')], out / 'frontend')
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
    try:
        parsed = frontend.request({'op':'parse', 'source':base64.b64encode(path.read_bytes()).decode()})
        assert parsed['accepted'], parsed
        checked = adapter.request({'op':'check', 'ast':parsed['ast'], 'fixture':True})
        assert checked['ok'], checked
        return checked['fixture']
    finally:
        frontend.close();adapter.close()


def main():
    fingerprint=q.t.syntax_validation.implementation_fingerprint()
    out = Path(tempfile.mkdtemp(prefix='goto-protocol-', dir=ROOT / '.tools'))
    modules=[str(ROOT/p) for p in json.loads((ROOT/'spec/semantics/modules.json').read_text())]
    sources=json.loads((ROOT/'tests/semantics/goto_cases.json').read_text())
    cases=[('foreach_same','runtime-foreach-same',1,1,b'1x2'),
           ('switch_same','runtime-switch-same',0,0,b'A1'),
           ('foreach_out_nested','runtime-foreach-out-nested',2,0,b'9'),
           ('function_branch','runtime-function-branch',0,0,b'FX'),
           ('nested_scope','runtime-nested-scope',0,0,b'OI'),
           ('switch_tmp_same','runtime-switch-tmp-same',0,0,b'01'),
           ('switch_tmp_out','runtime-switch-tmp-out',0,0,b'S1'),
           ('foreach_owner_auth','runtime-foreach-owner-auth',1,1,b'1'),
           ('goto_task_auth','runtime-goto-task-auth',0,0,b'D')]
    assertions=0
    records=[]
    for name, source_key, before, after, expected in cases:
        caseout=out/name; caseout.mkdir()
        path=caseout/'source.php'; path.write_text(sources[source_key])
        fixture=fixture_for(path,caseout)
        sourcebytes=json.dumps(base64.b64encode(str(path).encode()).decode())
        checks=[f'S_initial = $php_run({fixture}, 0, {sourcebytes})',
                'S_pause = $goto_pause(S_initial[.COMPLETION = NORMAL], 512)',
                'S = S_pause[.COMPLETION = NORMAL]',
                'S.COMPLETION = NORMAL',
                'S.TODO = (STMT (NStmtGoto phpType11 metadata)) :: ptask_tail*',
                'S.ORIGIN = (porigin)',
                '$goto_target(S, porigin) = (pcpath_target)',
                '$goto_site(S, porigin, pcpath_target)',
                '$call_descriptors_valid(S)',
                '$call_tasks_valid(S, S.TODO)',
                '$heap_valid($heap_graph(S))',
                f'|S.ITERATORS| = {before}',
                'S_one = $drive_steps(S, 1)',
                'S_one.COMPLETION = BUDGET',
                'S_one.TODO = (AT (PORIGIN n pcpath_target) (STMT (NStmtLabel phpType11_label metadata_label))) :: ptask_next*',
                f'|S_one.ITERATORS| = {after}',
                '$heap_valid($heap_graph(S_one))',
                'S_one = $drive(S, 1)',
                'S_done = $drive(S_one[.COMPLETION = NORMAL], 1000)',
                'S_done.COMPLETION = NORMAL',
                '$heap_valid($heap_graph(S_done))',
                '$goto_outputs(S_done.EVENTS) = ['+','.join(map(str,expected))+']']
        if name=='function_branch':
            checks += ['S_top = S_initial[.COMPLETION = NORMAL]',
                       'S_top.CURRENT = eps',
                       'S.ORIGIN = (PORIGIN n pcpath_source)',
                       '$origin_node(S.SOURCES, PORIGIN n pcpath_target) = (statement_label)',
                       '$goto_label_valid(S, statement_label, (PORIGIN n pcpath_target))',
                       '~$goto_label_valid(S_top, statement_label, (PORIGIN n pcpath_target))']
        if name=='nested_scope':
            checks += ['S.CURRENT = (pcallcontext)',
                       'porigin_outer = (PORIGIN 0 ([PCINDEX 0, PCFIELD 5, PCINDEX 0]))',
                       '$origin_node(S.SOURCES, porigin_outer) = (statement_outer)',
                       '~$goto_label_valid(S, statement_outer, (porigin_outer))']
        if name=='foreach_same':
            checks += ['S_bad = S[.TODO = (STMT (NStmtGoto phpType11 metadata)) :: $forge_foreach(ptask_tail*, NStmtGoto phpType11 metadata)]',
                       'S_bad_after = $drive_steps(S_bad, 1)',
                       'S_bad_after.COMPLETION = UNSUPPORTED "invalid goto continuation"']
        if name=='foreach_owner_auth':
            checks += ['$saved_foreach(S.TODO) = (FOREACH_NEXT n_foreach (HARRAY n_array) statement_foreach (porigin_foreach) z_foreach)',
                       '$goto_marker_valid(S, FOREACH_NEXT n_foreach (HARRAY n_array) statement_foreach (porigin_foreach) z_foreach)',
                       '$(n_array + 1 < |S.ARRAYS|)',
                       '~$goto_marker_valid(S, FOREACH_NEXT n_foreach (HARRAY $(n_array + 1)) statement_foreach (porigin_foreach) z_foreach)',
                       '~$call_task_valid(S, FOREACH_NEXT n_foreach (HARRAY $(n_array + 1)) statement_foreach (porigin_foreach) z_foreach)',
                       '~$goto_marker_valid(S, FOREACH_NEXT n_foreach (HARRAY n_array) statement_foreach eps z_foreach)',
                       '~$goto_marker_valid(S, FOREACH_NEXT n_foreach (HARRAY n_array) statement_foreach (porigin_foreach) $(z_foreach + 1))',
                       '~$call_task_valid(S, FOREACH_NEXT n_foreach (HARRAY n_array) statement_foreach eps z_foreach)',
                       'S_done.ITERATORS = eps']
        if name=='goto_task_auth':
            checks += ['~$call_tasks_valid(S, (STMT (NStmtGoto (NIdentifier (BYTES "YmFk") metadata) metadata)) :: ptask_tail*)',
                       '~$call_tasks_valid(S[.ORIGIN = eps], S.TODO)']
        if name in ('switch_tmp_same','switch_tmp_out'):
            checks += ['$saved_switch(S.TODO) = (SWITCH_NEXT statement_switch porigin_switch (KNOWN (PARRAY n_array)))',
                       '$(0 < $heap_owners($heap_graph(S), HARRAY n_array))',
                       '$heap_owners($heap_graph(S_done), HARRAY n_array) = 0']
            if name=='switch_tmp_same':
                checks += ['$saved_switch(S_one.TODO) = (SWITCH_NEXT statement_switch porigin_switch (KNOWN (PARRAY n_array)))',
                           '$heap_owners($heap_graph(S_one), HARRAY n_array) = $heap_owners($heap_graph(S), HARRAY n_array)']
            else:
                checks += ['$saved_switch(S_one.TODO) = eps',
                           '$heap_owners($heap_graph(S_one), HARRAY n_array) = 0']
        fixture_text=PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+line+'\n' for line in checks)
        fixture_path=out/(name+'.watsup'); fixture_path.write_text(fixture_text)
        p=subprocess.run([str(ROOT/'tests/semantics/_build/default/numeric_runner.exe'),*modules,str(fixture_path)],capture_output=True,text=True,timeout=120)
        (out/(name+'.stdout')).write_text(p.stdout)
        (out/(name+'.stderr')).write_text(p.stderr)
        (out/(name+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':p.returncode})+'\n')
        print(name,p.returncode,p.stdout.strip(),p.stderr[:1000],flush=True)
        if p.returncode or p.stdout!='true\n' or p.stderr: raise SystemExit(1)
        assertions += len(checks)
        records.append({'case':name,'source_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'assertions':len(checks)})
    assert fingerprint == q.t.syntax_validation.implementation_fingerprint()
    (out/'report.json').write_text(json.dumps({'result':'pass','fingerprint':fingerprint,'cases':len(cases),'assertions':assertions,'records':records},indent=2)+'\n')
    print('PASS',out)
if __name__=='__main__': main()
