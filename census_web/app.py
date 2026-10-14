"""Web presentation uses only AgentService's public response boundary."""

from __future__ import annotations

import logging
import math

import streamlit as st

from census_agent.control import ControlIssue
from census_web.runtime import build_service

LOGGER = logging.getLogger("census_web.operations")
HISTORY_MESSAGES = 40
PROVENANCE_KEYS = (
    "title",
    "universe",
    "field_path",
    "year",
    "source_product",
    "table",
    "column",
    "estimate_kind",
    "survey_interval",
    "aggregation",
)


@st.cache_resource(show_spinner=False)
def get_service():
    # Shared immutable service facade and transactional control, never conversation state.
    return build_service()


def safe_public(public: dict) -> dict:
    """Defensive allowlist; never render diagnostics or arbitrary nested provider objects."""
    metric = public.get("metric")
    allowed = {
        "status": str(public.get("status", "error")),
        "answer": str(public.get("answer") or "No answer is available; please retry later."),
        "metric": {key: metric[key] for key in PROVENANCE_KEYS if key in metric}
        if isinstance(metric, dict)
        else None,
    }
    elapsed = public.get("latency_seconds")
    if isinstance(elapsed, (int, float)) and math.isfinite(elapsed) and elapsed >= 0:
        allowed["latency_seconds"] = elapsed
    return allowed


def clear_login() -> None:
    for key in ("reviewer_token", "conversation", "messages"):
        st.session_state.pop(key, None)


def show_response(response: dict) -> None:
    # Plain text prevents user/model-sourced links, images and HTML being interpreted.
    st.text(response["answer"])
    st.caption(f"Status: {response['status']}")
    metric = response.get("metric")
    if metric:
        st.caption(
            f"US Open Census · Release {metric.get('year', 'unknown')} · "
            f"{metric.get('source_product', 'unknown')}"
        )
        with st.expander("Data provenance"):
            st.json(metric, expanded=False)
    if "latency_seconds" in response:
        st.caption(f"Request completed in {response['latency_seconds']:.2f} seconds")


def main() -> None:
    st.set_page_config(page_title="Census Chat", page_icon="📊", layout="centered")
    st.title("Census Chat")
    st.caption("Grounded answers from US Open Census on Snowflake Marketplace")
    try:
        service = get_service()
    except Exception:
        LOGGER.warning("web_configuration_unavailable")
        st.error(
            "The data service is not configured for public access. Please contact the operator."
        )
        st.stop()

    if "reviewer_token" not in st.session_state:
        st.info("Enter the reviewer access token supplied through the private handoff.")
        with st.form("reviewer_login", clear_on_submit=True):
            token = st.text_input("Reviewer access token", type="password", max_chars=256)
            submitted = st.form_submit_button("Sign in")
        if submitted:
            try:
                conversation = service.create_session(token)
            except ControlIssue as exc:
                st.error(str(exc))
            except Exception:
                LOGGER.warning("web_login_unavailable")
                st.error("Sign-in is temporarily unavailable; please retry later.")
            else:
                st.session_state.reviewer_token = token
                st.session_state.conversation = conversation
                st.session_state.messages = []
                st.rerun()
        st.stop()

    busy = st.session_state.get("busy", False)
    with st.sidebar:
        st.header("Conversation")
        if st.button("New conversation", disabled=busy):
            try:
                service.reset(st.session_state.reviewer_token, st.session_state.conversation)
            except ControlIssue as exc:
                if exc.status == "unauthorized":
                    clear_login()
                    st.rerun()
                st.error(str(exc))
            except Exception:
                LOGGER.warning("web_reset_unavailable")
                st.error("Conversation could not be reset; retry later.")
            else:
                st.session_state.messages = []
                st.rerun()
        if st.button("Sign out", disabled=busy):
            try:
                service.reset(st.session_state.reviewer_token, st.session_state.conversation)
            except Exception:
                pass  # Local credentials/history still clear; server state expires by TTL.
            clear_login()
            st.rerun()
        st.caption("One active request globally. Busy requests fail promptly; retry shortly.")
        st.caption(
            "ACS release labels do not establish a survey interval. Unsupported statistics clarify or refuse."
        )

    messages = st.session_state.messages
    if not messages:
        st.info(
            "Try: Using 2020 decennial redistricting data, how many people live in Alabama? "
            "Then: What about Autauga County?"
        )
    for message in messages:
        with st.chat_message(message["role"]):
            if message["role"] == "user":
                st.text(message["text"])
            else:
                show_response(message["response"])
    question = st.chat_input(
        "Ask about Census data…", max_chars=2000, disabled=busy, submit_mode="disable"
    )
    if question:
        st.session_state.busy = True
        messages.append({"role": "user", "text": question})
        with st.chat_message("user"):
            st.text(question)
        with st.chat_message("assistant"):
            try:
                with st.status(
                    "Checking Census metadata and querying Snowflake…", expanded=False
                ) as progress:
                    result = service.ask(
                        st.session_state.reviewer_token, st.session_state.conversation, question
                    )
                    response = safe_public(result.public)
                    progress.update(label="Request complete", state="complete")
            except Exception:
                LOGGER.warning("web_request_unavailable")
                response = {
                    "status": "error",
                    "answer": "The data service is temporarily unavailable; retry later.",
                    "metric": None,
                }
            finally:
                st.session_state.busy = False
            show_response(response)
        messages.append({"role": "assistant", "response": response})
        del messages[:-HISTORY_MESSAGES]
        if response["status"] == "unauthorized":
            clear_login()
            st.rerun()
