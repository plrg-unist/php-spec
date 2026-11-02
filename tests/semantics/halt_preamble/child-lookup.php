#!/usr/bin/env php
<?php
$n = "__COMPILER_HALT_OFFSET__";
echo "C|", (int)defined($n), "|", __COMPILER_HALT_OFFSET__, "|";
return constant($n);
__halt_compiler();
child-lookup-payload
