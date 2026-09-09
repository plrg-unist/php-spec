#!/usr/bin/env python3
"""Extract positional send flags from configured, preprocessed PHP arginfo.

Source only: does not invoke PHP or evaluate submitted programs. Reuses the
namespace inventory's configured registration and preprocessor input audit.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def derive(producer):
    spec = importlib.util.spec_from_file_location('builtin_names', producer / 'scripts/generate-builtin-functions.py')
    names = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(names)
    _, report = names.derive(producer)
    records = []
    for table in report['tables']:
        raw = producer / report['raw'] / (table['source'].removeprefix('vendor/php-src/').replace('/', '_').removesuffix('.c') + '.stdout')
        source = raw.read_text()
        body = re.search(r'\b' + table['table'] + r'\[\]\s*=\s*\{(.*?)\n\};', source, re.S)[1]
        entries = re.findall(r'\{\s*"([^"]+)"\s*,\s*\w+\s*,\s*(\w+)\s*,', body)
        assert [entry[0] for entry in entries] == table['names']
        for name, arginfo in entries:
            array = re.search(r'\b' + arginfo + r'\[\]\s*=\s*\{(.*?)\n\};', source, re.S)
            assert array is not None, (name, arginfo)
            params = []
            for line in array[1].splitlines()[1:]:
                # Exact ZEND_ARG_* expansion of _ZEND_ARG_INFO_FLAGS at this pin.
                # Reject unknown layouts rather than inferring a by-value flag.
                match = re.fullmatch(r'\s*\{ "([a-zA-Z_][a-zA-Z_0-9]*)", .*', line)
                flags = re.findall(r'\(\(([012])u?\) << 25\) \| \(\(([01])\) \? \(1 << \(25 \+ 2\)\)', line)
                assert match and len(flags) == 1, (name, line)
                mode, variadic = map(int, flags[0])
                params.append({'name': match[1], 'send_mode': mode, 'variadic': bool(variadic)})
            assert not any(param['variadic'] for param in params[:-1]), name
            records.append({'name': name, 'source': table['source'], 'arginfo': arginfo,
                            'arginfo_sha256': hashlib.sha256(array[0].encode()).hexdigest(), 'parameters': params})
    assert len(records) == 780 and len({r['name'] for r in records}) == 780
    groups = {}
    for record in records:
        params = record['parameters']
        refs = tuple(i + 1 for i, p in enumerate(params) if p['send_mode'])
        variadic_ref = bool(params and params[-1]['variadic'] and params[-1]['send_mode'])
        if refs:
            groups.setdefault((refs, variadic_ref), []).append(record['name'])
    lines = [';; Generated from configured PHP 8.5.10 positional arginfo send flags.',
             ';; Argument compilation only; builtin execution remains separate.',
             'dec $pfunction_builtin_ref(ptbytes, nat) : bool',
             'dec $pfunction_builtin_ref_lower(ptbytes, nat) : bool',
             'def $pfunction_builtin_ref(ptbytes, n) = $pfunction_builtin_ref_lower($ptlc(ptbytes), n)']
    for (refs, variadic), group in sorted(groups.items()):
        lines += ['def $pfunction_builtin_ref_lower(ptbytes, n) = (' + ' \\/ '.join('n = ' + str(i) for i in refs) + (' \\/ $(n > ' + str(refs[-1]) + ')' if variadic else '') + ')',
                  '  -- if ptbytes <- [' + ', '.join('([' + ','.join(map(str, name.encode())) + '])' for name in sorted(group)) + ']']
    lines += ['def $pfunction_builtin_ref_lower(ptbytes, n) = false -- otherwise', '']
    report.update({'scope': 'source-derived positional builtin send flags, including prefer-reference and variadic tail; no builtin bodies',
                   'arguments': records,
                   'argument_generator': {'path': str(Path(__file__).resolve()), 'sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}})
    return '\n'.join(lines), report


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--producer', type=Path, default=ROOT)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    output, report = derive(args.producer.resolve())
    target = ROOT / 'spec/semantics/25-builtin-argument-modes.watsup'
    if args.check:
        if target.read_text() != output:
            parser.exit(1, 'builtin argument modes differ from configured sources\n')
    else:
        target.write_text(output)
        (ROOT / 'coverage/semantics/builtin-argument-modes.json').write_text(json.dumps(report, indent=2) + '\n')
    print(len(report['arguments']), 'source-derived positional argument signatures')
