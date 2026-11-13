#!/usr/bin/env python3
"""Check real paired setter Params, receipts and outside ownership."""
import argparse
import base64
import hashlib
import json
from pathlib import Path
import subprocess

import deprecated_reference_object_untyped_hook_short_get_pair_review_protocol as implicit
block = implicit.block
pair = implicit.pair
peer = implicit.peer
header = implicit.header
from error_handler_run import recorded
from recorded_worker import Worker
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('deprecated_reference_object_untyped_hook_actual_pair_review') / 'nested-untyped-hook-actual-pair-shared.php'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
quoted = peer.quoted
PREFIX = implicit.PREFIX + r'''
dec $peer_param_at(pcodeexpr,pcpath) : bool
def $peer_param_at(CODEEXPR pcpath z b,pcpath) = true
def $peer_param_at(pcodeexpr,pcpath) = false -- otherwise
dec $peer_without_param(pcodeexpr*,pcpath) : pcodeexpr*
def $peer_without_param(eps,pcpath) = eps
def $peer_without_param((CODEEXPR pcpath z b) :: pcodeexpr_tail*,pcpath) = $peer_without_param(pcodeexpr_tail*,pcpath)
def $peer_without_param(pcodeexpr :: pcodeexpr_tail*,pcpath) = pcodeexpr :: $peer_without_param(pcodeexpr_tail*,pcpath)
  -- if ~$peer_param_at(pcodeexpr,pcpath)
'''
SELECTED = implicit.SELECTED


def fields(fixture):
    implicit.SOURCE = SOURCE
    oldroot = quoted('Ns278UntypedHookShortGetPairPeer' + chr(92) + 'Root278')
    root = quoted('Ns279UntypedHookActualPairPeer' + chr(92) + 'Root279')
    checks = []
    for check in implicit.fields(fixture):
        if check.startswith('U = '):
            checks.append(check); continue
        check = check.replace(oldroot,root).replace('278','279')
        check = check.replace('phpType11_set (SEQUENCE eps) expression_set','phpType11_set (SEQUENCE ([phpType17_parameter])) expression_set')
        check = check.replace('$hook_parameter_facts(metadata_set) = [false]','$hook_parameter_facts(metadata_set) = [true]')
        check = check.replace('$hook_pair_backed_headers(', '$hook_pair_untyped_parameter_headers(')
        check = check.replace('$hook_pair_get_index(phpType38_set,phpType38_get,ppropertydesc_rootpad.NAME,"class")', '$hook_pair_untyped_parameter_get_index(phpType38_set,phpType38_get,ppropertydesc_rootpad.NAME)')
        if check == 'pfunction_set.SIGNATURE = $property_set_signature(ppropertydesc_rootpad)':
            checks += ['pfunction_set.SIGNATURE.PARAMETERS = [{NAME $ptascii("incoming"), TYPE eps, BYREF false, VARIADIC false, REQUIRED true, DEFAULT PSNONE}]',
                'pfunction_set.SIGNATURE.RETURNS = [(PTBRANCH ([PTBUILTIN "void"]))]', '~pfunction_set.SIGNATURE.BYREF']
            continue
        if check.startswith('$origin_node(S_raw.SOURCES,PORIGIN n_source (pcpath_set ++ [PCFIELD 4,PCINDEX 0])) = eps'):
            checks += ['pcpath_parameter = pcpath_set ++ [PCFIELD 4,PCINDEX 0]',
                '$origin_node(S_raw.SOURCES,PORIGIN n_source pcpath_parameter) = (phpType17_parameter)',
                'phpType17_parameter = NParam (SEQUENCE eps) (INTEGER 0) ABSENT (BOOLEAN false) (BOOLEAN false) (NExprVariable (BYTES text_parameter) metadata_variable) ABSENT (SEQUENCE eps) metadata_parameter',
                '$base64(text_parameter) = $ptascii("incoming")',
                '$origin_node(S_raw.SOURCES,PORIGIN n_source (pcpath_parameter ++ [PCFIELD 5])) = (NExprVariable (BYTES text_parameter) metadata_variable)',
                '$property_set_untyped_parameters(SEQUENCE ([phpType17_parameter]))',
                'ptcontext_parameter = {NAMESPACE pfunction_set.ENV.NAMESPACE, IMPORTS pfunction_set.ENV.CLASSES, SCOPE PTKNOWN pclassdesc_root.NAME eps, POSITION PTRETURN, OWNER pclassdesc_root.NAME, MEMBER $property_set_name(ppropertydesc_rootpad.NAME), FILE $call_sourcefile(S_raw.FILES,porigin_set), LINE $psline(metadata_set)}',
                '$property_set_untyped_signature(SEQUENCE ([phpType17_parameter]),ptcontext_parameter) = (pfunction_set.SIGNATURE)']
            continue
        if check.startswith('$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_set ++ [PCFIELD 4,PCINDEX 0]) = eps'):
            checks += ['$code_expression(pfunction_set.CODE.EXPRESSIONS,pcpath_parameter) = ((z_parameter,false))',
                'z_parameter = $psline(metadata_parameter)', '$(z_parameter > 0)']
            continue
        if check == '$ptascii("value") <- pfunction_set.CVS':
            checks += ['$ptascii("incoming") <- pfunction_set.CVS', '~($ptascii("value") <- pfunction_set.CVS)']
            continue
        if check.startswith('metadata_set_empty = '): check = check.replace('(MhookParameterList true)','(MhookParameterList false)')
        checks.append(check)
    extra = ['psparam_incoming = pfunction_set.SIGNATURE.PARAMETERS[0]',
        'S_wrong_name = S_functions[.FUNCTIONS = [pfunction_get,pfunction_set[.SIGNATURE.PARAMETERS = ([psparam_incoming[.NAME = $ptascii("value")]])]]]',
        '$property_hook_pair_origins(S_wrong_name,ppropertydesc_rootpad) = eps',
        '$property_hook_origin(S_wrong_name,ppropertydesc_rootpad) = eps',
        '$property_set_origin(S_wrong_name,ppropertydesc_rootpad) = eps']
    for label, code in [('missing','$peer_without_param(pfunction_set.CODE.EXPRESSIONS,pcpath_parameter)'),
            ('line','(CODEEXPR pcpath_parameter $(z_parameter + 1) false) :: $peer_without_param(pfunction_set.CODE.EXPRESSIONS,pcpath_parameter)')]:
        function = 'pfunction_param_' + label; state = 'S_param_' + label
        extra += [function + ' = pfunction_set[.CODE.EXPRESSIONS = ' + code + ']',
            '$peer_without_param(' + function + '.CODE.EXPRESSIONS,pcpath_parameter) = $peer_without_param(pfunction_set.CODE.EXPRESSIONS,pcpath_parameter)',
            '$code_expression(' + function + '.CODE.EXPRESSIONS,pfunction_set.BODY) = ((z_set_rhs,false))',
            state + ' = S_functions[.FUNCTIONS = [pfunction_get,' + function + ']]',
            '$property_hook_pair_origins(' + state + ',ppropertydesc_rootpad) = eps',
            '$property_hook_origin(' + state + ',ppropertydesc_rootpad) = eps',
            '$property_set_origin(' + state + ',ppropertydesc_rootpad) = eps']
    for label,path,node in [('param','pcpath_parameter','NScalarInt (INTEGER 0) eps'),
            ('var','(pcpath_parameter ++ [PCFIELD 5])','NExprVariable (BYTES "dmFsdWU=") metadata_variable')]:
        state = 'S_child_' + label
        extra += [state + ' = S_class[.SOURCES = [pcunit[.OCCURRENCES = (PCOCCURRENCE ' + path + ' (' + node + ')) :: pcunit.OCCURRENCES]]]',
            '$property_hook_pair_origins(' + state + ',ppropertydesc_rootpad) = eps',
            '$property_hook_origin(' + state + ',ppropertydesc_rootpad) = eps',
            '$property_set_origin(' + state + ',ppropertydesc_rootpad) = eps',
            '~$class_constant_reference_object_graph(' + state + ',n_receiver,eps)']
    at = checks.index('S_neutral = $class_constant_class_forward(S_class,S_raw.RESULT,expression_class,expression_member,z,ptask_tail*)')
    checks[at:at] = extra
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args(); out = args.output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / p for p in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    paths = [Path(__file__), Path(implicit.__file__), Path(block.__file__), Path(pair.__file__), Path(peer.__file__), Path(header.__file__), SOURCE, *modules, *(ROOT / p for p in (
        'spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'frontend/worker.php', 'frontend/SourcePrinter.php',
        'tests/semantics/deprecated_class_constant_fetch_protocol.py', 'tests/semantics/deprecated_parameter_default_protocol.py',
        'tests/semantics/deprecated_global_constant_protocol.py', 'tests/semantics/recorded_worker.py',
        'tests/semantics/error_handler_run.py', 'tests/semantics/static_types.py', 'tests/semantics/profile.json',
        '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
        'tests/semantics/_build/default/numeric_runner.exe'))]
    before = {str(p.relative_to(ROOT)): sha(p) for p in paths}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        frontend = Worker([str(types.PHP), '-n', *types.FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')], out / 'frontend')
        adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)], out / 'adapter')
        try:
            parsed = frontend.request({'op': 'parse', 'source': base64.b64encode(SOURCE.read_bytes()).decode()})
            assert parsed['accepted'] and not parsed['diagnostics']
            checked = adapter.request({'op': 'check', 'ast': parsed['ast'], 'fixture': True}); assert checked['ok']
        finally:
            try: adapter.close()
            finally: frontend.close()
        checks = fields(checked['fixture']); report['premises'] = len(checks)
        (out / 'assertions.json').write_text(json.dumps(checks, indent=2) + '\n')
        (out / 'protocol.watsup').write_text(PREFIX + SELECTED + '\ndec $main() : bool\ndef $main() = true\n' + ''.join('  -- if ' + c + '\n' for c in checks))
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
