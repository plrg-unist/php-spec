<?php
function source_argument_ready_333() { global $target333; $target333 = 'ready'; }
function source_name_333($sent) { echo 'NAME:', ($sent === null ? 'NULL' : $sent), '|'; return ($sent === null ? 'target333' : $sent); }
echo
    ${
        source_name_333(
            $arg333
        )
    };
echo 'BODY|';
return 52;
