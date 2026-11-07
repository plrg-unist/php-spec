"""Independent rejected static binding preserves the old source after CV removal."""
import hashlib
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_suffix('.json')
CASES = {row['id']: row['source'].encode() for row in json.loads(CATALOGUE.read_bytes())}

if __name__ == '__main__':
    for row in json.loads(CATALOGUE.read_bytes()):
        assert hashlib.sha256(CASES[row['id']]).hexdigest() == row['source_sha256']
    print(len(CASES), 'exact original')
