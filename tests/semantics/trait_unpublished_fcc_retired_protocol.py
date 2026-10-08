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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    selected = {name: case for name, case in CASES.items() if args.match in name}
    assert selected
    protocol.run(selected, (Path(__file__).resolve(), CATALOGUE, *HELPERS))
