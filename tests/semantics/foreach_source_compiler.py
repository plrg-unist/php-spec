#!/usr/bin/env python3
"""Foreach compilation, access modes and original body contexts."""
import base64,copy,hashlib,json,subprocess,tempfile
from pathlib import Path
import source_compiler as compiler
from source_compiler import types,context
ROOT=Path(__file__).resolve().parents[2]
REPORT=ROOT/"coverage/semantics/foreach-source-compiler.json"

SOURCES = [('prerequisite/key-ref', b'<?php foreach([] as &$k=>$v){}'),
 ('prerequisite/key-ref-both', b'<?php foreach([] as &$k=>&$v){}'),
 ('prerequisite/key-ref-before-iterable', b'<?php foreach([[]=>1] as &$k=>$v){}'),
 ('prerequisite/key-ref-before-list-spread', b'<?php foreach([] as &$k=>[...$v]){}'),
 ('prerequisite/key-ref-dim', b'<?php foreach([] as &$k[0]=>$v){}'),
 ('prerequisite/key-list', b'<?php foreach([] as list($k)=>$v){}'),
 ('prerequisite/key-list-empty', b'<?php foreach([] as list()=>$v){}'),
 ('prerequisite/key-list-holes', b'<?php foreach([] as list(,$k,)=>$v){}'),
 ('prerequisite/key-short-list', b'<?php foreach([] as [$k]=>$v){}'),
 ('prerequisite/key-short-holes', b'<?php foreach([] as [,$k,]=>$v){}'),
 ('prerequisite/key-list-ref', b'<?php foreach([] as [&$k]=>$v){}'),
 ('prerequisite/key-list-unpack', b'<?php foreach([] as [...$k]=>$v){}'),
 ('prerequisite/key-list-before-iterable', b'<?php foreach([[]=>1] as list($k)=>$v){}'),
 ('prerequisite/value-ref', b'<?php foreach([] as &$v){}'),
 ('prerequisite/value-ref-dim', b'<?php foreach([] as &$v[0]){}'),
 ('prerequisite/value-list-ref', b'<?php foreach([] as [&$v]){}'),
 ('prerequisite/value-nested-ref', b'<?php foreach([] as [[&$v]]){}'),
 ('prerequisite/value-list-hole', b'<?php foreach([] as [,$v,]){}'),
 ('prerequisite/value-genuine-hole', b'<?php foreach([] as list(,$v,)){}'),
 ('prerequisite/value-list-unpack', b'<?php foreach([] as [...$v]){}'),
 ('prerequisite/value-nested-unpack-ref', b'<?php foreach([] as [...[&$v]]){}'),
 ('prerequisite/value-long-nested', b'<?php foreach([] as [array($v)]){}'),
 ('prerequisite/value-mixed', b'<?php foreach([] as [list($v)]){}'),
 ('prerequisite/key-call', b'<?php foreach([] as foo()=>$v){}'),
 ('prerequisite/key-nullsafe', b'<?php foreach([] as $k?->p=>$v){}'),
 ('prerequisite/key-ref-multiline', b'<?php foreach(\n[[]=>1]\nas\n&$k\n=>\n$v\n){}'),
 ('prerequisite/vendor/php-src/Zend/tests/errmsg/errmsg_042.phpt',
  b'<?php\n\n$a = array(1,2,3);\nforeach ($a as &$k=>$v) {\n}\n\necho "Done\\n";\n?>\n'),
 ('prerequisite/vendor/php-src/Zend/tests/foreach/foreach_list_003.phpt',
  b"<?php\n\n$array = [['a', 'b'], 'c', 'd'];\n\nforeach($array as list($key) => list(list(), $a"
  b')) {\n}\n\n?>\n'),
 ('prerequisite/vendor/php-src/tests/lang/foreachLoop.006.phpt',
  b'<?php\n$a = array("a","b","c");\nforeach ($a as &$k=>$v) {\n  var_dump($v);\n}\n?>\n'),
 ('context/value-this', b'<?php foreach(\n[]\nas\n$this\n){}'),
 ('context/value-this-concat', b'<?php foreach(\n[]\nas\n${"th" . "is"}\n){}'),
 ('context/value-this-ternary', b'<?php foreach(\n[]\nas\n${true?"this":"x"}\n){}'),
 ('context/value-this-ref', b'<?php foreach(\n[]\nas\n&$this\n){}'),
 ('context/value-globals', b'<?php foreach(\n[]\nas\n$GLOBALS\n){}'),
 ('context/value-globals-concat', b'<?php foreach(\n[]\nas\n${"GLO"."BALS"}\n){}'),
 ('context/value-header', b'<?php foreach(\n[]\nas\n$http_response_header\n){}'),
 ('context/value-superglobal', b'<?php foreach(\n[]\nas\n$_SERVER\n){}'),
 ('context/key-this-after-cv', b'<?php foreach(\n[]\nas\n$this\n=>\n$v\n){}'),
 ('context/key-this-after-dim', b'<?php foreach(\n[]\nas\n$this\n=>\n$v[\n0\n]\n){}'),
 ('context/key-this-after-list', b'<?php foreach(\n[]\nas\n$this\n=>\n[$v,\n$w]\n){}'),
 ('context/key-globals', b'<?php foreach(\n[]\nas\n$GLOBALS\n=>\n$v\n){}'),
 ('context/key-header', b'<?php foreach(\n[]\nas\n$http_response_header\n=>\n$v\n){}'),
 ('context/value-call', b'<?php foreach(\n[]\nas\nfoo(\n)\n){}'),
 ('context/value-nullsafe', b'<?php foreach(\n[]\nas\n$x?->p\n){}'),
 ('context/value-call-ref', b'<?php foreach(\n[]\nas\n&foo(\n)\n){}'),
 ('context/key-call', b'<?php foreach(\n[]\nas\nfoo(\n)\n=>\n$v\n){}'),
 ('context/key-nullsafe', b'<?php foreach(\n[]\nas\n$x?->p\n=>\n$v\n){}'),
 ('context/value-list-empty', b'<?php foreach(\n[\n[]\n]\nas\nlist()\n){}'),
 ('context/value-list-spread', b'<?php foreach(\n[\n[]\n]\nas\n[...$v]\n){}'),
 ('context/value-list-mix', b'<?php foreach(\n[\n[]\n]\nas\n[list($v)]\n){}'),
 ('context/value-list-long', b'<?php foreach(\n[\n[]\n]\nas\n[array($v)]\n){}'),
 ('context/value-list-this', b'<?php foreach(\n[\n[]\n]\nas\n[$this]\n){}'),
 ('context/value-list-keyerror', b'<?php foreach(\n[\n[]\n]\nas\n[[]=>$v]\n){}'),
 ('context/iterable-hole-before-list', b'<?php foreach(\n[,1]\nas\n[...$v]\n){}'),
 ('context/iterable-key-before-list', b'<?php foreach(\n[[]=>1]\nas\n[...$v]\n){}'),
 ('context/iterable-dim-read', b'<?php foreach(\n$a[\n]\nas\n$v\n){}'),
 ('context/iterable-dim-ref', b'<?php foreach(\n$a[\n]\nas\n&$v\n){}'),
 ('context/iterable-dim-nested-ref', b'<?php foreach(\n$a[\n]\nas\n[&$v]\n){}'),
 ('context/iterable-literal-dim-ref', b'<?php foreach(\n[1][\n]\nas\n&$v\n){}'),
 ('context/iterable-nullsafe-ref', b'<?php foreach(\n$a?->p\nas\n&$v\n){}'),
 ('context/iterable-temp-ref', b'<?php foreach(\n[1,2]\nas\n&$v\n){echo $v;}'),
 ('context/iterable-temp-nested-ref', b'<?php foreach(\n[[1],[2]]\nas\n[&$v]\n){echo $v;}'),
 ('context/body-break', b'<?php foreach([] as $v){\nbreak;\n}'),
 ('context/body-break-depth', b'<?php foreach([] as $v){\nbreak 2;\n}'),
 ('context/body-array-hole', b'<?php foreach([] as $v){\n[,$x];\n}'),
 ('context/body-continue-nested', b'<?php foreach([] as $v){foreach([] as $w){continue 2;}}'),
 ('context/after-foreach-hole', b'<?php foreach(\n[]\nas $v){}\n[,$x];'),
 ('context/key-ref-before-bad-iterable', b'<?php foreach(\n[[]=>1]\nas &$k=>$v){}'),
 ('context/key-list-before-bad-iterable', b'<?php foreach(\n[[]=>1]\nas list($k)=>$v){}'),
 ('context/key-cv-value-keyedlist', b'<?php foreach(\n[[1]]\nas $k=>[0=>$v]){echo $k,$v;}'),
 ('context/value-list-ref-spread', b'<?php foreach(\n[[1]]\nas [...[&$v]]){}')]

BODY_CASES = [('brace', b'<?php foreach([] as $v)\n{\n[,$x];\n}', 2),
 ('nested', b'<?php foreach((([1])) as ${("v")})\n/* ) ( */\n{\n[,$x];\n}', 3),
 ('alternative', b'<?php foreach([] as $v)\n/* ) */\n:\n[,$x];\nendforeach;', 3),
 ('single', b'<?php foreach([] as $v)\n/* ) */\n[,$x];', 0),
 ('empty-single', b'<?php foreach([] as $v)\n;', 0),
 ('empty-brace', b'<?php foreach([] as $v)\n{\n}', 2),
 ('empty-alternative', b'<?php foreach([] as $v)\n:\nendforeach;', 2),
 ('nested-loops', b'<?php foreach([] as $v)\n{\nforeach([] as $w):\nbreak 3;\nendforeach;\n}', 2),
 ('parenthesized-target', b'<?php foreach(([1]) as $v[(0)])\n/* ( ) */\n{\n[,$x];\n}', 3),
 ('bodyless-following', b'<?php foreach([] as $v);\n[,$x];', 0)]

METADATA_CASES = [('value',
  b'<?php foreach($a as $v){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPR)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('ref',
  b'<?php foreach($a as &$v){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPW)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('listref',
  b'<?php foreach($a as [&$v]){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPW)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('nestedref',
  b'<?php foreach($a as [[&$v]]){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPW)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('temporaryref',
  b'<?php foreach([[1]] as [&$v]){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPR)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('computedref',
  b'<?php foreach(${$name} as &$v){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPW)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('dimensionref',
  b'<?php foreach($a[] as [&$v]){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPW)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('keyvalue',
  b'<?php foreach($a as $k=>$v[0]){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPR)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('globalsvalue',
  b'<?php foreach($a as $_SERVER){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPR)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('effectiterable',
  b'<?php foreach((list($x)=[[1]]) as $v){}',
  ['P.COMPLETION = PPCNORMAL',
   'P.LOOPS = 0',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 0]) = (PPR)',
   '$ppaccess(P, [PCINDEX 0, PCFIELD 3]) = (PPW)',
   '$access_paths(P.ACCESS) = $expression_paths(P.EXPRESSIONS)']),
 ('body-edit-None',
  b'<?php foreach([] as $v)\n{\n[,$x];\n}',
  ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing control body token line")', 'P.LOOPS = 0']),
 ('body-edit--1',
  b'<?php foreach([] as $v)\n{\n[,$x];\n}',
  ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")', 'P.LOOPS = 0']),
 ('body-edit-0',
  b'<?php foreach([] as $v)\n{\n[,$x];\n}',
  ['P.COMPLETION = PPCABRUPT (STATICERROR "Cannot use empty array elements in arrays" 3)',
   'P.LOOPS = 0']),
 ('body-edit-1',
  b'<?php foreach([] as $v)\n{\n[,$x];\n}',
  ['P.COMPLETION = PPCABRUPT (STATICERROR "Cannot use empty array elements in arrays" 3)',
   'P.LOOPS = 0']),
 ('body-edit-2',
  b'<?php foreach([] as $v)\n{\n[,$x];\n}',
  ['P.COMPLETION = PPCABRUPT (STATICERROR "Cannot use empty array elements in arrays" 3)',
   'P.LOOPS = 0']),
 ('body-edit-3',
  b'<?php foreach([] as $v)\n{\n[,$x];\n}',
  ['P.COMPLETION = PPCABRUPT (STATICERROR "Cannot use empty array elements in arrays" 3)',
   'P.LOOPS = 0']),
 ('body-edit-4',
  b'<?php foreach([] as $v)\n{\n[,$x];\n}',
  ['P.COMPLETION = PPCABRUPT (STATICERROR "Cannot use empty array elements in arrays" 3)',
   'P.LOOPS = 0']),
 ('body-edit-5',
  b'<?php foreach([] as $v)\n{\n[,$x];\n}',
  ['P.COMPLETION = PPCABRUPT (UNSUPPORTED "missing ordinary compiler line")', 'P.LOOPS = 0']),
 ('ending-cv',
  b'<?php foreach(\n$a\nas\n$v\n){}',
  ['P.COMPLETION = PPCNORMAL', 'P.LOCATION.LINE = 2', 'P.LOOPS = 0']),
 ('loop-depth-restored',
  b'<?php foreach(\n$a\nas\n$v\n){break;} break;',
  ['P.LOOPS = 0',
   'P.COMPLETION = PPCABRUPT (STATICBYTES ($ptascii("\'break\' not in the \'loop\' or \'switch\' '
   'context")) 5)'])]

PENDING = {
    'context/value-header': 'compile-time http_response_header context',
    'context/iterable-nullsafe-ref': 'ordinary expression or writable operand compilation',
}


def inputs():
    paths = [*compiler.SPECS, Path(__file__), ROOT/'frontend/worker.php',
             ROOT/'spec/schema.json', ROOT/'spec/lexer-encodings.json',
             types.PHP, types.ROOT/'.tools/php-file.so',
             types.ROOT/'_build/default/adapter/main.exe',
             types.ROOT/'tests/semantics/_build/default/numeric_runner.exe']
    return {'closure': types.syntax_validation.implementation_fingerprint(),
            'direct': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


def main():
    before=inputs();fixtures=[];records=[];pending=[];boundaries=[]
    adapter=types.Worker([str(types.ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    def worker(flags):
        return types.Worker([str(types.PHP),'-n',*flags,'-d',
                            'extension='+str(types.ROOT/'.tools/php-file.so'),str(ROOT/'frontend/worker.php')])
    def parse(frontend,source):
        parsed=frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
        assert parsed['accepted'],parsed
        return parsed['ast']
    def add(ast,checks):
        checked=adapter.request({'op':'check','ast':ast,'fixture':True})
        assert checked['ok'],checked
        n=len(fixtures)
        fixtures.append(f'dec $case{n}() : bool\ndef $case{n}() = true\n  -- if P = $ppstart(91, '
                        +checked['fixture']+', '+types.byte_expr(str(file))+')\n'
                        +''.join('  -- if '+check+'\n' for check in checks))
        return checked
    def lint(name,source,frontend,flags,body_line=None):
        ast=parse(frontend,source)
        if body_line is not None:
            assert ast['program'][0]['meta']['statementBodyLine']=={'int':str(body_line)},name
        file.write_bytes(source)
        command=[str(types.PHP),'-n',*flags,*types.FLAGS,'-l',str(file)]
        native=subprocess.run(command,capture_output=True,cwd=types.ROOT,env=types.ENV,timeout=10)
        checks=['$pptrace(P) = '+context.expected_events(context.events(native),file)]
        if native.returncode==0:checks.append('P.COMPLETION = PPCNORMAL')
        if name in PENDING:checks=['P.COMPLETION = PPCABRUPT (UNSUPPORTED '+json.dumps(PENDING[name])+')']
        checked=add(ast,checks)
        record={'id':name,**compiler.oracle_record(source,checked,command,native)}
        (pending if name in PENDING else records).append(record)
    try:
        with tempfile.TemporaryDirectory(dir=types.ROOT/'.tools') as tmp:
            file=(Path(tmp)/'input.php').resolve()
            frontend=worker([])
            try:
                for name,source in SOURCES:lint(name,source,frontend,[])
                for name,source,checks in METADATA_CASES:
                    ast=parse(frontend,source)
                    if name.startswith('body-edit-'):
                        value=name.removeprefix('body-edit-');meta=ast['program'][0]['meta']
                        if value=='None':meta.pop('statementBodyLine')
                        else:meta['statementBodyLine']={'int':value}
                    add(ast,checks)
                    boundaries.append({'id':name,'source_base64':base64.b64encode(source).decode(),'checks':checks})
            finally:frontend.close()
            for encoding in ['plain','UTF-16BE']:
                flags=[] if encoding=='plain' else ['-d','zend.multibyte=1','-d','internal_encoding=UTF-8']
                frontend=worker(flags)
                try:
                    for name,source,body_line in BODY_CASES:
                        if encoding!='plain':source=b'\xfe\xff'+source.decode().encode('utf-16be')
                        lint('body/'+encoding+'/'+name,source,frontend,flags,body_line)
                finally:frontend.close()
            fixture=Path(tmp)/'compiler.watsup'
            fixture.write_text(compiler.PREFIX+'\n'.join(fixtures)+'\ndec $main() : bool\ndef $main() = true\n'
                               +''.join(f'  -- if $case{i}()\n' for i in range(len(fixtures))))
            run=subprocess.run([str(types.ROOT/'tests/semantics/_build/default/numeric_runner.exe'),
                                *map(str,compiler.SPECS),str(fixture)],capture_output=True,text=True,timeout=120)
            if run.returncode or run.stdout.strip()!='true':
                failure=Path(tempfile.mkdtemp(prefix='foreach-source-compiler-failure-',dir=types.ROOT/'.tools'))
                (failure/'compiler.watsup').write_text(fixture.read_text())
                (failure/'results.json').write_text(json.dumps({'inputs':before,'records':records,'pending':pending,
                    'boundaries':boundaries,'status':run.returncode,'stdout':run.stdout,'stderr':run.stderr},indent=2)+'\n')
                raise AssertionError((str(failure),run.stdout,run.stderr))
    finally:adapter.close()
    assert before==inputs(),'foreach compiler inputs changed'
    report={'scope':'Foreach compiler/body contexts and access metadata; two explicit pending core boundaries do not count as native agreements',
            'fingerprint':before,'profile':types.PROFILE,'records':records,'pending':pending,'boundaries':boundaries}
    REPORT.write_text(json.dumps(report,indent=2)+'\n')
    print(len(records),'native lints (including 20 body profiles);',len(boundaries),
          'access/metadata/depth controls;',len(pending),'explicit pending core boundaries')


if __name__=='__main__':main()
