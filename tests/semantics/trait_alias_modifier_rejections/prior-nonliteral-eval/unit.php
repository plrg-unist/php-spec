trait T{function f(){declare(encoding=1,encoding=true);}}
class C{use T{f as readonly g;}}
declare(encoding=2);
echo ;