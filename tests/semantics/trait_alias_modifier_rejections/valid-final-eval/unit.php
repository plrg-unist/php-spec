trait T{function f(){}}
class C{use T{f as final g;}}
declare(encoding=2);
echo ;