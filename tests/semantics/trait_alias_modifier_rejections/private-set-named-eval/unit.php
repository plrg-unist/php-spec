trait T{function f(){}}
class C{use T{f as private(set) g;}}
declare(encoding=2);
echo ;