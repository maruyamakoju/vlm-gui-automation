#!/usr/bin/env python3
"""
Business Scenarios Library - API/Library Mode
For integration with FastAPI backend
"""

import requests
import os
import time
from typing import Dict, List, Any

# API configuration
API_BASE = os.getenv('API_BASE_URL', 'http://127.0.0.1:8002')

# Import scenarios from demo_business (to avoid duplication)
try:
    from demo_business import SCENARIOS
except ImportError:
    SCENARIOS = {}

def get_available_scenarios() -> List[Dict[str, Any]]:
    """Get list of available scenarios"""
    return [
        {
            'id': key,
            'name': scenario['name'],
            'description': scenario['description'],
            'steps_count': len(scenario['plan']['steps'])
        }
        for key, scenario in SCENARIOS.items()
    ]

def run_scenario(scenario_name: str, api_base: str = None) -> Dict[str, Any]:
    """Execute a scenario and return results as dictionary"""
    if scenario_name not in SCENARIOS:
        return {
            'success': False,
            'scenario_name': scenario_name,
            'error': f'Unknown scenario: {scenario_name}',
            'available_scenarios': list(SCENARIOS.keys())
        }

    scenario = SCENARIOS[scenario_name]
    base_url = api_base or API_BASE

    try:
        start_time = time.time()
        response = requests.post(
            f'{base_url}/api/v1/execute_plan',
            json=scenario['plan'],
            timeout=120
        )
        execution_time = time.time() - start_time

        if response.status_code != 200:
            return {
                'success': False,
                'scenario_name': scenario_name,
                'error': f'API error: {response.status_code}',
                'execution_time': execution_time
            }

        result = response.json()
        return {
            'success': result.get('success', False),
            'scenario_name': scenario_name,
            'scenario_title': scenario['name'],
            'total_steps': len(result.get('results', [])),
            'results': result.get('results', []),
            'execution_time': execution_time
        }

    except Exception as e:
        return {
            'success': False,
            'scenario_name': scenario_name,
            'error': f'Exception: {type(e).__name__}',
            'error_detail': str(e)
        }
