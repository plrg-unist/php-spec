#!/usr/bin/env python3
"""Independent imported method identity, scope and publication checks."""
from pathlib import Path

import closure_call_protocol as protocol

IMPORTED = ('S.CURRENT = (pcallcontext) '
            '-- if pcallcontext.FUNCTION = TRAIT_ORIGIN porigin_owner porigin_source ptbytes_selected')
VALID = [
    '$call_current_valid(S)',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$closure_state_valid(S)',
    '$heap_valid($heap_graph(S))',
]
FINISH = [
    'S_done = $drive(S, 2000)',
    'S_done.COMPLETION = NORMAL',
    'S_done.TODO = eps',
    'S_done.CURRENT = eps',
    'S_done.FRAMES = eps',
    '$heap_valid($heap_graph(S_done))',
    'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
]

CASES = {
    'alias-origin-and-inherited-called-class': {
        'source': '<?php trait T{function FoO(){echo "F";}}'
                  'class C{use T{FoO as MiXeD;}}class D extends C{}(new D)->mixed();',
        'stage': IMPORTED,
        'checks': [
            *VALID,
            'ptbytes_selected = $ptascii("MiXeD")',
            'pcallcontext.NAME = $ptascii("C::MiXeD")',
            'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
            '$class_at(S.CLASSES, porigin_owner) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("C")',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            '$class_at(S.CLASSES, porigin_called) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("D")',
            '$class_method_origin(S.CLASSES, pcallcontext.FUNCTION) = (pmethoddesc)',
            'pmethoddesc.OWNER = porigin_owner',
            'pmethoddesc.NAME = ptbytes_selected',
            '$origin_source(porigin_source) = PORIGIN n_unit pcpath_source',
            '$origin_node(S.SOURCES, PORIGIN n_unit pcpath_source) = '
            '(NStmtClassMethod phpType14 phpType24 phpType4 '
            '(NIdentifier (BYTES text_name) metadata_name) phpType16 phpType18 phpType47 metadata)',
            '$base64(text_name) = $ptascii("FoO")',
            '$call_sourcefile(S.FILES, pcallcontext.FUNCTION) = '
            '$call_sourcefile(S.FILES, PORIGIN n_unit pcpath_source)',
            '~$finally_current_complete(S[.ORIGIN = '
            '(TRAIT_ORIGIN porigin_called porigin_source ptbytes_selected)])',
            '~$finally_current_complete(S[.ORIGIN = '
            '(TRAIT_ORIGIN porigin_owner porigin_source $ptascii("FoO"))])',
            '~$call_current_valid(S[.CURRENT = '
            '(pcallcontext[.LEXICAL_CLASS = (porigin_called)])])',
            '~$call_current_valid(S[.CURRENT = '
            '(pcallcontext[.FUNCTION = TRAIT_ORIGIN porigin_called porigin_source ptbytes_selected])])',
            *FINISH,
        ],
    },
    'same-source-distinct-imports-cannot-exchange-identity': {
        'source': '<?php trait T{function f(){echo "F";}}'
                  'class C{use T;}class E{use T;}(new C)->f();',
        'stage': IMPORTED,
        'checks': [
            *VALID,
            'S.CLASSES = [pclassdesc_t, pclassdesc_c, pclassdesc_e]',
            'pclassdesc_c.ORIGIN = porigin_owner',
            '$method_named(pclassdesc_c.METHODS, $ptascii("f")) = (pmethoddesc_c)',
            '$method_named(pclassdesc_e.METHODS, $ptascii("f")) = (pmethoddesc_e)',
            'pmethoddesc_c.FUNCTION.ORIGIN =/= pmethoddesc_e.FUNCTION.ORIGIN',
            '$origin_source(pmethoddesc_c.FUNCTION.ORIGIN) = '
            '$origin_source(pmethoddesc_e.FUNCTION.ORIGIN)',
            '~$call_current_valid(S[.CURRENT = '
            '(pcallcontext[.FUNCTION = pmethoddesc_e.FUNCTION.ORIGIN])])',
            '~$declaration_history_valid(S[.CLASSES = '
            '[pclassdesc_t, pclassdesc_c[.METHODS = [pmethoddesc_e]], pclassdesc_e]])',
            '~$declaration_history_valid(S[.CLASSES = '
            '[pclassdesc_t, pclassdesc_c[.METHODS = eps], pclassdesc_e]])',
            'S_bad = $drive(S[.CLASSES = '
            '[pclassdesc_t, pclassdesc_c[.METHODS = [pmethoddesc_e]], pclassdesc_e]], 20)',
            'S_bad.COMPLETION = UNSUPPORTED text',
            *FINISH,
        ],
    },
    'deferred-default-retains-physical-parameter-site': {
        'source': '<?php trait T{function f($x=__CLASS__){echo $x;}}'
                  'class C{use T{f as g;}}class E{use T;}(new C)->g();',
        'stage': (IMPORTED + ' -- if S.TODO = '
                  '(DEFAULT_RECEIVE pcallcontext.FUNCTION 0) :: ptask_tail*'),
        'checks': [
            *VALID,
            'ptbytes_selected = $ptascii("g")',
            '$call_task_valid(S, DEFAULT_RECEIVE pcallcontext.FUNCTION 0)',
            '$origin_source(porigin_source) = PORIGIN n_unit pcpath_source',
            '$default_parameter_origin(S, pcallcontext.FUNCTION, 0) = '
            'PORIGIN n_unit (pcpath_source ++ [PCFIELD 4, PCINDEX 0])',
            '$function_at($all_functions(S), pcallcontext.FUNCTION) = (pfunction)',
            '$default_at(pfunction.DEFAULTS, 0) = (pdefault)',
            'pdefault.ORIGIN = PORIGIN n_unit '
            '(pcpath_source ++ [PCFIELD 4, PCINDEX 0, PCFIELD 6])',
            '$default_scope_dependent(S, pdefault.ORIGIN)',
            '~$call_task_valid(S, DEFAULT_RECEIVE porigin_source 0)',
            '~$call_task_valid(S, DEFAULT_RECEIVE pcallcontext.FUNCTION 1)',
            *FINISH,
        ],
    },
    'retired-maker-keeps-authentic-private-alias': {
        'source': '<?php trait T{function f(){echo get_called_class();}'
                  'function make(){return $this->secret(...);}}'
                  'class C{use T{f as private secret;}}class D extends C{}'
                  '$f=(new D)->make();$f();',
        'stage': IMPORTED + ' -- if ptbytes_selected = $ptascii("secret")',
        'checks': [
            *VALID,
            'pcallcontext.LEXICAL_CLASS = (porigin_owner)',
            '$class_at(S.CLASSES, porigin_owner) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("C")',
            'pcallcontext.CALLED_CLASS = (porigin_called)',
            '$class_at(S.CLASSES, porigin_called) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("D")',
            '$class_method_origin(S.CLASSES, pcallcontext.FUNCTION) = (pmethoddesc)',
            'pmethoddesc.VISIBILITY = PROPERTY_PRIVATE',
            'pcallcontext.TARGET = CLOSURE_TARGET n_closure',
            '$object_body(S.OBJECTS[n_closure]) = '
            'METHODCLOSURE porigin_method porigin_site porigin_requested (pmethodcapture)',
            'pmethodcapture.LEXICAL_CLASS = (porigin_owner)',
            'pmethodcapture.CALLED_CLASS = (porigin_called)',
            '$method_capture_certificate_valid(S, porigin_site, (pmethodcapture))',
            '~$method_capture_certificate_valid(S, porigin_site, '
            '(pmethodcapture[.FUNCTION = pcallcontext.FUNCTION]))',
            '~$method_capture_certificate_valid(S, porigin_site, '
            '(pmethodcapture[.CALLSITE = (PORIGIN 999 eps)]))',
            'S.FRAMES = [pframe]',
            'pframe.CONTEXT = eps',
            '~$call_current_valid(S[.CURRENT = '
            '(pcallcontext[.LEXICAL_CLASS = (porigin_called)])])',
            *FINISH,
        ],
    },
    'retired-real-closure-valid-after-another-class-imports-body': {
        'source': '<?php trait T{function make(){return function(){echo get_called_class();};}}'
                  'class C{use T;}class D extends C{}class E{use T;}'
                  '$f=(new D)->make();$f();',
        'stage': ('S.CURRENT = (pcallcontext) '
                  '-- if pcallcontext.TARGET = CLOSURE_TARGET n_closure'),
        'checks': [
            *VALID,
            '$closure_scope_at(S.CLOSURESCOPES, n_closure) = (pclosurescope)',
            '$closure_scope_row_valid(S, pclosurescope)',
            '$class_at(S.CLASSES, pclosurescope.LEXICAL) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("C")',
            '$class_at(S.CLASSES, pclosurescope.CALLED) = (pclassdesc_called)',
            'pclassdesc_called.NAME = $ptascii("D")',
            'pcallcontext.LEXICAL_CLASS = (pclosurescope.LEXICAL)',
            'pcallcontext.CALLED_CLASS = (pclosurescope.CALLED)',
            'S.FRAMES = [pframe]',
            'pframe.CONTEXT = eps',
            '~$closure_scope_row_valid(S, pclosurescope[.LEXICAL = PORIGIN 999 eps])',
            '~$call_current_valid(S[.CURRENT = '
            '(pcallcontext[.CALLED_CLASS = eps])])',
            *FINISH,
        ],
    },
    'inherited-alias-reuses-importing-class-static-cell': {
        'source': '<?php trait T{static function f(){static $n=0;echo ++$n;}}'
                  'class C{use T{f as g;}}class D extends C{}C::g();D::g();',
        'stage': (IMPORTED + ' -- if S.TODO = (STATIC_INIT porigin_static) :: ptask_tail* '
                  '-- if pcallcontext.CALLED_CLASS = (porigin_called) '
                  '-- if $class_at(S.CLASSES, porigin_called) = (pclassdesc_called) '
                  '-- if pclassdesc_called.NAME = $ptascii("D")'),
        'checks': [
            *VALID,
            'ptbytes_selected = $ptascii("g")',
            '$class_at(S.CLASSES, porigin_owner) = (pclassdesc_owner)',
            'pclassdesc_owner.NAME = $ptascii("C")',
            'porigin_owner =/= porigin_called',
            '$call_task_valid(S, STATIC_INIT porigin_static)',
            'porigin_key = $trait_static_key(S, porigin_static)',
            'porigin_key = TRAIT_ORIGIN porigin_owner porigin_static ptbytes_selected',
            '$static_function_at($all_functions(S), porigin_key) = (pfunction)',
            'pfunction.ORIGIN = pcallcontext.FUNCTION',
            '$static_at(S.STATICS, porigin_key) = (n_cell)',
            '$state_static_at(S, porigin_static) = (n_cell)',
            'S.STORE[n_cell] = DEFINED (PINT 1)',
            '$static_origin_valid(S, porigin_key)',
            '~$static_origin_valid(S, '
            'TRAIT_ORIGIN porigin_called porigin_static ptbytes_selected)',
            '~$call_task_valid(S, STATIC_INIT porigin_key)',
            *FINISH,
        ],
    },
    'parent-link-failure-restores-unpublished-imports': {
        'source': '<?php echo "PRE";final class P{}trait T{function f(){}}'
                  'class C extends P{use T;}',
        'stage': ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
                  'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
                  '-- if S.ORIGIN = (porigin_class) '
                  '-- if $class_at(S.CLASSES, porigin_class) = (pclassdesc) '
                  '-- if pclassdesc.NAME = $ptascii("C")'),
        'checks': [
            *VALID,
            'pclassdesc.METHODS = eps',
            '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
            'S_failed = $activate_class_body(S, pclassdesc)',
            'S_failed.COMPLETION = FATAL ptbytes_message pclassdesc.LINE',
            'ptbytes_message = $ptascii("Class C cannot extend final class P")',
            'S_failed.CLASSES = S.CLASSES',
            'S_failed.CLASSNAMES = S.CLASSNAMES',
            'S_failed.LINKEDPARENTS = S.LINKEDPARENTS',
            'S_failed.LINKEDINTERFACES = S.LINKEDINTERFACES',
            'S_failed.CLASSSTATICS = S.CLASSSTATICS',
            'S_failed.DECLARATIONS = S.DECLARATIONS',
            '$declaration_history_valid(S_failed)',
            '$class_at(S_failed.CLASSES, porigin_class) = (pclassdesc)',
            '$class_named(S_failed.CLASSNAMES, $ptascii("c")) = eps',
        ],
    },
    'goto-uses-active-import-with-authentic-source-occurrence': {
        'source': '<?php trait T{function f(){goto L;echo "N";L:echo "F";}}'
                  'class C{use T;}class E{use T;}(new C)->f();',
        'stage': (IMPORTED + ' -- if S.TODO = '
                  '(STMT (NStmtGoto phpType11 metadata)) :: ptask_tail* '
                  '-- if S.ORIGIN = (porigin_goto)'),
        'checks': [
            *VALID,
            '$goto_task_valid(S, NStmtGoto phpType11 metadata, (porigin_goto))',
            '$goto_scope_valid(S, porigin_goto)',
            '$origin_node(S.SOURCES, porigin_goto) = (NStmtGoto phpType11 metadata)',
            '~$goto_scope_valid(S, PORIGIN 999 eps)',
            '~$goto_task_valid(S, NStmtGoto phpType11 metadata, (PORIGIN 999 eps))',
            '~$call_descriptors_valid(S[.CURRENT = '
            '(pcallcontext[.FUNCTION = porigin_source])])',
            *FINISH,
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__),))
