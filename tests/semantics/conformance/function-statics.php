<?php
function f(){static $x=0; return ++$x;} echo f(),f(),f();
