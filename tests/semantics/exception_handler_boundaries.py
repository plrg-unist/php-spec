#!/usr/bin/env python3
"""Current keyword/compound exception callbacks; historical controls stay in the222 ledger."""
from pathlib import Path

import shutdown_review

shutdown_review.CASES = Path(__file__).with_name('callback_api_review_cases.json')


def main():
    return shutdown_review.run('exception-', [], None, False, [])


if __name__ == '__main__':
    raise SystemExit(0 if main() else 1)
