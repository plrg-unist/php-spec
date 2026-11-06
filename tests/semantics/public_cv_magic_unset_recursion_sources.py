#!/usr/bin/env python3
"""Recursive CV unset clears stored values before suppressing a guarded callback."""
from pathlib import Path

import tick_sources as ticks

SOURCE = b'''<?php
$count=0;
function recurse85($member){
    global $count;$count=$count+1;
    $current=$GLOBALS['object'];unset($GLOBALS['object']);echo "U";
    unset($current->$member);echo isset($current->value)===false,";";
    unset($current->$member);echo isset($current->value)===false,";";
    unset($current);throw new Exception("recursive");
}
class PublicCVUnset85 {
    public int $value=7;
    public int $plain=99;
    public function __unset(string $member):void {
        echo "M",$member,";";$GLOBALS['name']="plain";
        $this->value=9;recurse85($member);
    }
    public function __destruct(){echo "A;";}
}
$object=new PublicCVUnset85;$name="value";unset($object->$name);$keep="keep";
try{unset($object->$name);$keep="lost";}catch(Exception $error){echo "C",$keep,";";}
unset($error);
$object=new PublicCVUnset85;$name="value";unset($object->$name);
try{unset($object->$name);$keep="lost";}catch(Exception $error){echo "F",$keep,";";}
unset($error);echo $count,"Z";
'''

SOURCE_EXPECTED = b'Mvalue;U1;1;A;Ckeep;Mvalue;U1;1;A;Fkeep;2Z'

CASES = {'public-cv-recursive-unset-state-before-guard': (SOURCE, SOURCE_EXPECTED)}
CONTROLS = {}


def main():
    previous = ticks.fingerprint
    ticks.fingerprint = lambda: {**previous(), **{
        str(Path(__file__).relative_to(ticks.ROOT)): ticks.sha(Path(__file__))}}
    ticks.CASES, ticks.CONTROLS = CASES, CONTROLS
    ticks.STATUSES = {name: 'normal' for name in CASES}
    ticks.EXITS = {name: 0 for name in CASES}
    ticks.main(model_timeout=1800)


if __name__ == '__main__':
    main()
