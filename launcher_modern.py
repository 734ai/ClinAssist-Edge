#!/usr/bin/env python3
"""
ClinAssist Edge™ Modern UI Launcher
Easy deployment script for the advanced modern Streamlit interface
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def get_project_root():
    """Get project root directory."""
    return Path(__file__).parent

def check_dependencies():
    """Check if required dependencies are installed."""
    print("🔍 Checking dependencies...")
    
    required = ['streamlit', 'torch', 'transformers']
    missing = []
    
    for package in required:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing.append(package)
    
    if missing:
        print(f"\n⚠️  Missing: {', '.join(missing)}")
        print(f"Install with: pip install {' '.join(missing)}")
        return False
    
    return True

def launch_modern_ui(port=8501, host='localhost', dev=False):
    """Launch the modern UI."""
    project_root = get_project_root()
    app_path = project_root / 'app' / 'streamlit_app_modern.py'
    
    if not app_path.exists():
        print(f"❌ Error: {app_path} not found")
        sys.exit(1)
    
    print(f"\n🚀 Launching ClinAssist Edge™ Modern UI...")
    print(f"   📍 URL: http://{host}:{port}")
    print(f"   🎨 Theme: Dark Professional (Anduril/Palantir)")
    print(f"   📁 App: {app_path}")
    
    # Build command
    cmd = [
        'streamlit', 'run',
        str(app_path),
        '--server.port', str(port),
        '--server.address', host,
        '--server.headless', 'false' if not dev else 'true',
        '--theme.primaryColor', '#00D4FF',
        '--theme.backgroundColor', '#0A0E27',
        '--theme.secondaryBackgroundColor', '#16213E',
        '--theme.textColor', '#E8F4F8',
        '--theme.font', 'sans serif',
    ]
    
    if dev:
        print("\n🔧 Development mode enabled")
        cmd.append('--logger.level=debug')
    
    print(f"\n{'='*60}")
    print("ClinAssist Edge™ v2.0 - State-of-the-Art Clinical Intelligence")
    print(f"{'='*60}\n")
    
    try:
        subprocess.run(cmd, cwd=str(project_root))
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)

def launch_basic_ui(port=8502, host='localhost'):
    """Launch the basic UI (original)."""
    project_root = get_project_root()
    app_path = project_root / 'app' / 'streamlit_app.py'
    
    if not app_path.exists():
        print(f"❌ Error: {app_path} not found")
        sys.exit(1)
    
    print(f"\n🚀 Launching ClinAssist Edge™ Basic UI...")
    print(f"   📍 URL: http://{host}:{port}")
    
    cmd = [
        'streamlit', 'run',
        str(app_path),
        '--server.port', str(port),
        '--server.address', host,
    ]
    
    try:
        subprocess.run(cmd, cwd=str(project_root))
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)

def launch_advanced_ui(port=8503, host='localhost'):
    """Launch the advanced UI (intermediate)."""
    project_root = get_project_root()
    app_path = project_root / 'app' / 'streamlit_app_advanced.py'
    
    if not app_path.exists():
        print(f"❌ Error: {app_path} not found")
        sys.exit(1)
    
    print(f"\n🚀 Launching ClinAssist Edge™ Advanced UI...")
    print(f"   📍 URL: http://{host}:{port}")
    
    cmd = [
        'streamlit', 'run',
        str(app_path),
        '--server.port', str(port),
        '--server.address', host,
    ]
    
    try:
        subprocess.run(cmd, cwd=str(project_root))
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down...")
        sys.exit(0)

def install_dependencies():
    """Install required dependencies."""
    project_root = get_project_root()
    
    print("📦 Installing dependencies...")
    
    # Try advanced first, then fallback to basic
    for req_file in ['requirements-advanced.txt', 'requirements.txt']:
        req_path = project_root / req_file
        if req_path.exists():
            print(f"   Installing from {req_file}...")
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', '-r', str(req_path)
            ])
            return
    
    print("❌ No requirements file found")

def show_menu():
    """Show interactive menu."""
    print("\n" + "="*60)
    print("ClinAssist Edge™ - Launcher Menu")
    print("="*60)
    print("\nAvailable Interfaces:")
    print("  1. 🎨 Modern UI (Anduril/Palantir design) - RECOMMENDED")
    print("  2. 🚀 Advanced UI (Feature-rich)")
    print("  3. 📋 Basic UI (Original)")
    print("  4. 📦 Install Dependencies")
    print("  5. ❌ Exit")
    print("\n" + "="*60)

def main():
    """Main launcher function."""
    parser = argparse.ArgumentParser(
        description="ClinAssist Edge™ - Modern UI Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s modern                    # Launch modern UI
  %(prog)s advanced                  # Launch advanced UI
  %(prog)s basic                     # Launch basic UI
  %(prog)s modern --port 9000        # Custom port
  %(prog)s install                   # Install dependencies
        """
    )
    
    parser.add_argument(
        'interface',
        nargs='?',
        choices=['modern', 'advanced', 'basic', 'install', 'menu'],
        default='menu',
        help='Interface to launch (default: menu)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=None,
        help='Port number (modern: 8501, advanced: 8503, basic: 8502)'
    )
    
    parser.add_argument(
        '--host',
        default='localhost',
        help='Host address (default: localhost)'
    )
    
    parser.add_argument(
        '--dev',
        action='store_true',
        help='Development mode (for modern UI)'
    )
    
    args = parser.parse_args()
    
    # Check dependencies first
    if args.interface != 'install' and args.interface != 'menu':
        if not check_dependencies():
            print("\n❌ Please install missing dependencies first:")
            print("   pip install streamlit transformers torch")
            sys.exit(1)
    
    # Launch based on selection
    if args.interface == 'modern':
        port = args.port or 8501
        launch_modern_ui(port=port, host=args.host, dev=args.dev)
    
    elif args.interface == 'advanced':
        port = args.port or 8503
        launch_advanced_ui(port=port, host=args.host)
    
    elif args.interface == 'basic':
        port = args.port or 8502
        launch_basic_ui(port=port, host=args.host)
    
    elif args.interface == 'install':
        install_dependencies()
    
    elif args.interface == 'menu':
        while True:
            show_menu()
            choice = input("Enter choice (1-5): ").strip()
            
            if choice == '1':
                try:
                    port = int(input("Port (default 8501): ") or "8501")
                    launch_modern_ui(port=port)
                except KeyboardInterrupt:
                    continue
                except ValueError:
                    print("❌ Invalid port number")
                    continue
            
            elif choice == '2':
                try:
                    port = int(input("Port (default 8503): ") or "8503")
                    launch_advanced_ui(port=port)
                except KeyboardInterrupt:
                    continue
                except ValueError:
                    print("❌ Invalid port number")
                    continue
            
            elif choice == '3':
                try:
                    port = int(input("Port (default 8502): ") or "8502")
                    launch_basic_ui(port=port)
                except KeyboardInterrupt:
                    continue
                except ValueError:
                    print("❌ Invalid port number")
                    continue
            
            elif choice == '4':
                install_dependencies()
                continue
            
            elif choice == '5':
                print("\n👋 Goodbye!")
                sys.exit(0)
            
            else:
                print("❌ Invalid choice")
                continue

if __name__ == '__main__':
    main()
