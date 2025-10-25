"""
Comprehensive test suite for ModuleRegistry.

Tests all functionality including:
- Module registration and validation
- Module discovery and lookup
- Lifecycle management (status changes)
- Health checking
- Statistics and monitoring
- Error handling
"""

import pytest
from datetime import datetime
from backend.interfaces.legal_module import ILegalModule
from backend.interfaces.data_structures import (
    LogicTreeNode,
    ModuleMetadata,
    ModuleStatus,
    FieldRequirement,
    QuestionTemplate,
    MatchResult
)
from backend.common_services.logic_tree_framework import LogicTreeFramework
from backend.common_services.module_registry import ModuleRegistry, ModuleRegistration


# ==== MOCK MODULES FOR TESTING ====

class MockModule(ILegalModule):
    """Mock legal module for testing"""

    def __init__(
        self,
        module_id: str,
        module_name: str,
        tree_nodes: list = None,
        version: str = "1.0.0",
        tags: list = None,
        healthy: bool = True
    ):
        self._module_id = module_id
        self._module_name = module_name
        # Always provide at least one default node if none specified
        if tree_nodes is None:
            tree_nodes = [
                LogicTreeNode(
                    node_id=f"{module_id}-DEFAULT",
                    citation=f"Default node for {module_id}",
                    module_id=module_id,
                    what=[{"default": "content"}]
                )
            ]
        self._tree_nodes = tree_nodes
        self._version = version
        self._tags = tags or []
        self._healthy = healthy

    @property
    def metadata(self) -> ModuleMetadata:
        return ModuleMetadata(
            module_id=self._module_id,
            module_name=self._module_name,
            version=self._version,
            status=ModuleStatus.REGISTERED,
            author="Test Author",
            description=f"Test module {self._module_id}",
            effective_date="2024-01-01",
            last_updated="2024-10-26",
            dependencies=[],
            tags=self._tags
        )

    def get_tree_nodes(self) -> list:
        return self._tree_nodes

    def get_tree_version(self) -> str:
        return "1.0"

    def get_field_requirements(self) -> list:
        return []

    def get_question_templates(self) -> list:
        return []

    def validate_fields(self, fields: dict) -> tuple:
        return True, []

    def check_completeness(self, filled_fields: dict) -> tuple:
        return 1.0, []

    def calculate(self, fields: dict) -> dict:
        return {}

    def get_arguments(self, node_id: str) -> dict:
        return {}

    def get_recommendations(self, analysis_result: dict) -> list:
        return []

    async def health_check(self) -> bool:
        return self._healthy


# ==== FIXTURES ====

@pytest.fixture
def tree_framework():
    """Create a LogicTreeFramework for testing"""
    return LogicTreeFramework()


@pytest.fixture
def registry(tree_framework):
    """Create a ModuleRegistry with a tree framework"""
    return ModuleRegistry(tree_framework)


@pytest.fixture
def sample_nodes():
    """Create sample tree nodes"""
    return [
        LogicTreeNode(
            node_id="NODE-1",
            citation="Test Rule 1",
            module_id="TEST",
            what=[{"fact": "test fact"}]
        ),
        LogicTreeNode(
            node_id="NODE-2",
            citation="Test Rule 2",
            module_id="TEST",
            which=[{"scope": "test scope"}]
        )
    ]


@pytest.fixture
def sample_module(sample_nodes):
    """Create a sample module with nodes"""
    return MockModule(
        module_id="TEST_MODULE",
        module_name="Test Legal Module",
        tree_nodes=sample_nodes,
        tags=["test", "sample"]
    )


# ==== INITIALIZATION TESTS ====

def test_registry_initialization(tree_framework):
    """Test registry initializes correctly"""
    registry = ModuleRegistry(tree_framework)

    assert registry.tree_framework is tree_framework
    assert len(registry.list_modules()) == 0


def test_registry_requires_tree_framework():
    """Test registry requires LogicTreeFramework"""
    with pytest.raises(TypeError, match="must be LogicTreeFramework"):
        ModuleRegistry("not a framework")


# ==== REGISTRATION TESTS ====

def test_register_valid_module(registry, sample_module):
    """Test registering a valid module"""
    registry.register_module(sample_module, auto_activate=False)

    assert registry.is_registered("TEST_MODULE")
    assert len(registry.list_modules()) == 1


def test_register_module_auto_activate(registry, sample_module):
    """Test module is auto-activated by default"""
    registry.register_module(sample_module, auto_activate=True)

    metadata = registry.get_module_metadata("TEST_MODULE")
    assert metadata.status == ModuleStatus.ACTIVE


def test_register_module_with_minimal_tree(registry, tree_framework):
    """Test registering module with minimal tree (single node)"""
    minimal_module = MockModule(
        module_id="MINIMAL",
        module_name="Minimal Module",
        tree_nodes=[
            LogicTreeNode(
                node_id="MIN-1",
                citation="Minimal Rule",
                module_id="MINIMAL",
                what=[{"fact": "minimal"}]
            )
        ]
    )

    # Should succeed
    registry.register_module(minimal_module, auto_activate=False)
    assert registry.is_registered("MINIMAL")


def test_register_invalid_module_type(registry):
    """Test registering non-ILegalModule fails"""
    with pytest.raises(TypeError, match="must implement ILegalModule"):
        registry.register_module("not a module")


def test_register_duplicate_module_id(registry, sample_module):
    """Test registering same module_id twice fails"""
    registry.register_module(sample_module, auto_activate=False)

    with pytest.raises(ValueError, match="already registered"):
        registry.register_module(sample_module, auto_activate=False)


def test_register_module_registers_tree(registry, sample_module, tree_framework):
    """Test module registration also registers tree"""
    registry.register_module(sample_module, auto_activate=False)

    # Check tree was registered
    tree_modules = tree_framework.get_registered_modules()
    assert "TEST_MODULE" in tree_modules

    # Check tree nodes are accessible
    tree = tree_framework.get_module_tree("TEST_MODULE")
    assert len(tree) == 2


def test_register_module_updates_statistics(registry, sample_module):
    """Test registration updates statistics"""
    stats_before = registry.get_statistics()

    registry.register_module(sample_module, auto_activate=False)

    stats_after = registry.get_statistics()
    assert stats_after["total_modules"] == stats_before["total_modules"] + 1
    assert stats_after["total_tree_nodes"] == stats_before["total_tree_nodes"] + 2


# ==== LOOKUP AND DISCOVERY TESTS ====

def test_get_module(registry, sample_module):
    """Test getting a registered module"""
    registry.register_module(sample_module, auto_activate=False)

    module = registry.get_module("TEST_MODULE")
    assert module is sample_module


def test_get_module_not_found(registry):
    """Test getting non-existent module returns None"""
    module = registry.get_module("NONEXISTENT")
    assert module is None


def test_get_module_metadata(registry, sample_module):
    """Test getting module metadata"""
    registry.register_module(sample_module, auto_activate=False)

    metadata = registry.get_module_metadata("TEST_MODULE")
    assert metadata.module_id == "TEST_MODULE"
    assert metadata.module_name == "Test Legal Module"


def test_is_registered(registry, sample_module):
    """Test checking if module is registered"""
    assert not registry.is_registered("TEST_MODULE")

    registry.register_module(sample_module, auto_activate=False)

    assert registry.is_registered("TEST_MODULE")


def test_list_all_modules(registry):
    """Test listing all modules"""
    mod1 = MockModule("MOD1", "Module 1", tags=["tag1"])
    mod2 = MockModule("MOD2", "Module 2", tags=["tag2"])

    registry.register_module(mod1, auto_activate=False)
    registry.register_module(mod2, auto_activate=False)

    modules = registry.list_modules()
    assert len(modules) == 2
    assert "MOD1" in modules
    assert "MOD2" in modules


def test_list_modules_by_status(registry):
    """Test listing modules filtered by status"""
    mod1 = MockModule("MOD1", "Module 1")
    mod2 = MockModule("MOD2", "Module 2")

    registry.register_module(mod1, auto_activate=True)  # Will be ACTIVE
    registry.register_module(mod2, auto_activate=False)  # Will be REGISTERED

    active_modules = registry.list_modules(status=ModuleStatus.ACTIVE)
    assert len(active_modules) == 1
    assert "MOD1" in active_modules

    registered_modules = registry.list_modules(status=ModuleStatus.REGISTERED)
    assert len(registered_modules) == 1
    assert "MOD2" in registered_modules


def test_list_modules_by_tags(registry):
    """Test listing modules filtered by tags"""
    mod1 = MockModule("MOD1", "Module 1", tags=["costs", "singapore"])
    mod2 = MockModule("MOD2", "Module 2", tags=["discovery", "uk"])
    mod3 = MockModule("MOD3", "Module 3", tags=["costs", "uk"])

    registry.register_module(mod1, auto_activate=False)
    registry.register_module(mod2, auto_activate=False)
    registry.register_module(mod3, auto_activate=False)

    # Find modules with 'costs' tag
    costs_modules = registry.list_modules(tags=["costs"])
    assert len(costs_modules) == 2
    assert "MOD1" in costs_modules
    assert "MOD3" in costs_modules

    # Find modules with 'uk' tag
    uk_modules = registry.list_modules(tags=["uk"])
    assert len(uk_modules) == 2
    assert "MOD2" in uk_modules
    assert "MOD3" in uk_modules


def test_list_all_modules_metadata(registry):
    """Test getting metadata for all modules"""
    mod1 = MockModule("MOD1", "Module 1")
    mod2 = MockModule("MOD2", "Module 2")

    registry.register_module(mod1, auto_activate=False)
    registry.register_module(mod2, auto_activate=False)

    all_metadata = registry.list_all_modules()
    assert len(all_metadata) == 2
    assert all(isinstance(m, ModuleMetadata) for m in all_metadata)


# ==== LIFECYCLE MANAGEMENT TESTS ====

def test_set_module_status_registered_to_active(registry, sample_module):
    """Test transitioning from REGISTERED to ACTIVE"""
    registry.register_module(sample_module, auto_activate=False)

    registry.set_module_status("TEST_MODULE", ModuleStatus.ACTIVE)

    metadata = registry.get_module_metadata("TEST_MODULE")
    assert metadata.status == ModuleStatus.ACTIVE


def test_set_module_status_active_to_disabled(registry, sample_module):
    """Test transitioning from ACTIVE to DISABLED"""
    registry.register_module(sample_module, auto_activate=True)

    registry.set_module_status("TEST_MODULE", ModuleStatus.DISABLED)

    metadata = registry.get_module_metadata("TEST_MODULE")
    assert metadata.status == ModuleStatus.DISABLED


def test_set_module_status_disabled_to_active(registry, sample_module):
    """Test transitioning from DISABLED back to ACTIVE"""
    registry.register_module(sample_module, auto_activate=True)
    registry.set_module_status("TEST_MODULE", ModuleStatus.DISABLED)

    registry.set_module_status("TEST_MODULE", ModuleStatus.ACTIVE)

    metadata = registry.get_module_metadata("TEST_MODULE")
    assert metadata.status == ModuleStatus.ACTIVE


def test_set_module_status_to_deprecated(registry, sample_module):
    """Test transitioning to DEPRECATED (one-way)"""
    registry.register_module(sample_module, auto_activate=True)

    registry.set_module_status("TEST_MODULE", ModuleStatus.DEPRECATED)

    metadata = registry.get_module_metadata("TEST_MODULE")
    assert metadata.status == ModuleStatus.DEPRECATED


def test_set_module_status_cannot_undeprecate(registry, sample_module):
    """Test cannot transition from DEPRECATED to anything else"""
    registry.register_module(sample_module, auto_activate=True)
    registry.set_module_status("TEST_MODULE", ModuleStatus.DEPRECATED)

    with pytest.raises(ValueError, match="Invalid status transition"):
        registry.set_module_status("TEST_MODULE", ModuleStatus.ACTIVE)


def test_set_module_status_invalid_transition(registry, sample_module):
    """Test invalid status transitions are rejected"""
    registry.register_module(sample_module, auto_activate=False)

    # Cannot go from REGISTERED to DISABLED
    with pytest.raises(ValueError, match="Invalid status transition"):
        registry.set_module_status("TEST_MODULE", ModuleStatus.DISABLED)


def test_set_module_status_not_registered(registry):
    """Test setting status of non-existent module fails"""
    with pytest.raises(KeyError, match="not registered"):
        registry.set_module_status("NONEXISTENT", ModuleStatus.ACTIVE)


def test_set_module_status_updates_indices(registry, sample_module):
    """Test status change updates status indices"""
    registry.register_module(sample_module, auto_activate=False)

    # Should be in REGISTERED list
    registered = registry.list_modules(status=ModuleStatus.REGISTERED)
    assert "TEST_MODULE" in registered

    # Change to ACTIVE
    registry.set_module_status("TEST_MODULE", ModuleStatus.ACTIVE)

    # Should now be in ACTIVE list, not REGISTERED
    active = registry.list_modules(status=ModuleStatus.ACTIVE)
    registered = registry.list_modules(status=ModuleStatus.REGISTERED)

    assert "TEST_MODULE" in active
    assert "TEST_MODULE" not in registered


# ==== UNREGISTRATION TESTS ====

def test_unregister_module(registry, sample_module):
    """Test unregistering a module"""
    registry.register_module(sample_module, auto_activate=False)
    assert registry.is_registered("TEST_MODULE")

    registry.unregister_module("TEST_MODULE")

    assert not registry.is_registered("TEST_MODULE")
    assert len(registry.list_modules()) == 0


def test_unregister_module_not_registered(registry):
    """Test unregistering non-existent module fails"""
    with pytest.raises(KeyError, match="not registered"):
        registry.unregister_module("NONEXISTENT")


def test_unregister_removes_from_indices(registry):
    """Test unregistration removes from all indices"""
    mod = MockModule("MOD1", "Module 1", tags=["test"])
    registry.register_module(mod, auto_activate=True)

    # Should be in indices
    assert "MOD1" in registry.list_modules(status=ModuleStatus.ACTIVE)
    assert "MOD1" in registry.list_modules(tags=["test"])

    registry.unregister_module("MOD1")

    # Should be removed from all indices
    assert "MOD1" not in registry.list_modules(status=ModuleStatus.ACTIVE)
    assert "MOD1" not in registry.list_modules(tags=["test"])


# ==== HEALTH CHECK TESTS ====

@pytest.mark.asyncio
async def test_health_check_healthy_module(registry):
    """Test health check on healthy module"""
    healthy_module = MockModule("HEALTHY", "Healthy Module", healthy=True)
    registry.register_module(healthy_module, auto_activate=False)

    is_healthy = await registry.health_check_module("HEALTHY")

    assert is_healthy is True


@pytest.mark.asyncio
async def test_health_check_unhealthy_module(registry):
    """Test health check on unhealthy module"""
    unhealthy_module = MockModule("UNHEALTHY", "Unhealthy Module", healthy=False)
    registry.register_module(unhealthy_module, auto_activate=False)

    is_healthy = await registry.health_check_module("UNHEALTHY")

    assert is_healthy is False


@pytest.mark.asyncio
async def test_health_check_updates_registration(registry):
    """Test health check updates registration record"""
    module = MockModule("TEST", "Test Module", healthy=True)
    registry.register_module(module, auto_activate=False)

    await registry.health_check_module("TEST")

    info = registry.get_module_registration_info("TEST")
    assert info["health_status"] == "healthy"
    assert info["last_health_check"] is not None


@pytest.mark.asyncio
async def test_health_check_not_registered(registry):
    """Test health check on non-existent module fails"""
    with pytest.raises(KeyError, match="not registered"):
        await registry.health_check_module("NONEXISTENT")


@pytest.mark.asyncio
async def test_health_check_all(registry):
    """Test health check on all modules"""
    mod1 = MockModule("MOD1", "Module 1", healthy=True)
    mod2 = MockModule("MOD2", "Module 2", healthy=False)
    mod3 = MockModule("MOD3", "Module 3", healthy=True)

    registry.register_module(mod1, auto_activate=False)
    registry.register_module(mod2, auto_activate=False)
    registry.register_module(mod3, auto_activate=False)

    results = await registry.health_check_all()

    assert len(results) == 3
    assert results["MOD1"] is True
    assert results["MOD2"] is False
    assert results["MOD3"] is True


# ==== STATISTICS TESTS ====

def test_get_statistics_empty_registry(registry):
    """Test statistics for empty registry"""
    stats = registry.get_statistics()

    assert stats["total_modules"] == 0
    assert stats["total_registrations"] == 0
    assert stats["total_tree_nodes"] == 0
    assert stats["active_modules"] == 0


def test_get_statistics_with_modules(registry):
    """Test statistics with registered modules"""
    nodes1 = [
        LogicTreeNode("N1", "Citation 1", "MOD1", what=[{"a": "b"}]),
        LogicTreeNode("N2", "Citation 2", "MOD1", what=[{"c": "d"}]),
        LogicTreeNode("N3", "Citation 3", "MOD1", what=[{"e": "f"}])
    ]
    nodes2 = [
        LogicTreeNode("N4", "Citation 4", "MOD2", what=[{"g": "h"}])
    ]
    mod1 = MockModule("MOD1", "Module 1", tree_nodes=nodes1)
    mod2 = MockModule("MOD2", "Module 2", tree_nodes=nodes2)

    registry.register_module(mod1, auto_activate=True)
    registry.register_module(mod2, auto_activate=False)

    stats = registry.get_statistics()

    assert stats["total_modules"] == 2
    assert stats["total_tree_nodes"] == 4  # 3 + 1
    assert stats["active_modules"] == 1
    assert stats["modules_by_status"][ModuleStatus.ACTIVE.value] == 1
    assert stats["modules_by_status"][ModuleStatus.REGISTERED.value] == 1


def test_get_module_registration_info(registry, sample_module):
    """Test getting detailed registration info"""
    registry.register_module(sample_module, auto_activate=True)

    info = registry.get_module_registration_info("TEST_MODULE")

    assert info is not None
    assert info["module_id"] == "TEST_MODULE"
    assert info["module_name"] == "Test Legal Module"
    assert info["version"] == "1.0.0"
    assert info["status"] == ModuleStatus.ACTIVE.value
    assert info["tree_node_count"] == 2
    assert "registered_at" in info
    assert info["tags"] == ["test", "sample"]


def test_get_module_registration_info_not_found(registry):
    """Test getting info for non-existent module"""
    info = registry.get_module_registration_info("NONEXISTENT")
    assert info is None


# ==== INTEGRATION TESTS ====

def test_full_module_lifecycle(registry):
    """Test complete module lifecycle"""
    module = MockModule("LIFECYCLE", "Lifecycle Module", tree_nodes=[
        LogicTreeNode("N1", "Citation", "LIFECYCLE", what=[{"test": "data"}])
    ])

    # 1. Register
    registry.register_module(module, auto_activate=False)
    assert registry.is_registered("LIFECYCLE")
    assert registry.get_module_metadata("LIFECYCLE").status == ModuleStatus.REGISTERED

    # 2. Activate
    registry.set_module_status("LIFECYCLE", ModuleStatus.ACTIVE)
    assert registry.get_module_metadata("LIFECYCLE").status == ModuleStatus.ACTIVE

    # 3. Disable
    registry.set_module_status("LIFECYCLE", ModuleStatus.DISABLED)
    assert registry.get_module_metadata("LIFECYCLE").status == ModuleStatus.DISABLED

    # 4. Reactivate
    registry.set_module_status("LIFECYCLE", ModuleStatus.ACTIVE)
    assert registry.get_module_metadata("LIFECYCLE").status == ModuleStatus.ACTIVE

    # 5. Deprecate (one-way)
    registry.set_module_status("LIFECYCLE", ModuleStatus.DEPRECATED)
    assert registry.get_module_metadata("LIFECYCLE").status == ModuleStatus.DEPRECATED

    # 6. Unregister
    registry.unregister_module("LIFECYCLE")
    assert not registry.is_registered("LIFECYCLE")


def test_multiple_modules_with_tree_integration(registry, tree_framework):
    """Test multiple modules integrating with tree framework"""
    # Create multiple modules with different trees
    mod1_nodes = [
        LogicTreeNode("M1-N1", "Citation 1", "MOD1", what=[{"a": "1"}]),
        LogicTreeNode("M1-N2", "Citation 2", "MOD1", which=[{"b": "2"}])
    ]
    mod2_nodes = [
        LogicTreeNode("M2-N1", "Citation 1", "MOD2", if_then=[{"c": "3"}])
    ]

    mod1 = MockModule("MOD1", "Module 1", tree_nodes=mod1_nodes, tags=["tag1"])
    mod2 = MockModule("MOD2", "Module 2", tree_nodes=mod2_nodes, tags=["tag2"])

    # Register both
    registry.register_module(mod1, auto_activate=True)
    registry.register_module(mod2, auto_activate=True)

    # Verify both are registered
    assert len(registry.list_modules()) == 2

    # Verify trees are registered in framework
    framework_modules = tree_framework.get_registered_modules()
    assert "MOD1" in framework_modules
    assert "MOD2" in framework_modules

    # Verify can retrieve trees
    tree1 = tree_framework.get_module_tree("MOD1")
    tree2 = tree_framework.get_module_tree("MOD2")
    assert len(tree1) == 2
    assert len(tree2) == 1

    # Verify tag-based lookup
    tag1_modules = registry.list_modules(tags=["tag1"])
    assert "MOD1" in tag1_modules
    assert "MOD2" not in tag1_modules
