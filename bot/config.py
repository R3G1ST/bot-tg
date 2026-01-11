from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
PAY_TEXT = os.getenv("PAY_TEXT")

TARIFFS = {
    "m1": {"days":30, "devices":1, "price":200},
    "m3": {"days":90, "devices":2, "price":500},
    "m6": {"days":180, "devices":3, "price":900},
}
