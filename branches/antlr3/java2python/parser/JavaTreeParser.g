/*
For more information see the head comment within the 'java.g' grammar file
that defines the input for this tree grammar.

BSD licence

Copyright (c) 2007-2008 by HABELITZ Software Developments

All rights reserved.

http://www.habelitz.com


Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions
are met:

 1. Redistributions of source code must retain the above copyright
    notice, this list of conditions and the following disclaimer.
 2. Redistributions in binary form must reproduce the above copyright
    notice, this list of conditions and the following disclaimer in the
    documentation and/or other materials provided with the distribution.
 3. The name of the author may not be used to endorse or promote products
    derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY HABELITZ SOFTWARE DEVELOPMENTS ('HSD') ``AS IS''
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL 'HSD' BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
*/
tree grammar JavaTreeParser;

options { language=Python; backtrack=true; memoize=true; tokenVocab=Java;
          ASTLabelType=CommonTree; superClass=LocalTreeParser; }

@treeparser::header {
from java2python.parser.extra import LocalTreeParser
}

javaSource[module] @init { self.onJavaSource(module) }
    :   ^(JAVA_SOURCE annotationList packageDeclaration? importDeclaration* typeDeclaration*)
    ;

packageDeclaration
    :   ^(PACKAGE q0=qualifiedIdentifier) { self.onPackageDecl($q0.text) }
    ;

importDeclaration
    :   ^(IMPORT s0=STATIC? q0=qualifiedIdentifier d0=DOTSTAR?)
         { self.onImportDecl($q0.text, bool($s0), bool($d0)) }
    ;

typeDeclaration
    @init { self.commentHandler($start) }
    :   ^(CLASS m0=modifierList i0=IDENT t0=genericTypeParameterList?
                x0=extendsClause? p0=implementsClause?
          { klass = self.onClass($i0.text, $m0.mods, $x0.clauses, $p0.clauses) }
          classTopLevelScope
          { self.pop() }
        )

    |   ^(INTERFACE m1=modifierList i1=IDENT t1=genericTypeParameterList? x1=extendsClause?
          { self.onClass($i1.text, $m1.mods, $x1.clauses) }
          interfaceTopLevelScope
          { self.pop() }
        )

    |   ^(ENUM m2=modifierList i2=IDENT p2=implementsClause?
          { klass = self.onClass($i2.text, $m2.mods, None, $p2.clauses) }
          enumTopLevelScope
          { self.pop() }
        )

    |   ^(AT m3=modifierList i3=IDENT
          { klass = self.onAnnoType($i3.text, $m3.mods) }
          annotationTopLevelScope
          { self.pop() }
        )
    ;

extendsClause returns [clauses] @init { clauses = [] }
    :   ^(EXTENDS_CLAUSE (t0=type { clauses.append($t0.value) })+)
    ;

implementsClause returns [clauses] @init { clauses = [] }
    :   ^(IMPLEMENTS_CLAUSE (t0=type { clauses.append($t0.value) })+)
    ;

genericTypeParameterList
    :   ^(GENERIC_TYPE_PARAM_LIST genericTypeParameter+)
    ;

genericTypeParameter
    :   ^(IDENT bound?)
    ;

bound
    :   ^(EXTENDS_BOUND_LIST type+)
    ;

enumTopLevelScope @init { enums = [] }
    @after { self.onEnumScope(enums) }
    :   ^(ENUM_TOP_LEVEL_SCOPE (e0=enumConstant { enums.append($e0.decl) })+ classTopLevelScope?)
    ;

enumConstant returns [decl] @init { klass = None }
    @after {
        $decl = ($i0.text, $a0.args)
        if not klass:
            klass = self.onEnum($i0.text, $a0.args)
        self.pop()
    }
    :   ^(i0=IDENT annotationList (a0=arguments)?
          ({ klass = self.onEnum($i0.text, $a0.args) } classTopLevelScope)?
        )
    ;

classTopLevelScope @init { self.commentHandler($start) }
    :   ^(CLASS_TOP_LEVEL_SCOPE classScopeDeclarations*)
    ;

classScopeDeclarations
    :   ^(CLASS_INSTANCE_INITIALIZER block)
    |   ^(CLASS_STATIC_INITIALIZER block)

    |   ^(FUNCTION_METHOD_DECL m0=modifierList genericTypeParameterList? t0=type i0=IDENT
          p0=formalParameterList arrayDeclaratorList? throwsClause?
          { self.onMethod($i0.text, $m0.mods, $p0.params) } block? { self.pop() }
        )

    |   ^(VOID_METHOD_DECL m1=modifierList genericTypeParameterList? i1=IDENT
          p1=formalParameterList throwsClause?
          { self.onMethod($i1.text, $m1.mods, $p1.params) } block? { self.pop() }
        )

    |   ^(VAR_DECLARATION m2=modifierList t2=type v2=variableDeclaratorList)
         { self.onVariables($v2.decls, $t2.value) }

    |   ^(CONSTRUCTOR_DECL m3=modifierList genericTypeParameterList?
          p3=formalParameterList throwsClause?
          { self.onMethod("__init__", $m3.mods, $p3.params) } block { self.pop() }
        )
    |   typeDeclaration
    ;

interfaceTopLevelScope
    :   ^(INTERFACE_TOP_LEVEL_SCOPE interfaceScopeDeclarations*)
    ;

interfaceScopeDeclarations
    :   ^(FUNCTION_METHOD_DECL m0=modifierList genericTypeParameterList? t0=type i0=IDENT
          p0=formalParameterList arrayDeclaratorList? throwsClause?
          { self.onMethod($i0.text, $m0.mods, $p0.params, pop=True) }
        )

    |   ^(VOID_METHOD_DECL m1=modifierList genericTypeParameterList? i1=IDENT
          p1=formalParameterList throwsClause?
          { self.onMethod($i1.text, $m1.mods, $p1.params, pop=True) }
        )
    |   ^(VAR_DECLARATION modifierList t2=type v2=variableDeclaratorList)
          { self.onVariables($v2.decls, $t2.value) }
    |   typeDeclaration
    ;

variableDeclaratorList returns [decls] @init { $decls = [] }
    :   ^(VAR_DECLARATOR_LIST (v0=variableDeclarator { $decls.append($v0.decl) })+)
    ;

variableDeclarator returns [decl] @init { $decl = dict() }
    :   ^(VAR_DECLARATOR v0=variableDeclaratorId { $decl = $v0.decl }
          (vi0=variableInitializer { $decl["init"] = $vi0.exp })?
         )
    ;

variableDeclaratorId returns [decl] @init { $decl = dict() }
    :   ^(i0=IDENT { $decl["id"] = $i0.text }
              (a0=arrayDeclaratorList { $decl["array"] = [$a0.text] })?
        )
    ;

variableInitializer returns [exp]
    :   arrayInitializer { $exp = $arrayInitializer.exp }
    |   expression { $exp = $expression.exp }
    ;

arrayDeclarator
    :   LBRACK RBRACK
    ;

arrayDeclaratorList
    :   ^(ARRAY_DECLARATOR_LIST ARRAY_DECLARATOR*)
    ;

arrayInitializer returns [exp] @init { $exp = [] }
    @after { $exp = "[" + ", ".join($exp) + "]" }
    :   ^(ARRAY_INITIALIZER (v0=variableInitializer { $exp.append($v0.exp) })*)
    ;

throwsClause
    :   ^(THROWS_CLAUSE qualifiedIdentifier+)
    ;

modifierList returns [mods] @init { $mods = [] }
    :   ^(MODIFIER_LIST (m0=modifier { $mods.append($m0.value) })*)
    ;

modifier returns [value]
    :   PUBLIC { $value = $text }
    |   PROTECTED { $value = $text }
    |   PRIVATE { $value = $text }
    |   STATIC { $value = $text }
    |   ABSTRACT { $value = $text }
    |   NATIVE { $value = $text }
    |   SYNCHRONIZED { $value = $text }
    |   TRANSIENT { $value = $text }
    |   VOLATILE { $value = $text }
    |   STRICTFP { $value = $text }
    |   localModifier { $value = $localModifier.value }
    ;

localModifier returns [value]
    :   FINAL { $value = $FINAL.text }
    |   annotation { $value = $annotation.value }
    ;

localModifierList returns [mods] @init { $mods = [] }
    :   ^(LOCAL_MODIFIER_LIST (m0=localModifier { $mods.append($m0.value) })*)
    ;

type returns [value]
    :   ^(TYPE
          (p0=primitiveType { $value = $p0.text } | q0=qualifiedTypeIdent { $value = $q0.text })
          (arrayDeclaratorList { $value += $arrayDeclaratorList.text })? // FAIL
        )
    ;

qualifiedTypeIdent
    :   ^(QUALIFIED_TYPE_IDENT typeIdent+)
    ;

typeIdent returns [value]
    :   ^(i0=IDENT genericTypeArgumentList?) { $value = $i0.text }
    ;

primitiveType
    :   BOOLEAN
    |   CHAR
    |   BYTE
    |   SHORT
    |   INT
    |   LONG
    |   FLOAT
    |   DOUBLE
    ;

// generic types and arguments aren't handled -- yet
// one idea to use them is in python 3 output.
// see pep 3107 http://www.python.org/dev/peps/pep-3107/

genericTypeArgumentList
    :   ^(GENERIC_TYPE_ARG_LIST genericTypeArgument+)
    ;

genericTypeArgument
    :   type
    |   ^(QUESTION genericWildcardBoundType?)
    ;

genericWildcardBoundType
    :   ^(EXTENDS type)
    |   ^(SUPER type)
    ;

formalParameterList returns [params] @init { params = [] }
    :   ^(FORMAL_PARAM_LIST (p0=formalParameterStandardDecl { params.append($p0.value) })*
            (f0=formalParameterVarargDecl { params.append($f0.value) })?
        )
    ;

formalParameterStandardDecl returns [value]
    :   ^(FORMAL_PARAM_STD_DECL localModifierList t0=type v0=variableDeclaratorId)
         { $value = self.makeParamDecl($v0.decl, $t0.text) }
    ;

formalParameterVarargDecl returns [value]
    :   ^(FORMAL_PARAM_VARARG_DECL localModifierList t0=type v0=variableDeclaratorId)
         { $value = self.makeParamDecl($v0.decl, $t0.text, isVariadic=True) }
    ;

qualifiedIdentifier
    :   IDENT
    |   ^(DOT qualifiedIdentifier IDENT)
    ;

annotationList
    :   ^(ANNOTATION_LIST annotation*)
    ;

annotation returns [value] @init { inits = [] }
    :   ^(AT q0=qualifiedIdentifier (a0=annotationInit { inits.append($a0.exp) })?)
         { $value = [$q0.text, inits] }
    ;

annotationInit returns [exp]
    :   ^(ANNOTATION_INIT_BLOCK (a0=annotationInitializers { $exp = $a0.inits }))
    ;

annotationInitializers returns [inits] @init { $inits = [] }
    :   ^(ANNOTATION_INIT_KEY_LIST
            (a0=annotationInitializer { $inits.append($a0.value) })+
        )
    |   ^(ANNOTATION_INIT_DEFAULT_KEY
            (a1=annotationElementValue { $inits = [$a1.exp] })
        )
    ;

annotationInitializer returns [value]
    :   ^(i0=IDENT v0=annotationElementValue) { $value = [$i0.text, $v0.exp] }
    ;

annotationElementValue returns [exp]
    :   ^(ANNOTATION_INIT_ARRAY_ELEMENT annotationElementValue*)
    |   annotation // TODO
    |   expression { $exp = $expression.exp }
    ;

annotationTopLevelScope
    :   ^(ANNOTATION_TOP_LEVEL_SCOPE annotationScopeDeclarations*)
    ;

annotationScopeDeclarations
    :   ^(ANNOTATION_METHOD_DECL m0=modifierList t0=type i0=IDENT (d0=annotationDefaultValue)?)
        { self.onAnnotationMethod($i0.text, $m0.mods, $d0.value) }
    |   ^(VAR_DECLARATION modifierList type variableDeclaratorList)
    |   typeDeclaration
    ;

annotationDefaultValue returns[value]
    :   ^(DEFAULT (v0=annotationElementValue { $value = $v0.text }))
    ;

block
    :   ^(BLOCK_SCOPE blockStatement*)
    ;

blockStatement
    :   localVariableDeclaration
    |   typeDeclaration
    |   statement
    ;

localVariableDeclaration
    :   ^(VAR_DECLARATION m0=localModifierList t0=type v0=variableDeclaratorList)
         { self.onVariables($v0.decls, $t0.value) }
    ;

statement
    :   block
    |   ^(ASSERT (a0=expression { args=[$a0.exp] }
                 (a1=expression { args.append($a1.exp) })?)
            { self.onAssert(*args) }
        )

    |   ^(IF parenthesizedExpression statement statement?)

    |   ^(FOR i0=forInit c0=forCondition u0=forUpdater
             { b, s = self.onFor($i0.exps, $c0.cond) }
             statement
             { self.onForFinish(s, $u0.exps, pop=True) }
        )

    |   ^(FOR_EACH
             localModifierList t1=type i1=IDENT e1=expression
             { self.onForEach($t1.value, $i1.text, $e1.exp) }
             statement
             { self.pop() }
        )

    |   ^(WHILE { ws = self.onWhile() }
            p0=parenthesizedExpression
            statement
            { self.onWhileFinish(ws, $p0.exp, pop=True) }
        )

    |   ^(DO { ds = self.onDo() }
            statement
            (p0=parenthesizedExpression { self.onDoFinish(ds, $p0.exp, pop=True) })
        )

    |   ^(TRY { self.onTry() }
          block { self.pop() } catches?
          ({ self.onFinally() } block { self.pop() } )?
        )

    |   ^(SWITCH parenthesizedExpression switchBlockLabels)
    |   ^(SYNCHRONIZED parenthesizedExpression block)
    |   ^(RETURN (ex0=expression { self.onReturn($ex0.exp) })?)
    |   ^(THROW (ex0=expression { self.onThrow($ex0.exp) }))

    |   ^(BREAK (id0=IDENT)? ) { self.onBreak($id0.text if $id0 else None) }
    |   ^(CONTINUE (id0=IDENT)? ) { self.onContinue($id0.text if $id0 else None) }
    |   ^(LABELED_STATEMENT IDENT statement)
    |   (x0=expression { self.current.addSource($x0.exp or "") })
    |   SEMI
    ;

catches
    :   ^(CATCH_CLAUSE_LIST (
            { stmt = self.onExcept() }
            c0=catchClause
            { self.onExceptClause(stmt, $c0.clause, pop=True) }
         )+
        )
    ;

catchClause returns [clause]
    :   ^(CATCH (d0=formalParameterStandardDecl { $clause = $d0.value}) block)
    ;

switchBlockLabels
    :   ^(SWITCH_BLOCK_LABEL_LIST switchCaseLabel* switchDefaultLabel? switchCaseLabel*)
    ;

switchCaseLabel
    :   ^(CASE expression blockStatement*)
    ;

switchDefaultLabel
    :   ^(DEFAULT blockStatement*)
    ;

forInit returns [exps] @init { $exps = [] }
    :   ^(FOR_INIT (d0=localVariableDeclaration { $exps.append($d0.text) }
                   | (e0=expression { $exps.append($e0.exp) })*)?)
    ;

forCondition returns [cond] @init { $cond = None }
    :   ^(FOR_CONDITION (e0=expression { $cond = $e0.exp })?)
    ;

forUpdater returns [exps] @init { $exps = [] }
    :   ^(FOR_UPDATE (e0=expression {$exps.append($e0.exp)})*)
    ;

parenthesizedExpression returns [exp]
    :   ^(PARENTESIZED_EXPR e0=expression { $exp = "(" + ($e0.exp or "") + ")" })
    ;

expression returns [exp]
    :   ^(EXPR e0=expr { $exp = $e0.exp } )
    ;

expr returns [exp]
    :   ^(ASSIGN left=expr right=expr) { self.onAssign("=", left, right) }
    |   ^(PLUS_ASSIGN left=expr right=expr) { $exp = "\%s += \%s" \% ($left.exp, $right.exp) }
    |   ^(MINUS_ASSIGN expr expr)
    |   ^(STAR_ASSIGN expr expr)
    |   ^(DIV_ASSIGN expr expr)
    |   ^(AND_ASSIGN expr expr)
    |   ^(OR_ASSIGN expr expr)
    |   ^(XOR_ASSIGN expr expr)
    |   ^(MOD_ASSIGN expr expr)
    |   ^(BIT_SHIFT_RIGHT_ASSIGN expr expr)
    |   ^(SHIFT_RIGHT_ASSIGN left=expr right=expr) { self.onAssign(">>=", left, right) }
    |   ^(SHIFT_LEFT_ASSIGN left=expr right=expr) { self.onAssign("<<=", left, right) }
    |   ^(QUESTION expr expr expr)
    |   ^(LOGICAL_OR expr expr)
    |   ^(LOGICAL_AND expr expr)
    |   ^(OR expr expr)
    |   ^(XOR expr expr)
    |   ^(AND expr expr)
    |   ^(EQUAL left=expr right=expr)  { $exp = ("\%s == \%s" \% (left, right)) }
    |   ^(NOT_EQUAL expr expr)
    |   ^(INSTANCEOF expr type)
    |   ^(LESS_OR_EQUAL left=expr right=expr) { $exp = ("\%s <= \%s" \% (left, right)) }
    |   ^(GREATER_OR_EQUAL expr expr)
    |   ^(BIT_SHIFT_RIGHT expr expr)
    |   ^(SHIFT_RIGHT left=expr right=expr) { self.onAssign(">>", left, right) }
    |   ^(GREATER_THAN left=expr right=expr) { $exp = ("\%s > \%s" \% (left, right)) }
    |   ^(SHIFT_LEFT left=expr right=expr) { self.onAssign("<<", left, right) }
    |   ^(LESS_THAN left=expr right=expr) { $exp = ("\%s < \%s" \% (left, right)) }
    |   ^(PLUS left=expr right=expr) { $exp = ("\%s + \%s" \% (left, right)) }
    |   ^(MINUS expr expr)
    |   ^(STAR left=expr right=expr) { $exp = ("\%s * \%s" \% (left, right)) }
    |   ^(DIV expr expr)
    |   ^(MOD expr expr)
    |   ^(UNARY_PLUS expr)
    |   ^(UNARY_MINUS expr)
    |   ^(PRE_INC left=expr) { $exp = "\%s += 1" \% ($left.exp, ) }
    |   ^(PRE_DEC expr)
    |   ^(POST_INC left=expr) { $exp = "\%s += 1" \% ($left.exp, ) }
    |   ^(POST_DEC left=expr)  { $exp = "\%s -= 1" \% ($left.exp, ) }
    |   ^(NOT right=expr)
    |   ^(LOGICAL_NOT right=expr) { $exp = ("not \%s" \% (right.exp, )) }
    |   ^(CAST_EXPR type expr)
    |   p0=primaryExpression { $exp = $p0.exp }
    ;

primaryExpression returns [exp]
    @init { $exp = "" }
    :   ^(  DOT
            (   p0=primaryExpression { $exp += $p0.exp + "." }
                (   i0=IDENT { $exp += self.altName($i0.text) }
                |   THIS
                |   SUPER
                |   innerNewExpression
                |   CLASS
                )
            |   primitiveType CLASS
            |   VOID CLASS
            )
        )
    |   parenthesizedExpression { $exp = $parenthesizedExpression.exp }
    |   IDENT { $exp = self.altName($IDENT.text) }
    |   ^(METHOD_CALL p0=primaryExpression genericTypeArgumentList? a0=arguments
         { $exp = self.makeMethodExpr($p0.exp, $a0.args) }
        )
    |   explicitConstructorCall
    |   ^(ARRAY_ELEMENT_ACCESS p0=primaryExpression e0=expression
            { $exp = self.makeArrayAccess($p0.exp, $e0.exp) }
        )
    |   literal { $exp = $literal.value }
    |   newExpression { $exp = $newExpression.exp }
    |   THIS
    |   arrayTypeDeclarator
    |   SUPER
    ;

explicitConstructorCall
    :   ^(THIS_CONSTRUCTOR_CALL genericTypeArgumentList? arguments)
    |   ^(SUPER_CONSTRUCTOR_CALL primaryExpression? genericTypeArgumentList? arguments)
    ;

arrayTypeDeclarator
    :   ^(ARRAY_DECLARATOR (arrayTypeDeclarator | qualifiedIdentifier | primitiveType))
    ;

newExpression returns [exp]
    :   ^(  STATIC_ARRAY_CREATOR
            (   t0=primitiveType newArrayConstruction
            |   genericTypeArgumentList? q0=qualifiedTypeIdent newArrayConstruction
            )
            { $exp = ($q0.text, "") }
        )
    |   ^(CLASS_CONSTRUCTOR_CALL genericTypeArgumentList? q1=qualifiedTypeIdent
          a1=arguments classTopLevelScope?
          { $exp = self.makeMethodExpr($q1.text, $a1.args) }
        )
    ;

innerNewExpression // something like 'InnerType innerType = outer.new InnerType();'
    :   ^(CLASS_CONSTRUCTOR_CALL genericTypeArgumentList? IDENT arguments classTopLevelScope?)
    ;

newArrayConstruction
    :   arrayDeclaratorList arrayInitializer
    |   expression+ arrayDeclaratorList?
    ;

arguments returns [args] @init { args = [] }
    :   ^(ARGUMENT_LIST (ex0=expression { args.append($ex0.exp) })*)
    ;

literal returns [value]
    :   HEX_LITERAL { $value = $text }
    |   OCTAL_LITERAL { $value = $text }
    |   d0=DECIMAL_LITERAL { $value = self.fixFloatLiteral($d0.text) }
    |   f0=FLOATING_POINT_LITERAL { $value = self.fixFloatLiteral($f0.text) }
    |   CHARACTER_LITERAL { $value = $text }
    |   STRING_LITERAL { $value = $text }
    |   TRUE { $value = 'True' }
    |   FALSE { $value = 'False' }
    |   NULL { $value = 'None' }
    ;
