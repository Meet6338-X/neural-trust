"""
Test script for ChainGuardian backend API endpoints.

Run this script to verify all endpoints are working correctly.
"""

import httpx
import json

BASE_URL = "http://localhost:8002"

def test_endpoints():
    """Test all API endpoints."""
    
    print("=" * 60)
    print("ChainGuardian Backend API Tests")
    print("=" * 60)
    
    with httpx.Client(timeout=30.0) as client:
        # Test 1: Health check
        print("\n1. Testing /health...")
        try:
            response = client.get(f"{BASE_URL}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Detailed health check
        print("\n2. Testing /health/detailed...")
        try:
            response = client.get(f"{BASE_URL}/health/detailed")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {json.dumps(response.json(), indent=2)}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Audit patterns
        print("\n3. Testing /api/audit/contract/patterns...")
        try:
            response = client.get(f"{BASE_URL}/api/audit/contract/patterns")
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                patterns = response.json()
                print(f"   Found {len(patterns)} vulnerability patterns")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Contract audit
        print("\n4. Testing /api/audit/contract...")
        try:
            sample_teal = """
#pragma version 8
txn Sender
app_global_put
int 1
return
"""
            response = client.post(
                f"{BASE_URL}/api/audit/contract",
                json={
                    "code": sample_teal,
                    "language": "teal",
                    "check_types": ["security", "optimization", "best_practice"]
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Risk Score: {result.get('risk_score')}")
                print(f"   Total Issues: {result.get('total_issues')}")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 5: Risk analysis
        print("\n5. Testing /api/analysis/risk...")
        try:
            response = client.post(
                f"{BASE_URL}/api/analysis/risk",
                json={
                    "type": "transfer",
                    "amount": 100.0,
                    "sender": "TESTSENDER" * 6,
                    "recipient": "TESTRECIPIENT" * 5,
                    "protocol": "tinyman"
                }
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                print(f"   Risk Score: {result.get('risk_score')}")
                print(f"   Recommendation: {result.get('recommendation')}")
            else:
                print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 6: Fee estimation
        print("\n6. Testing /api/simulate/fees...")
        try:
            response = client.get(f"{BASE_URL}/api/simulate/fees?transaction_type=payment&priority=normal")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 7: WebSocket status
        print("\n7. Testing /ws/status...")
        try:
            response = client.get(f"{BASE_URL}/ws/status")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"   Error: {e}")
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_endpoints()
