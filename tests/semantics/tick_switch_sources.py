#!/usr/bin/env python3
"""Original-source switch tick plans; shared tick observation/profile harness."""
from pathlib import Path

import tick_sources as ticks


HEAD = b'<?php function t(){echo "T";}register_tick_function("t");'
CASES = {
    'constant-body': (HEAD + b'declare(ticks=1){switch(1){case 1:echo "A";break;default:echo "B";}}echo "Z";', b'ATZ'),
    'cv-body': (HEAD + b'$x=1;declare(ticks=1){switch($x){case 1:echo "A";break;default:echo "B";}}echo "Z";', b'ATZ'),
    'temporary-body': (HEAD + b'function f(){return 1;}declare(ticks=1){switch(f()){case 1:echo "A";break;default:echo "B";}}echo "Z";', b'ATTZ'),
    'default-fallthrough': (HEAD + b'declare(ticks=1){switch(0){case 1:echo "A";break;default:echo "D";case 2:echo "C";}}echo "Z";', b'DTCTZ'),
    'no-match': (HEAD + b'declare(ticks=1){switch(3){case 1:echo "A";break;case 2:echo "B";}}echo "Z";', b'Z'),
    'later-condition-declarables': (HEAD + b'switch(0){case 0:echo "A";break;case (function(){declare(ticks=1);return 1;})():echo "B";}echo "Z";', b'ATZT'),
    'unselected-body-declarables': (HEAD + b'declare(ticks=1){switch(0){case 0:echo "A";break;default:declare(ticks=3);echo "B";}echo "Z";echo "Y";echo "W";}echo "E";', b'ATZYWTE'),
    'temporary-owned-subject': (HEAD + b'class R{function __destruct(){echo "D";}}function f(){return new R;}declare(ticks=1){switch(f()){default:echo "A";}}echo "Z";', b'ATDTZ'),
    'nested-switch': (HEAD + b'declare(ticks=1){switch(1){case 1:switch(2){case 2:echo "N";break;default:echo "X";}break;default:echo "Y";}}echo "Z";', b'NTZ'),
    'callback-throw': (b'<?php function t(){throw new Exception("E");}register_tick_function("t");try{declare(ticks=1){switch(0){case 0:echo "A";echo "B";}}}catch(Exception $e){echo "C";}echo "Z";', b'ACZ'),
}
CONTROLS = {
    'suppressed-subject-kind': (HEAD + b'$x=1;declare(ticks=1){switch(@$x){default:echo "A";}}echo "Z";', b''),
    'multiline-empty-case-line': (HEAD + b'declare(ticks=1){switch(0){default\n:\n}}echo "Z";', b''),
}


def main(cases=CASES, controls=CONTROLS, producer=Path(__file__)):
    previous = ticks.fingerprint

    def fingerprint():
        return {**previous(), str(producer.relative_to(ticks.ROOT)): ticks.sha(producer)}

    ticks.fingerprint = fingerprint
    ticks.CASES, ticks.CONTROLS = cases, controls
    ticks.STATUSES = {name: 'normal' for name in cases}
    ticks.EXITS = {name: 0 for name in cases}
    ticks.main()


if __name__ == '__main__':
    main()
