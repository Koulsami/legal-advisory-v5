#!/usr/bin/env python3
"""
Legal Advisory System v5.0 - Python API Client Example
Demonstrates how to interact with the API using Python's requests library
"""

import requests
import json
from typing import Dict, Any, Optional


class LegalAdvisoryClient:
    """Python client for Legal Advisory System API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url.rstrip('/')
        self.session_id: Optional[str] = None

    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = requests.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    def create_session(self, user_id: str) -> Dict[str, Any]:
        """Create a new conversation session"""
        response = requests.post(
            f"{self.base_url}/sessions",
            json={"user_id": user_id}
        )
        response.raise_for_status()
        data = response.json()
        self.session_id = data["session_id"]
        return data

    def get_session(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Get session details"""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID provided or set")

        response = requests.get(f"{self.base_url}/sessions/{sid}")
        response.raise_for_status()
        return response.json()

    def send_message(self, message: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """Send a message in the conversation"""
        sid = session_id or self.session_id
        if not sid:
            raise ValueError("No session ID provided or set")

        response = requests.post(
            f"{self.base_url}/messages",
            json={
                "session_id": sid,
                "message": message
            }
        )
        response.raise_for_status()
        return response.json()

    def list_modules(self) -> Dict[str, Any]:
        """List available legal modules"""
        response = requests.get(f"{self.base_url}/modules")
        response.raise_for_status()
        return response.json()

    def get_statistics(self) -> Dict[str, Any]:
        """Get system statistics"""
        response = requests.get(f"{self.base_url}/statistics")
        response.raise_for_status()
        return response.json()


def print_section(title: str):
    """Print formatted section header"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_response(response: Dict[str, Any]):
    """Print formatted response"""
    print(f"Status: {response.get('status', 'unknown')}")
    print(f"Completeness: {response.get('completeness_score', 0) * 100:.0f}%")
    print(f"\nMessage:\n{response.get('message', 'No message')}")

    if response.get('result'):
        print(f"\n📊 Result:")
        print(json.dumps(response['result'], indent=2))

    if response.get('questions'):
        print(f"\n❓ Follow-up Questions:")
        for q in response['questions']:
            print(f"  - {q}")
    print()


def example_1_simple_query():
    """Example 1: Simple one-shot query"""
    print_section("Example 1: Simple Query")

    client = LegalAdvisoryClient()

    # Create session
    print("Creating session...")
    session = client.create_session(user_id="python_example_1")
    print(f"✅ Session created: {session['session_id']}\n")

    # Send message
    print("Sending query...")
    response = client.send_message(
        "I need costs for a High Court default judgment for $50,000 liquidated claim"
    )
    print_response(response)


def example_2_conversational():
    """Example 2: Multi-turn conversation"""
    print_section("Example 2: Conversational Flow")

    client = LegalAdvisoryClient()

    # Create session
    print("Creating session...")
    session = client.create_session(user_id="python_example_2")
    print(f"✅ Session created: {session['session_id']}\n")

    # Multi-turn conversation
    messages = [
        "I need help calculating legal costs",
        "It's for a default judgment",
        "District Court",
        "The claim is $30,000 and it's liquidated"
    ]

    for i, message in enumerate(messages, 1):
        print(f"Message {i}: \"{message}\"")
        response = client.send_message(message)
        print_response(response)
        print("-" * 80)


def example_3_complex_trial():
    """Example 3: Complex trial scenario"""
    print_section("Example 3: Complex Contested Trial")

    client = LegalAdvisoryClient()

    # Create session
    session = client.create_session(user_id="python_example_3")
    print(f"✅ Session created: {session['session_id']}\n")

    # Send complex query
    response = client.send_message(
        "I need costs for a contested trial in High Court that lasted 5 days for a claim of $250,000"
    )
    print_response(response)


def example_4_system_info():
    """Example 4: Get system information"""
    print_section("Example 4: System Information")

    client = LegalAdvisoryClient()

    # Health check
    print("Health Check:")
    health = client.health_check()
    print(json.dumps(health, indent=2))
    print()

    # List modules
    print("Available Modules:")
    modules = client.list_modules()
    print(json.dumps(modules, indent=2))
    print()

    # Get statistics
    print("System Statistics:")
    stats = client.get_statistics()
    print(json.dumps(stats, indent=2))
    print()


def example_5_error_handling():
    """Example 5: Error handling"""
    print_section("Example 5: Error Handling")

    client = LegalAdvisoryClient()

    # Create session
    session = client.create_session(user_id="python_example_5")
    print(f"✅ Session created: {session['session_id']}\n")

    # Try invalid input
    print("Sending invalid input...")
    try:
        response = client.send_message("Calculate costs for -$1000")
        print_response(response)
    except requests.exceptions.HTTPError as e:
        print(f"❌ Error: {e}")
        print(f"Response: {e.response.text}")

    # Recover with valid input
    print("\nRecovering with valid input...")
    response = client.send_message(
        "Calculate costs for High Court default judgment $50,000 liquidated"
    )
    print_response(response)


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("  Legal Advisory System v5.0 - Python API Client Examples")
    print("=" * 80)
    print("\nMake sure the API server is running:")
    print("  uvicorn backend.api.routes:app --reload")
    print("\nPress Enter to continue...")
    input()

    examples = [
        ("Simple Query", example_1_simple_query),
        ("Conversational Flow", example_2_conversational),
        ("Complex Trial", example_3_complex_trial),
        ("System Information", example_4_system_info),
        ("Error Handling", example_5_error_handling),
    ]

    for i, (name, func) in enumerate(examples, 1):
        print(f"\n\n{'=' * 80}")
        print(f"  Running Example {i}/{len(examples)}: {name}")
        print('=' * 80)
        func()

        if i < len(examples):
            print("\n⏸️  Press Enter to continue to next example...")
            input()

    print("\n" + "=" * 80)
    print("  All Examples Complete!")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo interrupted by user.")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server.")
        print("Please make sure the server is running:")
        print("  uvicorn backend.api.routes:app --reload")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
