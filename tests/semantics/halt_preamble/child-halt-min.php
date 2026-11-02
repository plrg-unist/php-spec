#!/usr/bin/env php
<?php
echo "C|", (__FILE__ === __DIR__ . "/child-halt-min.php"), "|", __LINE__, "|", __COMPILER_HALT_OFFSET__, "|";
return 7;
__halt_compiler();
child-min-payload
