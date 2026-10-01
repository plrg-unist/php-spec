#!/usr/bin/env python3
"""Deferred defaults coexist with temporary scope and typed static storage."""
from pathlib import Path
import copy
import json

import closure_call_protocol as protocol
import closure_default_cache_protocol as defaults

CATALOGUE = Path(__file__).with_name('closure_default_cache_current_bridge_cases.json')
SOURCE = json.loads(CATALOGUE.read_text())[0]['source']
GUARDS = ['$default_caches_valid(S, S.DEFAULTCACHE)', '$call_descriptors_valid(S)',
          '$closure_state_valid(S)', '$class_statics_valid(S)', '$heap_valid($heap_graph(S))']
CASES = {
    'default-cache-temporary-scope-static-write': {
        'source': SOURCE,
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = CLOSURE_CALL_TARGET n_source n_receiver '
                  '-- if S.DEFAULTCACHE = [pdefaultcache] '
                  '-- if S.CLASSSTATICS = [pclassstatic] '
                  '-- if pclassstatic.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("1")))'),
        'checks': [
            'S.OBJECTS[n_source] = REALCLOSURE porigin pitem* pstaticcell*',
            'S.OBJECTS[n_receiver] = INSTANCE porigin_class',
            'pcallcontext.LEXICAL_CLASS = (porigin_class)',
            'pcallcontext.CALLED_CLASS = (porigin_class)',
            '$default_function_at(S.CLOSURETEMPLATES, pdefaultcache.ORIGIN) = (pfunction)',
            'pfunction.ORIGIN = porigin', 'pfunction.DEFAULTS = [pdefault]',
            'pdefault.KIND = PDDEFERRED', 'pdefault.INDEX = 0',
            '$compiled_read(S, pdefault.ORIGIN) = eps',
            'pdefaultcache.VALUE = PINT 1', 'pdefaultcache.CLASS = PVSCALAR',
            '$lookup(S.ENV, $ptascii("x")) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PINT 1)',
            *GUARDS,
            '~$default_caches_valid(S[.CLOSURETEMPLATES = eps], S.DEFAULTCACHE)',
            '~$call_descriptors_valid(S[.CLOSURETEMPLATES = eps])',
        ],
    },
    'default-cache-both-objects-retired': {
        'source': SOURCE,
        'stage': ('S.CURRENT = eps -- if S.DEFAULTCACHE = [pdefaultcache_closure, pdefaultcache_arrow] '
                  '-- if $lookup(S.ENV, $ptascii("c")) = (n_cell_c) '
                  '-- if S.STORE[n_cell_c] = DEFINED PNULL '
                  '-- if $lookup(S.ENV, $ptascii("d")) = (n_cell_d) '
                  '-- if S.STORE[n_cell_d] = DEFINED PNULL'),
        'checks': [
            '$default_function_at(S.CLOSURETEMPLATES, pdefaultcache_closure.ORIGIN) = (pfunction_closure)',
            '$default_function_at(S.CLOSURETEMPLATES, pdefaultcache_arrow.ORIGIN) = (pfunction_arrow)',
            'S.OBJECTS[0] = REALCLOSURE pfunction_closure.ORIGIN pitem_closure* pstaticcell_closure*',
            'S.OBJECTS[3] = REALCLOSURE pfunction_arrow.ORIGIN pitem_arrow* pstaticcell_arrow*',
            '~$heap_member(HOBJECT 0, S.ALLOCATIONS)',
            '~$heap_member(HOBJECT 3, S.ALLOCATIONS)',
            'pfunction_closure.DEFAULTS = [pdefault_closure]',
            'pfunction_arrow.DEFAULTS = [pdefault_arrow]',
            'pdefault_closure.KIND = PDDEFERRED', 'pdefault_arrow.KIND = PDDEFERRED',
            '$compiled_read(S, pdefault_closure.ORIGIN) = eps',
            '$compiled_read(S, pdefault_arrow.ORIGIN) = eps',
            'pdefaultcache_closure.VALUE = PINT 1', 'pdefaultcache_arrow.VALUE = PINT 2',
            'S.CLASSSTATICS = [pclassstatic]',
            'pclassstatic.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("2")))',
            *GUARDS,
            '~$default_caches_valid(S[.CLOSURETEMPLATES = eps], S.DEFAULTCACHE)',
            '~$call_descriptors_valid(S[.CLOSURETEMPLATES = eps])',
            '~$default_caches_valid(S, S.DEFAULTCACHE ++ S.DEFAULTCACHE)',
        ],
    },
    'default-cache-stored-arrow-rejection': copy.deepcopy(
        defaults.CASES['arrow-default-cache-stored-rejection']),
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__), CATALOGUE, Path(defaults.__file__)))
