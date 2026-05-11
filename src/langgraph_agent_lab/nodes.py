"""Node skeletons for the LangGraph workflow.

Each function should be small, testable, and return a partial state update. Avoid mutating the
input state in place.
"""

from __future__ import annotations

import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from .state import AgentState, ApprovalDecision, Route, make_event

# Module-level classification constants to prevent N806 lint alerts
RISKY_KW = frozenset({"refund", "delete", "send", "cancel", "remove", "revoke"})
TOOL_KW = frozenset({"status", "order", "lookup", "check", "track", "find", "search"})
ERROR_KW = frozenset({"timeout", "fail", "error", "crash", "unavailable", "failure"})


def intake_node(state: AgentState) -> dict:
    """Normalize raw query into state fields."""
    t0 = time.monotonic()
    query = state.get("query", "").strip()
    
    latency_ms = int((time.monotonic() - t0) * 1000)
    return {
        "query": query,
        "messages": [f"intake:{query[:40]}"],
        "latency_log": [{"node": "intake", "latency_ms": latency_ms}],
        "events": [make_event("intake", "completed", "query normalized")],
    }


def classify_node(state: AgentState) -> dict:
    """Classify the query into a route with strong keyword-based heuristic logic."""
    t0 = time.monotonic()
    query = state.get("query", "").lower()
    
    # Word boundary extraction by stripping common punctuation symbols and splitting
    words = set(re.sub(r"[?!.,;:]", "", query).split())
    
    route = Route.SIMPLE
    risk_level = "low"
    
    if words & RISKY_KW:
        route, risk_level = Route.RISKY, "high"
    elif words & TOOL_KW:
        route, risk_level = Route.TOOL, "medium"
    elif len(words) < 5 and "it" in words:
        route, risk_level = Route.MISSING_INFO, "low"
    elif words & ERROR_KW:
        route, risk_level = Route.ERROR, "medium"
        
    latency_ms = int((time.monotonic() - t0) * 1000)
    return {
        "route": route.value,
        "risk_level": risk_level,
        "latency_log": [{"node": "classify", "latency_ms": latency_ms}],
        "events": [make_event("classify", "completed", f"route={route.value}")],
    }


def ask_clarification_node(state: AgentState) -> dict:
    """Ask for missing information instead of hallucinating."""
    t0 = time.monotonic()
    question = "Can you provide the order id or the missing context?"
    latency_ms = int((time.monotonic() - t0) * 1000)
    return {
        "pending_question": question,
        "final_answer": question,
        "latency_log": [{"node": "clarify", "latency_ms": latency_ms}],
        "events": [make_event("clarify", "completed", "missing information requested")],
    }





def tool_node(state: AgentState) -> dict:
    """Call multiple mock tools in parallel."""
    t0 = time.monotonic()
    attempt = int(state.get("attempt", 0))
    scenario_id = state.get("scenario_id", "unknown")
    route = state.get("route")

    def run_main_tool() -> str:
        time.sleep(0.05) # mock io latency
        if route == Route.ERROR.value and attempt < 2:
             return f"ERROR: transient failure attempt={attempt} scenario={scenario_id}"
        return f"mock-tool-main-result for scenario={scenario_id}"

    def run_audit_tool() -> str:
        time.sleep(0.03) # mock io latency
        return f"mock-tool-audit-record for scenario={scenario_id}"

    results = []
    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(run_main_tool): "main_tool",
            executor.submit(run_audit_tool): "audit_tool"
        }
        for future in as_completed(futures):
            try:
                results.append(future.result())
            except Exception as e:
                results.append(f"ERROR: {futures[future]} execution crashed: {str(e)}")
    
    latency_ms = int((time.monotonic() - t0) * 1000)
    combined_output = " | ".join(results)
    
    return {
        "tool_results": [combined_output],
        "latency_log": [{"node": "tool", "latency_ms": latency_ms}],
        "events": [make_event("tool", "completed", f"parallel tools executed attempt={attempt}")],
    }


def risky_action_node(state: AgentState) -> dict:
    """Prepare a risky action for approval."""
    t0 = time.monotonic()
    latency_ms = int((time.monotonic() - t0) * 1000)
    return {
        "proposed_action": "prepare refund or external action; approval required",
        "latency_log": [{"node": "risky_action", "latency_ms": latency_ms}],
        "events": [make_event("risky_action", "pending_approval", "approval required")],
    }


def approval_node(state: AgentState) -> dict:
    """Human approval step with optional LangGraph interrupt()."""
    t0 = time.monotonic()
    import os

    if os.getenv("LANGGRAPH_INTERRUPT", "").lower() == "true":
        from langgraph.types import interrupt

        value = interrupt({
            "proposed_action": state.get("proposed_action"),
            "risk_level": state.get("risk_level"),
        })
        if isinstance(value, dict):
            decision = ApprovalDecision(**value)
        else:
            decision = ApprovalDecision(approved=bool(value))
    else:
        decision = ApprovalDecision(approved=True, comment="mock approval for lab")
        
    latency_ms = int((time.monotonic() - t0) * 1000)
    return {
        "approval": decision.model_dump(),
        "latency_log": [{"node": "approval", "latency_ms": latency_ms}],
        "events": [make_event("approval", "completed", f"approved={decision.approved}")],
    }


def retry_or_fallback_node(state: AgentState) -> dict:
    """Record a retry attempt."""
    t0 = time.monotonic()
    attempt = int(state.get("attempt", 0)) + 1
    errors = [f"transient failure attempt={attempt}"]
    latency_ms = int((time.monotonic() - t0) * 1000)
    return {
        "attempt": attempt,
        "errors": errors,
        "latency_log": [{"node": "retry", "latency_ms": latency_ms}],
        "events": [make_event("retry", "completed", "retry attempt recorded", attempt=attempt)],
    }


def answer_node(state: AgentState) -> dict:
    """Produce a final response."""
    t0 = time.monotonic()
    if state.get("tool_results"):
        answer = f"I found: {state['tool_results'][-1]}"
    else:
        answer = "This is a safe mock answer. Replace with your agent response."
    latency_ms = int((time.monotonic() - t0) * 1000)
    return {
        "final_answer": answer,
        "latency_log": [{"node": "answer", "latency_ms": latency_ms}],
        "events": [make_event("answer", "completed", "answer generated")],
    }


def evaluate_node(state: AgentState) -> dict:
    """Evaluate tool results — the 'done?' check that enables retry loops."""
    t0 = time.monotonic()
    tool_results = state.get("tool_results", []) or []
    latency_ms = int((time.monotonic() - t0) * 1000)
    
    latest = tool_results[-1] if tool_results else ""
    has_failure = "ERROR" in str(latest)
    
    if has_failure:
        return {
            "evaluation_result": "needs_retry",
            "latency_log": [{"node": "evaluate", "latency_ms": latency_ms}],
            "events": [make_event(
                "evaluate", "completed", "latest tool result contains failure, retry triggered"
            )],
        }
    return {
        "evaluation_result": "success",
        "latency_log": [{"node": "evaluate", "latency_ms": latency_ms}],
        "events": [make_event("evaluate", "completed", "tool result satisfactory")],
    }


def dead_letter_node(state: AgentState) -> dict:
    """Log unresolvable failures for manual review."""
    t0 = time.monotonic()
    latency_ms = int((time.monotonic() - t0) * 1000)
    ans = "Request could not be completed after maximum retry attempts. Logged for manual review."
    atpt = state.get('attempt', 0)
    return {
        "final_answer": ans,
        "latency_log": [{"node": "dead_letter", "latency_ms": latency_ms}],
        "events": [make_event("dead_letter", "completed", f"max retries exceeded, attempt={atpt}")],
    }


def finalize_node(state: AgentState) -> dict:
    """Finalize the run and emit a final audit event."""
    t0 = time.monotonic()
    latency_ms = int((time.monotonic() - t0) * 1000)
    return {
        "latency_log": [{"node": "finalize", "latency_ms": latency_ms}],
        "events": [make_event("finalize", "completed", "workflow finished")]
    }
