from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from coda import format_data
from bkms import update_sheet

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        update_sheet(attendance, input_data.group, input_data.sabhaHeld, input_data.p2Guju, input_data.date, input_data.prepCycleDone)
        return {"message": f"{count} Kishores found. BKMS updated successfully."}
    except Exception as e:
        return {"error": str(e)}
