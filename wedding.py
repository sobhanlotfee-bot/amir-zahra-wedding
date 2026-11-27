
from flask import Flask, request
from pathlib import Path
from datetime import datetime
import csv
import html
import os
import urllib.request
import urllib.parse
import json

app = Flask(__name__)

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
STATIC.mkdir(exist_ok=True)

WEDDING_DATE = "2026-12-23T19:00:00+03:30"
ADDRESS = "میدان معلم، بلوار بسیج، جنب ورزشگاه الغدیر، تالار پذیرایی فریال، سمنان"

MAP_URL = (
    "https://www.google.com/maps/dir/?api=1"
    "&destination=35.5868900%2C53.3861140"
    "&travelmode=driving&dir_action=navigate"
)


def send_telegram_message(name, count, attendance):
    token = os.getenv("BOT_TOKEN")
    chat_id = os.getenv("ADMIN_CHAT_ID")

    if not token or not chat_id:
        app.logger.error("Telegram environment variables are missing")
        return False

    status = (
        "با کمال میل در جشن حضور خواهد داشت ❤️"
        if attendance == "yes"
        else "متأسفانه امکان حضور ندارد"
    )

    message = (
        "💌 <b>پاسخ جدید دعوت‌نامه عروسی</b>\n\n"
        f"👤 نام مهمان: {html.escape(name)}\n"
        f"👥 تعداد نفرات: {count}\n"
        f"📩 پاسخ: {status}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data)

        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode("utf-8"))

        if not result.get("ok"):
            app.logger.error("Telegram API returned an unsuccessful response")
            return False

        return True

    except Exception:
        app.logger.exception("Telegram notification failed")
        return False


@app.route("/", methods=["GET", "POST"])
def home():

    if request.method == "POST":
        name = request.form.get("name", "").strip()[:80]
        count = request.form.get("count", "1")
        attendance = request.form.get("attendance", "")

        if (
            not name
            or count not in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
            or attendance not in ["yes", "no"]
        ):
            return {
                "ok": False,
                "message": "لطفاً اطلاعات را کامل و صحیح وارد کنید."
            }, 400

        try:
            with open(
                BASE / "guests.csv",
                "a",
                newline="",
                encoding="utf-8-sig"
            ) as f:
                csv.writer(f).writerow([
                    name,
                    count,
                    attendance,
                    datetime.now().isoformat()
                ])

            send_telegram_message(name, count, attendance)

            return {
                "ok": True,
                "message": "پاسخ شما با موفقیت ثبت شد. سپاس از همراهی شما ❤️"
            }

        except Exception:
            app.logger.exception("RSVP saving failed")

            return {
                "ok": False,
                "message": "ثبت پاسخ با مشکل مواجه شد. لطفاً دوباره تلاش کنید."
            }, 500

    photo_names = ["wedding-photo.jpg"] + [
        f"photo{i}.jpg" for i in range(1, 7)
    ]

    photos = [
        f"/static/{name}"
        for name in photo_names
        if (STATIC / name).is_file()
        and (STATIC / name).stat().st_size > 1000
    ]

    gallery = "".join(
        f'<button class="photo reveal" onclick="openPhoto(this)">'
        f'<img src="{p}" alt="خاطره زیبا"></button>'
        for p in photos
    ) or '<p class="empty">عکس‌ها به‌زودی اضافه می‌شوند.</p>'

    video = ""
    video_file = STATIC / "wedding.mp4"

    if video_file.is_file() and video_file.stat().st_size > 1000:
        video = """
        <section class="section reveal">
          <div class="section-title">لحظه‌های عاشقانه</div>
          <div class="video-frame">
            <video class="video" controls playsinline preload="metadata">
              <source src="/static/wedding.mp4" type="video/mp4">
            </video>
          </div>
        </section>
        """

    return PAGE.replace("{{GALLERY}}", gallery).replace(
        "{{VIDEO}}", video
    ).replace("{{DATE}}", WEDDING_DATE).replace(
        "{{ADDRESS}}", html.escape(ADDRESS)
    ).replace(
        "{{MAP_URL}}", html.escape(MAP_URL, quote=True)
    )


PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#f5ead7">
<meta name="description" content="دعوت‌نامه جشن ازدواج امیر و زهرا">
<title>دعوت‌نامه عروسی امیر و زهرا</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&family=Marhey:wght@400;500;600;700&display=swap');

:root {
 --gold:#b18a4b;
 --gold-light:#e4cc94;
 --gold-dark:#80602e;
 --cream:#f8efdf;
 --paper:#fbf4e7;
 --ink:#59452f;
 --wine:#762d38;
 --wine-light:#a34c53;
 --line:rgba(177,138,75,.55);
}

* {
 box-sizing:border-box;
}

html {
 width:100%;
 max-width:100%;
 overflow-x:hidden;
 scroll-behavior:smooth;
}

body {
 margin:0;
 width:100%;
 max-width:100%;
 min-width:0;
 font-family:Vazirmatn,Tahoma,sans-serif;
 color:var(--ink);
 background:
  radial-gradient(ellipse at 12% 8%,rgba(226,202,157,.35),transparent 35%),
  radial-gradient(ellipse at 88% 45%,rgba(225,205,170,.28),transparent 35%),
  repeating-linear-gradient(0deg,rgba(130,98,53,.018) 0px,rgba(130,98,53,.018) 1px,transparent 1px,transparent 5px),
  linear-gradient(135deg,#fff9ed,#f2e5d0 50%,#fffaf0);
 overflow-x:hidden;
}

body::before {
 content:"";
 position:fixed;
 inset:0;
 z-index:0;
 pointer-events:none;
 opacity:.24;
 background-image:url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.8' numOctaves='3' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.16'/%3E%3C/svg%3E");
}

button,input,select {
 font:inherit;
 max-width:100%;
}

button {cursor:pointer}
a {color:inherit;text-decoration:none}
img,video {max-width:100%;}

button:focus-visible,
a:focus-visible,
input:focus-visible,
select:focus-visible {
 outline:2px solid var(--gold-dark);
 outline-offset:4px;
}

/* ---------------------------
   نامه آغازین تمام صفحه
---------------------------- */

.intro {
 position:fixed;
 inset:0;
 z-index:1000;
 width:100%;
 height:100vh;
 height:100dvh;
 overflow:hidden;
 background:
  radial-gradient(ellipse at center,#fff9ed 0%,#f0e0c3 100%);
 display:flex;
 align-items:center;
 justify-content:center;
 opacity:1;
 visibility:visible;
 transition:opacity 1.4s ease,visibility 1.4s ease;
}

.intro::before {
 content:"";
 position:absolute;
 inset:13px;
 border:1px solid rgba(177,138,75,.55);
 pointer-events:none;
}

.intro::after {
 content:"";
 position:absolute;
 inset:22px;
 border:1px solid rgba(177,138,75,.25);
 pointer-events:none;
}

.intro.leaving {
 opacity:0;
 visibility:hidden;
 pointer-events:none;
}

.envelope-wrap {
 position:absolute;
 inset:0;
 width:100%;
 height:100%;
 text-align:center;
 perspective:1500px;
}

.envelope {
 position:relative;
 width:100%;
 height:100%;
 overflow:hidden;
 cursor:pointer;
 isolation:isolate;
 background:
  radial-gradient(ellipse at 50% 42%,rgba(255,255,255,.85),transparent 55%),
  repeating-linear-gradient(0deg,rgba(130,98,53,.025) 0px,rgba(130,98,53,.025) 1px,transparent 1px,transparent 5px),
  linear-gradient(145deg,#fff9ed,#ead8b8);
 -webkit-tap-highlight-color:transparent;
}

.envelope::before {
 content:"";
 position:absolute;
 inset:clamp(25px,5vw,65px);
 border:1px solid rgba(177,138,75,.75);
 box-shadow:inset 0 0 0 7px rgba(255,255,255,.25);
 pointer-events:none;
 z-index:8;
}

.envelope::after {
 content:"";
 position:absolute;
 inset:clamp(34px,6vw,76px);
 border:1px solid rgba(177,138,75,.22);
 pointer-events:none;
 z-index:8;
}

.corner {
 position:absolute;
 width:45px;
 height:45px;
 border-color:#b18a4b;
 border-style:solid;
 opacity:.7;
 z-index:9;
 pointer-events:none;
}

.corner.tl {top:clamp(25px,5vw,65px);right:clamp(25px,5vw,65px);border-width:1px 1px 0 0;}
.corner.tr {top:clamp(25px,5vw,65px);left:clamp(25px,5vw,65px);border-width:1px 0 0 1px;}
.corner.bl {bottom:clamp(25px,5vw,65px);right:clamp(25px,5vw,65px);border-width:0 1px 1px 0;}
.corner.br {bottom:clamp(25px,5vw,65px);left:clamp(25px,5vw,65px);border-width:0 0 1px 1px;}

.intro-caption {
 position:absolute;
 top:17%;
 left:0;
 right:0;
 z-index:10;
 color:#967340;
 font-size:clamp(12px,2.7vw,16px);
 letter-spacing:3px;
 animation:captionGlow 3s ease-in-out infinite;
}

.intro-title {
 position:absolute;
 top:24%;
 left:0;
 right:0;
 z-index:10;
 font-family:Marhey,Vazirmatn,sans-serif;
 font-size:clamp(24px,6vw,43px);
 color:#94713d;
 text-shadow:0 4px 20px #c4a46a55;
}

.envelope-flap {
 position:absolute;
 inset:0;
 z-index:5;
 background:
  linear-gradient(145deg,rgba(255,255,255,.55),transparent 45%),
  linear-gradient(150deg,#fff7e6,#dfc89e);
 clip-path:polygon(0 0,100% 0,50% 58%);
 transform-origin:top center;
 transition:transform 1.6s cubic-bezier(.2,.7,.15,1);
 backface-visibility:hidden;
}

.envelope-flap::after {
 content:"";
 position:absolute;
 inset:0;
 background:linear-gradient(180deg,rgba(255,255,255,.35),transparent 70%);
}

.letter-under {
 position:absolute;
 inset:0;
 z-index:2;
 background:
  radial-gradient(ellipse at center,rgba(255,255,255,.8),transparent 65%),
  linear-gradient(145deg,#fffaf0,#f1e2c7);
 display:flex;
 align-items:center;
 justify-content:center;
}

.letter-under-inner {
 width:min(80%,520px);
 padding:35px 20px;
 border-top:1px solid var(--line);
 border-bottom:1px solid var(--line);
 color:#9b7a48;
 opacity:.8;
}

.letter-under-inner strong {
 display:block;
 font-family:Marhey,Vazirmatn,sans-serif;
 font-size:clamp(28px,7vw,52px);
 margin:15px 0;
}

.seal {
 position:absolute;
 z-index:12;
 width:clamp(90px,22vw,130px);
 height:clamp(90px,22vw,130px);
 border-radius:50%;
 top:50%;
 left:50%;
 transform:translate(-50%,-50%);
 display:grid;
 place-items:center;
 color:#f9e9c5;
 font-family:Marhey,Vazirmatn,sans-serif;
 font-size:clamp(23px,6vw,34px);
 background:
  radial-gradient(circle at 30% 23%,#c77c79 0%,#963e48 35%,#68232f 75%,#4a1b24 100%);
 border:5px double #d9b979;
 box-shadow:
  0 12px 30px #4e202b66,
  inset 0 4px 8px #f4c9a455,
  inset 0 -7px 10px #3e101a66;
 transition:transform .8s ease,opacity .7s ease,filter .7s ease;
}

.seal::before {
 content:"";
 position:absolute;
 inset:9px;
 border:1px solid rgba(246,219,165,.65);
 border-radius:50%;
}

.seal::after {
 content:"";
 position:absolute;
 inset:-8px;
 border-radius:50%;
 border:1px solid rgba(177,138,75,.6);
}

.open-hint {
 position:absolute;
 bottom:17%;
 left:0;
 right:0;
 z-index:11;
 color:#987847;
 font-size:13px;
 letter-spacing:1px;
 animation:hintPulse 2.2s ease-in-out infinite;
}

.envelope.open .envelope-flap {
 transform:rotateX(180deg);
}

.envelope.open .seal {
 transform:translate(-50%,-50%) scale(1.7) rotate(25deg);
 opacity:0;
 filter:blur(12px);
}

.envelope.open .open-hint,
.envelope.open .intro-caption,
.envelope.open .intro-title {
 opacity:0;
 transition:opacity .5s ease;
}

.envelope.open .letter-under-inner {
 animation:letterTextIn 1.5s ease both;
}

@keyframes captionGlow {
 0%,100% {opacity:.65}
 50% {opacity:1}
}

@keyframes hintPulse {
 0%,100% {opacity:.5;transform:translateY(0)}
 50% {opacity:1;transform:translateY(-5px)}
}

@keyframes letterTextIn {
 from {opacity:0;transform:translateY(35px)}
 to {opacity:1;transform:translateY(0)}
}

/* ---------------------------
   محتوای اصلی
---------------------------- */

#site {
 position:relative;
 z-index:1;
 width:100%;
 max-width:100%;
 overflow-x:clip;
 opacity:0;
 visibility:hidden;
 transform:translateY(25px) scale(.99);
 transition:
  opacity 1.6s ease,
  transform 1.6s cubic-bezier(.2,.7,.2,1),
  visibility 1.6s ease;
}

#site.visible {
 opacity:1;
 visibility:visible;
 transform:translateY(0) scale(1);
}

.page-frame {
 position:fixed;
 inset:12px;
 border:1px solid rgba(177,138,75,.22);
 pointer-events:none;
 z-index:20;
}

.hero {
 position:relative;
 width:100%;
 min-height:100vh;
 min-height:100svh;
 display:flex;
 justify-content:center;
 align-items:center;
 text-align:center;
 padding:90px 20px 70px;
 overflow:hidden;
}

.hero::before {
 content:"";
 position:absolute;
 width:min(90vw,650px);
 aspect-ratio:1;
 border-radius:50%;
 border:1px solid rgba(177,138,75,.24);
 box-shadow:
  0 0 0 16px rgba(177,138,75,.035),
  0 0 0 32px rgba(177,138,75,.025);
 animation:slowRotate 35s linear infinite;
}

.hero::after {
 content:"✧";
 position:absolute;
 top:13%;
 color:#b18a4b;
 font-size:28px;
 opacity:.65;
 animation:starFloat 4s ease-in-out infinite;
}

.hero-content {
 position:relative;
 z-index:2;
 width:min(750px,100%);
 padding:40px 15px;
}

.eyebrow {
 font-size:13px;
 letter-spacing:3px;
 color:#a27e45;
 opacity:0;
 animation:softAppear 1.3s .3s ease forwards;
}

.names {
 font-family:Marhey,Vazirmatn,sans-serif;
 font-size:clamp(50px,12vw,105px);
 font-weight:600;
 color:#a47c3d;
 line-height:1.55;
 margin:22px 0;
 text-shadow:0 6px 25px #c9a86c45;
}

.names span {
 display:block;
 font-family:Vazirmatn,sans-serif;
 font-size:24px;
 color:#b18a4b;
}

.gold-line {
 width:150px;
 height:1px;
 margin:25px auto;
 background:linear-gradient(90deg,transparent,#b28a48,transparent);
}

.invitation {
 max-width:490px;
 margin:auto;
 line-height:2.7;
 color:#796448;
 font-size:15px;
}

.hero-date {
 margin-top:27px;
 color:#9b7948;
 line-height:2.4;
}

.hero-ornament {
 margin:28px auto 0;
 width:65px;
 height:65px;
 border:1px solid rgba(177,138,75,.7);
 border-radius:50%;
 display:grid;
 place-items:center;
 color:#a47c3d;
 font-size:23px;
}

.scroll-cue {
 position:absolute;
 bottom:27px;
 left:50%;
 transform:translateX(-50%);
 color:#a17b46;
 font-size:11px;
 letter-spacing:2px;
 display:flex;
 flex-direction:column;
 align-items:center;
 gap:8px;
}

.scroll-cue span:last-child {
 width:1px;
 height:35px;
 background:linear-gradient(#b18a4b,transparent);
 animation:scrollLine 1.8s ease-in-out infinite;
}

@keyframes scrollLine {
 0%,100% {transform:scaleY(.5);transform-origin:top;opacity:.5}
 50% {transform:scaleY(1);opacity:1}
}

@keyframes slowRotate {to {transform:rotate(360deg)}}
@keyframes starFloat {0%,100%{transform:translateY(0) rotate(0)}50%{transform:translateY(-12px) rotate(35deg)}}
@keyframes softAppear {to {opacity:1}}

/* ---------------------------
   افکت ورود بخش‌ها با اسکرول
---------------------------- */

.reveal {
 opacity:0;
 transform:translateY(55px);
 filter:blur(5px);
 transition:
  opacity 1s ease,
  transform 1.1s cubic-bezier(.2,.7,.2,1),
  filter 1s ease;
}

.reveal.visible {
 opacity:1;
 transform:translateY(0);
 filter:blur(0);
}

.section {
 position:relative;
 width:min(1050px,92%);
 max-width:calc(100% - 24px);
 margin:90px auto;
 padding:55px 25px;
 text-align:center;
 border-top:1px solid rgba(177,138,75,.45);
 border-bottom:1px solid rgba(177,138,75,.45);
 background:linear-gradient(90deg,transparent,rgba(255,250,240,.42),transparent);
}

.section::before,
.section::after {
 content:"✧";
 position:absolute;
 top:-12px;
 color:#b18a4b;
 font-size:20px;
 background:#f7eddc;
 padding:0 12px;
}

.section::before {right:20px}
.section::after {left:20px}

.section-title {
 font-family:Marhey,Vazirmatn,sans-serif;
 font-size:clamp(23px,5vw,34px);
 color:#a17b3d;
 font-weight:600;
 margin-bottom:30px;
}

.section-title::after {
 content:"";
 display:block;
 width:85px;
 height:1px;
 margin:15px auto 0;
 background:linear-gradient(90deg,transparent,#b18a4b,transparent);
}

/* ---------------------------
   روزشمار تعاملی با لمس
---------------------------- */

.countdown-intro {
 color:#8c7657;
 line-height:2.2;
 font-size:14px;
 margin-bottom:24px;
}

.countdown-wrap {
 position:relative;
 width:100%;
 max-width:560px;
 margin:0 auto;
 padding:12px 0;
 touch-action:pan-y;
 user-select:none;
 -webkit-user-select:none;
}

.countdown {
 display:grid;
 grid-template-columns:repeat(4,minmax(0,1fr));
 gap:12px;
 direction:rtl;
}

.time {
 min-width:0;
 aspect-ratio:1;
 border-radius:50%;
 background:
  radial-gradient(circle at 30% 25%,#fff,#f0dfbd);
 border:1px solid #d7bb80;
 box-shadow:
  0 9px 22px #80633a20,
  inset 0 2px 6px white;
 display:flex;
 flex-direction:column;
 align-items:center;
 justify-content:center;
 gap:4px;
}

.time strong {
 font-size:clamp(18px,4vw,30px);
 color:#a17b3d;
 font-weight:700;
}

.time small {
 color:#8c7759;
 font-size:clamp(10px,2.5vw,13px);
}

.countdown-cover {
 position:absolute;
 inset:0;
 z-index:3;
 border-radius:24px;
 background:
  radial-gradient(ellipse at 30% 30%,rgba(255,255,255,.88),rgba(239,224,195,.96)),
  repeating-linear-gradient(45deg,rgba(177,138,75,.08) 0 2px,transparent 2px 8px);
 backdrop-filter:blur(13px);
 -webkit-backdrop-filter:blur(13px);
 border:1px solid rgba(177,138,75,.3);
 display:flex;
 align-items:center;
 justify-content:center;
 color:#8f7040;
 font-size:14px;
 pointer-events:none;
 -webkit-mask-image:radial-gradient(circle 0px at var(--x,50%) var(--y,50%),transparent 0px,black 1px);
 mask-image:radial-gradient(circle 0px at var(--x,50%) var(--y,50%),transparent 0px,black 1px);
 transition:opacity .25s ease;
}

.countdown-wrap.is-revealing .countdown-cover {
 -webkit-mask-image:radial-gradient(circle 78px at var(--x,50%) var(--y,50%),transparent 0 62px,#000 86px);
 mask-image:radial-gradient(circle 78px at var(--x,50%) var(--y,50%),transparent 0 62px,#000 86px);
}

.countdown-hint {
 margin-top:20px;
 color:#9b8058;
 font-size:12px;
}

/* ---------------------------
   جزئیات مراسم
---------------------------- */

.details {
 display:grid;
 grid-template-columns:repeat(2,minmax(0,1fr));
 gap:30px;
 max-width:750px;
 margin:0 auto;
}

.detail {
 position:relative;
 min-width:0;
 padding:32px 18px;
 border:1px solid rgba(177,138,75,.45);
 background:rgba(255,250,240,.48);
 transition:transform .5s ease,background .5s ease,box-shadow .5s ease;
}

.detail:hover {
 transform:translateY(-8px);
 background:rgba(255,250,240,.8);
 box-shadow:0 18px 35px #80633a18;
}

.symbol {
 font-size:35px;
 color:#b28a48;
}

.detail h3 {
 color:#9b773e;
 font-weight:600;
}

.detail p {
 line-height:2.2;
 font-size:14px;
 color:#796448;
}

.address-text {
 line-height:2.4;
 margin:30px auto 15px;
 max-width:650px;
 font-size:14px;
}

.action {
 display:inline-flex;
 align-items:center;
 justify-content:center;
 border:1px solid #c5a36a;
 border-radius:3px;
 padding:14px 30px;
 color:#fff9ed;
 background:linear-gradient(135deg,#b89456,#89642f);
 box-shadow:0 8px 20px #80633a25;
 transition:transform .35s ease,box-shadow .35s ease;
 margin:8px;
 max-width:100%;
}

.action:hover {
 transform:translateY(-4px);
 box-shadow:0 13px 25px #80633a35;
}

/* ---------------------------
   گالری
---------------------------- */

.gallery {
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(min(220px,100%),1fr));
 gap:28px;
 padding:10px;
 min-width:0;
 perspective:1000px;
}

.photo {
 position:relative;
 width:100%;
 min-width:0;
 height:300px;
 padding:9px;
 border:1px solid #c9ab72;
 border-radius:3px;
 background:linear-gradient(145deg,#fff,#ead8b6);
 box-shadow:0 14px 30px #80633a25;
 overflow:hidden;
 transition:transform .6s cubic-bezier(.2,.7,.2,1),box-shadow .6s ease;
}

.photo:hover {
 transform:translateY(-9px) rotateY(-5deg) rotateX(2deg);
 box-shadow:0 24px 40px #80633a35;
}

.photo img {
 width:100%;
 height:100%;
 object-fit:cover;
 display:block;
 transition:transform .8s ease;
}

.photo:hover img {transform:scale(1.055)}

.empty {color:#9c835e}

.video-frame {
 max-width:750px;
 margin:auto;
 padding:10px;
 border:1px solid #c9ab72;
 background:#fff9ed;
 box-shadow:0 18px 35px #80633a25;
}

.video {
 width:100%;
 display:block;
}

/* ---------------------------
   فرم حضور
---------------------------- */

.form {
 width:100%;
 max-width:490px;
 margin:25px auto 0;
}

.form input,
.form select {
 display:block;
 width:100%;
 max-width:100%;
 padding:15px 20px;
 margin:12px 0;
 border:1px solid #ddc99f;
 border-radius:3px;
 outline:none;
 color:#5c4930;
 background:rgba(255,253,248,.8);
 transition:border-color .3s,box-shadow .3s;
}

.form input:focus,
.form select:focus {
 border-color:#b28a48;
 box-shadow:0 0 0 3px #d9bd8340;
}

.choice-title {
 margin:25px 0 12px;
 color:#8b7048;
 font-weight:600;
}

.attendance-options {
 display:grid;
 grid-template-columns:repeat(2,minmax(0,1fr));
 gap:12px;
 margin-top:12px;
}

.attendance-option {
 position:relative;
 display:block;
 min-width:0;
 cursor:pointer;
}

.attendance-option input {
 position:absolute;
 opacity:0;
 pointer-events:none;
}

.choice-card {
 min-height:115px;
 padding:17px 12px;
 border:1px solid #d9c49b;
 background:rgba(255,253,248,.7);
 display:flex;
 flex-direction:column;
 align-items:center;
 justify-content:center;
 gap:9px;
 line-height:1.9;
 color:#725b3b;
 transition:.3s;
}

.choice-card .choice-icon {
 font-size:25px;
 color:#b18a4b;
}

.attendance-option.yes input:checked + .choice-card {
 border-color:#77966c;
 background:#edf4e9;
 box-shadow:0 0 0 3px #77966c25;
 color:#45643d;
}

.attendance-option.no input:checked + .choice-card {
 border-color:#bd8b80;
 background:#f9eeeb;
 box-shadow:0 0 0 3px #bd8b8025;
 color:#87554d;
}

.attendance-option input:focus-visible + .choice-card {
 outline:3px solid #b18a4b;
 outline-offset:3px;
}

.form-submit {
 width:100%;
 margin-top:20px;
}

.form-submit:disabled {
 opacity:.7;
 cursor:wait;
 transform:none;
}

/* ---------------------------
   پایان و نورهای شناور
---------------------------- */

.closing {
 padding:80px 15px 50px;
 text-align:center;
 color:#987b50;
 line-height:2.7;
}

.closing-ornament {
 width:75px;
 height:75px;
 border:1px solid rgba(177,138,75,.6);
 border-radius:50%;
 display:grid;
 place-items:center;
 margin:0 auto 25px;
 color:#a17b3d;
 font-size:27px;
 animation:slowRotate 22s linear infinite;
}

.closing strong {
 display:block;
 font-family:Marhey,Vazirmatn,sans-serif;
 color:#a17b3d;
 font-size:clamp(25px,6vw,38px);
}

.footer {
 text-align:center;
 padding:20px 15px 60px;
 color:#987b50;
 font-size:12px;
}

.lightbox {
 position:fixed;
 inset:0;
 z-index:2000;
 background:#20180fee;
 display:none;
 align-items:center;
 justify-content:center;
 padding:20px;
}

.lightbox.show {display:flex}

.lightbox img {
 max-width:95%;
 max-height:85vh;
 border:7px solid #e7d2a5;
 box-shadow:0 20px 70px #0008;
}

.close {
 position:absolute;
 top:20px;
 left:25px;
 color:white;
 background:none;
 border:0;
 font-size:35px;
}

.petal {
 position:fixed;
 top:-30px;
 color:#b18a4b;
 opacity:.28;
 pointer-events:none;
 z-index:2;
 animation:fall linear infinite;
}

@keyframes fall {
 to {transform:translateY(110vh) rotate(450deg)}
}

/* ---------------------------
   موبایل
---------------------------- */

@media screen and (max-width:768px) {
 .page-frame {inset:7px}

 .hero {
  min-height:95svh;
  padding:70px 15px 65px;
 }

 .hero-content {padding:30px 10px}

 .section {
  width:calc(100% - 28px);
  max-width:calc(100% - 28px);
  margin:65px auto;
  padding:40px 13px;
 }

 .countdown {
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:5px;
 }

 .details,
 .gallery {
  grid-template-columns:minmax(0,1fr);
 }

 .attendance-options {
  grid-template-columns:minmax(0,1fr);
 }

 .photo {height:270px}

 .intro-caption {top:18%}
 .intro-title {top:27%}
 .open-hint {bottom:17%}
}

@media(prefers-reduced-motion:reduce) {
 *,
 *::before,
 *::after {
  animation-duration:.01ms!important;
  transition-duration:.01ms!important;
  scroll-behavior:auto!important;
 }
}
</style>
</head>

<body>

<!-- نامه آغازین -->
<div class="intro" id="intro">
 <div class="envelope-wrap">

  <div class="envelope" id="envelope" onclick="openInvitation()">

   <div class="letter-under">
    <div class="letter-under-inner">
     <div>با عشق و احترام</div>
     <strong>امیر و زهرا</strong>
     <div>دعوت‌نامه جشن پیوند ما</div>
    </div>
   </div>

   <div class="envelope-flap"></div>

   <div class="corner tl"></div>
   <div class="corner tr"></div>
   <div class="corner bl"></div>
   <div class="corner br"></div>

   <div class="intro-caption">یک دعوت ویژه برای شما</div>
   <div class="intro-title">لحظه‌ای برای یک خاطره ابدی</div>

   <div class="seal">A ♡ Z</div>

   <div class="open-hint">برای گشودن دعوت‌نامه لمس کنید</div>

  </div>
 </div>
</div>

<!-- محتوای اصلی -->
<main id="site">

 <div class="page-frame"></div>

 <header class="hero">
  <div class="hero-content">

   <div class="eyebrow">دعوت‌نامه رسمی جشن ازدواج</div>

   <div class="names">
    امیر
    <span>و</span>
    زهرا
   </div>

   <div class="gold-line"></div>

   <p class="invitation">
    با افتخار از شما دعوت می‌کنیم
    تا در جشن آغاز زندگی مشترک ما حضور داشته باشید
    و شادی این لحظه زیبا را با ما قسمت کنید.
   </p>

   <div class="hero-ornament">A ♡ Z</div>

   <div class="hero-date">
    چهارشنبه ۲ دی ۱۴۰۵<br>
    ساعت ۱۹ تا ۲۲
   </div>

  </div>

  <div class="scroll-cue">
   <span>ادامه دعوت‌نامه</span>
   <span></span>
  </div>
 </header>

 <!-- روزشمار -->
 <section class="section reveal">
  <div class="section-title">تا آغاز یک خاطره جاودانه</div>

  <p class="countdown-intro">
   لحظه‌شماری برای روز زیبای دیدار
  </p>

  <div class="countdown-wrap" id="countdownWrap">

   <div class="countdown">
    <div class="time">
     <strong id="days">۰</strong>
     <small>روز</small>
    </div>

    <div class="time">
     <strong id="hours">۰</strong>
     <small>ساعت</small>
    </div>

    <div class="time">
     <strong id="minutes">۰</strong>
     <small>دقیقه</small>
    </div>

    <div class="time">
     <strong id="seconds">۰</strong>
     <small>ثانیه</small>
    </div>
   </div>

   <div class="countdown-cover" id="countdownCover">
    ✧ با لمس و کشیدن انگشت، زمان را آشکار کنید ✧
   </div>

  </div>

  <div class="countdown-hint">
   انگشت خود را روی تصویر حرکت دهید تا اعداد نمایان شوند
  </div>
 </section>

 <!-- اطلاعات مراسم -->
 <section class="section reveal">
  <div class="section-title">جزئیات مراسم</div>

  <div class="details">

   <div class="detail">
    <div class="symbol">♛</div>
    <h3>زمان جشن</h3>
    <p>
     چهارشنبه ۲ دی ۱۴۰۵<br>
     ساعت ۱۹ تا ۲۲
    </p>
   </div>

   <div class="detail">
    <div class="symbol">✧</div>
    <h3>مکان مراسم</h3>
    <p>
     تالار پذیرایی فریال<br>
     سمنان
    </p>
   </div>

  </div>

  <p class="address-text">{{ADDRESS}}</p>

  <a class="action"
     target="_blank"
     rel="noopener"
     href="{{MAP_URL}}">
    مشاهده مسیر تالار
  </a>
 </section>

 <!-- گالری -->
 <section class="section reveal">
  <div class="section-title">قاب‌هایی از خاطرات</div>
  <div class="gallery">{{GALLERY}}</div>
 </section>

 {{VIDEO}}

 <!-- پاسخ دعوت -->
 <section class="section reveal" id="rsvp">
  <div class="section-title">حضور شما مایه افتخار ماست</div>

  <p>
   لطفاً نام و تعداد مهمانان را وارد کنید
   و پاسخ خود را برای ما بفرستید.
  </p>

  <form class="form" id="rsvpForm">

   <input
    name="name"
    maxlength="80"
    placeholder="نام و نام خانوادگی"
    required
   >

   <select name="count" aria-label="تعداد مهمانان">
    <option value="1">۱ نفر</option>
    <option value="2">۲ نفر</option>
    <option value="3">۳ نفر</option>
    <option value="4">۴ نفر</option>
    <option value="5">۵ نفر</option>
    <option value="6">۶ نفر</option>
    <option value="7">۷ نفر</option>
    <option value="8">۸ نفر</option>
    <option value="9">۹ نفر</option>
    <option value="10">۱۰ نفر</option>
   </select>

   <div class="choice-title">پاسخ شما به دعوت</div>

   <div class="attendance-options">

    <label class="attendance-option yes">
     <input
      type="radio"
      name="attendance"
      value="yes"
      required
     >

     <span class="choice-card">
      <span class="choice-icon">♡</span>
      <span>با کمال میل در جشن شما حضور خواهم داشت</span>
     </span>
    </label>

    <label class="attendance-option no">
     <input
      type="radio"
      name="attendance"
      value="no"
      required
     >

     <span class="choice-card">
      <span class="choice-icon">✧</span>
      <span>متأسفانه امکان حضور ندارم</span>
     </span>
    </label>

   </div>

   <button class="action form-submit" type="submit">
    ثبت پاسخ
   </button>

  </form>
 </section>

 <audio id="weddingMusic" loop preload="auto">
  <source src="/static/music.mp3" type="audio/mpeg">
 </audio>

 <section class="closing reveal">
  <div class="closing-ornament">✧</div>
  <div>به امید دیدار در زیباترین شب زندگی‌مان</div>
  <strong>امیر ♡ زهرا</strong>
  <div>۲ دی ۱۴۰۵</div>
 </section>

 <footer class="footer">
  با عشق، برای یک شروع زیبا
 </footer>

</main>

<!-- نمایش بزرگ عکس -->
<div class="lightbox" id="lightbox" onclick="closePhoto()">
 <button class="close" aria-label="بستن">×</button>
 <img id="largePhoto" alt="نمایش بزرگ عکس">
</div>

<script>
let opened = false;

const weddingAudio = document.getElementById("weddingMusic");

// تلاش برای پخش خودکار؛ ممکن است مرورگر اجازه ندهد.
if (weddingAudio) {
 weddingAudio.load();

 weddingAudio.play().catch(() => {
  console.log("Autoplay requires user interaction.");
 });
}


// باز شدن نامه
function openInvitation() {
 if (opened) return;

 opened = true;

 const envelope = document.getElementById("envelope");
 const intro = document.getElementById("intro");
 const site = document.getElementById("site");

 // شروع موسیقی با لمس کاربر
 if (weddingAudio && weddingAudio.paused) {
  weddingAudio.play().catch(() => {
   console.log("Audio playback was blocked.");
  });
 }

 envelope.classList.add("open");

 // کمی مکث برای حس سینمایی
 setTimeout(() => {
  site.classList.add("visible");
 }, 350);

 setTimeout(() => {
  intro.classList.add("leaving");
 }, 950);

 setTimeout(() => {
  intro.style.display = "none";
  document.body.style.overflow = "auto";
  window.scrollTo(0, 0);
 }, 2400);
}

document.body.style.overflow = "hidden";


// نمایش بخش‌ها هنگام اسکرول
const revealItems = document.querySelectorAll(".reveal");

if ("IntersectionObserver" in window) {
 const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
   if (entry.isIntersecting) {
    entry.target.classList.add("visible");
    revealObserver.unobserve(entry.target);
   }
  });
 }, {
  threshold: 0.13,
  rootMargin: "0px 0px -35px 0px"
 });

 revealItems.forEach(item => revealObserver.observe(item));

} else {
 revealItems.forEach(item => item.classList.add("visible"));
}


// روزشمار
const target = new Date("{{DATE}}").getTime();

function updateCountdown() {
 let diff = Math.max(0, target - Date.now());

 const values = {
  days: Math.floor(diff / 86400000),
  hours: Math.floor(diff / 3600000) % 24,
  minutes: Math.floor(diff / 60000) % 60,
  seconds: Math.floor(diff / 1000) % 60
 };

 for (const id in values) {
  const element = document.getElementById(id);

  if (element) {
   element.textContent = values[id].toLocaleString("fa-IR");
  }
 }
}

updateCountdown();
setInterval(updateCountdown, 1000);


// افکت پاک شدن مه با لمس یا حرکت ماوس
const countdownWrap = document.getElementById("countdownWrap");
const countdownCover = document.getElementById("countdownCover");

function revealCountdown(event) {
 const rect = countdownWrap.getBoundingClientRect();

 const x = event.clientX - rect.left;
 const y = event.clientY - rect.top;

 countdownCover.style.setProperty("--x", x + "px");
 countdownCover.style.setProperty("--y", y + "px");

 countdownWrap.classList.add("is-revealing");
}

countdownWrap.addEventListener("pointerdown", revealCountdown);
countdownWrap.addEventListener("pointermove", event => {
 if (event.pointerType === "touch" || event.buttons === 1) {
  revealCountdown(event);
 }
});

countdownWrap.addEventListener("pointerleave", () => {
 countdownWrap.classList.remove("is-revealing");
});

countdownWrap.addEventListener("pointerup", () => {
 setTimeout(() => {
  countdownWrap.classList.remove("is-revealing");
 }, 1800);
});


// گالری عکس
function openPhoto(button) {
 const img = button.querySelector("img");

 document.getElementById("largePhoto").src = img.src;
 document.getElementById("lightbox").classList.add("show");
}

function closePhoto() {
 document.getElementById("lightbox").classList.remove("show");
}

document.addEventListener("keydown", event => {
 if (event.key === "Escape") {
  closePhoto();
 }
});


// ثبت پاسخ بدون بارگذاری مجدد
const rsvpForm = document.getElementById("rsvpForm");

rsvpForm.addEventListener("submit", async function(event) {
 event.preventDefault();

 const submitButton = rsvpForm.querySelector(".form-submit");

 submitButton.disabled = true;
 submitButton.textContent = "در حال ثبت پاسخ...";

 try {
  const response = await fetch("/", {
   method: "POST",
   body: new FormData(rsvpForm)
  });

  const result = await response.json();

  alert(result.message);

  if (result.ok) {
   rsvpForm.reset();
  }

 } catch (error) {
  alert("ارتباط برقرار نشد. لطفاً دوباره تلاش کنید.");

 } finally {
  submitButton.disabled = false;
  submitButton.textContent = "ثبت پاسخ";
 }
});


// ذرات طلایی شناور
for (let i = 0; i < 13; i++) {
 const petal = document.createElement("div");

 petal.className = "petal";
 petal.textContent = "✦";
 petal.style.left = Math.random() * 100 + "vw";
 petal.style.animationDuration = (12 + Math.random() * 14) + "s";
 petal.style.animationDelay = (-Math.random() * 18) + "s";
 petal.style.fontSize = (9 + Math.random() * 12) + "px";

 document.body.appendChild(petal);
}

</script>

</body>
</html>
"""


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
