#!/usr/bin/env python3
"""Coalesce ticks distinguish compiled operands from runtime lazy selection."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'direct-constant-coalesce-emits-switch-temporary': (b'<?php function t(){echo "T";}register_tick_function("t");declare(ticks=1){echo "P";1 ?? 2;switch(1 ?? 2){case 1:echo "A";break;default:echo "B";}echo "Z";}unregister_tick_function("t");', b'PTTATTZT'),
    'coalesce-assignment-callback-observes-committed-value': (b'<?php $x=null;function t(){global $x;if($x==="new"){echo $x;throw new Exception;}}register_tick_function("t");try{declare(ticks=1){$x ??= (static function(){declare(ticks=1);return "new";})();}}catch(Exception $e){echo "Z";}unregister_tick_function("t");', b'newZ'),
}


def main(cases=CASES, controls=None, producer=Path(__file__)):
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(path.relative_to(ticks.ROOT)): ticks.sha(path) for path in [Path(__file__), producer]}}
    ticks.CASES, ticks.CONTROLS = cases, controls or {}
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
