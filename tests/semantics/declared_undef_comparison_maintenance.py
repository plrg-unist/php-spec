#!/usr/bin/env python3
"""Classify only the affected old declared-row image and DIRECT expiry."""
from pathlib import Path
import argparse
import json

from nonpublic_numeric_comparison_review_cases import CASES
from nonpublic_numeric_comparison_review_protocol import PREFIX, front, layout
from undefined_spaceship_state import ROOT, run


def checks(program,path,name):
    assert name == 'private-shadow-physical-key'
    return front(program,path,name) + layout(True) + [
        'S_unset = S[.OBJECTPROPS = $objectprops_set(S.OBJECTPROPS,n_right,[ppropertyslot_rightfirst[.STATE = PROP_UNSET],ppropertyslot_rightsecond])]',
        '$aggregate_decl_image(S_unset,n_right,ptbytes_keys*)',
        '$number_compare_valid(S_unset,pnumbercompare)',
        '$number_compare_other(S_unset,pnumbercompare) = eps',
        'S_expired = S_unset[.TODO = (NUMBER_COMPARE_RESULT pnumbercompare) :: pnumbercompare.SOURCE.TAIL]',
        '$call_task_valid(S_expired,NUMBER_COMPARE_RESULT pnumbercompare)',
        'PhpStep: S_expired ~> S_refused',
        'S_refused = S_expired[.TODO = eps][.COMPLETION = UNSUPPORTED "numeric comparison expired operand"]',
    ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    assert not args.output.exists(),args.output
    result = run({'private-shadow-physical-key':CASES['private-shadow-physical-key']},
        checks,PREFIX,args.output,extra_inputs=[
            Path(__file__),ROOT/'tests/semantics/nonpublic_numeric_comparison_review_cases.py',
            ROOT/'tests/semantics/nonpublic_numeric_comparison_review_protocol.py'])
    result['historical_renewal_credit'] = 0
    result['scope'] = 'One source-reached prefix and derived refusal; no native/source agreement or old campaign replay.'
    (args.output/'report.json').write_text(json.dumps(result,indent=2)+'\n')
