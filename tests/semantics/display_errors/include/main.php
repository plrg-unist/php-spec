<?php
echo 'MAIN|';
ini_set('display_errors', 'stdout');
include 'child.php';
echo 'MODE[', ini_get('display_errors'), ']|END';
