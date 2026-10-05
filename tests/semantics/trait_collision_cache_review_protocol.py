#!/usr/bin/env python3
"""Reached composition caches retain full import causes and real array owners."""
from pathlib import Path
import json

import closure_call_protocol as protocol

HERE = Path(__file__).resolve().parent
ARRAYS = HERE / 'trait_data_collision_cache_array_review_cases.json'
IMPORTS = HERE / 'trait_data_collision_lookup_order_review_cases.json'
ARRAY_SOURCE = next(row['source'] for row in json.loads(ARRAYS.read_text())['cases']
                    if row['id'] == 'imported-array-dependency-has-one-cache-owner-before-static-fill-and-cow')
IMPORT_SOURCE = next(row['source'] for row in json.loads(IMPORTS.read_text())['cases']
                     if row['id'] == 'earlier-imported-dependency-caches-distinct-using-class-values')

COMMON = [
    'S.CURRENT = eps',
    'S.FRAMES = eps',
    '$call_descriptors_valid(S)',
    '$declaration_history_valid(S)',
    '$class_constant_state_valid(S)',
    '$class_statics_valid(S)',
    '$heap_valid($heap_graph(S))',
    '$call_task_valid(S, DECL_NOTICES pdeclnoticebatch)',
    '$task_nodes(DECL_NOTICES pdeclnoticebatch) = eps',
]

CASES = {
    'imported-array-cache-before-static-fill-and-cow': {
        'source': ARRAY_SOURCE,
        'stage': ('S.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail* '
                  '-- if pdeclnoticebatch.INDEX = 0 '
                  '-- if $trait_notice_items(pdeclnoticebatch.NOTICES)'),
        'checks': COMMON + [
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) = (porigin_c)',
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("T"))) = (porigin_t)',
            '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
            '$class_constant_desc(pclassdesc_c.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            'pclassconstantdesc_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_y_source',
            'pclassconstantdesc_y.OWNER = porigin_c',
            '~pclassconstantdesc_y.FOLDED',
            '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            'S.CLASSCONSTANTCACHE = [pdefaultcache_y]',
            'pdefaultcache_y.VALUE = PARRAY n_y',
            'pdefaultcache_y.CLASS = PVARRAY b_array ([(KINT 2048, PVSTRING b_string)])',
            'S.ARRAYS[n_y].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("X")))]',
            '$trait_cache_event_at(S.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = (ptraitcachecause_y)',
            'ptraitcachecause_y.CLASS = porigin_c',
            'ptraitcachecause_y.LOOKUPS = [porigin_fetch]',
            'ptraitcachecause_y.ROOT = porigin_fetch',
            'ptraitcachecause_y.TABLE = pclassdesc_c.CONSTANTS',
            '$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            '$ppproperty_desc_at(pclassdesc_c.PROPERTIES, $ptascii("x")) = (ppropertydesc_x)',
            'ppropertydesc_x.DEFAULT = PROP_DEFERRED porigin_fetch',
            '$class_static_at(S.CLASSSTATICS, ppropertydesc_x.ORIGIN) = (pclassstatic_x)',
            'pclassstatic_x.STATE = PROP_DEFERRED porigin_fetch',
            '$heap_count(HARRAY n_y, $class_constant_roots(S.CLASSCONSTANTCACHE)) = 1',
            '$heap_count(HARRAY n_y, $pools_nodes(S.POOLS)) = 0',
            '$heap_count(HARRAY n_y, $class_static_roots(S.CLASSSTATICS)) = 0',
            '$heap_owners($heap_graph(S), HARRAY n_y) = 1',
            'S.CLASSCONSTANTHISTORY = [(CCLINK porigin_t n_t), (CCTRAITCACHE pclassconstantdesc_y.ORIGIN ptraitcachecause_y), (CCLINK porigin_c n_c)]',
            'pdeclnoticebatch.NOTICES = [(TRAIT_DATA_NOTICE porigin_c ptraitcachecause_y.PREFIX ptraitcachecause_y.USERPREFIX pfdiagnostic)]',
            'pfdiagnostic.OWNER = porigin_c',
            'pfdiagnostic.LEVEL = 8192',
            'pfdiagnostic.LINE = 3',
            '$trait_cache_notice_prefix(S, S.CLASSCONSTANTHISTORY, porigin_c, ptraitcachecause_y.PREFIX) = eps',
            '~$trait_cache_cause_valid(S, porigin_y_source, ptraitcachecause_y)',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.CLASS = porigin_t])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.ROOT = porigin_c])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.ROOT = pclassconstantdesc_y.INITIALIZER])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.TABLE = eps])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.LOOKUPS = eps])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.LOOKUPS = [pclassconstantdesc_y.INITIALIZER]])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.LOOKUPS = [porigin_fetch, porigin_fetch]])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.PREFIX = $nabs($(ptraitcachecause_y.PREFIX + 1))])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_y.ORIGIN, ptraitcachecause_y[.USERPREFIX = $nabs($(|S.USERCONSTANTS| + 1))])',
            '~$trait_cache_cause_valid(S[.SOURCES = eps], pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            '~$trait_cache_cause_valid(S[.CODE = eps], pclassconstantdesc_y.ORIGIN, ptraitcachecause_y)',
            '~$class_constant_state_valid(S[.CLASSCONSTANTCACHE = eps])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTCACHE = [pdefaultcache_y, pdefaultcache_y]])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTCACHE = [pdefaultcache_y[.ORIGIN = porigin_y_source]]])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTCACHE = [pdefaultcache_y[.VALUE = PINT 0]]])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTCACHE = [pdefaultcache_y[.CLASS = PVSCALAR]]])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTHISTORY = [(CCLINK porigin_t n_t), (CCLINK porigin_c n_c)]])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTHISTORY = [(CCLINK porigin_t n_t), (CCTRAITCACHE pclassconstantdesc_y.ORIGIN (ptraitcachecause_y[.TABLE = eps])), (CCLINK porigin_c n_c)]])',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_c ptraitcachecause_y.PREFIX ptraitcachecause_y.USERPREFIX (pfdiagnostic[.OWNER = porigin_t]))]]))',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$call_descriptors_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$class_statics_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = (pdefaultcache_y)',
            '$class_static_at(S_done.CLASSSTATICS, ppropertydesc_x.ORIGIN) = (pclassstatic_x_done)',
            'pclassstatic_x_done.STATE = PROP_VALUE (DIRECT (PARRAY n_x))',
            'n_x =/= n_y',
            'S_done.ARRAYS[n_y].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("X")))]',
            'S_done.ARRAYS[n_x].ITEMS = [ENTRY (KINT 2048) (DIRECT (PSTRING $ptascii("W")))]',
            '$heap_owners($heap_graph(S_done), HARRAY n_y) = 1',
            '$heap_owners($heap_graph(S_done), HARRAY n_x) = 1',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
        ],
    },
    'same-trait-source-keeps-distinct-imported-cache-causes': {
        'source': IMPORT_SOURCE,
        'stage': ('S.TODO = (DECL_NOTICES pdeclnoticebatch) :: ptask_tail* '
                  '-- if pdeclnoticebatch.INDEX = 0 '
                  '-- if pdeclnoticebatch.CLASSES = [(porigin_e, n_e)] '
                  '-- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) '
                  '-- if pclassdesc_e.NAME = $ptascii("E")'),
        'checks': COMMON + [
            '$class_named(S.CLASSNAMES, $ptlc($ptascii("C"))) = (porigin_c)',
            '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
            '$class_constant_desc(pclassdesc_c.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_c_y)',
            '$class_constant_desc(pclassdesc_e.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_e_y)',
            'pclassconstantdesc_c_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_y_source',
            'pclassconstantdesc_e_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_e porigin_y_source',
            'pclassconstantdesc_c_y.OWNER = porigin_c',
            'pclassconstantdesc_e_y.OWNER = porigin_e',
            'pclassconstantdesc_c_y.INITIALIZER = pclassconstantdesc_e_y.INITIALIZER',
            '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_c_y.ORIGIN) = (pdefaultcache_c_y)',
            '$default_cache_at(S.CLASSCONSTANTCACHE, pclassconstantdesc_e_y.ORIGIN) = (pdefaultcache_e_y)',
            'S.CLASSCONSTANTCACHE = [pdefaultcache_c_y, pdefaultcache_e_y]',
            'pdefaultcache_c_y.VALUE = PSTRING $ptascii("2048C")',
            'pdefaultcache_e_y.VALUE = PSTRING $ptascii("2048E")',
            '$trait_cache_event_at(S.CLASSCONSTANTHISTORY, pclassconstantdesc_c_y.ORIGIN) = (ptraitcachecause_c)',
            '$trait_cache_event_at(S.CLASSCONSTANTHISTORY, pclassconstantdesc_e_y.ORIGIN) = (ptraitcachecause_e)',
            'ptraitcachecause_c.CLASS = porigin_c',
            'ptraitcachecause_e.CLASS = porigin_e',
            'ptraitcachecause_c.ROOT = ptraitcachecause_e.ROOT',
            'ptraitcachecause_c.LOOKUPS = ptraitcachecause_e.LOOKUPS',
            'ptraitcachecause_c.TABLE =/= ptraitcachecause_e.TABLE',
            '$(ptraitcachecause_c.PREFIX < ptraitcachecause_e.PREFIX)',
            'ptraitcachecause_e.PREFIX = n_e',
            '$trait_cache_cause_valid(S, pclassconstantdesc_c_y.ORIGIN, ptraitcachecause_c)',
            '$trait_cache_cause_valid(S, pclassconstantdesc_e_y.ORIGIN, ptraitcachecause_e)',
            '$trait_cache_notice_prefix(S, S.CLASSCONSTANTHISTORY, porigin_e, ptraitcachecause_e.PREFIX) = [pdefaultcache_c_y]',
            'pdeclnoticebatch.NOTICES = [(TRAIT_DATA_NOTICE porigin_e n_e ptraitcachecause_e.USERPREFIX pfdiagnostic)]',
            'pfdiagnostic.OWNER = porigin_e',
            'pfdiagnostic.LINE = 3',
            '~$trait_cache_cause_valid(S, porigin_y_source, ptraitcachecause_e)',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_e_y.ORIGIN, ptraitcachecause_c)',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_c_y.ORIGIN, ptraitcachecause_e)',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_e_y.ORIGIN, ptraitcachecause_e[.TABLE = ptraitcachecause_c.TABLE])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_e_y.ORIGIN, ptraitcachecause_e[.CLASS = porigin_c])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_e_y.ORIGIN, ptraitcachecause_e[.ROOT = pclassconstantdesc_e_y.INITIALIZER])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_e_y.ORIGIN, ptraitcachecause_e[.LOOKUPS = eps])',
            '~$trait_cache_cause_valid(S, pclassconstantdesc_e_y.ORIGIN, ptraitcachecause_e[.PREFIX = ptraitcachecause_c.PREFIX])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTCACHE = [pdefaultcache_e_y, pdefaultcache_c_y]])',
            '~$class_constant_state_valid(S[.CLASSCONSTANTCACHE = [pdefaultcache_c_y, pdefaultcache_e_y[.ORIGIN = pclassconstantdesc_c_y.ORIGIN]]])',
            '~$call_task_valid(S, DECL_NOTICES (pdeclnoticebatch[.NOTICES = [(TRAIT_DATA_NOTICE porigin_e n_e ptraitcachecause_e.USERPREFIX (pfdiagnostic[.OWNER = porigin_c]))]]))',
            'S_done = $drive(S, 2000)',
            'S_done.COMPLETION = NORMAL',
            'S_done.TODO = eps',
            'S_done.CURRENT = eps',
            'S_done.FRAMES = eps',
            '$call_descriptors_valid(S_done)',
            '$class_constant_state_valid(S_done)',
            '$heap_valid($heap_graph(S_done))',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_c_y.ORIGIN) = (pdefaultcache_c_y)',
            '$default_cache_at(S_done.CLASSCONSTANTCACHE, pclassconstantdesc_e_y.ORIGIN) = (pdefaultcache_e_y)',
            'S_done = $drive(S_initial[.COMPLETION = NORMAL], 2000)',
        ],
    },
}

# Keep the same reached E state and every original check under the runner's
# 300-second cap. These partitions repeat 17 binding checks and three stage
# checks; that setup is not additional semantic coverage.
IMPORT_CASE = CASES.pop('same-trait-source-keeps-distinct-imported-cache-causes')
IMPORT_CHECKS = IMPORT_CASE['checks']
CASES['same-trait-source-imported-cache-source-causes'] = {
    **IMPORT_CASE,
    'checks': IMPORT_CHECKS[:34] + IMPORT_CHECKS[38:46],
}
CASES['same-trait-source-imported-cache-history-and-finish'] = {
    **IMPORT_CASE,
    'checks': IMPORT_CHECKS[9:25] + [IMPORT_CHECKS[31]]
              + IMPORT_CHECKS[34:38] + IMPORT_CHECKS[46:],
}


if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), ARRAYS, IMPORTS))
