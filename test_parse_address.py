"""
Test script for parse-address API endpoints
Run the server first, then execute this script
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_v1_parse_address():
    print("=" * 60)
    print("Testing API v1 - Parse Address (3 levels)")
    print("=" * 60)
    
    test_cases = [
        "456 haha, Xã Quang Trọng, Huyện Thạch An, Tỉnh Cao Bằng",
        "Tỉnh Cao Bằng",
        "Huyện Thạch An, Cao Bằng",
        "Xã Quang Trọng, Huyện Thạch An",
    ]
    
    for address in test_cases:
        print(f"\nInput: {address}")
        try:
            response = requests.get(
                f"{BASE_URL}/api/v1/parse-address",
                params={"address": address}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"Result: {json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

def test_v2_parse_address():
    print("\n" + "=" * 60)
    print("Testing API v2 - Parse Address (2 levels)")
    print("=" * 60)
    
    test_cases = [
        "456 haha, Xã Quang Trọng, Tỉnh Cao Bằng",
        "Tỉnh Cao Bằng",
        "Xã Quang Trọng, Cao Bằng",
        "123 Đường ABC, Phường Hoàn Kiếm, Hà Nội",
    ]
    
    for address in test_cases:
        print(f"\nInput: {address}")
        try:
            response = requests.get(
                f"{BASE_URL}/api/v2/parse-address",
                params={"address": address}
            )
            if response.status_code == 200:
                result = response.json()
                print(f"Result: {json.dumps(result, ensure_ascii=False, indent=2)}")
            else:
                print(f"Error: {response.status_code} - {response.text}")
        except Exception as e:
            print(f"Exception: {e}")

if __name__ == "__main__":
    print("Make sure the server is running on http://127.0.0.1:8000")
    print("Start server with: uvicorn api.main:app --reload\n")
    
    try:
        test_v1_parse_address()
        test_v2_parse_address()
        print("\n" + "=" * 60)
        print("Tests completed!")
        print("=" * 60)
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to server.")
        print("Please start the server first with:")
        print("  uvicorn api.main:app --reload")
