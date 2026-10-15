"""Check active virtual setter alias-write Error and abrupt assignment."""
from pathlib import Path
import argparse, base64, hashlib, json, subprocess, sys, tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import error_handler_run as recorder
from recorded_worker import Worker
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
git = lambda *parts: subprocess.check_output(['git', *parts], cwd=ROOT, env=recorder.ENV).decode().strip()

PREFIX = ('dec $avsa_replace(pcoccurrence*,pcpath,pcnode) : pcoccurrence*\n'
 'def $avsa_replace(eps,pcpath,pcnode) = eps\n'
 'def $avsa_replace((PCOCCURRENCE pcpath pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath pcnode) :: '
 'pcoccurrence*\n'
 'def $avsa_replace((PCOCCURRENCE pcpath_other pcnode_old) :: pcoccurrence*,pcpath,pcnode) = (PCOCCURRENCE pcpath_other '
 'pcnode_old) :: $avsa_replace(pcoccurrence*,pcpath,pcnode)\n'
 '  -- if pcpath_other =/= pcpath\n'
 'dec $avsa_stage(pstate,nat) : bool\n'
 'def $avsa_stage(S,0) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = (pcallcontext)\n'
 '  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n'
 '  -- if S.TODO = (ASSIGN_ARRAY pbase 8 false) :: ptask*\n'
 'def $avsa_stage(S,1) = true\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if S.CURRENT = eps\n'
 '  -- if S.TODO = (PROPERTY_PREP (NIdentifier (BYTES text_name) metadata_name) 26) :: (DIM_FETCH 26) :: ptask*\n'
 '  -- if $base64(text_name) = $ptascii("stored")\n'
 'def $avsa_stage(S,n) = false -- otherwise\n'
 'dec $avsa_seek(pstate,nat,nat) : pstate\n'
 'def $avsa_seek(S,n_stage,n) = S\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if $avsa_stage(S,n_stage) \\/ n = 0\n'
 'def $avsa_seek(S,n_stage,n) = $avsa_seek($drive_steps(S[.COMPLETION = NORMAL],1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION = NORMAL \\/ S.COMPLETION = BUDGET\n'
 '  -- if ~$avsa_stage(S,n_stage) /\\ $(n > 0)\n'
 'def $avsa_seek(S,n_stage,n) = $avsa_seek($drive_steps(S,1),n_stage,$nabs($(n - 1)))\n'
 '  -- if S.COMPLETION =/= NORMAL /\\ S.COMPLETION =/= BUDGET\n'
 '  -- if $throwable_pending(S.COMPLETION) /\\ $(n > 0)\n'
 'def $avsa_seek(S,n_stage,n) = S -- otherwise\n'
 'dec $avsa_after(pstate,pstate) : pstate\n'
 'def $avsa_after(S,S_next) = '
 '$gc_transition_owners(S,$destruction_transition_owners(S,$sensitive_trace_freeze($source_exception_transition(S,$throwable_transition(S,S_next)))))\n'
 'dec $avsa_guard(pstate) : bool\n'
 'def $avsa_guard(S) = ($call_descriptors_valid(S) /\\ $declaration_history_valid(S) /\\ $property_state_valid(S) /\\ '
 '$heap_valid($heap_prune($heap_graph(S))))\n'
 'dec $avsa_output(pevent*) : ptbytes\n'
 'def $avsa_output(eps) = eps\n'
 'def $avsa_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $avsa_output(pevent*)\n')

ERROR = ['$avsa_stage(S,0)',
 'S_global = $global_table_view(S)',
 '$lookup(S_global.ENV,$ptascii("child")) = (n_child_cell)',
 'S_global.STORE[n_child_cell] = DEFINED (POBJECT n_child)',
 '$lookup(S_global.ENV,$ptascii("result")) = (n_result_cell)',
 'S_global.STORE[n_result_cell] = DEFINED (PINT 7)',
 '$lookup(S_global.ENV,$ptascii("raw")) = (n_raw_cell)',
 'S_global.STORE[n_raw_cell] = DEFINED (PARRAY n_raw)',
 'S.ARRAYS[n_raw].ITEMS = [ENTRY (KSTRING ($ptascii("stored"))) (DIRECT (PINT 10))]',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("VirtualAliasParent78"))) = (porigin_parent)',
 '$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
 '$class_named(S.CLASSNAMES,$ptlc($ptascii("VirtualAliasChild78"))) = (porigin_child)',
 '$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
 'pclassdesc_parent.KIND = "class" /\\ pclassdesc_parent.PARENT = eps /\\ |pclassdesc_parent.PROPERTIES| = 2 /\\ '
 'pclassdesc_child.PROPERTIES = eps',
 '$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
 'ppropertydesc_stored = pclassdesc_parent.PROPERTIES[0]',
 'ppropertydesc = pclassdesc_parent.PROPERTIES[1]',
 'ppropertydesc_stored.ORIGIN = porigin_stored',
 'ppropertydesc.ORIGIN = porigin_property',
 'ppropertydesc_stored.NAME = $ptascii("stored") /\\ ppropertydesc.NAME = $ptascii("value") /\\ ppropertydesc.KEY = '
 'ppropertydesc.NAME /\\ ppropertydesc.DEFAULT = PROP_UNINITIALIZED',
 '$property_default_state(S,ppropertydesc) = (PROP_INITIAL) /\\ $property_hook_virtual(S,ppropertydesc) /\\ '
 '$property_hook_effective_origin(S,ppropertydesc) = eps',
 '$property_set_origin(S,ppropertydesc) = (porigin_hook)',
 '$function_at(S.FUNCTIONS,porigin_hook) = (pfunction_hook)',
 'pfunction_hook.NAME = $ptascii("VirtualAliasParent78::$value::set") /\\ pfunction_hook.LINE = 5 /\\ '
 'pfunction_hook.ENDLINE = 11',
 'pfunction_hook.SIGNATURE = $property_set_signature(ppropertydesc) /\\ pfunction_hook.SIGNATURE.PARAMETERS[0].NAME = '
 '$ptascii("value") /\\ pfunction_hook.SIGNATURE.PARAMETERS[0].TYPE = [PTBRANCH ([PTBUILTIN "int"])]',
 '$objectprops_at(S.OBJECTPROPS,n_child) = ([{DECL (porigin_stored), NAME ppropertydesc_stored.KEY, STATE PROP_VALUE '
 '(DIRECT (PINT 10))}])',
 'S.OBJECTS[n_child] = INSTANCE porigin_child /\\ $property_set_write_only(S,n_child,ppropertydesc.KEY)',
 'S.CURRENT = (pcallcontext_set)',
 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook_outer',
 'ppropertyhook_outer.OBJECT = n_child /\\ ppropertyhook_outer.PROPERTY = porigin_property /\\ ppropertyhook_outer.HOOK '
 '= porigin_hook /\\ ppropertyhook_outer.LINE = 20',
 'pcallcontext_set.FUNCTION = porigin_hook /\\ pcallcontext_set.RECEIVER = (n_child) /\\ pcallcontext_set.LEXICAL_CLASS '
 '= (porigin_parent) /\\ pcallcontext_set.CALLED_CLASS = (porigin_child) /\\ pcallcontext_set.CALLSITE = '
 '(ppropertyhook_outer.SITE) /\\ pcallcontext_set.LINE = 20',
 'S.FRAMES = pframe_set :: pframe_tail*',
 'pframe_set.CONTEXT = eps /\\ pframe_set.ORIGIN = (ppropertyhook_outer.SITE)',
 '$property_set_context_valid(S,pcallcontext_set) /\\ '
 '$property_set_frame(S,pcallcontext_set,pframe_set,ppropertyhook_outer)',
 'S.TODO = (ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase_receiver poperand_name z_receiver) 8 false) :: ptask_tail*',
 'S.ORIGIN = (PORIGIN n_source pcpath_site)',
 '$origin_node(S.SOURCES,PORIGIN n_source pcpath_site) = (NExprAssign expression_target (NExprVariable (BYTES '
 'text_input) metadata_input) metadata_assign)',
 '$base64(text_input) = $ptascii("value")',
 '$source_emission_cv(S,n_source,pcpath_site ++ [PCFIELD 1],NExprVariable (BYTES text_input) metadata_input)',
 'S.RESULT = VARIABLE ($ptascii("value")) z_input',
 '$lookup(S.ENV,$ptascii("value")) = (n_value_cell)',
 'S.STORE[n_value_cell] = DEFINED (PINT 20)',
 '$lookup(S.ENV,$ptascii("alias")) = (n_alias_cell)',
 'S.STORE[n_alias_cell] = DEFINED (POBJECT n_child)',
 '$property_pending_assign_valid(S,BASE_PROPERTY_PENDING pbase_receiver poperand_name z_receiver,8,false) /\\ '
 '$call_task_valid(S,ASSIGN_ARRAY (BASE_PROPERTY_PENDING pbase_receiver poperand_name z_receiver) 8 false)',
 'S_target = $property_pending_resolve(S,pbase_receiver,poperand_name,PPW,z_receiver,8)',
 'S_target.COMPLETION = NORMAL /\\ S_target.BASE = BASE_PROPERTY (POBJECT n_child) ppropertydesc.KEY',
 '$property_set_needed(S,n_child,ppropertydesc.NAME) /\\ $property_set_pending(S) /\\ '
 '$property_set_virtual_active(S,n_child,ppropertydesc) /\\ ~$property_set_backing(S,n_child,ppropertydesc)',
 '$property_set_plan(S) = eps',
 '$property_set_virtual_write_error(S) = (ppropertyhook_inner)',
 'ppropertyhook_inner = {SITE (PORIGIN n_source pcpath_site), OBJECT n_child, PROPERTY porigin_property, HOOK '
 'porigin_hook, LINE 8}',
 'ppropertyhook_inner.SITE =/= ppropertyhook_outer.SITE /\\ $property_set_valid(S,ppropertyhook_inner) /\\ '
 '$property_set_function(S,ppropertyhook_inner) = (pfunction_hook)',
 'S_rhs = $resolve_at(S_target,S.RESULT,8)',
 'S_rhs.COMPLETION = NORMAL /\\ S_rhs.RESULT = KNOWN (PINT 20) /\\ S_rhs.OBJECTPROPS = S.OBJECTPROPS /\\ S_rhs.EVENTS = '
 'S.EVENTS /\\ S_rhs.CURRENT = S.CURRENT /\\ S_rhs.FRAMES = S.FRAMES',
 '$avsa_output(S.EVENTS) = '
 '$ptascii("I:ONLY/ABSENT/10|SET:VirtualAliasParent78/VirtualAliasChild78/VirtualAliasParent78::$value::set/20|")',
 '$avsa_guard(S)',
 'ptbytes_message = $ptascii("Must not write to virtual property VirtualAliasChild78::$value")',
 'PhpStep: S ~> S_error_raw',
 'S_error_raw.COMPLETION = THROWN "Error" ptbytes_message 8 /\\ S_error_raw.TODO = ptask_tail* /\\ S_error_raw.EVENTS = '
 'S.EVENTS /\\ S_error_raw.OBJECTPROPS = S.OBJECTPROPS /\\ S_error_raw.STORE = S.STORE',
 'S_error_raw.CURRENT = S.CURRENT /\\ S_error_raw.FRAMES = S.FRAMES /\\ S_error_raw.RESULT = KNOWN (PINT 20)',
 'S_error = $avsa_after(S,S_error_raw)',
 'S_error.COMPLETION = THROWING n_error',
 '$object_name(S_error,n_error) = $ptascii("Error") /\\ $throwable_field(S_error,n_error,"message") = PSTRING '
 'ptbytes_message /\\ $throwable_field(S_error,n_error,"line") = PINT 8',
 '$objectprops_at(S_error.OBJECTPROPS,n_child) = ([{DECL (porigin_stored), NAME ppropertydesc_stored.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 10))}])',
 '$property_set_write_only(S_error,n_child,ppropertydesc.KEY) /\\ $avsa_guard(S_error)',
 'S_final_found = $avsa_seek(S_error,1,1000)',
 'S_final_found.COMPLETION = NORMAL \\/ S_final_found.COMPLETION = BUDGET',
 'S_final = S_final_found[.COMPLETION = NORMAL]',
 '$avsa_stage(S_final,1)',
 'S_final.CURRENT = eps /\\ S_final.FRAMES = eps',
 'S_final_global = $global_table_view(S_final)',
 '$lookup(S_final_global.ENV,$ptascii("result")) = (n_result_final)',
 'S_final_global.STORE[n_result_final] = DEFINED (PINT 7)',
 '$lookup(S_final_global.ENV,$ptascii("raw")) = (n_raw_final_cell)',
 'S_final_global.STORE[n_raw_final_cell] = DEFINED (PARRAY n_raw_final)',
 'S_final.ARRAYS[n_raw_final].ITEMS = [ENTRY (KSTRING ($ptascii("stored"))) (DIRECT (PINT 10))]',
 '$objectprops_at(S_final.OBJECTPROPS,n_child) = ([{DECL (porigin_stored), NAME ppropertydesc_stored.KEY, STATE '
 'PROP_VALUE (DIRECT (PINT 10))}])',
 '$property_set_write_only(S_final,n_child,ppropertydesc.KEY) /\\ $avsa_guard(S_final)',
 'PhpStep: S_final ~> S_fetch_raw',
 'S_fetch = $avsa_after(S_final,S_fetch_raw)',
 'S_fetch.COMPLETION = NORMAL /\\ S_fetch.BASE = BASE_PROPERTY (POBJECT n_child) ppropertydesc_stored.KEY /\\ '
 'S_fetch.CURRENT = eps /\\ S_fetch.FRAMES = eps',
 'PhpStep: S_fetch ~> S_read_raw',
 'S_read = $avsa_after(S_fetch,S_read_raw)',
 'S_read.COMPLETION = NORMAL /\\ S_read.RESULT = KNOWN (PINT 10) /\\ S_read.OBJECTPROPS = S_final.OBJECTPROPS /\\ '
 'S_read.CURRENT = eps /\\ S_read.FRAMES = eps',
 'S_done = $drive(S_read,1000)',
 'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps /\\ S_done.CURRENT = eps /\\ S_done.FRAMES = eps /\\ '
 '$avsa_guard(S_done)',
 '$avsa_output(S_done.EVENTS) = '
 '$ptascii("I:ONLY/ABSENT/10|SET:VirtualAliasParent78/VirtualAliasChild78/VirtualAliasParent78::$value::set/20|ERROR:Must '
 'not write to virtual property VirtualAliasChild78::$value|F:ONLY/ABSENT/10/7|")']

DERIVED = ['$property_set_virtual_write_error(S[.CURRENT = eps]) = eps',
 '$property_set_virtual_write_error(S[.FRAMES = eps]) = eps',
 '$property_set_virtual_write_error(S[.CURRENT = (pcallcontext_set[.RECEIVER = eps])]) = eps',
 '$property_set_virtual_write_error(S[.CURRENT = (pcallcontext_set[.FUNCTION = porigin_parent])]) = eps',
 '$property_set_valid(S,ppropertyhook_inner[.LINE = 9]) = false',
 'S_known = S[.RESULT = KNOWN (PINT 20)]',
 '$property_set_pending(S_known) /\\ $property_set_virtual_active(S_known,n_child,ppropertydesc) /\\ '
 '$property_set_valid(S_known,ppropertyhook_inner) /\\ $property_set_virtual_write_error(S_known) = eps',
 'S_wrong_name = S[.RESULT = VARIABLE ($ptascii("alias")) 8]',
 '$property_set_virtual_write_error(S_wrong_name) = eps',
 'S_undefined = S[.STORE[n_value_cell] = UNDEFINED]',
 '$property_set_pending(S_undefined) /\\ $property_set_virtual_active(S_undefined,n_child,ppropertydesc) /\\ '
 '$property_set_valid(S_undefined,ppropertyhook_inner) /\\ $property_set_virtual_write_error(S_undefined) = eps',
 '$source_unit(S.SOURCES,n_source) = (pcunit_source)',
 'S.SOURCES = [pcunit_source]',
 'S_leaf = S[.SOURCES = ([pcunit_source[.OCCURRENCES = $avsa_replace(pcunit_source.OCCURRENCES,pcpath_site ++ [PCFIELD '
 '1],NExprVariable (BYTES "YWxpYXM=") metadata_input)]])]',
 '$property_pending_assign_valid(S_leaf,BASE_PROPERTY_PENDING pbase_receiver poperand_name z_receiver,8,false) /\\ '
 '$property_set_valid(S_leaf,ppropertyhook_inner) /\\ $property_set_virtual_active(S_leaf,n_child,ppropertydesc)',
 '$property_set_virtual_write_error(S_leaf) = eps',
 'S_array = S[.STORE[n_value_cell] = DEFINED (PARRAY n_raw)]',
 '$typed_parameter_conversion(S_array,pfunction_hook.SIGNATURE.PARAMETERS[0],PARRAY n_raw) = TYPEREJECT',
 '$property_set_virtual_write_error(S_array) = (ppropertyhook_inner) /\\ $property_set_pending(S_array) /\\ '
 '$property_set_plan(S_array) = eps',
 'S_array_target = $property_pending_resolve(S_array,pbase_receiver,poperand_name,PPW,z_receiver,8)',
 'S_array_rhs = $resolve_at(S_array_target,S_array.RESULT,8)',
 'S_array_rhs.COMPLETION = NORMAL /\\ S_array_rhs.RESULT = KNOWN (PARRAY n_raw)',
 'PhpStep: S_array ~> S_array_error_raw',
 'S_array_error_raw.COMPLETION = THROWN "Error" ptbytes_message 8 /\\ S_array_error_raw.TODO = ptask_tail* /\\ '
 'S_array_error_raw.RESULT = KNOWN (PARRAY n_raw) /\\ S_array_error_raw.CURRENT = S_array.CURRENT /\\ '
 'S_array_error_raw.FRAMES = S_array.FRAMES /\\ S_array_error_raw.EVENTS = S_array.EVENTS /\\ '
 'S_array_error_raw.OBJECTPROPS = S_array.OBJECTPROPS']

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--group', choices=['error'], required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'active_virtual_set_alias_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = HERE / 'profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    clauses, negatives, case_index, start_stage = {
        'error': (ERROR, DERIVED, 0, 0),
    }[args.group]
    selections = [(args.group, clauses, negatives)]
    cases = [data['cases'][case_index]]
    sources = [HERE / 'active-virtual-set-alias.php']
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    assert sha(compiler) == '26d77fb9bfae2b2868e137a94051f55f9b607660c340e9b22ae8300fb0d8ce88'
    assert sha(runner) == 'b57a2ed7daf86de23993a29d079083377cfef6da133739a164dbfdb9f11fd7a0'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, *sources, profile_file, php,
               adapter, bridge, worker, runner, compiler, manifest, *modules, ROOT / 'spec/schema.json',
               ROOT / 'spec/php.watsup', ROOT / 'spec/nodes.json', ROOT / 'frontend/target.php',
               ROOT / 'frontend/wire.php', ROOT / 'frontend/wire.py',
               HERE / 'recorded_worker.py', HERE / 'static_types.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status, (revision, status)
    before = {str(path): sha(path) for path in watched}
    out = Path(tempfile.mkdtemp(prefix='active-virtual-set-alias-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = sum(len(row[2]) for row in selections)
    reached = sum(5 + len(row[1]) for row in selections)
    report = {'revision': revision, 'group': args.group, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': derived, 'reached_premises': reached, 'premises': derived + reached,
              'cap_seconds': 90, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for key, value in profile.items() for part in ('-d', key + '=' + value)]
        fixtures = []
        for i, (source, case) in enumerate(zip(sources, cases)):
            assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / ('frontend-' + str(i)))
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted'], parsed
                adapter_worker = Worker([str(adapter), str(ROOT)], out / ('adapter-' + str(i)))
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
                fixtures.append(checked['fixture'])
            finally:
                if adapter_worker:
                    adapter_worker.close()
                frontend.close()
        content = PREFIX
        for selection, ast_fixture, source, case in zip(selections, fixtures, sources, cases):
            name, clauses, negatives = selection
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET',
                     'S_found = $avsa_seek(S_initial,' + str(start_stage) + ',1000)',
                     r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
                     'S = S_found[.COMPLETION = NORMAL]']
            content += '\ndec $avsa_' + name + '() : bool\ndef $avsa_' + name + '() = true\n'
            for condition in setup + clauses + negatives:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $avsa_' + name + '() = false -- otherwise\n'
        content += '\ndec $main() : bool\ndef $main() = (' + ' /\\ '.join('$avsa_' + name + '()' for name, _, _ in selections) + ')\n'
        fixture = out / 'hook.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 90)
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 90)
            output = (out / 'state.stdout').read_bytes()
            evaluated = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(evaluated)
            passed = evaluated and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(path): sha(path) for path in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[key] for key in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({key: report[key] for key in ('passed', 'application_evaluations', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']


if __name__ == '__main__':
    main()
