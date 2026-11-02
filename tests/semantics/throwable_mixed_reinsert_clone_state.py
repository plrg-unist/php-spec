#!/usr/bin/env python3
"""Check the reached reinserted-key clone table and guarded mirror selection."""
import argparse
import base64
import json
from pathlib import Path

from throwable_empty_clone_protocol import PREFIX
from throwable_mixed_reinsert_clone_cases import CASES, EXPECTED
from undefined_spaceship_state import ROOT, run


def checks(program, path, name):
    assert name == 'mixed-reinsert-view-cow'
    encoded = json.dumps(base64.b64encode(str(path).encode()).decode())
    return [
        'S_initial = $php_run(' + program + ',0,' + encoded + ')',
        'S_initial.COMPLETION = BUDGET',
        'S = $tec_seek_output(S_initial[.COMPLETION = NORMAL],15000,$ptascii("B|2:2:7|"))',
        '$tbp_output(S.EVENTS) = $ptascii("B|2:2:7|")',
        'S.COMPLETION = NORMAL',
        '$lookup(S.ENV,$ptascii("left")) = (n_left_cv)',
        'S.STORE[n_left_cv] = DEFINED (POBJECT n_left)',
        '$objectprops_record_at(S.OBJECTPROPS,n_left) = (pobjectprops_left)',
        'pobjectprops_left.SLOTS = [ppropertyslot_fixed,ppropertyslot_old,ppropertyslot_live]',
        'ppropertyslot_fixed.DECL =/= eps',
        'ppropertyslot_old.DECL = eps',
        'ppropertyslot_old.NAME = $ptascii("live")',
        'ppropertyslot_old.STATE = PROP_UNSET',
        'ppropertyslot_live.DECL = eps',
        'ppropertyslot_live.NAME = $ptascii("live")',
        'ppropertyslot_live.STATE = PROP_VALUE (DIRECT (PINT 2))',
        '$object_table_at(S.OBJECTTABLES,n_left) = (n_table_left)',
        '$entry_lookup(S.ARRAYS[n_table_left].ITEMS,KSTRING $ptascii("live")) = (DIRECT (PINT 2))',
        '$object_tables_valid(S)',
        '$object_table_ordinary(S,n_left)',
        '$clone_mixed_ready(S,n_left)',
        '$property_slot_at([ppropertyslot_old,ppropertyslot_live],$ptascii("live")) = (ppropertyslot_live)',
        '$clone_mixed_mirrors([ppropertyslot_old,ppropertyslot_live],[ENTRY (KSTRING $ptascii("live")) (DIRECT (PINT 2))]) = ([ppropertyslot_live])',
        '$clone_mixed_mirrors([ppropertyslot_old],[ENTRY (KSTRING $ptascii("live")) (DIRECT (PINT 2))]) = eps',
        '$clone_mixed_mirrors([ppropertyslot_old],eps) = ([ppropertyslot_old])',
        'n_copy = |S.OBJECTS|',
        'S_copy = $clone_plain(S,n_left)',
        'S_copy.COMPLETION = NORMAL',
        '$objectprops_record_at(S_copy.OBJECTPROPS,n_copy) = (pobjectprops_copy)',
        'pobjectprops_copy.SLOTS = [ppropertyslot_fixed_copy,ppropertyslot_live_copy]',
        'ppropertyslot_live_copy.NAME = $ptascii("live")',
        'ppropertyslot_live_copy.STATE = PROP_VALUE (DIRECT (PINT 2))',
        '$object_table_at(S_copy.OBJECTTABLES,n_copy) = (n_table_copy)',
        'n_table_copy =/= n_table_left',
        '$entry_lookup(S_copy.ARRAYS[n_table_copy].ITEMS,KSTRING $ptascii("live")) = (DIRECT (PINT 2))',
        '$object_tables_valid(S_copy)',
        'S_done = $drive_steps(S,15000)',
        'S_done.COMPLETION = NORMAL /\\ S_done.TODO = eps',
        '$tbp_output(S_done.EVENTS) = $ptascii(' + json.dumps(EXPECTED[name].decode()) + ')',
    ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    run({'mixed-reinsert-view-cow': CASES['mixed-reinsert-view-cow']}, checks, PREFIX,
        args.output, extra_inputs=[ROOT / 'tests/semantics/throwable_mixed_reinsert_clone_cases.py',
                                   ROOT / 'tests/semantics/throwable_mixed_reinsert_clone_state.py'],
        timeout=180)
