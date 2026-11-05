echo ;
trait T{function f(){}}
class C{use T{f as readonly g;}}
declare(encoding=2);