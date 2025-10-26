#!/usr/bin/env python3
"""
Legal Advisory System v5.0 - Interactive Demo
Demonstrates the system's capabilities with realistic scenarios
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.conversation.conversation_manager import ConversationManager
from backend.config.settings import Settings
from backend.common_services.analysis_engine import AnalysisEngine
from backend.common_services.module_registry import ModuleRegistry
from backend.common_services.matching_engine import UniversalMatchingEngine
from backend.common_services.logic_tree_framework import LogicTreeFramework
from backend.modules.order_21.order21_module import Order21Module
from backend.hybrid_ai.hybrid_orchestrator import HybridAIOrchestrator
from backend.emulators.ai_emulator import AIEmulator
from datetime import datetime


class DemoRunner:
    """Interactive demo runner for Legal Advisory System v5.0"""

    def __init__(self):
        self.settings = Settings()

        # Initialize common services
        self.logic_tree_framework = LogicTreeFramework()
        self.matching_engine = UniversalMatchingEngine()
        self.module_registry = ModuleRegistry(tree_framework=self.logic_tree_framework)
        self.analysis_engine = AnalysisEngine(
            module_registry=self.module_registry,
            matching_engine=self.matching_engine,
            tree_framework=self.logic_tree_framework
        )

        # Register Order 21 module
        order21_module = Order21Module()
        self.module_registry.register_module(order21_module)

        # Initialize hybrid AI orchestrator (using emulator for demo)
        ai_service = AIEmulator()
        self.hybrid_ai = HybridAIOrchestrator(ai_service=ai_service)

        # Initialize conversation manager
        self.conversation_manager = ConversationManager(
            hybrid_ai=self.hybrid_ai,
            analysis_engine=self.analysis_engine,
            module_registry=self.module_registry
        )

    def print_header(self, text: str, width: int = 80):
        """Print formatted header"""
        print("\n" + "=" * width)
        print(f"  {text}")
        print("=" * width + "\n")

    def print_section(self, text: str, width: int = 80):
        """Print formatted section"""
        print("\n" + "-" * width)
        print(f"  {text}")
        print("-" * width + "\n")

    async def run_scenario(self, scenario_name: str, user_id: str, messages: list[str]):
        """Run a single demo scenario"""
        self.print_section(f"Scenario: {scenario_name}")

        # Create session
        print(f"👤 User: {user_id}")
        session = self.conversation_manager.create_session(user_id=user_id)
        print(f"✅ Session created: {session.session_id}\n")

        # Process messages
        for i, message in enumerate(messages, 1):
            print(f"💬 User Message {i}:")
            print(f"   \"{message}\"")
            print()

            response = await self.conversation_manager.process_message(
                user_message=message,
                session_id=session.session_id
            )

            print(f"🤖 System Response:")
            print(f"   Status: {response.status}")
            print(f"   Completeness: {response.completeness_score:.0%}")
            print()
            print(f"   Message:")
            # Indent each line of the response
            for line in response.message.split('\n'):
                print(f"   {line}")
            print()

            if response.result:
                print(f"   📊 Result:")
                for key, value in response.result.items():
                    if isinstance(value, dict):
                        print(f"      {key}:")
                        for k, v in value.items():
                            print(f"         {k}: {v}")
                    else:
                        print(f"      {key}: {value}")
                print()

            if response.questions:
                print(f"   ❓ Follow-up Questions:")
                for question in response.questions:
                    print(f"      - {question}")
                print()

            # Pause between messages for readability
            await asyncio.sleep(0.5)

        return session

    async def demo_1_simple_query(self):
        """Demo 1: Simple straightforward query with all information"""
        await self.run_scenario(
            scenario_name="Simple High Court Default Judgment",
            user_id="demo_user_1",
            messages=[
                "I need to calculate costs for a High Court default judgment for a claim of $50,000 (liquidated)"
            ]
        )

    async def demo_2_conversational(self):
        """Demo 2: Multi-turn conversation with progressive information gathering"""
        await self.run_scenario(
            scenario_name="Conversational Cost Inquiry",
            user_id="demo_user_2",
            messages=[
                "I need help calculating legal costs",
                "It's for a default judgment",
                "High Court",
                "The claim amount is $75,000 and it's liquidated",
            ]
        )

    async def demo_3_complex_trial(self):
        """Demo 3: Contested trial with complexity factors"""
        await self.run_scenario(
            scenario_name="Complex Contested Trial",
            user_id="demo_user_3",
            messages=[
                "I need costs for a contested trial in the District Court that lasted 4 days for a claim of $120,000"
            ]
        )

    async def demo_4_unliquidated_claim(self):
        """Demo 4: Unliquidated claim"""
        await self.run_scenario(
            scenario_name="Unliquidated Default Judgment",
            user_id="demo_user_4",
            messages=[
                "What are the costs for a Magistrates Court default judgment for an unliquidated claim of $15,000?"
            ]
        )

    async def demo_5_summary_judgment(self):
        """Demo 5: Summary judgment"""
        await self.run_scenario(
            scenario_name="Summary Judgment",
            user_id="demo_user_5",
            messages=[
                "I obtained summary judgment in High Court for $200,000. What are the costs?"
            ]
        )

    async def demo_6_error_handling(self):
        """Demo 6: Error handling with invalid inputs"""
        await self.run_scenario(
            scenario_name="Error Handling & Validation",
            user_id="demo_user_6",
            messages=[
                "Calculate costs for a claim of negative $1000",
                "Okay, make it $25,000 for a High Court default judgment"
            ]
        )

    async def run_all_demos(self):
        """Run all demo scenarios"""
        self.print_header("Legal Advisory System v5.0 - Interactive Demo")

        print("This demo showcases the system's key capabilities:")
        print("  ✓ Natural language understanding")
        print("  ✓ Progressive information gathering")
        print("  ✓ 100% accurate legal calculations")
        print("  ✓ AI-enhanced explanations")
        print("  ✓ Conversational flow")
        print("  ✓ Error handling")

        demos = [
            ("Demo 1: Simple Query", self.demo_1_simple_query),
            ("Demo 2: Conversational Flow", self.demo_2_conversational),
            ("Demo 3: Complex Trial", self.demo_3_complex_trial),
            ("Demo 4: Unliquidated Claim", self.demo_4_unliquidated_claim),
            ("Demo 5: Summary Judgment", self.demo_5_summary_judgment),
            ("Demo 6: Error Handling", self.demo_6_error_handling),
        ]

        for i, (name, demo_func) in enumerate(demos, 1):
            self.print_header(f"{name} ({i}/{len(demos)})")
            await demo_func()

            # Pause between demos
            if i < len(demos):
                print("\n⏸️  Press Enter to continue to next demo...")
                input()

        self.print_header("Demo Complete!")
        print("All scenarios completed successfully.")
        print(f"\n📊 Statistics:")
        stats = self.conversation_manager.get_statistics()
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print()


async def main():
    """Main demo entry point"""
    demo = DemoRunner()

    print("\n" + "=" * 80)
    print("  Legal Advisory System v5.0 - Interactive Demo")
    print("=" * 80)
    print("\nOptions:")
    print("  1. Run all demos (recommended)")
    print("  2. Run specific demo")
    print("  3. Quick demo (Demo 1 only)")
    print()

    choice = input("Enter choice (1-3, or press Enter for option 1): ").strip() or "1"

    if choice == "1":
        await demo.run_all_demos()
    elif choice == "2":
        print("\nAvailable demos:")
        print("  1. Simple Query")
        print("  2. Conversational Flow")
        print("  3. Complex Trial")
        print("  4. Unliquidated Claim")
        print("  5. Summary Judgment")
        print("  6. Error Handling")
        demo_num = input("\nEnter demo number (1-6): ").strip()

        demo_map = {
            "1": demo.demo_1_simple_query,
            "2": demo.demo_2_conversational,
            "3": demo.demo_3_complex_trial,
            "4": demo.demo_4_unliquidated_claim,
            "5": demo.demo_5_summary_judgment,
            "6": demo.demo_6_error_handling,
        }

        if demo_num in demo_map:
            demo.print_header(f"Running Demo {demo_num}")
            await demo_map[demo_num]()
        else:
            print("Invalid choice. Running Demo 1 instead.")
            await demo.demo_1_simple_query()
    else:
        demo.print_header("Quick Demo")
        await demo.demo_1_simple_query()


if __name__ == "__main__":
    asyncio.run(main())
