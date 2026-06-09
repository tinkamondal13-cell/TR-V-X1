#!/usr/bin/env python3
"""
Ternary Converter Utility
Convert between balanced ternary and decimal/binary representations
"""

class TernaryConverter:
    """Convert between balanced ternary and other representations"""
    
    @staticmethod
    def decimal_to_balanced_ternary(n: int, width: int = 32) -> str:
        """Convert decimal to balanced ternary
        
        Args:
            n: Decimal number to convert
            width: Number of trits in result
            
        Returns:
            String representation of balanced ternary (T=−1, 0, 1)
        """
        if n == 0:
            return '0' * width
        
        # Handle negative numbers
        negative = n < 0
        n = abs(n)
        
        # Convert to ternary
        trits = []
        while n > 0:
            remainder = n % 3
            n //= 3
            
            if remainder == 0:
                trits.append('0')
            elif remainder == 1:
                trits.append('1')
            else:  # remainder == 2
                trits.append('T')  # T represents -1
                n += 1  # Carry
        
        # Pad to width
        while len(trits) < width:
            trits.append('0')
        
        result = ''.join(reversed(trits[:width]))
        
        # Negate if needed
        if negative:
            result = TernaryConverter.negate_balanced_ternary(result)
        
        return result
    
    @staticmethod
    def balanced_ternary_to_decimal(bt: str) -> int:
        """Convert balanced ternary to decimal
        
        Args:
            bt: Balanced ternary string (T=−1, 0, 1)
            
        Returns:
            Decimal value
        """
        result = 0
        power = 1
        
        for trit in reversed(bt):
            if trit == '1':
                result += power
            elif trit == 'T':
                result -= power
            # '0' contributes nothing
            
            power *= 3
        
        return result
    
    @staticmethod
    def negate_balanced_ternary(bt: str) -> str:
        """Negate a balanced ternary number
        
        Args:
            bt: Balanced ternary string
            
        Returns:
            Negated balanced ternary
        """
        result = []
        for trit in bt:
            if trit == '1':
                result.append('T')
            elif trit == 'T':
                result.append('1')
            else:
                result.append('0')
        
        return ''.join(result)
    
    @staticmethod
    def decimal_to_hex_ternary(n: int, width: int = 8) -> str:
        """Convert decimal to packed hex ternary
        Each hex digit represents 2 trits
        
        Args:
            n: Decimal number
            width: Number of hex digits (each = 2 trits)
            
        Returns:
            Hex string representation
        """
        bt = TernaryConverter.decimal_to_balanced_ternary(n, width * 2)
        
        # Convert pairs of trits to hex
        hex_str = '0x'
        for i in range(0, len(bt), 2):
            pair = bt[i:i+2]
            
            # Map balanced ternary pairs to hex
            mapping = {
                'TT': '0', 'T0': '1', 'T1': '2',
                '0T': '3', '00': '4', '01': '5',
                '1T': '6', '10': '7', '11': '8'
            }
            
            hex_str += mapping.get(pair, 'X')
        
        return hex_str
    
    @staticmethod
    def info_ternary(n: int, width: int = 32):
        """Display detailed ternary information
        
        Args:
            n: Decimal number to analyze
            width: Width in trits
        """
        bt = TernaryConverter.decimal_to_balanced_ternary(n, width)
        hex_repr = TernaryConverter.decimal_to_hex_ternary(n, width // 4)
        
        print(f"\nTernary Analysis of {n}:")
        print(f"  Decimal:     {n}")
        print(f"  Balanced TN: {bt}")
        print(f"  Hex TN:      {hex_repr}")
        print(f"  Trit count:  {len(bt)}")
        print(f"  Power of 3:  3^{len(bt)} = {3**len(bt)}")
        
        # Count trits
        ones = bt.count('1')
        zeros = bt.count('0')
        negs = bt.count('T')
        
        print(f"  Trit breakdown:")
        print(f"    +1 (ones):  {ones}")
        print(f"    -1 (negs):  {negs}")
        print(f"     0 (zeros): {zeros}")


def main():
    """Main function for interactive testing"""
    print("""
    ╔═════════════════════════════════════╗
    ║   Triton Ternary Converter v1.0   ║
    ║  Balanced Ternary Conversion Tool  ║
    ╚═════════════════════════════════════╝
    """)
    
    while True:
        try:
            print("\nOptions:")
            print("  1. Decimal to Balanced Ternary")
            print("  2. Balanced Ternary to Decimal")
            print("  3. Analyze Number")
            print("  4. Exit")
            
            choice = input("\nSelect option (1-4): ").strip()
            
            if choice == '1':
                n = int(input("Enter decimal number: "))
                width = int(input("Enter width in trits (default 32): ") or "32")
                bt = TernaryConverter.decimal_to_balanced_ternary(n, width)
                print(f"Result: {bt}")
            
            elif choice == '2':
                bt = input("Enter balanced ternary (T,-,1,0): ").upper()
                bt = bt.replace('-', 'T')
                result = TernaryConverter.balanced_ternary_to_decimal(bt)
                print(f"Result: {result}")
            
            elif choice == '3':
                n = int(input("Enter decimal number: "))
                TernaryConverter.info_ternary(n)
            
            elif choice == '4':
                print("Exiting...")
                break
            
            else:
                print("Invalid option")
        
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nExiting...")
            break


if __name__ == '__main__':
    main()
