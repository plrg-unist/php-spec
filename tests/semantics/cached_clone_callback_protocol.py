"""Check cached clone callback tables, borrowed sources, references and throw cleanup."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = r'''
syntax pckstage = CK_CLONE | CK_FOREACH | CK_RETURN | CK_RESULT | CK_THROW | CK_DISCARD | CK_DTOR nat | CK_CATCH | CK_OUTPUT ptbytes
dec $ck_output(pevent*) : ptbytes
def $ck_output(eps) = eps
def $ck_output((OUTPUT ptbytes) :: pevent_tail*) = ptbytes ++ $ck_output(pevent_tail*)
dec $ck_stage(pstate,pckstage) : bool
def $ck_stage(S,CK_CLONE) = true
  -- if S.TODO = (CLONE_RESULT porigin z) :: ptask_tail*
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ck_stage(S,CK_FOREACH) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_copy porigin_method
  -- if $clone_method(S,n_copy) = (pmethoddesc)
  -- if pmethoddesc.FUNCTION.ORIGIN = porigin_method
  -- if S.TODO = (FOREACH_NEXT n_iterator (HOBJECT n_copy) statement porigin? z) :: ptask_tail*
  -- if $iterator_lookup(S.ITERATORS,n_iterator) = (OBJECTITER n_iterator n_copy 0 false)
def $ck_stage(S,CK_RETURN) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_copy porigin_method
  -- if $clone_method(S,n_copy) = (pmethoddesc)
  -- if pmethoddesc.FUNCTION.ORIGIN = porigin_method
  -- if S.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin?) :: ptask_tail*
def $ck_stage(S,CK_THROW) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = METHOD_TARGET n_copy porigin_method
  -- if $clone_method(S,n_copy) = (pmethoddesc)
  -- if pmethoddesc.FUNCTION.ORIGIN = porigin_method
  -- if S.TODO = (THROW_VALUE porigin z) :: ptask_tail*
def $ck_stage(S,CK_RESULT) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_tail*
def $ck_stage(S,CK_DISCARD) = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if S.TODO = (THROW_SEARCH n_error) :: (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_tail*
def $ck_stage(S,CK_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ck_stage(S,CK_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $ck_stage(S,CK_OUTPUT ptbytes) = ($ck_output(S.EVENTS) = ptbytes)
  -- if S.CURRENT = eps /\ S.FRAMES = eps
def $ck_stage(S,pckstage) = false -- otherwise
dec $ck_seek(pstate,pckstage,nat) : pstate
def $ck_seek(S,pckstage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ck_stage(S,pckstage) \/ n = 0
def $ck_seek(S,pckstage,n) = $ck_seek($drive_steps(S[.COMPLETION = NORMAL],1),pckstage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ck_stage(S,pckstage) /\ $(n > 0)
def $ck_seek(S,pckstage,n) = $ck_seek($drive_steps(S,1),pckstage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ck_seek(S,pckstage,n) = S -- otherwise
dec $ck_after(pstate,pstate) : pstate
def $ck_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ck_guard(pstate) : bool
def $ck_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $object_tables_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

def lines(text): return [line for line in text.strip().splitlines() if line]
def reach(name, previous, stage):
    return [f'{name}_found = $ck_seek({previous},{stage},2000)',
            fr'{name}_found.COMPLETION = NORMAL \/ {name}_found.COMPLETION = BUDGET',
            f'{name} = {name}_found[.COMPLETION = NORMAL]', f'$ck_stage({name},{stage})']

FRONT = lines(r'''
S_front.TODO = (CLONE_RESULT porigin_clone z_clone) :: ptask_tail*
S_front.ORIGIN = (porigin_clone)
S_front.RESULT = VARIABLE ptbytes_source z_source
ptbytes_source = $ptascii("source")
$clone_task_valid(S_front,porigin_clone,z_clone)
$lookup(S_front.ENV,ptbytes_source) = (n_source_cell)
S_front.STORE[n_source_cell] = DEFINED (POBJECT n_source)
$clone_cached_ready(S_front,n_source) /\ $clone_callback_value(S_front,POBJECT n_source)
~$clone_readonly_updates(S_front,n_source) /\ S_front.GC.ACTIVE = eps
$clone_method(S_front,n_source) = (pmethoddesc_clone)
pmethoddesc_clone.FUNCTION = pfunction_clone
~pmethoddesc_clone.STATIC /\ pmethoddesc_clone.VISIBILITY = PROPERTY_PUBLIC
pfunction_clone.SIGNATURE.PARAMETERS = eps /\ ~pfunction_clone.SIGNATURE.BYREF
$objectprops_record_at(S_front.OBJECTPROPS,n_source) = (pobjectprops_source)
pobjectprops_source.MATERIALIZED
$object_table_at(S_front.OBJECTTABLES,n_source) = (n_table_source)
$node_children(S_front,HARRAY n_table_source) = eps
$heap_owners($heap_graph(S_front),HOBJECT n_source) = 1
$heap_owners($heap_graph(S_front),HARRAY n_table_source) = 1
$ck_output(S_front.EVENTS) = ptbytes_prefix
$ck_guard(S_front)
PhpStep: S_front ~> S_copy_raw
S_copy = $ck_after(S_front,S_copy_raw)
S_copy.TODO = (CLONE_CALLBACK_ENTER pcloneoperation) :: ptask_tail*
pcloneoperation.SITE = porigin_clone /\ pcloneoperation.LINE = z_clone /\ pcloneoperation.SOURCE = n_source
n_copy = pcloneoperation.TARGET
n_copy = |S_front.OBJECTS|
pcloneoperation.INPUT = (VARIABLE ptbytes_source z_source) /\ pcloneoperation.CALL = eps /\ pcloneoperation.SCOPE = eps
$clone_input_nodes(pcloneoperation.INPUT) = eps
$task_nodes(CLONE_CALLBACK_ENTER pcloneoperation) = [HOBJECT n_copy]
S_copy.CLONES = [pclonewindow]
pclonewindow.OPERATION = pcloneoperation /\ pclonewindow.PHASE = CLONE_CALLBACK /\ pclonewindow.AVAILABLE = eps /\ pclonewindow.REVISIONS = eps
$clone_callback_live(S_copy,pcloneoperation)
S_copy.RESULT = KNOWN PNULL /\ S_copy.BASE = BASE_VALUE (KNOWN PNULL)
$object_table_at(S_copy.OBJECTTABLES,n_copy) = (n_table_copy)
n_table_copy = |S_front.ARRAYS|
n_table_copy =/= n_table_source
S_copy.ARRAYS[n_table_source] = S_front.ARRAYS[n_table_source]
$objectprops_record_at(S_copy.OBJECTPROPS,n_source) = (pobjectprops_source)
$objectprops_record_at(S_copy.OBJECTPROPS,n_copy) = (pobjectprops_copy)
pobjectprops_copy.MATERIALIZED
$node_children(S_copy,HARRAY n_table_copy) = eps
$heap_owners($heap_graph(S_copy),HOBJECT n_source) = 1 /\ $heap_owners($heap_graph(S_copy),HOBJECT n_copy) = 1
$heap_owners($heap_graph(S_copy),HARRAY n_table_source) = 1 /\ $heap_owners($heap_graph(S_copy),HARRAY n_table_copy) = 1
S_copy.ALLOCATIONS = S_front.ALLOCATIONS ++ [HOBJECT n_copy,HARRAY n_table_copy]
$ck_guard(S_copy)
''')
ENTER = lines(r'''
PhpStep: S_copy ~> S_enter_raw
S_enter = $ck_after(S_copy,S_enter_raw)
S_enter.CURRENT = (pcallcontext_clone)
pcallcontext_clone.TARGET = METHOD_TARGET n_copy pfunction_clone.ORIGIN
pcallcontext_clone.RECEIVER = (n_copy) /\ pcallcontext_clone.LEXICAL_CLASS = (pmethoddesc_clone.OWNER) /\ pcallcontext_clone.CALLED_CLASS = (pmethoddesc_clone.OWNER)
S_enter.FRAMES = [pframe_clone]
pframe_clone.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_tail*
$clone_maker_at(S_enter.CLONEMAKERS,n_copy) = ($clone_producer_receipt(pcloneoperation))
$clone_context_valid(S_enter,pcallcontext_clone)
$heap_owners($heap_graph(S_enter),HOBJECT n_source) = 1 /\ $heap_owners($heap_graph(S_enter),HOBJECT n_copy) = 2
$ck_guard(S_enter)
''')
ITERATE = lines(r'''
S_iter.CURRENT = (pcallcontext_clone)
S_iter.TODO = (FOREACH_NEXT n_iterator (HOBJECT n_copy) statement_foreach porigin_foreach? z_foreach) :: ptask_foreach_tail*
$iterator_lookup(S_iter.ITERATORS,n_iterator) = (OBJECTITER n_iterator n_copy 0 false)
$object_table_at(S_iter.OBJECTTABLES,n_copy) = (n_table_copy)
S_iter.ARRAYS[n_table_copy].ITEMS = S_copy.ARRAYS[n_table_copy].ITEMS
S_iter.FRAMES = [pframe_clone]
S_saved = $constant_frame_scope(S_iter,pframe_clone,eps)
$clone_operation_valid(S_saved,pcloneoperation) /\ $clone_source_input_valid(S_saved,pcloneoperation)
$clone_callback_live(S_saved,pcloneoperation)
$call_descriptors_local_valid(S_saved)
$clone_context_valid(S_iter,pcallcontext_clone)
$ck_output(S_iter.EVENTS) = ptbytes_before_foreach
$ck_guard(S_iter)
''')
RETURN = lines(r'''
S_return.CURRENT = (pcallcontext_clone)
S_return.TODO = (RETURN_UNWIND (KNOWN PNULL) porigin_return?) :: ptask_return_tail*
S_return.FRAMES = [pframe_clone]
S_return_saved = $constant_frame_scope(S_return,pframe_clone,eps)
$clone_operation_valid(S_return_saved,pcloneoperation) /\ $clone_callback_live(S_return_saved,pcloneoperation)
$call_descriptors_local_valid(S_return_saved)
$heap_owners($heap_graph(S_return),HOBJECT n_copy) = 2
$ck_output(S_return.EVENTS) = ptbytes_after_callback
$ck_guard(S_return)
''')
RESULT = lines(r'''
S_result.TODO = (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_tail*
S_result.RESULT = KNOWN PNULL
$clone_callback_live(S_result,pcloneoperation)
$heap_owners($heap_graph(S_result),HOBJECT n_copy) = 1
$ck_guard(S_result)
PhpStep: S_result ~> S_delivery_raw
S_delivery_raw.TODO = ptask_tail*
S_delivery_raw.RESULT = KNOWN (POBJECT n_copy)
$clone_window_at(S_delivery_raw.CLONES,pcloneoperation) = eps
$heap_owners($heap_graph(S_delivery_raw),HOBJECT n_copy) = 1
S_delivery = $ck_after(S_result,S_delivery_raw)
$ck_guard(S_delivery)
''')
REFERENCE = lines(r'''
$property_slot_at(pobjectprops_source.SLOTS,$ptascii("value")) = (ppropertyslot_source)
ppropertyslot_source.STATE = PROP_VALUE (ALIAS n_value_cell)
ppropertyslot_source.DECL = (porigin_property)
S_front.STORE[n_value_cell] = DEFINED (PINT 1)
$propref_at(S_front.PROPREFS,n_value_cell) = (ppropref_source)
ppropref_source.SOURCES = [OBJECT_PROP_SOURCE n_source $ptascii("value") porigin_property]
$property_slot_at(pobjectprops_copy.SLOTS,$ptascii("value")) = (ppropertyslot_copy)
''')
RETIRED = lines(r'''
S_iter.STORE[n_source_cell] = DEFINED PNULL
~(HOBJECT n_source <- S_iter.ALLOCATIONS) /\ ~(HARRAY n_table_source <- S_iter.ALLOCATIONS)
$object_table_at(S_iter.OBJECTTABLES,n_source) = eps
$heap_owners($heap_graph(S_iter),HOBJECT n_payload) = 1
S_source_now = $resolve(S_saved,VARIABLE ptbytes_source z_source)
S_source_now.COMPLETION = NORMAL
S_source_now.RESULT = KNOWN PNULL
''')
FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ck_output(S_final.EVENTS) = ptbytes_final
~(HOBJECT n_source <- S_final.ALLOCATIONS) /\ ~(HOBJECT n_copy <- S_final.ALLOCATIONS)
$clone_window_at(S_final.CLONES,pcloneoperation) = eps /\ $ck_guard(S_final)
S_budget = $drive_steps(S_front,0)
S_budget = S_front[.COMPLETION = BUDGET]
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')
DERIVED = lines(r'''
pcloneoperation_wrong_input = pcloneoperation[.INPUT = (KNOWN (POBJECT n_source))]
~$clone_source_input_valid(S_copy,pcloneoperation_wrong_input)
pcloneoperation_wrong_line = pcloneoperation[.LINE = $(pcloneoperation.LINE + 1)]
~$clone_operation_source_valid(S_copy,pcloneoperation_wrong_line)
pcloneoperation_wrong_source = pcloneoperation[.SOURCE = n_copy]
~$clone_operation_body_valid(S_copy,pcloneoperation_wrong_source)
S_wrong_cache = S_copy[.ARRAYS[n_table_copy].ITEMS = S_front.ARRAYS[n_table_source].ITEMS]
~$object_tables_valid(S_wrong_cache)
''')

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('singleton', 'held', 'retire', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'cached_clone_callback_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_observations_accepted']
    assert [case['id'] for case in data['cases']] == ['singleton', 'held', 'retire', 'throwing']
    selected = data['cases']
    if args.case:
        assert len(args.case) == len(set(args.case))
        selected = [case for case in selected if case['id'] in args.case]
        assert len(selected) == len(args.case)
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, profile_file, php, adapter, bridge, worker, runner, compiler,
               manifest, *modules, *(HERE / case['source_file'] for case in data['cases']),
               *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json', 'frontend/target.php',
                    'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='cached-clone-callback-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [], 'fixtures': [], 'selection': [case['id'] for case in selected],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'premises': 0, 'reached_premises': 0, 'derived_premises': 0,
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent', 'jobs': 1}, 'passed': False}
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        for case in selected:
            name = case['id']
            source = HERE / case['source_file']
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            native_stderr = base64.b64decode(case['stderr_template_base64']).replace(b'{FILE}', case['original_source'].encode())
            native_tuple = base64.b64decode(case['stdout_base64']) + b'\0' + native_stderr + b'\0' + str(case['exit_status']).encode()
            assert hashlib.sha256(native_tuple).hexdigest() == case['native_raw_sha256']
            directory = out / name
            directory.mkdir()
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], directory / 'frontend')
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
                adapter_worker = Worker([str(adapter), str(ROOT)], directory / 'adapter')
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
            output = base64.b64decode(case['stdout_base64']).decode()
            before_output = {'singleton':'U:', 'held':'H:', 'retire':'R:', 'throwing':'X:'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'ptbytes_prefix = $ptascii(' + json.dumps(before_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + reach('S_front','S_initial','CK_CLONE') + FRONT
            keys = ['value','tag'] if name in ('singleton','held') else ['tag','payload']
            source_items = '[' + ','.join('ENTRY (KSTRING ($ptascii('+json.dumps(k)+'))) (INDIRECT n_source ($ptascii('+json.dumps(k)+')))' for k in keys) + ']'
            copy_items = '[' + ','.join('ENTRY (KSTRING ($ptascii('+json.dumps(k)+'))) (INDIRECT n_copy ($ptascii('+json.dumps(k)+')))' for k in keys) + ']'
            positions = '[' + ','.join('POSITION (KSTRING ($ptascii('+json.dumps(k)+'))) '+str(i) for i,k in enumerate(keys)) + ']'
            reached += ['S_front.ARRAYS[n_table_source].ITEMS = '+source_items,
                        'S_copy.ARRAYS[n_table_copy].ITEMS = '+copy_items,
                        'S_copy.ARRAYS[n_table_copy].POSITIONS = '+positions,
                        'S_copy.ARRAYS[n_table_copy].SERIAL = '+str(len(keys)),
                        'S_copy.ARRAYS[n_table_copy].NEXT = $(-9223372036854775808)']
            if name in ('singleton','held'):
                reached += REFERENCE
                if name == 'singleton':
                    reached += ['$heap_owners($heap_graph(S_front),HCELL n_value_cell) = 1',
                                'ppropertyslot_copy.STATE = PROP_VALUE (DIRECT (PINT 1))',
                                '$heap_owners($heap_graph(S_copy),HCELL n_value_cell) = 1',
                                '$propref_at(S_copy.PROPREFS,n_value_cell) = (ppropref_source)']
                else:
                    reached += ['$heap_owners($heap_graph(S_front),HCELL n_value_cell) = 2',
                                'ppropertyslot_copy.STATE = PROP_VALUE (ALIAS n_value_cell)',
                                '$heap_owners($heap_graph(S_copy),HCELL n_value_cell) = 3',
                                '$propref_at(S_copy.PROPREFS,n_value_cell) = (ppropref_copy)',
                                'ppropref_copy.SOURCES = [OBJECT_PROP_SOURCE n_source ($ptascii("value")) porigin_property,OBJECT_PROP_SOURCE n_copy ($ptascii("value")) porigin_property]']
            else:
                reached += lines(r"""
$property_slot_at(pobjectprops_source.SLOTS,$ptascii("payload")) = (ppropertyslot_payload)
ppropertyslot_payload.STATE = PROP_VALUE (DIRECT (POBJECT n_payload))
$property_slot_at(pobjectprops_copy.SLOTS,$ptascii("payload")) = (ppropertyslot_payload)
$heap_owners($heap_graph(S_front),HOBJECT n_payload) = 1
$heap_owners($heap_graph(S_copy),HOBJECT n_payload) = 2
""")
            reached += ENTER
            if name == 'retire':
                reached += reach('S_source_dtor','S_enter','CK_DTOR n_source')
                reached += lines(r"""
S_source_dtor.CURRENT = (pcallcontext_source_dtor)
$destructor_context_call(pcallcontext_source_dtor,S_source_dtor.CURRENT,S_source_dtor.FRAMES) = (pdestructorcall_source)
pdestructorcall_source.OBJECT = n_source
$clone_window_at(S_source_dtor.CLONES,pcloneoperation) = (pclonewindow)
$ck_output(S_source_dtor.EVENTS) = $ptascii("R:C|")
$ck_guard(S_source_dtor)
""")
                reached += ['ptbytes_before_foreach = $ptascii("R:C|D1|")']
                reached += reach('S_iter','S_source_dtor','CK_FOREACH') + ITERATE + RETIRED
            else:
                reached += ['ptbytes_before_foreach = ptbytes_prefix ++ $ptascii("C|")']
                reached += reach('S_iter','S_enter','CK_FOREACH') + ITERATE
                reached += ['S_iter.STORE[n_source_cell] = DEFINED (POBJECT n_source)',
                            'S_iter.ARRAYS[n_table_source] = S_front.ARRAYS[n_table_source]']
            if name != 'throwing':
                after = before_output + ('C|value:7|tag:2|c|' if name in ('singleton','held') else 'C|D1|T2|P7|c|')
                reached += ['ptbytes_after_callback = $ptascii('+json.dumps(after)+')']
                reached += reach('S_return','S_iter','CK_RETURN') + RETURN
                if name in ('singleton','held'):
                    reached += lines(r"""
$objectprops_record_at(S_return.OBJECTPROPS,n_source) = (pobjectprops_source)
$objectprops_record_at(S_return.OBJECTPROPS,n_copy) = (pobjectprops_copy_return)
$property_slot_at(pobjectprops_copy_return.SLOTS,$ptascii("value")) = (ppropertyslot_copy_return)
""")
                    if name == 'singleton':
                        reached += ['S_return.STORE[n_value_cell] = DEFINED (PINT 1)',
                                    'ppropertyslot_copy_return.STATE = PROP_VALUE (DIRECT (PINT 7))',
                                    '$propref_at(S_return.PROPREFS,n_value_cell) = (ppropref_source)']
                    else:
                        reached += ['S_return.STORE[n_value_cell] = DEFINED (PINT 7)',
                                    'ppropertyslot_copy_return.STATE = PROP_VALUE (ALIAS n_value_cell)',
                                    '$propref_at(S_return.PROPREFS,n_value_cell) = (ppropref_copy)',
                                    '$heap_owners($heap_graph(S_return),HCELL n_value_cell) = 3']
                else:
                    reached += ['~(HOBJECT n_source <- S_return.ALLOCATIONS)',
                                '$heap_owners($heap_graph(S_return),HOBJECT n_payload) = 1']
                reached += reach('S_result','S_return','CK_RESULT') + RESULT
                if name == 'held':
                    reached += reach('S_catch','S_delivery','CK_CATCH')
                    reached += lines(r"""
S_catch.TODO = (CATCH_BIND porigin_catch n_catch_index n_error) :: ptask_catch_tail*
S_catch.OBJECTS[n_error] = THROWABLE pthrowable_error
pthrowable_error.KIND = "TypeError"
$propref_at(S_catch.PROPREFS,n_value_cell) = (ppropref_catch)
ppropref_catch.SOURCES = [OBJECT_PROP_SOURCE n_copy ($ptascii("value")) porigin_property]
S_catch.STORE[n_value_cell] = DEFINED (PINT 7)
$heap_owners($heap_graph(S_catch),HCELL n_value_cell) = 2
$ck_output(S_catch.EVENTS) = $ptascii("H:C|value:7|tag:2|c|7/7/7|")
$ck_guard(S_catch)
""")
                    reached += reach('S_free','S_catch','CK_OUTPUT ($ptascii("H:C|value:7|tag:2|c|7/7/7|T|7|free|"))')
                    reached += lines(r"""
S_free.STORE[n_value_cell] = DEFINED (PSTRING_CARRIER INTERNED_STRING $ptascii("free"))
$propref_at(S_free.PROPREFS,n_value_cell) = eps
$heap_owners($heap_graph(S_free),HCELL n_value_cell) = 1
$ck_guard(S_free)
S_end = S_free
""")
                elif name == 'retire':
                    reached += reach('S_payload','S_delivery','CK_DTOR n_payload')
                    reached += ['$ck_output(S_payload.EVENTS) = $ptascii("R:C|D1|T2|P7|c|A|2/7|D2|")',
                                r'$clone_window_at(S_payload.CLONES,pcloneoperation) = eps /\ $ck_guard(S_payload)',
                                'S_end = S_payload']
                else:reached += ['S_end = S_delivery']
            else:
                reached += lines(r"""
$lookup(S_front.ENV,$ptascii("error")) = (n_error_cell)
S_front.STORE[n_error_cell] = DEFINED (POBJECT n_error)
$lookup(S_front.ENV,$ptascii("result")) = (n_result_cell)
S_front.STORE[n_result_cell] = DEFINED (PINT 42)
""")
                reached += reach('S_source_dtor','S_iter','CK_DTOR n_source')
                reached += lines(r"""
S_source_dtor.CURRENT = (pcallcontext_source_dtor)
$destructor_context_call(pcallcontext_source_dtor,S_source_dtor.CURRENT,S_source_dtor.FRAMES) = (pdestructorcall_source)
pdestructorcall_source.OBJECT = n_source
$clone_window_at(S_source_dtor.CLONES,pcloneoperation) = (pclonewindow)
$ck_output(S_source_dtor.EVENTS) = $ptascii("X:C|T2|P7|")
$ck_guard(S_source_dtor)
""")
                reached += reach('S_throw','S_source_dtor','CK_THROW')
                reached += lines(r"""
S_throw.CURRENT = (pcallcontext_clone)
S_throw.TODO = (THROW_VALUE porigin_throw z_throw) :: ptask_throw_tail*
S_throw.FRAMES = [pframe_clone]
S_throw_saved = $constant_frame_scope(S_throw,pframe_clone,eps)
$clone_operation_valid(S_throw_saved,pcloneoperation) /\ $clone_callback_live(S_throw_saved,pcloneoperation)
$call_descriptors_local_valid(S_throw_saved)
S_throw.STORE[n_source_cell] = DEFINED PNULL
~(HOBJECT n_source <- S_throw.ALLOCATIONS) /\ ~(HARRAY n_table_source <- S_throw.ALLOCATIONS)
$heap_owners($heap_graph(S_throw),HOBJECT n_payload) = 1
S_error_read = $resolve_at(S_throw,S_throw.RESULT,z_throw)
S_error_read.COMPLETION = NORMAL
S_error_read.RESULT = KNOWN (POBJECT n_error)
$ck_output(S_throw.EVENTS) = $ptascii("X:C|T2|P7|D1|c|")
$ck_guard(S_throw)
""")
                reached += reach('S_discard','S_throw','CK_DISCARD')
                reached += lines(r"""
S_discard.TODO = (THROW_SEARCH n_error) :: (CLONE_CALLBACK_RESULT pcloneoperation) :: ptask_tail*
$clone_callback_live(S_discard,pcloneoperation) /\ $ck_guard(S_discard)
PhpStep: S_discard ~> S_discard_raw
S_discard_raw.TODO = (THROW_SEARCH n_error) :: ptask_tail*
$clone_window_at(S_discard_raw.CLONES,pcloneoperation) = eps
$heap_owners($heap_graph(S_discard_raw),HOBJECT n_copy) = 0
S_releasing = $ck_after(S_discard,S_discard_raw)
""")
                reached += reach('S_copy_dtor','S_releasing','CK_DTOR n_copy')
                reached += lines(r"""
S_copy_dtor.CURRENT = (pcallcontext_copy_dtor)
$destructor_context_call(pcallcontext_copy_dtor,S_copy_dtor.CURRENT,S_copy_dtor.FRAMES) = (pdestructorcall_copy)
pdestructorcall_copy.OPERATION = (pdestructionoperation_copy)
pdestructionoperation_copy.SOURCE = THROW_SEARCH n_error
pdestructionoperation_copy.PENDING = (n_error)
pdestructionoperation_copy.VALUE = KNOWN PNULL /\ pdestructionoperation_copy.BASE = BASE_VALUE (KNOWN PNULL)
$clone_window_at(S_copy_dtor.CLONES,pcloneoperation) = eps
$ck_output(S_copy_dtor.EVENTS) = $ptascii("X:C|T2|P7|D1|c|")
$ck_guard(S_copy_dtor)
""")
                reached += reach('S_payload','S_copy_dtor','CK_DTOR n_payload')
                reached += ['$ck_output(S_payload.EVENTS) = $ptascii("X:C|T2|P7|D1|c|D2|")', '$ck_guard(S_payload)']
                reached += reach('S_catch','S_payload','CK_CATCH')
                reached += lines(r"""
S_catch.TODO = (CATCH_BIND porigin_catch n_catch_index n_error) :: ptask_catch_tail*
S_catch.STORE[n_result_cell] = DEFINED (PINT 42)
~(HOBJECT n_source <- S_catch.ALLOCATIONS) /\ ~(HOBJECT n_copy <- S_catch.ALLOCATIONS) /\ ~(HOBJECT n_payload <- S_catch.ALLOCATIONS)
$throwable_previous_id(S_catch,n_error) = eps
$clone_window_at(S_catch.CLONES,pcloneoperation) = eps
$ck_output(S_catch.EVENTS) = $ptascii("X:C|T2|P7|D1|c|D2|V7|")
$ck_guard(S_catch)
S_end = S_catch
""")
            reached += FINISH
            if name in ('retire','throwing'):reached += ['~(HOBJECT n_payload <- S_final.ALLOCATIONS)']
            derived = DERIVED if name == 'singleton' else []
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'cached-clone-callback.watsup'
            fixture.write_text(content)
            row = {'id': name, 'path': str(fixture), 'sha256': sha(fixture), 'reached_premises': len(reached), 'derived_premises': len(derived), 'premises': len(reached) + len(derived)}
            report['fixtures'].append(row)
            for key in ('premises', 'reached_premises', 'derived_premises'):
                report[key] += row[key]
        report.update(prepared=True, passed=True)
        if not args.prepare_only:
            for fixture in report['fixtures']:
                directory = Path(fixture['path']).parent
                process = recorder.recorded([str(compiler), 'algo', *map(str, modules), fixture['path']], directory / 'compiler', 90)
                passed = process['exit'] == 0 and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id': fixture['id'] + '-algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner), '--sl', *map(str, modules), fixture['path']], directory / 'state', 90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['interruption'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
                report['records'].append({'id': fixture['id'] + '-strict-SL-application', 'process': process, 'passed': passed})
                report['passed'] = passed
                assert passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixtures_stable=all(row['sha256'] == sha(Path(row['path'])) for row in report['fixtures']),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixtures_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'premises', 'reached_premises', 'derived_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()

