<?php
trait T{function f(){}}
class C{use T{f as abstract g;}}
declare(encoding=2);
echo ;