<?php
function source_globals_ready_320() { $GLOBALS['payload']->value = 'ready'; }

echo
    $GLOBALS
        ->value;
return 52;
