# Call reference assignment and surrounding instruction lines

Compiler 96 pairs named positional call-reference acquisition with runtime 97.
It lowers the assignment source through the existing call compiler and module 87
write-result checks. Other writable call contexts retain their prior rules. Array
reference items containing direct calls are compile errors after key compilation
and before call argument compilation. Reference-return declarations, dynamic and
named/unpacked calls, and registered builtin execution remain separate work.

A plain call result assigned by reference emits the assignment-specific Notice
and performs an ordinary target write, preserving existing aliases for CV,
computed-variable and dimension targets. An actual returned reference follows the
reference binding path. MAKE_REF does not convert a plain call VAR into a source
reference. Runtime source guards and ownership review remain mandatory.

Calls have two relevant lines. The call instruction uses its own source line;
a following reference assignment or return inherits the line left by compiling
the call arguments. Nested calls preserve that post-argument location as well.
The shared ppexpr call rule now records the first line without overwriting the
second. The existing ppcall_done location utility remains intact for module 88's
constant diagnostic restoration. This fixes both the new assignment Notice and
an independently retained accepted-926 typed return TypeError location defect.
No second expression evaluator or runtime schema field is introduced.

Final compiler 929/d365385a changes six paths over accepted 926/599f3963. The
maintained 29-source gate checks 26 exact native compilation phases, three explicit
boundaries and 29 source mode/line projections. Shared-line regression checks pass
44 named phases plus two pending, 56 typed phases plus eight pending, 54 default
phases plus three pending, and 37 strict phases plus two pending. Those four gates
retain their tested 929/9331a80c identity: the final bridge changes only a comment
and expands the two maintained test files. It does not relabel the earlier runs.

Evidence keeps ten historical reference-return/acquisition originals replayed on
accepted 926, fifteen new acquisition/array/builtin originals, four new multiline
assignment originals and the reviewer's typed-return location original. Native
compilation and execution are separate. All old Unsupported outcomes remain gaps.
The first builtin diagnostic omission and both line-prototype loader failures are
retained with their source bytes; the corrected source uses the existing helpers.
Original compiler 929/4633dc5c and archive e4060036 remain immutable historical
pre-line-repair evidence. Runtime pairing, state ownership, diagnostics, protocol
closure and final independent acceptance are reported separately. No full reference
return family, typed family, or PHP core closure is claimed.

The compiler pairs with frozen runtime 933/7391ccdf. Its five copied source/test
files match byte-for-byte with their modes, and the ordered registry adds only
module 97. The separate pairing report records those checks.

Paired code commit `af228143` installs the reviewed 933/7391ccdf source closure.
