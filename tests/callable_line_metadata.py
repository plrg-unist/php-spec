#!/usr/bin/env python3
"""Token-derived dynamic callable invocation lines survive checked transport."""
import base64,copy
from validate import ROOT,Worker,require,normalize,structurally_equal
from destructuring_metadata import nodes

CASES=[
 (b'<?php\n$f\n( \n1\n)++;',[3]),
 (b'<?php\n$f (\n\n1\n)++;',[2]),
 (b'<?php\nfoo\n(\n[&$q[]]\n)++;',[None]),
 (b'<?php\n(\n$f\n)()++;',[4]),
 (b'<?php\n$f\n(\n[&$q[]]\n)++;',[3]),
 (b'<?php $a[0]\n();',[2]),
 (b'<?php foo()\n();',[2, None]),
 (b'<?php ($a->foo())\n();',[2]),
 (b'<?php $a->foo();',[]),
 (b'<?php A::foo();',[]),
 (b'<?php $a?->foo();',[]),
 (b'<?php ("f")\n();',[2]),
 (b'<?php $f /*\n comment\n*/\n();',[4]),
 (b'<?php $f\r\n();',[2]),
 (b'<?php $f(...);',[1]),
 (b'<?php foo(...);',[None]),
 (b'<?php $f(\n$x\n);',[1]),
]

def main():
    profiles=[(source,{},expected) for source,expected in CASES]
    profiles += [(b'\xff\xfe'+source.decode().encode('utf-16le'),{'zend.multibyte':'1','internal_encoding':'UTF-8'},expected) for source,expected in CASES]
    profiles.append((b'<?php $f/*\xff*/\n();',{'zend.multibyte':'1','internal_encoding':'UTF-8','zend.script_encoding':'ISO-8859-1'},[2]))
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    checks=0;pair=[]
    try:
        for source,ini,expected in profiles:
            flags=[flag for key,value in ini.items() for flag in ['-d',key+'='+value]]
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',*flags,str(ROOT/'frontend/worker.php')])
            try:
                parsed=require(frontend.call(op='parse',source=base64.b64encode(source).decode()),'parse');assert parsed['accepted'],parsed
                ast=parsed['ast'];actual=[int(n['meta']['callableExprLine']['int']) if 'callableExprLine' in n['meta'] else None for n in nodes(ast,'Expr_FuncCall')];assert actual==expected,(source,actual,expected)
                checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                printed=require(frontend.call(op='print',ast=checked['ast']),'print');assert printed['ast']==ast
                reparsed=require(frontend.call(op='parse',source=printed['source']),'reparse');assert reparsed['accepted'];assert structurally_equal(normalize(ast),normalize(reparsed['ast']))
                checks+=5
                if source in (CASES[0][0],CASES[1][0]):pair.append(ast)
                if any(line is not None for line in expected):
                    for value in [None,{'int':'7'}]:
                        edited=copy.deepcopy(ast);target=next(n for n in nodes(edited,'Expr_FuncCall') if 'callableExprLine' in n['meta'])
                        if value is None:target['meta'].pop('callableExprLine')
                        else:target['meta']['callableExprLine']=value
                        changed=require(adapter.call(op='check',ast=edited),'edited callable line');assert changed['ast']==edited
                        output=require(frontend.call(op='print',ast=changed['ast']),'edited line printing');assert output['ast']==edited
                        roundtrip=require(frontend.call(op='parse',source=output['source']),'edited line reparse');assert roundtrip['accepted']
                        assert structurally_equal(normalize(edited),normalize(roundtrip['ast']));checks+=4
                    for value in [True,'2',None,{'bytes':'Mg=='}]:
                        edited=copy.deepcopy(ast);target=next(n for n in nodes(edited,'Expr_FuncCall') if 'callableExprLine' in n['meta']);target['meta']['callableExprLine']=value
                        assert not adapter.call(op='check',ast=edited).get('ok');checks+=1
            finally:frontend.close()
    finally:adapter.close()
    assert len(pair)==2 and pair[0]!=pair[1]
    for ast in pair:
        for node in nodes(ast,'Expr_FuncCall'):node['meta'].pop('callableExprLine',None)
    assert pair[0]==pair[1];checks+=2
    print(len(profiles),'callable creation source/encoding profiles;',checks,'checked transport boundaries passed')

if __name__=='__main__':main()
