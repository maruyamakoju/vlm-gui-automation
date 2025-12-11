"""
Test VLM Adapter - Phase 5-A

Validates that the VLM adapter layer works correctly with:
1. Dummy VLM client
2. Factory function
3. Global instance management
"""

import os
import sys
from pathlib import Path
from PIL import Image
import time

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


def test_dummy_vlm_client():
    """Test 1: Dummy VLM client basic functionality."""
    print("[TEST 1] Dummy VLM Client")
    print("-" * 50)

    from vlm_adapter import DummyVLMClient

    # Create dummy client
    client = DummyVLMClient()

    # Check if ready
    assert client.is_ready(), "Dummy client should always be ready"
    print("✓ Dummy client is ready")

    # Create a test image
    test_image = Image.new('RGB', (1920, 1080), color=(255, 255, 255))

    # Test analyze_screen
    result = client.analyze_screen(
        image=test_image,
        instruction="Find the submit button",
        context={"app_name": "TestApp"}
    )

    # Validate result structure
    assert result["success"] is True, "Result should be successful"
    assert "summary" in result, "Result should have summary"
    assert "elements" in result, "Result should have elements"
    assert "reasoning" in result, "Result should have reasoning"
    assert "processing_time" in result, "Result should have processing_time"
    assert len(result["elements"]) > 0, "Result should have some elements"

    print(f"✓ analyze_screen() returned valid result")
    print(f"  - Summary: {result['summary'][:80]}...")
    print(f"  - Elements: {len(result['elements'])} detected")
    print(f"  - Processing time: {result['processing_time']:.3f}s")

    # Test multiple calls
    result2 = client.analyze_screen(test_image, "Click the menu")
    assert client.call_count == 2, "Call count should increment"
    print(f"✓ Call counter working (count: {client.call_count})")

    print("\n[TEST 1] PASS\n")


def test_factory_function():
    """Test 2: Factory function creates correct client types."""
    print("[TEST 2] Factory Function")
    print("-" * 50)

    from vlm_adapter import get_vlm_client, DummyVLMClient

    # Force dummy mode via environment
    os.environ["USE_DUMMY_VLM"] = "true"

    # Get client with auto-detect
    client1 = get_vlm_client()
    assert isinstance(client1, DummyVLMClient), "Should return DummyVLMClient when USE_DUMMY_VLM=true"
    print("✓ Auto-detect returns DummyVLMClient when USE_DUMMY_VLM=true")

    # Get client with explicit backend
    client2 = get_vlm_client(backend="dummy")
    assert isinstance(client2, DummyVLMClient), "Should return DummyVLMClient when backend='dummy'"
    print("✓ Explicit backend='dummy' returns DummyVLMClient")

    # Test invalid backend
    try:
        get_vlm_client(backend="invalid")
        assert False, "Should raise ValueError for invalid backend"
    except ValueError as e:
        assert "Unknown VLM backend" in str(e)
        print("✓ Invalid backend raises ValueError")

    print("\n[TEST 2] PASS\n")


def test_global_instance():
    """Test 3: Global instance management."""
    print("[TEST 3] Global Instance Management")
    print("-" * 50)

    from vlm_adapter import (
        init_global_vlm_client,
        get_global_vlm_client,
        reset_global_vlm_client
    )

    # Reset first
    reset_global_vlm_client()

    # Try to get before init (should fail)
    try:
        get_global_vlm_client()
        assert False, "Should raise RuntimeError when not initialized"
    except RuntimeError as e:
        assert "not initialized" in str(e)
        print("✓ get_global_vlm_client() raises error when not initialized")

    # Initialize global client
    client = init_global_vlm_client(backend="dummy")
    assert client is not None
    print("✓ init_global_vlm_client() returns client")

    # Get global client
    client2 = get_global_vlm_client()
    assert client2 is client, "Should return same instance"
    print("✓ get_global_vlm_client() returns singleton instance")

    # Reset and verify
    reset_global_vlm_client()
    try:
        get_global_vlm_client()
        assert False, "Should fail after reset"
    except RuntimeError:
        print("✓ reset_global_vlm_client() clears singleton")

    print("\n[TEST 3] PASS\n")


def test_integration_with_image():
    """Test 4: Integration test with actual image operations."""
    print("[TEST 4] Integration with Image")
    print("-" * 50)

    from vlm_adapter import get_vlm_client

    # Create a more realistic test image
    test_image = Image.new('RGB', (1920, 1080), color=(200, 220, 240))

    # Get dummy client
    client = get_vlm_client(backend="dummy")

    # Test various instructions
    test_cases = [
        ("Click the submit button", {"app_name": "Form"}),
        ("Find all menu items", {"app_name": "Chrome"}),
        ("Locate the search box", {"app_name": "Excel"}),
    ]

    for instruction, context in test_cases:
        result = client.analyze_screen(
            image=test_image,
            instruction=instruction,
            context=context
        )
        assert result["success"] is True
        print(f"✓ '{instruction}' -> {len(result['elements'])} elements")

    print("\n[TEST 4] PASS\n")


def run_all_tests():
    """Run all VLM adapter tests."""
    print("=" * 50)
    print("VLM ADAPTER TEST SUITE")
    print("=" * 50)
    print()

    start_time = time.time()

    try:
        test_dummy_vlm_client()
        test_factory_function()
        test_global_instance()
        test_integration_with_image()

        elapsed = time.time() - start_time
        print("=" * 50)
        print(f"ALL TESTS PASSED ({elapsed:.2f}s)")
        print("=" * 50)
        return True

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
