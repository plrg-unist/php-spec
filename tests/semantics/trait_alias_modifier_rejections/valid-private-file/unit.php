<?php
trait T{function f(){}}
class C{use T{f as private g;}}
declare(encoding=2);
echo ;