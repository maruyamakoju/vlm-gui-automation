#!/usr/bin/env python3
"""
Product Quality Check Script
Tests all Phase 4 components and generates quality report
"""

import requests
import json
import time
import sys
from typing import Dict, List, Any
import os

# API configuration
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8002")

class QualityChecker:
    def __init__(self):
        self.results = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "tests_passed": 0,
            "tests_failed": 0,
            "tests_total": 0,
            "test_details": []
        }

    def test(self, name: str, func):
        """Run a test and record results"""
        self.results["tests_total"] += 1
        print(f"\n[TEST {self.results['tests_total']}] {name}")
        print("-" * 70)

        try:
            result = func()
            if result["success"]:
                self.results["tests_passed"] += 1
                print(f"[OK] PASS: {result.get('message', 'Test passed')}")
            else:
                self.results["tests_failed"] += 1
                print(f"[X] FAIL: {result.get('message', 'Test failed')}")

            self.results["test_details"].append({
                "name": name,
                "success": result["success"],
                "message": result.get("message", ""),
                "details": result.get("details", {})
            })

            return result
        except Exception as e:
            self.results["tests_failed"] += 1
            print(f"[X] ERROR: {str(e)}")
            self.results["test_details"].append({
                "name": name,
                "success": False,
                "message": f"Exception: {str(e)}",
                "details": {}
            })
            return {"success": False, "message": str(e)}

    def print_summary(self):
        """Print final quality report"""
        print("\n" + "=" * 70)
        print("QUALITY CHECK SUMMARY".center(70))
        print("=" * 70)
        print(f"\nTimestamp: {self.results['timestamp']}")
        print(f"Total Tests: {self.results['tests_total']}")
        print(f"Passed: {self.results['tests_passed']} [OK]")
        print(f"Failed: {self.results['tests_failed']} [X]")

        success_rate = (self.results['tests_passed'] / self.results['tests_total'] * 100) if self.results['tests_total'] > 0 else 0
        print(f"Success Rate: {success_rate:.1f}%")

        print("\n" + "=" * 70)

        if self.results["tests_failed"] == 0:
            print("[OK] ALL TESTS PASSED - PRODUCT QUALITY: EXCELLENT")
        elif success_rate >= 80:
            print("[!] MOST TESTS PASSED - PRODUCT QUALITY: GOOD")
        elif success_rate >= 50:
            print("[!] SOME TESTS FAILED - PRODUCT QUALITY: NEEDS IMPROVEMENT")
        else:
            print("[X] MANY TESTS FAILED - PRODUCT QUALITY: POOR")

        print("=" * 70 + "\n")

        return self.results


# Test Functions

def test_server_health():
    """Test 1: Check if server is running"""
    try:
        response = requests.get(f"{API_BASE}/", timeout=5)
        if response.status_code == 200:
            return {
                "success": True,
                "message": "Server is running and responding",
                "details": {"status_code": response.status_code}
            }
        else:
            return {
                "success": False,
                "message": f"Server returned status {response.status_code}",
                "details": {"status_code": response.status_code}
            }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "message": "Cannot connect to server - is it running?",
            "details": {"api_base": API_BASE}
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


def test_business_scenarios_endpoint():
    """Test 2: GET /api/v1/business_scenarios"""
    try:
        response = requests.get(f"{API_BASE}/api/v1/business_scenarios", timeout=10)

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"API returned status {response.status_code}",
                "details": {"status_code": response.status_code}
            }

        data = response.json()

        if not data.get("success"):
            return {
                "success": False,
                "message": f"API returned success=False: {data.get('error', 'Unknown error')}",
                "details": data
            }

        scenarios = data.get("scenarios", [])
        count = data.get("count", 0)

        if count != 4:
            return {
                "success": False,
                "message": f"Expected 4 scenarios, got {count}",
                "details": {"scenarios": scenarios}
            }

        expected_ids = ["sales_dashboard", "inventory_check", "customer_survey", "email_automation"]
        scenario_ids = [s["id"] for s in scenarios]

        if set(scenario_ids) != set(expected_ids):
            return {
                "success": False,
                "message": f"Scenario IDs don't match expected",
                "details": {"expected": expected_ids, "actual": scenario_ids}
            }

        return {
            "success": True,
            "message": f"Found {count} business scenarios with correct structure",
            "details": {
                "scenarios": [s["id"] for s in scenarios],
                "count": count
            }
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


def test_library_module_import():
    """Test 3: Can import business_scenarios module"""
    try:
        # Try to import the module
        import business_scenarios

        # Check if required functions exist
        if not hasattr(business_scenarios, 'get_available_scenarios'):
            return {
                "success": False,
                "message": "Module missing get_available_scenarios function"
            }

        if not hasattr(business_scenarios, 'run_scenario'):
            return {
                "success": False,
                "message": "Module missing run_scenario function"
            }

        # Try calling get_available_scenarios
        scenarios = business_scenarios.get_available_scenarios()

        if not isinstance(scenarios, list):
            return {
                "success": False,
                "message": "get_available_scenarios didn't return a list"
            }

        if len(scenarios) != 4:
            return {
                "success": False,
                "message": f"Expected 4 scenarios, got {len(scenarios)}"
            }

        return {
            "success": True,
            "message": "Module imports correctly and functions work",
            "details": {"scenarios_count": len(scenarios)}
        }

    except ImportError as e:
        return {
            "success": False,
            "message": f"Cannot import module: {str(e)}"
        }
    except Exception as e:
        return {"success": False, "message": str(e)}


def test_execute_plan_endpoint():
    """Test 4: POST /api/v1/execute_plan (basic)"""
    try:
        # Simple test plan
        test_plan = {
            "steps": [
                {
                    "step": 1,
                    "action": "wait",
                    "target": "test_wait",
                    "duration": 0.1,
                    "rationale": "Quality check test"
                }
            ]
        }

        response = requests.post(
            f"{API_BASE}/api/v1/execute_plan",
            json=test_plan,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"API returned status {response.status_code}",
                "details": {"status_code": response.status_code}
            }

        data = response.json()

        if not data.get("success"):
            return {
                "success": False,
                "message": "Plan execution failed",
                "details": data
            }

        return {
            "success": True,
            "message": "Execute plan endpoint works correctly",
            "details": {"steps_executed": len(data.get("results", []))}
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


def test_conditional_action():
    """Test 5: Conditional action execution"""
    try:
        # Test plan with conditional
        test_plan = {
            "steps": [
                {
                    "step": 1,
                    "action": "conditional",
                    "target": "test_condition",
                    "rationale": "Test conditional branching",
                    "parameters": {
                        "condition": {
                            "type": "element_exists",
                            "selector": "nonexistent_element"
                        },
                        "if_true": [
                            {"action": "wait", "duration": 0.1}
                        ],
                        "if_false": [
                            {"action": "wait", "duration": 0.1}
                        ]
                    }
                }
            ]
        }

        response = requests.post(
            f"{API_BASE}/api/v1/execute_plan",
            json=test_plan,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"API returned status {response.status_code}"
            }

        data = response.json()
        results = data.get("results", [])

        if len(results) == 0:
            return {
                "success": False,
                "message": "No results returned"
            }

        first_result = results[0]

        if first_result.get("action") != "conditional":
            return {
                "success": False,
                "message": f"Expected conditional action, got {first_result.get('action')}"
            }

        return {
            "success": True,
            "message": "Conditional action executes correctly",
            "details": {
                "condition_met": first_result.get("condition_met"),
                "executed_branch": first_result.get("executed_branch")
            }
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


def test_loop_action():
    """Test 6: Loop action execution"""
    try:
        # Test plan with loop
        test_plan = {
            "steps": [
                {
                    "step": 1,
                    "action": "loop",
                    "target": "test_loop",
                    "rationale": "Test loop execution",
                    "parameters": {
                        "loop_type": "repeat",
                        "count": 3,
                        "actions": [
                            {"action": "wait", "duration": 0.1}
                        ]
                    }
                }
            ]
        }

        response = requests.post(
            f"{API_BASE}/api/v1/execute_plan",
            json=test_plan,
            timeout=10
        )

        if response.status_code != 200:
            return {
                "success": False,
                "message": f"API returned status {response.status_code}"
            }

        data = response.json()
        results = data.get("results", [])

        if len(results) == 0:
            return {
                "success": False,
                "message": "No results returned"
            }

        first_result = results[0]

        if first_result.get("action") != "loop":
            return {
                "success": False,
                "message": f"Expected loop action, got {first_result.get('action')}"
            }

        iterations = first_result.get("iterations", 0)

        if iterations != 3:
            return {
                "success": False,
                "message": f"Expected 3 iterations, got {iterations}"
            }

        return {
            "success": True,
            "message": "Loop action executes correctly",
            "details": {
                "loop_type": first_result.get("loop_type"),
                "iterations": iterations
            }
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


def test_env_configuration():
    """Test 7: Environment variable configuration"""
    try:
        # Check if API_BASE_URL is configurable
        import business_scenarios

        # The module should have API_BASE from env or default
        if not hasattr(business_scenarios, 'API_BASE'):
            return {
                "success": False,
                "message": "Module doesn't have API_BASE variable"
            }

        api_base = business_scenarios.API_BASE

        # Should be a valid URL
        if not api_base.startswith("http"):
            return {
                "success": False,
                "message": f"API_BASE is not a valid URL: {api_base}"
            }

        return {
            "success": True,
            "message": "Environment configuration works correctly",
            "details": {"api_base": api_base}
        }

    except Exception as e:
        return {"success": False, "message": str(e)}


def main():
    """Run all quality checks"""
    print("=" * 70)
    print("VLM GUI AUTOMATION - PRODUCT QUALITY CHECK".center(70))
    print("=" * 70)
    print(f"\nAPI Base: {API_BASE}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    checker = QualityChecker()

    # Run all tests
    checker.test("Server Health Check", test_server_health)
    checker.test("Business Scenarios API Endpoint", test_business_scenarios_endpoint)
    checker.test("Library Module Import", test_library_module_import)
    checker.test("Execute Plan Endpoint", test_execute_plan_endpoint)
    checker.test("Conditional Action Execution", test_conditional_action)
    checker.test("Loop Action Execution", test_loop_action)
    checker.test("Environment Configuration", test_env_configuration)

    # Print summary
    results = checker.print_summary()

    # Save results to file
    results_file = "quality_check_results.json"
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"[INFO] Detailed results saved to: {results_file}\n")

    # Exit with appropriate code
    sys.exit(0 if results["tests_failed"] == 0 else 1)


if __name__ == "__main__":
    main()
