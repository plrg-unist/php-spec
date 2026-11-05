trait T{function f(){}}
class C{use T{f as protected(set) g;}}
declare(encoding=2);
echo ;