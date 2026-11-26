
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

    # ثبت پاسخ بدون رفرش صفحه
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

    photos = [
        f"/static/photo{i}.jpg"
        for i in range(1, 7)
        if (STATIC / f"photo{i}.jpg").is_file()
        and (STATIC / f"photo{i}.jpg").stat().st_size > 1000
    ]

    gallery = "".join(
        f'<button class="photo" onclick="openPhoto(this)"><img src="{p}" alt="خاطره زیبا"></button>'
        for p in photos
    ) or '<p class="empty">عکس‌ها به‌زودی اضافه می‌شوند.</p>'

    video = ""
    video_file = STATIC / "wedding.mp4"

    if video_file.is_file() and video_file.stat().st_size > 1000:
        video = """
        <section class="section">
          <div class="section-title">لحظه‌های عاشقانه</div>
          <video class="video" controls playsinline preload="metadata">
            <source src="/static/wedding.mp4" type="video/mp4">
          </video>
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
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
<meta name="theme-color" content="#f9f0df">
<title>دعوت‌نامه عروسی امیر و زهرا</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');

:root {
 --gold:#b18a4b;
 --cream:#fffaf0;
 --ink:#59452f;
}

* { box-sizing:border-box; }

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
 radial-gradient(ellipse at 10% 15%,#f0dfbd,transparent 35%),
 radial-gradient(ellipse at 90% 60%,#f2e5d2,transparent 35%),
 linear-gradient(135deg,#fffaf0,#f5ead8,#fffdf7);
 overflow-x:hidden;
}

button,input,select {
 font:inherit;
 max-width:100%;
}

button {cursor:pointer}
a {color:inherit;text-decoration:none}

img,video {max-width:100%;}

.intro {
 position:fixed;
 inset:0;
 z-index:1000;
 display:flex;
 align-items:center;
 justify-content:center;
 padding:20px;
 background:radial-gradient(circle,#fffdf6,#e9d7b5);
 opacity:1;
 visibility:visible;
 transition:opacity 1.25s ease, visibility 1.25s ease;
}

.intro.leaving {
 opacity:0;
 visibility:hidden;
 pointer-events:none;
}

.envelope-wrap {
 width:min(440px,90vw);
 max-width:100%;
 text-align:center;
}

.intro-caption {
 color:#987541;
 margin-bottom:30px;
 letter-spacing:2px;
}

.envelope {
 position:relative;
 width:100%;
 aspect-ratio:1.45;
 border-radius:20px;
 background:linear-gradient(145deg,#f8edda,#e7d2ad);
 box-shadow:0 30px 65px #6f542d45,inset 0 2px 5px white;
 border:1px solid #d1b77e;
 overflow:hidden;
 cursor:pointer;
 -webkit-tap-highlight-color:transparent;
}

.envelope-flap {
 position:absolute;
 inset:0 0 auto;
 height:60%;
 background:linear-gradient(150deg,#fff5e1,#d9c08e);
 clip-path:polygon(0 0,100% 0,50% 100%);
 transform-origin:top;
 transition:transform 1.1s cubic-bezier(.22,.61,.36,1);
 z-index:4;
}

.seal {
 position:absolute;
 z-index:5;
 width:83px;
 height:83px;
 border-radius:50%;
 top:43%;
 left:50%;
 transform:translate(-50%,-50%);
 display:grid;
 place-items:center;
 color:#fff5d7;
 font-size:25px;
 background:radial-gradient(circle at 30% 25%,#f0d89b,#b18a4b 65%,#735329);
 border:5px double #f9e9bd;
 box-shadow:0 7px 20px #75552d55;
 transition:opacity .35s ease;
}

.letter {
 position:absolute;
 z-index:2;
 left:8%;
 right:8%;
 bottom:8%;
 height:75%;
 border-radius:42px;
 background:linear-gradient(145deg,#fffefa,#fff5df);
 box-shadow:0 0 20px #8c6a3530;
 border:1px solid #ead9b8;
 transition:transform 1.1s cubic-bezier(.22,.61,.36,1);
}

.envelope.open .envelope-flap {transform:rotateX(180deg);}
.envelope.open .seal {opacity:0;}
.envelope.open .letter {transform:translateY(-65%);}

#site {
 width:100%;
 max-width:100%;
 overflow-x:clip;
 opacity:0;
 visibility:hidden;
 transform:translateY(18px);
 transition:opacity 1.7s ease,transform 1.7s ease,visibility 1.7s ease;
}

#site.visible {
 opacity:1;
 visibility:visible;
 transform:translateY(0);
}

.hero {
 width:100%;
 max-width:100%;
 min-height:100vh;
 display:flex;
 justify-content:center;
 align-items:center;
 text-align:center;
 padding:35px 18px;
}

.hero-card {
 width:min(850px,100%);
 max-width:100%;
 min-width:0;
 padding:75px 25px;
 border-radius:48% 48% 35% 35% / 22% 22% 15% 15%;
 border:1px solid #d5b77d;
 background:radial-gradient(ellipse at top,#fff,#fffaf0 60%,#f1e3c9);
 box-shadow:0 35px 80px #80633a25,inset 0 0 45px #d9bd8330,0 0 0 9px #ffffff80;
 position:relative;
 overflow:hidden;
}

.eyebrow {font-size:13px;letter-spacing:3px;color:#a27e45;}

.names {
 font-size:clamp(48px,10vw,88px);
 font-weight:700;
 color:#a47c3d;
 line-height:1.45;
 margin:25px 0;
 text-shadow:0 6px 18px #c9a86c45;
}

.and {display:block;font-size:24px;color:#c1a06a;}

.gold-line {
 width:140px;
 height:2px;
 margin:25px auto;
 background:linear-gradient(90deg,transparent,#b28a48,transparent);
}

.invitation {
 max-width:450px;
 margin:auto;
 line-height:2.5;
 color:#796448;
}

.round-seal {
 width:90px;
 height:90px;
 margin:30px auto;
 border-radius:50%;
 display:grid;
 place-items:center;
 color:white;
 font-size:29px;
 background:radial-gradient(circle at 35% 30%,#efd99f,#b18a48 65%,#785627);
 box-shadow:0 9px 22px #80633a55;
 border:4px double #f8e9bd;
}

.section {
 width:min(1050px,92%);
 max-width:calc(100% - 24px);
 min-width:0;
 margin:80px auto;
 padding:42px 22px;
 border-radius:55px;
 background:linear-gradient(145deg,#fffdf8,#f8efdf);
 border:1px solid #ead9b8;
 box-shadow:0 25px 60px #82643b20,inset 0 2px 10px white;
 text-align:center;
}

.section-title {
 font-size:27px;
 color:#a17b3d;
 font-weight:700;
 margin-bottom:30px;
}

.section-title:after {
 content:"✧";
 display:block;
 color:#c4a166;
 margin-top:8px;
}

.countdown {
 display:grid;
 grid-template-columns:repeat(4,minmax(0,1fr));
 justify-content:center;
 gap:10px;
 direction:rtl;
 width:100%;
 max-width:520px;
 margin:0 auto;
}

.time {
 width:100%;
 min-width:0;
 height:auto;
 aspect-ratio:1;
 border-radius:50%;
 background:linear-gradient(145deg,#fff,#f0dfbd);
 border:1px solid #d7bb80;
 box-shadow:0 9px 20px #80633a20,inset 0 2px 5px white;
 display:flex;
 flex-direction:column;
 align-items:center;
 justify-content:center;
}

.time strong {font-size:clamp(15px,4vw,26px);color:#a17b3d;}
.time small {color:#8c7759;font-size:clamp(9px,2.5vw,14px);}

.details {
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
 gap:20px;
}

.detail {
 min-width:0;
 padding:30px 15px;
 border-radius:45px;
 background:linear-gradient(145deg,#fff,#f1e4ca);
 border:1px solid #e3cea4;
 box-shadow:0 10px 25px #80633a18;
}

.symbol {font-size:34px;color:#b28a48;}
.detail h3 {color:#9b773e;}
.detail p {line-height:2.1;font-size:14px;}

.action {
 display:inline-flex;
 align-items:center;
 justify-content:center;
 border:0;
 border-radius:50px;
 padding:14px 27px;
 color:white;
 background:linear-gradient(135deg,#d6b875,#98713a);
 box-shadow:0 8px 20px #80633a35;
 transition:.3s;
 margin:7px;
 max-width:100%;
}

.action:hover {transform:translateY(-3px);}

.gallery {
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(min(210px,100%),1fr));
 gap:25px;
 padding:10px;
 min-width:0;
}

.photo {
 width:100%;
 min-width:0;
 height:285px;
 padding:9px;
 border:0;
 border-radius:48% 48% 35% 35%;
 background:linear-gradient(145deg,#fff,#d9bd83);
 box-shadow:0 15px 30px #80633a30;
 overflow:hidden;
 transition:transform .4s;
}

.photo:hover {transform:translateY(-8px) rotate(1deg);}
.photo img {width:100%;height:100%;object-fit:cover;border-radius:inherit;}
.empty {color:#9c835e;}

.video {
 width:100%;
 max-width:700px;
 border-radius:35px;
 box-shadow:0 15px 35px #80633a30;
}

.form {width:100%;max-width:490px;margin:25px auto 0;}

.form input,.form select {
 display:block;
 width:100%;
 max-width:100%;
 padding:15px 20px;
 margin:9px 0;
 border:1px solid #ddc99f;
 border-radius:35px;
 outline:none;
 color:#5c4930;
 background:#fffdf8;
}

.form input:focus,.form select:focus {
 border-color:#b28a48;
 box-shadow:0 0 0 3px #d9bd8340;
}

.choice-title {margin:22px 0 12px;color:#8b7048;font-weight:600;}

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
 min-height:105px;
 padding:17px 12px;
 border:2px solid #e2d2b2;
 border-radius:25px;
 background:linear-gradient(145deg,#fffefa,#f8efdf);
 display:flex;
 flex-direction:column;
 align-items:center;
 justify-content:center;
 gap:9px;
 line-height:1.9;
 color:#725b3b;
 transition:.2s;
}

.choice-card .choice-icon {font-size:25px;}

.attendance-option.yes input:checked+.choice-card {
 border-color:#77966c;
 background:#edf4e9;
 box-shadow:0 0 0 3px #77966c25;
 color:#45643d;
}

.attendance-option.no input:checked+.choice-card {
 border-color:#bd8b80;
 background:#f9eeeb;
 box-shadow:0 0 0 3px #bd8b8025;
 color:#87554d;
}

.attendance-option input:focus-visible+.choice-card {
 outline:3px solid #b18a4b;
 outline-offset:3px;
}

.form-submit {width:100%;margin-top:20px;}

.form-submit:disabled {
 opacity:.7;
 cursor:wait;
 transform:none;
}

.footer {
 text-align:center;
 padding:50px 15px;
 color:#987b50;
 line-height:2.5;
}

.footer strong {color:#a17b3d;font-size:22px;}

.lightbox {
 position:fixed;
 inset:0;
 z-index:2000;
 background:#20180fdc;
 display:none;
 align-items:center;
 justify-content:center;
 padding:20px;
}

.lightbox.show {display:flex;}

.lightbox img {
 max-width:95%;
 max-height:85vh;
 border:7px solid #e7d2a5;
 border-radius:35px;
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
 color:#c7a66c;
 opacity:.35;
 pointer-events:none;
 z-index:5;
 animation:fall linear infinite;
}

@keyframes fall {to {transform:translateY(110vh) rotate(450deg);}}

@media screen and (max-width:768px) {
 html,body {
  width:100%;
  max-width:100%;
  overflow-x:hidden;
 }

 #site {
  width:100%;
  max-width:100%;
  overflow-x:clip;
 }

 .hero {min-height:auto;padding:35px 12px;}

 .hero-card {
  width:100%;
  padding:45px 15px;
  border-radius:35px;
 }

 .section {
  width:calc(100% - 24px);
  max-width:calc(100% - 24px);
  margin:35px auto;
  padding:28px 12px;
  border-radius:28px;
 }

 .countdown {
  width:100%;
  grid-template-columns:repeat(4,minmax(0,1fr));
  gap:5px;
 }

 .time {width:100%;min-width:0;}

 .details,.gallery {grid-template-columns:minmax(0,1fr);}

 .attendance-options {grid-template-columns:minmax(0,1fr);}

 .names {font-size:clamp(42px,12vw,60px);}
 .photo {height:240px;}
}

@media(prefers-reduced-motion:reduce) {
 *,*:before,*:after {
  animation-duration:.01ms!important;
  transition-duration:.01ms!important;
  scroll-behavior:auto!important;
 }
}
</style>
</head>

<body>

<div class="intro" id="intro">
 <div class="envelope-wrap">
  <div class="intro-caption">یک دعوت ویژه برای شما</div>

  <div class="envelope" id="envelope" onclick="openInvitation()">
   <div class="letter"></div>
   <div class="envelope-flap"></div>
   <div class="seal">A ♡ Z</div>
  </div>
 </div>
</div>

<main id="site">

<header class="hero">
 <div class="hero-card">
  <div class="eyebrow">دعوت‌نامه رسمی جشن ازدواج</div>
  <div class="names">امیر<span class="and">و</span>زهرا</div>
  <div class="gold-line"></div>
  <p class="invitation">با افتخار از شما دعوت می‌کنیم در جشن آغاز زندگی مشترک ما حضور داشته باشید.</p>
  <div class="round-seal">A ♡ Z</div>
  <div>چهارشنبه ۲ دی ۱۴۰۵</div>
  <div>ساعت ۱۹ تا ۲۲</div>
 </div>
</header>

<section class="section">
 <div class="section-title">تا آغاز یک خاطره جاودانه</div>
 <div class="countdown">
  <div class="time"><strong id="days">۰</strong><small>روز</small></div>
  <div class="time"><strong id="hours">۰</strong><small>ساعت</small></div>
  <div class="time"><strong id="minutes">۰</strong><small>دقیقه</small></div>
  <div class="time"><strong id="seconds">۰</strong><small>ثانیه</small></div>
 </div>
</section>

<section class="section">
 <div class="section-title">جزئیات مراسم</div>

 <div class="details">
  <div class="detail">
   <div class="symbol">♛</div>
   <h3>زمان جشن</h3>
   <p>چهارشنبه ۲ دی ۱۴۰۵<br>۱۹ تا ۲۲</p>
  </div>

  <div class="detail">
   <div class="symbol">✧</div>
   <h3>مکان مراسم</h3>
   <p>تالار پذیرایی فریال<br>سمنان</p>
  </div>
 </div>

 <p style="line-height:2;margin-top:25px">{{ADDRESS}}</p>

 <a class="action" target="_blank" rel="noopener" href="{{MAP_URL}}">
    مسیریابی تا تالار
 </a>
</section>

<section class="section">
 <div class="section-title">قاب‌هایی از خاطرات</div>
 <div class="gallery">{{GALLERY}}</div>
</section>

{{VIDEO}}

<section class="section" id="rsvp">
 <div class="section-title">حضور شما مایه افتخار ماست</div>
 <p>لطفاً نام و تعداد مهمانان را وارد کنید و یکی از گزینه‌های زیر را انتخاب کنید.</p>

 <form class="form" id="rsvpForm">
  <input name="name" maxlength="80" placeholder="نام و نام خانوادگی" required>

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
    <input type="radio" name="attendance" value="yes" required>
    <span class="choice-card">
     <span class="choice-icon">♡</span>
     <span>با کمال میل در جشن شما حضور خواهم داشت</span>
    </span>
   </label>

   <label class="attendance-option no">
    <input type="radio" name="attendance" value="no" required>
    <span class="choice-card">
     <span class="choice-icon">✧</span>
     <span>متأسفانه امکان حضور ندارم</span>
    </span>
   </label>
  </div>

  <button class="action form-submit" type="submit">ثبت پاسخ</button>
 </form>
</section>

<audio id="weddingMusic" loop preload="auto">
 <source src="/static/music.mp3" type="audio/mpeg">
</audio>

<footer class="footer">
 <div>با عشق و آرزوی روزهایی روشن</div>
 <strong>امیر ♡ زهرا</strong>
 <div>۲ دی ۱۴۰۵</div>
</footer>

</main>

<div class="lightbox" id="lightbox" onclick="closePhoto()">
 <button class="close" aria-label="بستن">×</button>
 <img id="largePhoto" alt="نمایش بزرگ عکس">
</div>

<script>
let opened = false;

const weddingAudio = document.getElementById("weddingMusic");

if (weddingAudio) {
 weddingAudio.load();
}

function openInvitation() {
 if (opened) return;
 opened = true;

 const envelope = document.getElementById("envelope");
 const intro = document.getElementById("intro");
 const site = document.getElementById("site");

 if (weddingAudio) {
  weddingAudio.currentTime = 0;
  weddingAudio.play().catch(error => {
   console.log("Audio playback was blocked:", error);
  });
 }

 envelope.classList.add("open");
 site.classList.add("visible");

 requestAnimationFrame(() => {
  intro.classList.add("leaving");
 });

 setTimeout(() => {
  intro.style.display = "none";
  document.body.style.overflow = "auto";
 }, 1300);
}

document.body.style.overflow = "hidden";

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
  document.getElementById(id).textContent =
   values[id].toLocaleString("fa-IR");
 }
}

updateCountdown();
setInterval(updateCountdown, 1000);

function openPhoto(button) {
 const img = button.querySelector("img");
 document.getElementById("largePhoto").src = img.src;
 document.getElementById("lightbox").classList.add("show");
}

function closePhoto() {
 document.getElementById("lightbox").classList.remove("show");
}

document.addEventListener("keydown", e => {
 if (e.key === "Escape") closePhoto();
});

// ثبت پاسخ بدون بارگذاری مجدد صفحه
const rsvpForm = document.getElementById("rsvpForm");

rsvpForm.addEventListener("submit", async function(e) {
 e.preventDefault();

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

for (let i = 0; i < 16; i++) {
 const petal = document.createElement("div");

 petal.className = "petal";
 petal.textContent = "✦";
 petal.style.left = Math.random() * 100 + "vw";
 petal.style.animationDuration = (9 + Math.random() * 12) + "s";
 petal.style.animationDelay = (-Math.random() * 15) + "s";
 petal.style.fontSize = (10 + Math.random() * 15) + "px";

 document.body.appendChild(petal);
}
</script>

</body>
</html>
"""

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
