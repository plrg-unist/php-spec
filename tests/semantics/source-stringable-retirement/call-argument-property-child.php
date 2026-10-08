<?php
function source_argument_ready_333() { global $target333, $arg333; $target333->value = 'ready'; $arg333 = 'target333'; }
function source_name_333($sent) { echo 'NAME:', ($sent === null ? 'NULL' : $sent), '|'; return ($sent === null ? 'target333' : $sent); }
echo
    ${
        source_name_333(
            $arg333
        )
    }
        ->value;
echo 'BODY|';
return 52;
