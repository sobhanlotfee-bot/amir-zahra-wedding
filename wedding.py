from flask import Flask, request, redirect, send_file
from pathlib import Path
from datetime import datetime
import csv
import io
import html

app = Flask(__name__)

BASE = Path(__file__).resolve().parent
STATIC = BASE / "static"
STATIC.mkdir(exist_ok=True)

WEDDING_DATE = "2026-12-24T19:00:00+03:30"
ADDRESS = "میدان معلم، بلوار بسیج، جنب ورزشگاه القدیر، تبار پذیرایی فریال، سمنان"


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        name = request.form.get("name", "").strip()[:80]
        count = request.form.get("count", "1")
        if name and count in ["1", "2", "3", "4", "5"]:
            with open(BASE / "guests.csv", "a", newline="", encoding="utf-8-sig") as f:
                csv.writer(f).writerow([name, count, datetime.now().isoformat()])
        return redirect("/#rsvp")

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
    )


@app.route("/calendar")
def calendar():
    content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Amir and Zahra//Wedding//FA
BEGIN:VEVENT
UID:amir-zahra-wedding-20261224
DTSTAMP:20261125T120000Z
DTSTART:20261224T153000Z
DTEND:20261224T183000Z
SUMMARY:جشن ازدواج امیر و زهرا
LOCATION:پذیرایی فریال، سمنان
DESCRIPTION:جشن آغاز زندگی مشترک امیر و زهرا
END:VEVENT
END:VCALENDAR"""

    return send_file(
        io.BytesIO(content.encode("utf-8")),
        mimetype="text/calendar",
        as_attachment=True,
        download_name="amir-zahra-wedding.ics"
    )


PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#f9f0df">
<title>دعوت‌نامه عروسی امیر و زهرا</title>

<style>
@import url('https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');

:root {
 --gold:#b18a4b;
 --cream:#fffaf0;
 --ink:#59452f;
}

* {box-sizing:border-box}
html {scroll-behavior:smooth}
body {
 margin:0;
 font-family:Vazirmatn,Tahoma,sans-serif;
 color:var(--ink);
 background:
 radial-gradient(ellipse at 10% 15%,#f0dfbd,transparent 35%),
 radial-gradient(ellipse at 90% 60%,#f2e5d2,transparent 35%),
 linear-gradient(135deg,#fffaf0,#f5ead8,#fffdf7);
 overflow-x:hidden;
}
button,input,select {font:inherit}
button {cursor:pointer}
a {color:inherit;text-decoration:none}

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
 transition:opacity 1.5s ease, visibility 1.5s ease;
}
.intro.hidden {
 opacity:0;
 visibility:hidden;
 pointer-events:none;
}

.envelope-wrap {
 width:min(440px,90vw);
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
 transition:transform 1.2s ease;
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
 transition:opacity .5s ease;
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
 transition:transform 1.3s ease;
}

.envelope.open .envelope-flap {
 transform:rotateX(180deg);
}

.envelope.open .seal {
 opacity:0;
}

.envelope.open .letter {
 transform:translateY(-65%);
}

/* محو شدن کامل صفحه پاکت */
.intro.leaving {
 opacity:0;
 visibility:hidden;
 pointer-events:none;
}

#site {
 opacity:0;
 visibility:hidden;
 transform:translateY(35px);
 transition:
 opacity 1.8s ease,
 transform 1.8s ease,
 visibility 1.8s ease;
}

#site.visible {
 opacity:1;
 visibility:visible;
 transform:translateY(0);
}

.hero {
 min-height:100vh;
 display:flex;
 justify-content:center;
 align-items:center;
 text-align:center;
 padding:35px 18px;
}
.hero-card {
 width:min(850px,100%);
 padding:75px 25px;
 border-radius:48% 48% 35% 35% / 22% 22% 15% 15%;
 border:1px solid #d5b77d;
 background:radial-gradient(ellipse at top,#fff,#fffaf0 60%,#f1e3c9);
 box-shadow:0 35px 80px #80633a25,inset 0 0 45px #d9bd8330,0 0 0 9px #ffffff80;
 position:relative;
 overflow:hidden;
}
.eyebrow {font-size:13px;letter-spacing:3px;color:#a27e45}
.names {
 font-size:clamp(48px,10vw,88px);
 font-weight:700;
 color:#a47c3d;
 line-height:1.45;
 margin:25px 0;
 text-shadow:0 6px 18px #c9a86c45;
}
.and {display:block;font-size:24px;color:#c1a06a}
.gold-line {
 width:140px;
 height:2px;
 margin:25px auto;
 background:linear-gradient(90deg,transparent,#b28a48,transparent);
}
.invitation {max-width:450px;margin:auto;line-height:2.5;color:#796448}
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
.countdown {display:flex;justify-content:center;flex-wrap:wrap;gap:13px}
.time {
 width:105px;
 height:105px;
 border-radius:50%;
 background:linear-gradient(145deg,#fff,#f0dfbd);
 border:1px solid #d7bb80;
 box-shadow:0 9px 20px #80633a20,inset 0 2px 5px white;
 display:flex;
 flex-direction:column;
 align-items:center;
 justify-content:center;
}
.time strong {font-size:26px;color:#a17b3d}
.time small {color:#8c7759}
.details {
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
 gap:20px;
}
.detail {
 padding:30px 15px;
 border-radius:45px;
 background:linear-gradient(145deg,#fff,#f1e4ca);
 border:1px solid #e3cea4;
 box-shadow:0 10px 25px #80633a18;
}
.symbol {font-size:34px;color:#b28a48}
.detail h3 {color:#9b773e}
.detail p {line-height:2.1;font-size:14px}
.gallery {
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
 gap:25px;
 padding:10px;
}
.photo {
 height:285px;
 padding:9px;
 border:0;
 border-radius:48% 48% 35% 35%;
 background:linear-gradient(145deg,#fff,#d9bd83);
 box-shadow:0 15px 30px #80633a30;
 overflow:hidden;
 transition:transform .4s;
}
.photo:hover {transform:translateY(-8px) rotate(1deg)}
.photo img {width:100%;height:100%;object-fit:cover;border-radius:inherit}
.empty {color:#9c835e}
.video {
 width:100%;
 max-width:700px;
 border-radius:35px;
 box-shadow:0 15px 35px #80633a30;
}
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
}
.action:hover {transform:translateY(-3px)}
.form {max-width:450px;margin:auto}
.form input,.form select {
 width:100%;
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

.music-box {
 width:min(560px,92%);
 margin:45px auto;
 padding:28px 22px;
 text-align:center;
 border-radius:42px;
 border:1px solid #e2cda3;
 background:linear-gradient(145deg,#fffdf8,#f4e8d2);
 box-shadow:0 18px 45px #80633a20,inset 0 2px 8px white;
}
.music-heading {font-size:21px;font-weight:700;color:#9b773e}
.music-subtitle {font-size:13px;color:#9b8564;margin-top:7px}
.music-player {
 display:flex;
 align-items:center;
 gap:15px;
 margin:24px 0 18px;
 padding:15px;
 border-radius:28px;
 background:#fffaf0;
 border:1px solid #ead9b8;
}
.music-disc {
 width:58px;
 height:58px;
 flex:0 0 58px;
 border-radius:50%;
 display:grid;
 place-items:center;
 color:#fff4d7;
 font-size:27px;
 background:radial-gradient(circle at center,#e6cf9d 0 12%,#98713a 13% 18%,#d5b574 19% 100%);
}
.music-disc.playing {animation:spin 5s linear infinite}
@keyframes spin {to{transform:rotate(360deg)}}
.music-info {flex:1;text-align:right;min-width:0}
.music-info strong {display:block;color:#765a32;font-size:14px}
.music-info span {display:block;color:#9b8564;font-size:12px;margin-top:5px}
.music-play {
 width:48px;
 height:48px;
 flex:0 0 48px;
 border:0;
 border-radius:50%;
 color:white;
 font-size:18px;
 background:linear-gradient(135deg,#d6b875,#98713a);
}
.music-progress-row,.volume-row {
 display:flex;
 align-items:center;
 gap:10px;
 color:#8d7653;
 font-size:12px;
}
.music-progress-row input,.volume-row input {
 flex:1;
 min-width:0;
 accent-color:#aa8448;
}
.volume-row {max-width:260px;margin:12px auto 0}
.music-note {font-size:12px;color:#9b8564;margin:14px 0 0}

.footer {
 text-align:center;
 padding:50px 15px;
 color:#987b50;
 line-height:2.5;
}
.footer strong {color:#a17b3d;font-size:22px}
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
.lightbox.show {display:flex}
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
@keyframes fall {
 to {transform:translateY(110vh) rotate(450deg)}
}

@media(max-width:600px) {
 .hero-card {padding:65px 18px}
 .section {border-radius:38px;padding:32px 16px}
 .time {width:82px;height:82px}
 .time strong {font-size:21px}
 .photo {height:240px}
 .names {font-size:57px}
 .music-box {padding:24px 15px}
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
  <div>پنجشنبه ۳ دی ۱۴۰۵</div>
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
  <div class="detail"><div class="symbol">♛</div><h3>زمان جشن</h3><p>پنجشنبه ۳ دی ۱۴۰۵<br>۱۹ تا ۲۲</p></div>
  <div class="detail"><div class="symbol">✧</div><h3>مکان مراسم</h3><p>پذیرایی فریال<br>سمنان</p></div>
 </div>
 <p style="line-height:2;margin-top:25px">{{ADDRESS}}</p>
 <a class="action" target="_blank" rel="noopener" href="https://www.google.com/maps/search/?api=1&query=تبار+پذیرایی+فریال+سمنان">مشاهده مسیر روی نقشه</a>
 <a class="action" href="/calendar">افزودن به تقویم</a>
</section>

<section class="section">
 <div class="section-title">قاب‌هایی از خاطرات</div>
 <div class="gallery">{{GALLERY}}</div>
</section>

{{VIDEO}}

<section class="section" id="rsvp">
 <div class="section-title">حضور شما مایه افتخار ماست</div>
 <p>لطفاً حضور خود را ثبت کنید.</p>
 <form class="form" method="POST">
  <input name="name" maxlength="80" placeholder="نام و نام خانوادگی" required>
  <select name="count">
   <option value="1">۱ نفر</option>
   <option value="2">۲ نفر</option>
   <option value="3">۳ نفر</option>
   <option value="4">۴ نفر</option>
   <option value="5">۵ نفر</option>
  </select>
  <button class="action" type="submit">ثبت حضور</button>
 </form>
</section>

<section class="section">
 <div class="section-title">دعوت‌نامه را به اشتراک بگذارید</div>
 <p>خوشحال می‌شویم این دعوت را با عزیزانتان به اشتراک بگذارید.</p>
 <button class="action" onclick="shareInvite()">اشتراک‌گذاری</button>
 <button class="action" onclick="copyLink()">کپی لینک سایت</button>
</section>

<audio id="weddingMusic" loop preload="auto">
    <source src="/static/music.mp3" type="audio/mpeg">
</audio>

<footer class="footer">
 <div>با عشق و آرزوی روزهایی روشن</div>
 <strong>امیر ♡ زهرا</strong>
 <div>۳ دی ۱۴۰۵</div>
</footer>
</main>

<div class="lightbox" id="lightbox" onclick="closePhoto()">
 <button class="close" aria-label="بستن">×</button>
 <img id="largePhoto" alt="نمایش بزرگ عکس">
</div>

<script>
let opened = false;

function openInvitation() {
 if (opened) return;
 opened = true;

 const envelope = document.getElementById("envelope");
 const intro = document.getElementById("intro");
 const site = document.getElementById("site");

 envelope.classList.add("open");

 // ابتدا پاکت باز می‌شود؛ سپس صفحه اول محو می‌شود.
 setTimeout(() => {
  intro.classList.add("leaving");
  site.classList.add("visible");
  document.body.style.overflow = "auto";

  setTimeout(() => {
   intro.style.display = "none";
  }, 1600);

 }, 1500);
}

document.body.style.overflow = "hidden";
const music = document.getElementById("weddingMusic");

document.addEventListener("pointerdown", function startMusic() {
    if (!music) return;
    music.play().catch(() => {});
});

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

async function shareInvite() {
 const data = {
  title: "عروسی امیر و زهرا",
  text: "دعوت‌نامه جشن ازدواج امیر و زهرا",
  url: location.href
 };

 if (navigator.share) {
  try { await navigator.share(data); } catch (e) {}
 } else {
  copyLink();
 }
}

async function copyLink() {
 try {
  await navigator.clipboard.writeText(location.href);
  alert("لینک کپی شد.");
 } catch (e) {
  prompt("لینک سایت:", location.href);
 }
}
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