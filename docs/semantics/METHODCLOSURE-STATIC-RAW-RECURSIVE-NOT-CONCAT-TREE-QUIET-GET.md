# Recursive quiet scalar NOT/CONCAT selectors

Close finite actual BooleanNot/CONCAT trees over the currently certified quiet
raw String/signed64 Integer/Boolean/null and signed64-result UnaryPlus leaves.
Each receipt gives echo(value), and truth(value) equals String truth of those
bytes: Integer0 gives ASCII0, nonzero Integer gives truthy decimal, false/null
give empty and true gives ASCII1. NOT yields PBOOL and CONCAT yields String,
so the invariant is inductive. Every NOT child must have non-NUL returned text.
The literal current Text fallback retains its raw-byte behavior; this makes no
blanket claim that all fallback or CONCAT results exclude NUL. FLOAT needs a
separate argument: signed-zero formatting can change String truth, and NaNs
can warn, so quietness alone does not justify its receipt.

Authenticate exact actual nodes/full metadata/PCFIELD children at every link.
Recursive selector CONCAT retains fixed currentText fallback and disjoint
newSome/priorTextNone site arms, exact rootPSTRING/no child pools, class
normalization after full join and method casefold. FLOAT/NaN/CV/arithmetic,
UnaryMinus, nonquiet/out-of-range UnaryPlus, wider owners/lifetimes and every
exact held boundary stay outside this extension. Pure .watsup; no Zend fallback.

Four native originals ran once; all four pre-edit runs were expected
Unsupported. Author source comparisons and 222/333 fixture assertions passed;
independent source comparisons and 105/102/54 assertions passed at separate
stable cuts. No failures or timeouts occurred. The independent MAIN composition
and sole joined SL508 load are clear. Fixture assertions carry no source credit.
The full core and wider contexts remain unfinished; see the
[review record](../../coverage/semantics/magic-property-methodclosure-static-raw-recursive-not-concat-tree-quiet-get-review.json).
