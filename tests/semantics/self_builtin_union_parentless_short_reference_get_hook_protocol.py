#!/usr/bin/env python3
"""Check scoped-self multi-builtin states, with exact bounded wide-case cuts."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

import self_parentless_short_reference_get_hook_protocol as protocol


def main():
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--cut', choices=('lifecycle', 'budget'))
    args, remaining = parser.parse_known_args()
    sys.argv[1:] = remaining
    if args.cut:
        out = Path(remaining[remaining.index('--output') + 1]).resolve()
        original = protocol.fields

        def fields(fixture, source, case):
            assert case['id'] == 'weak-relative-self-seven'
            full = original(fixture, source, case)
            suffix = ['S_return_zero = $drive_steps(S_return,0)',
                      'S_return_zero = S_return[.COMPLETION = BUDGET]',
                      'S_return_one = $drive_steps(S_return_zero[.COMPLETION = NORMAL],1)',
                      'S_return_one = $drive_steps(S_return,1)',
                      '$drive_steps(S_return_one[.COMPLETION = NORMAL],30000) = S_end',
                      'S_cleanup_zero = $drive_steps(S_before,0)',
                      'S_cleanup_zero = S_before[.COMPLETION = BUDGET]',
                      '$drive_steps(S_cleanup_zero[.COMPLETION = NORMAL],1) = $drive_steps(S_before,1)']
            assert full[-8:] == suffix
            boundary = len(full) - 8
            bindings = [0, 1] + [i for i, check in enumerate(full)
                                  if re.fullmatch(r'S_[A-Za-z0-9_]+ = \$lbr_seek\(.*\)', check)]
            bindings += [i for i, check in enumerate(full)
                         if check == 'S_end = $drive_steps(S_free,30000)']
            assert bindings == sorted(set(bindings))
            cuts = {'lifecycle': list(range(boundary)),
                    'budget': sorted(bindings + list(range(boundary, len(full))))}
            assert set(cuts['lifecycle']) | set(cuts['budget']) == set(range(len(full)))
            assert set(cuts['lifecycle']) & set(cuts['budget']) == set(bindings)
            data = (json.dumps(full, indent=2) + '\n').encode()
            (out / 'full-assertions.json').write_bytes(data)
            manifest = {'cut': args.cut, 'indices': cuts[args.cut], 'all_cuts': cuts,
                        'original_premises': len(full), 'shared_binding_indices': bindings,
                        'physical_premises': sum(map(len, cuts.values())),
                        'full_assertions_sha256': hashlib.sha256(data).hexdigest(),
                        'exact_union_reconstructs_original_indices': True,
                        'full_298_pass_claim': False, 'source_credit': 0}
            (out / 'partition.json').write_text(json.dumps(manifest, indent=2) + '\n')
            return [full[i] for i in cuts[args.cut]]

        protocol.fields = fields
    protocol.main('self_builtin_union_parentless_short_reference_get_hook')
    if args.cut:
        reportpath = out / 'report.json'
        report = json.loads(reportpath.read_text())
        report['scope'] = 'partition-' + args.cut
        report['partition'] = json.loads((out / 'partition.json').read_text())
        reportpath.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
