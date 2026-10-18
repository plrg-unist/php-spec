"""Check terminal empty without isset, borrowed CV ownership and later real getter."""
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
syntax pgetemptystage = GE_PREP | GE_PUBLIC | GE_READ | GE_ENTER | GE_RESULT | GE_THROW | GE_CATCH | GE_DTOR nat | GE_COLLECT | GE_OUTPUT ptbytes
dec $ge_output(pevent*) : ptbytes
def $ge_output(eps) = eps
def $ge_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $ge_output(pevent*)
dec $ge_stage(pstate,pgetemptystage) : bool
def $ge_stage(S,GE_PREP) = true
  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z) :: (ORIGIN_RETURN (porigin)) :: (ISSET_RESULT true z) :: ptask*
  -- if $base64(text_name) = $ptascii("value")
def $ge_stage(S,GE_PUBLIC) = true
  -- if S.TODO = (ISSET_RESULT true z) :: ptask*
  -- if S.BASE = BASE_PROPERTY (POBJECT n) $ptascii("ready")
def $ge_stage(S,GE_READ) = ($property_get_plan(S) =/= eps)
def $ge_stage(S,GE_ENTER) = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_GET_TARGET n porigin
def $ge_stage(S,GE_RESULT) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask*
def $ge_stage(S,GE_THROW) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (THROW_SEARCH n) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask*
def $ge_stage(S,GE_CATCH) = true
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask*
def $ge_stage(S,GE_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $ge_stage(S,GE_COLLECT) = true
  -- if S.TODO = (CONFIG_INVOKE pconfigcall) :: ptask*
  -- if pconfigcall.KIND = INTRINSIC_GC_COLLECT
def $ge_stage(S,GE_OUTPUT ptbytes) = ($ge_output(S.EVENTS) = ptbytes)
def $ge_stage(S,pgetemptystage) = false -- otherwise
dec $ge_seek(pstate,pgetemptystage,nat) : pstate
def $ge_seek(S,pgetemptystage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $ge_stage(S,pgetemptystage) \/ n = 0
def $ge_seek(S,pgetemptystage,n) = $ge_seek($drive_steps(S[.COMPLETION = NORMAL],1),pgetemptystage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$ge_stage(S,pgetemptystage) /\ $(n > 0)
def $ge_seek(S,pgetemptystage,n) = $ge_seek($drive_steps(S,1),pgetemptystage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $ge_seek(S,pgetemptystage,n) = S -- otherwise
dec $ge_after(pstate,pstate) : pstate
def $ge_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $ge_guard(pstate) : bool
def $ge_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
'''

COMMON = r'''
$ge_stage(S,GE_PREP)
S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_empty) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT true z_empty) :: ptask_tail*
S.ORIGIN = (porigin_site) /\ S.CURRENT = eps /\ S.FRAMES = eps
S.BASE = BASE_VALUE (KNOWN PNULL) /\ $operand_nodes(S.RESULT) = eps
S_read = $quiet_operand(S,S.RESULT)
S_read.COMPLETION = NORMAL
S_read.RESULT = KNOWN (POBJECT n_child)
$property_empty_source(S,porigin_site,$base64(text_name),z_empty) /\ $property_empty_get_skip(S) /\ $property_empty_prepare(S)
~$property_get_pending(S) /\ $property_get_plan(S) = eps
$property_isset_method(S,n_child) = eps
$property_get_method(S,n_child) = (pmethoddesc_get)
$property_empty_get_source(S,pmethoddesc_get)
$property_effective_desc(S,n_child,$base64(text_name)) = (ppropertydesc)
ppropertydesc.VISIBILITY = PROPERTY_PRIVATE /\ $property_declaring_class(S.CLASSES,ppropertydesc.ORIGIN) = (pmethoddesc_get.OWNER)
S.OBJECTS[n_child] = INSTANCE porigin_child
porigin_child =/= pmethoddesc_get.OWNER /\ $property_resolve(S,n_child,$base64(text_name)) = PROPERTY_ACCESS $base64(text_name)
$objectprops_at(S.OBJECTPROPS,n_child) = (ppropertyslot_all*)
$property_slot_at(ppropertyslot_all*,$base64(text_name)) = eps
$heap_owners($heap_graph(S),HOBJECT n_child) = 1 /\ $ge_guard(S)
PhpStep: S ~> S_skip_raw
S_skip_raw.TODO = (ORIGIN_RETURN (porigin_site)) :: ptask_tail*
S_skip_raw.RESULT = KNOWN (PBOOL true) /\ S_skip_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_skip_raw.EVENTS = S.EVENTS /\ S_skip_raw.STORE = S.STORE /\ S_skip_raw.OBJECTPROPS = S.OBJECTPROPS
S_skip = $ge_after(S,S_skip_raw)
S_skip.GC = S.GC /\ S_skip.DESTRUCTION = S.DESTRUCTION /\ S_skip.EVENTS = S.EVENTS
$heap_owners($heap_graph(S_skip),HOBJECT n_child) = 1 /\ $machine_base_roots(S_skip) = eps /\ $ge_guard(S_skip)
PhpStep: S_skip ~> S_origin_raw
S_origin_raw.TODO = ptask_tail* /\ S_origin_raw.RESULT = KNOWN (PBOOL true) /\ S_origin_raw.ORIGIN = (porigin_site)
S_origin = $ge_after(S_skip,S_origin_raw)
S_origin.GC = S.GC /\ $heap_owners($heap_graph(S_origin),HOBJECT n_child) = 1
S_public_found = $ge_seek(S_origin,GE_PUBLIC,1000)
S_public_found.COMPLETION = NORMAL \/ S_public_found.COMPLETION = BUDGET
S_public = S_public_found[.COMPLETION = NORMAL]
S_public.TODO = (ISSET_RESULT true z_public) :: ptask_public*
S_public.BASE = BASE_PROPERTY (POBJECT n_child) $ptascii("ready")
$ge_output(S_public.EVENTS) = ptbytes_prefix ++ $ptascii("T|")
~$property_get_needed(S_public,n_child,$ptascii("ready")) /\ ~$property_empty_get_skip(S_public)
PhpStep: S_public ~> S_public_raw
S_public_raw.RESULT = KNOWN (PBOOL false) /\ S_public_raw.TODO = ptask_public* /\ S_public_raw.EVENTS = S_public.EVENTS
S_public_done = $ge_after(S_public,S_public_raw)
S_get_found = $ge_seek(S_public_done,GE_READ,1000)
S_get_found.COMPLETION = NORMAL \/ S_get_found.COMPLETION = BUDGET
S_get = S_get_found[.COMPLETION = NORMAL]
$property_get_plan(S_get) = (ppropertyget)
ppropertyget.OBJECT = n_child /\ ppropertyget.NAME = $base64(text_name) /\ ppropertyget.METHOD = pmethoddesc_get.FUNCTION.ORIGIN
$property_get_pending(S_get) /\ ~$property_empty_get_skip(S_get)
$ge_output(S_get.EVENTS) = ptbytes_prefix ++ $ptascii("T|F|")
S_entered_found = $ge_seek(S_get,GE_ENTER,1000)
S_entered_found.COMPLETION = NORMAL \/ S_entered_found.COMPLETION = BUDGET
S_entered = S_entered_found[.COMPLETION = NORMAL]
S_entered.CURRENT = (pcallcontext_get)
pcallcontext_get.TARGET = PROPERTY_GET_TARGET n_child ppropertyget.METHOD
$property_get_context(S_entered,pcallcontext_get) /\ $ge_guard(S_entered)
'''.strip().splitlines()

RETURN = r'''
S_result_found = $ge_seek(S_entered,GE_RESULT,1000)
S_result_found.COMPLETION = NORMAL \/ S_result_found.COMPLETION = BUDGET
S_result = S_result_found[.COMPLETION = NORMAL]
S_result.TODO = (PROPERTY_GET_RESULT ppropertyget) :: ptask_result*
S_result.RESULT = KNOWN (PINT 42) /\ $ge_output(S_result.EVENTS) = ptbytes_prefix ++ $ptascii("T|F|G|")
S_after_get = S_result
'''.strip().splitlines()

THROW = r'''
S_throw_found = $ge_seek(S_entered,GE_THROW,1000)
S_throw_found.COMPLETION = NORMAL \/ S_throw_found.COMPLETION = BUDGET
S_throw = S_throw_found[.COMPLETION = NORMAL]
S_throw.TODO = (THROW_SEARCH n_error) :: (PROPERTY_GET_RESULT ppropertyget) :: ptask_throw*
$throwable_live(S_throw,n_error) /\ $ge_output(S_throw.EVENTS) = ptbytes_prefix ++ $ptascii("T|F|G|")
S_catch_found = $ge_seek(S_throw,GE_CATCH,1000)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_try n_catch n_error) :: ptask_catch*
$throwable_live(S_catch,n_error) /\ $ge_output(S_catch.EVENTS) = ptbytes_prefix ++ $ptascii("T|F|G|")
PhpStep: S_catch ~> S_catch_raw
$lookup(S_catch_raw.ENV,$ptascii("caught")) = (n_caught_cell)
S_catch_raw.STORE[n_caught_cell] = DEFINED (POBJECT n_error)
S_after_get = $ge_after(S_catch,S_catch_raw)
S_after_get.COMPLETION = NORMAL /\ $throwable_live(S_after_get,n_error) /\ $ge_guard(S_after_get)
'''.strip().splitlines()

FINISH = r'''
S_dtor_found = $ge_seek(S_after_get,GE_DTOR n_child,1000)
S_dtor_found.COMPLETION = NORMAL \/ S_dtor_found.COMPLETION = BUDGET
S_dtor = S_dtor_found[.COMPLETION = NORMAL]
$ge_stage(S_dtor,GE_DTOR n_child) /\ $ge_output(S_dtor.EVENTS) = ptbytes_before_dtor
$ge_guard(S_dtor)
S_final = $drive_steps(S_dtor,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$ge_output(S_final.EVENTS) = ptbytes_final /\ ~(HOBJECT n_child <- S_final.ALLOCATIONS)
$ge_guard(S_final)
S_budget = $drive_steps(S_entered,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_entered.TODO /\ S_budget.EVENTS = S_entered.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
'''.strip().splitlines()

DERIVED = r'''
S_missing = S[.SOURCES = eps]
S_missing.TODO = S.TODO /\ S_missing.ORIGIN = S.ORIGIN /\ ~$property_empty_get_skip(S_missing)
pfunction_get = pmethoddesc_get.FUNCTION
pfunction_badline = pfunction_get[.LINE = $(pfunction_get.LINE + 1)]
pmethoddesc_badline = pmethoddesc_get[.FUNCTION = pfunction_badline]
~$property_empty_get_source(S,pmethoddesc_badline)
S_wrongflag = S[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_empty) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT false z_empty) :: ptask_tail*]
~$property_empty_get_skip(S_wrongflag) /\ $property_get_pending(S_wrongflag) /\ $property_get_plan(S_wrongflag) = eps
PhpStep: S_wrongflag ~> S_wrongflag_done
S_wrongflag_done.COMPLETION = UNSUPPORTED "magic getter receiver, signature or recursive access" /\ S_wrongflag_done.EVENTS = S.EVENTS
S_wrongline = S[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) $(z_empty + 1)) :: (ORIGIN_RETURN (porigin_site)) :: (ISSET_RESULT true $(z_empty + 1)) :: ptask_tail*]
~$property_empty_get_skip(S_wrongline) /\ $property_get_pending(S_wrongline)
S_ancestor = S[.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) z_empty) :: (ORIGIN_RETURN (porigin_site)) :: (DIM_FETCH z_empty) :: ptask_tail*]
~$property_empty_get_skip(S_ancestor) /\ $property_get_pending(S_ancestor) /\ $property_get_plan(S_ancestor) = eps
S_owning = S[.RESULT = KNOWN (POBJECT n_child)]
$operand_nodes(S_owning.RESULT) = [HOBJECT n_child] /\ ~$property_empty_get_skip(S_owning)
S_cached = S[.BASE = BASE_PROPERTY (POBJECT n_child) $base64(text_name)]
~$property_empty_get_skip(S_cached)
S_other = $write_name($write_name(S,$ptascii("other"),POBJECT n_child),$ptascii("child"),PNULL)[.RESULT = VARIABLE $ptascii("other") z_empty]
S_other_read = $quiet_operand(S_other,S_other.RESULT)
S_other_read.COMPLETION = NORMAL /\ S_other_read.RESULT = KNOWN (POBJECT n_child)
~$property_empty_get_skip(S_other) /\ $property_get_needed(S_other,n_child,$base64(text_name))
ppropertyslot_dynamic = {DECL eps, NAME $base64(text_name), STATE PROP_VALUE (DIRECT (PINT 1))}
S_dynamic = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_child,ppropertyslot_all* ++ [ppropertyslot_dynamic])]
$property_effective_desc(S_dynamic,n_child,$base64(text_name)) = (ppropertydesc)
$property_unset_access_valid(S_dynamic,n_child,$base64(text_name),ppropertydesc,$property_resolve(S_dynamic,n_child,$base64(text_name)))
~$property_get_needed(S_dynamic,n_child,$base64(text_name)) /\ ~$property_empty_get_skip(S_dynamic)
PhpStep: S_dynamic ~> S_dynamic_raw
S_dynamic_origin = $ge_after(S_dynamic,S_dynamic_raw)
PhpStep: S_dynamic_origin ~> S_dynamic_terminal_raw
S_dynamic_terminal = $ge_after(S_dynamic_origin,S_dynamic_terminal_raw)
S_dynamic_terminal.TODO = (ISSET_RESULT true z_empty) :: ptask_tail*
PhpStep: S_dynamic_terminal ~> S_dynamic_done
S_dynamic_done.COMPLETION = NORMAL /\ S_dynamic_done.RESULT = KNOWN (PBOOL false) /\ S_dynamic_done.EVENTS = S.EVENTS
'''.strip().splitlines()

GC = r'''
S_collect_found = $ge_seek(S_gc_initial,GE_COLLECT,1000)
S_collect_found.COMPLETION = NORMAL \/ S_collect_found.COMPLETION = BUDGET
S_collect = S_collect_found[.COMPLETION = NORMAL]
$ge_stage(S_collect,GE_COLLECT)
S_collect_started = $drive_steps(S_collect,1)
S_collect_started.COMPLETION = NORMAL \/ S_collect_started.COMPLETION = BUDGET
S_collect_started.GC.ACTIVE =/= eps
S_gc_found = $ge_seek(S_collect_started,GE_PREP,1000)
S_gc_found.COMPLETION = NORMAL \/ S_gc_found.COMPLETION = BUDGET
S_gc = S_gc_found[.COMPLETION = NORMAL]
S_gc.GC.ACTIVE = eps /\ S_gc.GC.PLAN = eps /\ $gc_nodes(S_gc.GC.BUFFER) = eps
$property_empty_get_skip(S_gc) /\ $machine_base_roots(S_gc) = eps
S_gc_read = $quiet_operand(S_gc,S_gc.RESULT)
S_gc_read.COMPLETION = NORMAL
S_gc_read.RESULT = KNOWN (POBJECT n_gc_child)
$heap_owners($heap_graph(S_gc),HOBJECT n_gc_child) = 1
PhpStep: S_gc ~> S_gc_raw
S_gc_raw.RESULT = KNOWN (PBOOL true) /\ S_gc_raw.BASE = BASE_VALUE (KNOWN PNULL)
S_gc_skip = $ge_after(S_gc,S_gc_raw)
S_gc_skip.GC = S_gc.GC /\ S_gc_skip.DESTRUCTION = S_gc.DESTRUCTION /\ $machine_base_roots(S_gc_skip) = eps
$heap_owners($heap_graph(S_gc_skip),HOBJECT n_gc_child) = 1
S_gc_output_found = $ge_seek(S_gc_skip,GE_OUTPUT $ptascii("N:T|"),1000)
S_gc_output_found.COMPLETION = NORMAL \/ S_gc_output_found.COMPLETION = BUDGET
S_gc_output = S_gc_output_found[.COMPLETION = NORMAL]
$ge_stage(S_gc_output,GE_OUTPUT $ptascii("N:T|"))
S_gc_output.GC = S_gc.GC /\ $gc_nodes(S_gc_output.GC.BUFFER) = eps /\ $heap_owners($heap_graph(S_gc_output),HOBJECT n_gc_child) = 1
$ge_guard(S_gc_output)
S_gc_budget = $drive_steps(S_gc,0)
S_gc_budget.COMPLETION = BUDGET /\ S_gc_budget.TODO = S_gc.TODO /\ S_gc_budget.GC = S_gc.GC
$ge_seek(S_gc_budget[.COMPLETION = NORMAL],GE_OUTPUT $ptascii("N:T|"),1000) = S_gc_output_found
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', choices=('normal', 'throwing'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'magic_empty_get_only_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    selected = [case for case in data['cases'] if case['id'] in ('normal', 'throwing')]
    assert len(selected) == 2
    if args.case:
        selected = [case for case in selected if case['id'] == args.case]
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, profile_file, php, adapter, bridge, worker, runner, compiler,
               manifest, *modules, *(HERE / case['source_file'] for case in data['cases']), HERE / data['gc_prefix']['source_file'],
               *(ROOT / name for name in ['spec/schema.json', 'spec/php.watsup', 'spec/nodes.json', 'frontend/target.php',
                    'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/static_types.py'])]
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='magic-empty-get-only-protocol-', dir=ROOT / '.tools'))
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
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $ge_seek(S_initial,GE_PREP,1000)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]', 'ptbytes_prefix = $ptascii(' + json.dumps(output[:2]) + ')',
                     'ptbytes_before_dtor = $ptascii(' + json.dumps(output[:output.index('D|')]) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + (RETURN if name == 'normal' else THROW) + FINISH + [f'z_empty = {case["empty_line"]}']
            if name == 'normal':
                gc_source = HERE / data['gc_prefix']['source_file']
                assert sha(gc_source) == data['gc_prefix']['source_sha256']
                frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], directory / 'gc-frontend')
                adapter_worker = None
                try:
                    parsed_gc = frontend.request({'op': 'parse', 'source': base64.b64encode(gc_source.read_bytes()).decode()})
                    assert parsed_gc['accepted']
                    adapter_worker = Worker([str(adapter), str(ROOT)], directory / 'gc-adapter')
                    checked_gc = adapter_worker.request({'op': 'check', 'ast': parsed_gc['ast'], 'fixture': True})
                    assert checked_gc['ok'] and checked_gc['ast'] == parsed_gc['ast']
                finally:
                    if adapter_worker:
                        adapter_worker.close()
                    frontend.close()
                reached += ['S_gc_initial = $php_run(' + checked_gc['fixture'] + ',0,' + json.dumps(base64.b64encode(str(gc_source).encode()).decode()) + ')',
                            r'S_gc_initial.COMPLETION = NORMAL \/ S_gc_initial.COMPLETION = BUDGET'] + GC
            derived = DERIVED if name == 'normal' else []
            content = PREFIX + '\ndec $main() : bool\ndef $main() = true\n'
            for condition in reached + derived:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $main() = false -- otherwise\n'
            fixture = directory / 'hook.watsup'
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
                passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (directory / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (directory / 'compiler.stdout').read_bytes()
                report['records'].append({'id': fixture['id'] + '-algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
                report['passed'] = passed
                assert passed
                report['application_invocations'] += 1
                process = recorder.recorded([str(runner), '--sl', *map(str, modules), fixture['path']], directory / 'state', 90)
                output = (directory / 'state.stdout').read_bytes()
                evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
                report['application_evaluations'] += int(evaluated)
                passed = evaluated and not process['timeout'] and not process['group_after'] and not (directory / 'state.stderr').read_bytes() and output == b'true\n'
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
