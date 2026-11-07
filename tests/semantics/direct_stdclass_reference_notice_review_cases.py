"""Independent named DIRECT object-leaf COW and retained-CV discriminator."""
import json
from pathlib import Path

CATALOGUE = Path(__file__).with_suffix('.json')
CASES = {row['id']: row['source'].encode() for row in json.loads(CATALOGUE.read_bytes())}
