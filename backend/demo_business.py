#!/usr/bin/env python3
"""
Production-Ready Business Scenario Demo
Showcases Phase 4 (conditional/loop) features in real business contexts
"""

import requests
import json
import time
import webbrowser
import argparse
import os
from pathlib import Path
from typing import Dict, List, Any

# API configuration from environment variable or default
API_BASE = os.getenv("API_BASE_URL", "http://127.0.0.1:8002")

SCENARIOS = {
    "sales_dashboard": {
        "name": "Sales Dashboard - December Filter & Export",
        "description": "Filter sales data for December and export to CSV",
        "plan": {
            "steps": [
                {
                    "step": 1,
                    "action": "click",
                    "target": "date_filter_button",
                    "rationale": "Open date filter menu"
                },
                {
                    "step": 2,
                    "action": "click",
                    "target": "december_option",
                    "rationale": "Select December from dropdown"
                },
                {
                    "step": 3,
                    "action": "conditional",
                    "target": "error_check",
                    "rationale": "Check if data loaded successfully",
                    "parameters": {
                        "condition": {
                            "type": "element_exists",
                            "selector": "error_message"
                        },
                        "if_true": [
                            {"action": "click", "target": "retry_button"},
                            {"action": "wait", "duration": 2}
                        ],
                        "if_false": [
                            {"action": "continue"}
                        ]
                    }
                },
                {
                    "step": 4,
                    "action": "loop",
                    "target": "pagination",
                    "rationale": "Load all pages of December data",
                    "parameters": {
                        "loop_type": "while",
                        "condition": {
                            "type": "element_exists",
                            "selector": "next_page_button"
                        },
                        "max_iterations": 10,
                        "actions": [
                            {"action": "click", "target": "next_page_button"},
                            {"action": "wait", "duration": 1.5}
                        ]
                    }
                },
                {
                    "step": 5,
                    "action": "click",
                    "target": "export_csv_button",
                    "rationale": "Export filtered data to CSV"
                },
                {
                    "step": 6,
                    "action": "conditional",
                    "target": "export_confirmation",
                    "rationale": "Verify export completed successfully",
                    "parameters": {
                        "condition": {
                            "type": "text_contains",
                            "selector": "status_message",
                            "match_text": "Export completed"
                        },
                        "if_true": [
                            {"action": "continue"}
                        ],
                        "if_false": [
                            {"action": "abort", "message": "Export failed"}
                        ]
                    }
                }
            ]
        }
    },

    "inventory_check": {
        "name": "Inventory Audit - Low Stock Alert",
        "description": "Check all inventory items and flag low stock",
        "plan": {
            "steps": [
                {
                    "step": 1,
                    "action": "click",
                    "target": "inventory_tab",
                    "rationale": "Open inventory management"
                },
                {
                    "step": 2,
                    "action": "loop",
                    "target": "check_all_items",
                    "rationale": "Iterate through all inventory items",
                    "parameters": {
                        "loop_type": "for_each",
                        "selector": "inventory_item",
                        "max_iterations": 50,
                        "actions": [
                            {"action": "click", "target": "current_item"},
                            {"action": "wait", "duration": 0.5},
                            {
                                "action": "conditional",
                                "parameters": {
                                    "condition": {
                                        "type": "text_contains",
                                        "selector": "stock_level",
                                        "match_text": "Low"
                                    },
                                    "if_true": [
                                        {"action": "click", "target": "flag_button"},
                                        {"action": "wait", "duration": 0.3}
                                    ],
                                    "if_false": [
                                        {"action": "continue"}
                                    ]
                                }
                            }
                        ]
                    }
                },
                {
                    "step": 3,
                    "action": "click",
                    "target": "generate_report",
                    "rationale": "Generate low stock report"
                }
            ]
        }
    },

    "customer_survey": {
        "name": "Customer Survey - Batch Data Entry",
        "description": "Enter survey responses for multiple customers",
        "plan": {
            "steps": [
                {
                    "step": 1,
                    "action": "click",
                    "target": "surveys_tab",
                    "rationale": "Open surveys section"
                },
                {
                    "step": 2,
                    "action": "loop",
                    "target": "fill_surveys",
                    "rationale": "Fill survey forms for batch of customers",
                    "parameters": {
                        "loop_type": "repeat",
                        "count": 5,
                        "actions": [
                            {"action": "click", "target": "new_survey_button"},
                            {"action": "type", "target": "customer_name", "text": "Customer {{iteration}}"},
                            {"action": "click", "target": "rating_5_stars"},
                            {"action": "type", "target": "comments", "text": "Excellent service"},
                            {"action": "click", "target": "submit_button"},
                            {"action": "wait", "duration": 1},
                            {
                                "action": "conditional",
                                "parameters": {
                                    "condition": {
                                        "type": "text_contains",
                                        "selector": "status",
                                        "match_text": "Success"
                                    },
                                    "if_true": [
                                        {"action": "continue"}
                                    ],
                                    "if_false": [
                                        {"action": "click", "target": "retry_button"},
                                        {"action": "wait", "duration": 2}
                                    ]
                                }
                            }
                        ]
                    }
                }
            ]
        }
    },

    "email_automation": {
        "name": "Email Campaign - Send to All Active Customers",
        "description": "Send promotional email to all active customers with error handling",
        "plan": {
            "steps": [
                {
                    "step": 1,
                    "action": "click",
                    "target": "email_campaigns",
                    "rationale": "Open email campaign manager"
                },
                {
                    "step": 2,
                    "action": "click",
                    "target": "create_campaign",
                    "rationale": "Create new campaign"
                },
                {
                    "step": 3,
                    "action": "click",
                    "target": "select_template",
                    "rationale": "Choose email template"
                },
                {
                    "step": 4,
                    "action": "loop",
                    "target": "send_to_customers",
                    "rationale": "Send email to each active customer",
                    "parameters": {
                        "loop_type": "for_each",
                        "selector": "active_customer",
                        "max_iterations": 100,
                        "actions": [
                            {"action": "click", "target": "current_item"},
                            {"action": "click", "target": "send_button"},
                            {"action": "wait", "duration": 0.5},
                            {
                                "action": "conditional",
                                "parameters": {
                                    "condition": {
                                        "type": "element_exists",
                                        "selector": "send_error"
                                    },
                                    "if_true": [
                                        {"action": "click", "target": "skip_button"},
                                        {"action": "wait", "duration": 0.3}
                                    ],
                                    "if_false": [
                                        {"action": "continue"}
                                    ]
                                }
                            }
                        ]
                    }
                },
                {
                    "step": 5,
                    "action": "click",
                    "target": "view_report",
                    "rationale": "View campaign delivery report"
                }
            ]
        }
    }
}


def print_banner(text):
    print("\n" + "=" * 70)
    print(text.center(70))
    print("=" * 70 + "\n")


def print_step(step_num, description):
    print(f"\n[Step {step_num}] {description}")
    print("-" * 70)


def execute_scenario(scenario_name):
    """Execute a business scenario demo"""
    if scenario_name not in SCENARIOS:
        print(f"[ERROR] Unknown scenario: {scenario_name}")
        print(f"Available scenarios: {', '.join(SCENARIOS.keys())}")
        return False

    scenario = SCENARIOS[scenario_name]

    print_banner(f"BUSINESS SCENARIO DEMO: {scenario['name']}")
    print(f"Description: {scenario['description']}\n")

    # Execute the plan
    print_step(1, "Executing automation plan")
    try:
        response = requests.post(
            f"{API_BASE}/api/v1/execute_plan",
            json=scenario['plan'],
            timeout=120
        )

        if response.status_code != 200:
            print(f"[ERROR] API returned status {response.status_code}")
            print(response.text)
            return False

        result = response.json()
        print(f"[OK] Plan executed successfully")
        print(f"     Total steps: {len(result.get('results', []))}")
        print(f"     Success: {result.get('success', False)}")

        # Print step details
        print("\n[Step Details]")
        for i, step_result in enumerate(result.get('results', []), 1):
            action = step_result.get('action', 'unknown')
            success = step_result.get('success', False)
            status_icon = "[OK]" if success else "[X]"

            print(f"  {status_icon} Step {i}: {action}")

            # Print conditional/loop specific info
            if action == "conditional":
                branch = step_result.get('executed_branch', 'unknown')
                condition = step_result.get('condition_met', False)
                print(f"     → Condition met: {condition}, executed: {branch}")
            elif action == "loop":
                loop_type = step_result.get('loop_type', 'unknown')
                iterations = step_result.get('iterations', 0)
                print(f"     → Loop type: {loop_type}, iterations: {iterations}")

        print_banner("SCENARIO COMPLETE")
        return True

    except requests.exceptions.ConnectionError:
        print("[ERROR] Cannot connect to backend server")
        print(f"        Make sure server is running on {API_BASE}")
        return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False


def list_scenarios():
    """List all available scenarios"""
    print_banner("AVAILABLE BUSINESS SCENARIOS")
    for key, scenario in SCENARIOS.items():
        print(f"\n[{key}]")
        print(f"  Name: {scenario['name']}")
        print(f"  Description: {scenario['description']}")
        print(f"  Steps: {len(scenario['plan']['steps'])}")


def run_all_scenarios():
    """Run all scenarios sequentially"""
    print_banner("RUNNING ALL BUSINESS SCENARIOS")
    results = {}

    for scenario_name in SCENARIOS.keys():
        print(f"\n>>> Starting scenario: {scenario_name}")
        success = execute_scenario(scenario_name)
        results[scenario_name] = success

        if not success:
            print(f"[WARN] Scenario {scenario_name} failed, continuing...")

        time.sleep(2)  # Brief pause between scenarios

    # Print summary
    print_banner("ALL SCENARIOS SUMMARY")
    for scenario_name, success in results.items():
        status = "[OK] PASS" if success else "[X] FAIL"
        print(f"  {status}  {scenario_name}")

    total = len(results)
    passed = sum(1 for s in results.values() if s)
    print(f"\n  Results: {passed}/{total} scenarios passed")


def main():
    parser = argparse.ArgumentParser(
        description="Production-Ready Business Scenario Demo (Phase 4)"
    )
    parser.add_argument(
        "--scenario",
        choices=list(SCENARIOS.keys()) + ['all', 'list'],
        help="Business scenario to run"
    )

    args = parser.parse_args()

    if not args.scenario:
        print_banner("VLM GUI AUTOMATION - BUSINESS DEMO")
        print("Usage examples:")
        print(f"  python demo_business.py --scenario sales_dashboard")
        print(f"  python demo_business.py --scenario inventory_check")
        print(f"  python demo_business.py --scenario all")
        print(f"  python demo_business.py --scenario list")
        print()
        list_scenarios()
        return

    if args.scenario == 'list':
        list_scenarios()
    elif args.scenario == 'all':
        run_all_scenarios()
    else:
        execute_scenario(args.scenario)


if __name__ == "__main__":
    main()
