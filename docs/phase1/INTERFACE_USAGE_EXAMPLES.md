# Interface Usage Examples
## Legal Advisory System v5.0

This document provides practical examples of how to use each interface in the system.

---

## 1. ILegalModule Interface

### Basic Implementation
```python
from backend.interfaces.legal_module import ILegalModule, ModuleMetadata
from backend.interfaces.data_structures import LogicTreeNode
from typing import List, Dict, Any

class Order21Module(ILegalModule):
    """Implementation for Singapore Rules of Court Order 21"""
    
    def __init__(self):
        self._metadata = ModuleMetadata(
            module_id="ORDER_21",
            name="Order 21 - Costs",
            version="1.0.0",
            description="Singapore legal costs calculation"
        )
        self._tree = self._build_logic_tree()
    
    @property
    def metadata(self) -> ModuleMetadata:
        return self._metadata
    
    def get_tree_nodes(self) -> List[LogicTreeNode]:
        return self._tree
    
    def _build_logic_tree(self) -> List[LogicTreeNode]:
        # Build your logic tree here
        return [
            LogicTreeNode(
                node_id="O21_FIXED_COSTS",
                citation="Order 21 Rule 2",
                module_id="ORDER_21"
            )
        ]
    
    async def health_check(self) -> bool:
        return len(self._tree) > 0
```

### Using the Module
```python
# Instantiate the module
module = Order21Module()

# Get metadata
print(f"Module: {module.metadata.name}")
print(f"Version: {module.metadata.version}")

# Get logic tree
nodes = module.get_tree_nodes()
print(f"Tree has {len(nodes)} nodes")

# Check health
is_healthy = await module.health_check()
```

---

## 2. IMatchingEngine Interface

### Basic Implementation
```python
from backend.interfaces.matching import IMatchingEngine
from backend.interfaces.data_structures import MatchResult
from typing import List, Dict, Any

class SimpleMatchingEngine(IMatchingEngine):
    """Simple keyword-based matching"""
    
    async def match(
        self,
        filled_fields: Dict[str, Any],
        tree_nodes: List[LogicTreeNode],
        threshold: float = 0.6
    ) -> List[MatchResult]:
        matches = []
        
        for node in tree_nodes:
            score = self._calculate_score(filled_fields, node)
            
            if score >= threshold:
                matches.append(MatchResult(
                    node_id=node.node_id,
                    node=node,
                    match_score=score,
                    matched_fields=filled_fields.copy(),
                    missing_fields=[],
                    confidence=score,
                    reasoning=f"Matched with {score:.2f} confidence"
                ))
        
        return sorted(matches, key=lambda x: x.confidence, reverse=True)
    
    def _calculate_score(self, fields: Dict, node: LogicTreeNode) -> float:
        # Your scoring logic here
        return 0.75
    
    async def health_check(self) -> bool:
        return True
```

### Using the Matching Engine
```python
# Create engine
matcher = SimpleMatchingEngine()

# Prepare data
user_data = {
    "court_level": "HIGH_COURT",
    "case_type": "TRIAL",
    "party_count": 2
}

tree_nodes = module.get_tree_nodes()

# Match
matches = await matcher.match(
    filled_fields=user_data,
    tree_nodes=tree_nodes,
    threshold=0.6
)

# Process results
for match in matches:
    print(f"Node: {match.node_id}")
    print(f"Confidence: {match.confidence:.2f}")
    print(f"Reasoning: {match.reasoning}")
```

---

## 3. IAIService Interface

### Basic Implementation
```python
from backend.interfaces.ai_service import IAIService, AIRequest, AIResponse
from backend.interfaces.data_structures import AIServiceType

class OpenAIService(IAIService):
    """OpenAI GPT integration"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
    
    async def generate(self, request: AIRequest) -> AIResponse:
        """Generate AI response"""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": request.system_prompt or ""},
                    {"role": "user", "content": request.prompt}
                ]
            )
            
            return AIResponse(
                content=response.choices[0].message.content,
                service_type=request.service_type,
                model="gpt-4",
                tokens_used=response.usage.total_tokens,
                success=True
            )
        except Exception as e:
            return AIResponse(
                content="",
                service_type=request.service_type,
                model="gpt-4",
                tokens_used=0,
                success=False,
                error_message=str(e)
            )
    
    async def health_check(self) -> bool:
        try:
            await self.generate(AIRequest(
                prompt="test",
                service_type=AIServiceType.CONVERSATION
            ))
            return True
        except:
            return False
```

### Using AI Service
```python
# Create service
ai = OpenAIService(api_key="your-key")

# Create request
request = AIRequest(
    prompt="Explain fixed costs in Order 21",
    service_type=AIServiceType.EXPLANATION,
    context={"court": "HIGH_COURT"},
    system_prompt="You are a legal advisor"
)

# Generate response
response = await ai.generate(request)

if response.success:
    print(response.content)
    print(f"Used {response.tokens_used} tokens")
else:
    print(f"Error: {response.error_message}")
```

---

## 4. Polymorphic Usage

### Swapping Implementations
```python
# Define function that works with any matching engine
async def find_best_match(
    engine: IMatchingEngine,  # Works with ANY implementation!
    user_data: Dict[str, Any],
    nodes: List[LogicTreeNode]
) -> Optional[MatchResult]:
    matches = await engine.match(user_data, nodes, threshold=0.7)
    return matches[0] if matches else None

# Use with different engines
simple_engine = SimpleMatchingEngine()
advanced_engine = AdvancedMatchingEngine()
mock_engine = MockMatchingEngine()

# All work the same way!
match1 = await find_best_match(simple_engine, data, nodes)
match2 = await find_best_match(advanced_engine, data, nodes)
match3 = await find_best_match(mock_engine, data, nodes)
```

---

## 5. Complete Workflow Example
```python
async def complete_legal_advisory_workflow():
    """Demonstrates complete system workflow"""
    
    # 1. Initialize components
    module = Order21Module()
    matcher = AdvancedMatchingEngine()
    validator = LegalValidator()
    calculator = Order21Calculator()
    ai = ClaudeAIService()
    
    # 2. Get user input
    user_input = {
        "court_level": "HIGH_COURT",
        "case_type": "DEFAULT_JUDGMENT",
        "party_count": 1
    }
    
    # 3. Validate input
    is_valid = await validator.validate(user_input, module.metadata)
    if not is_valid:
        return "Invalid input"
    
    # 4. Get tree nodes
    nodes = module.get_tree_nodes()
    
    # 5. Match to logic tree
    matches = await matcher.match(user_input, nodes, threshold=0.7)
    if not matches:
        return "No matching rules found"
    
    best_match = matches[0]
    
    # 6. Calculate costs
    result = await calculator.calculate(
        node=best_match.node,
        filled_fields=user_input
    )
    
    # 7. Enhance with AI explanation
    ai_request = AIRequest(
        prompt=f"Explain this cost calculation: {result}",
        service_type=AIServiceType.EXPLANATION,
        context=user_input
    )
    
    explanation = await ai.generate(ai_request)
    
    # 8. Return complete result
    return {
        "costs": result,
        "explanation": explanation.content,
        "citation": best_match.node.citation,
        "confidence": best_match.confidence
    }

# Run the workflow
result = await complete_legal_advisory_workflow()
print(result)
```

---

## 6. Testing with Mocks
```python
import pytest
from backend.emulators import MockLegalModule, MockMatchingEngine

@pytest.mark.asyncio
async def test_matching_workflow():
    """Test matching workflow with mocks"""
    
    # Use mocks for fast, isolated testing
    module = MockLegalModule()
    matcher = MockMatchingEngine()
    
    # Get test data
    nodes = module.get_tree_nodes()
    user_data = {"test": "data"}
    
    # Perform matching
    matches = await matcher.match(user_data, nodes)
    
    # Verify results
    assert len(matches) > 0
    assert matches[0].confidence > 0.5
    assert matches[0].node_id in [n.node_id for n in nodes]
```

---

## 7. Configuration Usage
```python
from backend.config.settings import get_settings, Environment

# Get settings based on environment
settings = get_settings()

# Access configuration
if settings.environment == Environment.DEVELOPMENT:
    # Use emulators in development
    ai_service = MockAIService() if settings.use_ai_emulator else ClaudeAIService()
else:
    # Use real services in production
    ai_service = ClaudeAIService()

# Check debug flags
if settings.debug_enabled:
    print(f"Debug level: {settings.debug_level}")
    if settings.trace_ai_calls:
        print("AI tracing enabled")
```

---

## Best Practices

1. **Always use type hints** - Helps catch errors early
2. **Implement health_check()** - Enables monitoring
3. **Handle errors gracefully** - Return error responses, don't crash
4. **Use mocks for testing** - Fast, isolated, deterministic
5. **Follow interface contracts** - Don't add required parameters
6. **Document your implementations** - Help future developers

---

*Document Version: 1.0*  
*Last Updated: $(date)*
