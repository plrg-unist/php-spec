#!/usr/bin/env python3
"""Bare yield/exit reduction context and existing parenthesized exit spans."""
import base64,copy
from validate import ROOT,Worker,require,normalize,structurally_equal
from destructuring_metadata import nodes
CASES=[
 (b'<?php [yield\n ,\n ,];','Expr_Yield',2),
 (b'<?php [yield  ,\n\n,];','Expr_Yield',1),
 (b'<?php [yield /*\n*/,];','Expr_Yield',2),
 (b'<?php [yield 1\n,];','Expr_Yield',None),
 (b'<?php [yield 1=>2\n,];','Expr_Yield',None),
 (b'<?php [exit\n ,\n ,];','Expr_Exit',2),
 (b'<?php [exit  ,\n\n,];','Expr_Exit',1),
 (b'<?php [die /*\n*/,];','Expr_Exit',2),
 (b'<?php [exit(\n)\n,];','Expr_Exit',None),
 (b'<?php [die( /*\n*/\n),];','Expr_Exit',None),
 (b'<?php [exit(1\n)\n,];','Expr_Exit',None),
]
def main():
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)]);checks=0;profiles=0
    try:
        for encoding in ('plain','UTF-16BE'):
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',* ([] if encoding=='plain' else ['-d','zend.multibyte=1','-d','internal_encoding=UTF-8']),str(ROOT/'frontend/worker.php')])
            try:
                for source,kind,expected in CASES:
                    code=source if encoding=='plain' else b'\xfe\xff'+source.decode().encode('utf-16be')
                    ast=require(frontend.call(op='parse',source=base64.b64encode(code).decode()),'parse')['ast'];target=next(nodes(ast,kind))
                    assert target['meta'].get('nullaryExprLine')==(None if expected is None else {'int':str(expected)}),(source,target)
                    checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                    printed=require(frontend.call(op='print',ast=checked['ast']),'print');assert printed['ast']==ast
                    reparsed=require(frontend.call(op='parse',source=printed['source']),'reparse');assert reparsed['accepted'];assert structurally_equal(normalize(ast),normalize(reparsed['ast']));checks+=5;profiles+=1
                    for value in (None,{'int':'0'},{'int':'-1'},{'int':'91'}):
                        edited=copy.deepcopy(ast);target=next(nodes(edited,kind))
                        if value is None:target['meta'].pop('nullaryExprLine',None)
                        else:target['meta']['nullaryExprLine']=value
                        checked=require(adapter.call(op='check',ast=edited),'edited context');assert checked['ast']==edited
                        printed=require(frontend.call(op='print',ast=checked['ast']),'edited print');assert printed['ast']==edited;checks+=2
                    for value in (True,'2',None,{'bytes':'Mg=='},{'int':'02'}):
                        edited=copy.deepcopy(ast);next(nodes(edited,kind))['meta']['nullaryExprLine']=value
                        assert not adapter.call(op='check',ast=edited).get('ok');checks+=1
            finally:frontend.close()
    finally:adapter.close()
    print(profiles,'nullary reduction source/encoding profiles;',checks,'checked boundaries passed')
if __name__=='__main__':main()
