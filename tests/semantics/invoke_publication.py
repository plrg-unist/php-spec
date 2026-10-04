#!/usr/bin/env python3
"""Original-source __invoke publication, visibility and consumer checks."""
import argparse
from pathlib import Path

import user_string

CATALOGUE = Path(__file__).with_name('invoke_publication_cases.json')


def run(match=''):
    user_string.CASES = CATALOGUE
    return user_string.run(match)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--match', default='')
    args = parser.parse_args()
    raise SystemExit(0 if run(args.match) else 1)
