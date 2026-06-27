#!/usr/bin/env python3
"""
Test script to demonstrate the fix for the active/inactive classification issue.
This shows what happens before and after the fix.
"""

import sys
import os
from datetime import datetime, timedelta

# Add the current directory to the path so we can import our modules
sys.path.insert(0, '.')

from activity import classify_profile, parse_linkedin_date

def test_classification_scenarios():
    """Test various scenarios to show how the classification works."""

    print("=== Active/Inactive Classification Test ===\n")

    # Simulate the ACTIVITY_WINDOW_DAYS from config (default 10 days)
    window_days = 10
    now = datetime.now()

    test_cases = [
        # (description, date_str_or_none, expected_status_reasoning)
        ("No activity detected", None, "Should be Inactive (no evidence of recent activity)"),
        ("Activity today", "today", "Should be Active (0 days ago <= 10)"),
        ("Activity 3 days ago", "3d", "Should be Active (3 days ago <= 10)"),
        ("Activity 5 days ago", "5 days ago", "Should be Active (5 days ago <= 10)"),
        ("Activity 10 days ago", "10d", "Should be Active (10 days ago <= 10)"),
        ("Activity 11 days ago", "11 days ago", "Should be Inactive (11 days ago > 10)"),
        ("Activity 3 weeks ago", "3w", "Should be Inactive (~21 days ago > 10)"),
    ]

    for description, date_input, expected_reasoning in test_cases:
        print(f"Scenario: {description}")

        # Simulate what happens in agent.py process_lead function
        last_date = None

        if date_input is not None:
            # This simulates the activity parsing
            last_date = parse_linkedin_date(date_input)
            print(f"  Parsed date: {last_date}")
            if last_date:
                days_ago = (now - last_date).days
                print(f"  Days ago: {days_ago}")

        # This is the OLD behavior (with hardcoded 3-day fallback)
        # if not last_date and profile_has_current_company:  # Simplified condition
        #     old_last_date = now - timedelta(days=3)
        #     old_days_ago = 3
        #     old_status = "Active" if old_days_ago <= window_days else "Inactive"
        # else:
        #     old_status = classify_profile(last_date, window_days) if last_date else "Inactive"

        # This is the NEW behavior (after fix)
        new_status = classify_profile(last_date, window_days) if last_date else "Inactive"

        print(f"  Old approach would have: Hardcoded 3-day fallback -> Active (misleading!)")
        print(f"  New approach: {new_status} ({expected_reasoning})")
        print()

def demonstrate_the_problem():
    """Show exactly what the problem was and how the fix resolves it."""

    print("=== Problem Demonstration ===\n")

    print("BEFORE THE FIX:")
    print("- When no recent LinkedIn activity was found in a profile")
    print("- BUT the profile had a current company")
    print("- The code would SET last_date to exactly 3 days ago")
    print("- This made the profile appear 'Active' (3 days <= 10-day window)")
    print("- RESULT: Profiles falsely appeared as 'active 3 days ago'")
    print("- THIS WAS MISLEADING AND INACCURATE\n")

    print("AFTER THE FIX:")
    print("- When no recent LinkedIn activity is found in a profile")
    print("- We leave last_date as None (no artificial date assigned)")
    print("- classify_profile(None, window_days) returns 'Inactive'")
    print("- RESULT: Accurate classification based on actual evidence")
    print("- Profiles without recent LinkedIn activity are correctly marked as Inactive\n")

if __name__ == "__main__":
    demonstrate_the_problem()
    test_classification_scenarios()

    print("=== Summary of Fixes Applied ===")
    print("1. Removed misleading hardcoded 3-day fallback in agent.py")
    print("2. Enhanced date parsing in activity.py to handle more formats")
    print("3. Result: Accurate active/inactive classification based on actual LinkedIn activity")