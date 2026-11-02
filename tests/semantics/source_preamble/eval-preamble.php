<?php
try { eval("\xEF\xBB\xBF echo 'X';"); echo 'OK|'; }
catch (ParseError $e) { echo 'P', $e->getLine(), ':', $e->getMessage(), '|'; }
echo 'S', eval("#!/usr/bin/env php\nreturn __LINE__;"), '|';
