#!/usr/bin/env python3
"""Ordinary array omissions remain checked syntax with stable item indices."""
import base64,copy
from validate import ROOT,Worker,require,normalize,structurally_equal
from destructuring_metadata import nodes
CASES=[
 (b'<?php [\n,\n];', [([None],2)]),
 (b'<?php [\n\n,\n];', [([None],3)]),
 (b'<?php [1,,2,,];', [([True,None,True,None],None)]),
 (b'<?php [,,];', [([None,None],1)]),
 (b'<?php array(,,);', [([None,None],1)]),
 (b'<?php array(1,,2,,);', [([True,None,True,None],None)]),
 (b'<?php [];', [([],None)]),
 (b'<?php array();', [([],None)]),
 (b'<?php [1,];', [([True],None)]),
 (b'<?php [\n/* comma , */\n,\n];', [([None],3)]),
 (b'<?php [1,/* before hole */ ,/* after hole */];', [([True,None],None)]),
 (b'<?php false && [,$x];', [([None,True],1)]),
 (b'<?php true || array(,$x);', [([None,True],1)]),
 (b'<?php [true ? 1 : [,]];', [([True],None),([None],1)]),
 (b'<?php [[,],,];', [([True,None],None),([None],1)]),
 (b'<?php [list(,$x),,];', [([True,None],None)]),
]
def main():
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    checks=0;profiles=0;pair=[]
    try:
        for encoding in ('plain','UTF-16BE'):
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',* ([] if encoding=='plain' else ['-d','zend.multibyte=1','-d','internal_encoding=UTF-8']),str(ROOT/'frontend/worker.php')])
            try:
                for source,expected in CASES:
                    code=source if encoding=='plain' else b'\xfe\xff'+source.decode().encode('utf-16be')
                    parsed=require(frontend.call(op='parse',source=base64.b64encode(code).decode()),'parse');assert parsed['accepted'],parsed
                    ast=parsed['ast'];arrays=nodes(ast,'Expr_Array')
                    actual=[([True if item is not None else None for item in n['fields'][0]],int(n['meta']['arrayFirstHoleLine']['int']) if 'arrayFirstHoleLine' in n['meta'] else None) for n in arrays]
                    assert actual==expected,(source,actual,expected)
                    checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                    printed=require(frontend.call(op='print',ast=checked['ast']),'print');assert printed['ast']==ast
                    reparsed=require(frontend.call(op='parse',source=printed['source']),'reparse');assert reparsed['accepted'];assert structurally_equal(normalize(ast),normalize(reparsed['ast']))
                    printed_again=require(frontend.call(op='print',ast=reparsed['ast']),'print again');assert printed_again['source']==printed['source'];checks+=6;profiles+=1
                    if encoding=='plain' and source in (CASES[0][0],CASES[1][0]):pair.append(ast)
                    if any(line is not None for _,line in expected):
                        for value in (None,{'int':'0'},{'int':'-1'},{'int':'91'}):
                            edited=copy.deepcopy(ast);node=next(n for n in nodes(edited,'Expr_Array') if 'arrayFirstHoleLine' in n['meta'])
                            if value is None:node['meta'].pop('arrayFirstHoleLine')
                            else:node['meta']['arrayFirstHoleLine']=value
                            checked=require(adapter.call(op='check',ast=edited),'edited line');assert checked['ast']==edited
                            output=require(frontend.call(op='print',ast=checked['ast']),'edited line print');assert output['ast']==edited
                            checks+=2
                        for value in (True,'2',None,{'bytes':'Mg=='},{'int':'02'}):
                            edited=copy.deepcopy(ast);node=next(n for n in nodes(edited,'Expr_Array') if 'arrayFirstHoleLine' in n['meta']);node['meta']['arrayFirstHoleLine']=value
                            assert not adapter.call(op='check',ast=edited).get('ok');checks+=1
                    for value in (True,{'node':'Expr_Variable','fields':[{'bytes':'eA=='}],'meta':{}},{'int':'1'}):
                        edited=copy.deepcopy(ast);next(nodes(edited,'Expr_Array'))['fields'][0]=[value]
                        assert not adapter.call(op='check',ast=edited).get('ok');checks+=1
            finally:frontend.close()
    finally:adapter.close()
    assert pair[0]!=pair[1];checks+=1
    print(profiles,'ordinary omission source/encoding profiles;',checks,'checked boundaries passed')
if __name__=='__main__':main()
