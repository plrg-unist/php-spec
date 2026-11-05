<?php
trait T{function f(){}}
class C{use T{f as static g;}}
declare(encoding=2);
echo ;