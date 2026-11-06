#!/usr/bin/env python3
"""Default null-C fatal from a fresh Exception in a direct __toString body."""
from pathlib import Path
import function_scope as scope

CASES = {
    'fresh-exception': b"<?php echo 'P';class T{function __toString(){throw new Exception('E');}}function h($b,$p){return new T;}ob_start('h');echo 'A';",
    'fresh-exception-retained-object': b"<?php echo 'P';class T{function __toString(){throw new Exception('E');}function __destruct(){echo 'D';}}function h($b,$p){return new T;}ob_start('h');echo 'A';",
}

if __name__ == '__main__':
    raise SystemExit(0 if scope.main(CASES, 'output-final-cast-throw', Path(__file__),
                                    publish=False, model_seconds=90) else 1)
