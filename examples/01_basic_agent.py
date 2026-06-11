"""Basic single-agent example.

Runs end-to-end with a stubbed LLM so it works without any API keys.
To use a real model, drop the `completion_fn` argument - ArabicAgent will
call litellm with `model="gemini/gemini-2.5-flash"` (or "gpt-4o", "qwen2.5", ...)
using whichever provider credentials are configured in your environment.
"""

from arabic_agentforge import ArabicAgent
from arabic_agentforge.guards import ArabicHallucinationGuard, Citation


def fake_completion(**kwargs):
    """Stand-in for `litellm.completion` so this example runs offline."""
    return {
        "choices": [
            {
                "finish_reason": "stop",
                "message": {
                    "role": "assistant",
                    "content": "تم إنشاء طلب صيانة لطابعة القسم الثالث بنجاح [1].",
                },
            }
        ]
    }


agent = ArabicAgent(
    name="inventory-agent",
    model="gemini/gemini-2.5-flash",  # or "qwen2.5", "gpt-4o"
    dialect="gulf",
    hallucination_guard=ArabicHallucinationGuard(
        citation_required=True,
        confidence_threshold=0.85,
    ),
    completion_fn=fake_completion,
)

sources = [Citation(source="ERPNext Issue #442", excerpt="Maintenance ticket created for printer in dept. 3")]

result = agent.run("سوّ لي تذكرة صيانة لطابعة القسم الثالث", sources=sources)

print("Response:", result.response)
print("Detected dialect:", result.detected_dialect.value)
print("Citations:", [c.source for c in result.citations])
print("Guard result:", result.guard_result)
