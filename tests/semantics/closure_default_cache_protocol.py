#!/usr/bin/env python3
"""Authenticate deferred Closure/arrow caches across object retirement."""
from pathlib import Path
import closure_call_protocol as protocol

ACTIVE = [
    'S.OBJECTS[n_source] = REALCLOSURE porigin pitem* pstaticcell*',
    'S.CLOSURETEMPLATES = [pfunction]', 'pfunction.ORIGIN = porigin',
    'pfunction.DEFAULTS = [pdefault]',
    'pdefault.ORIGIN = pdefaultcache.ORIGIN', 'pdefault.KIND = PDDEFERRED',
    '$compiled_read(S, pdefault.ORIGIN) = eps',
    'pdefaultcache.VALUE = PINT 1', 'pdefaultcache.CLASS = PVSCALAR',
    '$lookup(S.ENV, $ptascii("x")) = (n_cell)',
    'S.STORE[n_cell] = DEFINED (PINT 1)',
    '$default_caches_valid(S, S.DEFAULTCACHE)',
    '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
    '~$default_caches_valid(S[.CLOSURETEMPLATES = eps], S.DEFAULTCACHE)',
    '~$default_caches_valid(S, S.DEFAULTCACHE ++ S.DEFAULTCACHE)',
    'pfunction_bad = pfunction[.DEFAULTS = [pdefault[.KIND = PDSTORED]]]',
    '~$default_caches_valid(S[.CLOSURETEMPLATES = [pfunction_bad]], S.DEFAULTCACHE)',
    'pfunction_wrong_index = pfunction[.DEFAULTS = [pdefault[.INDEX = 1]]]',
    '~$default_caches_valid(S[.CLOSURETEMPLATES = [pfunction_wrong_index]], S.DEFAULTCACHE)',
    'pfunction_wrong_source = pfunction[.ORIGIN = pdefault.ORIGIN]',
    '~$default_caches_valid(S[.CLOSURETEMPLATES = [pfunction_wrong_source]], S.DEFAULTCACHE)',
    '~$default_caches_valid(S, [pdefaultcache[.CLASS = PVSTRING false]])',
]
STORED = [
    'S.OBJECTS[n_source] = REALCLOSURE porigin pitem* pstaticcell*',
    'S.CLOSURETEMPLATES = [pfunction]', 'pfunction.ORIGIN = porigin',
    'pfunction.DEFAULTS = [pdefault]', 'pdefault.KIND = PDSTORED',
    'S.DEFAULTCACHE = eps', '$compiled_read(S, pdefault.ORIGIN) = (PINT 1)',
    '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
    'pfunction_bad = pfunction[.DEFAULTS = [pdefault[.KIND = PDDEFERRED]]]',
    'S_bad = $default_cache_value(S, pdefault.ORIGIN, PINT 1, PVSCALAR)[.CLOSURETEMPLATES = [pfunction_bad]]',
    '$compiled_read(S_bad, pdefault.ORIGIN) = (PINT 1)',
    '~$default_caches_valid(S_bad, S_bad.DEFAULTCACHE)', '~$call_descriptors_valid(S_bad)',
]
CASES = {}
for name, source in [
    ('closure-default-cache-active', '<?php const C=1; $c=function($x=C){echo $x;}; $c();'),
    ('arrow-default-cache-active', '<?php const C=1; $c=fn($x=C)=>$x; echo $c();'),
]:
    CASES[name] = {
        'source': source,
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_source -- if S.CONSTCONTEXT = eps -- if S.DEFAULTCACHE = pdefaultcache :: pdefaultcache_tail*',
        'checks': ACTIVE,
    }
CASES['closure-default-cache-retired-object'] = {
    'source': '<?php const C=1; $c=function($x=C){echo $x;}; $c(); $c=null; echo "R";',
    'stage': 'S.CURRENT = eps -- if S.DEFAULTCACHE = pdefaultcache :: pdefaultcache_tail* -- if $lookup(S.ENV, $ptascii("c")) = (n_cell_c) -- if S.STORE[n_cell_c] = DEFINED PNULL',
    'checks': [
        'S.OBJECTS = [REALCLOSURE porigin pitem* pstaticcell*]',
        '~$heap_member(HOBJECT 0, S.ALLOCATIONS)',
        'S.CLOSURETEMPLATES = [pfunction]', 'pfunction.ORIGIN = porigin',
        'pfunction.DEFAULTS = [pdefault]', 'pdefault.KIND = PDDEFERRED',
        'pdefault.ORIGIN = pdefaultcache.ORIGIN',
        '$compiled_read(S, pdefault.ORIGIN) = eps',
        'pdefaultcache.VALUE = PINT 1',
        '$default_caches_valid(S, S.DEFAULTCACHE)',
        '$call_descriptors_valid(S)', '$closure_state_valid(S)', '$heap_valid($heap_graph(S))',
        '~$default_caches_valid(S[.CLOSURETEMPLATES = eps], S.DEFAULTCACHE)',
    ],
}
for name, source in [
    ('closure-default-cache-stored-rejection', '<?php $c=function($x=1){echo $x;}; $c();'),
    ('arrow-default-cache-stored-rejection', '<?php $c=fn($x=1)=>$x; echo $c();'),
]:
    CASES[name] = {
        'source': source,
        'stage': 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_source -- if $lookup(S.ENV, $ptascii("x")) = (n_cell) -- if S.STORE[n_cell] = DEFINED (PINT 1)',
        'checks': STORED,
    }

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__),))
