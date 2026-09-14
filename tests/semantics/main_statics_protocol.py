#!/usr/bin/env python3
"""Initial-main static source identity, active scope and persistent-cell validity."""
from pathlib import Path
import base64,json,os,subprocess,tempfile
import request_environment as q
import request_environment_state as rs
from recorded_worker import Worker
R=Path(__file__).resolve().parents[2]
SOURCES = {'main-static-initializer-mutates-prior-array-alias': 'PD9waHAKJHg9WzFdOyRvbGQ9JiR4OwpmdW5jdGlvbiBpbml0KCl7Z2xvYmFsICR4OyR4WzBdPTI7cmV0dXJuIFszXTt9CnN0YXRpYyAkeD1pbml0KCk7CmVjaG8gJG9sZFswXSwkeFswXSwkR0xPQkFMU1sieCJdWzBdOyRuYW1lPSJ4IjskeyRuYW1lfVswXT00O2VjaG8gJHhbMF0sJG9sZFswXTs=',
 'main-static-global-call-unset-cache': 'PD9waHAKZnVuY3Rpb24gYnVtcCgpe2dsb2JhbCAkeDskeCsrO30KZm9yKCRpPTA7JGk8MjskaSsrKXtzdGF0aWMgJHg9NDtidW1wKCk7ZWNobyAkeDt1bnNldCgkR0xPQkFMU1sieCJdKTtlY2hvIGlzc2V0KCR4KTt9',
 'main-static-named-return-alias-isolation': 'PD9waHAKc3RhdGljICR4PTE7CmZ1bmN0aW9uICZmKCl7c3RhdGljICR4PTc7cmV0dXJuICR4O30KJHk9JmYoKTtmdW5jdGlvbiBidW1wKCl7Z2xvYmFsICR4OyR4Kys7fQpidW1wKCk7JHkrKztlY2hvICR4LCR5LGYoKSwkR0xPQkFMU1sieCJdOw==',
 'main-static-array-owner-suppressed-typed-error': 'PD9waHAKc3RhdGljICRhPVsxXTskYWxpYXM9JiRhO2VjaG8gJGFbMF07CmZ1bmN0aW9uIGcoaW50ICR4KXtyZXR1cm4gJHg7fQpzdGF0aWMgJGI9CiBAZyhbXSk7',
 'main-static-stored-global-alias': 'PD9waHAgJHg9NDskYT0mJHg7c3RhdGljICR4PTc7ZWNobyAkeCwkYSwkR0xPQkFMU1sieCJdOysrJHg7ZWNobyAkYSwkR0xPQkFMU1sieCJdOw=='}
PREFIX = 'dec $review_stage(pstate, bool) : bool\ndef $review_stage(S, false) = true -- if S.CURRENT = eps -- if S.TODO = (STATIC_INIT porigin) :: ptask_tail*\ndef $review_stage(S, true) = true -- if S.CURRENT =/= eps -- if S.STATICS =/= eps\ndef $review_stage(S, b) = false -- otherwise\ndec $review_find(pstate, nat, bool) : pstate\ndef $review_find(S, n, b) = S -- if $review_stage(S, b)\ndef $review_find(S, n, b) = $review_find(S_next[.COMPLETION = NORMAL], n_rest, b)\n  -- if ~$review_stage(S, b)\n  -- if $(n > 0)\n  -- if n_rest = $(n - 1)\n  -- if S_next = $drive_steps(S, 1)\ndec $review_forge_entry(pcodeexpr) : pcodeexpr\ndef $review_forge_entry(CODESTATIC pcpath ptbytes z_begin z_bind b) = CODESTATIC pcpath ($ptascii("forged")) z_begin z_bind b\ndef $review_forge_entry(pcodeexpr) = pcodeexpr -- otherwise\ndec $review_forge(pcodeexpr*) : pcodeexpr*\ndef $review_forge(eps) = eps\ndef $review_forge(pcodeexpr :: pcodeexpr_tail*) = $review_forge_entry(pcodeexpr) :: $review_forge(pcodeexpr_tail*)\n'
CASES = [{'id': 'main-initializer-control',
  'source': 'main-static-named-return-alias-isolation',
  'valid': True,
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400, false)',
             'S.TODO = (STATIC_INIT porigin_main) :: ptask_tail*',
             'S.STATICS = eps',
             '$main_static_origin(S, porigin_main)',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'pfunction = S.FUNCTIONS[0]',
             '$static_code_entries(pfunction.CODE.EXPRESSIONS) = [(CODESTATIC '
             'pcpath_named ptbytes z_begin z_bind true)]',
             'porigin_named = PORIGIN pfunction.CODE.UNIT pcpath_named',
             '~$main_static_origin(S, porigin_named)',
             'S_post = $drive_steps(S, 1)',
             'S_post.STATICS = [pstaticcell]',
             'n_cell = pstaticcell.CELL',
             'S_post.STORE[n_cell] = DEFINED (PINT 1)',
             'S_changed = S',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': 'c49ce2ac227f5e9d3a729e09264cc7c7f972026c7f09d89172707216f2c58595'},
 {'id': 'nested-function-task-in-main',
  'source': 'main-static-named-return-alias-isolation',
  'valid': False,
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400, false)',
             'S.TODO = (STATIC_INIT porigin_main) :: ptask_tail*',
             'S.STATICS = eps',
             '$main_static_origin(S, porigin_main)',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'pfunction = S.FUNCTIONS[0]',
             '$static_code_entries(pfunction.CODE.EXPRESSIONS) = [(CODESTATIC '
             'pcpath_named ptbytes z_begin z_bind true)]',
             'porigin_named = PORIGIN pfunction.CODE.UNIT pcpath_named',
             '~$main_static_origin(S, porigin_named)',
             'S_post = $drive_steps(S, 1)',
             'S_post.STATICS = [pstaticcell]',
             'n_cell = pstaticcell.CELL',
             'S_post.STORE[n_cell] = DEFINED (PINT 1)',
             'S_changed = S[.ORIGIN = (porigin_named)][.TODO = (STATIC_INIT '
             'porigin_named) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '~$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function '
             'descriptor"'],
  'original_fixture_sha256': '4075a8da4b73b4fa70060cbc08291bb6949be535285fbd51910eb1c927fa0956'},
 {'id': 'persistent-entry-named-reassociation',
  'source': 'main-static-named-return-alias-isolation',
  'valid': True,
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400, false)',
             'S.TODO = (STATIC_INIT porigin_main) :: ptask_tail*',
             'S.STATICS = eps',
             '$main_static_origin(S, porigin_main)',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'pfunction = S.FUNCTIONS[0]',
             '$static_code_entries(pfunction.CODE.EXPRESSIONS) = [(CODESTATIC '
             'pcpath_named ptbytes z_begin z_bind true)]',
             'porigin_named = PORIGIN pfunction.CODE.UNIT pcpath_named',
             '~$main_static_origin(S, porigin_named)',
             'S_post = $drive_steps(S, 1)',
             'S_post.STATICS = [pstaticcell]',
             'n_cell = pstaticcell.CELL',
             'S_post.STORE[n_cell] = DEFINED (PINT 1)',
             'S_changed = S_post[.COMPLETION = NORMAL][.STATICS = '
             '[pstaticcell[.ORIGIN = porigin_named]]]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': 'e786143731e1992d2f665e11a439e3b8db984f3c2f8adbd8de83e52ff8753b7d'},
 {'id': 'arbitrary-main-cell-value',
  'source': 'main-static-named-return-alias-isolation',
  'valid': True,
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400, false)',
             'S.TODO = (STATIC_INIT porigin_main) :: ptask_tail*',
             'S.STATICS = eps',
             '$main_static_origin(S, porigin_main)',
             '$call_descriptors_valid(S)',
             '$heap_valid($heap_graph(S))',
             'pfunction = S.FUNCTIONS[0]',
             '$static_code_entries(pfunction.CODE.EXPRESSIONS) = [(CODESTATIC '
             'pcpath_named ptbytes z_begin z_bind true)]',
             'porigin_named = PORIGIN pfunction.CODE.UNIT pcpath_named',
             '~$main_static_origin(S, porigin_named)',
             'S_post = $drive_steps(S, 1)',
             'S_post.STATICS = [pstaticcell]',
             'n_cell = pstaticcell.CELL',
             'S_post.STORE[n_cell] = DEFINED (PINT 1)',
             'S_changed = S_post[.COMPLETION = NORMAL][.STORE = '
             '$set_cell(S_post.STORE, n_cell, DEFINED (PINT 99))]',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': '1cbf51a2389d4057f923c8ea7f50cb220bb7fda471d86814e03e887299e87fbf'},
 {'id': 'pure-main-forged-marker',
  'source': 'main-static-stored-global-alias',
  'valid': False,
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400, false)',
             '$call_descriptors_valid(S)',
             'S.FUNCTIONS = eps',
             'S.CODE = [pcode]',
             'S_changed = S[.CODE = [pcode[.EXPRESSIONS = '
             '$review_forge(pcode.EXPRESSIONS)]]]',
             '$heap_valid($heap_graph(S_changed))',
             '~$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function '
             'descriptor"'],
  'original_fixture_sha256': '41133a4691814ce87eb05f54f1781a6c9b324796571ce87b5c9b14f09d305fb4'},
 {'id': 'main-owner-and-saved-task-during-callee',
  'source': 'main-static-array-owner-suppressed-typed-error',
  'valid': True,
  'checks': ['S_initial = __INITIAL__',
             'S_changed = $review_find(S_initial[.COMPLETION = NORMAL], 400, '
             'true)',
             'S_changed.CURRENT =/= eps',
             'S_changed.GLOBALTABLE =/= eps',
             'S_changed.STATICS = [pstaticcell]',
             '$main_static_origin(S_changed, pstaticcell.ORIGIN)',
             '$call_frames_valid(S_changed, S_changed.FRAMES)',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed, 0)',
             'S_zero.COMPLETION = BUDGET'],
  'original_fixture_sha256': '50b5c0618b743b3afd8d662f6dcda17f4912787dbf014f1d79ede3b1dce32725'},
 {'id': 'additional-unit-source-context',
  'source': 'main-static-stored-global-alias',
  'valid': True,
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400, false)',
             '$call_descriptors_valid(S)',
             'S.FUNCTIONS = eps',
             'S.CODE = [pcode]',
             'S.TODO = (STATIC_INIT (PORIGIN 0 pcpath_static)) :: ptask_tail*',
             'pcunit_main = S.SOURCES[0]',
             'S_added = $compile_source(S[.FILES = S.FILES ++ [SOURCEFILE 1 '
             '([117,110,105,116,49])]], $ppstart_cwd(1, pcunit_main.AST, '
             '[117,110,105,116,49], $call_request_cwd(S.REQUEST)))',
             'S_added.COMPLETION = NORMAL',
             'S_extra = S_added[.TODO = S.TODO][.ORIGIN = S.ORIGIN]',
             '|S_extra.SOURCES| = 2',
             '|S_extra.CODE| = 2',
             '$call_projection(S_extra, S_extra.SOURCES) = FUNCTIONCHECK eps',
             '$scope_codes_valid(S_extra, S_extra.CODE)',
             '$call_descriptors_valid(S_extra)',
             '$static_descriptor(S_extra, PORIGIN 1 pcpath_static) =/= eps',
             '~$main_static_origin(S_extra, PORIGIN 1 pcpath_static)',
             'S_bound = $drive_steps(S_extra, 1)',
             'S_bound.STATICS = [pstaticcell]',
             'S_changed = S_extra',
             '$heap_valid($heap_graph(S_changed))',
             '$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed[.COMPLETION = NORMAL], 0)',
             'S_zero.COMPLETION = BUDGET']},
 {'id': 'additional-unit-persistent-origin',
  'source': 'main-static-stored-global-alias',
  'valid': False,
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400, false)',
             '$call_descriptors_valid(S)',
             'S.FUNCTIONS = eps',
             'S.CODE = [pcode]',
             'S.TODO = (STATIC_INIT (PORIGIN 0 pcpath_static)) :: ptask_tail*',
             'pcunit_main = S.SOURCES[0]',
             'S_added = $compile_source(S[.FILES = S.FILES ++ [SOURCEFILE 1 '
             '([117,110,105,116,49])]], $ppstart_cwd(1, pcunit_main.AST, '
             '[117,110,105,116,49], $call_request_cwd(S.REQUEST)))',
             'S_added.COMPLETION = NORMAL',
             'S_extra = S_added[.TODO = S.TODO][.ORIGIN = S.ORIGIN]',
             '|S_extra.SOURCES| = 2',
             '|S_extra.CODE| = 2',
             '$call_projection(S_extra, S_extra.SOURCES) = FUNCTIONCHECK eps',
             '$scope_codes_valid(S_extra, S_extra.CODE)',
             '$call_descriptors_valid(S_extra)',
             '$static_descriptor(S_extra, PORIGIN 1 pcpath_static) =/= eps',
             '~$main_static_origin(S_extra, PORIGIN 1 pcpath_static)',
             'S_bound = $drive_steps(S_extra, 1)',
             'S_bound.STATICS = [pstaticcell]',
             'S_changed = S_bound[.COMPLETION = NORMAL][.STATICS = '
             '[pstaticcell[.ORIGIN = PORIGIN 1 pcpath_static]]]',
             '$heap_valid($heap_graph(S_changed))',
             '~$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed[.COMPLETION = NORMAL], 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function '
             'descriptor"']},
 {'id': 'additional-unit-current-task',
  'source': 'main-static-stored-global-alias',
  'valid': False,
  'checks': ['S_initial = __INITIAL__',
             'S = $review_find(S_initial[.COMPLETION = NORMAL], 400, false)',
             '$call_descriptors_valid(S)',
             'S.FUNCTIONS = eps',
             'S.CODE = [pcode]',
             'S.TODO = (STATIC_INIT (PORIGIN 0 pcpath_static)) :: ptask_tail*',
             'pcunit_main = S.SOURCES[0]',
             'S_added = $compile_source(S[.FILES = S.FILES ++ [SOURCEFILE 1 '
             '([117,110,105,116,49])]], $ppstart_cwd(1, pcunit_main.AST, '
             '[117,110,105,116,49], $call_request_cwd(S.REQUEST)))',
             'S_added.COMPLETION = NORMAL',
             'S_extra = S_added[.TODO = S.TODO][.ORIGIN = S.ORIGIN]',
             '|S_extra.SOURCES| = 2',
             '|S_extra.CODE| = 2',
             '$call_projection(S_extra, S_extra.SOURCES) = FUNCTIONCHECK eps',
             '$scope_codes_valid(S_extra, S_extra.CODE)',
             '$call_descriptors_valid(S_extra)',
             '$static_descriptor(S_extra, PORIGIN 1 pcpath_static) =/= eps',
             '~$main_static_origin(S_extra, PORIGIN 1 pcpath_static)',
             'S_bound = $drive_steps(S_extra, 1)',
             'S_bound.STATICS = [pstaticcell]',
             'S_changed = S_extra[.ORIGIN = (PORIGIN 1 pcpath_static)][.TODO = '
             '(STATIC_INIT (PORIGIN 1 pcpath_static)) :: ptask_tail*]',
             '$heap_valid($heap_graph(S_changed))',
             '~$call_descriptors_valid(S_changed)',
             'S_zero = $drive(S_changed[.COMPLETION = NORMAL], 0)',
             'S_zero.COMPLETION = UNSUPPORTED "invalid compiled function '
             'descriptor"']}]
D=Path(tempfile.mkdtemp(prefix='main-statics-protocol-',dir=R/'.tools'))
(D/'producer.py').write_bytes(Path(__file__).read_bytes())
before=q.t.syntax_validation.implementation_fingerprint()
(D/'inputs.json').write_text(json.dumps({'fingerprint':before},indent=2));print(D,flush=True)
modules=[R/p for p in json.loads((R/'spec/semantics/modules.json').read_text())]
runner=R/'tests/semantics/_build/default/numeric_runner.exe'
f=a=None;initials={};originals=[];records=[]
try:
 f=Worker([str(q.t.PHP),'-n',*q.t.FLAGS,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],D/'frontend-wire')
 a=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],D/'adapter-wire')
 for name,source64 in SOURCES.items():
  directory=D/name;directory.mkdir();path=directory/'source.php';path.write_bytes(base64.b64decode(source64))
  payload=directory/'request.input';payload.write_bytes(q.packet(1700000000,125000,[b'LC_ALL=C',b'TZ=UTC',b'FIRST=one']))
  request={'env':[[q.b64(k),q.b64(v)] for k,v in [(b'LC_ALL',b'C'),(b'TZ',b'UTC'),(b'FIRST',b'one')]],'argv':[q.b64(os.fsencode(path))],'file':q.b64(os.fsencode(path)),'seconds':'1700000000','microseconds':125000,'variables':q.b64(b'EGPCS'),'jit':True,'cwd':q.b64(os.fsencode(directory))}
  parsed=f.request({'op':'parse','source':source64});assert parsed['accepted']
  checked=a.request({'op':'check','ast':parsed['ast'],'fixture':True});(directory/'checked.json').write_text(json.dumps(checked))
  originals.append({'id':name,'source_base64':source64,'context':str(path),'request':request});(D/'originals.json').write_text(json.dumps(originals,indent=2))
  initials[name]='$php_request_run('+checked['fixture']+', 0, '+json.dumps(q.b64(os.fsencode(path)))+', '+rs.request_fixture(request)+')'
finally:
 try:
  if f:f.close()
 finally:
  if a:a.close()
for case in CASES:
 checks=[s.replace('__INITIAL__',initials[case['source']]) for s in case['checks']]
 fixture=D/(case['id']+'.watsup');fixture.write_text(PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+s+'\n' for s in checks))
 command=[str(runner),*map(str,modules),str(fixture)];(D/(case['id']+'.command.json')).write_text(json.dumps(command))
 try:
  z=subprocess.run(command,capture_output=True,timeout=120)
 except subprocess.TimeoutExpired as e:
  (D/(case['id']+'.stdout')).write_bytes(e.stdout or b'');(D/(case['id']+'.stderr')).write_bytes(e.stderr or b'');(D/(case['id']+'.status.json')).write_text(json.dumps({'status':'timeout','seconds':120}));raise
 (D/(case['id']+'.stdout')).write_bytes(z.stdout);(D/(case['id']+'.stderr')).write_bytes(z.stderr);(D/(case['id']+'.status.json')).write_text(json.dumps({'status':'exit','exit_status':z.returncode}))
 record={'id':case['id'],'source':case['source'],'valid':case['valid'],'assertions':len(checks),'pass':z.returncode==0 and z.stdout.strip()==b'true' and not z.stderr};records.append(record);(D/'results.json').write_text(json.dumps(records,indent=2));print(record,flush=True)
assert before==q.t.syntax_validation.implementation_fingerprint()
report={'result':'pass' if all(r['pass'] for r in records) else 'fail','scope':'Nine initial-main source/stage/persistent-cell controls: four invalid states reject, five finite valid source/value/context controls accept. Additional-unit controls first establish independent source projection and heap validity. No native execution or include lifetime claim','fingerprint':before,'raw':str(D),'sources':len(originals),'cases':len(records),'assertions':sum(r['assertions'] for r in records),'records':records}
(D/'report.json').write_text(json.dumps(report,indent=2));target=R/'coverage/semantics/main-statics-protocol.json';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2));assert report['result']=='pass'
