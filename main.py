from imaplib import ParseFlags
from constants import EOF
from emit import Emitter
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
    emitter = Emitter("out.c")
    parser = Parser(lexer, emitter)

    parser.program()
    emitter.write_file()
    print("Parsing Complete")


if __name__ == "__main__":
    main()
