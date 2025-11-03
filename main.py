from constants import EOF
from lex import Lexer


def main():
    source = '+ -*/ = == != <= >= "Sargam Poudel" < > 123 123.45   \n'
    source = "+-123 9.8654*/"
    source = "F+-123 foo*THEN/"
    lexer = Lexer(source)

    token = lexer.get_token()

    while lexer.peek() != EOF:
        print(token.kind)
        token = lexer.get_token()


if __name__ == "__main__":
    main()
