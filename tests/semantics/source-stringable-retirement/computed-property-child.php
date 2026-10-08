<?php
function source_computed_ready_327() { global $target327; $target327->value = 'ready'; }
function source_name_327() { global $target327; echo 'NAME:', $target327->value, '|'; return 'target327'; }
echo
    ${
        source_name_327()
    }
        ->value;
echo 'BODY|';
return 52;
