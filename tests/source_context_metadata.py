#!/usr/bin/env python3
"""Retain namespace brace lines through checked byte-safe source transport."""
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
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    checks=0
    try:
        for source,ini,line in cases:
            flags=[item for key,value in ini.items() for item in ['-d',key+'='+value]]
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',*flags,str(ROOT/'frontend/worker.php')])
            try:
                parsed=require(frontend.call(op='parse',source=base64.b64encode(source).decode()),'parse')
                assert parsed['accepted'],parsed
                original=parsed['ast']; node=original['program'][0]
                assert node['meta']['namespaceBraceLine']=={'int':str(line)}
                checked=require(adapter.call(op='elaborate',ast=original,fixture=True),'checked metadata')
                assert checked['ast']==original
                printed=require(frontend.call(op='print',ast=checked['ast']),'fresh printing')
                assert printed['ast']==original
                reparsed=require(frontend.call(op='parse',source=printed['source']),'printed parsing')
                assert reparsed['accepted'] and structurally_equal(normalize(original),normalize(reparsed['ast']))
                # Fresh printer uses checked syntax, not location metadata to replay original text.
                changed=copy.deepcopy(original);changed['program'][0]['meta']['namespaceBraceLine']={'int':'99'}
                changed=require(adapter.call(op='elaborate',ast=changed),'edited metadata')['ast']
                assert changed['program'][0]['meta']['namespaceBraceLine']=={'int':'99'}
                assert require(frontend.call(op='print',ast=changed),'edited printing')['source']==printed['source']
                absent=copy.deepcopy(original);del absent['program'][0]['meta']['namespaceBraceLine']
                assert require(adapter.call(op='elaborate',ast=absent),'absent metadata')['ast']==absent
                malformed=copy.deepcopy(original);malformed['program'][0]['meta']['namespaceBraceLine']={'bytes':'MQ=='}
                assert not adapter.call(op='check',ast=malformed)['ok']
                bad_fixture=checked['fixture'].replace(f'MnamespaceBraceLine ({line})','MnamespaceBraceLine ("bad")')
                assert bad_fixture!=checked['fixture']
                assert not adapter.call(op='elaborate_fixture',fixture=bad_fixture)['ok']
                checks+=10
            finally:
                frontend.close()
    finally:
        adapter.close()
    print(json.dumps({'profiles':len(cases),'checks':checks,'passed':checks,'scope':'source metadata transport; semantic line mutation is checked by semantics/source_context.py'}))


if __name__=='__main__':main()
