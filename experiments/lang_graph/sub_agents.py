import json
from langchain_ollama import ChatOllama
from langchain.tools import tool
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command



model = ChatOllama(model="qwen3:4b-instruct-2507-q4_K_M")
# supervisor = ChatOllama(model="gpt-oss:20b", temperature=0.7)
# subagent = ChatOllama(model="mistral:7b")


# ==================================================== tools ======================================================
@tool
def create_calendar_event(
    title: str, start_time: str, end_time: str, attendees: list[str], location: str = ""
) -> str:
    """Create a calendar event. Requires exato ISO datetime format."""
    return f"Event created: {title} from {start_time} to {end_time} with {len(attendees)} attendees."


@tool
def send_email(to: list[str], subject: str, body: str, cc: list[str] = []) -> str:
    """Send an email via email API. Requires properly formatted addresses."""
    return f"Email sent to {', '.join(to)} - Subject: {subject}"


@tool
def get_available_time_slots(
    attendees: list[str], date: str, duration_minutos: int
) -> list[str]:
    """Check calendar availability for given attendees on a specific date."""
    return ["09:00", "14:00", "16:00"]


# ==================================================== subagents ======================================================
@tool
def schedule_event(request: str) -> str:
    """Schedule calendar events using natural language.

    Use this when the user wants to create, modify, or check calendar appointments.
    Handles date/time parsing, availability checking, and event creation.

    Input: Natural language scheduling request (e.g., 'meeting with design team
    next Tuesday at 2pm')
    """
    result = calendar_agent.invoke({"messages": [{"role": "user", "content": request}]})
    # return json.dumps({"status": "success", "sumary": result["messages"][-1].text})
    return result["messages"][-1].text


@tool
def manage_email(request: str) -> str:
    """Send emails using natural language.

    Use this when the user wants to send notifications, reminders, or any email
    communication. Handles recipient extraction, subject generation, and email
    composition.

    Input: Natural language email request (e.g., 'send them a reminder about
    the meeting')
    """
    result = email_agent.invoke({"messages": [{"role": "user", "content": request}]})
    # return json.dumps({"status": "success", "summary": result["messages"][-1].text})
    return result["messages"][-1].text


calendar_agent = create_agent(
    model,
    tools=[create_calendar_event, get_available_time_slots],
    system_prompt=(
        "You are a calendar scheduling assistant. "
        "Parse natural language scheduling requests (e.g., 'next Tuesday at 2pm') "
        "into proper ISO datetime formats. "
        "Use get_available_time_slots to check availability when needed. "
        "Use create_calendar_event to schedule events. "
        "Always confirm what was scheduled in your final response.",
    ),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"create_calendar_event": True},
            description_prefix="Calendar event pending approval",
        ),
    ],
)

email_agent = create_agent(
    model,
    tools=[send_email],
    system_prompt=(
        "You are an email assistant. "
        "Compose professional emails based on natural language requests. "
        "Extract recipient information and craft appropriate subject lines and body text. "
        "Use send_email to send the message. "
        "Always confirm what was sent in your final response."
    ),
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={"send_mail": True},
            description_prefix="Outbound email pending approval",
        )
    ],
)


# ==================================================== supervisor_agent ======================================================
SUPERVISOR_PROMPT = (
    "You are a helpful personal assistant. "
    "You can schedule calendar events and send emails. "
    "Break down user requests into appropriate tool calls and coordinate the results. "
    "When a request involves multiple actions, use multiple tools in sequence."
)


supervisor_agent = create_agent(
    model,
    tools=[schedule_event, manage_email],
    system_prompt=SUPERVISOR_PROMPT,
    checkpointer=InMemorySaver(),
)
config = {"configurable": {"thread_id": "1"}}
# query = (
#     "Schedule a meeting with the design team next Tuesday at 2pm for 1 hour, "
#     "and send them an email reminder about reviewing the new mockups."
# )


# ==================================================== run ======================================================
from langchain.messages import HumanMessage
def model_agent(query): 
    messages = [HumanMessage(content= query)] 
    messages = supervisor_agent.invoke({"messages": messages}, config=config) 
    return messages["messages"][-1].content


