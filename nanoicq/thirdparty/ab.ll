
/* scanner for a toy Pascal-like language */

%{

#ifdef c_plusplus
#include <cmath>

#include <iostream>

using namespace std;
#else

#include <math.h>

#endif

%}

DIGIT       [0-9]
ID          [a-z][a-z0-9]*
AND         ("and"|"&&")
AOR			("or"|"||")
NOT         ("not"|"!")
LPAREN      "("
RPAREN      ")"
PLUS        +
MINUS       -
QUOTED		\"[^\"]+\"

%%

{DIGIT}+    {
           printf( "An integer: %s (%d)\n", yytext,
                   atoi( yytext ) );
           }

{DIGIT}+"."{DIGIT}*        {
           printf( "A float: %s (%g)\n", yytext,
                   atof( yytext ) );
           }

{LPAREN}[^\()\n]+{RPAREN}		{
			printf("An PARENTS token: %s\n", yytext);
		}

if|then|begin|end|procedure|function        {
           printf( "A keyword: %s\n", yytext );
           }

{QUOTED}	{
			printf("An QUOTED token: %s\n", yytext);
		}

{AND}	{
			printf("An AND token: %s\n", yytext);
		}

{AOR}	{
			printf("An OR token: %s\n", yytext);
		}

{NOT}	{
			printf("An NOT token: %s\n", yytext);
		}

{ID}        printf( "An identifier: %s\n", yytext );

"+"|"-"|"*"|"/"   printf( "An operator: %s\n", yytext );

"{"[\^{$\;$}}\n]*"}"     /* eat up one-line comments */

[ \t\n]+          /* eat up whitespace */

.           printf( "Unrecognized character: %s\n", yytext );

%%

int main(int argc, char** argv)
{
    ++argv, --argc;  /* skip over program name */
    if ( argc > 0 )
        yyin = fopen( argv[0], "r" );
    else
        yyin = stdin;

    yylex();
}
