#!/usr/bin/env python3
"""
Triton Debugger
Interactive debugger for Triton programs
"""

import cmd
import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class BreakPoint:
    """Represents a breakpoint"""
    address: int
    enabled: bool
    hit_count: int = 0

class TritonDebugger(cmd.Cmd):
    """Interactive debugger for Triton"""
    
    intro = """
    ╔═════════════════════════════════════════╗
    ║     TRITON DEBUGGER v1.0-alpha         ║
    ║  Interactive Ternary Architecture      ║
    ║     Debugger & Emulator                ║
    ╚═════════════════════════════════════════╝
    
    Type 'help' for available commands.
    """
    
    prompt = "(triton) "
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.memory: Dict[int, int] = {}
        self.registers: Dict[str, int] = {
            f'r{i}': 0 for i in range(32)
        }
        self.registers.update({
            'sp': 0xFFFF0000,
            'fp': 0xFFFF0000,
            'lr': 0,
            'pc': 0,
            'status': 0
        })
        self.breakpoints: Dict[int, BreakPoint] = {}
        self.program_counter = 0
        self.halt_flag = False
    
    def do_run(self, arg):
        """Run the program"""
        print("Starting program execution...")
        self.running = True
        # TODO: Implement actual program execution
        print("Program would execute here")
    
    def do_step(self, arg):
        """Execute one instruction"""
        if not self.running:
            print("Program not loaded. Use 'load' to load a program.")
            return
        print(f"Executing instruction at PC: {hex(self.program_counter)}")
        self.program_counter += 1
    
    def do_continue(self, arg):
        """Continue execution"""
        if not self.running:
            print("Program not running")
            return
        print("Continuing execution...")
        # TODO: Implement actual execution continuation
    
    def do_break(self, arg):
        """Set a breakpoint
        Usage: break <address> or break <label>
        """
        if not arg:
            print("Usage: break <address>")
            return
        
        try:
            if arg.startswith('0x'):
                address = int(arg, 16)
            else:
                address = int(arg)
            
            if address not in self.breakpoints:
                self.breakpoints[address] = BreakPoint(address, True)
                print(f"Breakpoint set at {hex(address)}")
            else:
                self.breakpoints[address].enabled = True
                print(f"Breakpoint enabled at {hex(address)}")
        except ValueError:
            print(f"Invalid address: {arg}")
    
    def do_delete(self, arg):
        """Delete a breakpoint
        Usage: delete <breakpoint_id> or delete all
        """
        if arg == 'all':
            self.breakpoints.clear()
            print("All breakpoints deleted")
        else:
            try:
                address = int(arg, 16) if arg.startswith('0x') else int(arg)
                if address in self.breakpoints:
                    del self.breakpoints[address]
                    print(f"Breakpoint deleted at {hex(address)}")
            except ValueError:
                print(f"Invalid address: {arg}")
    
    def do_info(self, arg):
        """Display information
        Usage: info registers, info breakpoints, info memory
        """
        if arg == 'registers':
            print("\n=== Registers ===")
            for reg_name, value in sorted(self.registers.items()):
                print(f"  {reg_name:6s} = {hex(value)}")
        
        elif arg == 'breakpoints':
            if not self.breakpoints:
                print("No breakpoints set")
            else:
                print("\n=== Breakpoints ===")
                for addr, bp in sorted(self.breakpoints.items()):
                    status = "Enabled" if bp.enabled else "Disabled"
                    print(f"  {hex(addr):10s} {status:8s} (hit {bp.hit_count} times)")
        
        elif arg == 'memory':
            if not self.memory:
                print("Memory is empty")
            else:
                print("\n=== Memory ===")
                for addr, value in sorted(self.memory.items())[:10]:
                    print(f"  {hex(addr):10s}: {hex(value)}")
                if len(self.memory) > 10:
                    print(f"  ... and {len(self.memory) - 10} more entries")
        
        else:
            print("Usage: info registers|breakpoints|memory")
    
    def do_register(self, arg):
        """View or set a register
        Usage: register <name> [value]
        """
        parts = arg.split()
        if not parts:
            print("Usage: register <name> [value]")
            return
        
        reg_name = parts[0].lower()
        
        if reg_name not in self.registers:
            print(f"Invalid register: {reg_name}")
            return
        
        if len(parts) > 1:
            try:
                value = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])
                self.registers[reg_name] = value
                print(f"Set {reg_name} = {hex(value)}")
            except ValueError:
                print(f"Invalid value: {parts[1]}")
        else:
            print(f"{reg_name} = {hex(self.registers[reg_name])}")
    
    def do_memory(self, arg):
        """Read or write memory
        Usage: memory read <address> [count]
               memory write <address> <value>
        """
        parts = arg.split()
        
        if not parts:
            print("Usage: memory read|write <address> [count/value]")
            return
        
        command = parts[0].lower()
        
        if command == 'read':
            if len(parts) < 2:
                print("Usage: memory read <address> [count]")
                return
            
            try:
                address = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])
                count = int(parts[2]) if len(parts) > 2 else 1
                
                print(f"\nMemory at {hex(address)}:")
                for i in range(count):
                    addr = address + i
                    value = self.memory.get(addr, 0)
                    print(f"  {hex(addr):10s}: {hex(value)}")
            except ValueError as e:
                print(f"Error: {e}")
        
        elif command == 'write':
            if len(parts) < 3:
                print("Usage: memory write <address> <value>")
                return
            
            try:
                address = int(parts[1], 16) if parts[1].startswith('0x') else int(parts[1])
                value = int(parts[2], 16) if parts[2].startswith('0x') else int(parts[2])
                
                self.memory[address] = value
                print(f"Wrote {hex(value)} to {hex(address)}")
            except ValueError as e:
                print(f"Error: {e}")
        
        else:
            print(f"Unknown command: memory {command}")
    
    def do_load(self, arg):
        """Load a program
        Usage: load <filename>
        """
        if not arg:
            print("Usage: load <filename>")
            return
        
        print(f"Loading program: {arg}")
        # TODO: Implement program loading
        self.running = True
        self.program_counter = 0
    
    def do_disassemble(self, arg):
        """Disassemble memory
        Usage: disassemble <address> [count]
        """
        if not arg:
            print("Usage: disassemble <address> [count]")
            return
        
        parts = arg.split()
        try:
            address = int(parts[0], 16) if parts[0].startswith('0x') else int(parts[0])
            count = int(parts[1]) if len(parts) > 1 else 10
            
            print(f"\nDisassembly at {hex(address)}:")
            for i in range(count):
                print(f"  {hex(address + i*4):10s}: [instruction would be here]")
        except ValueError as e:
            print(f"Error: {e}")
    
    def do_stack(self, arg):
        """Display stack contents"""
        sp = self.registers['sp']
        print(f"\nStack Pointer: {hex(sp)}")
        print("Stack Contents:")
        for i in range(5):
            addr = sp + i * 4
            value = self.memory.get(addr, 0)
            print(f"  {hex(addr):10s}: {hex(value)}")
    
    def do_help(self, arg):
        """Show help"""
        if arg:
            super().do_help(arg)
        else:
            print("""
            Available Commands:
            ===================
            
            Execution:
              run             - Start program execution
              step            - Execute one instruction
              continue        - Continue execution
              halt            - Halt program
            
            Breakpoints:
              break <addr>    - Set breakpoint
              delete <addr>   - Delete breakpoint
            
            Inspection:
              info            - Show system information
              register        - View/set registers
              memory          - Read/write memory
              stack           - Show stack contents
              disassemble     - Disassemble code
            
            File I/O:
              load <file>     - Load program
              save <file>     - Save state
            
            Other:
              help            - Show this help
              quit/exit       - Exit debugger
            """)
    
    def do_quit(self, arg):
        """Exit the debugger"""
        print("\nExiting Triton Debugger...")
        return True
    
    def do_exit(self, arg):
        """Exit the debugger"""
        return self.do_quit(arg)
    
    def emptyline(self):
        """Handle empty input"""
        pass


if __name__ == '__main__':
    debugger = TritonDebugger()
    debugger.cmdloop()
