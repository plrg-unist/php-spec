#!/usr/bin/env python3
"""Destructuring retains nested spread flags through checked syntax."""
import base64,copy
from validate import ROOT,Worker,require,normalize,structurally_equal


def nodes(value,kind):
    if isinstance(value,dict):
        if value.get('node')==kind:yield value
        for child in value.values():yield from nodes(child,kind)
    elif isinstance(value,list):
        for child in value:yield from nodes(child,kind)


def main():
    cases=[
        ('<?php [...[$x]]=$a;',1),
        ('<?php [...$x]=$a;',1),
        ('<?php [[...[$x]]]=$a;',1),
        ('<?php [...[...[$x]]]=$a;',2),
        ('<?php [...[&$x]]=$a;',1),
        ('<?php [...[, $x, ,]]=$a;',1),
        ('<?php [...array($x)]=$a;',1),
        ('<?php foreach($a as [...[$x]]){}',1),
        ('<?php [[[$x]]]=$a;',0),
        ('<?php [list($x)]=$a;',0),
        ('<?php [/*...*/[$x]]=$a;',0),
    ]
    profiles=[(source.encode(),{},count) for source,count in cases]
    for source,count in cases[:4]:
        profiles.append((b'\xff\xfe'+source.encode('utf-16le'),{'zend.multibyte':'1','internal_encoding':'UTF-8'},count))
    profiles.append((b'<?php [...[/*\xff*/$x]]=$a;',{'zend.multibyte':'1','internal_encoding':'UTF-8','zend.script_encoding':'ISO-8859-1'},1))
    profiles=[(*profile,None) for profile in profiles]
    styles=[
        ('<?php [array($x)]=$a;',[(2,2,0),(2,1,0)]),
        ('<?php [[$x]]=$a;',[(2,2,0),(2,2,0)]),
        ('<?php [list($x)]=$a;',[(2,2,0),(1,None,0)]),
        ('<?php list(array($x))=$a;',[(1,None,0)]),
        ('<?php [array(,$x)]=$a;',[(2,2,0),(2,1,1)]),
        ('<?php [array($x,,)]=$a;',[(2,2,0),(2,1,1)]),
        ('<?php [array(,)]=$a;',[(2,2,0),(2,1,1)]),
        ('<?php [array()]=$a;',[(2,2,0),(2,1,0)]),
        ('<?php [[,$x]]=$a;',[(2,2,0),(2,2,1)]),
        ('<?php [list(,$x)]=$a;',[(2,2,0),(1,None,1)]),
        ('<?php [array($x),[$y],list($z)]=$a;',[(2,2,0),(2,1,0),(2,2,0),(1,None,0)]),
        ('<?php [array(array($x))]=$a;',[(2,2,0),(2,1,0),(2,1,0)]),
        ('<?php foreach($a as [array(,$x)]){}',[(2,2,0),(2,1,1)]),
        ('<?php [array(/*,*/$x)]=$a;',[(2,2,0),(2,1,0)]),
    ]
    profiles += [(source.encode(),{},0,expected) for source,expected in styles]
    for source,expected in [styles[0],styles[4],styles[5],styles[9]]:
        profiles.append((b'\xff\xfe'+source.encode('utf-16le'),{'zend.multibyte':'1','internal_encoding':'UTF-8'},0,expected))
    profiles.append((b'<?php [array(/*\xff*/,$x)]=$a;',{'zend.multibyte':'1','internal_encoding':'UTF-8','zend.script_encoding':'ISO-8859-1'},0,[(2,2,0),(2,1,1)]))
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    checks=0
    try:
        for source,ini,count,expected_styles in profiles:
            flags=[flag for key,value in ini.items() for flag in ['-d',key+'='+value]]
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',*flags,str(ROOT/'frontend/worker.php')])
            try:
                parsed=require(frontend.call(op='parse',source=base64.b64encode(source).decode()),'parse');assert parsed['accepted'],parsed
                ast=parsed['ast'];assert sum(n['fields'][3] for n in nodes(ast,'ArrayItem'))==count
                if expected_styles is not None:
                    actual=[(int(n['meta']['kind']['int']),int(n['meta']['destructuringArrayKind']['int']) if 'destructuringArrayKind' in n['meta'] else None,sum(item is None for item in n['fields'][0])) for n in nodes(ast,'Expr_List')]
                    assert actual==expected_styles,(source,actual,expected_styles)
                checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                printed=require(frontend.call(op='print',ast=checked['ast']),'print');assert printed['ast']==ast
                reparsed=require(frontend.call(op='parse',source=printed['source']),'reparse');assert reparsed['accepted']
                assert structurally_equal(normalize(ast),normalize(reparsed['ast']))
                assert sum(n['fields'][3] for n in nodes(reparsed['ast'],'ArrayItem'))==count
                if expected_styles is not None:
                    actual=[(int(n['meta']['kind']['int']),int(n['meta']['destructuringArrayKind']['int']) if 'destructuringArrayKind' in n['meta'] else None,sum(item is None for item in n['fields'][0])) for n in nodes(reparsed['ast'],'Expr_List')]
                    assert actual==expected_styles,(source,actual,expected_styles)
                    checks+=1
                checks+=6
                if expected_styles is not None and any(kind==1 for _,kind,_ in expected_styles):
                    for kind in [None,1,2]:
                        edited=copy.deepcopy(ast);target=next(n for n in nodes(edited,'Expr_List') if n['meta'].get('destructuringArrayKind')=={'int':'1'})
                        if kind is None:target['meta'].pop('destructuringArrayKind')
                        else:target['meta']['destructuringArrayKind']={'int':str(kind)}
                        changed=require(adapter.call(op='check',ast=edited),'edited array kind');assert changed['ast']==edited
                        output=require(frontend.call(op='print',ast=changed['ast']),'edited kind printing');assert output['ast']==edited
                        roundtrip=require(frontend.call(op='parse',source=output['source']),'edited kind reparsing');assert roundtrip['accepted']
                        assert structurally_equal(normalize(edited),normalize(roundtrip['ast']))
                        checks+=4
                    for kind in [True,'1',None,{'bytes':'MQ=='}]:
                        edited=copy.deepcopy(ast);target=next(n for n in nodes(edited,'Expr_List') if n['meta'].get('destructuringArrayKind')=={'int':'1'});target['meta']['destructuringArrayKind']=kind
                        assert not adapter.call(op='check',ast=edited).get('ok');checks+=1
            finally:frontend.close()
    finally:adapter.close()
    print(len(profiles),'destructuring source/encoding profiles;',checks,'spread/style transport checks passed')


if __name__=='__main__':main()
