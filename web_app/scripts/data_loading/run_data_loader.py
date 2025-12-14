#!/usr/bin/env python3
"""
Helper script to run the buildings data loader
"""

import subprocess
import sys
import os

def main():
    """Run the buildings data loader"""
    
    # Change to the web_app directory
    web_app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(web_app_dir)
    
    print("Loading buildings data into the database...")
    print("=" * 50)
    
    try:
        # Run the data loader
        result = subprocess.run([sys.executable, 'load_buildings_data.py'], 
                              capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        
        if result.returncode == 0:
            print("\n" + "=" * 50)
            print("✅ Buildings data loaded successfully!")
            print("\nYou can now:")
            print("1. Start the Flask app: python app.py")
            print("2. Visit http://localhost:5000/buildings to view the data")
        else:
            print("\n" + "=" * 50)
            print("❌ Error loading buildings data")
            print(f"Exit code: {result.returncode}")
            
    except Exception as e:
        print(f"Error running data loader: {e}")

if __name__ == "__main__":
    main()
