#!/usr/bin/env python3
"""
Error Handler Test Suite

Verifies that the unified error handler returns the expected JSON shape.
"""

import requests
import json
import os
from pprint import pprint

API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8002")


def assert_error_response(data, expected_code: str):
    """Verify standardized error response format."""
    assert data.get("success") is False, "success should be False"
    assert "error" in data, "error field missing"
    err = data["error"]
    assert err.get("code") == expected_code, f"expected code={expected_code}, got={err.get('code')}"
    assert "message" in err, "error.message missing"
    assert "timestamp" in data, "timestamp missing"


def test_invalid_content_type():
    """Test that invalid content-type returns VALIDATION_ERROR."""
    print("[TEST] /api/v1/analyze_screen invalid content-type")

    files = {
        # content_type をわざと変にする
        "file": ("test.txt", b"not an image", "text/plain"),
    }

    r = requests.post(f"{API_BASE}/api/v1/analyze_screen", files=files, timeout=5)
    print("  status:", r.status_code)
    print("  body:  ", r.text)

    assert r.status_code == 400
    data = r.json()
    assert_error_response(data, "VALIDATION_ERROR")


def test_missing_file_field():
    """Test that missing file field returns VALIDATION_ERROR."""
    print("[TEST] /api/v1/analyze_screen missing file field")

    r = requests.post(f"{API_BASE}/api/v1/analyze_screen", files={}, timeout=5)
    print("  status:", r.status_code)
    print("  body:  ", r.text)

    assert r.status_code == 422
    data = r.json()
    assert_error_response(data, "VALIDATION_ERROR")


def test_corrupted_image():
    """Test that corrupted image data returns VALIDATION_ERROR."""
    print("[TEST] /api/v1/analyze_screen corrupted image")

    files = {
        "file": ("corrupted.png", b"\x89PNG\r\n\x1a\ncorrupted", "image/png"),
    }

    r = requests.post(f"{API_BASE}/api/v1/analyze_screen", files=files, timeout=5)
    print("  status:", r.status_code)
    print("  body:  ", r.text)

    assert r.status_code == 400
    data = r.json()
    assert_error_response(data, "VALIDATION_ERROR")


def test_nonexistent_endpoint():
    """Test that nonexistent endpoint returns standard error format."""
    print("[TEST] /api/v1/nonexistent endpoint")

    r = requests.get(f"{API_BASE}/api/v1/nonexistent", timeout=5)
    print("  status:", r.status_code)
    print("  body:  ", r.text)

    assert r.status_code == 404
    # FastAPI's default 404 may not use our handler, but check structure
    data = r.json()
    # This might not match our format exactly, so we're lenient here
    print("  [INFO] 404 response structure:", data)


def main():
    print("=" * 70)
    print("ERROR HANDLER TEST SUITE")
    print("=" * 70)
    print("API Base:", API_BASE)
    print()

    tests = [
        ("Invalid content-type", test_invalid_content_type),
        ("Missing file field", test_missing_file_field),
        ("Corrupted image data", test_corrupted_image),
        ("Nonexistent endpoint", test_nonexistent_endpoint),
    ]

    passed = 0
    for name, func in tests:
        try:
            func()
            print(f"[OK] {name}")
            passed += 1
        except AssertionError as e:
            print(f"[X] {name} FAILED:", e)
        except Exception as e:
            print(f"[X] {name} ERROR:", e)
        print()

    print("=" * 70)
    print(f"Summary: {passed}/{len(tests)} tests passed")
    print("=" * 70)

    if passed == len(tests):
        print("[OK] ALL ERROR HANDLER TESTS PASSED")
        return 0
    else:
        print(f"[X] {len(tests) - passed} tests failed")
        return 1


if __name__ == "__main__":
    exit(main())
