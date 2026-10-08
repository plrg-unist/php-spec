"""Independent genuine FCC scope and failed-import retirement checks."""
from pathlib import Path
import argparse
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'tests/semantics'))
import closure_call_protocol as protocol

HELPERS = [ROOT / 'tests/semantics/trait_public_object_initializer_review.watsup',
           ROOT / 'tests/semantics/trait_unpublished_real.watsup',
           ROOT / 'tests/semantics/trait_failed_real.watsup', HERE / 'trait_unpublished_fcc_receipts.watsup']
protocol.MODULES = [*protocol.MODULES, *HELPERS]
CATALOGUE = HERE / 'trait_data_unpublished_fcc_receipt_cases.json'
SOURCES = {row['id']: row['source'] for row in json.loads(CATALOGUE.read_text())['cases']}
STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
         'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_c) '
         '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C")')

EQUAL = [
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$review19_fcc_table(S, pclassdesc_c) = ((S_constants, pclassdesc_constants))',
    '$class_constant_desc(pclassdesc_constants.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_c',
    '$trait_fcc_source(S_constants, pclassconstantdesc_y)',
    '$ppproperty_desc_at(pclassdesc_constants.PROPERTIES, $ptascii("x")) = (ppropertydesc_x)',
    'ppropertydesc_x.DEFAULT = PROP_DEFERRED porigin_root',
    'porigin_root = PORIGIN n_source pcpath_root',
    '$origin_node(S.SOURCES, porigin_root) = (expression_root)',
    '$review_trait_object_seed(S_constants, pclassdesc_constants, porigin_root) = (F_seed)',
    '$review_trait_real_start(F_seed, pcpath_root, pclassconstantdesc_y, $expression_line(expression_root)) = ((S_start, ptraitcachecause))',
    'n_fcc = |S_start.OBJECTS|',
    'S_birth = $review_trait_real_birth(S_start, ptraitcachecause, n_fcc, 300)',
    'S_birth.COMPLETION = NORMAL',
    '$trait_fcc_active_known(S_birth, ptraitcachecause, pclassconstantdesc_y)',
    '$class_named(S_birth.CLASSNAMES, $ptascii("c")) = eps',
    '$constant_callable_record(S_birth.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
    '$trait_real_birth_at(S_birth.CLASSCONSTANTHISTORY, n_fcc) = ((pconstantclosure.SITE, ptraitcachecause))',
    'S_birth.OBJECTS[n_fcc] = CONSTANTCLOSURE pconstantclosure.SITE (METHODCLOSURE porigin_method pconstantclosure.SITE porigin_c eps)',
    '$class_method_origin(S_birth.CLASSES, porigin_method) = (pmethoddesc)',
    'pmethoddesc.OWNER = porigin_c',
    'pmethoddesc.FUNCTION.ORIGIN = PORIGIN n_method pcpath_method',
    '$closure_scope_at(S_birth.CLOSURESCOPES, n_fcc) = (pclosurescope)',
    r'pclosurescope.LEXICAL = porigin_c /\ pclosurescope.CALLED = porigin_c',
    r'pclosurescope.RECEIVER = eps /\ pclosurescope.CREATION = eps',
    '$trait_fcc_birth_owner(S_birth, pconstantclosure) = (porigin_c)',
    '$method_closure_scope_valid(S_birth, pclosurescope)',
    '$closure_scope_row_valid(S_birth, pclosurescope)',
    '$constant_callable_record_valid(S_birth, pconstantclosure)',
    '$origin_node(S_birth.SOURCES, pconstantclosure.SITE) = (pcnode)',
    r'$trait_fcc_form(pcnode) /\ ~$trait_real_form(pcnode)',
    '~$closure_scope_row_valid(S_birth[.TODO = eps], pclosurescope)',
    '~$method_closure_scope_ordinary(S_birth, pclosurescope)',
    '~$closure_scope_row_valid(S_birth, pclosurescope[.RECEIVER = (n_fcc)])',
]

FAILED = [
    'S_seed = S[.TODO = ptask_tail*]',
    'S_link = $review_trait_real_failed_link(S_seed, pclassdesc_c)',
    'n_fcc = |S_seed.OBJECTS|',
    '$trait_real_birth_at(S_link.CLASSCONSTANTHISTORY, n_fcc) = ((porigin_site, ptraitcachecause))',
    '$constant_callable_record(S_link.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
    '$trait_cache_cause_selected(S_link, ptraitcachecause) = (pclassconstantdesc_y)',
    'S_link.OBJECTS[n_fcc] = CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin_method porigin_site porigin_c eps)',
    '$class_method_origin(S_link.CLASSES, porigin_method) = (pmethoddesc_c)',
    'pmethoddesc_c.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_c porigin_source ptbytes_method',
    'HOBJECT n_fcc <- S_link.ALLOCATIONS',
    '$closure_scope_at(S_link.CLOSURESCOPES, n_fcc) = (pclosurescope)',
    '$trait_real_receipt_source(S_link, pconstantclosure, ptraitcachecause) = (pclassconstantdesc_y)',
    '$trait_failed_cache_ready(S_seed, S_link)',
    'PhpStep: S ~> S_after',
    'S_after.COMPLETION = STATICBYTES ptbytes_message z_fatal',
    'S_after.CLASSES = S_seed.CLASSES',
    'S_after.DECLARATIONS = S_seed.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_c $declaration_cause(S_seed)]',
    '$class_named(S_after.CLASSNAMES, $ptascii("c")) = eps',
    '$class_method_origin(S_after.CLASSES, porigin_method) = eps',
    '$class_constant_origin(S_after.CLASSES, pclassconstantdesc_y.ORIGIN) = eps',
    '$default_cache_at(S_after.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
    '$trait_cache_event_at(S_after.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = eps',
    '~(HOBJECT n_fcc <- S_after.ALLOCATIONS)',
    '$closure_scope_at(S_after.CLOSURESCOPES, n_fcc) = eps',
    '$trait_fcc_retired_receipt(S_after, pconstantclosure) = (pclassconstantdesc_y)',
    '$trait_real_retired_receipt(S_after, pconstantclosure) = eps',
    '$trait_real_birth_owner(S_after, pconstantclosure) = (porigin_c)',
    '$constant_callable_record_valid(S_after, pconstantclosure)',
    '~$constant_callable_value_valid(S_after, n_fcc, porigin_site)',
    '$trait_fcc_birth_owner(S_after, pconstantclosure) = eps',
    '$trait_fcc_cached_header(S_after, porigin_site) = eps',
    '$class_constant_state_valid(S_after)',
    '$call_descriptors_valid(S_after)',
    '$declaration_history_valid(S_after)',
    '$heap_valid($heap_graph(S_after))',
    'S_live = S_after[.ALLOCATIONS = S_after.ALLOCATIONS ++ [HOBJECT n_fcc]]',
    '$trait_fcc_retired_receipt(S_live, pconstantclosure) = eps',
    '~$constant_callable_record_valid(S_live, pconstantclosure)',
    '$trait_fcc_retired_receipt(S_after[.CLOSURESCOPES = S_after.CLOSURESCOPES ++ [pclosurescope]], pconstantclosure) = eps',
    '$trait_fcc_retired_receipt(S_after[.DECLARATIONS = S_seed.DECLARATIONS], pconstantclosure) = eps',
    '$trait_fcc_retired_receipt(S_after[.CLASSNAMES = S_after.CLASSNAMES ++ [($ptascii("c"), porigin_c)]], pconstantclosure) = eps',
    '$trait_fcc_retired_receipt(S_after, pconstantclosure[.PREFIX = $(pconstantclosure.PREFIX + 1)]) = eps',
    '$trait_fcc_retired_receipt(S_after, pconstantclosure[.DECL = porigin_c]) = eps',
    '$trait_fcc_retired_receipt(S_after, pconstantclosure[.SITE = porigin_c]) = eps',
    '$trait_fcc_receipt_source(S_after, pconstantclosure, ptraitcachecause[.TABLE = eps]) = eps',
    '$trait_fcc_receipt_source(S_after, pconstantclosure, ptraitcachecause[.LOOKUPS = eps]) = eps',
    '$trait_fcc_receipt_source(S_after, pconstantclosure, ptraitcachecause[.USERPREFIX = $(ptraitcachecause.USERPREFIX + 1)]) = eps',
    'S_first = S_after[.CONSTANTCLOSURES = pconstantclosure[.OBJECT = $(n_fcc + 1)] :: S_after.CONSTANTCLOSURES]',
    '$trait_fcc_receipt_source(S_first, pconstantclosure, ptraitcachecause) = eps',
    'S_method = S_after[.OBJECTS = $object_set(S_after.OBJECTS, n_fcc, CONSTANTCLOSURE porigin_site (METHODCLOSURE porigin_source porigin_site porigin_c eps))]',
    '$trait_fcc_receipt_source(S_method, pconstantclosure, ptraitcachecause) = eps',
    'S_missing = S_after[.CLASSCONSTANTHISTORY = S_seed.CLASSCONSTANTHISTORY]',
    '~$constant_callable_record_valid(S_missing, pconstantclosure)',
]

CASES = {
    'own-fcc-equal-scope-stays-disjoint-from-real-birth': {
        'source': SOURCES['equal-scope'], 'stage': STAGE,
        'checks': EQUAL,
    },
    'failed-imported-fcc-retires-without-publishing-or-executable-authority': {
        'source': SOURCES['failed-imported-fcc'], 'stage': STAGE,
        'checks': FAILED,
    },
}

# Genuine source prefixes; the forbidden FCC rows are negative inputs only.
ACCESS_SOURCES = {'private': '<?php\n'
            'trait T {\n'
            '    public static function m() { echo "M;"; }\n'
            '    public const Y = self::m(...);\n'
            '    public static $x = self::Y;\n'
            '}\n'
            'trait U { use T; }\n'
            'echo "PRE;";\n'
            'class C { use U { m as private; } public static $x = self::Y; }\n'
            'echo "POST;";\n',
 'protected': '<?php\n'
              'trait T {\n'
              '    public static function m() { echo "M;"; }\n'
              '    public const Y = self::m(...);\n'
              '    public static $x = self::Y;\n'
              '}\n'
              'trait U { use T; }\n'
              'echo "PRE;";\n'
              'class C { use U { m as protected; } public static $x = self::Y; }\n'
              'echo "POST;";\n'}
ACCESS_CHECKS = ['$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
 '$review19_fcc_table(S, pclassdesc_c) = ((S_constants, pclassdesc_constants))',
 '$class_constant_desc(pclassdesc_constants.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
 '$trait_fcc_source(S_constants, pclassconstantdesc_y)',
 '$ppproperty_desc_at(pclassdesc_constants.PROPERTIES, $ptascii("x")) = (ppropertydesc_x)',
 'ppropertydesc_x.DEFAULT = PROP_DEFERRED porigin_root',
 'porigin_root = PORIGIN n_source pcpath_root',
 '$origin_node(S.SOURCES, porigin_root) = (expression_root)',
 '$review_trait_object_seed(S_constants, pclassdesc_constants, porigin_root) = (F_seed)',
 '$review_trait_real_start(F_seed, pcpath_root, pclassconstantdesc_y, '
 '$expression_line(expression_root)) = ((S_start, ptraitcachecause))',
 '$trait_fcc_receipt_methods(S_start, ptraitcachecause) = ((S_copy, ptraitmethod*))',
 '$class_at(S_copy.CLASSES, porigin_c) = (pclassdesc_copy)',
 '$method_named(pclassdesc_copy.METHODS, $ptascii("m")) = (pmethoddesc_copy)',
 '$trait_fcc_receipt_target(pmethoddesc_copy, ptraitmethod*) = (pmethoddesc_unfixed)',
 'pmethoddesc_copy.OWNER = porigin_c',
 'pmethoddesc_unfixed.OWNER =/= porigin_c',
 '$class_at(S_copy.CLASSES, pmethoddesc_unfixed.OWNER) = (pclassdesc_exporter)',
 'pclassdesc_exporter.NAME = $ptascii("U")',
 'pclassdesc_exporter.KIND = "trait"',
 'pmethoddesc_unfixed[.OWNER = porigin_c] = pmethoddesc_copy',
 '$method_accessible(S_copy, pmethoddesc_copy, (porigin_c))',
 '~$method_accessible(S_copy, pmethoddesc_unfixed, (porigin_c))',
 'n_forbidden = |S_start.OBJECTS|',
 'porigin_site = pclassconstantdesc_y.INITIALIZER',
 '$origin_node(S_start.SOURCES, porigin_site) = (pcnode)',
 '$trait_fcc_form(pcnode)',
 'pconstantclosure = {OBJECT n_forbidden, SITE porigin_site, DECL pclassconstantdesc_y.ORIGIN, '
 'PREFIX ptraitcachecause.PREFIX}',
 'S_forbidden = S_start[.OBJECTS = S_start.OBJECTS ++ [CONSTANTCLOSURE porigin_site (METHODCLOSURE '
 'pmethoddesc_unfixed.FUNCTION.ORIGIN porigin_site porigin_c eps)]][.CONSTANTCLOSURES = '
 'S_start.CONSTANTCLOSURES ++ [pconstantclosure]][.CLASSCONSTANTHISTORY = '
 'S_start.CLASSCONSTANTHISTORY ++ [CCTRAITBIRTH n_forbidden porigin_site ptraitcachecause]]',
 '$trait_cache_cause_selected(S_forbidden, ptraitcachecause) = (pclassconstantdesc_y)',
 '$constant_callable_first(S_forbidden.CONSTANTCLOSURES, porigin_site) = (pconstantclosure)',
 '$trait_real_birth_at(S_forbidden.CLASSCONSTANTHISTORY, n_forbidden) = ((porigin_site, '
 'ptraitcachecause))',
 '$trait_fcc_receipt_source(S_forbidden, pconstantclosure, ptraitcachecause) = eps',
 '$trait_real_receipt_source(S_forbidden, pconstantclosure, ptraitcachecause) = eps']
CASES.update({
    f"forbidden-{visibility}-unfixed-trait-fcc-receipt": {
        "source": source, "stage": STAGE,
        "checks": [*ACCESS_CHECKS[:15],
                   f"pmethoddesc_copy.VISIBILITY = PROPERTY_{visibility.upper()}",
                   *ACCESS_CHECKS[15:]],
    }
    for visibility, source in ACCESS_SOURCES.items()
})


LATER_STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
         'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_e) '
         '-- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) '
         '-- if pclassdesc_e.NAME = $ptascii("E")')
LATER = [
    'S_seed = S[.TODO = ptask_tail*]',
    '$class_named(S_seed.CLASSNAMES, $ptascii("c")) = (porigin_c)',
    '$class_at(S_seed.CLASSES, porigin_c) = (pclassdesc_c)',
    '$method_named(pclassdesc_c.METHODS, $ptascii("m")) = (pmethoddesc_c)',
    'pmethoddesc_c.OWNER = porigin_c',
    'pmethoddesc_c.FUNCTION.ORIGIN = PORIGIN n_c pcpath_c',
    '$method_named(pclassdesc_e.METHODS, $ptascii("m")) = (pmethoddesc_e)',
    'pmethoddesc_e.OWNER = porigin_e',
    'pmethoddesc_e.FUNCTION.ORIGIN = PORIGIN n_e pcpath_e',
    'pmethoddesc_e.FUNCTION.ORIGIN =/= pmethoddesc_c.FUNCTION.ORIGIN',
    'S_link = $review_trait_real_failed_link(S_seed, pclassdesc_e)',
    'n_later = |S_seed.OBJECTS|',
    '$trait_real_birth_at(S_link.CLASSCONSTANTHISTORY, n_later) = ((porigin_site, ptraitcachecause))',
    '$constant_callable_record(S_link.CONSTANTCLOSURES, n_later) = (pconstantclosure)',
    '$constant_callable_first(S_seed.CONSTANTCLOSURES, porigin_site) = (pconstantclosure_first)',
    '$(pconstantclosure_first.OBJECT < n_later)',
    'pconstantclosure_first.DECL =/= pconstantclosure.DECL',
    '$(pconstantclosure_first.PREFIX < pconstantclosure.PREFIX)',
    '$trait_fcc_cached_header(S_seed, porigin_site) = ((pconstantclosure_first, porigin_c, pmethoddesc_c))',
    '$constant_callable_published(S_seed.DECLARATIONS[0:pconstantclosure.PREFIX], porigin_c)',
    '$constant_callable_cached_method_at(S_seed, porigin_site, pconstantclosure.PREFIX) = (pmethoddesc_c)',
    '$trait_cache_cause_selected(S_link, ptraitcachecause) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_e',
    'pconstantclosure.DECL = pclassconstantdesc_y.ORIGIN',
    'S_link.OBJECTS[n_later] = CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_c.FUNCTION.ORIGIN porigin_site porigin_e eps)',
    'HOBJECT n_later <- S_link.ALLOCATIONS',
    '$closure_scope_at(S_link.CLOSURESCOPES, n_later) = (pclosurescope)',
    r'pclosurescope.LEXICAL = porigin_c /\ pclosurescope.CALLED = porigin_e',
    r'pclosurescope.RECEIVER = eps /\ pclosurescope.CREATION = eps',
    '$trait_real_receipt_source(S_link, pconstantclosure, ptraitcachecause) = (pclassconstantdesc_y)',
    '$trait_failed_cache_ready(S_seed, S_link)',
    'PhpStep: S ~> S_after',
    'S_after.COMPLETION = STATICBYTES ptbytes_message z_fatal',
    'S_after.CLASSES = S_seed.CLASSES',
    'S_after.DECLARATIONS = S_seed.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_e $declaration_cause(S_seed)]',
    '$class_named(S_after.CLASSNAMES, $ptascii("e")) = eps',
    '$class_named(S_after.CLASSNAMES, $ptascii("c")) = (porigin_c)',
    '$trait_fcc_cached_header(S_after, porigin_site) = ((pconstantclosure_first, porigin_c, pmethoddesc_c))',
    '$constant_callable_record_valid(S_after, pconstantclosure_first)',
    '$constant_callable_value_valid(S_after, pconstantclosure_first.OBJECT, porigin_site)',
    'HOBJECT pconstantclosure_first.OBJECT <- S_after.ALLOCATIONS',
    '$class_constant_origin(S_after.CLASSES, pclassconstantdesc_y.ORIGIN) = eps',
    '$default_cache_at(S_after.CLASSCONSTANTCACHE, pclassconstantdesc_y.ORIGIN) = eps',
    '$trait_cache_event_at(S_after.CLASSCONSTANTHISTORY, pclassconstantdesc_y.ORIGIN) = eps',
    '~(HOBJECT n_later <- S_after.ALLOCATIONS)',
    '$closure_scope_at(S_after.CLOSURESCOPES, n_later) = eps',
    '$trait_fcc_retired_receipt(S_after, pconstantclosure) = (pclassconstantdesc_y)',
    '$trait_real_birth_owner(S_after, pconstantclosure) = (porigin_e)',
    '$constant_callable_record_valid(S_after, pconstantclosure)',
    '~$constant_callable_value_valid(S_after, n_later, porigin_site)',
    '$trait_fcc_birth_owner(S_after, pconstantclosure) = eps',
    '$class_constant_state_valid(S_after)',
    '$call_descriptors_valid(S_after)',
    '$declaration_history_valid(S_after)',
    '$heap_valid($heap_graph(S_after))',
    'S_fresh = S_after[.OBJECTS = $object_set(S_after.OBJECTS, n_later, CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_e.FUNCTION.ORIGIN porigin_site porigin_e eps))]',
    '$trait_fcc_receipt_source(S_fresh, pconstantclosure, ptraitcachecause) = eps',
    '~$constant_callable_record_valid(S_fresh, pconstantclosure)',
    'S_wrong_called = S_after[.OBJECTS = $object_set(S_after.OBJECTS, n_later, CONSTANTCLOSURE porigin_site (METHODCLOSURE pmethoddesc_c.FUNCTION.ORIGIN porigin_site porigin_c eps))]',
    '$trait_fcc_receipt_source(S_wrong_called, pconstantclosure, ptraitcachecause) = eps',
    '$trait_fcc_receipt_source(S_after, pconstantclosure[.PREFIX = pconstantclosure_first.PREFIX], ptraitcachecause[.PREFIX = pconstantclosure_first.PREFIX]) = eps',
    '$trait_fcc_receipt_source(S_after, pconstantclosure[.DECL = pconstantclosure_first.DECL], ptraitcachecause) = eps',
    '$trait_fcc_receipt_source(S_after, pconstantclosure, ptraitcachecause[.TABLE = eps]) = eps',
    'S_missing = S_after[.CLASSCONSTANTHISTORY = S_seed.CLASSCONSTANTHISTORY]',
    '~$constant_callable_record_valid(S_missing, pconstantclosure)',
    'S_live = S_after[.ALLOCATIONS = S_after.ALLOCATIONS ++ [HOBJECT n_later]]',
    '$trait_fcc_retired_receipt(S_live, pconstantclosure) = eps',
    '~$constant_callable_record_valid(S_live, pconstantclosure)',
]
CASES['published-first-target-survives-different-owner-failed-later-birth'] = {
    'source': SOURCES['published-first-target-failed-later-birth'],
    'stage': LATER_STAGE,
    'checks': LATER,
}

FAILED_TARGET_STAGE = ('S.TODO = (STATIC_INIT porigin_static) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if pcallcontext.TARGET = CLOSURE_TARGET n_fcc '
         '-- if pcallcontext.LEXICAL_CLASS = (porigin_u) '
         '-- if $class_at(S.CLASSES, porigin_u) = (pclassdesc_u) '
         '-- if pclassdesc_u.NAME = $ptascii("U") '
         '-- if pcallcontext.CALLED_CLASS = (porigin_e) '
         '-- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) '
         '-- if pclassdesc_e.NAME = $ptascii("E")')
FAILED_TARGET = [
    '$call_current_valid(S)',
    '$constant_callable_record(S.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
    '$constant_callable_first(S.CONSTANTCLOSURES, pconstantclosure.SITE) = (pconstantclosure_first)',
    '$(pconstantclosure_first.OBJECT < n_fcc)',
    'pconstantclosure_first.DECL =/= pconstantclosure.DECL',
    '$trait_fcc_failed_header(S, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, pmethoddesc_unfixed))',
    '$trait_fcc_cached_header(S, pconstantclosure.SITE) = eps',
    '$class_at(S.CLASSES, porigin_c) = (pclassdesc_c)',
    'pclassdesc_c.NAME = $ptascii("C")',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S.CLASSNAMES, $ptascii("e")) = (porigin_e)',
    '$trait_failed_cache_index(S.DECLARATIONS, porigin_c, 0) = (n_failed)',
    '$(n_failed < pconstantclosure.PREFIX)',
    '$class_method_origin(S.CLASSES, pcallcontext.FUNCTION) = eps',
    '$closure_method_origin(S, pcallcontext.FUNCTION) = (pmethoddesc)',
    'pmethoddesc.OWNER = porigin_c',
    'pmethoddesc.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_c porigin_source ptbytes_method',
    'pmethoddesc.NAME = $ptascii("m")',
    'pmethoddesc_unfixed.OWNER = porigin_u',
    'pmethoddesc_unfixed[.OWNER = porigin_c] = pmethoddesc',
    'pmethoddesc.FUNCTION <- $trait_fcc_retained_functions(S)',
    '$function_at($all_functions(S), pmethoddesc.FUNCTION.ORIGIN) = (pmethoddesc.FUNCTION)',
    '$constant_callable_cached_method_at(S, pconstantclosure.SITE, pconstantclosure.PREFIX) = (pmethoddesc_unfixed)',
    '$constant_callable_cached_method_at(S, pconstantclosure.SITE, pconstantclosure_first.PREFIX) = eps',
    '$constant_callable_record_valid(S, pconstantclosure_first)',
    '~$constant_callable_value_valid(S, pconstantclosure_first.OBJECT, pconstantclosure.SITE)',
    '~(HOBJECT pconstantclosure_first.OBJECT <- S.ALLOCATIONS)',
    '$closure_scope_at(S.CLOSURESCOPES, pconstantclosure_first.OBJECT) = eps',
    '$constant_callable_record_valid(S, pconstantclosure)',
    '$constant_callable_value_valid(S, n_fcc, pconstantclosure.SITE)',
    'S.OBJECTS[n_fcc] = CONSTANTCLOSURE pconstantclosure.SITE (METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN pconstantclosure.SITE porigin_e eps)',
    '$closure_scope_at(S.CLOSURESCOPES, n_fcc) = (pclosurescope)',
    r'pclosurescope.LEXICAL = porigin_u /\ pclosurescope.CALLED = porigin_e',
    r'pclosurescope.RECEIVER = eps /\ pclosurescope.CREATION = eps',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_e, pclosurescope) = (porigin_e)',
    '$method_closure_scope_valid(S, pclosurescope)',
    '$target_function(S, CLOSURE_TARGET n_fcc) = (pfunction)',
    'pfunction = pmethoddesc.FUNCTION',
    '$default_at(pfunction.DEFAULTS, 0) = (pdefault)',
    'pdefault.KIND = PDSTORED',
    '$lookup(S.ENV, $ptascii("v")) = (n_parameter)',
    'S.STORE[n_parameter] = DEFINED (PINT 7)',
    '$state_static_at(S, porigin_static) = eps',
    '$trait_static_key(S, porigin_static) = TRAIT_ORIGIN porigin_c porigin_static ptbytes_method',
    'PhpStep: S ~> S_static',
    'S_static.COMPLETION = NORMAL',
    'S_static.CURRENT = S.CURRENT',
    '$state_static_at(S_static, porigin_static) = (n_static)',
    '$lookup(S_static.ENV, $ptascii("n")) = (n_static)',
    'S_static.STORE[n_static] = DEFINED (PINT 0)',
    '$static_at(S_static.STATICS, TRAIT_ORIGIN porigin_c porigin_static ptbytes_method) = (n_static)',
    '$class_constant_state_valid(S_static)',
    '$call_descriptors_valid(S_static)',
    '$declaration_history_valid(S_static)',
    '$heap_valid($heap_graph(S_static))',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_e, pclosurescope[.LEXICAL = porigin_c]) = eps',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_e, pclosurescope[.RECEIVER = (n_fcc)]) = eps',
    '$method_named(pclassdesc_e.METHODS, $ptascii("m")) = (pmethoddesc_e)',
    'pmethoddesc_e.FUNCTION.ORIGIN =/= pmethoddesc.FUNCTION.ORIGIN',
    'S_fresh = S[.OBJECTS = $object_set(S.OBJECTS, n_fcc, CONSTANTCLOSURE pconstantclosure.SITE (METHODCLOSURE pmethoddesc_e.FUNCTION.ORIGIN pconstantclosure.SITE porigin_e eps))]',
    '$trait_fcc_scope_owner(S_fresh, pmethoddesc_e, pconstantclosure.SITE, porigin_e, pclosurescope) = eps',
    '~$closure_scope_row_valid(S_fresh, pclosurescope)',
    'S_resurrect = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT pconstantclosure_first.OBJECT]]',
    '$trait_fcc_failed_header(S_resurrect, pconstantclosure.SITE) = eps',
    '$closure_method_origin(S_resurrect, pcallcontext.FUNCTION) = eps',
    'S.CONSTANTCLOSURES = pconstantclosure_first :: pconstantclosure_tail*',
    'S_wrong_decl = S[.CONSTANTCLOSURES = pconstantclosure_first[.DECL = porigin_c] :: pconstantclosure_tail*]',
    '$trait_fcc_failed_header(S_wrong_decl, pconstantclosure.SITE) = eps',
    '$closure_method_origin(S_wrong_decl, pcallcontext.FUNCTION) = eps',
]
CASES['failed-first-target-shutdown-default-and-static-identity'] = {
    'source': SOURCES['failed-first-shutdown'],
    'stage': FAILED_TARGET_STAGE,
    'checks': FAILED_TARGET,
}

FAILED_ALIAS_STAGE = ('S.TODO = (STATIC_INIT porigin_static) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if pcallcontext.TARGET = CLOSURE_TARGET n_fcc '
         '-- if pcallcontext.LEXICAL_CLASS = (porigin_u) '
         '-- if $class_at(S.CLASSES, porigin_u) = (pclassdesc_u) '
         '-- if pclassdesc_u.NAME = $ptascii("U") '
         '-- if pcallcontext.CALLED_CLASS = (porigin_e) '
         '-- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) '
         '-- if pclassdesc_e.NAME = $ptascii("E")')
FAILED_ALIAS = [
    '$call_current_valid(S)',
    '$constant_callable_record(S.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
    '$constant_callable_first(S.CONSTANTCLOSURES, pconstantclosure.SITE) = (pconstantclosure_first)',
    '$trait_fcc_failed_header(S, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, pmethoddesc_unfixed))',
    '$(pconstantclosure_first.OBJECT < n_fcc)',
    '$trait_fcc_cached_header(S, pconstantclosure.SITE) = eps',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S.CLASSNAMES, $ptascii("e")) = (porigin_e)',
    '$method_named(pclassdesc_e.METHODS, $ptascii("q")) = eps',
    '$trait_real_birth_at(S.CLASSCONSTANTHISTORY, n_fcc) = eps',
    '$class_constant_callable_receipt_owner(S, pconstantclosure) = (porigin_e)',
    '$constant_callable_published(S.DECLARATIONS[0:pconstantclosure.PREFIX], porigin_e)',
    '$constant_callable_cached_method_at(S, pconstantclosure.SITE, pconstantclosure.PREFIX) = (pmethoddesc_unfixed)',
    '$trait_fcc_snapshot_ordinary(S, pconstantclosure) = (pmethoddesc_unfixed)',
    '$class_method_origin(S.CLASSES, pcallcontext.FUNCTION) = eps',
    '$closure_method_origin(S, pcallcontext.FUNCTION) = (pmethoddesc)',
    'pmethoddesc.FUNCTION.ORIGIN = TRAIT_ORIGIN porigin_c porigin_source ptbytes_method',
    'pmethoddesc.NAME = $ptascii("q")',
    'pmethoddesc_unfixed.OWNER = porigin_u',
    'pmethoddesc_unfixed[.OWNER = porigin_c] = pmethoddesc',
    '$constant_callable_record_valid(S, pconstantclosure_first)',
    '~$constant_callable_value_valid(S, pconstantclosure_first.OBJECT, pconstantclosure.SITE)',
    '$constant_callable_value_valid(S, n_fcc, pconstantclosure.SITE)',
    '$closure_scope_at(S.CLOSURESCOPES, n_fcc) = (pclosurescope)',
    r'pclosurescope.LEXICAL = porigin_u /\ pclosurescope.CALLED = porigin_e',
    r'pclosurescope.RECEIVER = eps /\ pclosurescope.CREATION = eps',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_e, pclosurescope) = (porigin_e)',
    '$method_closure_scope_valid(S, pclosurescope)',
    '$trait_static_key(S, porigin_static) = TRAIT_ORIGIN porigin_c porigin_static ptbytes_method',
    'PhpStep: S ~> S_static',
    'S_static.COMPLETION = NORMAL',
    '$state_static_at(S_static, porigin_static) = (n_static)',
    'S_static.STORE[n_static] = DEFINED (PINT 0)',
    '$static_at(S_static.STATICS, TRAIT_ORIGIN porigin_c porigin_static ptbytes_method) = (n_static)',
    '$class_constant_state_valid(S_static)',
    '$call_descriptors_valid(S_static)',
    '$declaration_history_valid(S_static)',
    '$heap_valid($heap_graph(S_static))',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_e, pclosurescope[.CALLED = porigin_c]) = eps',
    'S_wrong_called = S[.OBJECTS = $object_set(S.OBJECTS, n_fcc, CONSTANTCLOSURE pconstantclosure.SITE (METHODCLOSURE pmethoddesc.FUNCTION.ORIGIN pconstantclosure.SITE porigin_c eps))]',
    '$trait_fcc_snapshot_ordinary(S_wrong_called, pconstantclosure) = eps',
    '$trait_fcc_snapshot_ordinary(S, pconstantclosure[.PREFIX = pconstantclosure_first.PREFIX]) = eps',
    'S.CONSTANTCLOSURES = pconstantclosure_first :: pconstantclosure_tail*',
    'S_wrong_source = S[.CONSTANTCLOSURES = pconstantclosure_first[.DECL = porigin_c] :: pconstantclosure_tail*]',
    '$trait_fcc_failed_header(S_wrong_source, pconstantclosure.SITE) = eps',
    '$trait_fcc_snapshot_ordinary(S_wrong_source, pconstantclosure) = eps',
]
CASES['failed-first-alias-target-published-import-scope'] = {
    'source': SOURCES['failed-first-alias-target-shutdown'],
    'stage': FAILED_ALIAS_STAGE,
    'checks': FAILED_ALIAS,
}

BOTH_FAILED_STAGE = ('S.TODO = (STMT (NStmtClass phpType14 phpType24 phpType3 '
         'phpType44 phpType42 phpType23 metadata)) :: ptask_tail* '
         '-- if S.ORIGIN = (porigin_e) '
         '-- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) '
         '-- if pclassdesc_e.NAME = $ptascii("E")')
BOTH_FAILED = [
    'S_seed = S[.TODO = ptask_tail*]',
    'S_seed.CONSTANTCLOSURES = pconstantclosure_first :: pconstantclosure_tail*',
    '$trait_fcc_failed_header(S_seed, pconstantclosure_first.SITE) = ((pconstantclosure_first, porigin_c, pmethoddesc_unfixed))',
    '$class_named(S_seed.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S_seed.CLASSNAMES, $ptascii("e")) = eps',
    '$trait_failed_cache_index(S_seed.DECLARATIONS, porigin_c, 0) = (n_failed)',
    '$closure_method_origin(S_seed, pmethoddesc_unfixed.FUNCTION.ORIGIN) = (pmethoddesc_c)',
    'pmethoddesc_c.OWNER = porigin_c',
    '$method_named(pclassdesc_e.METHODS, $ptascii("m")) = (pmethoddesc_e)',
    'pmethoddesc_e.FUNCTION.ORIGIN =/= pmethoddesc_c.FUNCTION.ORIGIN',
    'S_link = $review_trait_real_failed_link(S_seed, pclassdesc_e)',
    'n_later = |S_seed.OBJECTS|',
    '$trait_real_birth_at(S_link.CLASSCONSTANTHISTORY, n_later) = ((pconstantclosure_first.SITE, ptraitcachecause))',
    '$constant_callable_record(S_link.CONSTANTCLOSURES, n_later) = (pconstantclosure)',
    'pconstantclosure.DECL =/= pconstantclosure_first.DECL',
    '$(n_failed < pconstantclosure.PREFIX)',
    '$constant_callable_cached_method_at(S_link, pconstantclosure.SITE, pconstantclosure.PREFIX) = (pmethoddesc_unfixed)',
    'S_link.OBJECTS[n_later] = CONSTANTCLOSURE pconstantclosure.SITE (METHODCLOSURE pmethoddesc_c.FUNCTION.ORIGIN pconstantclosure.SITE porigin_e eps)',
    '$closure_scope_at(S_link.CLOSURESCOPES, n_later) = (pclosurescope)',
    'pclosurescope.LEXICAL = pmethoddesc_unfixed.OWNER',
    'pclosurescope.CALLED = porigin_e',
    '$trait_fcc_receipt_source(S_link, pconstantclosure, ptraitcachecause) = (pclassconstantdesc_y)',
    'pclassconstantdesc_y.OWNER = porigin_e',
    '$trait_failed_cache_ready(S_seed, S_link)',
    'PhpStep: S ~> S_after',
    'S_after.COMPLETION = STATICBYTES ptbytes_message z_fatal',
    'S_after.CLASSES = S_seed.CLASSES',
    'S_after.DECLARATIONS = S_seed.DECLARATIONS ++ [PDRTRAITCACHEFAIL porigin_e $declaration_cause(S_seed)]',
    '$class_named(S_after.CLASSNAMES, $ptascii("c")) = eps',
    '$class_named(S_after.CLASSNAMES, $ptascii("e")) = eps',
    '$trait_fcc_failed_header(S_after, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, pmethoddesc_unfixed))',
    '$trait_fcc_cached_header(S_after, pconstantclosure.SITE) = eps',
    '$constant_callable_record_valid(S_after, pconstantclosure_first)',
    '~$constant_callable_value_valid(S_after, pconstantclosure_first.OBJECT, pconstantclosure.SITE)',
    '$trait_fcc_retired_receipt(S_after, pconstantclosure) = (pclassconstantdesc_y)',
    '$constant_callable_record_valid(S_after, pconstantclosure)',
    '~$constant_callable_value_valid(S_after, n_later, pconstantclosure.SITE)',
    '~(HOBJECT pconstantclosure_first.OBJECT <- S_after.ALLOCATIONS)',
    '~(HOBJECT n_later <- S_after.ALLOCATIONS)',
    '$closure_scope_at(S_after.CLOSURESCOPES, pconstantclosure_first.OBJECT) = eps',
    '$closure_scope_at(S_after.CLOSURESCOPES, n_later) = eps',
    '$trait_fcc_birth_owner(S_after, pconstantclosure) = eps',
    '$class_constant_state_valid(S_after)',
    '$call_descriptors_valid(S_after)',
    '$declaration_history_valid(S_after)',
    '$heap_valid($heap_graph(S_after))',
    'S_fresh = S_after[.OBJECTS = $object_set(S_after.OBJECTS, n_later, CONSTANTCLOSURE pconstantclosure.SITE (METHODCLOSURE pmethoddesc_e.FUNCTION.ORIGIN pconstantclosure.SITE porigin_e eps))]',
    '$trait_fcc_receipt_source(S_fresh, pconstantclosure, ptraitcachecause) = eps',
    '~$constant_callable_record_valid(S_fresh, pconstantclosure)',
    'S_wrong_called = S_after[.OBJECTS = $object_set(S_after.OBJECTS, n_later, CONSTANTCLOSURE pconstantclosure.SITE (METHODCLOSURE pmethoddesc_c.FUNCTION.ORIGIN pconstantclosure.SITE porigin_c eps))]',
    '$trait_fcc_receipt_source(S_wrong_called, pconstantclosure, ptraitcachecause) = eps',
    '$trait_fcc_receipt_source(S_after, pconstantclosure[.PREFIX = pconstantclosure_first.PREFIX], ptraitcachecause[.PREFIX = pconstantclosure_first.PREFIX]) = eps',
    'S_after.CONSTANTCLOSURES = pconstantclosure_first :: pconstantclosure_later*',
    'S_wrong_source = S_after[.CONSTANTCLOSURES = pconstantclosure_first[.DECL = porigin_c] :: pconstantclosure_later*]',
    '$trait_fcc_failed_header(S_wrong_source, pconstantclosure.SITE) = eps',
    '$trait_fcc_receipt_source(S_wrong_source, pconstantclosure, ptraitcachecause) = eps',
    'S_live = S_after[.ALLOCATIONS = S_after.ALLOCATIONS ++ [HOBJECT n_later]]',
    '$trait_fcc_retired_receipt(S_live, pconstantclosure) = eps',
    '~$constant_callable_record_valid(S_live, pconstantclosure)',
]
CASES['failed-first-target-followed-by-failed-later-import'] = {
    'source': SOURCES['failed-first-target-failed-later-import'],
    'stage': BOTH_FAILED_STAGE,
    'checks': BOTH_FAILED,
}

FAILED_FIXUP_STAGE = ('S.TODO = (STATIC_INIT porigin_static) :: ptask_tail* '
         '-- if S.CURRENT = (pcallcontext) '
         '-- if pcallcontext.TARGET = CLOSURE_TARGET n_fcc '
         '-- if pcallcontext.LEXICAL_CLASS = (porigin_c) '
         '-- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) '
         '-- if pclassdesc_c.NAME = $ptascii("C") '
         '-- if pcallcontext.CALLED_CLASS = (porigin_e) '
         '-- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) '
         '-- if pclassdesc_e.NAME = $ptascii("E")')
FAILED_FIXUP = [
    '$call_current_valid(S)',
    '$constant_callable_record(S.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
    '$constant_callable_first(S.CONSTANTCLOSURES, pconstantclosure.SITE) = (pconstantclosure_first)',
    '$trait_fcc_failed_header(S, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, pmethoddesc_unfixed))',
    'pmethoddesc_unfixed.OWNER = porigin_u',
    '$class_at(S.CLASSES, porigin_u) = (pclassdesc_u)',
    '$class_named(S.CLASSNAMES, $ptascii("c")) = eps /\\ $class_named(S.CLASSNAMES, $ptascii("e")) = (porigin_e)',
    '$closure_method_origin(S, pcallcontext.FUNCTION) = (pmethoddesc)',
    'pmethoddesc = pmethoddesc_unfixed[.OWNER = porigin_c]',
    '$trait_fcc_failed_fixup_at(S, pconstantclosure_first, pconstantclosure.PREFIX) = ((porigin_c, pmethoddesc))',
    '$trait_fcc_failed_fixup_at(S, pconstantclosure_first, pconstantclosure_first.PREFIX) = eps',
    '$trait_fcc_fixed_at_known(S, pconstantclosure_first, porigin_c, pmethoddesc_unfixed, pconstantclosure_first.PREFIX) = (pmethoddesc_unfixed)',
    '$constant_callable_record_valid(S, pconstantclosure_first) /\\ ~(HOBJECT pconstantclosure_first.OBJECT <- S.ALLOCATIONS) /\\ $closure_scope_at(S.CLOSURESCOPES, pconstantclosure_first.OBJECT) = eps',
    '$closure_scope_at(S.CLOSURESCOPES, n_fcc) = (pclosurescope)',
    'pclassdesc_u.NAME = $ptascii("U") /\\ pclosurescope.LEXICAL = porigin_c /\\ pclosurescope.CALLED = porigin_e',
    '$method_closure_scope_valid(S, pclosurescope)',
    '$method_self_class_scope_valid(S, pclassdesc_c)',
    '~$method_self_class_scope_valid(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_u)])], pclassdesc_c)',
    '~$method_self_class_scope_valid(S[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET pconstantclosure_first.OBJECT][.INSTANCE = (pconstantclosure_first.OBJECT)])], pclassdesc_c)',
    '$lookup(S.ENV, $ptascii("v")) = (n_parameter)',
    'S.STORE[n_parameter] = DEFINED (PINT 7)',
    '$state_static_at(S, porigin_static) = eps',
    '$trait_static_key(S, porigin_static) = TRAIT_ORIGIN porigin_c porigin_static $ptascii("m")',
    'PhpStep: S ~> S_static',
    'S_static.COMPLETION = NORMAL /\\ S_static.CURRENT = S.CURRENT',
    '$state_static_at(S_static, porigin_static) = (n_static)',
    '$lookup(S_static.ENV, $ptascii("n")) = (n_static) /\\ S_static.STORE[n_static] = DEFINED (PINT 0) /\\ $static_at(S_static.STATICS, TRAIT_ORIGIN porigin_c porigin_static $ptascii("m")) = (n_static)',
    '$class_constant_state_valid(S_static)',
    '$call_descriptors_valid(S_static)',
    '$declaration_history_valid(S_static)',
    '$heap_valid($heap_graph(S_static))',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_e, pclosurescope[.LEXICAL = porigin_u]) = eps',
    '$trait_fcc_scope_owner(S, pmethoddesc, pconstantclosure.SITE, porigin_e, pclosurescope[.CALLED = porigin_c]) = eps',
    '~$constant_callable_cached_method_access(S, pconstantclosure.SITE, porigin_e, pmethoddesc_unfixed)',
    '$method_named(pclassdesc_e.METHODS, $ptascii("m")) = (pmethoddesc_e)',
    'S_fresh = S[.OBJECTS = $object_set(S.OBJECTS, n_fcc, CONSTANTCLOSURE pconstantclosure.SITE (METHODCLOSURE pmethoddesc_e.FUNCTION.ORIGIN pconstantclosure.SITE porigin_e eps))]',
    '$trait_fcc_scope_owner(S_fresh, pmethoddesc_e, pconstantclosure.SITE, porigin_e, pclosurescope) = eps',
    '~$method_self_class_scope_valid(S_fresh, pclassdesc_c)',
    '$trait_fcc_scope_receipt(S, pconstantclosure[.PREFIX = pconstantclosure_first.PREFIX], pmethoddesc, pclosurescope) = eps',
    '$trait_real_birth_at(S.CLASSCONSTANTHISTORY, pconstantclosure_first.OBJECT) = ((pconstantclosure_first.SITE, ptraitcachecause_first))',
    'S_wrong_table = S[.CLASSCONSTANTHISTORY = [CCTRAITBIRTH pconstantclosure_first.OBJECT pconstantclosure_first.SITE ptraitcachecause_first[.TABLE = eps]] ++ S.CLASSCONSTANTHISTORY]',
    '$trait_fcc_failed_fixup_at(S_wrong_table, pconstantclosure_first, pconstantclosure.PREFIX) = eps',
    # Synthetic opposite-operand probes retain the genuine first demand/receipt.
    '$ppproperty_desc_at(pclassdesc_u.PROPERTIES, $ptascii("x")) = (ppropertydesc_u)',
    'S_before_fixup = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_u[.PROPERTIES = [ppropertydesc_u[.DEFAULT = PROP_LITERAL (PINT 0)]]])]',
    '$trait_fcc_failed_header(S_before_fixup, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, pmethoddesc_unfixed))',
    '$trait_fcc_failed_fixup_at(S_before_fixup, pconstantclosure_first, pconstantclosure.PREFIX) = ((porigin_c, pmethoddesc_unfixed))',
    'S_unknown_phase = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_u[.PROPERTIES = [ppropertydesc_u[.DEFAULT = PROP_DEFERRED porigin_u]]])]',
    '$trait_fcc_failed_header(S_unknown_phase, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, pmethoddesc_unfixed))',
    '$trait_fcc_failed_fixup_at(S_unknown_phase, pconstantclosure_first, pconstantclosure.PREFIX) = eps',
    '$constant_callable_method_cached_at(S_unknown_phase, pconstantclosure.SITE, pconstantclosure.PREFIX)',
    '$constant_callable_method(S_unknown_phase, pconstantclosure.SITE, porigin_e, pconstantclosure.PREFIX) = eps',
    '~$constant_callable_method_access(S_unknown_phase, pconstantclosure.SITE, porigin_e, pmethoddesc)',
    '$default_cache_at(S.CLASSCONSTANTCACHE, pconstantclosure.DECL) = (pdefaultcache_e)',
    'S_wrong_cache = S[.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE ++ [pdefaultcache_e[.ORIGIN = pconstantclosure_first.DECL]]]',
    '$trait_fcc_failed_fixup_at(S_wrong_cache, pconstantclosure_first, pconstantclosure.PREFIX) = eps',
    'S_resurrect = S[.ALLOCATIONS = S.ALLOCATIONS ++ [HOBJECT pconstantclosure_first.OBJECT]]',
    '$trait_fcc_failed_fixup_at(S_resurrect, pconstantclosure_first, pconstantclosure.PREFIX) = eps',
    'S_wrong_abstract = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_c[.ABSTRACT = true])]',
    '~$declaration_history_valid(S_wrong_abstract)',
]
CASES['failed-first-post-fixup-target-shutdown-default-and-static-identity'] = {
    'source': SOURCES['failed-first-post-fixup-abstract-shutdown'],
    'stage': FAILED_FIXUP_STAGE,
    'checks': FAILED_FIXUP,
}

FAILED_SELF_NEW_STAGE = ('S.TODO = (EVAL (NExprNew (NName (BYTES text_self) metadata_name) (SEQUENCE phpType7*) metadata)) :: '
 'ptask_tail* -- if $ptlc($base64(text_self)) = $ptascii("self") -- if S.ORIGIN = (porigin_site) -- if '
 'S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_fcc -- if '
 'pcallcontext.LEXICAL_CLASS = (porigin_c) -- if $class_at(S.CLASSES, porigin_c) = (pclassdesc_c) -- if '
 'pclassdesc_c.NAME = $ptascii("C") -- if pcallcontext.CALLED_CLASS = (porigin_e) -- if $class_at(S.CLASSES, '
 'porigin_e) = (pclassdesc_e) -- if pclassdesc_e.NAME = $ptascii("E")')
FAILED_SELF_NEW = ['$ordinary_keyword_new_site(S, porigin_site)',
 '$method_source_task(S, NExprNew (NName (BYTES text_self) metadata_name) (SEQUENCE phpType7*) metadata)',
 '$call_current_valid(S)',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
 '$trait_fcc_failed_header(S, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, '
 'pmethoddesc_unfixed))',
 'pmethoddesc_unfixed.OWNER = porigin_u',
 '$class_at(S.CLASSES, porigin_u) = (pclassdesc_u)',
 '$class_named(S.CLASSNAMES, $ptascii("c")) = eps /\\ $class_named(S.CLASSNAMES, $ptascii("e")) = '
 '(porigin_e)',
 '~pclassdesc_c.ABSTRACT /\\ pclassdesc_c.PARENT = eps /\\ pclassdesc_c.INTERFACES = eps',
 '$closure_scope_at(S.CLOSURESCOPES, n_fcc) = (pclosurescope)',
 'pclosurescope.LEXICAL = porigin_c /\\ pclosurescope.CALLED = porigin_e',
 '$method_closure_scope_valid(S, pclosurescope)',
 '$trait_fcc_retained_new_scope(S, porigin_site) = ((pclassdesc_c, pconstantclosure_first))',
 '$trait_fcc_failed_abstract(S, pclassdesc_c, pconstantclosure_first)',
 '$constant_callable_record_valid(S, pconstantclosure_first) /\\ ~(HOBJECT pconstantclosure_first.OBJECT <- '
 'S.ALLOCATIONS) /\\ $closure_scope_at(S.CLOSURESCOPES, pconstantclosure_first.OBJECT) = eps',
 'porigin_site = PORIGIN n_unit pcpath_site',
 '$code_at(S.CODE, n_unit) = (pcode)',
 '$code_expression(pcode.EXPRESSIONS, pcpath_site) = ((z, false))',
 'PhpStep: S ~> S_rejected',
 'S_rejected.COMPLETION = THROWN "Error" $ptascii("Cannot instantiate abstract class C") z',
 'S_rejected.TODO = ptask_tail* /\\ S_rejected.CURRENT = S.CURRENT',
 'S_rejected.OBJECTS = S.OBJECTS /\\ S_rejected.ALLOCATIONS = S.ALLOCATIONS /\\ S_rejected.EVENTS = S.EVENTS',
 '$class_constant_state_valid(S_rejected)',
 '$call_descriptors_valid(S_rejected)',
 '$declaration_history_valid(S_rejected)',
 '$heap_valid($heap_graph(S_rejected))',
 '$trait_fcc_retained_new_scope(S, pconstantclosure_first.SITE) = eps',
 '$trait_fcc_retained_new_scope(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_u)])], porigin_site) = '
 'eps',
 '$trait_fcc_retained_new_scope(S[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET '
 'pconstantclosure_first.OBJECT][.INSTANCE = (pconstantclosure_first.OBJECT)])], porigin_site) = eps',
 '~$trait_fcc_failed_abstract(S, pclassdesc_e, pconstantclosure_first)',
 '~$trait_fcc_failed_abstract(S, pclassdesc_c, pconstantclosure_first[.PREFIX = '
 '$(pconstantclosure_first.PREFIX + 1)])',
 '$method_named(pclassdesc_u.METHODS, $ptascii("m")) = (pmethoddesc_u)',
 'S_no_requirement = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_u[.METHODS = [pmethoddesc_u]])]',
 '~$trait_fcc_failed_abstract(S_no_requirement, pclassdesc_c, pconstantclosure_first)',
 '$trait_fcc_retained_new(S_no_requirement, pclassdesc_c, pconstantclosure_first, z) = '
 'S_no_requirement[.COMPLETION = UNSUPPORTED "retained failed class construction"]',
 'S_interface = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_c[.INTERFACES = '
 '[$ptascii("Stringable")]])]',
 '~$trait_fcc_failed_abstract(S_interface, pclassdesc_c[.INTERFACES = [$ptascii("Stringable")]], '
 'pconstantclosure_first)',
 'S_parent = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_c[.PARENT = (pclassdesc_e.NAME)])]',
 '~$trait_fcc_failed_abstract(S_parent, pclassdesc_c[.PARENT = (pclassdesc_e.NAME)], pconstantclosure_first)']
CASES['failed-first-post-fixup-abstract-self-new-before-arguments'] = {
    'source': SOURCES['failed-first-post-fixup-abstract-self-new'],
    'stage': FAILED_SELF_NEW_STAGE,
    'checks': FAILED_SELF_NEW,
}

FAILED_STATIC_NEW_STAGE = ('S.TODO = (NOCTOR_ARGS pnoctorcall) :: (DYNAMIC_NEW_FINISH pdynamicnew) :: ptask_tail* -- if '
 'pnoctorcall.INDEX = 0 -- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = '
 'CLOSURE_TARGET n_fcc -- if pcallcontext.LEXICAL_CLASS = (porigin_c) -- if $class_at(S.CLASSES, '
 'porigin_c) = (pclassdesc_c) -- if pclassdesc_c.NAME = $ptascii("C") -- if '
 'pcallcontext.CALLED_CLASS = (porigin_e) -- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) '
 '-- if pclassdesc_e.NAME = $ptascii("E")')
FAILED_STATIC_NEW = ['$call_current_valid(S)',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
 '$trait_fcc_failed_header(S, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, '
 'pmethoddesc_unfixed))',
 '$constant_callable_record_valid(S, pconstantclosure_first) /\\ ~(HOBJECT '
 'pconstantclosure_first.OBJECT <- S.ALLOCATIONS) /\\ $closure_scope_at(S.CLOSURESCOPES, '
 'pconstantclosure_first.OBJECT) = eps',
 '$class_named(S.CLASSNAMES, $ptascii("c")) = eps /\\ $class_named(S.CLASSNAMES, $ptascii("e")) = '
 '(porigin_e)',
 '$closure_scope_at(S.CLOSURESCOPES, n_fcc) = (pclosurescope)',
 'pdynamicnew.CLOSURE = (CLOSURE_SCOPE pclosurescope) /\\ pdynamicnew.SCOPE = (porigin_c) /\\ '
 'pdynamicnew.CALLED = (porigin_e)',
 '$class_static_selection_scope_method(S, $dynamic_new_scope_source(S, pdynamicnew), porigin_c) = '
 'eps',
 '$ordinary_keyword_new_site(S, pdynamicnew.SITE)',
 '$dynamic_new_record_scope(S, pdynamicnew)',
 '$dynamic_new_record_valid(S, pdynamicnew)',
 '$dynamic_new_valid(S, pdynamicnew)',
 'pnoctorcall.SITE = pdynamicnew.SITE /\\ pnoctorcall.CLASS = pclassdesc_e.NAME /\\ '
 'pnoctorcall.SENT = eps',
 'S.OBJECTS[pnoctorcall.OBJECT] = INSTANCE porigin_e /\\ HOBJECT pnoctorcall.OBJECT <- '
 'S.ALLOCATIONS',
 'HOBJECT pnoctorcall.OBJECT <- $task_nodes(NOCTOR_ARGS pnoctorcall)',
 '$call_task_valid(S, NOCTOR_ARGS pnoctorcall)',
 '$class_constant_table_done(S, porigin_e)',
 '(CCUPDATENEW porigin_e pdynamicnew $(|S.DECLARATIONS|)) <- S.CLASSCONSTANTHISTORY',
 '$ppproperty_desc_at(pclassdesc_e.PROPERTIES, $ptascii("x")) = (ppropertydesc_x)',
 'ppropertydesc_x.ORIGIN = porigin_x',
 'n_fill = $nabs($(|S.CLASSCONSTANTHISTORY| - 2))',
 'S.CLASSCONSTANTHISTORY[n_fill] = CCSTATICNEW porigin_x pdynamicnew $(|S.DECLARATIONS|)',
 '$class_constant_history_fold(S, S.CLASSCONSTANTHISTORY[0:n_fill] ++ [CCSTATICNEW porigin_x '
 'pdynamicnew[.CALLED = (porigin_c)] $(|S.DECLARATIONS|)] ++ S.CLASSCONSTANTHISTORY[$nabs($(n_fill '
 '+ 1)):1], eps, eps, 0) = CCBAD',
 'pnoctorcall.ARGUMENTS = (NArg ABSENT expression (BOOLEAN false) (BOOLEAN false) metadata_arg) :: '
 'phpType7_tail*',
 'PhpStep: S ~> S_argument',
 'S_argument.COMPLETION = NORMAL /\\ S_argument.CURRENT = S.CURRENT',
 'S_argument.TODO = [$at_task($noctor_arg_origin(pnoctorcall), EVAL expression), NOCTOR_SEND '
 'pnoctorcall[.ARGUMENTS = phpType7_tail*], DYNAMIC_NEW_FINISH pdynamicnew] ++ ptask_tail*',
 'S_argument.OBJECTS = S.OBJECTS /\\ S_argument.ALLOCATIONS = S.ALLOCATIONS /\\ S_argument.EVENTS '
 '= S.EVENTS',
 '$class_constant_state_valid(S_argument)',
 '$call_descriptors_valid(S_argument)',
 '$declaration_history_valid(S_argument)',
 '$heap_valid($heap_graph(S_argument))',
 '~$dynamic_new_record_scope(S, pdynamicnew[.SCOPE = (pmethoddesc_unfixed.OWNER)])',
 '~$dynamic_new_record_scope(S, pdynamicnew[.CALLED = (porigin_c)])',
 '~$dynamic_new_record_scope(S, pdynamicnew[.SITE = pconstantclosure_first.SITE])',
 '~$dynamic_new_record_scope(S, pdynamicnew[.SCOPE = (pmethoddesc_unfixed.OWNER)][.CLOSURE = '
 '(CLOSURE_SCOPE pclosurescope[.LEXICAL = pmethoddesc_unfixed.OWNER])])',
 '~$dynamic_new_record_scope(S, pdynamicnew[.CLOSURE = (CLOSURE_SCOPE pclosurescope[.OBJECT = '
 'pconstantclosure_first.OBJECT])])',
 '$method_named(pclassdesc_e.METHODS, $ptascii("m")) = (pmethoddesc_fresh)',
 'S_fresh = S[.OBJECTS = $object_set(S.OBJECTS, n_fcc, CONSTANTCLOSURE pconstantclosure.SITE '
 '(METHODCLOSURE pmethoddesc_fresh.FUNCTION.ORIGIN pconstantclosure.SITE porigin_e eps))]',
 '~$dynamic_new_record_scope(S_fresh, pdynamicnew)']
CASES['failed-first-post-fixup-static-new-published-called-class'] = {
    'source': SOURCES['failed-first-post-fixup-static-new'],
    'stage': FAILED_STATIC_NEW_STAGE,
    'checks': FAILED_STATIC_NEW,
}

FAILED_OWN_SELF_NEW_STAGE = ('S.TODO = (EVAL (NExprNew (NName (BYTES text_self) metadata_name) (SEQUENCE phpType7*) metadata)) '
 ':: ptask_tail* -- if $ptlc($base64(text_self)) = $ptascii("self") -- if S.ORIGIN = '
 '(porigin_site) -- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_fcc '
 '-- if pcallcontext.LEXICAL_CLASS = (porigin_c) -- if $class_at(S.CLASSES, porigin_c) = '
 '(pclassdesc_c) -- if pclassdesc_c.NAME = $ptascii("C") -- if pcallcontext.CALLED_CLASS = '
 '(porigin_e) -- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) -- if pclassdesc_e.NAME = '
 '$ptascii("E")')
FAILED_OWN_SELF_NEW = ['$ordinary_keyword_new_site(S, porigin_site)',
 '$method_source_task(S, NExprNew (NName (BYTES text_self) metadata_name) (SEQUENCE phpType7*) '
 'metadata)',
 '$call_current_valid(S)',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
 '$trait_fcc_failed_header(S, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, '
 'pmethoddesc_unfixed))',
 'pmethoddesc_unfixed.OWNER = porigin_c /\\ pmethoddesc_unfixed.VISIBILITY = PROPERTY_PRIVATE',
 'pmethoddesc_unfixed.FUNCTION.ORIGIN = PORIGIN n_own pcpath_own',
 '$trait_fcc_failed_data_at(S, pconstantclosure_first, |S.DECLARATIONS|) = ((NORMAL, porigin_c, '
 'pmethoddesc_copy, pmethoddesc_unfixed))',
 'pmethoddesc_copy = pmethoddesc_unfixed',
 '$trait_fcc_failed_fixup_at(S, pconstantclosure_first, |S.DECLARATIONS|) = eps',
 '$trait_fcc_failed_data_at(S, pconstantclosure_first, pconstantclosure_first.PREFIX) = eps',
 '$class_named(S.CLASSNAMES, $ptascii("c")) = eps /\\ $class_named(S.CLASSNAMES, $ptascii("e")) = '
 '(porigin_e)',
 '$closure_scope_at(S.CLOSURESCOPES, n_fcc) = (pclosurescope)',
 'pclosurescope.LEXICAL = porigin_c /\\ pclosurescope.CALLED = porigin_e',
 '$trait_fcc_retained_new_scope(S, porigin_site) = ((pclassdesc_c, pconstantclosure_first))',
 '$trait_fcc_failed_abstract(S, pclassdesc_c, pconstantclosure_first)',
 '$constant_callable_record_valid(S, pconstantclosure_first) /\\ ~(HOBJECT '
 'pconstantclosure_first.OBJECT <- S.ALLOCATIONS) /\\ $closure_scope_at(S.CLOSURESCOPES, '
 'pconstantclosure_first.OBJECT) = eps',
 'porigin_site = PORIGIN n_unit pcpath_site',
 '$code_at(S.CODE, n_unit) = (pcode)',
 '$code_expression(pcode.EXPRESSIONS, pcpath_site) = ((z, false))',
 'PhpStep: S ~> S_rejected',
 'S_rejected.COMPLETION = THROWN "Error" $ptascii("Cannot instantiate abstract class C") z',
 'S_rejected.TODO = ptask_tail* /\\ S_rejected.CURRENT = S.CURRENT',
 'S_rejected.OBJECTS = S.OBJECTS /\\ S_rejected.ALLOCATIONS = S.ALLOCATIONS /\\ S_rejected.EVENTS '
 '= S.EVENTS',
 '$class_constant_state_valid(S_rejected)',
 '$call_descriptors_valid(S_rejected)',
 '$declaration_history_valid(S_rejected)',
 '$heap_valid($heap_graph(S_rejected))',
 '$trait_fcc_retained_new_scope(S, pconstantclosure_first.SITE) = eps',
 '$trait_fcc_retained_new_scope(S[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET '
 'pconstantclosure_first.OBJECT][.INSTANCE = (pconstantclosure_first.OBJECT)])], porigin_site) = '
 'eps',
 '~$trait_fcc_failed_abstract(S, pclassdesc_c, pconstantclosure_first[.PREFIX = '
 '$(pconstantclosure_first.PREFIX + 1)])',
 '$class_named(S.CLASSNAMES, $ptascii("u")) = (porigin_u)',
 '$class_at(S.CLASSES, porigin_u) = (pclassdesc_u)',
 '$ppproperty_desc_at(pclassdesc_u.PROPERTIES, $ptascii("x")) = (ppropertydesc_u)',
 'S_before_fixup = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_u[.PROPERTIES = '
 '[ppropertydesc_u[.DEFAULT = PROP_LITERAL (PINT 0)]]])]',
 '$trait_fcc_failed_data_at(S_before_fixup, pconstantclosure_first, |S.DECLARATIONS|) = '
 '((pcompletion_before, porigin_c, pmethoddesc_copy, pmethoddesc_unfixed))',
 '$iterator_notice_link_fatal(pcompletion_before)',
 '~$trait_fcc_failed_abstract(S_before_fixup, pclassdesc_c, pconstantclosure_first)',
 'S_unknown_phase = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_u[.PROPERTIES = '
 '[ppropertydesc_u[.DEFAULT = PROP_DEFERRED porigin_u]]])]',
 '$trait_fcc_failed_data_at(S_unknown_phase, pconstantclosure_first, |S.DECLARATIONS|) = '
 '((pcompletion_unknown, porigin_c, pmethoddesc_copy, pmethoddesc_unfixed))',
 'pcompletion_unknown =/= NORMAL /\\ $trait_fcc_failed_data_phase(pcompletion_unknown, porigin_c, '
 'pmethoddesc_copy, pmethoddesc_unfixed) = eps',
 '~$trait_fcc_failed_abstract(S_unknown_phase, pclassdesc_c, pconstantclosure_first)',
 '$trait_fcc_retained_new(S_unknown_phase, pclassdesc_c, pconstantclosure_first, z) = '
 'S_unknown_phase[.COMPLETION = UNSUPPORTED "retained failed class construction"]',
 '$trait_fcc_retained_new_scope(S[.CURRENT = (pcallcontext[.LEXICAL_CLASS = (porigin_u)])], '
 'porigin_site) = eps']
CASES['failed-first-post-fixup-own-private-self-new-before-arguments'] = {
    'source': SOURCES['failed-first-post-fixup-abstract-own-private-self-new'],
    'stage': FAILED_OWN_SELF_NEW_STAGE,
    'checks': FAILED_OWN_SELF_NEW,
}

FAILED_EXPLICIT_SELF_NEW_STAGE = ('S.TODO = (EVAL (NExprNew (NName (BYTES text_self) metadata_name) (SEQUENCE phpType7*) metadata)) '
 ':: ptask_tail* -- if $ptlc($base64(text_self)) = $ptascii("self") -- if S.ORIGIN = '
 '(porigin_site) -- if S.CURRENT = (pcallcontext) -- if pcallcontext.TARGET = CLOSURE_TARGET n_fcc '
 '-- if pcallcontext.LEXICAL_CLASS = (porigin_c) -- if $class_at(S.CLASSES, porigin_c) = '
 '(pclassdesc_c) -- if pclassdesc_c.NAME = $ptascii("C") -- if pcallcontext.CALLED_CLASS = '
 '(porigin_e) -- if $class_at(S.CLASSES, porigin_e) = (pclassdesc_e) -- if pclassdesc_e.NAME = '
 '$ptascii("E")')
FAILED_EXPLICIT_SELF_NEW = ['$ordinary_keyword_new_site(S, porigin_site)',
 '$method_source_task(S, NExprNew (NName (BYTES text_self) metadata_name) (SEQUENCE phpType7*) '
 'metadata)',
 '$call_current_valid(S)',
 '$constant_callable_record(S.CONSTANTCLOSURES, n_fcc) = (pconstantclosure)',
 '$trait_fcc_failed_header(S, pconstantclosure.SITE) = ((pconstantclosure_first, porigin_c, '
 'pmethoddesc_unfixed))',
 'pmethoddesc_unfixed.OWNER = porigin_c /\\ pmethoddesc_unfixed.VISIBILITY = PROPERTY_PRIVATE',
 'pclassdesc_c.ABSTRACT /\\ $class_named(S.CLASSNAMES, $ptascii("c")) = eps /\\ '
 '$class_named(S.CLASSNAMES, $ptascii("e")) = (porigin_e)',
 '$origin_node(S.SOURCES, porigin_c) = (NStmtClass phpType14 (INTEGER 16) phpType3 phpType44 '
 'phpType42 phpType23 metadata_class)',
 '$trait_fcc_failed_data_at(S, pconstantclosure_first, |S.DECLARATIONS|) = ((pcompletion_data, '
 'porigin_c, pmethoddesc_copy, pmethoddesc_unfixed))',
 '$iterator_notice_link_fatal(pcompletion_data)',
 'pmethoddesc_copy = pmethoddesc_unfixed',
 '$trait_fcc_failed_fixup_at(S, pconstantclosure_first, |S.DECLARATIONS|) = eps',
 '$closure_scope_at(S.CLOSURESCOPES, n_fcc) = (pclosurescope)',
 'pclosurescope.LEXICAL = porigin_c /\\ pclosurescope.CALLED = porigin_e',
 '$trait_fcc_retained_new_scope(S, porigin_site) = ((pclassdesc_c, pconstantclosure_first))',
 '$trait_fcc_failed_abstract(S, pclassdesc_c, pconstantclosure_first)',
 '$constant_callable_record_valid(S, pconstantclosure_first) /\\ ~(HOBJECT '
 'pconstantclosure_first.OBJECT <- S.ALLOCATIONS) /\\ $closure_scope_at(S.CLOSURESCOPES, '
 'pconstantclosure_first.OBJECT) = eps',
 'porigin_site = PORIGIN n_unit pcpath_site',
 '$code_at(S.CODE, n_unit) = (pcode)',
 '$code_expression(pcode.EXPRESSIONS, pcpath_site) = ((z, false))',
 'PhpStep: S ~> S_rejected',
 'S_rejected.COMPLETION = THROWN "Error" $ptascii("Cannot instantiate abstract class C") z',
 'S_rejected.TODO = ptask_tail* /\\ S_rejected.CURRENT = S.CURRENT',
 'S_rejected.OBJECTS = S.OBJECTS /\\ S_rejected.ALLOCATIONS = S.ALLOCATIONS /\\ S_rejected.EVENTS '
 '= S.EVENTS',
 '$class_constant_state_valid(S_rejected)',
 '$call_descriptors_valid(S_rejected)',
 '$declaration_history_valid(S_rejected)',
 '$heap_valid($heap_graph(S_rejected))',
 '$trait_fcc_retained_new_scope(S, pconstantclosure_first.SITE) = eps',
 '$trait_fcc_retained_new_scope(S[.CURRENT = (pcallcontext[.TARGET = CLOSURE_TARGET '
 'pconstantclosure_first.OBJECT][.INSTANCE = (pconstantclosure_first.OBJECT)])], porigin_site) = '
 'eps',
 '~$trait_fcc_failed_abstract(S, pclassdesc_c, pconstantclosure_first[.PREFIX = '
 '$(pconstantclosure_first.PREFIX + 1)])',
 'S_no_flag = S[.CLASSES = $trait_class_set(S.CLASSES, pclassdesc_c[.ABSTRACT = false])]',
 '~$trait_fcc_failed_abstract(S_no_flag, pclassdesc_c[.ABSTRACT = false], pconstantclosure_first)',
 '$trait_fcc_retained_new(S_no_flag, pclassdesc_c[.ABSTRACT = false], pconstantclosure_first, z) = '
 'S_no_flag[.COMPLETION = UNSUPPORTED "retained failed class construction"]',
 'porigin_c = PORIGIN n_class pcpath_class',
 '$source_unit(S.SOURCES, n_class) = (pcunit_class)',
 'S_no_source_flag = S[.SOURCES = [pcunit_class[.OCCURRENCES = [PCOCCURRENCE pcpath_class '
 '(NStmtClass phpType14 (INTEGER 0) phpType3 phpType44 phpType42 phpType23 metadata_class)] ++ '
 'pcunit_class.OCCURRENCES]] ++ S.SOURCES]',
 '~$trait_fcc_failed_abstract(S_no_source_flag, pclassdesc_c, pconstantclosure_first)',
 '$trait_fcc_retained_new(S_no_source_flag, pclassdesc_c, pconstantclosure_first, z) = '
 'S_no_source_flag[.COMPLETION = UNSUPPORTED "retained failed class construction"]']
CASES['failed-first-explicit-abstract-own-private-self-new-before-arguments'] = {
    'source': SOURCES['failed-first-explicit-abstract-pre-data-self-new'],
    'stage': FAILED_EXPLICIT_SELF_NEW_STAGE,
    'checks': FAILED_EXPLICIT_SELF_NEW,
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    selected = {name: case for name, case in CASES.items() if args.match in name}
    assert selected
    protocol.run(selected, (Path(__file__).resolve(), CATALOGUE, *HELPERS))
