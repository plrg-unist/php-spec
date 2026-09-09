#!/usr/bin/env python3
"""Foreach target designations survive checked transport and fresh printing."""
import base64,copy
from validate import ROOT,Worker,require,normalize,structurally_equal

CASES = {
    'key-ref': b'<?php foreach([] as &$k=>$v){}',
    'key-ref-both': b'<?php foreach([] as &$k=>&$v){}',
    'key-ref-before-iterable': b'<?php foreach([[]=>1] as &$k=>$v){}',
    'key-ref-before-list-spread': b'<?php foreach([] as &$k=>[...$v]){}',
    'key-ref-dim': b'<?php foreach([] as &$k[0]=>$v){}',
    'key-list': b'<?php foreach([] as list($k)=>$v){}',
    'key-list-empty': b'<?php foreach([] as list()=>$v){}',
    'key-list-holes': b'<?php foreach([] as list(,$k,)=>$v){}',
    'key-short-list': b'<?php foreach([] as [$k]=>$v){}',
    'key-short-holes': b'<?php foreach([] as [,$k,]=>$v){}',
    'key-list-ref': b'<?php foreach([] as [&$k]=>$v){}',
    'key-list-unpack': b'<?php foreach([] as [...$k]=>$v){}',
    'key-list-before-iterable': b'<?php foreach([[]=>1] as list($k)=>$v){}',
    'value-ref': b'<?php foreach([] as &$v){}',
    'value-ref-dim': b'<?php foreach([] as &$v[0]){}',
    'value-list-ref': b'<?php foreach([] as [&$v]){}',
    'value-nested-ref': b'<?php foreach([] as [[&$v]]){}',
    'value-list-hole': b'<?php foreach([] as [,$v,]){}',
    'value-genuine-hole': b'<?php foreach([] as list(,$v,)){}',
    'value-list-unpack': b'<?php foreach([] as [...$v]){}',
    'value-nested-unpack-ref': b'<?php foreach([] as [...[&$v]]){}',
    'value-long-nested': b'<?php foreach([] as [array($v)]){}',
    'value-mixed': b'<?php foreach([] as [list($v)]){}',
    'parse-ref-list-value': b'<?php foreach([] as &[$v]){}',
    'parse-ref-list-key': b'<?php foreach([] as &[$k]=>$v){}',
    'parse-long-key': b'<?php foreach([] as array($k)=>$v){}',
    'parse-literal-key': b'<?php foreach([] as 1=>$v){}',
    'key-call': b'<?php foreach([] as foo()=>$v){}',
    'key-nullsafe': b'<?php foreach([] as $k?->p=>$v){}',
    'key-ref-multiline': b'<?php foreach(\n[[]=>1]\nas\n&$k\n=>\n$v\n){}',
    'vendor/php-src/Zend/tests/errmsg/errmsg_042.phpt': b'<?php\n\n$a = array(1,2,3);\nforeach ($a as &$k=>$v) {\n}\n\necho "Done\\n";\n?>\n',
    'vendor/php-src/Zend/tests/foreach/foreach_list_003.phpt': b"<?php\n\n$array = [['a', 'b'], 'c', 'd'];\n\nforeach($array as list($key) => list(list(), $a)) {\n}\n\n?>\n",
    'vendor/php-src/tests/lang/foreachLoop.006.phpt': b'<?php\n$a = array("a","b","c");\nforeach ($a as &$k=>$v) {\n  var_dump($v);\n}\n?>\n',
}


def foreach_nodes(value):
    if isinstance(value,dict):
        if value.get('node')=='Stmt_Foreach':yield value
        for child in value.values():yield from foreach_nodes(child)
    elif isinstance(value,list):
        for child in value:yield from foreach_nodes(child)


def main():
    adapter=Worker([str(ROOT/'_build/default/adapter/main.exe'),str(ROOT)])
    profiles=boundaries=0
    try:
        for encoding in ['plain','UTF-16BE']:
            flags=[] if encoding=='plain' else ['-d','zend.multibyte=1','-d','internal_encoding=UTF-8']
            frontend=Worker([str(ROOT/'.tools/php/bin/php'),'-n',*flags,str(ROOT/'frontend/worker.php')])
            try:
                for name,source in CASES.items():
                    if encoding!='plain':source=b'\xfe\xff'+source.decode().encode('utf-16be')
                    encoded=base64.b64encode(source).decode();parsed=require(frontend.call(op='parse',source=encoded),'parse');oracle=require(frontend.call(op='oracle',source=encoded),'oracle')
                    assert parsed['accepted']==oracle['accepted'],(name,parsed,oracle);profiles+=1
                    if not parsed['accepted']:continue
                    ast=parsed['ast'];nodes=list(foreach_nodes(ast));assert nodes
                    keyref=name.startswith('key-ref') or name.endswith('errmsg_042.phpt') or name.endswith('foreachLoop.006.phpt')
                    assert any(node['fields'][5] for node in nodes)==keyref,name
                    assert all(len(node['fields'])==6 and isinstance(node['fields'][5],bool) for node in nodes)
                    checked=require(adapter.call(op='elaborate',ast=ast,fixture=True),'elaborate');assert checked['ast']==ast
                    printed=require(frontend.call(op='print',ast=checked['ast']),'fresh print');assert printed['ast']==ast
                    again=require(frontend.call(op='parse',source=printed['source']),'reparse');assert again['accepted'];assert structurally_equal(normalize(ast),normalize(again['ast']))
                    assert require(frontend.call(op='oracle',source=printed['source']),'printed oracle')['accepted']
                    assert require(frontend.call(op='print',ast=again['ast']),'print again')['source']==printed['source']
                ast=require(frontend.call(op='parse',source=base64.b64encode(CASES['key-ref']).decode()),'edit source')['ast']
                for mode in ['missing','extra','null','integer','bytes','array','false','true','true-absent']:
                    edited=copy.deepcopy(ast);fields=next(foreach_nodes(edited))['fields']
                    if mode=='missing':del fields[5]
                    elif mode=='extra':fields.append(False)
                    elif mode=='true-absent':fields[1]=None
                    else:fields[5]={'null':None,'integer':{'int':'1'},'bytes':{'bytes':'MQ=='},'array':[],'false':False,'true':True}[mode]
                    checked=adapter.call(op='check',ast=edited);accepted=mode in ['false','true','true-absent'];assert bool(checked.get('ok'))==accepted,(mode,checked)
                    if accepted:
                        printed=frontend.call(op='print',ast=checked['ast']);assert bool(printed.get('ok'))==(mode!='true-absent')
                        if mode!='true-absent':
                            reparsed=require(frontend.call(op='parse',source=printed['source']),'edited reparse');assert structurally_equal(normalize(edited),normalize(reparsed['ast']))
                    boundaries+=1
            finally:frontend.close()
    finally:adapter.close()
    print(profiles,'foreach target parser profiles;',boundaries,'typed and printer boundaries passed')

if __name__=='__main__':main()
