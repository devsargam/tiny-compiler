import sys
from emit import Emitter
from lex import Lexer, Token, TokenType


class Parser:
    def __init__(self, lexer: Lexer, emitter: Emitter) -> None:
        self.lexer: Lexer = lexer
        self.emitter: Emitter = emitter

        self.symbols = set()
        self.labels_declared = set()
        self.labels_gotoed = set()

        self.cur_token: Token = self.lexer.get_token()
        self.peek_token: Token = self.lexer.get_token()

    def check_token(self, kind):
        return kind == self.cur_token.kind

    def check_peek(self, kind: str):
        return kind == self.peek_token.kind

    def match(self, kind):
        if not self.check_token(kind):
            self.abort(f"Expected {kind}, got {self.cur_token.kind.name}")
        self.next_token()

    def next_token(self):
        self.cur_token = self.peek_token
        self.peek_token = self.lexer.get_token()

    def abort(self, message: str):
        sys.exit(f"Error. {message}")

    # program ::= {statement}
    def program(self):
        print("PROGRAM")
        self.emitter.header_line("#include <stdio.h>")
        self.emitter.header_line("int main(void) {")

        while self.check_token(TokenType.NEWLINE):
            self.next_token()

        while not self.check_token(TokenType.EOF):
            self.statement()

        self.emitter.emit_line("return 0;")
        self.emitter.emit_line("}")

        for label in self.labels_declared:
            if label not in self.labels_declared:
                self.abort(f"Attempting to GOTO to undeclared label: {label}")

    def statement(self):
        # Check the first token to see what kind of statmenet this is.

        # "PRINT" (expression | string)
        if self.check_token(TokenType.PRINT):
            print("STATEMENT-PRINT")
            self.next_token()

            if self.check_token(TokenType.STRING):
                self.next_token()
            else:
                self.expression()
        elif self.check_token(TokenType.IF):
            print("STATEMENT-IF")
            self.next_token()
            self.comparison()

            self.match(TokenType.THEN)
            self.nl()

            while not self.check_token(TokenType.ENDIF):
                self.statement()

            self.match(TokenType.ENDIF)
        elif self.check_token(TokenType.WHILE):
            print("STATEMENT-WHILE")
            self.next_token()
            self.comparison()

            self.match(TokenType.REPEAT)
            self.nl()

            while not self.check_token(TokenType.ENDWHILE):
                self.statement()

            self.match(TokenType.ENDWHILE)
        elif self.check_token(TokenType.LABEL):
            print("STATEMENT-LABEL")
            self.next_token()

            if self.cur_token.text in self.labels_declared:
                self.abort(f"Label already exists: {self.cur_token.text}")
            self.labels_declared.add(self.cur_token.text)

            self.match(TokenType.IDENT)

        elif self.check_token(TokenType.GOTO):
            print("STATEMENT-GOTO")
            self.next_token()
            self.labels_gotoed.add(self.cur_token.text)
            self.match(TokenType.IDENT)

        elif self.check_token(TokenType.LET):
            print("STATEMENT-LET")
            self.next_token()

            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)

            self.match(TokenType.IDENT)
            self.match(TokenType.EQ)

            self.expression()
        elif self.check_token(TokenType.INPUT):
            print("STATEMENT-INPUT")
            self.next_token()

            if self.cur_token.text not in self.symbols:
                self.symbols.add(self.cur_token.text)

            self.match(TokenType.IDENT)

        else:
            self.abort(
                f"Invalid statement at {self.cur_token.text} + ({self.cur_token.kind.name})"
            )

        self.nl()

    def comparison(self):
        print("COMPARISON")

        self.expression()

        if self.is_comparison_operator():
            self.next_token()
            self.expression()
        else:
            self.abort(f"Expected comparison operator at: {self.cur_token.text}")

    def is_comparison_operator(self):
        return (
            self.check_token(TokenType.GT)
            or self.check_token(TokenType.GTEQ)
            or self.check_token(TokenType.LT)
            or self.check_token(TokenType.LTEQ)
            or self.check_token(TokenType.EQEQ)
            or self.check_token(TokenType.NOTEQ)
        )

    def expression(self):
        print("EXPRESSION")

        self.term()

        while self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.next_token()
            self.term()

    def term(self):
        print("TERM")

        self.unary()

        while self.check_token(TokenType.ASTERISK) or self.check_token(TokenType.SLASH):
            self.next_token()
            self.unary()

    def unary(self):
        print("UNARY")

        if self.check_token(TokenType.PLUS) or self.check_token(TokenType.MINUS):
            self.next_token()

        self.primary()

    def primary(self):
        print(f"PRIMARY ({self.cur_token.text})")

        if self.check_token(TokenType.NUMBER):
            self.next_token()
        elif self.check_token(TokenType.IDENT):
            if self.cur_token.text not in self.symbols:
                self.abort(
                    f"Referencing variable before assignment: {self.cur_token.text}"
                )
            self.next_token()
        else:
            self.abort(f"Unexpected token at {self.cur_token.text}")

    def nl(self):
        print("NEWLINE")

        # Require at least one newline.
        self.match(TokenType.NEWLINE)
        # But we will allow extra newlines too, of course.
        while self.check_token(TokenType.NEWLINE):
            self.next_token()
