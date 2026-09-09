#!/usr/bin/env python3
"""Destructuring retains nested spread flags through checked syntax."""
import base64
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
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    checks=0
    try:
        for source,ini,count in profiles:
            flags=[flag for key,value in ini.items() for flag in ['-d',key+'='+value]]
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',*flags,str(ROOT/'frontend/worker.php')])
            try:
                parsed=require(frontend.call(op='parse',source=base64.b64encode(source).decode()),'parse');assert parsed['accepted'],parsed
                ast=parsed['ast'];assert sum(n['fields'][3] for n in nodes(ast,'ArrayItem'))==count
                checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                printed=require(frontend.call(op='print',ast=checked['ast']),'print');assert printed['ast']==ast
                reparsed=require(frontend.call(op='parse',source=printed['source']),'reparse');assert reparsed['accepted']
                assert structurally_equal(normalize(ast),normalize(reparsed['ast']))
                assert sum(n['fields'][3] for n in nodes(reparsed['ast'],'ArrayItem'))==count
                checks+=6
            finally:frontend.close()
    finally:adapter.close()
    print(len(profiles),'destructuring source/encoding profiles;',checks,'spread transport checks passed')


if __name__=='__main__':main()
