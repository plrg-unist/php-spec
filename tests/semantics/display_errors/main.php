<?php
echo 'I[', ini_get('display_errors'), ']|';
trigger_error('start', E_USER_NOTICE);
echo 'O[', ini_set('display_errors', 'stdout'), ']|';
trigger_error('stdout', E_USER_NOTICE);
echo 'N[', ini_set('display_errors', null), ']|';
trigger_error('null', E_USER_NOTICE);
ini_restore('display_errors');
echo 'R[', ini_get('display_errors'), ']|';
trigger_error('restore', E_USER_NOTICE);
echo 'END';
