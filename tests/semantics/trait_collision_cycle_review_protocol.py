#!/usr/bin/env python3
"""A reached copied lookup cycle uses full declarations and releases scratch owners."""
import json
from pathlib import Path

import closure_call_protocol as protocol
import trait_collision_error_review_protocol as errors

HERE = Path(__file__).resolve().parent
CATALOGUE = HERE / 'trait_data_collision_cycle_review_cases.json'
ROW = next(row for row in json.loads(CATALOGUE.read_text())['cases']
           if row['id'] == 'recursive-imported-Y-Z-Z-lookup-uses-full-visited-tail')

CASES = {
    'two-hop-copied-cycle-validates-full-visited-tail-and-releases-error-owners': {
        'source': ROW['source'],
        'stage': errors.STAGE,
        'checks': errors.BINDINGS + [
            'S.CURRENT = eps',
            'S.FRAMES = eps',
            'ppropertydesc_t.DEFAULT = PROP_DEFERRED porigin_root',
            'S_constants = $trait_data_constants(S, pclassdesc_c, [pclassdesc_t], eps)',
            'S_constants.COMPLETION = NORMAL',
            'S_constants.CLASSNAMES = S.CLASSNAMES',
            'S_constants.DECLARATIONS = S.DECLARATIONS',
            '$class_at(S_constants.CLASSES, porigin_c) = (pclassdesc_constants)',
            '$class_constant_desc(pclassdesc_constants.CONSTANTS, $ptascii("Y")) = (pclassconstantdesc_y)',
            '$class_constant_desc(pclassdesc_constants.CONSTANTS, $ptascii("Z")) = (pclassconstantdesc_z)',
            'pclassconstantdesc_y.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_raw_y',
            'pclassconstantdesc_z.ORIGIN = TRAIT_MEMBER_ORIGIN porigin_c porigin_raw_z',
            'pclassconstantdesc_y.ORIGIN =/= pclassconstantdesc_z.ORIGIN',
            '~pclassconstantdesc_y.FOLDED',
            '~pclassconstantdesc_z.FOLDED',
            '$trait_cache_requested_member(S_constants, porigin_c, porigin_root) = (pclassconstantdesc_y)',
            '$trait_cache_requested_member(S_constants, porigin_c, pclassconstantdesc_y.INITIALIZER) = (pclassconstantdesc_z)',
            'porigin_lookups* = [porigin_root, pclassconstantdesc_y.INITIALIZER]',
            '$trait_cache_lookups(S_constants, porigin_c, porigin_root, porigin_lookups*, eps) = (pclassconstantdesc_z)',
            '$trait_collision_visited(S_constants, porigin_c, porigin_root, porigin_lookups*, pclassconstantdesc_z.ORIGIN)',
            '~$trait_collision_visited(S_constants, porigin_c, porigin_root, eps, pclassconstantdesc_z.ORIGIN)',
            '~$trait_collision_visited(S_constants, porigin_c, porigin_root, [porigin_root], pclassconstantdesc_z.ORIGIN)',
            '~$trait_collision_visited(S_constants, porigin_c, porigin_root, porigin_lookups*, porigin_raw_z)',
            '~$trait_collision_visited(S_constants, porigin_t, porigin_root, porigin_lookups*, pclassconstantdesc_z.ORIGIN)',
            '~$trait_collision_visited(S_constants[.SOURCES = eps], porigin_c, porigin_root, porigin_lookups*, pclassconstantdesc_z.ORIGIN)',
            '~$trait_collision_visited(S_constants, porigin_c, pclassconstantdesc_y.INITIALIZER, porigin_lookups*, pclassconstantdesc_z.ORIGIN)',
            '~$trait_collision_visited(S_constants, porigin_c, porigin_root, [porigin_root, porigin_root], pclassconstantdesc_z.ORIGIN)',
            '$trait_cache_lookups(S_constants, porigin_c, porigin_root, porigin_lookups* ++ [pclassconstantdesc_z.INITIALIZER], eps) = eps',
            '$trait_member_fold(S_constants, pclassdesc_constants, porigin_root) = (F_error)',
            'F_error.EXTERNAL = (S_constants)',
            'F_error.RECORD = (pfrecorder)',
            'pfrecorder.CLASS = porigin_c',
            'pfrecorder.ROOT = porigin_root',
            'porigin_root = PORIGIN n_source pcpath_root',
            '$trait_recording(F_error, pcpath_root)',
            '~$trait_recording(F_error[.EXTERNAL = eps], pcpath_root)',
            '~$trait_recording(F_error[.RECORD = (pfrecorder[.CLASS = porigin_t])], pcpath_root)',
            'F_error.VALUE = eps',
            'F_error.RECORDED = eps',
            '$trait_fold_error(F_error) = (ptraitdataerror)',
            'ptraitdataerror.KIND = "Error"',
            'ptraitdataerror.MESSAGE = $ptascii("Cannot declare self-referencing constant self::Z")',
            'ptraitdataerror.LINE = 3',
            'ptraitdataerror.TRACE = [ptraceframe_expression]',
            'ptraceframe_expression.FUNCTION = $ptascii("[constant expression]")',
            'ptraceframe_expression.LINE = 5',
            'F_error.MEMORY.CLASSCONSTANTCACHE = S.CLASSCONSTANTCACHE',
            'F_error.MEMORY.CLASSCONSTANTHISTORY = S.CLASSCONSTANTHISTORY',
        ] + errors.TERMINAL + [
            'pthrowable_error.KIND = "Error"',
            '$(|S_failed.EVENTS| = |S.EVENTS| + 2)',
            'S_failed.EVENTS[0:|S.EVENTS|] = S.EVENTS',
            'S_failed.EVENTS[|S.EVENTS|:2] = [DIAGNOSTIC_SOURCE n_source "Warning" ptbytes_error 3, STDERR ptbytes_fatal_rendered]',
        ],
    },
}

if __name__ == '__main__':
    protocol.run(CASES, (Path(__file__).resolve(), CATALOGUE, Path(errors.__file__).resolve()))
