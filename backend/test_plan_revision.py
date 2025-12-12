#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test suite for Phase 3: Plan Revision API

Tests the /api/v1/revise_plan endpoint with real revision logic.
Uses FastAPI TestClient for direct testing without external server.
"""

from fastapi.testclient import TestClient
import sys

sys.path.insert(0, "C:/Users/07013/Desktop/vlm-gui-automation/backend")

from main import app

client = TestClient(app)


def test_revise_plan_filter_column():
    """Test 1: Revise filter column based on feedback."""
    print("\n[TEST 1] Revise plan - change filter column")
    print("-" * 60)

    payload = {
        "old_plan": [
            {
                "id": 1,
                "action": "set_filter",
                "target_element_id": "btn_filter",
                "description": "売上金額列でフィルタする",
                "safety_tag": "safe",
                "params": {"column": "売上金額"}
            },
            {
                "id": 2,
                "action": "export_csv",
                "target_element_id": "btn_export",
                "description": "CSVでエクスポート",
                "safety_tag": "safe",
                "params": {}
            }
        ],
        "user_feedback": "違う、この列じゃなくて税込金額列でフィルタして",
    }

    try:
        resp = client.post("/api/v1/revise_plan", json=payload)

        print(f"Status Code: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[FAIL] - Expected 200, got {resp.status_code}")
            print(f"Response: {resp.text}")
            return False

        data = resp.json()
        print(f"Response message: {data['message']}")

        # Validate response structure
        assert data["success"] is True, "Expected success: true"
        assert len(data["revised_plan"]) == 2, "Expected 2 steps"

        # Check if filter column was changed
        filter_step = data["revised_plan"][0]
        assert filter_step["action"] == "set_filter", "First step should be set_filter"
        assert filter_step["params"]["column"] == "税込金額", f"Column should be '税込金額', got '{filter_step['params'].get('column')}'"

        print("[PASS] - Filter column successfully revised to '税込金額'")
        return True

    except Exception as e:
        print(f"[FAIL] - {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_revise_plan_add_login():
    """Test 2: Add login step at beginning."""
    print("\n[TEST 2] Revise plan - add login step")
    print("-" * 60)

    payload = {
        "old_plan": [
            {
                "id": 1,
                "action": "click",
                "target_element_id": "btn_dashboard",
                "description": "ダッシュボードを開く",
                "safety_tag": "safe",
                "params": {}
            }
        ],
        "user_feedback": "先にログインしてから",
    }

    try:
        resp = client.post("/api/v1/revise_plan", json=payload)

        print(f"Status Code: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[FAIL] - Expected 200, got {resp.status_code}")
            return False

        data = resp.json()
        print(f"Response message: {data['message']}")

        assert data["success"] is True
        assert len(data["revised_plan"]) == 2, f"Expected 2 steps, got {len(data['revised_plan'])}"

        # Check if login step was added at beginning
        login_step = data["revised_plan"][0]
        assert login_step["action"] == "login", f"First step should be 'login', got '{login_step['action']}'"
        assert "ログイン" in login_step["description"], "Description should mention login"

        print("[PASS] - Login step successfully added at beginning")
        return True

    except Exception as e:
        print(f"[FAIL] - {str(e)}")
        return False


def test_revise_plan_empty_plan():
    """Test 3: Revise empty plan."""
    print("\n[TEST 3] Revise empty plan")
    print("-" * 60)

    payload = {
        "old_plan": [],
        "user_feedback": "新しいタブを開いて",
    }

    try:
        resp = client.post("/api/v1/revise_plan", json=payload)

        print(f"Status Code: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[FAIL] - Expected 200, got {resp.status_code}")
            return False

        data = resp.json()
        print(f"Response message: {data['message']}")

        # Empty plan should return empty (no pattern matched)
        assert data["success"] is True
        assert len(data["revised_plan"]) == 0 or len(data["revised_plan"]) == 1

        print("[PASS] - Empty plan handled correctly")
        return True

    except Exception as e:
        print(f"[FAIL] - {str(e)}")
        return False


def test_revise_plan_no_change():
    """Test 4: Feedback that doesn't match any pattern."""
    print("\n[TEST 4] Revise plan - no pattern match")
    print("-" * 60)

    payload = {
        "old_plan": [
            {
                "id": 1,
                "action": "click",
                "target_element_id": "btn_test",
                "description": "テストボタンをクリック",
                "safety_tag": "safe",
                "params": {}
            }
        ],
        "user_feedback": "よくわかりません",  # No pattern matches this
    }

    try:
        resp = client.post("/api/v1/revise_plan", json=payload)

        print(f"Status Code: {resp.status_code}")

        if resp.status_code != 200:
            print(f"[FAIL] - Expected 200, got {resp.status_code}")
            return False

        data = resp.json()
        print(f"Response message: {data['message']}")

        assert data["success"] is True
        # Plan should be unchanged
        assert len(data["revised_plan"]) == 1

        print("[PASS] - Unrecognized feedback handled correctly (no changes)")
        return True

    except Exception as e:
        print(f"[FAIL] - {str(e)}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("PHASE 3: PLAN REVISION API TEST SUITE")
    print("=" * 60)

    tests = [
        test_revise_plan_filter_column,
        test_revise_plan_add_login,
        test_revise_plan_empty_plan,
        test_revise_plan_no_change,
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"[ERROR] Test {test_func.__name__} crashed: {e}")
            results.append(False)

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Tests Passed: {passed}/{total}")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED")
        sys.exit(0)
    else:
        print(f"\n[FAIL] {total - passed} TEST(S) FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
