#!/usr/bin/env python3
"""
Test token handling for both global and China regions
"""

import sys
import os
import shutil
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, 'src')

from garminconnect import Garmin

def test_token_handling():
    """Test token handling for both regions"""
    # Test China region
    print("Testing China region token handling...")
    
    # Get credentials from user
    email = input("Enter your Garmin Connect email: ").strip()
    password = input("Enter your Garmin Connect password: ").strip()
    
    # Initialize Garmin client for China region
    garmin_cn = Garmin(email=email, password=password, is_cn=True)
    garmin_cn.login()
    
    print("✓ China region login successful!")
    
    # Save tokens for China region
    cn_tokenstore = "~/.garminconnect_cn"
    cn_tokenstore_expanded = os.path.expanduser(cn_tokenstore)
    
    print(f"Saving China region tokens to: {cn_tokenstore_expanded}")
    garmin_cn.garth.dump(cn_tokenstore)
    
    if os.path.exists(cn_tokenstore_expanded):
        print(f"✓ China region tokens saved successfully")
    else:
        print(f"✗ Failed to save China region tokens")
    
    # Test token login for China region
    print("\nTesting China region token login...")
    
    try:
        # Create new client and login with tokens
        garmin_cn_token = Garmin(is_cn=True)
        garmin_cn_token.login(cn_tokenstore)
        print("✓ China region token login successful!")
        
        # Verify connection
        user_profile = garmin_cn_token.get_user_profile()
        if user_profile:
            print("✓ China region connection verified with tokens")
    except Exception as e:
        print(f"✗ China region token login failed: {e}")
    
    print("\n" + "=" * 60)
    print("TOKEN TESTING COMPLETED")
    print("=" * 60)
    print(f"China region tokens saved to: {cn_tokenstore_expanded}")
    print("Tokens should now be used automatically for future logins")

def main():
    """Main function"""
    try:
        test_token_handling()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
