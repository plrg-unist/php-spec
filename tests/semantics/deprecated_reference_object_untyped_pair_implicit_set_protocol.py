#!/usr/bin/env python3
"""Reach actual untyped GET/SET entries and resume the first write locally."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess
from deprecated_global_constant_protocol import PREFIX
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_pair_implicit_set') / 'untyped-pair-implicit-set-execution.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
b64 = lambda b: base64.b64encode(b).decode()
PAUSE = r'''
dec $pair_phase(pstate,text) : bool
def $pair_phase(S,"get") = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook
  -- if S.TODO = (STMT statement) :: ptask*
  -- if $ccn_output(S.EVENTS) = eps
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("gets275execution")) = (n_gets)
  -- if S.STORE[n_gets] = DEFINED (PINT 0)
def $pair_phase(S,"set") = true
  -- if S.CURRENT = (pcallcontext)
  -- if pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook
  -- if S.TODO = (STMT statement) :: ptask*
  -- if $ccn_output(S.EVENTS) = $ptascii("D|")
  -- if $lookup(S.ENV,$ptascii("value")) = (n_value)
  -- if S.STORE[n_value] = DEFINED (PBOOL false)
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("sets275execution")) = (n_sets)
  -- if S.STORE[n_sets] = DEFINED (PINT 0)
def $pair_phase(S,"after") = true
  -- if S.CURRENT = eps /\ S.FRAMES = eps
  -- if $ccn_output(S.EVENTS) = $ptascii("D|")
  -- if S_global = $global_table_view(S)
  -- if $lookup(S_global.ENV,$ptascii("gets275execution")) = (n_gets)
  -- if $lookup(S_global.ENV,$ptascii("sets275execution")) = (n_sets)
  -- if $lookup(S_global.ENV,$ptascii("result275")) = (n_result)
  -- if S.STORE[n_gets] = DEFINED (PINT 1) /\ S.STORE[n_sets] = DEFINED (PINT 1)
  -- if S.STORE[n_result] = DEFINED (PBOOL false)
def $pair_phase(S,text) = false -- otherwise
dec $pair_pause(pstate,text,nat) : pstate
def $pair_pause(S,text,n_budget) = S -- if $pair_phase(S,text)
def $pair_pause(S,text,n_budget) = $pair_pause(S_next[.COMPLETION = NORMAL],text,$nabs($(n_budget - 1)))
  -- if ~$pair_phase(S,text)
  -- if S.COMPLETION = NORMAL /\ $(n_budget > 0) /\ S.TODO =/= eps
  -- if S_next = $drive_steps(S,1)
  -- if S_next.COMPLETION = BUDGET
def $pair_pause(S,text,n_budget) = S -- otherwise
'''


def fields(fixture):
    checks = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(b64(bytes(SOURCE))) + ')',
        'S_get = $pair_pause(S_start[.COMPLETION = NORMAL],"get",30000)', '$pair_phase(S_get,"get")',
        'S_get.CURRENT = (pcallcontext_get)', 'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_get',
        'pcallcontext_get.RECEIVER = (n_object)', '$property_hook_function(S_get,ppropertyhook_get) = (pfunction_get)',
        '$property_declaring_class(S_get.CLASSES,ppropertyhook_get.PROPERTY) = (porigin_owner)',
        '$class_at(S_get.CLASSES,porigin_owner) = (pclassdesc)',
        'pclassdesc.NAME = $base64(' + json.dumps(b64(b'Ns275UntypedPairExecution\\Box275')) + ')',
        'pclassdesc.PARENT = eps', 'pclassdesc.PROPERTIES = [ppropertydesc]',
        'ppropertydesc.TYPE = eps', 'ppropertydesc.NAME = $ptascii("tag")',
        '$property_hook_pair_origins(S_get,ppropertydesc) = [porigin_get,porigin_set]',
        'pfunction_get.ORIGIN = porigin_get', 'pcallcontext_get.FUNCTION = porigin_get', '$function_at(S_get.FUNCTIONS,porigin_set) = (pfunction_set)',
        'porigin_get = PORIGIN n_source (pcpath_group ++ [PCFIELD 4,PCINDEX 0])',
        'porigin_set = PORIGIN n_source (pcpath_group ++ [PCFIELD 4,PCINDEX 1])',
        'pcallcontext_get.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext_get.CALLED_CLASS = (porigin_owner)',
        '$lookup(S_get.ENV,$ptascii("value")) = eps', '~($ptascii("value") <- pfunction_get.CVS)',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}',
        'pfunction_set.SIGNATURE = $property_set_signature(ppropertydesc)',
        'pfunction_set.SIGNATURE.PARAMETERS = [{NAME $ptascii("value"), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]',
        '$objectprops_at(S_get.OBJECTPROPS,n_object) = ([ppropertyslot_get])',
        'ppropertyslot_get.STATE = PROP_VALUE (DIRECT (PINT 17))',
        '$call_descriptors_valid(S_get)', '$heap_valid($heap_graph(S_get))']
    for role in ['get', 'set']:
        origin = 'porigin_' + role; function = 'pfunction_' + role
        checks += [function + '.DEFAULTS = eps', '~' + function + '.EARLY',
            '$origin_node(S_get.SOURCES,' + origin + ') = (NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_' + role + ' (SEQUENCE eps) (SEQUENCE statement_' + role + '*) metadata_' + role + ')',
            '$hook_parameter_facts(metadata_' + role + ') = [false]',
            '$origin_child((' + origin + '),[PCFIELD 4,PCINDEX 0]) = (porigin_parameter_' + role + ')',
            '$origin_node(S_get.SOURCES,porigin_parameter_' + role + ') = eps',
            '$code_expression(' + function + '.CODE.EXPRESSIONS,pcpath_group ++ [PCFIELD 4,PCINDEX ' + ('0' if role == 'get' else '1') + ',PCFIELD 4,PCINDEX 0]) = eps',
            function + '.BODY = pcpath_group ++ [PCFIELD 4,PCINDEX ' + ('0' if role == 'get' else '1') + ',PCFIELD 5]']
    checks += ['S_set = $pair_pause(S_get,"set",30000)', '$pair_phase(S_set,"set")',
        'S_set.CURRENT = (pcallcontext_set)', 'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook_set',
        'pcallcontext_set.RECEIVER = (n_object)', 'pcallcontext_set.FUNCTION = porigin_set', '$property_set_function(S_set,ppropertyhook_set) = (pfunction_set)',
        'pcallcontext_set.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext_set.CALLED_CLASS = (porigin_owner)',
        '$lookup(S_set.ENV,$ptascii("value")) = (n_value)', 'S_set.STORE[n_value] = DEFINED (PBOOL false)',
        '$ptascii("value") <- pfunction_set.CVS', '~$property_set_explicit_origin(S_set,porigin_set)',
        '$default_parameter_line(S_set,porigin_set,0) = $source_line(metadata_set)',
        '$function_body_tasks(S_get,pfunction_get) = $statement_tasks(statement_get*,(PORIGIN n_source pfunction_get.BODY),0) ++ [$function_fallthrough(S_get,pfunction_get)]',
        '$function_body_tasks(S_set,pfunction_set) = $statement_tasks(statement_set*,(PORIGIN n_source pfunction_set.BODY),0) ++ [$function_fallthrough(S_set,pfunction_set)]',
        '$call_descriptors_valid(S_set)', '$heap_valid($heap_graph(S_set))']
    for phase, target in [('get', 'set'), ('set', 'after')]:
        checks += ['S_' + phase + '_zero = $drive_steps(S_' + phase + ',0)', 'S_' + phase + '_zero.COMPLETION = BUDGET',
            'S_' + phase + '_zero[.COMPLETION = NORMAL] = S_' + phase,
            'S_' + phase + '_one = $drive_steps(S_' + phase + ',1)', 'S_' + phase + '_one.COMPLETION = BUDGET']
        if target == 'after': checks += ['S_after = $pair_pause(S_set,"after",30000)', '$pair_phase(S_after,"after")']
        for budget in ['zero', 'one']:
            checks += ['$pair_pause(S_' + phase + '_' + budget + '[.COMPLETION = NORMAL],"' + target + '",30000) = S_' + target]
    checks += ['$objectprops_at(S_after.OBJECTPROPS,n_object) = ([ppropertyslot_after])',
        'ppropertyslot_after.STATE = PROP_VALUE (DIRECT (PBOOL true))',
        'S_after_global = $global_table_view(S_after)',
        '$lookup(S_after_global.ENV,$ptascii("gets275execution")) = (n_gets)',
        '$lookup(S_after_global.ENV,$ptascii("sets275execution")) = (n_sets)',
        '$call_descriptors_valid(S_after)', '$heap_valid($heap_graph(S_after))',
        'S_done = $drive(S_after,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("D|B|I|T|C|Z|")',
        'S_done.STORE[n_gets] = DEFINED (PINT 4)', 'S_done.STORE[n_sets] = DEFINED (PINT 3)',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php',
        'frontend/SourcePrinter.php', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py',
        'tests/semantics/static_types.py', 'tests/semantics/deprecated_class_constant_fetch_protocol.py',
        'tests/semantics/deprecated_parameter_default_protocol.py', 'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/profile.json', '.tools/php/bin/php', '.tools/php-file.so',
        '_build/default/adapter/main.exe', 'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': b64(SOURCE.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + PAUSE + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl', *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    if not report['passed']: print(report.get('stdout', '')[:2000], report.get('stderr', '')[:4000])
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
