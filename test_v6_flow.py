#!/usr/bin/env python3
"""
Test script for v6 conversational API flow
"""

import requests
import json

API_URL = "http://localhost:8000"

def test_v6_flow():
    """Test the v6 conversational flow like the frontend will use it"""

    print("=" * 80)
    print("TESTING V6 CONVERSATIONAL FLOW")
    print("=" * 80)

    # Step 1: Create session (frontend does this on mount)
    print("\n1. Creating v6 session...")
    response = requests.post(
        f"{API_URL}/api/v6/session",
        json={"user_id": f"test_user_frontend"}
    )

    if response.status_code != 200:
        print(f"❌ Failed to create session: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    session_id = data["session_id"]
    print(f"✅ Session created: {session_id}")
    print(f"\n📱 MyKraws says:\n{data['greeting']}")
    print(f"\n🔍 Phase: {data['phase']}")

    # Step 2: Send user message (frontend does this when user types)
    print("\n" + "=" * 80)
    print("2. Sending user message...")
    user_message = "Calculate costs for a High Court default judgment with a claim amount of $50,000"
    print(f"\n💬 User says: {user_message}")

    response = requests.post(
        f"{API_URL}/api/v6/message",
        json={
            "session_id": session_id,
            "message": user_message
        }
    )

    if response.status_code != 200:
        print(f"❌ Failed to send message: {response.status_code}")
        print(response.text)
        return

    data = response.json()
    print(f"\n📱 MyKraws says:\n{data['response']}")
    print(f"\n🔍 Phase: {data['phase']}")
    print(f"🔄 Continue conversation: {data['continue_conversation']}")

    # If there's metadata with thought process, show it
    if data.get('metadata') and data['metadata'].get('thought_process'):
        print(f"\n💭 Thought process: {data['metadata']['thought_process']}")

    # Step 3: Continue conversation if needed
    if data['continue_conversation']:
        print("\n" + "=" * 80)
        print("3. MyKraws might ask questions or continue the flow...")
        print("(In the frontend, user would respond to any questions)")

    print("\n" + "=" * 80)
    print("✅ V6 FLOW TEST COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    test_v6_flow()
