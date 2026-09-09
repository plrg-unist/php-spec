#!/usr/bin/env python3
"""Legacy Clone nodes retain the pinned PHP8.5 synthetic-call reduction line."""
import base64,copy
from validate import ROOT,Worker,require,normalize,structurally_equal
from destructuring_metadata import nodes
CASES=[
 (b'<?php [clone $x\n ,\n ,];',[2]),(b'<?php [clone $x  ,\n\n,];',[1]),
 (b'<?php [clone($x)\n ,\n ,];',[2]),(b'<?php [CLONE $x\n,];',[2]),
 (b'<?php [clone($x\n),];',[2]),(b'<?php [clone $x /*\n*/,];',[2]),
 (b'<?php [clone clone $x\n,];',[2,2]),
 (b'<?php [clone(value:$x\n),];',[]),(b'<?php [clone(...$x\n),];',[]),
 (b'<?php [\\clone($x\n),];',[]),(b'<?php [namespace\\clone($x\n),];',[]),
]
def main():
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)]);checks=0;profiles=0
    try:
        for encoding in ('plain','UTF-16BE'):
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',* ([] if encoding=='plain' else ['-d','zend.multibyte=1','-d','internal_encoding=UTF-8']),str(ROOT/'frontend/worker.php')])
            try:
                for source,expected in CASES:
                    code=source if encoding=='plain' else b'\xfe\xff'+source.decode().encode('utf-16be')
                    ast=require(frontend.call(op='parse',source=base64.b64encode(code).decode()),'parse')['ast'];targets=list(nodes(ast,'Expr_Clone'))
                    assert [int(n['meta']['cloneExprLine']['int']) for n in targets]==expected,(source,targets)
                    checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                    printed=require(frontend.call(op='print',ast=checked['ast']),'print');assert printed['ast']==ast
                    reparsed=require(frontend.call(op='parse',source=printed['source']),'reparse');assert reparsed['accepted'];assert structurally_equal(normalize(ast),normalize(reparsed['ast']));checks+=5;profiles+=1
                    if not targets:continue
                    for value in (None,{'int':'0'},{'int':'-1'},{'int':'91'}):
                        edited=copy.deepcopy(ast);target=next(nodes(edited,'Expr_Clone'))
                        if value is None:target['meta'].pop('cloneExprLine')
                        else:target['meta']['cloneExprLine']=value
                        checked=require(adapter.call(op='check',ast=edited),'edited context');assert checked['ast']==edited
                        printed=require(frontend.call(op='print',ast=checked['ast']),'edited print');assert printed['ast']==edited;checks+=2
                    for value in (True,'2',None,{'bytes':'Mg=='},{'int':'02'}):
                        edited=copy.deepcopy(ast);next(nodes(edited,'Expr_Clone'))['meta']['cloneExprLine']=value
                        assert not adapter.call(op='check',ast=edited).get('ok');checks+=1
            finally:frontend.close()
    finally:adapter.close()
    print(profiles,'clone reduction source/encoding profiles;',checks,'checked boundaries passed')
if __name__=='__main__':main()
