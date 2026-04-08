from fastapi import FastAPI, HTTPException, Depends, Request, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from .database import engine, Base, get_db, SessionLocal
from typing import List
import hashlib
from .models import Task, DBTask, DBUser, EmailReplyRequest, EmailSendRequest, UserAuthRequest, TokenResponse
from .ai_engine import select_and_process_task_stream, classify_priority_with_llm, generate_email_reply
from .logger import setup_logger
from .nlp import classify_priority
from .gmail_service import fetch_latest_emails, send_email
from .auth import get_current_user, create_access_token

logger = setup_logger("api_gateway")

app = FastAPI(title="AI Task Manager API (Enterprise SaaS Edition)")

@app.get("/")
def root():
    return {
        "status": "ok",
        "service": "AI Task Manager API",
        "docs": "/docs"
    }


@app.on_event("startup")
def on_startup() -> None:
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created or already exist.")
    except Exception as db_error:
        logger.error(f"Failed to initialize database during startup: {db_error}")
        raise

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Critical unhandled system error at [{request.method}] {request.url.path} -> {exc}")
    return JSONResponse(status_code=500, content={"detail": "Internal server error. Telemetry notified."})

# --- Identity Management Endpoints ---

@app.post("/register", response_model=TokenResponse)
def register(user: UserAuthRequest, db: Session = Depends(get_db)):
    if db.query(DBUser).filter(DBUser.username == user.username).first():
         raise HTTPException(status_code=400, detail="Username already registered")
    # For hackathon mapping brevity, omitting passlib bcrypt rounds
    new_user = DBUser(username=user.username, hashed_password=user.password) 
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    token = create_access_token(data={"sub": new_user.username})
    return {"access_token": token, "token_type": "bearer"}

@app.post("/login", response_model=TokenResponse)
def login(user: UserAuthRequest, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.username == user.username).first()
    if not db_user or db_user.hashed_password != user.password:
        raise HTTPException(status_code=401, detail="Incorrect credentials mapping")
    token = create_access_token(data={"sub": db_user.username})
    return {"access_token": token, "token_type": "bearer"}

# --- Task Execution Endpoints ---

@app.get("/tasks", response_model=List[Task])
def get_tasks(db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    return db.query(DBTask).filter(DBTask.user_id == current_user.id).all()

@app.post("/tasks", response_model=Task)
def add_task(task: Task, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    if task.priority == "auto":
        task.priority = classify_priority(task.text)

    if db.query(DBTask).filter(DBTask.id == task.id).first():
        raise HTTPException(status_code=400, detail="Task ID collision.")
    
    db_task = DBTask(
        id=task.id, 
        text=task.text, 
        priority=task.priority, 
        status=task.status,
        user_id=current_user.id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@app.put("/tasks/{task_id}/approve")
def approve_safeguarded_task(task_id: int, db: Session = Depends(get_db), current_user: DBUser = Depends(get_current_user)):
    task = db.query(DBTask).filter(DBTask.id == task_id, DBTask.user_id == current_user.id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    task.requires_confirmation = False
    db.commit()
    return {"status": "success", "message": "Confirmation restrictions natively lifted"}

# --- AI Workload Systems ---

def get_current_user_from_query(token: str, db: Session):
    from .auth import get_current_user
    return get_current_user(token=token, db=db)

@app.get("/run-ai-stream")
def run_ai_stream(token: str, db: Session = Depends(get_db)):
    """ Stream route explicitly resolving query-based tokens due to EventSource limitations """
    current_user = get_current_user_from_query(token, db)
    return StreamingResponse(
        select_and_process_task_stream(db, current_user.id), 
        media_type="text/event-stream"
    )

# --- Background Automation Workers ---

def process_emails_background_worker(user_id: int):
    """
    Isolated processing thread bridging heavy OpenAI semantic routines safely completely devoid of the request loop UI blocks.
    """
    db = SessionLocal()
    try:
        emails = fetch_latest_emails(max_results=10)
        added_tasks = []
        for e in emails:
            email_id_int = int(hashlib.md5(e["id"].encode()).hexdigest()[:8], 16)
            
            if not db.query(DBTask).filter(DBTask.id == email_id_int, DBTask.user_id == user_id).first():
                task_text = f"Email: {e['subject']} - {e['snippet']}"
                
                ai_classification = classify_priority_with_llm(task_text)
                evaluated_priority = ai_classification.get("priority", "medium")
                confidence_score = ai_classification.get("confidence", 0)
                
                requires_confirmation = True 
                ai_output_content = None
                task_status = "pending"
                
                if evaluated_priority == "low" and confidence_score >= 80:
                    ai_output_content = generate_email_reply(task_text, tone="informal") 
                    try:
                        send_email(e["sender"], f"Re: {e['subject']}", ai_output_content)
                        requires_confirmation = False
                        task_status = "completed"
                    except Exception as email_err:
                        logger.error(f"Background email dispatch error: {email_err}")
                        task_status = "pending" 

                new_task = DBTask(
                    id=email_id_int,
                    text=task_text,
                    priority=evaluated_priority,
                    confidence=confidence_score,
                    requires_confirmation=requires_confirmation,
                    status=task_status,
                    ai_output=ai_output_content,
                    user_id=user_id
                )
                db.add(new_task)
                added_tasks.append(new_task)
                
        if added_tasks:
            db.commit()
    except Exception as e:
        logger.error(f"Background workload failed structurally: {e}")
    finally:
        db.close()

@app.post("/emails/to-tasks")
def convert_emails_to_tasks(background_tasks: BackgroundTasks, current_user: DBUser = Depends(get_current_user)):
    background_tasks.add_task(process_emails_background_worker, current_user.id)
    return {"status": "queued", "message": "Heavy execution metrics completely offloaded securely."}

@app.get("/emails")
def get_emails(current_user: DBUser = Depends(get_current_user)):
    emails = fetch_latest_emails(max_results=10)
    return {"status": "success", "count": len(emails), "data": emails}

@app.post("/generate-reply")
def create_email_reply(request: EmailReplyRequest, current_user: DBUser = Depends(get_current_user)):
    reply_text = generate_email_reply(request.email_text, request.tone)
    return {"status": "success", "reply": reply_text}

@app.post("/send-reply")
def dispatch_email_response(request: EmailSendRequest, current_user: DBUser = Depends(get_current_user)):
    result = send_email(request.recipient, request.subject, request.message)
    return {"status": "success", "message_id": result.get("id")}
