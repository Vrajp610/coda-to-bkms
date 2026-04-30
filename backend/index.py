import json
import os
import queue
import threading
from pathlib import Path
from uuid import uuid4
from datetime import UTC, datetime
from fastapi import FastAPI, Header, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.coda import format_data, format_goshthi_data
from backend.bkms import update_sheet
from backend.bkms_user_update import update_users
from backend.goshthi import update_goshthi
from backend.bal_mandal import update_bal_sheet
from backend.utils.log_writer import write_run_log

app = FastAPI()
JOB_DIR = Path("logs") / "jobs"
JOB_LOCK = threading.Lock()

def _split_origins(value: str | None) -> list[str]:
    if not value:
        return []
    return [origin.strip().rstrip("/") for origin in value.split(",") if origin.strip()]


def _build_allowed_origins() -> list[str]:
    allowed = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    allowed.extend(_split_origins(os.getenv("ALLOWED_ORIGINS")))

    if os.getenv("FLY_APP_NAME"):
        app_name = os.getenv("FLY_APP_NAME")
        allowed.append(f"https://{app_name}.fly.dev")

    # Preserve order while removing duplicates and normalizing trailing slashes.
    return list(dict.fromkeys(origin.rstrip("/") for origin in allowed))


allowed_origins = _build_allowed_origins()

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "BKMS backend is running"}


@app.get("/health")
def health():
    return {"status": "ok"}


def _verify_trigger_token(
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    expected = os.getenv("BOT_TRIGGER_TOKEN")
    if not expected:
        return
    if x_bkms_token == expected or token == expected:
        return
    raise HTTPException(status_code=401, detail="Invalid or missing trigger token")

class BotInput(BaseModel):
    date: str
    group: str
    sabhaHeld: str
    p2Guju: str
    prepCycleDone: str
    captchaSeconds: int = 20


def _job_path(job_id: str) -> Path:
    return JOB_DIR / f"{job_id}.json"


def _utc_now_iso() -> str:
    return datetime.now(UTC).isoformat().replace("+00:00", "Z")


def _write_job(job_id: str, payload: dict):
    JOB_DIR.mkdir(parents=True, exist_ok=True)
    path = _job_path(job_id)
    with JOB_LOCK:
        path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def _read_job(job_id: str) -> dict | None:
    path = _job_path(job_id)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _update_job(job_id: str, **fields) -> dict:
    job = _read_job(job_id) or {"job_id": job_id}
    job.update(fields)
    job["updated_at"] = _utc_now_iso()
    _write_job(job_id, job)
    return job

@app.post("/run-bot")
def run_bot(
    input_data: BotInput,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
    job_id = uuid4().hex
    created_at = _utc_now_iso()
    _write_job(
        job_id,
        {
            "job_id": job_id,
            "job_type": "attendance",
            "status": "starting",
            "created_at": created_at,
            "updated_at": created_at,
            "date": input_data.date,
            "group": input_data.group,
            "sabhaHeld": input_data.sabhaHeld,
            "p2Guju": input_data.p2Guju,
            "prepCycleDone": input_data.prepCycleDone,
            "captchaSeconds": input_data.captchaSeconds,
            "message": "Starting attendance job.",
            "marked_present": None,
            "not_marked": None,
            "marked_present_ids": [],
            "not_marked_ids": [],
            "not_found_in_bkms": [],
            "error": None,
        },
    )
    try:
        result = format_data(input_data.group, input_data.date)
        if isinstance(result, str):
            _update_job(job_id, status="failed", message=result)
            return {
                "job_id": job_id,
                "status": "failed",
                "message": result,
            }
        attendance, count = result
        _update_job(
            job_id,
            status="running",
            attendance_count=count,
            message=f"{count} Kishores found in Coda. BKMS update starting in background...",
        )

        def run_in_background():
            try:
                outcome = update_sheet(
                    attendance,
                    input_data.group,
                    input_data.sabhaHeld,
                    input_data.p2Guju,
                    input_data.date,
                    input_data.prepCycleDone,
                    input_data.captchaSeconds,
                )
                outcome = outcome or {}
                _update_job(
                    job_id,
                    status="completed",
                    message=outcome.get("message", f"{count} Kishores found in Coda"),
                    marked_present=outcome.get("marked_present", 0),
                    not_marked=outcome.get("not_marked", 0),
                    marked_present_ids=outcome.get("marked_present_ids", []),
                    not_marked_ids=outcome.get("not_marked_ids", []),
                    not_found_in_bkms=outcome.get("not_found_in_bkms", []),
                    sabha_held=outcome.get("sabha_held", True),
                    completed_at=_utc_now_iso(),
                )
            except Exception as e:
                _update_job(
                    job_id,
                    status="failed",
                    error=str(e),
                    message=f"BKMS update failed: {e}",
                )

        thread = threading.Thread(target=run_in_background, daemon=True)
        thread.start()

        return {
            "job_id": job_id,
            "status": "running",
            "message": f"{count} Kishores found in Coda. BKMS update starting in background...",
            "attendance_count": count,
        }
    except Exception as e:
        _update_job(
            job_id,
            status="failed",
            error=str(e),
            message=f"Failed to start BKMS update: {e}",
        )
        return {"error": str(e), "job_id": job_id}


@app.get("/attendance-job/{job_id}")
def get_attendance_job(
    job_id: str,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
    job = _read_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Attendance job not found")
    return job

class UserUpdateInput(BaseModel):
    user_ids: list[str]

@app.post("/run-bot-stream")
def run_bot_stream(
    input_data: BotInput,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
    log_queue = queue.Queue()

    def log(msg):
        log_queue.put(msg)

    def run():
        try:
            result = format_data(input_data.group, input_data.date)
            if isinstance(result, str):
                log(result)
            else:
                attendance, count = result
                log(f"{count} Kishores found in Coda")
                update_sheet(
                    attendance, input_data.group, input_data.sabhaHeld,
                    input_data.p2Guju, input_data.date, input_data.prepCycleDone,
                    input_data.captchaSeconds,
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


class GoshthiInput(BaseModel):
    month: str
    year: str
    goshthiHeld: str
    hangout: str
    workshop: str


class BalMandalInput(BaseModel):
    date: str
    day: str
    sabhaHeld: str
    combinedGroups: str
    smrutiTime: str
    mukhpath: str
    prepCycleDone: str
    individualGroups: dict = {}
    captchaSeconds: int = 20

@app.post("/run-goshthi")
def run_goshthi(
    input_data: GoshthiInput,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
    try:
        result = format_goshthi_data(input_data.month, input_data.year)
        if isinstance(result, str):
            return {"message": result}
        attendance, count = result
        outcome = update_goshthi(
            attendance, input_data.month, input_data.year,
            input_data.goshthiHeld, input_data.hangout, input_data.workshop,
        )
        return {
            "message": f"{count} members found in Coda for {input_data.month} {input_data.year}",
            "marked_present": outcome["marked_present"],
            "not_marked": outcome["not_marked"],
            "not_found_in_bkms": outcome["not_found_in_bkms"],
            "goshthi_held": outcome["goshthi_held"],
        }
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-goshthi-stream")
def run_goshthi_stream(
    input_data: GoshthiInput,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
    log_queue = queue.Queue()

    def log(msg):
        log_queue.put(msg)

    def run():
        try:
            result = format_goshthi_data(input_data.month, input_data.year, log_callback=log)
            if isinstance(result, str):
                log(result)
            else:
                attendance, count = result
                log(f"{count} members found in Coda for {input_data.month} {input_data.year}")
                update_goshthi(
                    attendance, input_data.month, input_data.year,
                    input_data.goshthiHeld, input_data.hangout, input_data.workshop,
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
                write_run_log(lines, "goshthi", f"{input_data.month}_{input_data.year}_{timestamp}.log")
                yield "data: __DONE__\n\n"
                break
            if not msg.startswith("__COUNTDOWN__") and not msg.startswith("__NOT_MARKED__") and not msg.startswith("__NOT_FOUND__"):
                lines.append(msg)
            yield f"data: {msg}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.post("/run-bal-mandal")
def run_bal_mandal(
    input_data: BalMandalInput,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
    job_id = uuid4().hex
    created_at = _utc_now_iso()
    _write_job(
        job_id,
        {
            "job_id": job_id,
            "job_type": "bal_mandal",
            "status": "queued",
            "created_at": created_at,
            "updated_at": created_at,
            "date": input_data.date,
            "sabhaHeld": input_data.sabhaHeld,
            "combinedGroups": input_data.combinedGroups,
            "smrutiTime": input_data.smrutiTime,
            "mukhpath": input_data.mukhpath,
            "prepCycleDone": input_data.prepCycleDone,
            "individualGroups": input_data.individualGroups,
            "captchaSeconds": input_data.captchaSeconds,
            "message": "Bal Mandal job queued. Fetching attendance data from Coda...",
            "marked_present": None,
            "not_marked": None,
            "marked_present_ids": [],
            "not_marked_ids": [],
            "not_found_in_bkms": [],
            "error": None,
        },
    )

    def run_in_background():
        """Fetch Coda data and update BKMS in background (non-blocking)."""
        try:
            # Fetch attendance data from Coda for all Bal groups
            from backend.coda import get_bal_attendance_data
            result = get_bal_attendance_data(input_data.date, input_data.day)
            if isinstance(result, str):
                _update_job(job_id, status="failed", message=result)
                return

            attended_bals, count = result
            _update_job(
                job_id,
                status="running",
                attendance_count=count,
                message=f"{count} Bals found in Coda. Starting BKMS update...",
            )

            # Update BKMS
            outcome = update_bal_sheet(
                attended_bals,
                input_data.day,
                input_data.date,
                input_data.sabhaHeld,
                input_data.combinedGroups,
                input_data.smrutiTime,
                input_data.mukhpath,
                input_data.prepCycleDone,
                input_data.individualGroups,
                input_data.captchaSeconds,
            )
            outcome = outcome or {}
            _update_job(
                job_id,
                status="completed",
                message=f"Bal Mandal attendance updated for {input_data.date}",
                marked_present=outcome.get("marked_present", 0),
                not_marked=outcome.get("not_marked", 0),
                marked_present_ids=outcome.get("marked_present_ids", []),
                not_marked_ids=outcome.get("not_marked_ids", []),
                not_found_in_bkms=outcome.get("not_found_in_bkms", []),
                sabha_held=outcome.get("sabha_held", True),
                completed_at=_utc_now_iso(),
            )
        except Exception as e:
            _update_job(
                job_id,
                status="failed",
                error=str(e),
                message=f"Bal Mandal BKMS update failed: {e}",
            )

    thread = threading.Thread(target=run_in_background, daemon=True)
    thread.start()

    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Bal Mandal job queued. Use GetBalMandalJob to check status.",
    }


@app.post("/run-bal-mandal-stream")
def run_bal_mandal_stream(
    input_data: BalMandalInput,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
    log_queue = queue.Queue()

    def log(msg):
        log_queue.put(msg)

    def run():
        try:
            # Get attendance data from Coda for the selected day's Bal groups
            from backend.coda import get_bal_attendance_data
            result = get_bal_attendance_data(input_data.date, input_data.day, log_callback=log)
            if isinstance(result, str):
                log(result)
                outcome = {"marked_present": 0, "not_marked": 0, "marked_present_ids": [], "not_marked_ids": [], "not_found_in_bkms": [], "sabha_held": False}
            else:
                attended_bals, count = result
                log(f"{count} Bals found in Coda")
                outcome = update_bal_sheet(
                    attended_bals,
                    input_data.day,
                    input_data.date,
                    input_data.sabhaHeld,
                    input_data.combinedGroups,
                    input_data.smrutiTime,
                    input_data.mukhpath,
                    input_data.prepCycleDone,
                    input_data.individualGroups,
                    input_data.captchaSeconds,
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
                write_run_log(lines, "bal_mandal", f"{input_data.date}_{timestamp}.log")
                yield "data: __DONE__\n\n"
                break
            if not msg.startswith("__COUNTDOWN__") and not msg.startswith("__NOT_MARKED__") and not msg.startswith("__NOT_FOUND__"):
                lines.append(msg)
            yield f"data: {msg}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.post("/run-user-update")
def run_user_update(
    input_data: UserUpdateInput,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
    try:
        update_users(input_data.user_ids)
        return {"message": f"Processed {len(input_data.user_ids)} user ID(s)."}
    except Exception as e:
        return {"error": str(e)}


@app.post("/run-user-update-stream")
def run_user_update_stream(
    input_data: UserUpdateInput,
    x_bkms_token: str | None = Header(default=None),
    token: str | None = Query(default=None),
):
    _verify_trigger_token(x_bkms_token, token)
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
