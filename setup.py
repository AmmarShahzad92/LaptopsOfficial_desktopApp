# setup.py - Script to set up Laptops Official
import os
import sys

def create_directory_structure():
    """Create the required directory structure"""
    directories = [
        'app',
        'app/database',
        'app/models',
        'app/controllers',
        'app/windows',
        'app/windows/auth',
        'app/windows/user',
        'app/windows/category',
        'app/windows/product',
        'app/windows/supplier',
        'app/windows/stock',
        'app/windows/reports',
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        # Create __init__.py files
        init_file = os.path.join(directory, '__init__.py')
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('')
    
    print("Directory structure created successfully!")

def install_requirements():
    """Install required packages"""
    print("Installing requirements...")
    os.system(f"{sys.executable} -m pip install PyQt6")

if __name__ == "__main__":
    create_directory_structure()
    install_requirements()
    print("\nSetup complete!")
    print("\nTo run the application:")
    print("1. Place all the provided files in their respective directories")
    print("2. Run: python -m app.main")