#!/usr/bin/env php
<?php
$n = "__COMPILER_HALT_OFFSET__";
echo "H|", __COMPILER_HALT_OFFSET__, "|", (int)defined($n), "|", constant($n), "|";
__halt_compiler();
lookup-payload
