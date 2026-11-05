<?php
trait T{function f(){}}
class C{use T{f as public(set);}}
declare(encoding=2);
echo ;