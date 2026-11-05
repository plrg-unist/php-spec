#!/usr/bin/env python3
"""Single constant metadata code authority and ordered compiler contexts."""
import argparse
import base64
import copy
import hashlib
import json
from pathlib import Path
import subprocess

from error_handler_run import recorded
from recorded_worker import Worker
import source_compiler as compiler
import static_types as types

ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name('single_attributed_constant')
sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
b64 = lambda data: base64.b64encode(data).decode()
path_term = lambda path: '[' + ','.join('(' + kind + ' ' + str(index) + ')' for kind, index in path) + ']'


def nodes(value, path=()):
    if isinstance(value, dict) and 'node' in value:
        yield value, path
        for index, field in enumerate(value['fields']):
            yield from nodes(field, (*path, ('PCFIELD', index)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from nodes(child, (*path, ('PCINDEX', index)))


def prepare(out):
    cases=json.loads((SOURCE/'cases.json').read_text())
    frontend=Worker([str(types.PHP),'-n',*types.FLAGS,'-d','extension='+str(ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')],out/'frontend')
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)],out/'adapter')
    checks=[];asts={}
    selected=('quiet','quiet-duplicate','unknown-argument','closure-argument','initializer-closure','initializer-closure-array',
        'initializer-body-first','initializer-invalid-first','argument-before-unpack','argument-duplicate',
        'later-group-before-target','target','repeat-deprecated','cursor-initializer','cursor-argument',
        'cursor-attribute-closure','deprecated-pending','deprecated-alias-pending','namespace-deprecated')
    try:
        for name in selected:
            case=cases[name];path=SOURCE/case['source'];tag=name.replace('-','_')
            parsed=frontend.request({'op':'parse','source':b64(path.read_bytes())})
            assert parsed['accepted'] and not parsed['diagnostics'];asts[name]=parsed['ast']
            fixture=adapter.request({'op':'check','ast':parsed['ast'],'fixture':True})['fixture']
            checks+=['U_'+tag+' = '+fixture,'P_'+tag+' = $ppstart(91,U_'+tag+','+types.byte_expr(str(path))+')']
            if case['status']=='unsupported':
                checks+=['P_'+tag+'.COMPLETION = PPCABRUPT (UNSUPPORTED "Deprecated global constant metadata")']
            elif case['status']=='normal':checks+=['P_'+tag+'.COMPLETION = PPCNORMAL']
            else:
                if case.get('diagnostic_class')=='Error':
                    checks+=['P_'+tag+'.COMPLETION = PPCABRUPT (FATAL $ptascii('+json.dumps(case['message'])+') '+str(case['line'])+')']
                else:
                    checks+=['$pptrace(P_'+tag+') = [("fatal",$ptascii('+json.dumps(case['message'])+'),'+types.byte_expr(str(path))+','+str(case['line'])+')]']
        def bind_path(label,path):checks.extend([label+' = '+path_term(path)]);return label
        decl_path=next(path for node,path in nodes(asts['quiet']['program']) if node['node']=='Const')
        attr_path=next(path for node,path in nodes(asts['quiet']['program']) if node['node']=='Attribute')
        decl=bind_path('pcpath_decl',decl_path);init=bind_path('pcpath_init',(*decl_path,('PCFIELD',1)))
        metadata=bind_path('pcpath_metadata',(*attr_path,('PCFIELD',0)))
        checks+=['P_zero = $ppstart(0,U_quiet,'+types.byte_expr(str(SOURCE/cases['quiet']['source']))+')',
            'S_initial = $php_run(U_quiet,0,'+json.dumps(b64(bytes(SOURCE/cases['quiet']['source'])))+')',
            'S_initial.COMPLETION = BUDGET','$call_descriptors_valid(S_initial)',
            '$constant_attribute_unit_names_valid(P_zero,S_initial.CODE[0])',
            'S_initial.CODE[0].NAMES[1] = CODENAME '+metadata+' $ptascii("A") eps',
            '$code_expression(S_initial.CODE[0].EXPRESSIONS,'+metadata+') = eps',
            '$global_constant_declaration_source(S_initial.SOURCES,PORIGIN 0 '+decl+')',
            '$global_constant_initializer_root(P_zero.FOLD.SOURCE,'+init+') = (PORIGIN 0 '+decl+')',
            '$global_constant_initializer_root(P_zero.FOLD.SOURCE,'+metadata+') = eps',
            '~$ppconstant_metadata_argument(P_zero.FOLD.SOURCE,'+init+')',
            '$ppsingle_attributed_initializer(P_zero.FOLD.SOURCE,'+init+')']
        variants={
            'value':'.NAMES[1] = CODENAME '+metadata+' $ptascii("B") eps',
            'fallback':'.NAMES[1] = CODENAME '+metadata+' $ptascii("A") ($ptascii("B"))',
            'path':'.NAMES[1] = CODENAME '+init+' $ptascii("A") eps',
            'unit':'.UNIT = 1',
            'missing':'.NAMES = S_initial.CODE[0].NAMES[0:1] ++ S_initial.CODE[0].NAMES[2:$nabs($(|S_initial.CODE[0].NAMES| - 2))]',
            'duplicate':'.NAMES = S_initial.CODE[0].NAMES ++ [S_initial.CODE[0].NAMES[1]]'}
        for tag,change in variants.items():
            state='S_bad_'+tag
            checks+=[state+' = S_initial[.CODE[0]'+change+']',
                '~$constant_attribute_unit_names_valid(P_zero,'+state+'.CODE[0])',
                '~$call_descriptors_valid('+state+')']
        checks+=['S_done = $drive_steps(S_initial[.COMPLETION = NORMAL],10000)','S_done.COMPLETION = NORMAL',
            '|S_done.USERCONSTANTS| = 1','S_done.USERCONSTANTS[0].ORIGIN = PORIGIN 0 '+decl,
            '$constant_attribute_entry_valid(S_done,PORIGIN 0 '+decl+')',
            '$global_constant_user_valid(S_done,S_done.USERCONSTANTS[0])','$call_descriptors_valid(S_done)']
        duplicate_decl=next(path for node,path in nodes(asts['quiet-duplicate']['program']) if node['node']=='Const')
        duplicate_site=bind_path('pcpath_duplicate_first',duplicate_decl)
        checks+=['S_duplicate = $php_run(U_quiet_duplicate,10000,'+json.dumps(b64(bytes(SOURCE/cases['quiet-duplicate']['source'])))+')',
            'S_duplicate.COMPLETION = NORMAL','|S_duplicate.USERCONSTANTS| = 1',
            'S_duplicate.USERCONSTANTS[0].ORIGIN = PORIGIN 0 '+duplicate_site,
            'S_duplicate.USERCONSTANTS[0].VALUE = PINT 1',
            '$constant_attribute_entry_valid(S_duplicate,PORIGIN 0 '+duplicate_site+')',
            '$call_descriptors_valid(S_duplicate)']
        for name in ('initializer-closure','closure-argument'):
            node,path=next((node,path) for node,path in nodes(asts[name]['program']) if node['node']=='Expr_Closure')
            tag=name.replace('-','_');site=bind_path('pcpath_'+tag,path);state='P_'+tag
            checks+=['$origin_node(['+state+'.FOLD.SOURCE],PORIGIN 91 '+site+') = (expression_'+tag+')',
                '|'+state+'.CLOSURETEMPLATES| = 1',state+'.CLOSURETEMPLATES[0].BODY = '+site+' ++ [PCFIELD 6]']
            if name=='initializer-closure':
                checks+=['$ppconstant_compiled_closure('+state+','+site+',expression_'+tag+',PPR) = ('+state+'.CLOSURETEMPLATES[0].ENDLINE)']
                for bad,change in [('missing','.CLOSURETEMPLATES = eps'),
                    ('unit','.FOLD.SOURCE.ID = 92'),('origin','.CLOSURETEMPLATES[0].ORIGIN = PORIGIN 92 '+site),
                    ('body','.CLOSURETEMPLATES[0].BODY = eps'),
                    ('line','.CLOSURETEMPLATES[0].LINE = $('+state+'.CLOSURETEMPLATES[0].LINE + 1)'),
                    ('end','.CLOSURETEMPLATES[0].ENDLINE = $('+state+'.CLOSURETEMPLATES[0].ENDLINE + 1)')]:
                    checks+=['$ppconstant_compiled_closure('+state+'['+change+'],'+site+',expression_'+tag+',PPR) = eps']
                checks+=['$ppconstant_compiled_closure('+state+','+site+' ++ [PCFIELD 6],expression_'+tag+',PPR) = eps',
                    '~$ppconstant_metadata_argument('+state+'.FOLD.SOURCE,'+site+')']
            else:
                checks+=['$ppconstant_compiled_closure('+state+','+site+',expression_'+tag+',PPR) = eps',
                    '$ppconstant_metadata_argument('+state+'.FOLD.SOURCE,'+site+')',
                    '~$ppsingle_attributed_initializer('+state+'.FOLD.SOURCE,'+site+')',
                    '~$ppconstant_metadata_argument('+state+'.FOLD.SOURCE,'+site+' ++ [PCFIELD 6,PCINDEX 0])',
                    '$global_constant_initializer_root('+state+'.FOLD.SOURCE,'+site+') = eps']
    finally:
        try:adapter.close()
        finally:frontend.close()
    (out/'assertions.json').write_text(json.dumps(checks,indent=2)+'\n')
    (out/'protocol.watsup').write_text('var U : program\n'+compiler.PREFIX+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+x+'\n' for x in checks))
    return len(checks)

def main():
    parser = argparse.ArgumentParser(description=__doc__); parser.add_argument('--output', type=Path, required=True)
    out = parser.parse_args().output.resolve(); out.mkdir(parents=True, exist_ok=False)
    modules = [ROOT / path for path in json.loads((ROOT / 'spec/semantics/modules.json').read_text())]
    hashes = json.loads((SOURCE / 'hashes.json').read_text())
    watched = [Path(__file__), *modules, SOURCE / 'cases.json', SOURCE / 'hashes.json', *(SOURCE / name for name in hashes),
        *(ROOT / path for path in ('spec/semantics/modules.json', 'spec/php.watsup', 'spec/schema.json', 'adapter/main.ml',
            'frontend/worker.php', 'frontend/RejectedHeaderParser.php', 'frontend/FileLexer.php', 'bin/php-semantics',
            'vendor/php-parser/lib/PhpParser/ParserAbstract.php', 'vendor/php-parser/lib/PhpParser/Parser/Php8.php',
            '.tools/php/bin/php', '.tools/php-file.so', '_build/default/adapter/main.exe',
            'tests/semantics/_build/default/numeric_runner.exe', 'tests/semantics/source_compiler.py',
            'tests/semantics/static_types.py', 'tests/semantics/recorded_worker.py', 'tests/semantics/error_handler_run.py'))]
    before = {str(path.relative_to(ROOT)): sha(path) for path in watched}
    head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
    report = {'head': head, 'inputs': before, 'module_count': len(modules), 'source_agreement_credit': 0, 'passed': False}
    try:
        report['premises'] = prepare(out)
        report['process'] = recorded([str(ROOT / 'tests/semantics/_build/default/numeric_runner.exe'), '--sl',
            *map(str, modules), str(out / 'protocol.watsup')], out / 'check', 180)
        report['stdout'] = (out / 'check.stdout').read_text(); report['stderr'] = (out / 'check.stderr').read_text()
        report['head_stable'] = head == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
        report['inputs_stable'] = before == {str(path.relative_to(ROOT)): sha(path) for path in watched}
        report['passed'] = (report['process']['exit'] == 0 and not report['process']['timeout']
            and not report['process']['group_after'] and report['stdout'] == 'true\n' and not report['stderr']
            and report['head_stable'] and report['inputs_stable'])
    finally:
        (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    assert report['passed']; print('pass', report['premises'])


if __name__ == '__main__': main()
