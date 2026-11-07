"""Ordinary CLI nested DIRECT-array snapshot and COW original."""
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_suffix('.json')
CASES = {row['id']: row['source'].encode() for row in json.loads(CATALOGUE.read_bytes())}

if __name__ == '__main__':
    import fiber_static_api_sources as source
    source.CASES = CATALOGUE
    source.PREFIX = 'nested-array-reference-notice-review-'
    source.IMPLEMENTATION = Path(__file__)
    source.MODEL_SECONDS = 180
    source.PROCESS_SECONDS = 195
    source.__doc__ = __doc__
    raise SystemExit(0 if source.main() else 1)
