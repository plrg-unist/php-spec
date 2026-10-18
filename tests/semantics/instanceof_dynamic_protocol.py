"""Check dynamic instanceof class capture, delayed reads, cleanup and error order."""
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
syntax pdistage = DI_CLASS | DI_RESULT | DI_DTOR nat | DI_CLASS_STRING ptbytes | DI_CATCH
dec $di_output(pevent*) : ptbytes
def $di_output(eps) = eps
def $di_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $di_output(pevent*)
dec $di_stage(pstate,pdistage) : bool
def $di_stage(S,DI_CLASS) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (INSTANCEOF_DYNAMIC_CLASS poperand z) :: ptask_tail*
def $di_stage(S,DI_RESULT) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (INSTANCEOF_DYNAMIC_RESULT poperand pvalue z) :: ptask_tail*
def $di_stage(S,DI_DTOR n) = true
  -- if S.CURRENT = (pcallcontext)
  -- if $destructor_context_call(pcallcontext,S.CURRENT,S.FRAMES) = (pdestructorcall)
  -- if pdestructorcall.OBJECT = n
def $di_stage(S,DI_CLASS_STRING ptbytes) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (INSTANCEOF_DYNAMIC_CLASS poperand z) :: ptask_tail*
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if S_read = $quiet_operand(S[.COMPLETION = NORMAL],S.RESULT)
  -- if S_read.COMPLETION = NORMAL
  -- if S_read.RESULT = KNOWN pvalue
  -- if $instanceof_dynamic_class(S_read,pvalue) = (ptbytes)
def $di_stage(S,DI_CATCH) = true
  -- if S.CURRENT = eps
  -- if S.TODO = (CATCH_BIND porigin n_index n_error) :: ptask_tail*
def $di_stage(S,pdistage) = false -- otherwise
dec $di_seek(pstate,pdistage,nat) : pstate
def $di_seek(S,pdistage,n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $di_stage(S,pdistage) \/ n = 0
def $di_seek(S,pdistage,n) = $di_seek($drive_steps(S[.COMPLETION = NORMAL],1),pdistage,$nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$di_stage(S,pdistage) /\ $(n > 0)
def $di_seek(S,pdistage,n) = $di_seek($drive_steps(S,1),pdistage,$nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $di_seek(S,pdistage,n) = S -- otherwise
dec $di_after(pstate,pstate) : pstate
def $di_after(S,S_next) = $gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))
dec $di_guard(pstate) : bool
def $di_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $gc_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $di_undefined(pstate,ptbytes) : bool
def $di_undefined(S,ptbytes) = true -- if $lookup(S.ENV,ptbytes) = eps
def $di_undefined(S,ptbytes) = true
  -- if $lookup(S.ENV,ptbytes) = (n)
  -- if S.STORE[n] = UNDEFINED
def $di_undefined(S,ptbytes) = false -- otherwise
dec $di_literal_constant(pstate,nat,pconstant) : porigin*
def $di_literal_constant(S,n,PCONSTANT pcpath (PBOOL false)) = [PORIGIN n pcpath]
  -- if $origin_node(S.SOURCES,PORIGIN n pcpath) = (NExprInstanceof (NScalarInt (INTEGER 7) metadata_left) expression_right metadata)
def $di_literal_constant(S,n,pconstant) = eps -- otherwise
dec $di_literal_sites(pstate,nat,pconstant*) : porigin*
def $di_literal_sites(S,n,eps) = eps
def $di_literal_sites(S,n,pconstant :: pconstant_tail*) = $di_literal_constant(S,n,pconstant) ++ $di_literal_sites(S,n,pconstant_tail*)
'''

def lines(text): return [line for line in text.strip().splitlines() if line]

COMMON = lines(r'''
$di_stage(S,DI_CLASS)
S.TODO = (INSTANCEOF_DYNAMIC_CLASS poperand_left z_left) :: ptask_tail*
S.ORIGIN = (porigin_site)
$instanceof_dynamic_site(S,z_left) /\ $instanceof_dynamic_left_valid(S,poperand_left)
$instanceof_dynamic_rhs_valid(S,S.RESULT)
$task_nodes(INSTANCEOF_DYNAMIC_CLASS poperand_left z_left) = $operand_nodes(poperand_left)
$di_output(S.EVENTS) = ptbytes_initial
$di_guard(S)
S_budget_start = S
''')

OBJECT = lines(r'''
S.RESULT = KNOWN (POBJECT n_rhs)
n_rhs =/= n_left
HOBJECT n_rhs <- S.ALLOCATIONS
HOBJECT n_left <- S.ALLOCATIONS
$objectprops_at(S.OBJECTPROPS,n_rhs) = (ppropertyslot_rhs*)
$property_slot_at(ppropertyslot_rhs*,$ptascii("role")) = (ppropertyslot_role)
ppropertyslot_role.STATE = PROP_VALUE (DIRECT (PINT 1))
$instanceof_dynamic_rhs_live(S,POBJECT n_rhs)
$instanceof_dynamic_class(S,POBJECT n_rhs) = (ptbytes_class)
ptbytes_class = $ptascii("Child102")
$heap_owners($heap_graph(S),HOBJECT n_rhs) = 1
$heap_owners($heap_graph(S),HOBJECT n_left) = n_left_owners
PhpStep: S ~> S_captured
S_captured = S[.TODO = (INSTANCEOF_DYNAMIC_RESULT poperand_left (POBJECT n_rhs) z_left) :: ptask_tail*][.RESULT = KNOWN PNULL][.BASE = BASE_VALUE (KNOWN PNULL)]
$task_nodes(INSTANCEOF_DYNAMIC_RESULT poperand_left (POBJECT n_rhs) z_left) = $operand_nodes(poperand_left)
$heap_owners($heap_graph(S_captured),HOBJECT n_rhs) = 0
$heap_owners($heap_graph(S_captured),HOBJECT n_left) = n_left_owners
$call_task_valid(S_captured,INSTANCEOF_DYNAMIC_RESULT poperand_left (POBJECT n_rhs) z_left)
S_disposing = $di_after(S,S_captured)
S_rhs_found = $di_seek(S_disposing,DI_DTOR n_rhs,1500)
S_rhs_found.COMPLETION = NORMAL \/ S_rhs_found.COMPLETION = BUDGET
S_rhs = S_rhs_found[.COMPLETION = NORMAL]
$di_stage(S_rhs,DI_DTOR n_rhs)
$di_output(S_rhs.EVENTS) = ptbytes_initial
S_rhs.FRAMES = pframe_rhs :: eps
S_saved = $constant_frame_view(S_rhs,pframe_rhs,eps)
S_saved.ORIGIN = (porigin_site)
$instanceof_dynamic_class(S_saved,POBJECT n_rhs) = (ptbytes_class)
$call_task_valid(S_saved,INSTANCEOF_DYNAMIC_RESULT poperand_left (POBJECT n_rhs) z_left)
$heap_owners($heap_graph(S_rhs),HOBJECT n_left) = n_left_owners
$di_guard(S_rhs)
S_resume_found = $di_seek(S_rhs,DI_RESULT,1500)
S_resume_found.COMPLETION = NORMAL \/ S_resume_found.COMPLETION = BUDGET
S_resume = S_resume_found[.COMPLETION = NORMAL]
S_resume.TODO = (INSTANCEOF_DYNAMIC_RESULT poperand_left (POBJECT n_rhs) z_left) :: ptask_tail*
S_resume.CURRENT = eps /\ S_resume.FRAMES = eps
$di_output(S_resume.EVENTS) = ptbytes_initial ++ $ptascii("R|")
~(HOBJECT n_rhs <- S_resume.ALLOCATIONS)
~(HOBJECT n_rhs <- $gc_nodes(S_resume.GC.BUFFER))
~$instanceof_dynamic_rhs_live(S_resume,POBJECT n_rhs)
$instanceof_dynamic_class(S_resume,POBJECT n_rhs) = (ptbytes_class)
$heap_owners($heap_graph(S_resume),HOBJECT n_left) = 1
S_current_left = $quiet_operand(S_resume,VARIABLE ($ptascii("left")) z_left)
S_current_left.COMPLETION = NORMAL
S_current_left.RESULT = KNOWN (POBJECT n_other)
$object_name(S_resume,n_other) = $ptascii("Other102")
n_other =/= n_left
~$class_instanceof(S_resume,POBJECT n_other,ptbytes_class)
$class_instanceof(S_resume,POBJECT n_left,ptbytes_class)
$di_guard(S_resume)
PhpStep: S_resume ~> S_predicate
S_predicate.TODO = ptask_tail*
S_predicate.RESULT = KNOWN (PBOOL b_expected)
S_predicate.BASE = BASE_VALUE (KNOWN PNULL)
S_predicate.EVENTS = S_resume.EVENTS
S_predicate.ALLOCATIONS = S_resume.ALLOCATIONS
S_after_result = $di_after(S_resume,S_predicate)
''')

OWNING = lines(r'''
$heap_owners($heap_graph(S_predicate),HOBJECT n_left) = 0
S_left_found = $di_seek(S_after_result,DI_DTOR n_left,1500)
S_left_found.COMPLETION = NORMAL \/ S_left_found.COMPLETION = BUDGET
S_left = S_left_found[.COMPLETION = NORMAL]
$di_stage(S_left,DI_DTOR n_left)
$di_output(S_left.EVENTS) = ptbytes_initial ++ $ptascii("R|")
S_left.CURRENT = (pcallcontext_left)
$destructor_context_call(pcallcontext_left,S_left.CURRENT,S_left.FRAMES) = (pdestructorcall_left)
pdestructorcall_left.OPERATION = (pdestructionoperation_left)
pdestructionoperation_left.VALUE = KNOWN (PBOOL true)
pdestructionoperation_left.SOURCE = INSTANCEOF_DYNAMIC_RESULT poperand_left (POBJECT n_rhs) z_left
~(HOBJECT n_rhs <- S_left.ALLOCATIONS)
$instanceof_dynamic_class(S_left,POBJECT n_rhs) = (ptbytes_class)
$di_guard(S_left)
S_end = S_left
''')

STRINGS = lines(r'''
S_read = $quiet_operand(S,S.RESULT)
S_read.COMPLETION = NORMAL
S_read.RESULT = KNOWN pvalue_rhs
$instanceof_dynamic_class(S_read,pvalue_rhs) = (ptbytes_class)
$ptlc(ptbytes_class) = $ptascii("classstrings102") ++ [92] ++ $ptascii("base102")
$operand_nodes(poperand_left) = eps
PhpStep: S ~> S_captured
S_captured.TODO = (INSTANCEOF_DYNAMIC_RESULT poperand_left pvalue_rhs z_left) :: ptask_tail*
S_captured.AUTOLOAD = S.AUTOLOAD
PhpStep: S_captured ~> S_match
S_match.RESULT = KNOWN (PBOOL true)
S_match.EVENTS = S.EVENTS /\ S_match.AUTOLOAD = S.AUTOLOAD
$di_guard(S_match)
S_alias_found = $di_seek(S_match,DI_CLASS_STRING ($ptascii("Alias102")),1500)
S_alias_found.COMPLETION = NORMAL \/ S_alias_found.COMPLETION = BUDGET
S_alias = S_alias_found[.COMPLETION = NORMAL]
$di_stage(S_alias,DI_CLASS_STRING ($ptascii("Alias102")))
S_alias.TODO = (INSTANCEOF_DYNAMIC_CLASS poperand_alias z_alias) :: ptask_alias*
$instanceof_dynamic_rhs_valid(S_alias,S_alias.RESULT)
$di_guard(S_alias)
PhpStep: S_alias ~> S_alias_captured
S_alias_captured.TODO = (INSTANCEOF_DYNAMIC_RESULT poperand_alias pvalue_alias z_alias) :: ptask_alias*
$instanceof_dynamic_class(S_alias_captured,pvalue_alias) = ($ptascii("Alias102"))
PhpStep: S_alias_captured ~> S_alias_false
S_alias_false.RESULT = KNOWN (PBOOL false)
S_alias_false.EVENTS = S_alias.EVENTS /\ S_alias_false.AUTOLOAD = S.AUTOLOAD
S_missing_found = $di_seek(S_alias_false,DI_CLASS_STRING ($ptascii("Missing102")),1500)
S_missing_found.COMPLETION = NORMAL \/ S_missing_found.COMPLETION = BUDGET
S_missing = S_missing_found[.COMPLETION = NORMAL]
$di_stage(S_missing,DI_CLASS_STRING ($ptascii("Missing102")))
S_missing.TODO = (INSTANCEOF_DYNAMIC_CLASS poperand_missing z_missing) :: ptask_missing*
$instanceof_dynamic_rhs_valid(S_missing,S_missing.RESULT)
$di_guard(S_missing)
PhpStep: S_missing ~> S_missing_captured
S_missing_captured.TODO = (INSTANCEOF_DYNAMIC_RESULT poperand_missing pvalue_missing z_missing) :: ptask_missing*
$instanceof_dynamic_class(S_missing_captured,pvalue_missing) = ($ptascii("Missing102"))
PhpStep: S_missing_captured ~> S_missing_false
S_missing_false.RESULT = KNOWN (PBOOL false)
S_missing_false.EVENTS = S_missing.EVENTS /\ S_missing_false.AUTOLOAD = S.AUTOLOAD
S_end = S_missing_false
''')

INVALID = lines(r'''
$di_undefined(S,$ptascii("undefinedLeft"))
$lookup(S.ENV,$ptascii("answer")) = (n_answer)
S.STORE[n_answer] = DEFINED (PINT 42)
S.RESULT = VARIABLE n_rhs_name* z_rhs
n_rhs_name* = $ptascii("invalid")
z_rhs = $instanceof_dynamic_rhs_line(S)
PhpStep: S ~> S_error
S_error.COMPLETION = THROWN "Error" ($ptascii("Class name must be a valid object or a string")) z_rhs
S_error.EVENTS = S.EVENTS /\ S_error.STORE = S.STORE
$di_undefined(S_error,$ptascii("undefinedLeft"))
S_raised = $di_after(S,S_error)
S_raised.COMPLETION = THROWING n_error
$throwable_live(S_raised,n_error)
S_raised.OBJECTS[n_error] = THROWABLE pthrowable_error
pthrowable_error.KIND = "Error"
$di_output(S_raised.EVENTS) = ptbytes_initial
$di_guard(S_raised)
S_catch_found = $di_seek(S_raised,DI_CATCH,1500)
S_catch_found.COMPLETION = NORMAL \/ S_catch_found.COMPLETION = BUDGET
S_catch = S_catch_found[.COMPLETION = NORMAL]
S_catch.TODO = (CATCH_BIND porigin_catch n_index n_error) :: ptask_catch*
$di_undefined(S_catch,$ptascii("undefinedLeft"))
S_catch.STORE[n_answer] = DEFINED (PINT 42)
$di_output(S_catch.EVENTS) = ptbytes_initial
$di_guard(S_catch)
S_end = S_catch
''')

FINISH = lines(r'''
S_final = $drive_steps(S_end,10000)
S_final.COMPLETION = NORMAL /\ S_final.TODO = eps /\ S_final.CURRENT = eps /\ S_final.FRAMES = eps
$di_output(S_final.EVENTS) = ptbytes_final
$di_guard(S_final)
S_budget = $drive_steps(S_budget_start,0)
S_budget.COMPLETION = BUDGET /\ S_budget.TODO = S_budget_start.TODO /\ S_budget.EVENTS = S_budget_start.EVENTS
$drive_steps(S_budget[.COMPLETION = NORMAL],10000) = S_final
''')

RETIRED = lines(r'''
S_retired = S[.ALLOCATIONS = $destruction_nodes_delete(S.ALLOCATIONS,[HOBJECT n_rhs])]
~$instanceof_dynamic_rhs_live(S_retired,POBJECT n_rhs)
PhpStep: S_retired ~> S_retired_done
S_retired_done.COMPLETION = UNSUPPORTED "dynamic instanceof class operand"
S_oob = S[.RESULT = KNOWN (POBJECT (|S.OBJECTS|))]
~$instanceof_dynamic_rhs_live(S_oob,POBJECT (|S.OBJECTS|))
PhpStep: S_oob ~> S_oob_done
S_oob_done.COMPLETION = UNSUPPORTED "dynamic instanceof class operand"
''')

WRONG_RHS = lines(r'''
S_name = S[.RESULT = VARIABLE ($ptascii("other")) z_rhs]
~$instanceof_dynamic_rhs_valid(S_name,S_name.RESULT)
~$call_task_valid(S_name,INSTANCEOF_DYNAMIC_CLASS poperand_left z_left)
PhpStep: S_name ~> S_name_done
S_name_done.COMPLETION = UNSUPPORTED "invalid dynamic instanceof class source"
S_line = S[.RESULT = VARIABLE n_rhs_name* $(z_rhs + 1)]
~$instanceof_dynamic_rhs_valid(S_line,S_line.RESULT)
PhpStep: S_line ~> S_line_done
S_line_done.COMPLETION = UNSUPPORTED "invalid dynamic instanceof class source"
S_source = S[.ORIGIN = eps]
~$instanceof_dynamic_site(S_source,z_left)
PhpStep: S_source ~> S_source_done
S_source_done.COMPLETION = UNSUPPORTED "invalid dynamic instanceof class source"
''')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    parser.add_argument('--case', action='append', choices=('borrowed', 'owning', 'strings', 'invalid'))
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'instanceof_dynamic_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile and data['native_gate_completed']
    assert [case['id'] for case in data['cases']] == ['borrowed', 'owning', 'strings', 'invalid']
    selected = list(data['cases'])
    assert len(selected) == 4
    if args.case:
        selected = [case for case in selected if case['id'] in args.case]
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
    out = Path(tempfile.mkdtemp(prefix='instanceof-dynamic-protocol-', dir=ROOT / '.tools'))
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
            initial_output = {'borrowed':'B:r|','owning':'T:l|r|','strings':'S:','invalid':'X:'}[name]
            setup = ['S_initial = $php_run(' + checked['fixture'] + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $di_seek(S_initial,DI_CLASS,1500)', r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]',
                     'ptbytes_initial = $ptascii(' + json.dumps(initial_output) + ')',
                     'ptbytes_final = $ptascii(' + json.dumps(output) + ')']
            reached = setup + COMMON + [f'z_left = {case["instanceof_line"]}']
            derived = []
            if name in ('borrowed','owning'):
                if name == 'borrowed':
                    reached += ['poperand_left = VARIABLE ($ptascii("left")) z_left',
                                'S_left_read = $quiet_operand(S,poperand_left)', 'S_left_read.COMPLETION = NORMAL',
                                'S_left_read.RESULT = KNOWN (POBJECT n_left)', 'n_left_owners = 2', 'b_expected = false',
                                'porigin_site = PORIGIN n_source pcpath_site', '$pool_at(S.POOLS,n_source) = (ppool_source)',
                                '$di_literal_sites(S,n_source,ppool_source.CONSTANTS) = [porigin_literal]',
                                '$compiled_read(S,porigin_literal) = (PBOOL false)', 'porigin_literal = PORIGIN n_source pcpath_literal',
                                '$code_at(S.CODE,n_source) = (pcode_source)',
                                '$code_expression(pcode_source.EXPRESSIONS,pcpath_literal ++ [PCFIELD 1]) = eps']
                else:
                    reached += ['poperand_left = KNOWN (POBJECT n_left)', 'n_left_owners = 1', 'b_expected = true']
                reached += OBJECT + (OWNING if name == 'owning' else ['S_end = S_after_result'])
                derived = RETIRED if name == 'borrowed' else []
            elif name == 'strings':
                reached += STRINGS
            else:
                reached += INVALID
                derived = WRONG_RHS
            reached += FINISH
            if name in ('borrowed','owning'):
                reached += ['~(HOBJECT n_rhs <- S_final.ALLOCATIONS)', '~(HOBJECT n_left <- S_final.ALLOCATIONS)']
            if name == 'strings':
                reached += ['S_final.AUTOLOAD = S.AUTOLOAD']
            if name == 'invalid':
                reached += ['S_final.STORE[n_answer] = DEFINED (PINT 42)']
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
