#!/usr/bin/env python3
"""
Test script for case law integration with logic tree nodes.
Tests that enhanced nodes have case_law_references and they work correctly.
"""

import sys
sys.path.insert(0, '/home/claude/legal-advisory-v5')

from backend.modules.order_21.order21_module import Order21Module
from backend.modules.order_21.case_law_manager import get_case_law_manager
from backend.modules.order_21.rule_to_case_mapping import get_mapping_statistics

def test_enhanced_nodes():
    """Test that enhanced nodes are loaded with case law references"""
    print("=" * 80)
    print("TEST 1: Enhanced Nodes with Case Law References")
    print("=" * 80)

    module = Order21Module()
    nodes = module.get_tree_nodes()

    print(f"\n✓ Total nodes loaded: {len(nodes)}")

    # Check for enhanced nodes
    enhanced_nodes = [n for n in nodes if hasattr(n, 'case_law_references') and n.case_law_references]

    print(f"✓ Nodes with case law references: {len(enhanced_nodes)}")

    for node in enhanced_nodes:
        print(f"\n  Node: {node.node_id}")
        print(f"  Citation: {node.citation}")
        print(f"  Case Law References ({len(node.case_law_references)}): {', '.join(node.case_law_references)}")

    return len(enhanced_nodes) > 0


def test_case_law_retrieval():
    """Test that case law can be retrieved by ID"""
    print("\n" + "=" * 80)
    print("TEST 2: Case Law Retrieval by ID")
    print("=" * 80)

    manager = get_case_law_manager()

    # Test retrieving specific cases
    test_cases = [
        "2024_SGHC_146",  # Tjiang Giok Moy
        "2023_SGCA_40",   # Founder Group
        "2025_SGHCR_18_indemnity",  # Armira Capital
    ]

    for case_id in test_cases:
        case = manager._get_case_by_id(case_id)
        if case:
            print(f"\n✓ Retrieved case: {case_id}")
            print(f"  Short Name: {case.short_name}")
            print(f"  Citation: {case.citation}")
            print(f"  Provision: {case.provision}")
        else:
            print(f"\n✗ FAILED to retrieve case: {case_id}")
            return False

    return True


def test_get_relevant_case_law():
    """Test Order21Module.get_relevant_case_law() with node references"""
    print("\n" + "=" * 80)
    print("TEST 3: Get Relevant Case Law with Node References")
    print("=" * 80)

    module = Order21Module()
    nodes = module.get_tree_nodes()

    # Find a node with case law references
    test_node = None
    for node in nodes:
        if hasattr(node, 'case_law_references') and node.case_law_references:
            test_node = node
            break

    if not test_node:
        print("\n✗ No nodes with case law references found")
        return False

    print(f"\n✓ Testing with node: {test_node.node_id}")
    print(f"  Node has {len(test_node.case_law_references)} case law references")

    # Test getting case law with matched nodes
    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment",
        "claim_amount": 50000
    }

    case_law = module.get_relevant_case_law(
        filled_fields=filled_fields,
        max_cases=3,
        matched_nodes=[test_node]
    )

    print(f"\n✓ Retrieved {len(case_law)} cases")
    for i, case in enumerate(case_law, 1):
        print(f"\n  Case {i}:")
        print(f"    Short Name: {case.get('short_name')}")
        print(f"    Citation: {case.get('citation')}")
        print(f"    Principle: {case.get('principle', 'N/A')[:80]}...")

    return len(case_law) > 0


def test_mapping_statistics():
    """Test mapping statistics"""
    print("\n" + "=" * 80)
    print("TEST 4: Mapping Statistics")
    print("=" * 80)

    stats = get_mapping_statistics()

    print(f"\n✓ Total nodes mapped: {stats['total_nodes_mapped']}")
    print(f"✓ Total cases used: {stats['total_cases_used']}")
    print(f"✓ Total provisions mapped: {stats['total_provisions_mapped']}")
    print(f"✓ Avg cases per node: {stats['avg_cases_per_node']:.2f}")

    return stats['total_nodes_mapped'] > 0


def test_end_to_end_calculation():
    """Test end-to-end calculation with case law"""
    print("\n" + "=" * 80)
    print("TEST 5: End-to-End Calculation with Case Law")
    print("=" * 80)

    module = Order21Module()

    filled_fields = {
        "court_level": "High Court",
        "case_type": "default_judgment_liquidated",
        "claim_amount": 50000,
        "basis_of_taxation": "standard",
        "party_type": "plaintiff"
    }

    result = module.calculate(filled_fields)

    print(f"\n✓ Calculation completed")
    print(f"  Total Costs: ${result['total_costs']}")
    print(f"  Case Law Provided: {len(result.get('case_law', []))} cases")

    if result.get('case_law'):
        print(f"\n  Cases Cited:")
        for case in result['case_law']:
            print(f"    - {case.get('short_name')} {case.get('citation')}")

    return 'case_law' in result and len(result['case_law']) > 0


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("CASE LAW INTEGRATION TEST SUITE")
    print("=" * 80)

    tests = [
        ("Enhanced Nodes", test_enhanced_nodes),
        ("Case Law Retrieval", test_case_law_retrieval),
        ("Get Relevant Case Law", test_get_relevant_case_law),
        ("Mapping Statistics", test_mapping_statistics),
        ("End-to-End Calculation", test_end_to_end_calculation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n✗ TEST FAILED: {test_name}")
            print(f"  Error: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")

    print(f"\n{passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Case law integration is working correctly.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
