#!/usr/bin/env python3
"""
E-Bank Quick Start Script
This script helps you quickly start the E-Bank application.
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Check if Python version is 3.7+"""
    if sys.version_info < (3, 7):
        print("❌ Python 3.7 or higher is required!")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_virtual_environment():
    """Check if virtual environment is activated"""
    if sys.prefix == sys.base_prefix:
        print("⚠️  Virtual environment not detected")
        create_venv = input("Would you like to create and activate a virtual environment? (y/n): ")
        if create_venv.lower() in ['y', 'yes']:
            create_virtual_environment()
        else:
            print("Continuing without virtual environment...")
    else:
        print("✅ Virtual environment is active")

def create_virtual_environment():
    """Create and activate virtual environment"""
    try:
        print("Creating virtual environment...")
        subprocess.run([sys.executable, '-m', 'venv', 'ebank_env'], check=True)
        
        # Instructions for manual activation
        if platform.system() == 'Windows':
            activate_script = 'ebank_env\\Scripts\\activate'
        else:
            activate_script = 'source ebank_env/bin/activate'
        
        print("✅ Virtual environment created!")
        print(f"Please run the following command to activate it:")
        print(f"   {activate_script}")
        print("Then run this script again.")
        sys.exit(0)
        
    except subprocess.CalledProcessError:
        print("❌ Failed to create virtual environment")
        sys.exit(1)

def install_dependencies():
    """Install required Python packages"""
    print("Installing dependencies...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True, capture_output=True, text=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print("❌ Failed to install dependencies")
        print(f"Error: {e.stderr}")
        print("Please install dependencies manually: pip install -r requirements.txt")
        return False
    return True

def check_database_setup():
    """Check if database is set up"""
    try:
        import psycopg2
        print("✅ PostgreSQL driver (psycopg2) is available")
        
        setup_db = input("Do you want to set up the database now? (y/n): ")
        if setup_db.lower() in ['y', 'yes']:
            print("Running database setup...")
            try:
                subprocess.run([sys.executable, 'setup_database.py'], check=True)
                print("✅ Database setup completed")
            except subprocess.CalledProcessError:
                print("❌ Database setup failed")
                print("Please run 'python setup_database.py' manually")
        else:
            print("⚠️  Remember to set up the database before running the app")
            
    except ImportError:
        print("❌ psycopg2 not found. Installing...")
        try:
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'psycopg2-binary'], 
                          check=True)
            print("✅ psycopg2 installed")
        except subprocess.CalledProcessError:
            print("❌ Failed to install psycopg2")
            return False
    return True

def start_application():
    """Start the Flask application"""
    print("\n" + "="*50)
    print("🚀 STARTING E-BANK APPLICATION")
    print("="*50)
    print("Application will be available at: http://localhost:5000")
    print("\nAdmin Login:")
    print("  Username: admin")
    print("  Password: a123")
    print("\nSample Customer Login (if sample data was created):")
    print("  Mobile: 1234567890")
    print("  PIN: 1234")
    print("="*50)
    
    try:
        subprocess.run([sys.executable, 'app.py'])
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError:
        print("❌ Failed to start application")
        print("Please check your database configuration and try running 'python app.py' manually")

def main():
    """Main function"""
    print("🏦 E-Bank Quick Start")
    print("=" * 30)
    
    # Check Python version
    check_python_version()
    
    # Check virtual environment
    check_virtual_environment()
    
    # Install dependencies
    if not install_dependencies():
        sys.exit(1)
    
    # Check database setup
    if not check_database_setup():
        sys.exit(1)
    
    # Start application
    start_ready = input("\n✅ Setup complete! Start the application now? (y/n): ")
    if start_ready.lower() in ['y', 'yes']:
        start_application()
    else:
        print("\n📋 To start manually, run: python app.py")
        print("💡 For help, see README.md")

if __name__ == "__main__":
    main()
