#!/usr/bin/env python3
"""A reached owning send refuses a nonnumeric named key before recording it."""
from pathlib import Path
from types import SimpleNamespace

import config_generator_owning_value_review_cases as cases
import config_generator_owning_value_review_state as peer
import list_missing_warning_protocol as shared
from array_generator_unpack_state_review import initial, owners, public, seek


NAME = 'config-generator-owning-prefix-replaced-cache-throw'
SOURCES = SimpleNamespace(CASES={NAME: cases.CASES[NAME]}, __file__=cases.__file__)


def conditions(name, program, path, stdout):
    assert name == NAME
    checks = initial(program, path) + seek('S_initial', 1700, 'S_option') + [
        'S_option.TODO = (CONFIG_GENERATOR pconfiggenerator "ready") :: ptask*',
        'pconfiggenerator.ITEMS = eps',
        'pconfiggenerator.OBJECT = n_generator',
        'pconfiggenerator.INPUT = VARIABLE ($ptascii("gen")) z_input',
        'S_option.OBJECTS[n_generator] = GENERATOR pgenerator',
        'pgenerator.PHASE = GENERATOR_PAUSED',
        'pgenerator.VALUE = (POBJECT n_payload)',
        'pgenerator.KEY = (PINT 0)',
        '$config_generator_owning_value_source(S_option,pconfiggenerator)',
        '$config_generator_value(S_option,pconfiggenerator) = (POBJECT n_payload)',
        owners('S_option', 'HOBJECT n_generator', 2),
        'S_numeric = $generator_set(S_option,n_generator,pgenerator[.KEY = (PSTRING ($ptascii("0")))])',
        '$config_generator_key(S_numeric,PSTRING ($ptascii("0"))) = (KINT 0)',
        '$config_generator_value(S_numeric,pconfiggenerator) = (POBJECT n_payload)',
        '$config_generator_send_allowed(S_numeric,pconfiggenerator)',
        'S_named = $generator_set(S_option,n_generator,pgenerator[.KEY = (PSTRING ($ptascii("named77")))])',
        '$config_generator_valid(S_named,pconfiggenerator,"ready")',
        '$config_generator_key_input(pconfiggenerator,PSTRING ($ptascii("named77")))',
        '$config_generator_key(S_named,PSTRING ($ptascii("named77"))) = (KSTRING ($ptascii("named77")))',
        '$config_generator_value(S_named,pconfiggenerator) = eps',
        '~$config_generator_send_allowed(S_named,pconfiggenerator)',
        '~$config_generator_items(S_named,pconfiggenerator,[ENTRY (KSTRING ($ptascii("named77"))) (DIRECT (POBJECT n_payload))])',
        'PhpStep: S_named ~> S_refusal',
        'S_refusal.COMPLETION = UNSUPPORTED "CONFIG Generator unpack send outside scalar/key domain"',
    ] + public('S_option') + public('S_numeric') + public('S_named')
    return checks


if __name__ == '__main__':
    raise SystemExit(0 if shared.run(SOURCES, conditions, peer.HELPERS, model_timeout=180,
        extra_inputs=(Path(__file__), Path(peer.__file__),
                      Path(__file__).with_name('array_generator_unpack_state_review.py'))) else 1)
