trait T{function f(){}}
class C{use T{f as public(set) g;}}
declare(encoding=2);
echo ;