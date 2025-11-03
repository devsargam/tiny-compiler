import enum
import sys
from constants import EOF


class Lexer:
    def __init__(self, source: str):
        self.source: str = source + "\n"
        self.cur_char: str = ""
        self.cur_pos: int = -1
        self.next_char()

    def next_char(self):
        self.cur_pos += 1
        if self.cur_pos + 1 >= len(self.source):
            self.cur_char = EOF
        else:
            self.cur_char = self.source[self.cur_pos]

    def peek(self) -> str:
        if self.cur_pos + 1 >= len(self.source):
            return EOF
        else:
            return self.source[self.cur_pos + 1]

    def abort(self, message: str):
        sys.exit("Lexing error. " + message)

    def skip_whitespace(self):
        while self.cur_char == " " or self.cur_char == "\t" or self.cur_char == "\r":
            self.next_char()

    def skip_comment(self):
        if self.cur_char == "#":
            while self.cur_char != "\n":
                self.next_char()

    def get_token(self):
        self.skip_whitespace()
        self.skip_comment()
        token = None

        if self.cur_char == "+":
            token = Token(self.cur_char, TokenType.PLUS)
        elif self.cur_char == "-":
            token = Token(self.cur_char, TokenType.MINUS)
        elif self.cur_char == "*":
            token = Token(self.cur_char, TokenType.ASTERISK)
        elif self.cur_char == "/":
            token = Token(self.cur_char, TokenType.SLASH)
        elif self.cur_char == "\n":
            token = Token(self.cur_char, TokenType.NEWLINE)
        elif self.cur_char == "\0":
            token = Token(self.cur_char, TokenType.EOF)
        elif self.cur_char == "=":
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.EQEQ)
            else:
                token = Token(self.cur_char, TokenType.EQ)
        elif self.cur_char == ">":
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.GTEQ)
            else:
                token = Token(self.cur_char, TokenType.GT)

        elif self.cur_char == "<":
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.LTEQ)
            else:
                token = Token(self.cur_char, TokenType.LT)
        elif self.cur_char == "!":
            if self.peek() == "=":
                last_char = self.cur_char
                self.next_char()
                token = Token(last_char + self.cur_char, TokenType.NOTEQ)
            else:
                self.abort("Expected !=, got !" + self.peek())

        elif self.cur_char == '"':
            self.next_char()
            start_pos = self.cur_pos

            while self.cur_char != '"':
                if (
                    self.cur_char == "\r"
                    or self.cur_char == "\n"
                    or self.cur_char == "\t"
                    or self.cur_char == "\\"
                    or self.cur_char == "%"
                ):
                    self.abort("Illegal char in str")
                self.next_char()

            tok_text = self.source[start_pos : self.cur_pos]
            token = Token(tok_text, TokenType.STRING)

        elif self.cur_char.isdigit():
            start_pos = self.cur_pos
            while self.peek().isdigit():
                self.next_char()
            if self.peek() == ".":
                self.next_char()

                if not self.peek().isdigit():
                    self.abort("Illegal char in number")
                while self.peek().isdigit():
                    self.next_char()

            tok_text = self.source[start_pos : self.cur_pos + 1]
            token = Token(tok_text, TokenType.NUMBER)

        elif self.cur_char.isalpha():
            start_pos = self.cur_pos
            while self.peek().isalnum():
                self.next_char()

            tok_text = self.source[start_pos : self.cur_pos + 1]
            keyword = Token.checkIfKeyword(tok_text)

            if keyword is None:
                token = Token(tok_text, TokenType.IDENT)
            else:
                token = Token(tok_text, keyword)

        else:
            self.abort("Unknown token: " + self.cur_char)

        self.next_char()
        return token


class TokenType(enum.Enum):
    EOF = -1
    NEWLINE = 0
    NUMBER = 1
    IDENT = 2
    STRING = 3
    # Keywords.
    LABEL = 101
    GOTO = 102
    PRINT = 103
    INPUT = 104
    LET = 105
    IF = 106
    THEN = 107
    ENDIF = 108
    WHILE = 109
    REPEAT = 110
    ENDWHILE = 111
    # Operators.
    EQ = 201
    PLUS = 202
    MINUS = 203
    ASTERISK = 204
    SLASH = 205
    EQEQ = 206
    NOTEQ = 207
    LT = 208
    LTEQ = 209
    GT = 210
    GTEQ = 211


class Token:
    def __init__(self, token_text: str, token_kind: TokenType) -> None:
        self.text: str = token_text
        self.kind: TokenType = token_kind

    @staticmethod
    def checkIfKeyword(tokenText: str):
        for kind in TokenType:
            # Relies on all keyword enum values being 1XX.
            if kind.name == tokenText and kind.value >= 100 and kind.value < 200:
                return kind
        return None
