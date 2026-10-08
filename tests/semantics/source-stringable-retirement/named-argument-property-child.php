<?php
function source_named_ready_336() { global $target336, $arg336; $target336->value = 'ready'; $arg336 = 'target336'; }
function source_name_336($prefix = 'P', $sent = 'fallback') { echo 'PREFIX:', $prefix, '|NAME:', ($sent === null ? 'NULL' : $sent), '|'; return ($sent === null ? 'target336' : $sent); }
echo
    ${
        source_name_336(
            sent:
                $arg336
        )
    }
        ->value;
echo 'BODY|';
return 52;
