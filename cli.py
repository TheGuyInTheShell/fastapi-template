#!/usr/bin/env python3
"""
CLI tool for FastAPI template project management.
"""
import sys
import argparse
from core.cli.generate_module import generate_module
from core.cli.generate_socket import generate_socket
from core.cli.generate_webhook import generate_webhook
from core.cli.generate_plugin import generate_plugin


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='FastAPI Template CLI Tools',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate a simple module
  python cli.py generate:module products
  
  # Generate a socket module
  python cli.py generate:socket live_chat
  
  # Generate a webhook (inbound and outbound)
  python cli.py generate:webhook stripe
  
  # Generate an inbound-only webhook
  python cli.py generate:webhook github --in
  
  # Generate a plugin
  python cli.py generate:plugin mailer
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
    
    # Optional flags for webhooks
    parser.add_argument('--in', action='store_true', dest='in_only', help='Generate inbound webhook only')
    parser.add_argument('--out', action='store_true', dest='out_only', help='Generate outbound webhook only')
    
    args = parser.parse_args()
    
    # Route commands
    if args.command == 'generate:module':
        if not args.args:
            print("[ERROR] Module name is required")
            sys.exit(1)
        generate_module(args.args[0])
    
    elif args.command == 'generate:socket':
        if not args.args:
            print("[ERROR] Socket name is required")
            sys.exit(1)
        generate_socket(args.args[0])
        
    elif args.command == 'generate:webhook':
        if not args.args:
            print("[ERROR] Webhook name is required")
            sys.exit(1)
        
        direction = 'both'
        if args.in_only: direction = 'in'
        elif args.out_only: direction = 'out'
        
        generate_webhook(args.args[0], direction)
        
    elif args.command == 'generate:plugin':
        if not args.args:
            print("[ERROR] Plugin name is required")
            sys.exit(1)
        generate_plugin(args.args[0])
    
    else:
        print(f"[ERROR] Unknown command: {args.command}")
        print("\nAvailable commands:")
        print("  generate:module <name>   - Generate a new module structure")
        print("  generate:socket <name>   - Generate a new socket module")
        print("  generate:webhook <name>  - Generate a new webhook (use --in or --out for specific ones)")
        print("  generate:plugin <name>   - Generate a new plugin structure")
        sys.exit(1)


if __name__ == "__main__":
    main()
