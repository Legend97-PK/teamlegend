import asyncio
import requests
import re
import time
import phonenumbers
from phonenumbers import geocoder
from telegram import Bot, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.request import HTTPXRequest
from datetime import datetime
from http.client import RemoteDisconnected
from requests.exceptions import ConnectionError, Timeout
import json

# ================= CONFIG =================
# آپ کا بوٹ ٹوکن اور گروپ آئی ڈی
BOT_TOKEN = "8570883448:AAE9_hU5nIs02kXbE7cLEMvLjeeLbDw_-6k"
GROUP_ID = -1002968061060

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Linux; Android 12)",
    "X-Requested-With": "XMLHttpRequest",
    "Accept-Language": "en-US,en;q=0.9"
}

request_config = HTTPXRequest(connect_timeout=60, read_timeout=60)
bot = Bot(token=BOT_TOKEN, request=request_config)

# ================= PANELS =================
PANELS = {
    "PANEL-1": {
        "username": "legendhacker",
        "password": "legendhacker",
        "base": "http://51.89.99.105/NumberPanel",
        "login": "/login",
        "signin": "/signin",
        "stats": "/client/SMSCDRStats",
        "data": "/client/res/data_smscdr.php",
        "num_i": 2,
        "msg_i": 4,
        "sesskey": True
    },
    "PANEL-2": {
        "username": "testcelint",
        "password": "testcelint",
        "base": "http://139.99.63.204/ints",
        "login": "/login",
        "signin": "/signin",
        "stats": "/client/SMSCDRStats",
        "data": "/client/res/data_smscdr.php",
        "num_i": 2,
        "msg_i": 4,
        "sesskey": False
    },
    "PANEL-3": {
        "username": "atikh9012",
        "password": "teamlegend097",
        "base": "http://217.182.195.194/ints",
        "login": "/login",
        "signin": "/signin",
        "stats": "/agent/SMSCDRReports",
        "data": "/agent/res/data_smscdr.php",
        "num_i": 2,
        "msg_i": 5,
        "sesskey": False
    }
}

# ================= HELPERS =================
def extract_otp(text):
    text = str(text)
    for p in [r"\b\d{8}\b", r"\b\d{6}\b", r"\b\d{5}\b", r"\b\d{4}\b", r"\b\d{3}-\d{3}\b"]:
        m = re.search(p, text)
        if m:
            return m.group()
    return "N/A"

def mask_number(number_str, show_first=5, show_last=4):
    number_str = str(number_str)
    if not number_str.startswith("+"):
        number_str = "+" + number_str
    stars = "*" * (len(number_str) - (show_first + show_last))
    return f"{number_str[:show_first]}{stars}{number_str[-show_last:]}"

def get_country_info_from_number(number_str):
    try:
        if not str(number_str).startswith("+"):
            number_str = "+" + str(number_str)
        parsed = phonenumbers.parse(number_str)
        country = geocoder.description_for_number(parsed, "en")
        region = phonenumbers.region_code_for_number(parsed)
        if region:
            base = 127462 - ord("A")
            flag = chr(base + ord(region[0])) + chr(base + ord(region[1]))
        else:
            flag = "🌍"
        return country or "Unknown", flag
    except:
        return "Unknown", "🌍"

def format_message(record, source_id):
    raw = str(record["message"])
    otp = extract_otp(raw)
    msg = raw.replace("<", "&lt;").replace(">", "&gt;")
    country, flag = get_country_info_from_number(record["number"])
    formatted_number = mask_number(record["number"])
    s = str(record["service"]).lower()
    service_icon = "📱"
    if "whatsapp" in s: service_icon = "🟢"
    elif "telegram" in s: service_icon = "🔵"
    elif "facebook" in s: service_icon = "📘"

    return f"""
<b>{source_id} {flag} New {country} {record['service']} OTP!</b>

<blockquote>🕰 Time: {record['time']}</blockquote>
<blockquote>{flag} Country: {country}</blockquote>
<blockquote>{service_icon} Service: {record['service']}</blockquote>
<blockquote>📞 Number: {formatted_number}</blockquote>
<blockquote>🔑 OTP: <code>{otp}</code></blockquote>

<blockquote>📩 Full Message:</blockquote>
<pre>{msg}</pre>

<b>POWERED BY TEAM LEGENDS ✨
Owner By 💗 Kami_Broken 💯</b>
"""

# ================= PANEL CLASS =================
class Panel:
    def __init__(self, name, cfg):
        self.name = name
        self.cfg = cfg
        self.session = requests.Session()
        self.sesskey = None
        self.seen = set()

    def login(self):
        try:
            print(f"🔄 {self.name}: لاگ ان کرنے کی کوشش ہو رہی ہے...")
            r = self.session.get(self.cfg["base"] + self.cfg["login"], headers=HEADERS, timeout=30)
            
            # Captcha Solving
            cap = re.search(r"What is (\d+) \+ (\d+)", r.text)
            ans = str(int(cap.group(1)) + int(cap.group(2))) if cap else "10"

            res = self.session.post(
                self.cfg["base"] + self.cfg["signin"],
                data={"username": self.cfg["username"], "password": self.cfg["password"], "capt": ans},
                headers={**HEADERS, "Referer": self.cfg["base"] + self.cfg["login"]},
                timeout=30
            )

            # ویریفیکیشن: چیک کریں کہ لاگ ان پیج سے آگے بڑھے یا نہیں
            if "logout" in res.text.lower() or "dashboard" in res.text.lower() or res.status_code == 200:
                if self.cfg["sesskey"]:
                    r2 = self.session.get(self.cfg["base"] + self.cfg["stats"], headers=HEADERS, timeout=30)
                    m = re.search(r"sesskey=([^&\"']+)", r2.text)
                    if m: self.sesskey = m.group(1)
                print(f"✅ {self.name}: لاگ ان کامیاب (Login Success)")
                return True
            else:
                print(f"❌ {self.name}: لاگ ان ناکام رہا۔")
                return False
        except Exception as e:
            print(f"❌ {self.name} لاگ ان ایرر: {e}")
            return False

    def fetch(self):
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            url = f"{self.cfg['base']}{self.cfg['data']}?fdate1={today}%2000:00:00&fdate2={today}%2023:59:59&iDisplayLength=50&_={int(time.time()*1000)}"
            if self.sesskey:
                url += f"&sesskey={self.sesskey}"

            r = self.session.get(url, headers=HEADERS, timeout=40)

            # سیشن ختم ہونے کی صورت میں دوبارہ لاگ ان کریں
            if not r.text or "<html" in r.text.lower():
                print(f"🔄 {self.name}: سیشن ختم، دوبارہ لاگ ان ہو رہا ہے...")
                self.login()
                return []

            try:
                data = r.json()
            except:
                return []

            rows = data.get("aaData", [])
            new = []
            for row in rows:
                uid = str(row[0]) + str(row[self.cfg["num_i"]])
                number = str(row[self.cfg["num_i"]])
                message = str(row[self.cfg["msg_i"]])

                if number in ["0", "+0+0"] or not message.strip():
                    continue

                if uid not in self.seen:
                    self.seen.add(uid)
                    new.append({
                        "time": row[0],
                        "number": number,
                        "service": row[3],
                        "message": message
                    })
            return new
        except (RemoteDisconnected, ConnectionError, Timeout):
            return []
        except Exception as e:
            print(f"❌ {self.name} فیچ ایرر: {e}")
            return []

# ================= MAIN =================
async def main():
    print("🚀 بوٹ شروع ہو رہا ہے...")
    panels = [Panel(k, v) for k, v in PANELS.items()]
    
    for p in panels:
        p.login()

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(text="📱 Channel", url="https://t.me/+t0CAPbyw77kzYzU0"),
         InlineKeyboardButton(text="☎️ Numbers", url="https://t.me/+B14pt8ueq5U5YTg0")],
        [InlineKeyboardButton(text="📂 Folder", url="https://t.me/addlist/tWWLXLLgRsEyMmFk"),
         InlineKeyboardButton(text="🟢 WhatsApp", url="https://whatsapp.com/channel/0029VbBbCk559PwXfBzQ6c0k")]
    ])

    while True:
        for p in panels:
            try:
                new_sms_list = p.fetch()
                if new_sms_list:
                    for sms in new_sms_list:
                        await bot.send_message(
                            chat_id=GROUP_ID,
                            text=format_message(sms, p.name),
                            parse_mode="HTML",
                            reply_markup=keyboard
                        )
                        await asyncio.sleep(0.5)
            except Exception as e:
                print(f"⚠️ لوپ ایرر {p.name}: {e}")
        
        await asyncio.sleep(4)

if __name__ == "__main__":
    asyncio.run(main())
