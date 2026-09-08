#!/usr/bin/env python3
"""Local checked-type helpers versus pinned PHP compilation, never source execution semantics."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'frontend'))
import wire
sys.path.insert(0, str(ROOT / "tests"))
import validate as syntax_validation
PHP = ROOT / '.tools/php/bin/php'
ENV = dict(os.environ, LC_ALL='C', TZ='UTC')
ENV.pop('PHP_SPEC_SCRIPT_ENCODING', None)
PROFILE = json.loads((HERE / 'profile.json').read_text())
FLAGS = [flag for key, value in PROFILE.items() for flag in ('-d', key + '=' + value)]
SPECS = [ROOT / p for p in ['spec/php.watsup', 'spec/semantics/10-bytes.watsup', 'spec/semantics/16-static-types.watsup']]

class Worker:
    def __init__(self, cmd):
        self.p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True, env=ENV)
    def request(self, req):
        signal.setitimer(signal.ITIMER_REAL, 30)
        try:
            self.p.stdin.write(wire.dumps(req) + '\n')
            self.p.stdin.flush()
            result = wire.loads(self.p.stdout.readline())
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
        assert result['ok'], result
        return result
    def close(self):
        try:
            self.p.stdin.close()
            assert self.p.wait(timeout=5) == 0
        finally:
            if self.p.poll() is None:
                self.p.kill()
                self.p.wait(timeout=5)

def byte_expr(s):
    return '[' + ','.join(map(str, s.encode())) + ']'

def type_expr(node):
    if node is None:
        return 'ABSENT'
    tag = 'N' + node['node'].replace('_', '')
    if node['node'] in ['UnionType', 'IntersectionType']:
        value = '(SEQUENCE ([' + ','.join(type_expr(x) for x in node['fields'][0]) + ']))'
    elif node['node'] == 'NullableType':
        value = type_expr(node['fields'][0])
    else:
        value = '(BYTES ' + json.dumps(node['fields'][0]['bytes']) + ')'
    return f'({tag} ({value}) eps)'

def find_type(ast, position):
    def visit(x):
        if isinstance(x, dict):
            name = x.get('node')
            if name == 'Param' and position == 'parameter': return x['fields'][2]
            if name in ['Stmt_Function', 'Stmt_ClassMethod', 'Expr_Closure'] and position == 'return': return x['fields'][-2]
            if name == 'Stmt_Property' and position == 'property': return x['fields'][2]
            if name == 'Stmt_ClassConst' and position == 'constant': return x['fields'][2]
            for v in x.values():
                r = visit(v)
                if r is not None: return r
        elif isinstance(x, list):
            for v in x:
                r = visit(v)
                if r is not None: return r
    return visit(ast)

PATTERNS = [
    ('builtin-unqualified', r"Type declaration .* must be unqualified"),
    ('invalid-class-name', r"is an invalid class name"),
    ('reserved-type-name', r'as a type name as it is reserved'),
    ('no-class-scope', r'when no class scope is active'),
    ('no-parent', r'when current class scope has no parent'),
    ('duplicate-type', r'Duplicate type .* is redundant'),
    ('redundant-intersection', r'Type .* is redundant (?:as it is more restrictive|with type)'),
    ('mixed-standalone', r'Type mixed can only be used as a standalone type'),
    ('true-false-union', r'Type contains both true and false'),
    ('object-class-redundant', r'contains both object and a class type'),
    ('invalid-intersection-member', r'cannot be part of an intersection type'),
    ('mixed-nullable', r'Type mixed cannot be marked as nullable'),
    ('null-nullable', r'null cannot be marked as nullable'),
    ('void-standalone', r'Void can only be used as a standalone type'),
    ('never-standalone', r'never can only be used as a standalone type'),
    ('parameter-void', r'void cannot be used as a parameter type'),
    ('parameter-never', r'never cannot be used as a parameter type'),
    ('property-forbidden-type', r'Property .* cannot have type'),
    ('constant-forbidden-type', r'Class constant .* cannot have type'),
    ('confusable-class', r'will be interpreted as a class name'),
    ('underscore-class', r'Using "_" as a type name is deprecated'),
]

def main():
    def expired(signum, frame):
        raise TimeoutError('static type worker request exceeded 30 seconds')
    signal.signal(signal.SIGALRM, expired)
    subprocess.run([str(ROOT / 'scripts/opam-exec.sh'), 'dune', 'build', '--root', str(HERE), 'numeric_runner.exe'], check=True, cwd=ROOT, timeout=120)
    runner = HERE / '_build/default/numeric_runner.exe'
    watched = SPECS + [Path(__file__), PHP, runner, HERE / 'numeric_runner.ml', ROOT / 'vendor/php-src/Zend/zend_compile.c']
    def fingerprints():
        return {"closure": syntax_validation.implementation_fingerprint(), "direct": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in watched}}
    probe = subprocess.run([str(PHP), '-n', *FLAGS, '-r', 'echo json_encode([PHP_VERSION,PHP_SAPI,PHP_INT_SIZE,PHP_ZTS,ini_get_all(null,false)]);'], capture_output=True, text=True, timeout=10, env=ENV, check=True)
    identity = json.loads(probe.stdout)
    assert identity[:4] == ['8.5.10', 'cli', 8, False], identity[:4]
    for key,value in PROFILE.items():
        assert identity[4][key] == value, (key,identity[4][key],value)
    before = fingerprints()
    frontend = Worker([str(PHP), '-n', *FLAGS, '-d', 'extension=' + str(ROOT / '.tools/php-file.so'), str(ROOT / 'frontend/worker.php')])
    adapter = Worker([str(ROOT / '_build/default/adapter/main.exe'), str(ROOT)])
    atoms = ['int', 'INT', 'string', 'float', 'bool', 'true', 'false', 'null', 'void', 'never', 'mixed', 'object', 'iterable', 'array', 'callable', 'A', 'a', 'Traversable', 'self', 'parent', 'static', 'integer', 'boolean', 'double', 'resource', 'Integer', '_', r'\int', r'\A', r'namespace\A', r'namespace\int', r'\self', r'namespace\self']
    types = atoms + ['?' + t for t in ['int', 'null', 'void', 'never', 'mixed', 'A', 'self', 'static']]
    types += [a + '|' + b for a in ['int', 'bool', 'false', 'true', 'null', 'mixed', 'void', 'never', 'object', 'iterable', 'array', 'callable', 'A', 'Traversable', 'self', 'static'] for b in ['int', 'bool', 'false', 'true', 'null', 'mixed', 'void', 'never', 'object', 'iterable', 'array', 'callable', 'Traversable', 'a', 'self', 'parent', 'static']]
    types += ['A&B', 'A&a', 'int&A', 'iterable&A', 'self&A', 'parent&A', 'integer&integer', '(A&B)|A', 'A|(B&A)', '(A&B)|(B&A)', '(A&B)|(A&B&C)', '(A&B&C)|(B&A)', '(A&B)|(B&C)', 'object|(A&B)', 'iterable|(Traversable&A)', '(A&B)|mixed', 'integer|int|INT', 'object|A|int|INT']
    cases = [(t, p, scope, '') for t in types for p, scope in [('parameter','global'),('return','class')]]
    cases += [(t, p, 'class', '') for p in ['property','constant'] for t in ['void','never','callable','int','mixed','self','parent','object|A','?void']]
    cases += [(t, 'return', scope, '') for t in ['self','parent','static','self&A','parent&A'] for scope in ['global','noparent','trait','anonymous','closure']]
    cases += [(t, 'parameter', 'global', 'namespace Ns; use Foo\\Bar as Alias; ') for t in ['Alias', r'Alias\Sub', 'alias|\\Foo\\Bar', 'iterable|Traversable', 'iterable|\\Traversable', 'integer', 'boolean', 'double', 'resource', 'Integer', '_']]
    cases += [('integer', 'parameter', 'global', 'use Foo as integer; ')]
    multiline = {
        'multiline-parameter': ('<?php\nfunction f(\n integer |\n int |\n INT $x\n) {}', 3),
        'multiline-return': ('<?php\nfunction f():\n A|\n a {}', 2),
        'multiline-property': ('<?php\nclass C {\n public\n callable\n $x;\n}', 4),
    }
    cases += [(name, name.removeprefix('multiline-'), 'noparent' if name == 'multiline-property' else 'global', '') for name in multiline]
    records, declarations = [], []
    descriptors = {('Alias','parameter','global'):'[(PTBRANCH ([(PTCLASS ([70,111,111,92,66,97,114]))]))]', ('Alias\\Sub','parameter','global'):'[(PTBRANCH ([(PTCLASS ([70,111,111,92,66,97,114,92,83,117,98]))]))]', ('self','return','class'):'[(PTBRANCH ([(PTCLASS ([67]))]))]', ('parent','return','class'):'[(PTBRANCH ([(PTCLASS ([80]))]))]', ('self','return','trait'):'[(PTBRANCH ([PTSELF]))]', ('parent','return','closure'):'[(PTBRANCH ([PTPARENT]))]', ('static','return','anonymous'):'[(PTBRANCH ([PTSTATIC]))]', ('?int','parameter','global'):'[(PTBRANCH ([(PTBUILTIN \"int\")])),(PTBRANCH ([(PTBUILTIN \"null\")]))]', ('A&B','parameter','global'):'[(PTBRANCH ([(PTCLASS ([65])),(PTCLASS ([66]))]))]'}
    descriptor_checks = 0
    negative_context = '{NAMESPACE eps, IMPORTS eps, SCOPE PTGLOBAL, POSITION PTRETURN, OWNER eps, MEMBER eps, FILE ([102]), LINE 1}'
    negatives = [
        ('(NName (BYTES "") eps)', negative_context, 'edited invalid type name'),
        ('(NName (BYTES "XEE=") eps)', negative_context, 'edited invalid type name'),
        ('(NUnionType (SEQUENCE eps) eps)', negative_context, 'edited singleton or empty union'),
        ('(NIntersectionType (SEQUENCE eps) eps)', negative_context, 'edited singleton or empty intersection'),
        ('(NVarLikeIdentifier (BYTES "eA==") eps)', negative_context, 'variable-like identifier in declaration type'),
        ('(NIdentifier (BYTES "aW50") eps)', negative_context.replace('LINE 1','LINE 0'), 'missing source file or compiler line'),
        ('(NIdentifier (BYTES "aW50") eps)', negative_context.replace('FILE ([102])','FILE eps'), 'missing source file or compiler line'),
    ]
    try:
        with tempfile.TemporaryDirectory(prefix='static-types-', dir=ROOT / '.tools') as tmp:
            for index, (t, position, scope, ns) in enumerate(cases):
                member = {'parameter': f'function f({t} $x) {{}}', 'return': f'function f(): {t} {{}}', 'property': f'public {t} $x;', 'constant': f'const {t} X = UNKNOWN;'}[position]
                if scope == 'class': body = f'class P {{}} class C extends P {{ {member} }}'
                elif scope == 'noparent': body = f'class C {{ {member} }}'
                elif scope == 'trait': body = f'trait T {{ {member} }}'
                elif scope == 'anonymous': body = f'$x = new class {{ {member} }};'
                elif scope == 'closure': body = '$x = ' + member.replace('function f', 'function') + ';'
                else: body = member
                source = ('<?php ' + ns + body).encode()
                compiler_line = 1
                if t in multiline:
                    source_text, compiler_line = multiline[t]
                    source = source_text.encode()
                parsed = frontend.request({'op':'parse','source':base64.b64encode(source).decode()})
                native = frontend.request({'op':'oracle','source':base64.b64encode(source).decode()})
                frontend_restriction = None
                if parsed['accepted'] != native['accepted']:
                    assert source == b'<?php function f(void $x) {}' and native['accepted'], (source,parsed,native)
                    assert base64.b64decode(parsed['message']) == b'void cannot be used as a parameter type on line 1'
                    frontend_restriction = parsed
                    seed = frontend.request({'op':'parse','source':base64.b64encode(b'<?php function f(): void {}').decode()})
                    checked_seed = adapter.request({'op':'check','ast':seed['ast']})
                    node = find_type(checked_seed['ast'],'return')
                if not parsed['accepted'] and frontend_restriction is None:
                    records.append({'type':t,'position':position,'scope':scope,'source':source.decode(),'status':'parser-rejected','frontend':parsed,'zend':native})
                    continue
                if frontend_restriction is None:
                    checked = adapter.request({'op':'check','ast':parsed['ast']})
                    node = find_type(checked['ast'], position)
                assert node, (position, checked)
                file = Path(tmp) / 'input.php'; file.write_bytes(source)
                run = subprocess.run([str(PHP), '-n',*FLAGS,'-l',str(file)],capture_output=True,text=True,timeout=10,env=ENV)
                assert run.returncode in (0, 255), (source, 'unexpected oracle termination', run.returncode, run.stdout, run.stderr)
                diagnostics, messages = [], []
                for line in run.stderr.splitlines():
                    if not line.strip() or line == 'Stack trace:' or re.match(r'#\d+ ', line): continue
                    assert re.match(r'(?:PHP )?(Warning|Deprecated|Fatal error): (.*) in .* on line (\d+)$',line), repr(line)
                    severity, message, oracle_line = re.match(r'(?:PHP )?(Warning|Deprecated|Fatal error): (.*) in .* on line (\d+)$',line).groups()
                    assert int(oracle_line) == compiler_line, (source,oracle_line,compiler_line)
                    matches = [code for code, pattern in PATTERNS if re.search(pattern,message)]
                    # Unresolved constant initializers defer value checking beyond local type compilation.
                    if not matches: raise AssertionError((source,run.stderr))
                    messages.append(message)
                    diagnostics.append(({'Warning':'warning','Deprecated':'deprecated','Fatal error':'fatal'}[severity],matches[0]))
                scope_expr = {'global':'PTGLOBAL','class':'(PTKNOWN ([67]) ([80]))','noparent':'(PTKNOWN ([67]) eps)','trait':'PTDEFERRED','anonymous':'(PTANONYMOUS false)','closure':'PTDEFERRED'}[scope]
                imports = '([([65,108,105,97,115], [70,111,111,92,66,97,114])])' if ns.startswith('namespace') else ('([([105,110,116,101,103,101,114], [70,111,111])])' if ns else 'eps')
                context = f'{{NAMESPACE ({byte_expr("Ns") if ns.startswith("namespace") else "eps"}), IMPORTS {imports}, SCOPE {scope_expr}, POSITION PT{position.upper()}, OWNER ([67]), MEMBER ({byte_expr("X" if position == "constant" else "x")}), FILE ({byte_expr(str(file))}), LINE {compiler_line}}}'
                expected = '[' + ','.join('(' + json.dumps(level) + ',' + json.dumps(code) + ')' for level,code in diagnostics) + ']'
                success = 'false' if run.returncode else 'true'
                declarations.append(f'dec $case{index}() : bool\ndef $case{index}() = true\n  -- if ptresult = $ptype_normalize({type_expr(node)}, {context})\n  -- if $pttest_ok(ptresult) = {success}\n  -- if $pttest_diags(ptresult) = {expected}\n  -- if $pttest_messages(ptresult) = [{','.join(byte_expr(m) for m in messages)}]\n  -- if $pttest_locations(ptresult) = [{','.join(f'({byte_expr(str(file))},{compiler_line})' for m in messages)}]\n')
                if (t,position,scope) in descriptors:
                    declarations[-1] += f'  -- if ptresult = PTOK ({descriptors[t,position,scope]}) eps\n'
                    descriptor_checks += 1
                records.append({'type':t,'position':position,'scope':scope,'source':source.decode(),'status':'frontend-compile-restriction' if frontend_restriction else 'compared','frontend_restriction':frontend_restriction,'context':{'file':str(file),'compiler_line':compiler_line},'exit':run.returncode,'diagnostics':diagnostics,'stderr':run.stderr.replace(str(file),'input.php')})
            prefix = '''dec $pttest_ok(ptresult) : bool
 def $pttest_ok(PTOK ptbranch* ptdiagnostic*) = true
 def $pttest_ok(PTERROR ptdiagnostic*) = false
 dec $pttest_diags(ptresult) : (text, text)*
 def $pttest_diags(PTOK ptbranch* (PTDIAGNOSTIC text_level text_code ptbranch_arg* ptcontext)*) = (text_level, text_code)*
 def $pttest_diags(PTERROR (PTDIAGNOSTIC text_level text_code ptbranch_arg* ptcontext)*) = (text_level, text_code)*
 dec $pttest_messages(ptresult) : ptbytes*
 def $pttest_messages(PTOK ptbranch* ptdiagnostic*) = ($ptmessage(ptdiagnostic))*
 def $pttest_messages(PTERROR ptdiagnostic*) = ($ptmessage(ptdiagnostic))*
 dec $pttest_locations(ptresult) : (ptbytes, nat)*
 def $pttest_locations(PTOK ptbranch* (PTDIAGNOSTIC text_level text_code ptbranch_arg* ptcontext)*) = (ptcontext.FILE, ptcontext.LINE)*
 def $pttest_locations(PTERROR (PTDIAGNOSTIC text_level text_code ptbranch_arg* ptcontext)*) = (ptcontext.FILE, ptcontext.LINE)*
'''
            comparisons = len(declarations)
            intended = []
            for scope in ['PTGLOBAL', '(PTKNOWN ([67]) eps)', '(PTKNOWN ([67]) ([80]))', '(PTANONYMOUS false)', '(PTANONYMOUS true)', 'PTDEFERRED']:
                for position in ['PTRETURN','PTPARAMETER','PTPROPERTY','PTCONSTANT']:
                    context = negative_context.replace('SCOPE PTGLOBAL', 'SCOPE ' + scope).replace('POSITION PTRETURN','POSITION ' + position)
                    code = 'no-class-scope' if scope == 'PTGLOBAL' else ('static-return-only' if position != 'PTRETURN' else None)
                    expression = f'$ptype_normalize((NNameRelative (BYTES "c3RhdGlj") eps), {context})'
                    assertion = f'  -- if ptresult = {expression}\n'
                    if code is None:
                        assertion += '  -- if ptresult = PTOK ([(PTBRANCH ([PTSTATIC]))]) eps\n'
                    else:
                        message = 'Cannot use "static" when no class scope is active' if scope == 'PTGLOBAL' else 'static can only be used as a return type'
                        assertion += f'  -- if $pttest_ok(ptresult) = false\n  -- if $pttest_diags(ptresult) = [("fatal", "{code}")]\n  -- if $pttest_messages(ptresult) = [{byte_expr(message)}]\n'
                    declarations.append(f'dec $case_intended{len(intended)}() : bool\ndef $case_intended{len(intended)}() = true\n' + assertion)
                    intended.append({'syntax':'NNameRelative static','scope':scope,'position':position,'expected':code or 'PTSTATIC','classification':'adjudicated semantics, not oracle agreement'})
            for index,(ast,context,message) in enumerate(negatives):
                declarations.append(f'dec $case_negative{index}() : bool\ndef $case_negative{index}() = true\n  -- if $ptype_normalize({ast},{context}) = PTUNSUPPORTED {json.dumps(message)}\n')
            for start in range(0,len(declarations),50):
                batch = declarations[start:start+50]
                names = [re.search(r'\$case(?:_negative|_intended)?\d+',d).group() for d in batch]
                fixture = Path(tmp) / 'cases.watsup'
                fixture.write_text(prefix + '\n'.join(batch) + '\ndec $main() : bool\ndef $main() = true\n' + '\n'.join(f'  -- if {n}()' for n in names) + '\n')
                r = subprocess.run([str(runner),*map(str,SPECS),str(fixture)],capture_output=True,text=True,timeout=120)
                if r.returncode or r.stdout.strip() != 'true':
                    (ROOT / '.tools/static-types-failure.watsup').write_text(fixture.read_text())
                    raise AssertionError((start, r.stdout, r.stderr))
    finally:
        frontend.close(); adapter.close()
    assert before == fingerprints(), 'inputs changed during validation'
    report = {'target':'PHP 8.5.10 CLI NTS signed64','result':'pass','compared':comparisons,'explicit_unsupported':len(negatives),'intended_semantics':intended,'descriptor_checks':descriptor_checks,'parser_rejected':len(records)-comparisons,'frontend_compile_restrictions':sum(r['status']=='frontend-compile-restriction' for r in records),'fingerprints':before,'identity':identity,'profile':PROFILE,'environment':{'LC_ALL':'C','TZ':'UTC'},'budgets':{'request_seconds':30,'shutdown_seconds':5,'lint_seconds':10,'batch_seconds':120},'comparison':'ordered severity, code, exact message bytes, explicit file and compiler line; nine exact descriptors','cases':records}
    (ROOT / 'coverage/semantics/static-types.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k not in ['cases','fingerprints','identity','intended_semantics']}))

if __name__ == '__main__': main()
