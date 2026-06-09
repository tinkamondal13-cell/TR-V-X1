#!/usr/bin/env python3
"""
Triton Assembler Lexer
Tokenizes Triton assembly source code
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional, Tuple

class TokenType(Enum):
    """Token types for Triton assembly language"""
    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    FLOAT = auto()
    
    # Keywords
    INSTRUCTION = auto()
    DIRECTIVE = auto()
    REGISTER = auto()
    
    # Operators and Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    COMMA = auto()
    COLON = auto()
    HASH = auto()
    SEMICOLON = auto()
    DOT = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    
    # End of file
    EOF = auto()
    COMMENT = auto()
    NEWLINE = auto()

@dataclass
class Token:
    """Represents a token in the assembly source"""
    type: TokenType
    value: str
    line: int
    column: int

class TritonLexer:
    """Lexer for Triton assembly language"""
    
    # Triton instruction set
    INSTRUCTIONS = {
        'ADD', 'SUB', 'MUL', 'DIV', 'MOD',
        'AND', 'OR', 'XOR', 'NOT',
        'SHL', 'SHR', 'ROL', 'ROR',
        'LW', 'LB', 'SW', 'SB',
        'BEQ', 'BNE', 'BLT', 'BGE', 'BLE', 'BGT',
        'J', 'JAL', 'RET', 'CALL',
        'ADDI', 'SUBI', 'MULI', 'DIVI',
        'ANDI', 'ORI', 'XORI',
        'NOP', 'HALT', 'BREAK',
        'MOV', 'LA', 'LI',
        'FENCE', 'SYSCALL'
    }
    
    # Directives
    DIRECTIVES = {
        '.section', '.global', '.local', '.align',
        '.word', '.byte', '.ascii', '.float',
        '.org', '.include', '.define'
    }
    
    # Register names
    REGISTERS = {
        f'r{i}' for i in range(32)
    } | {'sp', 'fp', 'lr', 'pc', 'status'}
    
    def __init__(self, source: str):
        """Initialize lexer with source code"""
        self.source = source
        self.position = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
    
    def error(self, message: str) -> None:
        """Report lexical error"""
        print(f"Lexer Error at line {self.line}, column {self.column}: {message}")
        raise SyntaxError(f"{message} at {self.line}:{self.column}")
    
    def peek(self, offset: int = 0) -> Optional[str]:
        """Peek at character without consuming"""
        pos = self.position + offset
        if pos < len(self.source):
            return self.source[pos]
        return None
    
    def advance(self) -> Optional[str]:
        """Consume and return next character"""
        if self.position >= len(self.source):
            return None
        
        char = self.source[self.position]
        self.position += 1
        
        if char == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        
        return char
    
    def skip_whitespace(self) -> None:
        """Skip whitespace characters"""
        while self.peek() and self.peek() in ' \t\r':
            self.advance()
    
    def skip_comment(self) -> None:
        """Skip comment lines"""
        if self.peek() == ';':
            while self.peek() and self.peek() != '\n':
                self.advance()
    
    def read_string(self, quote: str) -> str:
        """Read string literal"""
        result = ""
        self.advance()  # Skip opening quote
        
        while self.peek() and self.peek() != quote:
            if self.peek() == '\\':
                self.advance()
                next_char = self.advance()
                if next_char == 'n':
                    result += '\n'
                elif next_char == 't':
                    result += '\t'
                elif next_char == 'r':
                    result += '\r'
                elif next_char == '\\':
                    result += '\\'
                else:
                    result += next_char
            else:
                result += self.advance()
        
        if self.peek() == quote:
            self.advance()  # Skip closing quote
        else:
            self.error(f"Unterminated string literal")
        
        return result
    
    def read_identifier(self) -> str:
        """Read identifier or keyword"""
        result = ""
        while self.peek() and (self.peek().isalnum() or self.peek() in '_'):
            result += self.advance()
        return result
    
    def read_number(self) -> Tuple[str, TokenType]:
        """Read numeric literal (decimal, hex, or binary)"""
        result = ""
        token_type = TokenType.NUMBER
        
        # Handle hex (0x) or binary (0b)
        if self.peek() == '0':
            result += self.advance()
            if self.peek() and self.peek().lower() == 'x':
                result += self.advance()
                while self.peek() and self.peek() in '0123456789abcdefABCDEF':
                    result += self.advance()
            elif self.peek() and self.peek().lower() == 'b':
                result += self.advance()
                while self.peek() and self.peek() in '01':
                    result += self.advance()
            else:
                while self.peek() and self.peek().isdigit():
                    result += self.advance()
        else:
            while self.peek() and self.peek().isdigit():
                result += self.advance()
        
        # Check for float
        if self.peek() == '.':
            token_type = TokenType.FLOAT
            result += self.advance()
            while self.peek() and self.peek().isdigit():
                result += self.advance()
        
        return result, token_type
    
    def tokenize(self) -> List[Token]:
        """Tokenize the entire source"""
        while self.position < len(self.source):
            self.skip_whitespace()
            
            if self.position >= len(self.source):
                break
            
            # Comments
            if self.peek() == ';':
                self.skip_comment()
                continue
            
            # Newlines
            if self.peek() == '\n':
                self.advance()
                self.tokens.append(Token(TokenType.NEWLINE, '\n', self.line, self.column))
                continue
            
            line, col = self.line, self.column
            char = self.peek()
            
            # String literals
            if char in '"\'':
                value = self.read_string(char)
                self.tokens.append(Token(TokenType.STRING, value, line, col))
            
            # Identifiers and keywords
            elif char.isalpha() or char == '_':
                identifier = self.read_identifier()
                
                if identifier.upper() in self.INSTRUCTIONS:
                    self.tokens.append(Token(TokenType.INSTRUCTION, identifier.upper(), line, col))
                elif identifier in self.DIRECTIVES:
                    self.tokens.append(Token(TokenType.DIRECTIVE, identifier, line, col))
                elif identifier.lower() in self.REGISTERS:
                    self.tokens.append(Token(TokenType.REGISTER, identifier.lower(), line, col))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier, line, col))
            
            # Numbers
            elif char.isdigit():
                value, token_type = self.read_number()
                self.tokens.append(Token(token_type, value, line, col))
            
            # Operators and punctuation
            elif char == '(':
                self.advance()
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
            elif char == ')':
                self.advance()
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
            elif char == '{':
                self.advance()
                self.tokens.append(Token(TokenType.LBRACE, '{', line, col))
            elif char == '}':
                self.advance()
                self.tokens.append(Token(TokenType.RBRACE, '}', line, col))
            elif char == ',':
                self.advance()
                self.tokens.append(Token(TokenType.COMMA, ',', line, col))
            elif char == ':':
                self.advance()
                self.tokens.append(Token(TokenType.COLON, ':', line, col))
            elif char == '#':
                self.advance()
                self.tokens.append(Token(TokenType.HASH, '#', line, col))
            elif char == ';':
                self.advance()
                self.tokens.append(Token(TokenType.SEMICOLON, ';', line, col))
            elif char == '.':
                self.advance()
                self.tokens.append(Token(TokenType.DOT, '.', line, col))
            elif char == '+':
                self.advance()
                self.tokens.append(Token(TokenType.PLUS, '+', line, col))
            elif char == '-':
                self.advance()
                self.tokens.append(Token(TokenType.MINUS, '-', line, col))
            elif char == '*':
                self.advance()
                self.tokens.append(Token(TokenType.MULTIPLY, '*', line, col))
            elif char == '/':
                self.advance()
                self.tokens.append(Token(TokenType.DIVIDE, '/', line, col))
            else:
                self.error(f"Unexpected character: '{char}'")
        
        # Add EOF token
        self.tokens.append(Token(TokenType.EOF, '', self.line, self.column))
        return self.tokens


if __name__ == "__main__":
    # Test lexer
    test_code = """
    ; Triton Assembly Test
    .section .text
    .global main
    
    main:
        ADDI r1, r0, 10      ; r1 = 10
        ADDI r2, r0, 20      ; r2 = 20
        ADD r3, r1, r2       ; r3 = r1 + r2
        HALT
    """
    
    lexer = TritonLexer(test_code)
    tokens = lexer.tokenize()
    
    for token in tokens:
        print(f"{token.type.name:15} {token.value:20} Line {token.line:3} Col {token.column:3}")
