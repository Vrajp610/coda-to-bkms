import queue
import threading
from datetime import datetime
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.coda import format_data
from backend.bkms import update_sheet
from backend.bkms_user_update import update_users
from backend.utils.log_writer import write_run_log

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BotInput(BaseModel):
    date: str
    group: str
    sabhaHeld: str
    p2Guju: str
    prepCycleDone: str

@app.post("/run-bot")
def run_bot(input_data: BotInput):
    try:
        attendance, count = format_data(input_data.group, input_data.date)
        if isinstance(attendance, str):
            return {"message": attendance}
        result = update_sheet(attendance, input_data.group, input_data.sabhaHeld, input_data.p2Guju, input_data.date, input_data.prepCycleDone)
        return {
            "message": f"{count} Kishores found in Coda",
            "marked_present": result["marked_present"],
            "not_marked": result["not_marked"],
            "not_found_in_bkms": result["not_found_in_bkms"],
            "sabha_held": result["sabha_held"]
        }
    except Exception as e:
        return {"error": str(e)}

class UserUpdateInput(BaseModel):
    user_ids: list[str]

@app.post("/run-bot-stream")
def run_bot_stream(input_data: BotInput):
    log_queue = queue.Queue()

    def log(msg):
        log_queue.put(msg)

    def run():
        try:
            attendance, count = format_data(input_data.group, input_data.date)
            if isinstance(attendance, str):
                log(attendance)
            else:
                log(f"{count} Kishores found in Coda")
                update_sheet(
                    attendance, input_data.group, input_data.sabhaHeld,
                    input_data.p2Guju, input_data.date, input_data.prepCycleDone,
                    log_callback=log,
                )
        except Exception as e:
            log(f"ERROR: {e}")
        finally:
            log_queue.put(None)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    def event_stream():
        lines = []
        while True:
            msg = log_queue.get()
            if msg is None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                group_slug = input_data.group.lower().replace(" ", "_")
                write_run_log(lines, f"attendance/{group_slug}", f"{input_data.date}_{timestamp}.log")
                yield "data: __DONE__\n\n"
                break
            if not msg.startswith("__COUNTDOWN__") and not msg.startswith("__NOT_MARKED__") and not msg.startswith("__NOT_FOUND__"):
                lines.append(msg)
            yield f"data: {msg}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/run-user-update-stream")
def run_user_update_stream(input_data: UserUpdateInput):
    log_queue = queue.Queue()

    def log(msg):
        log_queue.put(msg)

    def run():
        try:
            update_users(input_data.user_ids, log_callback=log)
        except Exception as e:
            log_queue.put(f"ERROR: {e}")
        finally:
            log_queue.put(None)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()

    def event_stream():
        lines = []
        while True:
            msg = log_queue.get()
            if msg is None:
                timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                write_run_log(lines, "user_update", f"{timestamp}.log")
                yield "data: __DONE__\n\n"
                break
            if not msg.startswith("__COUNTDOWN__"):
                lines.append(msg)
            yield f"data: {msg}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
