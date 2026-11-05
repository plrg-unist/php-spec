trait T{function f(){}}
class C{use T{f as readonly}}
declare(encoding=2);
echo ;