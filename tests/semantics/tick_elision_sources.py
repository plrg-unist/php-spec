#!/usr/bin/env python3
"""Conditional tick plans follow actual compiled redirects and retained effects."""
from pathlib import Path

import tick_sources as ticks


CASES = {
    'logical-bool-redirect-cv-and-switch-free': (b'<?php function t(){echo "T";}$flag=1;register_tick_function("t");declare(ticks=1){echo "P";true && $flag;switch(true && $flag){case true:echo "A";break;default:echo "B";}echo "Z";}unregister_tick_function("t");', b'PTTATTZT'),
    'redirect-retains-effect-outside-selected-cv': (b'<?php function t(){echo "T";}$flag=1;register_tick_function("t");declare(ticks=1){echo "P";(print "L") && $flag;echo "Z";}unregister_tick_function("t");', b'PTLTZT'),
    'shorthand-compiles-runtime-unselected-body': (b'<?php function t(){echo "T";}register_tick_function("t");declare(ticks=0){$value=true ?: (static function(){declare(ticks=2);return 0;})();echo "Z";echo "W";}', b'ZTW'),
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
