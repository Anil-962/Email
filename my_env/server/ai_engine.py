import os
import json
from typing import Optional, Generator
from sqlalchemy.orm import Session
from openai import OpenAI
from .models import DBTask
from .logger import setup_logger

logger = setup_logger("ai_engine")

def get_openai_client() -> OpenAI:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not configured")
    return OpenAI(api_key=api_key)

# The Agentic functions tool schema injected into the LLM context.
# This forces the LLM to 'do the work' instead of just retrieving IDs.
tools = [
    {
        "type": "function",
        "function": {
            "name": "process_task",
            "description": "Perform detailed work to resolve the given task comprehensively.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer", 
                        "description": "The integer ID of the highest priority pending task."
                    },
                    "generated_output": {
                        "type": "string", 
                        "description": "The literal produced content of performing the task. If it says 'write email', provide the full email body. If it says 'summarize', provide the summary. Be thorough and helpful."
                    }
                },
                "required": ["task_id", "generated_output"]
            }
        }
    }
]

def classify_priority_with_llm(task_text: str) -> dict:
    """
    Uses OpenAI to dynamically parse an email or task text to classify priority and compute
    semantic confidence matrices automatically securely avoiding manual evaluation blocks.
    Returns: {"priority": "low|medium|high", "confidence": int 0-100}
    """
    try:
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not configured")
            
        prompt = (
            "Analyze the following email/task text and determine its true urgency and safety for autonomous resolution. "
            "Return exactly one JSON object with two keys: "
            "1. 'priority' mapped to 'high', 'medium', or 'low'. "
            "2. 'confidence' mapped to an integer (0-100) indicating how certain you are of your priority selection. "
            "Strict Rules: Urgent syntax or explicitly strict deadlines -> 'high', low confidence if ambiguous. "
            "Informational reading, newsletters, or casual FYIs -> 'low', high confidence. "
            "Standard workloads without strict timeline pressure -> 'medium'.\n\n"
            f"Text Payload: {task_text}"
        )
        
        response = get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an executive assistant and semantic inference classifier."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            temperature=0.0
        )
        
        result = json.loads(response.choices[0].message.content)
        priority = result.get("priority", "medium").strip().lower()
        confidence = result.get("confidence", 50)
        
        if priority not in ["low", "medium", "high"]:
            priority = "medium"
            
        logger.info(f"OpenAI intelligently mapped priority as {priority.upper()} (Confidence: {confidence}/100)")
        return {"priority": priority, "confidence": int(confidence)}
        
    except Exception as e:
        logger.warning(f"OpenAI classifier fallback triggered -> {e}")
        text_lower = task_text.lower()
        if any(w in text_lower for w in ['urgent', 'asap', 'deadline', 'critical', 'emergency']):
            return {"priority": "high", "confidence": 30} # Deterministic logic assumes weak confidence initially
        if any(w in text_lower for w in ['fyi', 'newsletter', 'info', 'update', 'read', 'optional']):
            return {"priority": "low", "confidence": 85}
        return {"priority": "medium", "confidence": 50}

def generate_email_reply(email_text: str, tone: str) -> str:
    """
    Uses OpenAI to dynamically draft a short, cohesive email reply targeting a specific tone.
    """
    try:
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY not configured")
            
        system_prompt = (
            "You are a professional executive assistant. Your task is to draft a short, "
            "concise, and appropriate email reply to the provided email content. "
            f"The tone of the reply MUST be exactly: {tone}. "
            "Keep the response brief, actionable, and do not include boilerplate placeholders like [Your Name]."
        )
        
        response = get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Email Subject/Body:\n{email_text}"}
            ],
            temperature=0.7 # Slight variance allowed for creative tone execution
        )
        
        reply_content = response.choices[0].message.content.strip()
        logger.info(f"OpenAI successfully drafted an {tone} reply payload.")
        return reply_content
        
    except Exception as e:
        logger.error(f"OpenAI reply drafting fallback triggered -> {e}")
        raise ValueError(f"AI Drafting Engine fault: {str(e)}")

def select_and_process_task_stream(db: Session, user_id: int) -> Generator[str, None, None]:
    """
    Agentic Workflow Generator: Yields SSE tokens seamlessly so the React Application
    can stream internal AI reasoning securely in real-time.
    """
    yield "data: Mounting Agentic context...\n\n"
    
    pending_db_tasks = db.query(DBTask).filter(
        DBTask.status == "pending",
        DBTask.requires_confirmation == False,
        DBTask.user_id == user_id
    ).all()
    if not pending_db_tasks:
        yield "data: No pending tasks found in database.\n\n"
        yield "data: [DONE]\n\n"
        return

    tasks_data = [{"id": t.id, "text": t.text, "priority": t.priority} for t in pending_db_tasks]
    
    yield f"data: Found {len(pending_db_tasks)} pending tasks. Scanning semantic priorities...\n\n"

    prompt = (
        "You are an AI Task Manager and autonomous execution Agent. Review the following list of pending tasks. "
        "1. Identify the single most important and urgent task to work on next. "
        "2. You MUST call the 'process_task' tool to 'perform' the task. "
        "Generate a concrete, substantial, and highly professional 'generated_output' that completely satisfies the intent of the task.\n\n"
        f"Tasks: {json.dumps(tasks_data)}"
    )

    try:
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
        yield "data: Connecting to OpenAI Task Processing Grid via Function Calling...\n\n"
        
        response = get_openai_client().chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a proactive, highly intelligent task execution agent."},
                {"role": "user", "content": prompt}
            ],
            tools=tools,
            tool_choice={"type": "function", "function": {"name": "process_task"}} # Force explicit execution
        )
        
        message = response.choices[0].message
        
        if message.tool_calls:
            tool_call = message.tool_calls[0]
            args = json.loads(tool_call.function.arguments)
            selected_id = args.get("task_id")
            generated_output = args.get("generated_output")
            
            yield f"data: Task #{selected_id} isolated as primary objective.\n\n"
            yield f"data: Auto-resolving task workload: {generated_output[:40]}...\n\n"
            
            selected_task = next((t for t in pending_db_tasks if t.id == selected_id), None)
            if not selected_task:
                raise ValueError(f"LLM returned an invalid task ID reference: {selected_id}")
                
            # Bind the agentic output onto the database model directly
            selected_task.ai_output = generated_output
            selected_task.status = "completed"
            
            db.commit()
            db.refresh(selected_task)
            
            yield "data: Output commited. Task lifecycle closed.\n\n"
            yield "data: [DONE]\n\n"
        else:
            yield "data: Error: Tool structure mismatch internally. Alert developers.\n\n"
            yield "data: [DONE]\n\n"

    except Exception as e:
        logger.warning(f"AI Stream failed severely: {e}")
        yield f"data: AI Engine Context Error: {e}.\n\n"
        yield "data: [DONE]\n\n"
