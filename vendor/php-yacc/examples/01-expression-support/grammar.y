
%left '+'

%%

expr: 
      expr '+' expr   { $$ = $1 + $3; }
    | '1'             { $$ = 1; }
;

%%
