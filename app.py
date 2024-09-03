import os

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from twilio.rest import Client
from apscheduler.schedulers.background import BackgroundScheduler
from typing import Optional

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER')
TO_PHONE_NUMBER = os.getenv('TO_PHONE_NUMBER')


client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

sushi_count = 0

def send_sms():
    global sushi_count
    client.messages.create(
        to=TO_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        body=f"Dzień dobry, z tej strony Sky Engine. Na sushi od nas jest: {sushi_count} chętnych.\nPozdrawiam."
    )

def reset_shushi_count():
    global sushi_count
    sushi_count = 0

scheduler = BackgroundScheduler()
scheduler.add_job(send_sms, 'cron', day_of_week='tue,thu', hour=8, minute=30)
scheduler.add_job(reset_shushi_count, 'cron', day_of_week='mon,wed', hour=23, minute=59)
scheduler.start()

@app.on_event("shutdown")
def shutdown_event():
    scheduler.shutdown()

@app.post('/')
async def incerement_sushi_count(request: Request):
    global sushi_count
    sushi_count += 1

@app.get('/')
async def hello_world(request: Request):
    template = "index.html"
    context = {"request": request, "sushi_count": sushi_count}
    return templates.TemplateResponse(template, context)


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)