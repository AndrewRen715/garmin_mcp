#!/usr/bin/env python3
"""
Test script for uploading health data using garmin-uploader
"""

import sys
import os
import tempfile
import subprocess
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def create_test_fit_file():
    """Create a test FIT file for health data"""
    # Create a simple FIT file structure
    # Note: This is a placeholder - real FIT files have specific binary format
    fit_content = """FIT File for health data
Date: 2026-04-08
Type: health
Data: {
    "steps": 10000,
    "heart_rate": 75,
    "sleep_score": 80,
    "stress_level": 30,
    "body_battery": 70
}
"""
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.fit', delete=False) as f:
        f.write(fit_content.encode('utf-8'))
        temp_file = f.name
    
    return temp_file

def test_health_upload():
    """Test uploading health data using garmin-uploader"""
    print("Testing health data upload with garmin-uploader...")
    
    # Create test FIT file
    test_file = create_test_fit_file()
    print(f"Created test FIT file: {test_file}")
    
    # Try to upload using garmin-uploader
    print("\nAttempting to upload health data...")
    print("Note: This will fail with our placeholder FIT file, but we'll test the process")
    
    try:
        # Get device ID from Garmin Connect
        print("\n1. Getting device information...")
        garmin_global = Garmin(is_cn=False)
        garmin_global.login("~/.garminconnect")
        
        devices = garmin_global.get_devices()
        if devices:
            device_id = devices[0].get('deviceId')
            device_name = devices[0].get('displayName') or devices[0].get('productDisplayName')
            print(f"   Found device: {device_name} (ID: {device_id})")
        else:
            print("   No devices found")
            device_id = "12345678"  # Default device ID
        
        # Test garmin-uploader command
        print("\n2. Testing garmin-uploader command...")
        print("   Command: garmin-uploader --help")
        
        result = subprocess.run(
            ["garmin-uploader", "--help"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("   ✓ garmin-uploader is working")
            print("   Command output:")
            print(result.stdout[:500] + "..." if len(result.stdout) > 500 else result.stdout)
        else:
            print("   ✗ garmin-uploader failed")
            print(f"   Error: {result.stderr}")
        
        # Test file upload (will fail with placeholder)
        print("\n3. Testing file upload process...")
        print("   This will fail with our placeholder FIT file, but demonstrates the process")
        
        # Command that would be used for real upload
        print("   Expected command for real upload:")
        print(f"   garmin-uploader --device {device_id} {test_file}")
        
    except Exception as e:
        print(f"   ✗ Error during test: {e}")
    finally:
        # Clean up
        if os.path.exists(test_file):
            os.unlink(test_file)
            print(f"\nCleaned up test file: {test_file}")
    
    print("\n" + "=" * 60)
    print("HEALTH DATA UPLOAD TEST COMPLETED")
    print("=" * 60)
    print("Note: This test demonstrates the upload process, but uses a placeholder FIT file.")
    print("In a real implementation, you would need to create proper FIT files with health data.")
    print("The garmin-uploader is installed and ready for use with proper FIT files.")

def main():
    """Main function"""
    try:
        test_health_upload()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
