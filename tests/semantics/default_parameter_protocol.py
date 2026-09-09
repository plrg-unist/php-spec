"""Public source-bound default cache, receive, binding and descriptor guards."""
from pathlib import Path
import json
import subprocess
import tempfile
import default_parameters
import function_scope as scope
import request_environment_state as rs
from recorded_worker import Worker
q = scope.q
R = Path(__file__).resolve().parents[2]
CACHE_PREFIX = r'''
dec $cache_pause(pstate, nat) : pstate
def $cache_pause(S, n) = S
  -- if S.DEFAULTCACHE =/= eps
  -- if S.CURRENT = eps
def $cache_pause(S, n) = $cache_pause($drive_steps(S, 1)[.COMPLETION = NORMAL], $nabs($(n - 1)))
  -- if $(n > 0)
  -- if S.DEFAULTCACHE = eps \/ S.CURRENT =/= eps
'''
TASK_PREFIX = r'''
dec $default_task_cut(pstate, bool) : bool
def $default_task_cut(S, false) = true
  -- if S.TODO = (DEFAULT_RECEIVE porigin n) :: ptask*
  -- if ptask* = eps
def $default_task_cut(S, true) = true
  -- if S.TODO = (DEFAULT_BIND porigin n) :: ptask*
  -- if ptask* = eps
def $default_task_cut(S, b) = false -- otherwise
dec $default_task_find(pstate, bool, nat) : pstate
def $default_task_find(S, b, n) = S
  -- if $default_task_cut(S, b)
def $default_task_find(S, b, n) = $default_task_find($drive_steps(S, 1)[.COMPLETION = NORMAL], b, $nabs($(n - 1)))
  -- if ~$default_task_cut(S, b)
  -- if $(n > 0)
'''
CACHE_VARIANTS = {
    'control': ('S', False),
    'arbitrary-integer': ('S[.DEFAULTCACHE = [pdefaultcache[.VALUE = PINT 99]]]', False),
    'arbitrary-null': ('S[.DEFAULTCACHE = [pdefaultcache[.VALUE = PNULL]]]', False),
    'arbitrary-empty-static-string': ('S[.DEFAULTCACHE = [pdefaultcache[.VALUE = PSTRING eps][.CLASS = PVSTRING true]]]', False),
    'arbitrary-byte-static-string': ('S[.DEFAULTCACHE = [pdefaultcache[.VALUE = PSTRING ([0,255,65])][.CLASS = PVSTRING true]]]', False),
    'arbitrary-shared-empty-array': ('S_empty[.DEFAULTCACHE = [pdefaultcache[.VALUE = PARRAY n_empty][.CLASS = PVARRAY true eps]]]', False),
    'wrong-origin': ('S[.DEFAULTCACHE = [pdefaultcache[.ORIGIN = PORIGIN 0 eps]]]', True),
    'duplicate-origin': ('S[.DEFAULTCACHE = [pdefaultcache,pdefaultcache]]', True),
    'wrong-class-tag': ('S[.DEFAULTCACHE = [pdefaultcache[.CLASS = PVSTRING true]]]', True),
    'allocated-empty-string': ('S[.DEFAULTCACHE = [pdefaultcache[.VALUE = PSTRING eps][.CLASS = PVSTRING false]]]', True),
    'allocated-empty-array': ('S_empty[.DEFAULTCACHE = [pdefaultcache[.VALUE = PARRAY n_empty][.CLASS = PVARRAY false eps]]]', True),
    'nonempty-shared-array': ('S_array[.DEFAULTCACHE = [pdefaultcache[.VALUE = PARRAY n_array][.CLASS = PVARRAY true ([(KINT 0,PVSCALAR)])]]]', True),
}

def main():
    before = q.t.syntax_validation.implementation_fingerprint()
    raw = Path(tempfile.mkdtemp(prefix='default-parameter-protocol-', dir=R / '.tools'))
    mods = [R / p for p in json.loads((R / 'spec/semantics/modules.json').read_text())]
    runner = R / 'tests/semantics/_build/default/numeric_runner.exe'
    frontend = Worker([str(q.t.PHP), '-n', *q.t.FLAGS, '-d', 'extension=' + str(R / '.tools/php-file.so'), str(R / 'frontend/worker.php')], raw / 'frontend-wire')
    adapter = Worker([str(R / '_build/default/adapter/main.exe'), str(R)], raw / 'adapter-wire')
    records = []
    try:
        for source_id in ['const-default-fallback-scalar-cache', 'numeric-warning-repeated', 'literal-omitted', 'ignored-required-default']:
            directory = raw / source_id; directory.mkdir()
            source = default_parameters.CASES[source_id]
            path = directory / 'source.php'; path.write_bytes(source)
            payload = directory / 'request.input'; payload.write_bytes(q.packet(1700000000, 125000, [b'LC_ALL=C', b'TZ=UTC', b'FIRST=one']))
            request = {'env': [[q.b64(k), q.b64(v)] for k,v in [(b'LC_ALL',b'C'),(b'TZ',b'UTC'),(b'FIRST',b'one')]], 'argv': [q.b64(bytes(path))], 'file': q.b64(bytes(path)), 'seconds':'1700000000', 'microseconds':125000, 'variables':q.b64(b'EGPCS'), 'jit':True, 'cwd':q.b64(bytes(directory))}
            native = scope.native(path, payload, directory)
            parsed = frontend.request({'op':'parse','source':q.b64(source)})
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})
            result = adapter.request({'op':'execute','ast':parsed['ast'],'steps':10000,'filename':q.b64(bytes(path)),'request':request})
            actual = q.cli.observe(result['state'],str(path))
            assert actual['status'] in ('normal','php_error') and all(actual[k]==native[k] for k in ('stdout','stderr','exit_status'))
            (directory/'source.json').write_text(json.dumps({'source_base64':q.b64(source),'request':request,'native':native,'actual':actual},indent=2))
            (directory/'checked.json').write_text(json.dumps(checked)); (directory/'state.json').write_text(json.dumps(result))
            initial = '$php_request_run(' + checked['fixture'] + ', 0, ' + json.dumps(q.b64(bytes(path))) + ', ' + rs.request_fixture(request) + ')'
            groups = []
            if source_id == 'const-default-fallback-scalar-cache':
                setup = ['S_initial = '+initial, 'S = $cache_pause(S_initial[.COMPLETION = NORMAL], 200)', 'S.DEFAULTCACHE = [pdefaultcache]', 'S_empty = $allocate_array(S, $array_empty())', 'S_empty.RESULT = KNOWN (PARRAY n_empty)', 'S_array = $allocate_array(S, $array_insert($array_empty(), KINT 0, DIRECT (PINT 7)))', 'S_array.RESULT = KNOWN (PARRAY n_array)']
                groups.append(('cache',CACHE_PREFIX,setup,[(n,t,b,0) for n,(t,b) in CACHE_VARIANTS.items()]))
            elif source_id == 'numeric-warning-repeated':
                for stage,flag,task in [('receive','false','DEFAULT_RECEIVE'),('bind','true','DEFAULT_BIND')]:
                    setup = ['S_initial = '+initial, 'S = $default_task_find(S_initial[.COMPLETION = NORMAL], '+flag+', 200)', 'S.TODO = ('+task+' porigin n) :: ptask_tail*', 'ptask_tail* = eps', 'S.CURRENT = (pcallcontext)', '$function_at(S.FUNCTIONS, porigin) = (pfunction)']
                    vs = [('control','S',False,0), ('control-full','S',False,1000), ('trailing-zero','S[.TODO = S.TODO ++ [DISCARD]]',True,0), ('trailing-full','S[.TODO = S.TODO ++ [DISCARD]]',True,1000), ('index-outside','S[.TODO = ['+task+' porigin 99]]',True,0), ('foreign-callee','S[.TODO = ['+task+' (PORIGIN 0 eps) n]]',True,0), ('supplied-index','S[.CURRENT = (pcallcontext[.ARGC = 1])]',True,0), ('altered-descriptor','S[.FUNCTIONS = [pfunction[.DEFAULTS = eps]]]',True,0)]
                    if stage == 'bind': vs += [('without-context','S[.CONSTCONTEXT = eps]',True,0)]
                    groups.append((stage,TASK_PREFIX,setup,vs))
            else:
                setup = ['S_initial = '+initial, 'S = $drive(S_initial[.COMPLETION = NORMAL], 1000)', 'S.FUNCTIONS = [pfunction]', '$default_parameter_origin(pfunction.ORIGIN, 0) = PORIGIN n_unit pcpath', 'porigin = PORIGIN n_unit (pcpath ++ [PCFIELD 6])']
                groups.append(('cache-kind','',setup,[('control','S',False,0),('stored-or-dropped-origin','S[.DEFAULTCACHE = [{ORIGIN porigin, VALUE PINT 99, CLASS PVSCALAR}]]',True,0)]))
            for group,prefix,setup,vs in groups:
                for name,term,invalid,budget in vs:
                    out=directory/(group+'-'+name);out.mkdir();fixture=out/'case.watsup'
                    fixture.write_text(prefix+'\ndec $main() : pstate\ndef $main() = $drive('+term+'[.COMPLETION = NORMAL], '+str(budget)+')\n'+''.join('  -- if '+x+'\n' for x in setup))
                    cmd=[str(runner),*map(str,mods),str(fixture)];(out/'command.json').write_text(json.dumps(cmd))
                    p=subprocess.run(cmd,capture_output=True,timeout=60)
                    (out/'stdout').write_bytes(p.stdout);(out/'stderr').write_bytes(p.stderr);(out/'status.json').write_text(json.dumps({'exit_status':p.returncode}))
                    expected='UNSUPPORTED' if invalid else ('NORMAL' if budget or group == 'cache-kind' else 'BUDGET')
                    ok=p.returncode==0 and not p.stderr and ('COMPLETION '+expected) in p.stdout.decode()
                    row={'source':source_id,'id':group+'-'+name,'expected':expected,'pass':ok};records.append(row)
                    (raw/'results.json').write_text(json.dumps(records,indent=2));print(row,flush=True)
                    assert ok, (p.stderr[-1000:],p.stdout[-1000:])
    finally:
        try: frontend.close()
        finally: adapter.close()
    assert before == q.t.syntax_validation.implementation_fingerprint()
    report={'result':'pass','fingerprint':before,'records':records,'raw':str(raw)}
    (raw/'report.json').write_text(json.dumps(report,indent=2));(R/'coverage/semantics/default-parameter-protocol.json').write_text(json.dumps(report,indent=2));print(raw,flush=True)
    return True
if __name__ == '__main__': raise SystemExit(0 if main() else 1)
