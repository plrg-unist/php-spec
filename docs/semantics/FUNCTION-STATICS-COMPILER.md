# Named-function static declarations

Compiler111 admits static declarations in supported named user functions. It
uses the pinned `zend_compile_static_var` traversal and pre-evaluation rules,
while runtime112 owns persistent reference cells. Main-unit bindings, class and
closure identity, exception retries and dynamic-source lifetime remain required
core dependencies. The earlier broad integration981/764 is historical.

`PPCSTATIC` in the existing compiler expression list exports `CODESTATIC` with
the declaration path, source variable name, begin line, bind line and stored-mode
flag. The checked `NStaticVar` supplies the initializer at FIELD1; ABSENT means
null. No new public code field is introduced. Runtime source guards reconstruct
the descriptor and relate it to the installed containing function.

`$this` rejection precedes duplicate-name rejection, which precedes initializer
pre-evaluation. Duplicate tracking includes dead branches, traverses comma
entries in order and excludes nested function scopes. The compiler records a CV
for every static name: Zend uses `lookup_cv` even when ordinary reads of that
name use an auto-global or `$GLOBALS` access path. The first implementation
omitted those special CVs. Native opcode/CV projections exposed that omission;
the ordinary special-name sources already agreed before the inventory repair.

Stored mode comes from the contextual constant-folding result before ordinary
expression compilation. An absent initializer needs no pool entry. A stored
expression uses its FIELD1 constant value and class facts without an ordinary
CODEEXPR. A dynamic initializer compiles through ordinary PPR, preserving locals,
side effects, redirects and source lines. In particular, `@1` takes the dynamic
binding path even though its later expression result is constant. Selected
conditional effects execute once; unselected invalid operands remain skipped
only when the pinned pre-evaluator actually selects that branch.

The begin line belongs to the static-variable declaration. Stored bindings keep
that line; dynamic bindings use the compiler location after the initializer.
Source metadata remains unchanged. `PPCSTATIC` has finite skip/export rules in
existing compiler consumers; it is not an ordinary expression or call argument.

The compiler evidence retains thirty exact source contexts: fourteen original
compiler and five runtime contexts on981, followed by eleven contexts on990.
The final maintained fixture checks29 phase outcomes and121 projections, with
one catch-dependent source explicitly Unsupported. Four focused existing gates
cover function compilation46, dynamic calls42 plus2 dependencies, reference
returns58, and typed functions57 plus7 dependencies. Original native profiles,
separate opcode profiles, checked requests and process closures remain distinct.

The archive preserves first descriptor/CV failures and setup failures: recursive
fixture syntax, a fixture incorrectly tracing an Unsupported program, a missing
copied runtime declaration, a colliding test helper, and a missing copied C pin.
Successful fixture reconstruction reuses retained native contexts. The first
snapshot's original string-sorted digest55433cfd and corrected maintained
Path-sorted digest e615c4eb describe the same992 file hashes and modes; the
explicit correction records the hashing protocol rather than relabeling old
executions. Runtime's first constant-pool and stored-read source failures remain
bound through their exact original snapshots and streams.

[Compiler originals](../../coverage/semantics/function-static-compiler-originals.json)
and [exact pairing](../../coverage/semantics/function-static-compiler-pairing.json)
bind the gate identities to the separately reviewed runtime installation.
Runtime behavior and its final fresh maintained compiler gate are reported by
[function statics](../../coverage/semantics/function-statics-runtime.json).
