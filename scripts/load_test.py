"""
LOAD TEST SCRIPT - Shattyk Kuziyeva
Tests system with 1000+ concurrent users
"""

import requests
import threading
import time
from datetime import datetime

print("=" * 60)
print("⚡ LOAD TEST - GYM IT SYSTEM")
print("👤 Test Engineer: Shattyk Kuziyeva")
print("=" * 60)

# Test results
results = {
    'success': 0,
    'fail': 0,
    'total': 0
}

# Services to test (microservices architecture)
services = [
    "http://localhost:8000/",           # API Gateway
    "http://localhost:8001/health",     # Auth Service
    "http://localhost:8002/health",     # User Service
    "http://localhost:8003/health",     # Tournament Service
    "http://localhost:8004/health",     # Notification Service (Shattyk's)
]

def test_endpoint(endpoint):
    """Test a single endpoint"""
    try:
        start_time = time.time()
        response = requests.get(endpoint, timeout=5)
        end_time = time.time()
        
        response_time = (end_time - start_time) * 1000  # Convert to ms
        
        if response.status_code in [200, 201]:
            results['success'] += 1
            print(f"✅ {endpoint} - {response_time:.0f}ms")
        else:
            results['fail'] += 1
            print(f"⚠️  {endpoint} - Status {response.status_code}")
    
    except Exception as e:
        results['fail'] += 1
        print(f"❌ {endpoint} - Error: {str(e)[:50]}")

def run_load_test():
    """Run 1000 concurrent requests"""
    print(f"\n🚀 Starting load test at {datetime.now()}")
    print(f"📊 Target: 1000 concurrent requests\n")
    
    threads = []
    
    # Create 1000 requests
    for i in range(1000):
        # Pick a random service to test
        import random
        endpoint = random.choice(services)
        
        # Create thread for each request
        thread = threading.Thread(target=test_endpoint, args=(endpoint,))
        threads.append(thread)
        thread.start()
        
        # Show progress every 100 requests
        if i % 100 == 0 and i > 0:
            print(f"📈 Processed {i} requests...")
            time.sleep(0.1)  # Small delay
    
    # Wait for all threads to complete
    for thread in threads:
        thread.join()
    
    results['total'] = results['success'] + results['fail']
    
    # Generate report
    print("\n" + "=" * 60)
    print("📊 LOAD TEST REPORT - Shattyk Kuziyeva")
    print("=" * 60)
    print(f"📅 Test Date: {datetime.now()}")
    print(f"🎯 Total Requests: {results['total']}")
    print(f"✅ Successful: {results['success']}")
    print(f"❌ Failed: {results['fail']}")
    
    success_rate = (results['success'] / results['total']) * 100
    print(f"📈 Success Rate: {success_rate:.2f}%")
    
    print("\n" + "=" * 60)
    if success_rate >= 95:
        print("🎉 LOAD TEST PASSED!")
        print("System can handle 1000+ concurrent users.")
    elif success_rate >= 80:
        print("⚠️  LOAD TEST PASSED WITH WARNINGS")
        print("System can handle load but has some issues.")
    else:
        print("❌ LOAD TEST FAILED")
        print("System needs optimization for high load.")
    print("=" * 60)

# Run the test
if __name__ == "__main__":
    run_load_test()