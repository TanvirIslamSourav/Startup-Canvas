# AI Advisor Provider

> Swappable strategy for startup recommendations. **Today only the mock provider runs** — and that's by design.

---

## 1. Interface

`backend/app/ai/provider.py` defines:

```python
from typing import Protocol, TypedDict

class AdviceItem(TypedDict):
    title: str
    detail: str
    confidence: float

class AdviceResult(TypedDict):
    provider: str
    model: str
    content: list[AdviceItem]
    generated_at: str  # ISO 8601

class StartupAdvisorProvider(Protocol):
    name: str

    async def validate(self, idea: dict) -> AdviceResult: ...
    async def swot_suggestions(self, idea: dict) -> AdviceResult: ...
    async def risk_suggestions(self, idea: dict) -> AdviceResult: ...
    async def competitor_recommendations(self, idea: dict, market: str | None) -> AdviceResult: ...
    async def growth_roadmap(self, idea: dict) -> AdviceResult: ...
```

All methods are `async` to match what a real provider will look like (network call).

---

## 2. Dependency injection

Routers declare the provider via FastAPI dependency:

```python
from app.ai.provider import get_advisor_provider

@router.post("/validate")
async def validate(
    payload: IdeaRef,
    provider: StartupAdvisorProvider = Depends(get_advisor_provider),
): ...
```

`get_advisor_provider()` reads `STARTUP_ADVISOR_PROVIDER` (default `mock`) and returns the registered instance. There is **one global instance** (singleton) per process.

The router never imports a concrete class. Swapping providers = change one env var.

---

## 3. Mock implementation

`backend/app/ai/mock.py` reads from `backend/data/ai/<capability>.json` and returns canned suggestions based on simple keyword matching on the idea title/problem/solution.

Files:

```
backend/data/ai/
├── validate.json
├── swot.json
├── risks.json
├── competitors.json
└── growth.json
```

Each file is a `{ "<keyword>": [AdviceItem, ...], "_default": [...] }` map. Adding a new keyword‑targeted suggestion is a one‑file PR.

---

## 4. Future providers (stubs in place)

`backend/app/ai/{openai,gemini,claude,groq,ollama}.py` each export a class that raises `NotConfiguredError` with a helpful message. The shape matches the Protocol so that wiring one up later is purely additive:

```python
# example
class OpenAIProvider:
    name = "openai"
    async def validate(self, idea): raise NotConfiguredError("OpenAIProvider not configured")
```

Activation (later) will require:

1. Implementing the methods.
2. Reading the provider's API key from env.
3. Setting `STARTUP_ADVISOR_PROVIDER=openai` in `.env`.

No router or frontend changes are needed.

---

## 5. Why this design?

- **Testability** — the mock is deterministic and offline‑friendly; tests don't need network mocks.
- **Resilience** — if the real provider is down, falling back to mock is one env var.
- **Cost control** — development never accidentally hits a paid API.
- **Forward compatibility** — UI and business logic don't change when a real provider lands.

---

## 6. Adding a new capability

1. Add method to `StartupAdvisorProvider` Protocol.
2. Add stub implementations in all provider classes (raise `NotConfiguredError`).
3. Implement in `MockStartupAdvisorProvider` (read from a new JSON file).
4. Add a router endpoint that uses it.
5. Add a frontend button + query.