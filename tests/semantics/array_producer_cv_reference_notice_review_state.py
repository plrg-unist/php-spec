#!/usr/bin/env python3
"""Ground required array BYVAL reception at a named producer reference Notice."""
import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess

import class_negative_int_constant_alias_stdclass_reference_notice_review_state as prior
import error_handler_run as recorder
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
CATALOGUE = Path(__file__).with_name('array_producer_cv_reference_notice_review_cases.json')
PREFIX = (prior.PREFIX.replace('A:-13:19;', 'A:-17:23;M;')
    .replace('ReviewMixedNegativeConstant29', r'ReviewNotice32\\Primary\\ReviewMixedArray32')
    .replace('"take"', r'"ReviewNotice32\\Primary\\take"')
    .replace('"h"', r'"ReviewNotice32\\Primary\\h"'))

REACHED = r'''
S_initial.COMPLETION = BUDGET
S_pre = $sopn_seek(S_initial, 1536)[.COMPLETION = NORMAL]
$sopn_ready(S_pre)
S_pre.CURRENT = eps
S_pre.TODO = (NAMED_SEND pcalltarget eps 0 pnamedargs (porigin_call) z_call) :: ptask_tail*
S_pre.RESULT = KNOWN (PARRAY n_root)
$named_origin(S_pre, (porigin_call), 0) = (porigin_argument)
porigin_argument = PORIGIN n_unit pcpath_argument
$exit_fixed(S_pre, porigin_argument) = ((preqbytes, preqbytes_fallback?))
preqbytes = $ptascii("ReviewNotice32\\Primary\\make")
preqbytes_fallback? =/= eps
preqbytes_fallback? = ($ptascii("make"))
$call_target(S_pre, preqbytes, eps) = (pfunction_producer)
pfunction_producer.ORIGIN = PORIGIN n_unit pcpath_producer
pfunction_producer.NAME = preqbytes /\ pfunction_producer.EARLY
$call_target(S_pre, $ptascii("make"), eps) = (pfunction_global)
pfunction_global.ORIGIN =/= pfunction_producer.ORIGIN
$origin_node(S_pre.SOURCES, pfunction_producer.ORIGIN) = (NStmtFunction (SEQUENCE eps) (BOOLEAN false) phpType11 phpType16 phpType18 phpType23 metadata_function)
pfunction_producer.SIGNATURE.PARAMETERS = [psparam]
psparam.REQUIRED /\ ~psparam.BYREF /\ psparam.TYPE = [(PTBRANCH ([PTBUILTIN "array"]))] /\ ~psparam.VARIADIC /\ psparam.DEFAULT = PSNONE
~pfunction_producer.SIGNATURE.BYREF /\ pfunction_producer.SIGNATURE.RETURNS = eps
~$function_generator(S_pre, pfunction_producer)
phpType16 = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter])
$ptlc($base64(text_type)) = $ptascii("array")
$named_expression($named_source(S_pre, (porigin_call), 0)) = NExprFuncCall phpType19_producer phpType6_producer metadata_producer_call
$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE)
S_pre.PARAMETERBACKINGS = eps /\ S_pre.CONTAINERINITS = eps
(PDEFUNCTION n_unit pfunction_producer.ORIGIN) <- S_pre.DECLARATIONS
$declaration_early(S_pre.DECLARATIONS, pfunction_producer.ORIGIN, PPFUNCTION)
$declaration_history_valid(S_pre)
$reference_notice_producer_target(S_pre, porigin_argument) = (pfunction_producer)
$named_reference_notice_source(S_pre, pcalltarget, 0, (porigin_call))
$lookup(S_pre.ENV, $ptascii("leaf")) = (n_leaf)
$lookup(S_pre.ENV, $ptascii("owner")) = (n_owner_cv)
$lookup(S_pre.ENV, $ptascii("new")) = (n_new_cv)
S_pre.STORE[n_leaf] = DEFINED (POBJECT n_old)
S_pre.STORE[n_owner_cv] = DEFINED (POBJECT n_owner)
S_pre.STORE[n_new_cv] = DEFINED (POBJECT n_new)
S_pre.ARRAYS[n_root].ITEMS = [ENTRY (KSTRING ($ptascii("leaf"))) (ALIAS n_leaf)]
$propref_at(S_pre.PROPREFS, n_leaf) = (ppropref)
ppropref.SOURCES = [OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p, CLASS_PROP_SOURCE ppropertyid_s]
$node_children(S_pre, HOBJECT n_owner) = [HOBJECT n_old, HCELL n_leaf, HOBJECT n_old]
$node_children(S_pre, HCELL n_leaf) = [HOBJECT n_old]
H_pre = $heap_graph(S_pre)
H_pre = $heap_graph(S_pre[.PROPREFS = eps])
$heap_owners(H_pre, HARRAY n_root) = 3 /\ $heap_owners(H_pre, HCELL n_leaf) = 4
$heap_valid(H_pre) /\ $call_descriptors_valid(S_pre)
$named_reference_notice_array(S_pre, PARRAY n_root)
$named_reference_notice_pending(S_pre)
n_private = |S_pre.STORE|
S_step = $drive(S_pre, 1)
S_step.COMPLETION = BUDGET
S_notice = S_step[.COMPLETION = NORMAL]
S_notice.TODO = (ERROR_HANDLER_INVOKE perrorcall) :: ptask_tail*
perrorcall.RESUME = NAMED_ARGS pcalltarget eps 1 pnamedargs_after (porigin_call) z_call
pnamedargs_after.SLOTS = [NAMED_SENT (REFERENCE n_private)]
S_notice.STORE[n_private] = DEFINED (PARRAY n_root)
n_private <- S_notice.REFCELLS /\ (HCELL n_private) <- S_notice.ALLOCATIONS
$propref_at(S_notice.PROPREFS, n_private) = eps
$task_nodes(perrorcall.RESUME) = [HCELL n_private]
$node_children(S_notice, HCELL n_private) = [HARRAY n_root]
S_notice.HELD = S_pre.HELD /\ S_notice.DECLARATIONS = S_pre.DECLARATIONS
H_notice = $heap_graph(S_notice)
$heap_owners(H_notice, HCELL n_private) = 1 /\ $heap_owners(H_notice, HARRAY n_root) = 3
$heap_valid(H_notice) /\ $error_call_valid(S_notice, perrorcall)
S_returned = $sopn_after(S_notice, 2, 1536)[.COMPLETION = NORMAL]
$sopn_stage(S_returned, 2)
S_returned.RESULT = REFERENCE n_private
S_returned.STORE[n_private] = DEFINED (PARRAY n_copied)
n_copied =/= n_root
$lookup(S_returned.ENV, $ptascii("leaf")) = eps
S_returned.STORE[n_leaf] = DEFINED (POBJECT n_new)
S_returned.ARRAYS[n_root].ITEMS = S_pre.ARRAYS[n_root].ITEMS
S_returned.ARRAYS[n_copied].ITEMS = S_pre.ARRAYS[n_root].ITEMS ++ [ENTRY (KSTRING ($ptascii("tag"))) (DIRECT (PINT 9))]
$propref_at(S_returned.PROPREFS, n_leaf) = ({CELL n_leaf, SOURCES ([CLASS_PROP_SOURCE ppropertyid_s, OBJECT_PROP_SOURCE n_owner ($ptascii("p")) ppropertyid_p])})
H_returned = $heap_graph(S_returned)
$heap_owners(H_returned, HARRAY n_root) = 2 /\ $heap_owners(H_returned, HARRAY n_copied) = 1
$heap_owners(H_returned, HCELL n_leaf) = 4 /\ $heap_owners(H_returned, HCELL n_private) = 1
$heap_valid(H_returned) /\ $call_descriptors_valid(S_returned)
'''.strip().splitlines()

CONTROLS = r'''
S_no_publication = S_pre[.DECLARATIONS = eps]
$call_target(S_no_publication, preqbytes, eps) = (pfunction_producer)
$reference_notice_producer_target(S_no_publication, porigin_argument) = eps
~$named_reference_notice_pending(S_no_publication)
~$declaration_history_valid(S_no_publication)
$heap_graph(S_no_publication) = H_pre
S_wrong_publication = S_pre[.DECLARATIONS = [PDEFUNCTION n_unit (PORIGIN n_unit (pcpath_producer ++ [PCINDEX 999]))]]
$reference_notice_producer_target(S_wrong_publication, porigin_argument) = eps
~$named_reference_notice_pending(S_wrong_publication)
~$declaration_history_valid(S_wrong_publication)
$heap_graph(S_wrong_publication) = H_pre
S_runtime_publication = S_pre[.DECLARATIONS = [PDRFUNCTION pfunction_producer.ORIGIN {UNIT n_unit, CALLS eps, AUTOLOAD eps}]]
$call_target(S_runtime_publication, preqbytes, eps) = (pfunction_producer)
$reference_notice_producer_target(S_runtime_publication, porigin_argument) = eps
~$named_reference_notice_pending(S_runtime_publication)
$heap_graph(S_runtime_publication) = H_pre
~$error_call_valid(S_notice, perrorcall[.RESUME = NAMED_ARGS pcalltarget eps 1 {SLOTS ([NAMED_SENT (KNOWN (PARRAY n_root))]), NAMED eps} (porigin_call) z_call])
~$error_call_valid(S_notice, perrorcall[.LINE = $(perrorcall.LINE + 1)])
S_zero = $drive(S_notice, 0)
S_zero.COMPLETION = BUDGET /\ S_zero[.COMPLETION = NORMAL] = S_notice
S_one = $drive(S_zero[.COMPLETION = NORMAL], 1)
S_two = $drive(S_one[.COMPLETION = NORMAL], 1)
S_two = $drive(S_notice, 2)
'''.strip().splitlines()

CONTROLS += r'''
$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "QVJSQVk=") metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES "aW50") metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = [(PTBRANCH ([PTBUILTIN "mixed"]))]]]])
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])
$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN true) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.BYREF = true]]])
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.REQUIRED = false]]])
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.VARIADIC = true]]])
~$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN true) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.VARIADIC = true]]])
~$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) (NIdentifier (BYTES text_type) metadata_type) (BOOLEAN false) (BOOLEAN false) phpType10 (NExprArray (SEQUENCE eps) metadata_type) (SEQUENCE eps) metadata_parameter]), pfunction_producer.SIGNATURE)
~$reference_notice_producer_arguments(phpType6_producer, phpType16, pfunction_producer.SIGNATURE[.RETURNS = [(PTBRANCH ([PTBUILTIN "array"]))]])
$reference_notice_producer_arguments(phpType6_producer, SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) phpType10 ABSENT (SEQUENCE eps) metadata_parameter]), pfunction_producer.SIGNATURE[.PARAMETERS = [psparam[.TYPE = eps]]])
'''.strip().splitlines()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-provenance', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    provenance = args.native_provenance.resolve()
    native = json.loads(provenance.read_bytes())
    source = Path(native['command'][-1])
    row, = json.loads(CATALOGUE.read_bytes())
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    assert native['mode'] == 'native-only' and native['passed'] and native['inputs_stable']
    assert native['id'] == row['id'] and source.read_bytes() == row['source'].encode()
    assert sha(source) == native['source_sha256'] == row['source_sha256']
    assert native['runtime_sha256'] == native['runtime_sha256_after'] == sha(types.PHP)
    assert native['profile'] == json.loads((ROOT / 'tests/semantics/profile.json').read_bytes())
    assert source.with_name('native.stdout').read_bytes() == native['stdout'].encode() == row['native_stdout'].encode()
    assert source.with_name('native.stderr').read_bytes() == native['stderr'].encode() == row['native_stderr'].encode()
    assert native['exit'] == row['native_exit'] == 0 and not native['timeout'] and not native['group_after']
    out = args.output.resolve()
    out.mkdir(parents=True)
    frontend = adapter = None
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(source.read_bytes()).decode()})
        assert parsed['accepted']
        checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True})
        assert checked['ok'] and checked['fixture']
    finally:
        try:
            if frontend:
                frontend.close()
        finally:
            if adapter:
                adapter.close()
    initial = 'S_initial = $php_run(' + checked['fixture'] + ', 0, ' + json.dumps(base64.b64encode(os.fsencode(source)).decode()) + ')'
    reached = [initial] + REACHED
    fixture = out / 'state.watsup'
    fixture.write_text(PREFIX + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + line + '\n' for line in reached + CONTROLS))
    modules = [ROOT / name for name in json.loads((ROOT / 'spec/semantics/modules.json').read_bytes())]
    runner = ROOT / 'tests/semantics/_build/default/numeric_runner.exe'
    paths = modules + [runner, fixture, source, provenance, source.with_name('native.stdout'), source.with_name('native.stderr'), Path(__file__), Path(prior.__file__), CATALOGUE]
    paths += [ROOT / name for name in ('spec/semantics/modules.json', 'tests/semantics/profile.json', '_build/default/adapter/main.exe', '.tools/php/bin/php', '.tools/php-file.so', 'frontend/worker.php', 'frontend/target.php', 'frontend/wire.php', 'frontend/wire.py', 'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py')]
    fingerprints = lambda: {str(path): sha(path) for path in paths}
    before = fingerprints()
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    print(out, flush=True)
    process = recorder.recorded([str(runner), *map(str, modules), str(fixture)], out / 'run', 1200)
    stable = before == fingerprints()
    head_stable = revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    passed = (process['exit'] == 0 and not process['timeout'] and not process['group_after'] and stable and head_stable
        and (out / 'run.stdout').read_bytes() == b'true\n' and not (out / 'run.stderr').read_bytes())
    report = {'revision': revision, 'inputs': before, 'inputs_stable': stable, 'head_stable': head_stable,
        'source_sha256': sha(source), 'fixture_sha256': sha(fixture), 'conditions': len(reached) + len(CONTROLS),
        'reached_conditions': len(reached), 'derived_conditions': len(CONTROLS),
        'heap_bindings': len({line.split(' = ', 1)[0] for line in reached if line.startswith('H_') and ' = $heap_graph(' in line}),
        'executed_heap_bindings': sum(line.startswith('H_') and ' = $heap_graph(' in line for line in reached),
        'module_count': len(modules), 'mode': 'AL/cache=false/det=true', 'process': process, 'source_agreements': 0, 'passed': passed}
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    print('array-byval-producer', passed, flush=True)
    return passed


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
