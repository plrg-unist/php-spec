#!/usr/bin/env python3
"""Reach actual paired SET Params, preserving body receipts and real resumption."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_pair_implicit_set_protocol as pair
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE_DIR = Path(__file__).with_name('deprecated_reference_object_untyped_pair_actual_set_param')
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
MUTATE = r'''
dec $actual_param_receipt(pcodeexpr*,pcpath,int?) : pcodeexpr*
def $actual_param_receipt(eps,pcpath,z_new?) = eps
def $actual_param_receipt((CODEEXPR pcpath z b) :: pcodeexpr*,pcpath,eps) = $actual_param_receipt(pcodeexpr*,pcpath,eps)
def $actual_param_receipt((CODEEXPR pcpath z b) :: pcodeexpr*,pcpath,(z_new)) = (CODEEXPR pcpath z_new b) :: $actual_param_receipt(pcodeexpr*,pcpath,(z_new))
def $actual_param_receipt(pcodeexpr :: pcodeexpr*,pcpath,z_new?) = pcodeexpr :: $actual_param_receipt(pcodeexpr*,pcpath,z_new?) -- otherwise
'''


def fields(fixture, source, kind):
    name = 'received279short' if kind == 'short' else 'input279block'
    namespace = 'Ns279UntypedPairActualParam' + ('Short' if kind == 'short' else 'Block') + 'Execution'
    initial = '(PINT 17)' if kind == 'short' else 'PNULL'
    set_body = 'expression_set' if kind == 'short' else '(SEQUENCE statement_set*)'
    c = ['U = ' + fixture,
        'S_start = $php_run(U,0,' + json.dumps(pair.b64(bytes(source))) + ')',
        'S_get = $pair_pause(S_start[.COMPLETION = NORMAL],"get",30000)', '$pair_phase(S_get,"get")',
        'S_get.CURRENT = (pcallcontext_get)', 'pcallcontext_get.TARGET = PROPERTY_HOOK_TARGET ppropertyhook_get',
        'pcallcontext_get.RECEIVER = (n_object)', '$property_hook_function(S_get,ppropertyhook_get) = (pfunction_get)',
        '$property_declaring_class(S_get.CLASSES,ppropertyhook_get.PROPERTY) = (porigin_owner)',
        '$class_at(S_get.CLASSES,porigin_owner) = (pclassdesc)',
        'pclassdesc.NAME = $base64(' + json.dumps(pair.b64((namespace + '\\Box279').encode())) + ')',
        'pclassdesc.PARENT = eps', 'pclassdesc.PROPERTIES = [ppropertydesc]',
        'ppropertydesc.TYPE = eps', 'ppropertydesc.NAME = $ptascii("tag")',
        '$property_hook_pair_origins(S_get,ppropertydesc) = [porigin_get,porigin_set]',
        'pfunction_get.ORIGIN = porigin_get', '$function_at(S_get.FUNCTIONS,porigin_set) = (pfunction_set)',
        'porigin_get = PORIGIN n_source pcpath_get', '$(|pcpath_get| >= 2)',
        'pcpath_group = pcpath_get[0:$nabs($( |pcpath_get| - 2))]',
        'pcpath_get = pcpath_group ++ [PCFIELD 4,PCINDEX 0]',
        'porigin_set = PORIGIN n_source pcpath_set', 'pcpath_set = pcpath_group ++ [PCFIELD 4,PCINDEX 1]',
        'ppropertydesc.ORIGIN = PORIGIN n_source (pcpath_group ++ [PCFIELD 3,PCINDEX 0])',
        'pfunction_get.SIGNATURE = {PARAMETERS eps, RETURNS eps, BYREF false}',
        'pfunction_set.SIGNATURE = {PARAMETERS ([{NAME $ptascii("' + name + '"), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]), RETURNS ([(PTBRANCH ([PTBUILTIN "void"]))]), BYREF false}',
        '$lookup(S_get.ENV,$ptascii("value")) = eps', '~($ptascii("value") <- pfunction_get.CVS)',
        '$origin_node(S_get.SOURCES,porigin_get) = (NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_get (SEQUENCE eps) expression_get metadata_get)',
        '$origin_node(S_get.SOURCES,porigin_set) = (NPropertyHook (SEQUENCE eps) (INTEGER 0) (BOOLEAN false) phpType11_set phpType16_set ' + set_body + ' metadata_set)',
        '$hook_parameter_facts(metadata_get) = [false]', '$hook_parameter_facts(metadata_set) = [true]',
        'phpType16_set = SEQUENCE ([NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_param) metadata_var) ABSENT (SEQUENCE eps) metadata_param])',
        '$base64(text_param) = $ptascii("' + name + '")',
        'pcpath_param = pcpath_set ++ [PCFIELD 4,PCINDEX 0]',
        '$origin_node(S_get.SOURCES,PORIGIN n_source pcpath_param) = (NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_param) metadata_var) ABSENT (SEQUENCE eps) metadata_param)',
        '$origin_node(S_get.SOURCES,PORIGIN n_source (pcpath_param ++ [PCFIELD 5])) = (NExprVariable (BYTES text_param) metadata_var)',
        '$psline(metadata_param) = 10', '$source_line(metadata_set) = 9',
        '$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_param) = ((10,false))',
        'pfunction_get.BODY = pcpath_get ++ [PCFIELD 5]', 'pfunction_set.BODY = pcpath_set ++ [PCFIELD 5]',
        'pfunction_get.DEFAULTS = eps', 'pfunction_set.DEFAULTS = eps', '~pfunction_get.EARLY', '~pfunction_set.EARLY',
        'pfunction_get.LINE = 5', 'pfunction_get.ENDLINE = 8', 'pfunction_set.LINE = 9',
        'pfunction_set.ENDLINE = ' + ('15' if kind == 'short' else '14'),
        '$origin_node(S_get.SOURCES,PORIGIN n_source pfunction_get.BODY) = (expression_get)',
        '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get_expr,false))',
        '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get_arrow)',
        r'$(z_get_expr >= 5 /\ z_get_expr <= 8)', r'$(z_get_arrow >= 5 /\ z_get_arrow <= 8)',
        '$function_body_tasks(S_get,pfunction_get) = [$at_task((PORIGIN n_source pfunction_get.BODY),EVAL expression_get),RETURN_VALUE z_get_arrow]',
        '$property_hook_pair_backed(S_get,ppropertydesc)', '~$property_hook_virtual(S_get,ppropertydesc)',
        '$objectprops_at(S_get.OBJECTPROPS,n_object) = ([ppropertyslot_get])',
        'ppropertyslot_get.STATE = PROP_VALUE (DIRECT ' + initial + ')',
        '$property_default_state(S_get,ppropertydesc) = (PROP_VALUE (DIRECT ' + initial + '))',
        '$node_children(S_get,HOBJECT n_object) = eps', '$call_descriptors_valid(S_get)', '$heap_valid($heap_graph(S_get))']
    if kind == 'short':
        c += ['$origin_node(S_get.SOURCES,PORIGIN n_source pfunction_set.BODY) = (expression_set)',
            '$code_expression(pfunction_set.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set_rhs,false))',
            r'$(z_set_rhs >= 12 /\ z_set_rhs <= 15)',
            '$property_set_expression(S_get,porigin_set) = ((ppropertydesc,expression_set,9))']
    else:
        c += ['ppropertydesc.DEFAULT = PROP_NULL',
            '$function_body_tasks(S_get,pfunction_set) = $statement_tasks(statement_set*,(PORIGIN n_source pfunction_set.BODY),0) ++ [$function_fallthrough(S_get,pfunction_set)]']
    c += ['S_functions = S_get[.FUNCTIONS = [pfunction_get,pfunction_set]]',
        '$property_hook_pair_origins(S_functions,ppropertydesc) = [porigin_get,porigin_set]']
    for label, line in [('missing','eps'), ('hookline','(9)')]:
        state = 'S_param_' + label
        c += ['pfunction_' + label + ' = pfunction_set[.CODE.EXPRESSIONS = $actual_param_receipt(pfunction_set.CODE.EXPRESSIONS,pcpath_param,' + line + ')]',
            '$actual_param_receipt(pfunction_' + label + '.CODE.EXPRESSIONS,pcpath_param,eps) = $actual_param_receipt(pfunction_set.CODE.EXPRESSIONS,pcpath_param,eps)',
            state + ' = S_functions[.FUNCTIONS = [pfunction_get,pfunction_' + label + ']]',
            '$property_hook_pair_origins(' + state + ',ppropertydesc) = eps',
            '$property_hook_origin(' + state + ',ppropertydesc) = eps', '$property_set_origin(' + state + ',ppropertydesc) = eps',
            '$code_expression(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = ((z_get_expr,false))',
            '$arrow_line(pfunction_get.CODE.EXPRESSIONS,pfunction_get.BODY) = (z_get_arrow)']
        if kind == 'short': c += ['$code_expression(pfunction_' + label + '.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set_rhs,false))']
    c += ['S_set = $pair_pause(S_get,"set",30000)', '$pair_phase(S_set,"set")',
        'S_set.CURRENT = (pcallcontext_set)', 'pcallcontext_set.FUNCTION = porigin_set',
        'pcallcontext_set.TARGET = PROPERTY_SET_TARGET ppropertyhook_set',
        '$property_set_function(S_set,ppropertyhook_set) = (pfunction_set)',
        'pcallcontext_set.RECEIVER = (n_object)', 'pcallcontext_set.LEXICAL_CLASS = (porigin_owner)', 'pcallcontext_set.CALLED_CLASS = (porigin_owner)',
        '$lookup(S_set.ENV,$ptascii("' + name + '")) = (n_value)', 'S_set.STORE[n_value] = DEFINED (PBOOL false)',
        '$lookup(S_set.ENV,$ptascii("value")) = eps', '~($ptascii("value") <- pfunction_set.CVS)',
        '$ptascii("' + name + '") <- pfunction_set.CVS', '$property_set_explicit_origin(S_set,porigin_set)',
        '$default_parameter_origin(S_set,porigin_set,0) = PORIGIN n_source pcpath_param',
        '$default_parameter_line(S_set,porigin_set,0) = 10', '$call_descriptors_valid(S_set)', '$heap_valid($heap_graph(S_set))']
    for phase, target in [('get','set'), ('set','after')]:
        c += ['S_' + phase + '_zero = $drive_steps(S_' + phase + ',0)', 'S_' + phase + '_zero.COMPLETION = BUDGET',
            'S_' + phase + '_zero[.COMPLETION = NORMAL] = S_' + phase,
            'S_' + phase + '_one = $drive_steps(S_' + phase + ',1)', 'S_' + phase + '_one.COMPLETION = BUDGET']
        if target == 'after': c += ['S_after = $pair_pause(S_set,"after",30000)', '$pair_phase(S_after,"after")']
        for budget in ['zero','one']:
            c += ['$pair_pause(S_' + phase + '_' + budget + '[.COMPLETION = NORMAL],"' + target + '",30000) = S_' + target]
    c += ['$objectprops_at(S_after.OBJECTPROPS,n_object) = ([ppropertyslot_after])',
        'ppropertyslot_after.STATE = PROP_VALUE (DIRECT (PBOOL true))',
        'S_done = $drive(S_after,30000)', 'S_done.COMPLETION = NORMAL',
        '$ccn_output(S_done.EVENTS) = $ptascii("D|B|I|T|C|Z|")',
        'S_done.CURRENT = eps', 'S_done.FRAMES = eps', 'S_done.HELD = eps',
        '$call_descriptors_valid(S_done)', '$heap_valid($heap_graph(S_done))']
    return c


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    parser.add_argument('--kind', required=True, choices=('block','short'))
    args = parser.parse_args(); source = SOURCE_DIR / ('actual-param-both-short-execution.php' if args.kind == 'short' else 'actual-param-short-get-block-set-execution.php')
    out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(pair.__file__), source, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json','spec/php.watsup','spec/schema.json','frontend/worker.php','frontend/SourcePrinter.php',
        'tests/semantics/recorded_worker.py','tests/semantics/error_handler_run.py','tests/semantics/static_types.py',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py','tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py','tests/semantics/profile.json','.tools/php/bin/php','.tools/php-file.so',
        '_build/default/adapter/main.exe','tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    report = {'head':head,'inputs':before,'module_count':len(modules),'source_agreement_credit':0,'kind':args.kind,'passed':False}
    try:
        frontend = Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension=' + str(ROOT / '.tools/php-file.so'),str(ROOT / 'frontend/worker.php')],out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'),str(ROOT)],out / 'adapter')
        try:
            parsed = frontend.request({'op':'parse','source':pair.b64(source.read_bytes())}); assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op':'check','ast':parsed['ast'],'fixture':True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture'],source,args.kind); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks,indent=2) + '\n')
        name = 'received279short' if args.kind == 'short' else 'input279block'
        pause = pair.PAUSE.replace('275','279').replace('$ptascii("value")','$ptascii("' + name + '")')
        pause = pause.replace('pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)','pcallcontext.TARGET = PROPERTY_HOOK_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)')
        if args.kind == 'short': pause = pause.replace('pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n  -- if S.TODO = (STMT statement)','pcallcontext.TARGET = PROPERTY_SET_TARGET ppropertyhook\n  -- if S.TODO = (EVAL expression)')
        (out / 'protocol.watsup').write_text(pair.PREFIX + pair.SELECTED + pause + MUTATE + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'),'--sl',*map(str,modules),str(out / 'protocol.watsup')],out / 'check',240)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
        report['inputs_stable'] = before == {str(p.relative_to(ROOT)): sha(p) for p in paths}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout'] and not report['process']['group_after']
            and report['stdout'] == 'true\n' and not report['stderr'] and report['head_stable'] and report['inputs_stable'])
    finally: (out / 'report.json').write_text(json.dumps(report,indent=2) + '\n')
    if not report['passed']: print(report.get('stdout','')[:2000],report.get('stderr','')[:4000])
    assert report['passed']; print('pass',report['premises'])


if __name__ == '__main__': main()
