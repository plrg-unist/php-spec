#!/usr/bin/env python3
"""A real retired callable array cannot replace its factory's throw selection."""
import json
from pathlib import Path
import fiber_state_review as review

ROOT = Path(__file__).resolve().parents[2]
CATALOG = Path(__file__).with_name('fiber_from_callable_cases.json')
SOURCE_BYTES = CATALOG.read_bytes()
SOURCE = next(row['source'] for row in json.loads(SOURCE_BYTES)
              if row['id'] == 'author-fiber-from-unpacked-throw-injects-original')

CASES = {
    'factory-throw-keeps-retired-array-selection-and-real-injection': {
        'source': SOURCE,
        'stage': ('S.TODO = (CONFIG_INVOKE pconfigcall) :: '
                  '(FIBER_CAPTURE_RELEASE n_capture porigin) :: ptask_tail* '
                  '-- if pconfigcall.KIND = INTRINSIC_FIBER_THROW '
                  '-- if pconfigcall.SELECTION = (n_capture)'),
        'checks': [
            'S.ACTIVEFIBER = eps', 'S.CURRENT = eps', 'S.FIBERCALLERS = eps',
            'porigin = pconfigcall.SITE',
            'S.OBJECTS[n_capture] = FIBERAPICLOSURE pfibercapture',
            'pfibercapture.KIND = INTRINSIC_FIBER_THROW',
            'pfibercapture.NAME = $ptascii("ThRoW")',
            'pfibercapture.INPUT = (n_receiver)',
            'pconfigcall.OWNER = (n_receiver)',
            'pconfigcall.SENT = [NAMED_SENT (KNOWN (POBJECT n_error))]',
            'pfibercapture.FACTORY = (pfiberfactory)',
            'pconfigcall_factory = pfiberfactory.CALL',
            'pconfigcall_factory.KIND = INTRINSIC_FROM_CALLABLE',
            'pconfigcall_factory.SITE = pfibercapture.SITE',
            'pconfigcall_factory.OWNER = eps',
            'pconfigcall_factory.SENT = [NAMED_SENT (KNOWN (PARRAY n_array))]',
            'pconfigcall_factory.INDEX = 1', 'pconfigcall_factory.NAMED',
            'pconfigcall_factory.PACKS = [pconfigpack]', 'n_pack = pconfigpack.ARRAY',
            '~((HARRAY n_pack) <- S.ALLOCATIONS)',
            'pconfigpack.ITEMS = [ENTRY (KSTRING ($ptascii("callback"))) (DIRECT (PARRAY n_array))]',
            '$config_pack_source_valid(S, pconfigcall_factory, pconfigpack)',
            'pfiberfactory.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("ThRoW"))))]',
            '~((HARRAY n_array) <- S.ALLOCATIONS)',
            '$entry_lookup(S.ARRAYS[n_array].ITEMS, KINT 1) = (DIRECT (PSTRING ($ptascii("resume"))))',
            '$fiber_factory_members(S, PARRAY n_array, pfiberfactory.ITEMS) = ((POBJECT n_receiver, $ptascii("ThRoW")))',
            '$fiber_factory_selection(S, PARRAY n_array, pfiberfactory.ITEMS) = ((INTRINSIC_FIBER_THROW, $ptascii("ThRoW"), pfibercapture.INPUT))',
            '$config_selected_valid(S, pconfigcall_factory)',
            '$config_sent_shape(S, pconfigcall_factory)',
            '~$config_slots_valid(S, pconfigcall_factory.SENT)',
            '$fiber_capture_source_valid(S, pfibercapture)', '$fiber_capture_live(S, n_capture)',
            '$config_invoke_valid(S, pconfigcall)',
            '$fiber_capture_release_valid(S, n_capture, porigin)',
            '$fiber_at(S, n_receiver) = (pfiber_receiver)',
            'pfiber_receiver.STATUS = FIBER_SUSPENDED',
            '$node_children(S, HOBJECT n_capture) = [HOBJECT n_receiver]',
            '$config_nodes(pconfigcall) = [HOBJECT n_error]',
            '$task_nodes(FIBER_CAPTURE_RELEASE n_capture porigin) = [HOBJECT n_capture]',
            'H = $heap_graph(S)', '$heap_owners(H, HOBJECT n_capture) = 2',
            '$heap_owners(H, HOBJECT n_receiver) = 2', '$heap_owners(H, HOBJECT n_error) = 2',
            *review.VALID,
            'pfibercapture_name = pfibercapture[.NAME = $ptascii("resume")]',
            'S_name = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_name)]',
            '$heap_graph(S_name) = H', '~$fiber_capture_source_valid(S_name, pfibercapture_name)',
            '~$fiber_capture_live(S_name, n_capture)', '~$call_descriptors_valid(S_name)',
            'pfiberfactory_items = pfiberfactory[.ITEMS = [ENTRY (KINT 0) (DIRECT (POBJECT n_receiver)), ENTRY (KINT 1) (DIRECT (PSTRING ($ptascii("resume"))))]]',
            'pfibercapture_items = pfibercapture[.FACTORY = (pfiberfactory_items)]',
            'S_items = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_items)]',
            '$heap_graph(S_items) = H', '~$fiber_capture_source_valid(S_items, pfibercapture_items)',
            '~$call_descriptors_valid(S_items)',
            'pconfigcall_line = pconfigcall_factory[.LINE = $(pconfigcall_factory.LINE + 1)]',
            'pfiberfactory_line = pfiberfactory[.CALL = pconfigcall_line]',
            'pfibercapture_line = pfibercapture[.FACTORY = (pfiberfactory_line)]',
            'S_line = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_line)]',
            '$heap_graph(S_line) = H', '~$fiber_capture_source_valid(S_line, pfibercapture_line)',
            '~$call_descriptors_valid(S_line)',
            'pconfigcall_array = pconfigcall_factory[.SENT = [NAMED_SENT (KNOWN (PARRAY |S.ARRAYS|))]]',
            'pfiberfactory_array = pfiberfactory[.CALL = pconfigcall_array]',
            'pfibercapture_array = pfibercapture[.FACTORY = (pfiberfactory_array)]',
            'S_array = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_array)]',
            '$heap_graph(S_array) = H', '~$fiber_capture_source_valid(S_array, pfibercapture_array)',
            '~$call_descriptors_valid(S_array)',
            'pconfigpack_bad = pconfigpack[.ARRAY = |S.ARRAYS|]',
            'pconfigcall_pack = pconfigcall_factory[.PACKS = [pconfigpack_bad]]',
            'pfiberfactory_pack = pfiberfactory[.CALL = pconfigcall_pack]',
            'pfibercapture_pack = pfibercapture[.FACTORY = (pfiberfactory_pack)]',
            'S_pack = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_pack)]',
            '$heap_graph(S_pack) = H', '~$fiber_capture_source_valid(S_pack, pfibercapture_pack)',
            '~$call_descriptors_valid(S_pack)',
            'pfibercapture_missing = pfibercapture[.FACTORY = eps]',
            'S_missing = S[.OBJECTS = $object_set(S.OBJECTS, n_capture, FIBERAPICLOSURE pfibercapture_missing)]',
            '$heap_graph(S_missing) = H', '~$fiber_capture_source_valid(S_missing, pfibercapture_missing)',
            '~$call_descriptors_valid(S_missing)',
            'pconfigcall_owner = pconfigcall[.OWNER = (n_capture)]',
            'S_owner = S[.TODO = (CONFIG_INVOKE pconfigcall_owner) :: (FIBER_CAPTURE_RELEASE n_capture porigin) :: ptask_tail*]',
            '$heap_graph(S_owner) = H', '~$config_invoke_valid(S_owner, pconfigcall_owner)',
            '~$call_descriptors_valid(S_owner)',
            'S_zero = $drive(S, 0)', 'S_zero.COMPLETION = BUDGET',
            'S_zero[.COMPLETION = NORMAL] = S',
            'S_done = $drive(S, 4000)', *review.DONE,
            'S_done.EVENTS = [OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("injected"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1"), OUTPUT $ptascii("|"), OUTPUT $ptascii("27"), OUTPUT $ptascii("|"), OUTPUT $ptascii("1")]',
        ],
    },
}

if __name__ == '__main__':
    review.ROOT = ROOT
    review.CASES = CASES
    review.__file__ = str(Path(__file__).resolve())
    passed = review.run(list(CASES))
    assert CATALOG.read_bytes() == SOURCE_BYTES, 'Factory source catalog changed during run'
    raise SystemExit(0 if passed else 1)
