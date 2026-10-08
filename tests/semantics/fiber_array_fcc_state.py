#!/usr/bin/env python3
"""A static array capture retains selection after its input and pair retire."""
import argparse
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_array_fcc_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'peer-fiber-array-fcc-static-input-retires-before-suspend')


def changed_witness(name, expression):
    return [
        f'pfiberarray_{name} = {expression}',
        f'pfibercapture_{name} = pfibercapture[.ARRAY = (pfiberarray_{name})]',
        f'S_{name} = S[.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture_{name}]',
        f'$heap_graph(S_{name}) = H',
        f'~$fiber_capture_source_valid(S_{name}, pfibercapture_{name})',
        f'~$fiber_capture_live(S_{name}, n_capture)',
        f'~$config_invoke_valid(S_{name}, pconfigcall)',
        f'~$call_descriptors_valid(S_{name})',
    ]


CASES = {
    'array-fcc-static-witness-survives-retired-reference-input': {
        'source': SOURCE,
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: '
                  '(FIBER_CAPTURE_RELEASE n_capture porigin) :: ptask_tail* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_SUSPEND '
                  '-- if pconfigcall.SELECTION = (n_capture)'),
        'checks': [
            'S.ACTIVEFIBER = (n_runner)', 'S.FIBERCALLERS = [pfibercaller]',
            'pfibercaller.OBJECT = n_runner', 'pfibercaller.PREVIOUS = eps',
            'pfibercaller.API.KIND = eps', 'porigin = pconfigcall.SITE',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.FACTORY = eps', 'pfibercapture.ARRAY = (pfiberarray)',
            'pfibercapture.SITE = pfiberarray.SITE',
            'pfibercapture.KIND = INTRINSIC_FIBER_SUSPEND',
            'pfibercapture.NAME = $ptascii("SuSpEnD")',
            'pfibercapture.INPUT = (n_input)',
            'pfiberarray.INPUT = (n_input)', 'pfiberarray.NAME = pfibercapture.NAME',
            'pfiberarray.KIND = pfibercapture.KIND', 'n_callback = pfiberarray.ARRAY',
            'pfiberarray.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_input)), '
            'ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("SuSpEnD"))))]',
            '$entry_lookup(S.ARRAYS[n_callback].ITEMS, KINT 0) = (ALIAS n_receiver_cell)',
            '$entry_lookup(S.ARRAYS[n_callback].ITEMS, KINT 1) = (ALIAS n_method_cell)',
            '$entry_value(S, ALIAS n_receiver_cell) = PNULL',
            '$entry_value(S, ALIAS n_method_cell) = PSTRING ($ptascii("getCurrent"))',
            '~((HARRAY n_callback) <- S.ALLOCATIONS)',
            '~((HOBJECT n_input) <- S.ALLOCATIONS)', '$fiber_at(S, n_input) = eps',
            'n_runner =/= n_input', 'n_input < n_capture',
            'pconfigcall.OWNER = (n_capture)', 'pconfigcall.INDEX = 1',
            'pconfigcall.NAMED', 'pconfigcall.PACKS = eps',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (PSTRING ($ptascii("V"))))]',
            '$fiber_array_capture_source_valid(S, pfiberarray)',
            '~$fiber_array_source_valid(S, pfiberarray)',
            '$fiber_capture_source_valid(S, pfibercapture)',
            '$fiber_capture_live(S, n_capture)', '$fiber_capture_core_live(S, n_capture)',
            '$fiber_capture_config_selected(S, pconfigcall)',
            '$fiber_capture_release_valid(S, n_capture, porigin)',
            '$config_invoke_valid(S, pconfigcall)', 'H = $heap_graph(S)',
            '$heap_owners(H, HARRAY n_callback) = 0',
            '$heap_owners(H, HOBJECT n_input) = 0',
            '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_runner) = 2',
            '$node_children(S, HOBJECT n_capture) = eps',
            '$config_nodes(pconfigcall) = eps',
            '$task_nodes(FIBER_CAPTURE_RELEASE n_capture porigin) = [HOBJECT n_capture]',
            *review.VALID,
            *changed_witness('init', 'pfiberarray[.INIT = $(pfiberarray.INIT + 1)]'),
            *changed_witness('line', 'pfiberarray[.LINE = $(pfiberarray.LINE + 1)]'),
            *changed_witness('input', 'pfiberarray[.INPUT = (n_runner)]'),
            *changed_witness('name', 'pfiberarray[.NAME = $ptascii("getCurrent")]'),
            'n_beyond = |S.ARRAYS|',
            *changed_witness('arena', 'pfiberarray[.ARRAY = n_beyond]'),
            'pfibercapture_missing = pfibercapture[.ARRAY = eps]',
            'S_missing = S[.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture_missing]',
            '$heap_graph(S_missing) = H',
            '~$fiber_capture_source_valid(S_missing, pfibercapture_missing)',
            '~$fiber_capture_live(S_missing, n_capture)',
            '~$config_invoke_valid(S_missing, pconfigcall)',
            '~$call_descriptors_valid(S_missing)',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("V"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), '
            'OUTPUT $ptascii("|"), OUTPUT $ptascii("R"), OUTPUT $ptascii("|"), '
            'OUTPUT $ptascii("23")]',
        ],
    },
}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case', action='append')
    args = parser.parse_args()
    assert not args.case or set(args.case) <= CASES.keys()
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = all(review.run([name]) for name in args.case or list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Array FCC catalog changed during run'
    raise SystemExit(0 if passed else 1)
