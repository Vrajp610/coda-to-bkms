from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from backend.coda import format_data
from backend.bkms import update_sheet

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://vrajpatelbkms.vercel.app"
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
            "not_found_in_bkms": result["not_found_in_bkms"]
        }
    except Exception as e:
        return {"error": str(e)}
