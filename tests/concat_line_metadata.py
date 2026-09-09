#!/usr/bin/env python3
"""Concat reduction lookahead is checked context, independent of constant facts."""
import base64,copy
from validate import ROOT,Worker,require,normalize,structurally_equal
from destructuring_metadata import nodes
CASES=[
 (b'<?php ["a" . "b"];',[1]),
 (b'<?php [("a" . "b"\n)];',[2]),
 (b'<?php ["a" . "b"\n];',[2]),
 (b'<?php ["a" . "b"/*\n*/];',[2]),
 (b'<?php [("a" . "b"/*\n*/\n)];',[3]),
 (b'<?php [(("a" . "b"\n)\n)];',[2]),
 (b'<?php ["a" . ("b"\n)\n];',[3]),
 (b'<?php [("a"\n) . "b"\n];',[3]),
 (b'<?php [(1 . 2\n)];',[2]),
 (b'<?php [(1.5 . 2.5\n)];',[2]),
 (b'<?php [((-1) . "b"\n)];',[2]),
 (b'<?php [(true . "b"\n)];',[2]),
 (b'<?php [((true?"a":"x") . "b"\n)];',[2]),
 (b'<?php [("a" . ("b" . "c"\n)\n)];',[3,2]),
 (b'<?php [(<<<END\na\nEND\n. "b"\n)];',[5]),
]
def main():
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)]);checks=0;profiles=0
    try:
        for encoding in ('plain','UTF-16BE'):
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',* ([] if encoding=='plain' else ['-d','zend.multibyte=1','-d','internal_encoding=UTF-8']),str(ROOT/'frontend/worker.php')])
            try:
                for source,expected in CASES:
                    code=source if encoding=='plain' else b'\xfe\xff'+source.decode().encode('utf-16be')
                    ast=require(frontend.call(op='parse',source=base64.b64encode(code).decode()),'parse')['ast']
                    assert [int(n['meta']['concatExprLine']['int']) for n in nodes(ast,'Expr_BinaryOp_Concat')]==expected
                    checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                    printed=require(frontend.call(op='print',ast=checked['ast']),'print');assert printed['ast']==ast
                    reparsed=require(frontend.call(op='parse',source=printed['source']),'reparse');assert reparsed['accepted'];assert structurally_equal(normalize(ast),normalize(reparsed['ast']));checks+=5;profiles+=1
                    for value in (None,{'int':'0'},{'int':'-1'},{'int':'91'}):
                        edited=copy.deepcopy(ast);target=next(nodes(edited,'Expr_BinaryOp_Concat'))
                        if value is None:target['meta'].pop('concatExprLine')
                        else:target['meta']['concatExprLine']=value
                        checked=require(adapter.call(op='check',ast=edited),'edited context');assert checked['ast']==edited
                        printed=require(frontend.call(op='print',ast=checked['ast']),'edited print');assert printed['ast']==edited;checks+=2
                    for value in (True,'2',None,{'bytes':'Mg=='},{'int':'02'}):
                        edited=copy.deepcopy(ast);next(nodes(edited,'Expr_BinaryOp_Concat'))['meta']['concatExprLine']=value
                        assert not adapter.call(op='check',ast=edited).get('ok');checks+=1
            finally:frontend.close()
    finally:adapter.close()
    print(profiles,'concat reduction source/encoding profiles;',checks,'checked boundaries passed')
if __name__=='__main__':main()
