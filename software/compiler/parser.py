#!/usr/bin/env python3
"""
Triton Assembler Parser
Parses tokenized Triton assembly code into an AST
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from lexer import Token, TokenType, TritonLexer

@dataclass
class Instruction:
    """Represents an instruction"""
    mnemonic: str
    operands: List[str]
    line: int

@dataclass
class Label:
    """Represents a label"""
    name: str
    line: int

@dataclass
class Directive:
    """Represents an assembler directive"""
    name: str
    args: List[str]
    line: int

@dataclass
class Program:
    """Represents a complete program"""
    sections: Dict[str, List[Any]]  # .text, .data, etc.
    symbols: Dict[str, int]  # Symbol table

class TritonParser:
    """Parser for Triton assembly language"""
    
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.position = 0
        self.program = Program(sections={}, symbols={})
    
    def error(self, message: str) -> None:
        """Report parse error"""
        token = self.peek()
        print(f"Parse Error at line {token.line}: {message}")
        raise SyntaxError(f"{message} at line {token.line}")
    
    def peek(self, offset: int = 0) -> Token:
        """Peek at token without consuming"""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]  # Return EOF
    
    def advance(self) -> Token:
        """Consume and return next token"""
        token = self.peek()
        if token.type != TokenType.EOF:
            self.position += 1
        return token
    
    def expect(self, token_type: TokenType) -> Token:
        """Expect and consume a specific token type"""
        token = self.peek()
        if token.type != token_type:
            self.error(f"Expected {token_type.name}, got {token.type.name}")
        return self.advance()
    
    def skip_newlines(self) -> None:
        """Skip newline tokens"""
        while self.peek().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        """Parse the token stream"""
        self.program.sections['.text'] = []
        self.program.sections['.data'] = []
        current_section = '.text'
        
        while self.peek().type != TokenType.EOF:
            self.skip_newlines()
            
            token = self.peek()
            
            if token.type == TokenType.DIRECTIVE:
                directive = self.parse_directive()
                if directive.name in ['.text', '.data', '.section']:
                    if directive.name == '.section':
                        current_section = directive.args[0]
                    else:
                        current_section = directive.name
                    
                    if current_section not in self.program.sections:
                        self.program.sections[current_section] = []
                else:
                    if current_section not in self.program.sections:
                        self.program.sections[current_section] = []
                    self.program.sections[current_section].append(directive)
            
            elif token.type == TokenType.IDENTIFIER and self.peek(1).type == TokenType.COLON:
                label = self.parse_label()
                if current_section not in self.program.sections:
                    self.program.sections[current_section] = []
                self.program.sections[current_section].append(label)
                self.program.symbols[label.name] = label.line
            
            elif token.type == TokenType.INSTRUCTION:
                instruction = self.parse_instruction()
                if current_section not in self.program.sections:
                    self.program.sections[current_section] = []
                self.program.sections[current_section].append(instruction)
            
            else:
                self.skip_newlines()
                if self.peek().type != TokenType.EOF:
                    self.error(f"Unexpected token: {token.type.name}")
        
        return self.program
    
    def parse_directive(self) -> Directive:
        """Parse an assembler directive"""
        token = self.expect(TokenType.DIRECTIVE)
        args = []
        
        # Parse directive arguments
        while self.peek().type not in [TokenType.NEWLINE, TokenType.EOF]:
            if self.peek().type == TokenType.IDENTIFIER:
                args.append(self.advance().value)
            elif self.peek().type == TokenType.NUMBER:
                args.append(self.advance().value)
            elif self.peek().type == TokenType.STRING:
                args.append(self.advance().value)
            elif self.peek().type == TokenType.COMMA:
                self.advance()  # Skip comma
            else:
                break
        
        return Directive(token.value, args, token.line)
    
    def parse_label(self) -> Label:
        """Parse a label"""
        name_token = self.expect(TokenType.IDENTIFIER)
        self.expect(TokenType.COLON)
        return Label(name_token.value, name_token.line)
    
    def parse_instruction(self) -> Instruction:
        """Parse an instruction"""
        mnemonic_token = self.expect(TokenType.INSTRUCTION)
        operands = []
        
        # Parse operands
        while self.peek().type not in [TokenType.NEWLINE, TokenType.EOF, TokenType.SEMICOLON]:
            if self.peek().type == TokenType.REGISTER:
                operands.append(self.advance().value)
            elif self.peek().type == TokenType.NUMBER:
                operands.append(self.advance().value)
            elif self.peek().type == TokenType.IDENTIFIER:
                operands.append(self.advance().value)
            elif self.peek().type == TokenType.LPAREN:
                operands.append(self.advance().value)  # (
                if self.peek().type == TokenType.REGISTER:
                    operands[-1] += self.advance().value
                self.expect(TokenType.RPAREN)
                operands[-1] += ')'
            elif self.peek().type == TokenType.COMMA:
                self.advance()  # Skip comma
            elif self.peek().type == TokenType.PLUS or self.peek().type == TokenType.MINUS:
                operands.append(self.advance().value)
            else:
                break
        
        return Instruction(mnemonic_token.value, operands, mnemonic_token.line)


if __name__ == "__main__":
    test_code = """
    .section .text
    .global main
    
    main:
        ADDI r1, r0, 10
        ADDI r2, r0, 20
        ADD r3, r1, r2
        HALT
    """
    
    lexer = TritonLexer(test_code)
    tokens = lexer.tokenize()
    
    parser = TritonParser(tokens)
    program = parser.parse()
    
    print("Parsed Program:")
    for section, items in program.sections.items():
        print(f"\nSection: {section}")
        for item in items:
            print(f"  {item}")
    
    print(f"\nSymbols: {program.symbols}")
