<?php
function callEchoNamed($prefix = 'P', $sent = 'fallback') { echo 'PREFIX:', $prefix, '|SENT:', ($sent === null ? 'NULL' : $sent), '|'; return 'RESULT|'; }

echo
    callEchoNamed
    (
        sent:
            $argumentEchoNamed
    );
echo 'BODY|';
return 91;
