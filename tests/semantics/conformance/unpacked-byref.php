<?php
function f(&$x){$x=8;} $a=[1]; f(...$a); echo $a[0];
