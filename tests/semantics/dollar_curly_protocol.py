#!/usr/bin/env python3
"""Source-derived compiler chronology and deprecated interpolation certificates."""
from pathlib import Path
import argparse
import base64
import copy
import hashlib
import json
import subprocess
import tempfile
from error_handler_run import recorded
from recorded_worker import Worker

R = Path(__file__).resolve().parents[2]
P = Path(__file__).with_name('dollar-curly')


def prepare(out):
    b64=lambda value:base64.b64encode(value).decode()
    profile=json.loads((R/'tests/semantics/profile.json').read_text());flags=[a for k,v in profile.items() for a in ('-d',k+'='+v)]
    f=Worker([str(R/'.tools/php/bin/php'),'-n',*flags,'-d','extension='+str(R/'.tools/php-file.so'),str(R/'frontend/worker.php')],out/'frontend')
    try:original={name:f.request({'op':'parse','source':b64((P/(name+'.php')).read_bytes())})['ast'] for name in ('main-modern','included-multiline')}
    finally:f.close()
    def visit(value,path=()):
     if isinstance(value,list):
      for i,child in enumerate(value):yield from visit(child,path+(('PCINDEX',i),))
     elif isinstance(value,dict) and 'node' in value:
      yield value,path
      for i,child in enumerate(value['fields']):yield from visit(child,path+(('PCFIELD',i),))
    def legacy(ast):return [(node,path) for node,path in visit(ast['program']) if 'encapsVarKind' in node['meta']]
    main=original['main-modern']; parts=legacy(main);assert [int(n['meta']['encapsVarKind']['int']) for n,_ in parts]==[1,1,2,2]
    variants={'main':main,'multi':original['included-multiline']}
    erased=copy.deepcopy(main)
    for node,_ in legacy(erased):node['meta'].pop('encapsVarKind')
    variants['erased']=erased
    for name,index,kind in [('bad_kind',0,3),('bad_direct',0,2),('bad_dim',1,2),('bad_computed',2,1)]:
     ast=copy.deepcopy(main);legacy(ast)[index][0]['meta']['encapsVarKind']={'int':str(kind)};variants[name]=ast
    ast=copy.deepcopy(main);next(node for node,_ in visit(ast['program']) if node['node']=='InterpolatedStringPart')['meta']['encapsVarKind']={'int':'1'};variants['bad_text']=ast
    ast=copy.deepcopy(main);next(node for node,_ in visit(ast['program']) if node['node']=='Expr_Variable')['meta']['encapsVarKind']={'int':'1'};variants['outside']=ast
    w=Worker([str(R/'_build/default/adapter/main.exe'),str(R)],out/'syntax-adapter')
    try:fixtures={name:w.request({'op':'check','ast':ast,'fixture':True})['fixture'] for name,ast in variants.items()}
    finally:w.close()
    setup=''
    for name,fixture in fixtures.items():setup+='dec $dollar_'+name+'() : program\ndef $dollar_'+name+'() = '+fixture+'\n'
    def path_expr(path):return '(['+','.join(tag+' '+str(n) for tag,n in path)+'])'
    def diagnostic(path,kind,line,file):return 'PLDIAGNOSTIC "deprecated" "dollar-curly-'+('variable' if kind==1 else 'expression')+'" eps { UNIT 0, PATH '+path_expr(path)+', FILE $base64("'+b64(bytes(file))+'"), LINE '+str(line)+' }'
    checks=[]
    for name,source,lines in [('main','main-modern',[3,3,3,3]),('multi','included-multiline',[3,3,4,6,7,10,11,13])]:
     filename=P/(source+'.php');flags=legacy(variants[name]);assert len(flags)==len(lines)
     diagnostics=[diagnostic(path,int(node['meta']['encapsVarKind']['int']),line,filename) for (node,path),line in zip(flags,lines)]
     checks += ['P_'+name+' = $ppstart(0, $dollar_'+name+'(), $base64("'+b64(bytes(filename))+'"))','P_'+name+'.COMPLETION = PPCNORMAL','P_'+name+'.DIAGNOSTICS = ['+', '.join(diagnostics)+']']
    file=b64(bytes(P/'main-modern.php'))
    for name in variants:
     if name in ('main','multi'):continue
     checks+=['P_'+name+' = $ppstart(0, $dollar_'+name+'(), $base64("'+file+'"))']
     if name in ('erased','outside'):
      checks+=['P_'+name+'.COMPLETION = PPCNORMAL','P_'+name+'.DIAGNOSTICS = '+('eps' if name=='erased' else 'P_main.DIAGNOSTICS')]
     else:
      checks+=['P_'+name+'.COMPLETION = PPCABRUPT (UNSUPPORTED "invalid dollar-curly interpolation metadata")','|P_'+name+'.DIAGNOSTICS| = '+('0' if name in ('bad_kind','bad_direct') else '1' if name in ('bad_dim','bad_text') else '2')]
    checks+=['S_seed = $php_run($dollar_main(), 0, "'+file+'")','S_seed.COMPLETION = BUDGET','$declaration_history_valid(S_seed)','$call_descriptors_valid(S_seed)','P_main.DIAGNOSTICS[0] = PLDIAGNOSTIC "deprecated" "dollar-curly-variable" eps pllocation']
    for bad in ['PLDIAGNOSTIC "deprecated" "dollar-curly-variable" eps pllocation[.LINE = $(pllocation.LINE + 1)]','PLDIAGNOSTIC "deprecated" "dollar-curly-variable" eps pllocation[.PATH = eps]','PLDIAGNOSTIC "deprecated" "dollar-curly-variable" eps pllocation[.UNIT = 1]','PLDIAGNOSTIC "deprecated" "dollar-curly-variable" eps pllocation[.FILE = $ptascii("/wrong.php")]','PLDIAGNOSTIC "deprecated" "dollar-curly-expression" eps pllocation']:
     checks+=['~$declaration_history_valid(S_seed[.DECLARATIONS = $dollar_replace(S_seed.DECLARATIONS, '+bad+')])']
    helpers='''dec $dollar_warning(pdeclaration) : bool
def $dollar_warning(PDCOMPILEWARNING pldiagnostic) = true
def $dollar_warning(pdeclaration) = false -- otherwise
dec $dollar_replace(pdeclaration*, pldiagnostic) : pdeclaration*
def $dollar_replace(eps, pldiagnostic) = eps
def $dollar_replace((PDCOMPILEWARNING pldiagnostic_old) :: pdeclaration*, pldiagnostic) = (PDCOMPILEWARNING pldiagnostic) :: pdeclaration*
def $dollar_replace(pdeclaration :: pdeclaration_tail*, pldiagnostic) = pdeclaration :: $dollar_replace(pdeclaration_tail*, pldiagnostic)
  -- if ~$dollar_warning(pdeclaration)
'''
    fixture=setup+'\n'+helpers+'\ndec $main() : bool\ndef $main() = true\n'+''.join('  -- if '+check+'\n' for check in checks)+'def $main() = false -- otherwise\n'

    (out / 'protocol.watsup').write_text(fixture)
    (out / 'prepared.json').write_text(json.dumps({'conditions': len(checks),
        'sources': {name: str(P / (name + '.php')) for name in original}}) + '\n')
    return len(checks)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--prepare-only', action='store_true')
    args = parser.parse_args()
    out = Path(tempfile.mkdtemp(prefix='dollar-curly-protocol-', dir=R / '.tools')); print(out, flush=True)
    modules = [R / name for name in json.loads((R / 'spec/semantics/modules.json').read_text())]
    runner = R / 'tests/semantics/_build/default/numeric_runner.exe'
    watched = [*modules, R / 'spec/semantics/modules.json', R / 'spec/schema.json',
               R / 'frontend/worker.php', R / 'vendor/php-parser/lib/PhpParser/Parser/Php8.php',
               R / '_build/default/adapter/main.exe', runner, Path(__file__), *sorted(P.glob('*.php'))]
    digest = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    before = {str(path.relative_to(R)): digest(path) for path in watched}
    revision = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    conditions = prepare(out)
    report = {'revision': revision, 'inputs': before, 'conditions': conditions,
              'prepare_only': args.prepare_only,
              'environment': {'LC_ALL': 'C', 'TZ': 'UTC', 'PHP_SPEC_SCRIPT_ENCODING': 'absent'}}
    if not args.prepare_only:
        process = recorded([str(runner), *map(str, modules), str(out / 'protocol.watsup')], out / 'numeric', 90)
        report['process'] = process
        report['pass'] = (process['exit'] == 0 and not process['timeout']
                          and (out / 'numeric.stdout').read_bytes() == b'true\n'
                          and not (out / 'numeric.stderr').read_bytes())
    assert before == {str(path.relative_to(R)): digest(path) for path in watched}
    assert revision == subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=R, text=True).strip()
    (out / 'report.json').write_text(json.dumps(report, indent=2) + '\n')
    return args.prepare_only or report['pass']


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
