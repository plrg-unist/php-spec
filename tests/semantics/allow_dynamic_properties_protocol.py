"""Prepare reached permitted writes and source-backed class permission checks."""
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
dec $adp_stage(pstate, ptbytes, int) : bool
def $adp_stage(S, ptbytes, z_value) = true
  -- if S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask*
  -- if S.ORIGIN = (porigin)
  -- if $origin_node(S.SOURCES, porigin) = (NExprAssign (NExprPropertyFetch (NExprVariable (BYTES text) metadata_receiver) (NIdentifier (BYTES text_key) metadata_name) metadata_target) expression_rhs metadata)
  -- if $base64(text) = ptbytes /\ $base64(text_key) = $ptascii("extra")
  -- if S.RESULT = KNOWN (PINT z_value)
def $adp_stage(S, ptbytes, z) = false -- otherwise
dec $adp_seek(pstate, ptbytes, int, nat) : pstate
def $adp_seek(S, ptbytes, z, n) = S
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if $adp_stage(S, ptbytes, z) \/ n = 0
def $adp_seek(S, ptbytes, z, n) = $adp_seek($drive_steps(S[.COMPLETION = NORMAL], 1), ptbytes, z, $nabs($(n - 1)))
  -- if S.COMPLETION = NORMAL \/ S.COMPLETION = BUDGET
  -- if ~$adp_stage(S, ptbytes, z) /\ $(n > 0)
def $adp_seek(S, ptbytes, z, n) = $adp_seek($drive_steps(S, 1), ptbytes, z, $nabs($(n - 1)))
  -- if S.COMPLETION =/= NORMAL /\ S.COMPLETION =/= BUDGET
  -- if $throwable_pending(S.COMPLETION) /\ $(n > 0)
def $adp_seek(S, ptbytes, z, n) = S -- otherwise
dec $adp_after(pstate, pstate) : pstate
def $adp_after(S, S_next) = $gc_transition_owners(S, $destruction_transition_owners(S, $sensitive_trace_freeze($source_exception_transition(S, $throwable_transition(S, S_next)))))
dec $adp_guard(pstate) : bool
def $adp_guard(S) = ($call_descriptors_valid(S) /\ $declaration_history_valid(S) /\ $property_state_valid(S) /\ $heap_valid($heap_prune($heap_graph(S))))
dec $adp_output(pevent*) : ptbytes
def $adp_output(eps) = eps
def $adp_output((OUTPUT ptbytes) :: pevent*) = ptbytes ++ $adp_output(pevent*)
dec $adp_classes(pclassdesc*, pclassdesc) : pclassdesc*
def $adp_classes(eps, pclassdesc_new) = eps
def $adp_classes(pclassdesc :: pclassdesc_tail*, pclassdesc_new) = pclassdesc_new :: pclassdesc_tail*
  -- if pclassdesc.ORIGIN = pclassdesc_new.ORIGIN
def $adp_classes(pclassdesc :: pclassdesc_tail*, pclassdesc_new) = pclassdesc :: $adp_classes(pclassdesc_tail*, pclassdesc_new)
  -- if pclassdesc.ORIGIN =/= pclassdesc_new.ORIGIN
dec $adp_names(pcodename*, pcpath, ptbytes) : pcodename*
def $adp_names(eps, pcpath, ptbytes) = eps
def $adp_names((CODENAME pcpath ptbytes_old ptbytes_fallback?) :: pcodename_tail*, pcpath, ptbytes_new) = (CODENAME pcpath ptbytes_new eps) :: pcodename_tail*
def $adp_names((CODENAME pcpath_other ptbytes_old ptbytes_fallback?) :: pcodename_tail*, pcpath, ptbytes_new) = (CODENAME pcpath_other ptbytes_old ptbytes_fallback?) :: $adp_names(pcodename_tail*, pcpath, ptbytes_new)
  -- if pcpath_other =/= pcpath
dec $adp_codes(pcode*, pcode) : pcode*
def $adp_codes(eps, pcode_new) = eps
def $adp_codes(pcode :: pcode_tail*, pcode_new) = pcode_new :: pcode_tail*
  -- if pcode.UNIT = pcode_new.UNIT
def $adp_codes(pcode :: pcode_tail*, pcode_new) = pcode :: $adp_codes(pcode_tail*, pcode_new)
  -- if pcode.UNIT =/= pcode_new.UNIT
dec $adp_header_error(pchresult) : bool
def $adp_header_error(PCHERROR pchdiagnostic*) = true
def $adp_header_error(pchresult) = false -- otherwise
dec $adp_no_keyword(metadata) : metadata
def $adp_no_keyword(eps) = eps
def $adp_no_keyword((MclassKeywordLine z) :: metadataEntry_tail*) = $adp_no_keyword(metadataEntry_tail*)
def $adp_no_keyword(metadataEntry :: metadataEntry_tail*) = metadataEntry :: $adp_no_keyword(metadataEntry_tail*)
  -- if $class_keyword_item(metadataEntry) = eps
dec $adp_split_statement(program) : statement
def $adp_split_statement(PROGRAM ([statement_before, statement])) = statement
'''

OWN_PRE = [
    r'S_plain_found = $adp_seek(S_initial,$ptascii("plain"),7,1000)',
    r'S_plain_found.COMPLETION = NORMAL \/ S_plain_found.COMPLETION = BUDGET',
    r'S_plain = S_plain_found[.COMPLETION = NORMAL]',
    r'$adp_stage(S_plain,$ptascii("plain"),7) /\ $adp_guard(S_plain)',
    r'$lookup(S_plain.ENV,$ptascii("plain")) = (n_plain_cell)',
    r'S_plain.STORE[n_plain_cell] = DEFINED (POBJECT n_plain)',
    r'S_plain.OBJECTS[n_plain] = INSTANCE porigin_plain',
    r'~$class_allows_dynamic(S_plain,porigin_plain,|S_plain.CLASSES|)',
    r'S_plain.TODO = (ASSIGN_ARRAY pbase_plain z_plain false) :: ptask_plain*',
    r'$property_dynamic_capture(S_plain,pbase_plain,z_plain,false) = (pdynamicproperty)',
    r'$property_dynamic_valid(S_plain,pdynamicproperty) /\ $property_dynamic_warning_pending(S_plain)',
    r'pdynamicproperty.TARGET = n_plain /\ pdynamicproperty.RHS = KNOWN (PINT 7) /\ ~pdynamicproperty.RETIRED /\ pdynamicproperty.PENDING = eps',
    r'S_found = $adp_seek(S_plain,$ptascii("allowed"),17,1000)',
    r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
    r'S = S_found[.COMPLETION = NORMAL]',
    r'$adp_stage(S,$ptascii("allowed"),17) /\ $adp_guard(S)',
    r'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*',
    r'$lookup(S.ENV,$ptascii("allowed")) = (n_cell)',
    r'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
    r'S.OBJECTS[n_object] = INSTANCE porigin_class',
    r'$class_named(S.CLASSNAMES,$ptascii("dynamicallowed27")) = (porigin_class)',
    r'$class_at(S.CLASSES,porigin_class) = (pclassdesc)',
    r'porigin_class = PORIGIN n_unit pcpath_class',
    r'$source_unit(S.SOURCES,n_unit) = (pcunit)',
    r'pcunit = $pcsource(n_unit,pcunit.AST)',
    r'$origin_node(S.SOURCES,porigin_class) = (statement)',
    r'$pchlower(statement) = PCHRAW pchraw',
    r'ptcontext = {NAMESPACE eps, IMPORTS eps, SCOPE PTGLOBAL, POSITION PTCONSTANT, OWNER eps, MEMBER eps, FILE ($ptascii("fixture.php")), LINE pclassdesc.LINE}',
    r'$pchstart(PCHRAW pchraw,false,ptcontext) = PCHOK pchheader eps',
    r'pchraw.ATTRIBUTES = SEQUENCE ([(NAttributeGroup (SEQUENCE ([(NAttribute name (SEQUENCE eps) metadata_attribute)])) metadata_group)])',
    r'$code_at(S.CODE,n_unit) = (pcode)',
    r'pcpath_attribute = pcpath_class ++ [PCFIELD 0,PCINDEX 0,PCFIELD 0,PCINDEX 0,PCFIELD 0]',
    r'$code_name(pcode.NAMES,pcpath_attribute) = (($ptascii("AllowDynamicProperties"),eps))',
    r'$class_dynamic_attribute(S,porigin_class) /\ $class_allows_dynamic(S,porigin_class,|S.CLASSES|)',
    r'~$class_allows_dynamic(S,porigin_plain,|S.CLASSES|)',
    r'$property_dynamic_capture(S,pbase,z,false) = eps /\ ~$property_dynamic_warning_pending(S)',
    r'$objectprops_at(S.OBJECTPROPS,n_object) = (eps)',
    r'$node_children(S,HOBJECT n_object) = eps',
    r'$( $heap_owners($heap_prune($heap_graph(S)),HOBJECT n_object) > 0 )',
]
OWN_DERIVED = [
    r'~$class_allows_dynamic(S,porigin_class,0)',
    r'~$class_dynamic_attribute(S[.CLASSNAMES = eps],porigin_class)',
    r'~$class_dynamic_attribute(S[.CLASSES = eps],porigin_class)',
    r'~$class_dynamic_attribute(S[.SOURCES = eps],porigin_class)',
    r'~$class_dynamic_attribute(S[.CODE = eps],porigin_class)',
    r'~$class_dynamic_attribute(S,PORIGIN n_unit eps)',
    r'~$class_dynamic_attribute(S[.CLASSES = $adp_classes(S.CLASSES,pclassdesc[.READONLY = true])],porigin_class)',
    r'~$class_dynamic_attribute(S[.CLASSES = $adp_classes(S.CLASSES,pclassdesc[.NAME = $ptascii("DynamicPlain27")])],porigin_class)',
    r'pcode_bad = pcode[.NAMES = $adp_names(pcode.NAMES,pcpath_attribute,$ptascii("OtherAttribute27"))]',
    r'S_bad = S[.CODE = $adp_codes(S.CODE,pcode_bad)]',
    r'$code_name(pcode_bad.NAMES,pcpath_attribute) = (($ptascii("OtherAttribute27"),eps))',
    r'~$class_dynamic_attribute(S_bad,porigin_class)',
    r'~$declaration_history_valid(S_bad) /\ ~$adp_guard(S_bad)',
    r'S_rejected = $declaration_entry_check(S_bad)',
    r'S_rejected.COMPLETION = UNSUPPORTED "invalid declaration publication history" /\ S_rejected.TODO = eps',
    r'$heap_graph(S_bad) = $heap_graph(S) /\ S_bad.SOURCES = S.SOURCES /\ S_bad.CLASSES = S.CLASSES /\ S_bad.CLASSNAMES = S.CLASSNAMES',
    r'~$pchallows_dynamic(ptcontext,SEQUENCE eps)',
    r'~$pchallows_dynamic(ptcontext,SEQUENCE ([(NAttributeGroup (SEQUENCE ([(NAttribute name (SEQUENCE ([(NArg ABSENT (NScalarInt (INTEGER 1) eps) (BOOLEAN false) (BOOLEAN false) eps)])) metadata_attribute)])) metadata_group)]))',
    r'~$pchallows_dynamic(ptcontext,SEQUENCE ([(NAttributeGroup (SEQUENCE ([(NAttribute name (SEQUENCE eps) metadata_attribute),(NAttribute name (SEQUENCE eps) metadata_attribute)])) metadata_group)]))',
    r'~$pchallows_dynamic(ptcontext,SEQUENCE ([(NAttributeGroup (SEQUENCE ([(NAttribute name (SEQUENCE eps) metadata_attribute)])) metadata_group),(NAttributeGroup (SEQUENCE ([(NAttribute name (SEQUENCE eps) metadata_attribute)])) metadata_group)]))',
    r'~$pchallows_dynamic(ptcontext[.NAMESPACE = $ptascii("User27")],SEQUENCE ([(NAttributeGroup (SEQUENCE ([(NAttribute (NName (BYTES "QWxsb3dEeW5hbWljUHJvcGVydGllcw==") metadata_attribute) (SEQUENCE eps) metadata_attribute)])) metadata_group)]))',
    r'$adp_header_error($pchattributes(pchraw[.KIND = "trait"],pchheader[.KIND = "trait"],ptcontext))',
    r'$adp_header_error($pchattributes(pchraw[.KIND = "interface"],pchheader[.KIND = "interface"],ptcontext))',
    r'$adp_header_error($pchattributes(pchraw[.FLAGS = 64],pchheader[.READONLY = true],ptcontext))',
]
OWN_POST = [
    r'PhpStep: S ~> S_raw',
    r'S_raw.COMPLETION = NORMAL /\ S_raw.TODO = ptask_tail* /\ S_raw.RESULT = KNOWN (PINT 17)',
    r'$objectprops_record_at(S_raw.OBJECTPROPS,n_object) = (pobjectprops_new)',
    r'pobjectprops_new.MATERIALIZED /\ pobjectprops_new.SLOTS = [{DECL eps,NAME ($ptascii("extra")),STATE PROP_VALUE (DIRECT (PINT 17))}]',
    r'S_raw.OBJECTS = S.OBJECTS /\ S_raw.ARRAYS = S.ARRAYS /\ S_raw.STORE = S.STORE /\ S_raw.ENV = S.ENV',
    r'S_raw.EVENTS = S.EVENTS /\ S_raw.ALLOCATIONS = S.ALLOCATIONS /\ S_raw.SOURCES = S.SOURCES /\ S_raw.CODE = S.CODE',
    r'$node_children(S_raw,HOBJECT n_object) = eps',
    r'S_ready = $adp_after(S,S_raw)',
    r'$adp_guard(S_ready)',
    r'S_repeat_found = $adp_seek(S_ready,$ptascii("allowed"),19,1000)',
    r'S_repeat_found.COMPLETION = NORMAL \/ S_repeat_found.COMPLETION = BUDGET',
    r'S_repeat = S_repeat_found[.COMPLETION = NORMAL]',
    r'$adp_stage(S_repeat,$ptascii("allowed"),19) /\ $adp_guard(S_repeat)',
    r'$objectprops_at(S_repeat.OBJECTPROPS,n_object) = ([{DECL eps,NAME ($ptascii("extra")),STATE PROP_VALUE (DIRECT (PINT 17))}])',
    r'~$property_dynamic_warning_pending(S_repeat)',
    r'PhpStep: S_repeat ~> S_repeat_raw',
    r'S_repeat_raw.COMPLETION = NORMAL /\ S_repeat_raw.EVENTS = S_repeat.EVENTS /\ S_repeat_raw.ALLOCATIONS = S_repeat.ALLOCATIONS',
    r'$objectprops_at(S_repeat_raw.OBJECTPROPS,n_object) = ([{DECL eps,NAME ($ptascii("extra")),STATE PROP_VALUE (DIRECT (PINT 19))}])',
    r'S_repeat_ready = $adp_after(S_repeat,S_repeat_raw)',
    r'$adp_guard(S_repeat_ready)',
    r'S_done = $drive_steps(S_repeat_ready,2048)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
    r'$adp_output(S_done.EVENTS) = $ptascii("W|Creation of dynamic property DynamicPlain27::$extra is deprecated|P9|A19|") /\ $adp_guard(S_done)',
]
INHERITED = [
    r'S_found = $adp_seek(S_initial,$ptascii("grandchild"),9,1000)',
    r'S_found.COMPLETION = NORMAL \/ S_found.COMPLETION = BUDGET',
    r'S = S_found[.COMPLETION = NORMAL]',
    r'$adp_stage(S,$ptascii("grandchild"),9) /\ $adp_guard(S)',
    r'S.TODO = (ASSIGN_ARRAY pbase z false) :: ptask_tail*',
    r'$lookup(S.ENV,$ptascii("grandchild")) = (n_cell)',
    r'S.STORE[n_cell] = DEFINED (POBJECT n_object)',
    r'S.OBJECTS[n_object] = INSTANCE porigin_grand',
    r'$class_at(S.CLASSES,porigin_grand) = (pclassdesc_grand)',
    r'$class_named(S.CLASSNAMES,$ptascii("dynamicscope27") ++ [92] ++ $ptascii("grandchild27")) = (porigin_grand)',
    r'$class_link_at(S.LINKEDPARENTS,porigin_grand) = (SOURCE_PARENT porigin_child)',
    r'$class_at(S.CLASSES,porigin_child) = (pclassdesc_child)',
    r'$class_link_at(S.LINKEDPARENTS,porigin_child) = (SOURCE_PARENT porigin_parent)',
    r'$class_at(S.CLASSES,porigin_parent) = (pclassdesc_parent)',
    r'$class_dynamic_attribute(S,porigin_parent)',
    r'~$class_dynamic_attribute(S,porigin_child) /\ ~$class_dynamic_attribute(S,porigin_grand)',
    r'$class_allows_dynamic(S,porigin_child,|S.CLASSES|) /\ $class_allows_dynamic(S,porigin_grand,|S.CLASSES|)',
    r'$objectprops_at(S.OBJECTPROPS,n_object) = (eps)',
    r'$property_dynamic_capture(S,pbase,z,false) = eps /\ ~$property_dynamic_warning_pending(S)',
    r'PhpStep: S ~> S_raw',
    r'S_raw.COMPLETION = NORMAL /\ S_raw.TODO = ptask_tail* /\ S_raw.RESULT = KNOWN (PINT 9)',
    r'$objectprops_at(S_raw.OBJECTPROPS,n_object) = ([{DECL eps,NAME ($ptascii("extra")),STATE PROP_VALUE (DIRECT (PINT 9))}])',
    r'S_raw.EVENTS = S.EVENTS /\ S_raw.ALLOCATIONS = S.ALLOCATIONS /\ S_raw.OBJECTS = S.OBJECTS /\ S_raw.STORE = S.STORE /\ S_raw.ARRAYS = S.ARRAYS',
    r'S_ready = $adp_after(S,S_raw)',
    r'$adp_guard(S_ready)',
    r'S_done = $drive_steps(S_ready,2048)',
    r'S_done.COMPLETION = NORMAL /\ S_done.TODO = eps /\ S_done.CURRENT = eps /\ S_done.FRAMES = eps',
    r'$adp_output(S_done.EVENTS) = $ptascii("7|9|") /\ $adp_guard(S_done)',
]
INHERITED_DERIVED = [
    r'~$class_allows_dynamic(S[.LINKEDPARENTS = eps],porigin_grand,|S.CLASSES|)',
    r'~$class_allows_dynamic(S[.CLASSNAMES = eps],porigin_grand,|S.CLASSES|)',
    r'~$class_allows_dynamic(S,porigin_grand,1)',
    r'~$class_dynamic_parent(S,pclassdesc_grand[.PARENT = ($ptascii("OtherParent27"))],|S.CLASSES|)',
]
LINES = [
    r'statement = $adp_split_statement(SPLIT_PROGRAM)',
    r'statement = NStmtTrait phpType14 (NIdentifier (BYTES text_name) metadata_name) phpType23 metadata',
    r'$source_line(metadata) = 3 /\ $source_line(metadata_name) = 7',
    r'$class_header_line(metadata,NIdentifier (BYTES text_name) metadata_name,phpType14) = 6',
    r'$class_header_line($adp_no_keyword(metadata),NIdentifier (BYTES text_name) metadata_name,phpType14) = 0',
    r'$class_header_line((MclassKeywordLine 6) :: metadata,NIdentifier (BYTES text_name) metadata_name,phpType14) = 0',
    r'$class_header_line((MclassKeywordLine 2) :: $adp_no_keyword(metadata),NIdentifier (BYTES text_name) metadata_name,phpType14) = 0',
    r'$class_header_line((MclassKeywordLine 8) :: $adp_no_keyword(metadata),NIdentifier (BYTES text_name) metadata_name,phpType14) = 0',
    r'$class_header_line(metadata,NIdentifier (BYTES text_name) metadata_name,SEQUENCE eps) = 3',
]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--revision', required=True)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    recorder.ROOT = ROOT
    catalogue = HERE / 'allow_dynamic_properties_cases.json'
    data = json.loads(catalogue.read_bytes())
    profile_file = ROOT / 'tests/semantics/profile.json'
    profile = json.loads(profile_file.read_bytes())
    assert data['native_profile'] == profile
    sources = [HERE / ('allow-dynamic-properties-' + name + '.php') for name in ('own', 'inherited', 'split')]
    names = ['annotated-vs-ordinary', 'inherited-namespace-alias', 'split-keyword-name']
    for name, source in zip(names, sources):
        case = next(row for row in data['cases'] if row['id'] == name)
        assert source.read_bytes() == case['source'].encode() and sha(source) == case['source_sha256']
    php, adapter, bridge, worker, runner, compiler = (ROOT / name for name in [
        '.tools/php/bin/php', '_build/default/adapter/main.exe', '.tools/php-file.so',
        'frontend/worker.php', 'tests/semantics/_build/default/numeric_runner.exe', '.tools/spectec/bin/p4spectec'])
    assert sha(php) == 'b9adb7babbb8d7619a8e049cfb73369b40d8a72be6918d5b0de4c77509e05398'
    manifest = ROOT / 'spec/semantics/modules.json'
    modules = [ROOT / name for name in json.loads(manifest.read_bytes())]
    watched = [Path(__file__), Path(recorder.__file__), catalogue, *sources, profile_file, php,
               adapter, bridge, worker, runner, compiler, manifest, *modules,
               ROOT / 'spec/schema.json', ROOT / 'tests/semantics/recorded_worker.py']
    revision, status = git('rev-parse', 'HEAD'), git('status', '--short')
    assert revision == args.revision and not status
    before = {str(p): sha(p) for p in watched}
    out = Path(tempfile.mkdtemp(prefix='allow-dynamic-protocol-', dir=ROOT / '.tools'))
    print(out, flush=True)
    derived = len(OWN_DERIVED) + len(INHERITED_DERIVED) + len(LINES)
    reached = 4 + len(OWN_PRE) + len(OWN_POST) + len(INHERITED)
    report = {'revision': revision, 'inputs': before, 'profile': profile, 'module_count': len(modules),
              'mode': 'SL', 'cache': False, 'det': True, 'evaluated': False, 'records': [],
              'application_invocations': 0, 'application_evaluations': 0, 'source_agreements': 0,
              'derived_premises': derived, 'reached_premises': reached,
              'budget_seconds': 120, 'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'jobs': 1}, 'passed': False}
    fixture = None
    try:
        flags = [part for k, v in profile.items() for part in ('-d', k + '=' + v)]
        fixtures = []
        for i, source in enumerate(sources):
            frontend = Worker([str(php), '-n', *flags, '-d', 'extension=' + str(bridge), str(worker)], out / ('frontend-' + str(i)))
            adapter_worker = None
            try:
                parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
                assert parsed['accepted']
                adapter_worker = Worker([str(adapter), str(ROOT)], out / ('adapter-' + str(i)))
                checked = adapter_worker.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
                assert checked['ok'] and checked['ast'] == parsed['ast']
                fixtures.append(checked['fixture'])
            finally:
                if adapter_worker: adapter_worker.close()
                frontend.close()
        content = PREFIX
        for name, ast_fixture, source, clauses in [('own', fixtures[0], sources[0], OWN_PRE + OWN_DERIVED + OWN_POST),
                                                   ('inherited', fixtures[1], sources[1], INHERITED + INHERITED_DERIVED)]:
            setup = ['S_initial = $php_run(' + ast_fixture + ',0,' + json.dumps(base64.b64encode(str(source).encode()).decode()) + ')',
                     r'S_initial.COMPLETION = NORMAL \/ S_initial.COMPLETION = BUDGET']
            content += '\ndec $adp_' + name + '() : bool\ndef $adp_' + name + '() = true\n'
            for condition in setup + clauses:
                content += '  -- ' + ('' if condition.startswith('PhpStep:') else 'if ') + condition + '\n'
            content += 'def $adp_' + name + '() = false -- otherwise\n'
        content += '\ndec $adp_lines() : bool\ndef $adp_lines() = true\n'
        for condition in LINES:
            content += '  -- if ' + condition.replace('SPLIT_PROGRAM', fixtures[2]) + '\n'
        content += 'def $adp_lines() = false -- otherwise\n\ndec $main() : bool\ndef $main() = ($adp_own() /\\ $adp_inherited() /\\ $adp_lines())\n'
        fixture = out / 'permission.watsup'
        fixture.write_text(content)
        report.update(fixture=str(fixture), fixture_sha256=sha(fixture), prepared=True, passed=True)
        if not args.prepare_only:
            process = recorder.recorded([str(compiler), 'algo', *map(str, modules), str(fixture)], out / 'compiler', 120)
            main_present = b'\ndef $main : bool =\n' in (out / 'compiler.stdout').read_bytes()
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'compiler.stderr').read_bytes() and main_present
            report['records'].append({'id': 'algorithmic-compilation', 'process': process, 'passed': passed, 'main_present': main_present, 'application_evaluations': 0})
            report['passed'] = passed
            assert passed
            report['application_invocations'] = 1
            process = recorder.recorded([str(runner), '--sl', *map(str, modules), str(fixture)], out / 'state', 120)
            output = (out / 'state.stdout').read_bytes()
            report['evaluated'] = process['exit'] == 0 and output in (b'true\n', b'false\n')
            report['application_evaluations'] = int(report['evaluated'])
            passed = process['exit'] == 0 and not process['timeout'] and not process['group_after'] and not (out / 'state.stderr').read_bytes() and output == b'true\n'
            report['records'].append({'id': 'strict-SL-application', 'process': process, 'passed': passed})
            report['passed'] = passed
    finally:
        report.update(inputs_stable=before == {str(p): sha(p) for p in watched},
                      fixture_stable=fixture is None or report['fixture_sha256'] == sha(fixture),
                      head_stable=revision == git('rev-parse', 'HEAD'), status_stable=status == git('status', '--short'))
        report['passed'] = report['passed'] and all(report[k] for k in ('inputs_stable', 'fixture_stable', 'head_stable', 'status_stable'))
        (out / ('PREPARED.json' if args.prepare_only else 'report.json')).write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: report[k] for k in ('passed', 'evaluated', 'derived_premises', 'reached_premises', 'inputs_stable', 'head_stable', 'status_stable')}), flush=True)
    assert report['passed']

if __name__ == '__main__':
    main()
