#!/usr/bin/env python3
"""Actual grouping reductions survive checked ternary transport."""
import base64, copy
from validate import ROOT, Worker, require, normalize, structurally_equal


def ternaries(value):
    if isinstance(value, dict):
        if value.get('node') == 'Expr_Ternary':
            yield value
        for child in value.values():
            yield from ternaries(child)
    elif isinstance(value, list):
        for child in value:
            yield from ternaries(child)


def main():
    cases = [
        ('<?php echo 1?2:3;', [False]),
        ('<?php echo (1?2:3);', [True]),
        ('<?php echo ((1?2:3));', [True]),
        ('<?php echo 1?2:3?4:5;', [False, False]),
        ('<?php echo (1?2:3)?4:5;', [False, True]),
        ('<?php echo 1?2:(3?4:5);', [False, True]),
        ('<?php f(1?2:3);', [False]),
        ('<?php f((1?2:3));', [True]),
        ('<?php if(1?2:3){}', [False]),
        ('<?php echo 1?:2?:3;', [False, False]),
        ('<?php echo (1?:2)?3:4;', [False, True]),
        ('<?php echo (/*(*/1?2:3/*)*/)?4:5;', [False, True]),
        ('<?php echo [1?2:3?4:5];', [False, False]),
    ]
    profiles=[(source.encode(),{},expected) for source,expected in cases]
    for source,expected in cases[:5]:
        profiles.append((b'\xff\xfe'+source.encode('utf-16le'),{'zend.multibyte':'1','internal_encoding':'UTF-8'},expected))
    profiles.append((b'<?php echo (/*\xff*/1?2:3)?4:5;',{'zend.multibyte':'1','internal_encoding':'UTF-8','zend.script_encoding':'ISO-8859-1'},[False,True]))
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    count=0
    try:
        for source,ini,expected in profiles:
            flags=[flag for key,value in ini.items() for flag in ['-d',key+'='+value]]
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',*flags,str(ROOT/'frontend/worker.php')])
            try:
                parsed=require(frontend.call(op='parse',source=base64.b64encode(source).decode()),'parse');assert parsed['accepted'],parsed
                ast=parsed['ast'];assert [n['meta']['parenthesizedConditional'] for n in ternaries(ast)]==expected
                checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                printed=require(frontend.call(op='print',ast=checked['ast']),'print');assert printed['ast']==ast
                reparsed=require(frontend.call(op='parse',source=printed['source']),'reparse');assert reparsed['accepted']
                assert structurally_equal(normalize(ast),normalize(reparsed['ast']))
                for value in [None,False,True]:
                    edited=copy.deepcopy(ast);node=next(ternaries(edited))
                    if value is None:node['meta'].pop('parenthesizedConditional')
                    else:node['meta']['parenthesizedConditional']=value
                    result=require(adapter.call(op='check',ast=edited),'edited grouping');assert result['ast']==edited
                for value in [{'int':'1'},'true',1,None]:
                    edited=copy.deepcopy(ast);next(ternaries(edited))['meta']['parenthesizedConditional']=value
                    assert not adapter.call(op='check',ast=edited).get('ok')
                count+=12
            finally:frontend.close()
    finally:adapter.close()
    print(len(profiles),'grouping source/encoding profiles;',count,'transport checks passed')


if __name__=='__main__':main()
