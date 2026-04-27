#!/usr/bin/env python3
"""
Test init_api function with token handling
"""

import sys
import os
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garmin_mcp import init_api

def test_init_api():
    """Test init_api function with token handling"""
    print("Testing init_api function with China region...")
    
    # Set environment variable for China region
    os.environ['GARMIN_CN'] = 'true'
    
    # Test token login (should work without credentials)
    print("\n1. Testing init_api with token login...")
    garmin_client = init_api(None, None, is_cn=True)
    
    if garmin_client:
        print("✓ init_api token login successful!")
        
        # Verify connection
        try:
            user_profile = garmin_client.get_user_profile()
            if user_profile:
                print("✓ Connection verified with tokens")
        except Exception as e:
            print(f"✗ Failed to verify connection: {e}")
    else:
        print("✗ init_api token login failed")
    
    # Test with credentials (should save tokens if needed)
    print("\n2. Testing init_api with credentials...")
    
    # Get credentials from user
    email = input("Enter your Garmin Connect email: ").strip()
    password = input("Enter your Garmin Connect password: ").strip()
    
    garmin_client_creds = init_api(email, password, is_cn=True)
    
    if garmin_client_creds:
        print("✓ init_api login with credentials successful!")
        
        # Verify tokens were saved
        cn_tokenstore = "~/.garminconnect_cn"
        cn_tokenstore_expanded = os.path.expanduser(cn_tokenstore)
        
        if os.path.exists(cn_tokenstore_expanded):
            print(f"✓ Tokens saved to: {cn_tokenstore_expanded}")
        else:
            print(f"✗ Tokens not saved")
    else:
        print("✗ init_api login with credentials failed")
    
    print("\n" + "=" * 60)
    print("init_api TESTING COMPLETED")
    print("=" * 60)

def main():
    """Main function"""
    try:
        test_init_api()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
