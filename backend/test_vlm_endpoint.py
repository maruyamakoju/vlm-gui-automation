"""
Quick test for VLM adapter integration with main.py

Tests the /api/v1/analyze_screen endpoint using the new VLM adapter
"""

import requests
from PIL import Image
import io
import sys

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def create_test_image():
    """Create a simple test image."""
    img = Image.new('RGB', (800, 600), color=(255, 255, 255))
    return img


def test_analyze_screen_endpoint():
    """Test /api/v1/analyze_screen endpoint."""
    print("=" * 60)
    print("VLM ENDPOINT TEST (Phase 5-A Integration)")
    print("=" * 60)
    print()

    base_url = "http://127.0.0.1:8002"
    endpoint = f"{base_url}/api/v1/analyze_screen"

    # Check server health first
    print("1. Checking server health...")
    try:
        health_response = requests.get(f"{base_url}/health", timeout=5)
        if health_response.status_code == 200:
            print("   ✓ Server is running")
        else:
            print(f"   ✗ Server returned {health_response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ✗ Server not reachable: {e}")
        print("   Make sure the server is running on port 8002")
        return False

    # Create test image
    print("\n2. Creating test image...")
    test_image = create_test_image()
    print("   ✓ Test image created (800x600)")

    # Convert image to bytes
    img_byte_arr = io.BytesIO()
    test_image.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)

    # Send request to analyze_screen endpoint
    print("\n3. Sending POST request to /api/v1/analyze_screen...")
    try:
        files = {'file': ('test.png', img_byte_arr, 'image/png')}
        response = requests.post(endpoint, files=files, timeout=10)

        print(f"   Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()

            print("   ✓ Request successful!")
            print("\n4. Analyzing response...")
            print(f"   - success: {result.get('success')}")
            print(f"   - summary: {result.get('summary', 'N/A')[:80]}...")
            print(f"   - elements: {len(result.get('elements', []))} detected")
            print(f"   - processing_time: {result.get('processing_time', 0):.3f}s")

            # Validate expected fields
            if result.get('success') is True:
                print("\n   ✓ VLM adapter is working correctly!")
                return True
            else:
                print("\n   ✗ Response does not indicate success")
                return False
        else:
            print(f"   ✗ Request failed with status {response.status_code}")
            print(f"   Error: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"   ✗ Request error: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    print()
    success = test_analyze_screen_endpoint()
    print()
    print("=" * 60)
    if success:
        print("TEST PASSED: VLM adapter is integrated successfully!")
    else:
        print("TEST FAILED: VLM adapter integration issue")
    print("=" * 60)
    print()

    sys.exit(0 if success else 1)
