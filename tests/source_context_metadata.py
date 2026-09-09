#!/usr/bin/env python3
"""Retain compiler token lines through checked byte-safe source transport."""
import base64
import copy
import json
from validate import ROOT, Worker, require, normalize, structurally_equal


def main():
    text='<?php namespace\n/* { }\n */\n{\n}\n'
    cases=[
        (text.encode(),{},4),
        (b'<?php namespace\r\n// {}\r\n{\r\n}\r\n',{},3),
        (b'\xff\xfe'+text.encode('utf-16le'),{'zend.multibyte':'1','internal_encoding':'UTF-8'},4),
        (b'<?php namespace\n/*\xff { }*/\n{\n}\n',{'zend.multibyte':'1','internal_encoding':'UTF-8','zend.script_encoding':'ISO-8859-1'},3),
    ]
    cases=[(source,ini,line,'namespaceBraceLine') for source,ini,line in cases]
    for keyword in ['break','continue']:
        for source,line in [
            ('<?php '+keyword+';',1),
            ('<?php '+keyword+'\n/* comment */\n;',3),
            ('<?php '+keyword+' ?>\na',1),
            ('<?php '+keyword+' /*x*/ ?>\r\n',1),
            ('<?php while(true){ '+keyword+'\n; }',2),
            ('<?php '+keyword+' 1\n;',2),
        ]:
            cases.append((source.encode(),{},line,'statementTerminatorLine'))
        source='<?php '+keyword+'\n?>\n'
        cases.append((b'\xff\xfe'+source.encode('utf-16le'),{'zend.multibyte':'1','internal_encoding':'UTF-8'},2,'statementTerminatorLine'))
        source=('<?php '+keyword+'\n/*').encode()+b'\xff'+b'*/ ?>\r\n'
        cases.append((source,{'zend.multibyte':'1','internal_encoding':'UTF-8','zend.script_encoding':'ISO-8859-1'},2,'statementTerminatorLine'))
    cases=[(*case,None) for case in cases]
    for text,line,tag in [
        ('<?php if(true)\n{}',2,'Stmt_If'),
        ('<?php if(true)\n:\nendif;',2,'Stmt_If'),
        ('<?php if(true);',0,'Stmt_If'),
        ('<?php if(false);elseif(true)\n{}',2,'Stmt_ElseIf'),
        ('<?php if(false):elseif(true)\n:\nendif;',2,'Stmt_ElseIf'),
        ('<?php if(false){}\nelse\n{}',3,'Stmt_Else'),
        ('<?php if(false):else\n:\nendif;',2,'Stmt_Else'),
        ('<?php while(false)\n/* ( ) */\n{}',3,'Stmt_While'),
        ('<?php while(false)\n:\nendwhile;',2,'Stmt_While'),
        ('<?php while(false);',0,'Stmt_While'),
        ('<?php do\n{}while(false);',2,'Stmt_Do'),
        ('<?php do;while(false);',0,'Stmt_Do'),
        ('<?php for(;;)\n{/*comment*/}',2,'Stmt_For'),
        ('<?php for(;;)\n:/*comment*/endfor;',2,'Stmt_For'),
        ('<?php for(;;)/*comment*/;',0,'Stmt_For'),
        ('<?php if(")")\n/* ( */\n{}',3,'Stmt_If'),
        ('<?php if ((function($x){return "(";})(")"))\n{}',2,'Stmt_If'),
    ]:
        cases.append((text.encode(),{},line,'statementBodyLine',tag))
    for text,line in [
        ('<?php for(;;)\n;',2),
        ('<?php for(;;)\n/*comment*/\n;',3),
        ('<?php for(;;)\n?>\n',2),
        ('<?php for(;;)\r\n?>\r\n',2),
    ]:
        cases.append((text.encode(),{},line,'statementTerminatorLine','Stmt_For'))
    text='<?php if(true)\n/* \u00e9 ( */\n{}'
    cases.append((b'\xff\xfe'+text.encode('utf-16le'),{'zend.multibyte':'1','internal_encoding':'UTF-8'},3,'statementBodyLine','Stmt_If'))
    text=b'<?php for(;;)\n/*\xff*/\n;'
    cases.append((text,{'zend.multibyte':'1','internal_encoding':'UTF-8','zend.script_encoding':'ISO-8859-1'},3,'statementTerminatorLine','Stmt_For'))
    def target(ast,key,tag=None):
        pending=[ast]
        while pending:
            value=pending.pop()
            if isinstance(value,dict):
                if key in value.get('meta',{}) and (tag is None or value.get('node')==tag):return value
                pending.extend(value.values())
            elif isinstance(value,list):pending.extend(value)
        raise AssertionError(key)
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    checks=0
    try:
        for source,ini,line,key,tag in cases:
            flags=[item for key,value in ini.items() for item in ['-d',key+'='+value]]
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',*flags,str(ROOT/'frontend/worker.php')])
            try:
                parsed=require(frontend.call(op='parse',source=base64.b64encode(source).decode()),'parse')
                assert parsed['accepted'],parsed
                original=parsed['ast']; node=target(original,key,tag)
                assert node['meta'][key]=={'int':str(line)}
                checked=require(adapter.call(op='elaborate',ast=original,fixture=True),'checked metadata')
                assert checked['ast']==original
                printed=require(frontend.call(op='print',ast=checked['ast']),'fresh printing')
                assert printed['ast']==original
                reparsed=require(frontend.call(op='parse',source=printed['source']),'printed parsing')
                assert reparsed['accepted'] and structurally_equal(normalize(original),normalize(reparsed['ast']))
                # Fresh printer uses checked syntax, not location metadata to replay original text.
                changed=copy.deepcopy(original);target(changed,key,tag)['meta'][key]={'int':'99'}
                changed=require(adapter.call(op='elaborate',ast=changed),'edited metadata')['ast']
                assert target(changed,key,tag)['meta'][key]=={'int':'99'}
                assert require(frontend.call(op='print',ast=changed),'edited printing')['source']==printed['source']
                absent=copy.deepcopy(original);del target(absent,key,tag)['meta'][key]
                assert require(adapter.call(op='elaborate',ast=absent),'absent metadata')['ast']==absent
                malformed=copy.deepcopy(original);target(malformed,key,tag)['meta'][key]={'bytes':'MQ=='}
                assert not adapter.call(op='check',ast=malformed)['ok']
                bad_fixture=checked['fixture'].replace(f'M{key} ({line})',f'M{key} ("bad")')
                assert bad_fixture!=checked['fixture']
                assert not adapter.call(op='elaborate_fixture',fixture=bad_fixture)['ok']
                checks+=10
            finally:
                frontend.close()
    finally:
        adapter.close()
    print(json.dumps({'profiles':len(cases),'checks':checks,'passed':checks,'scope':'source metadata transport; semantic line mutation is checked by semantics/source_context.py and source_compiler.py'}))


if __name__=='__main__':main()
