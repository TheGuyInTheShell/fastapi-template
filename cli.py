#!/usr/bin/env python3
"""
CLI tool for FastAPI template project management.
"""
import sys
import argparse
from core.cli.generate_module import generate_module


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='FastAPI Template CLI Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a simple module
  python cli.py generate:module products
  
  # Generate a nested module
  python cli.py generate:module store.products
  
  # Generate deeply nested module
  python cli.py generate:module products
        """
    )
    
    parser.add_argument(
        'command',
        help='Command to execute (e.g., generate:module)'
    )
    
    parser.add_argument(
        'args',
        nargs='*',
        help='Command arguments'
    )
    
    args = parser.parse_args()
    
    # Route commands
    if args.command == 'generate:module':
        if not args.args:
            print("[ERROR] Module name is required")
            print("Usage: python cli.py generate:module <module_name>")
            print("Example: python cli.py generate:module products")
            sys.exit(1)
        
        module_name = args.args[0]
        generate_module(module_name)
    
    else:
        print(f"[ERROR] Unknown command: {args.command}")
        print("\nAvailable commands:")
        print("  generate:module <name>  - Generate a new module structure")
        sys.exit(1)


if __name__ == "__main__":
    main()
