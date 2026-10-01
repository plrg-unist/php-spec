#!/usr/bin/env python3
"""Source-derived current bridge; both pauses use explicit finite file mode."""
from pathlib import Path
import json

import include_mutable_protocol as protocol

CATALOGUE = Path(__file__).with_name('method_class_selector_current_bridge_cases.json')
SOURCE = json.loads(CATALOGUE.read_text())[0]['source'].encode()
CONFIG_SOURCE = (b'<?php class O{function __toString():string{echo "T";return ".tools";}}'
                 b'echo chdir(new O)?"C":"E";echo chdir("..")?"R":"E";')
GUARDS = ['$call_descriptors_valid(S)', '$class_state_valid(S)',
          '$class_statics_valid(S)', '$closure_state_valid(S)',
          '$default_caches_valid(S, S.DEFAULTCACHE)', '$heap_valid($heap_graph(S))']
CASES = [
    ('selected-static-retirement-default-cache', SOURCE,
     'S.TODO = (CALL_SEND (STATIC_METHOD_TARGET porigin_class porigin_method) '
     'phpType7* 0 eps (porigin_site) z) :: ptask_tail* '
     '-- if S.RESULT = KNOWN (PINT 0)', [
         'S.TODO = (CALL_SEND (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7* 0 eps (porigin_site) z) :: ptask_tail*',
         'S.RESULT = KNOWN (PINT 0)',
         '$class_at(S.CLASSES, porigin_class) = (pclassdesc)',
         'pclassdesc.NAME = $ptascii("A")',
         'S.OBJECTS[0] = INSTANCE porigin_class',
         '~((HOBJECT 0) <- S.ALLOCATIONS)',
         '$lookup(S.ENV, $ptascii("a")) = (n_cell_a)',
         'S.STORE[n_cell_a] = DEFINED PNULL',
         '$lookup(S.ENV, $ptascii("r")) = (n_cell_r)',
         'S.STORE[n_cell_r] = DEFINED (PSTRING $ptascii("s"))',
         '$propref_at(S.PROPREFS, n_cell_r) = eps',
         'S.CLASSSTATICS = [pclassstatic]',
         'pclassstatic.STATE = PROP_VALUE (DIRECT (PSTRING $ptascii("1")))',
         'S.DEFAULTCACHE = [pdefaultcache]',
         '$default_function_at(S.CLOSURETEMPLATES, pdefaultcache.ORIGIN) = (pfunction)',
         'pfunction.DEFAULTS = [pdefault]',
         'pdefault.KIND = PDDEFERRED', 'pdefault.INDEX = 0',
         '$compiled_read(S, pdefault.ORIGIN) = eps',
         'pdefaultcache.VALUE = PINT 1', 'pdefaultcache.CLASS = PVSCALAR',
         '$call_task_valid(S, CALL_SEND (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7* 0 eps (porigin_site) z)',
         '~((HOBJECT 0) <- $task_nodes(CALL_SEND (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7* 0 eps (porigin_site) z))',
         *GUARDS,
         '~$call_task_valid(S, CALL_SEND (STATIC_METHOD_TARGET porigin_class porigin_method) phpType7* 0 eps (porigin_site) $(z + 100))',
         '~$call_descriptors_valid(S[.CLOSURETEMPLATES = eps])',
     ]),
    ('config-entered-instance-authentication', CONFIG_SOURCE,
     'S.CURRENT = (pcallcontext) -- if S.FRAMES = pframe :: pframe_tail* '
     '-- if pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: '
     '(CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*', [
         'S.CURRENT = (pcallcontext)',
         'S.FRAMES = pframe :: pframe_tail*',
         'pframe.TODO = (STRINGIFY_RESULT n_object porigin_child z_call) :: (CONFIG_STRING_RESULT pconfigcall n_object porigin_child z_child z_call) :: ptask_tail*',
         'pcallcontext.TARGET = METHOD_TARGET n_object porigin_method',
         'pcallcontext.INSTANCE = eps',
         '$target_instance(pcallcontext.TARGET) = eps',
         'pcallcontext.RECEIVER = (n_object)',
         '(HOBJECT n_object) <- S.ALLOCATIONS',
         '$config_string_site_valid(S, pconfigcall, n_object, porigin_child, z_child, z_call)',
         '$config_string_trace_context(S, pcallcontext)',
         '$call_context_valid(S, pcallcontext, S.CVS)', '$call_current_valid(S)',
         *GUARDS,
         'pcallcontext_bad = pcallcontext[.INSTANCE = (n_object)]',
         'S_bad = S[.CURRENT = (pcallcontext_bad)]',
         '~$call_context_valid(S_bad, pcallcontext_bad, S_bad.CVS)',
         '~$call_current_valid(S_bad)', '~$call_descriptors_valid(S_bad)',
         '$heap_valid($heap_graph(S_bad))',
     ]),
]

if __name__ == '__main__':
    protocol.main(CASES, (Path(__file__), CATALOGUE,
                          protocol.ROOT / '.tools/request-clock.so'))
