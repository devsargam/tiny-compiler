from imaplib import ParseFlags
from constants import EOF
from lex import Lexer
import sys

from parse import Parser


def main():
    print("smol compiler")

    if len(sys.argv) != 2:
        sys.exit("Error: Compiler needs source file as argument")

    with open(sys.argv[1], "r") as file:
        source = file.read()

    lexer = Lexer(source)
    parser = Parser(lexer)

    parser.program()
    print("Parsing Complete")


if __name__ == "__main__":
    main()
