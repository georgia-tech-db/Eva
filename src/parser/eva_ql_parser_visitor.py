# coding=utf-8
# Copyright 2018-2020 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from antlr4 import TerminalNode
from src.expression.abstract_expression import (AbstractExpression,
                                                ExpressionType)
from src.expression.comparison_expression import ComparisonExpression
from src.expression.constant_value_expression import ConstantValueExpression
from src.expression.logical_expression import LogicalExpression
from src.expression.tuple_value_expression import TupleValueExpression
from src.parser.select_statement import SelectStatement
from src.parser.evaql.evaql_parser import evaql_parser
from src.parser.evaql.evaql_parserVisitor import evaql_parserVisitor
from src.parser.table_ref import TableRef, TableInfo
import warnings


class EvaParserVisitor(evaql_parserVisitor):
    # Visit a parse tree produced by evaql_parser#root.
    def visitRoot(self, ctx: evaql_parser.RootContext):
        for child in ctx.children:
            if child is not TerminalNode:
                return self.visit(child)

    # Visit a parse tree produced by evaql_parser#sqlStatements.
    def visitSqlStatements(self, ctx: evaql_parser.SqlStatementsContext):
        eva_statements = []
        for child in ctx.children:
            stmt = self.visit(child)
            if stmt is not None:
                eva_statements.append(stmt)

        return eva_statements

    # Visit a parse tree produced by evaql_parser#simpleSelect.
    def visitSimpleSelect(self, ctx: evaql_parser.SimpleSelectContext):
        select_stm = self.visitChildren(ctx)
        return select_stm

    # Visit a parse tree produced by evaql_parser#tableSources.
    def visitTableSources(self, ctx: evaql_parser.TableSourcesContext):
        table_list = []
        for child in ctx.children:
            table = self.visit(child)
            if table is not None:
                table_list.append(table)
        return table_list

    # Visit a parse tree produced by evaql_parser#querySpecification.
    def visitQuerySpecification(
            self, ctx: evaql_parser.QuerySpecificationContext):
        target_list = None
        from_clause = None
        where_clause = None
        # first child will be a SELECT terminal token
        for child in ctx.children[1:]:
            try:
                rule_idx = child.getRuleIndex()
                if rule_idx == evaql_parser.RULE_selectElements:
                    target_list = self.visit(child)

                elif rule_idx == evaql_parser.RULE_fromClause:
                    clause = self.visit(child)
                    from_clause = clause.get('from', None)
                    where_clause = clause.get('where', None)
            except BaseException:
                # stop parsing something bad happened
                return None
        # we don't support multiple table sources
        if from_clause is not None:
            from_clause = from_clause[0]
        select_stmt = SelectStatement(target_list, from_clause, where_clause)
        return select_stmt

    # Visit a parse tree produced by evaql_parser#selectElements.
    def visitSelectElements(self, ctx: evaql_parser.SelectElementsContext):
        select_list = []
        for child in ctx.children:
            element = self.visit(child)
            if element is not None:
                select_list.append(element)

        return select_list

    # Visit a parse tree produced by evaql_parser#fromClause.
    def visitFromClause(self, ctx: evaql_parser.FromClauseContext):
        from_table = None
        where_clause = None

        if ctx.tableSources():
            from_table = self.visit(ctx.tableSources())
        if ctx.whereExpr is not None:
            where_clause = self.visit(ctx.whereExpr)

        return {"from": from_table, "where": where_clause}

    # Visit a parse tree produced by evaql_parser#tableName.
    def visitTableName(self, ctx: evaql_parser.TableNameContext):
        table_name = self.visit(ctx.fullId())
        # assuming we get just table name
        # todo
        # handle database name and schema names
        if table_name is not None:
            table_info = TableInfo(table_name=table_name)
            return TableRef(table_info)
        else:
            warnings.warn("Invalid from table", SyntaxWarning)

    # Visit a parse tree produced by evaql_parser#fullColumnName.
    def visitFullColumnName(self, ctx: evaql_parser.FullColumnNameContext):
        # dotted id not supported yet
        column_name = self.visit(ctx.uid())
        if column_name is not None:
            return TupleValueExpression(col_name=column_name)
        else:
            warnings.warn("Column Name Missing", SyntaxWarning)

    # Visit a parse tree produced by evaql_parser#simpleId.
    def visitSimpleId(self, ctx: evaql_parser.SimpleIdContext):
        # todo handle children, right now assuming TupleValueExpr
        return ctx.getText()
        # return self.visitChildren(ctx)

    # Visit a parse tree produced by evaql_parser#stringLiteral.
    def visitStringLiteral(self, ctx: evaql_parser.StringLiteralContext):
        if ctx.STRING_LITERAL() is not None:
            return ConstantValueExpression(ctx.getText())
        # todo handle other types
        return self.visitChildren(ctx)

    # Visit a parse tree produced by evaql_parser#constant.
    def visitConstant(self, ctx: evaql_parser.ConstantContext):
        if ctx.REAL_LITERAL() is not None:
            return ConstantValueExpression(float(ctx.getText()))

        return self.visitChildren(ctx)

    # Visit a parse tree produced by evaql_parser#logicalExpression.
    def visitLogicalExpression(
            self, ctx: evaql_parser.LogicalExpressionContext):
        if len(ctx.children) < 3:
            # error scenario, should have 3 children
            return None
        left = self.visit(ctx.getChild(0))
        op = self.visit(ctx.getChild(1))
        right = self.visit(ctx.getChild(2))
        return LogicalExpression(op, left, right)

    # Visit a parse tree produced by evaql_parser#binaryComparasionPredicate.
    def visitBinaryComparasionPredicate(
            self, ctx: evaql_parser.BinaryComparisonPredicateContext):
        left = self.visit(ctx.left)
        right = self.visit(ctx.right)
        op = self.visit(ctx.comparisonOperator())
        return ComparisonExpression(op, left, right)

    # Visit a parse tree produced by evaql_parser#nestedExpressionAtom.
    def visitNestedExpressionAtom(
            self, ctx: evaql_parser.NestedExpressionAtomContext):
        # ToDo Can there be >1 expression in this case
        expr = ctx.expression(0)
        return self.visit(expr)

    # Visit a parse tree produced by evaql_parser#comparisonOperator.
    def visitComparisonOperator(
            self, ctx: evaql_parser.ComparisonOperatorContext):
        op = ctx.getText()
        if op == '=':
            return ExpressionType.COMPARE_EQUAL
        elif op == '<':
            return ExpressionType.COMPARE_LESSER
        elif op == '>':
            return ExpressionType.COMPARE_GREATER
        else:
            return ExpressionType.INVALID

    # Visit a parse tree produced by evaql_parser#logicalOperator.
    def visitLogicalOperator(self, ctx: evaql_parser.LogicalOperatorContext):
        op = ctx.getText()

        if op == 'OR':
            return ExpressionType.LOGICAL_OR
        elif op == 'AND':
            return ExpressionType.LOGICAL_AND
        else:
            return ExpressionType.INVALID
