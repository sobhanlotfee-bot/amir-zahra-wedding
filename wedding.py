
import os
import io
import csv
import sqlite3
import secrets
from datetime import datetime
from functools import wraps

from flask import (
    Flask, request, redirect, url_for, session,
    render_template_string, Response, abort
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "CHANGE_THIS_SECRET_KEY")

DB_PATH = os.environ.get("DATABASE_PATH", "wedding.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "CHANGE_THIS_ADMIN_PASSWORD")

WEDDING_DATE = "2026-12-23T19:00:00+03:30"
VENUE = "تالار پذیرایی فریال"
ADDRESS = "استان سمنان، میدان معلم، بلوار بسیج، جنب ورزشگاه الغدیر"


# ---------------- DATABASE ----------------

def connect_db():
    con = sqlite3.connect(DB_PATH, timeout=20)
    con.row_factory = sqlite3.Row
    return con


def init_db():
    with connect_db() as con:
        con.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            count INTEGER NOT NULL DEFAULT 1,
            status TEXT NOT NULL DEFAULT 'در انتظار پاسخ',
            created TEXT,
            token TEXT,
            table_no TEXT DEFAULT '',
            seat_no TEXT DEFAULT '',
            checked_in INTEGER DEFAULT 0
        )
        """)

        # Add new columns without deleting previous guest records.
        columns = {
            row["name"]
            for row in con.execute("PRAGMA table_info(guests)").fetchall()
        }

        migrations = {
            "token": "ALTER TABLE guests ADD COLUMN token TEXT",
            "table_no": "ALTER TABLE guests ADD COLUMN table_no TEXT DEFAULT ''",
            "seat_no": "ALTER TABLE guests ADD COLUMN seat_no TEXT DEFAULT ''",
            "checked_in": "ALTER TABLE guests ADD COLUMN checked_in INTEGER DEFAULT 0",
        }

        for column, sql in migrations.items():
            if column not in columns:
                con.execute(sql)

        con.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created TEXT
        )
        """)

        old_guests = con.execute(
            "SELECT id FROM guests WHERE token IS NULL OR token=''"
        ).fetchall()

        for guest in old_guests:
            con.execute(
                "UPDATE guests SET token=? WHERE id=?",
                (secrets.token_urlsafe(20), guest["id"])
            )


init_db()


# ---------------- SECURITY ----------------

def admin_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return function(*args, **kwargs)
    return wrapper


def get_guest(token):
    with connect_db() as con:
        return con.execute(
            "SELECT * FROM guests WHERE token=?",
            (token,)
        ).fetchone()


def create_qr(data):
    import qrcode

    image = qrcode.make(data)
    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)
    return output


# ---------------- DESIGN ----------------

STYLE = """
:root {
    --gold:#b18a50;
    --gold-light:#e5d0a8;
    --cream:#fbf7ef;
    --white:#fffdfa;
    --ink:#554231;
    --rose:#f2e5df;
}

* {
    box-sizing:border-box;
}

html {
    scroll-behavior:smooth;
}

body {
    margin:0;
    background:var(--cream);
    color:var(--ink);
    font-family:Tahoma,Arial,sans-serif;
    line-height:1.9;
}

a {
    color:inherit;
}

button,input,select,textarea {
    font:inherit;
}

.topline {
    height:5px;
    background:linear-gradient(
        90deg,#947044,#f0dfba,#947044
    );
}

nav {
    position:sticky;
    top:0;
    z-index:20;
    display:flex;
    justify-content:center;
    flex-wrap:wrap;
    gap:17px;
    padding:12px;
    background:#fffaf2ed;
    backdrop-filter:blur(12px);
    border-bottom:1px solid #e8d9c2;
}

nav a {
    text-decoration:none;
    color:#795d3a;
    font-size:13px;
}

.hero {
    min-height:88vh;
    display:grid;
    place-items:center;
    text-align:center;
    padding:35px 15px;
    background:
        radial-gradient(circle at 50% 35%,#fffdf8,#f1e3d2);
    position:relative;
    overflow:hidden;
}

.hero-card {
    width:100%;
    max-width:760px;
    padding:42px 20px;
    background:#fffaf0e8;
    border:1px solid #d5b987;
    outline:1px solid #e5d5b7;
    outline-offset:8px;
    box-shadow:0 25px 70px #76562c20;
}

.monogram {
    font-family:Georgia,serif;
    color:var(--gold);
    font-size:52px;
    letter-spacing:8px;
}

h1 {
    font-family:Georgia,serif;
    color:#9c7441;
    font-size:clamp(42px,8vw,75px);
    font-weight:normal;
    line-height:1.3;
    margin:8px;
}

h2 {
    color:#9c7441;
    font-family:Georgia,serif;
    font-weight:normal;
    font-size:30px;
}

h3 {
    color:#a17b47;
    font-weight:500;
}

.eyebrow {
    color:#987342;
    letter-spacing:3px;
    font-size:12px;
}

.goldline {
    width:80px;
    height:1px;
    background:#c7a36b;
    margin:18px auto;
}

.btn,button {
    display:inline-block;
    background:linear-gradient(120deg,#98703c,#c9a66c);
    color:white;
    border:0;
    border-radius:30px;
    padding:11px 23px;
    text-decoration:none;
    cursor:pointer;
    box-shadow:0 8px 20px #8e673722;
}

.btn.light {
    background:#fffaf2;
    color:#795a34;
    border:1px solid #d8c39e;
    box-shadow:none;
}

section {
    max-width:1050px;
    margin:32px auto;
    padding:30px 20px;
    text-align:center;
}

.panel {
    background:var(--white);
    border:1px solid #e7d8bf;
    border-radius:22px;
    padding:28px;
    box-shadow:0 12px 38px #795c3210;
}

.grid {
    display:grid;
    grid-template-columns:repeat(
        auto-fit,minmax(210px,1fr)
    );
    gap:15px;
}

.tile {
    background:#fffaf3;
    border:1px solid #eadcc6;
    border-radius:16px;
    padding:18px;
}

.countdown {
    display:flex;
    justify-content:center;
    flex-wrap:wrap;
    gap:10px;
    margin:22px;
}

.time {
    min-width:78px;
    padding:12px;
    border:1px solid #e5d3b3;
    border-radius:14px;
    background:#fffaf2;
    color:#8d683b;
}

.time b {
    display:block;
    font:26px Georgia,serif;
}

.gallery {
    display:grid;
    grid-template-columns:repeat(3,1fr);
    gap:12px;
}

.gallery img,.gallery video {
    width:100%;
    height:230px;
    object-fit:cover;
    border-radius:15px;
    border:4px solid white;
    box-shadow:0 8px 22px #62482118;
}

form {
    max-width:520px;
    margin:auto;
    text-align:right;
}

input,select,textarea {
    width:100%;
    padding:12px;
    margin:7px 0 13px;
    border:1px solid #dfcfb4;
    border-radius:10px;
    background:#fffefa;
    color:var(--ink);
}

textarea {
    min-height:110px;
}

.note {
    font-size:12px;
    color:#8b7a65;
}

footer {
    text-align:center;
    padding:40px 15px;
    background:#efe3d2;
    color:#82653e;
}

.flower {
    position:fixed;
    top:-30px;
    z-index:30;
    color:#c9a978;
    opacity:.55;
    pointer-events:none;
    animation:fall linear infinite;
}

@keyframes fall {
    to {
        transform:translateY(110vh) rotate(360deg);
    }
}

/* 3D invitation envelope */

#intro {
    position:fixed;
    inset:0;
    z-index:100;
    background:linear-gradient(140deg,#f7eee1,#e8d4b8);
    display:grid;
    place-items:center;
    transition:opacity 1s;
}

#intro.hidden {
    opacity:0;
    pointer-events:none;
}

.envelope {
    position:relative;
    width:min(330px,85vw);
    height:210px;
    background:#e9d8bd;
    border:1px solid #b9945e;
    box-shadow:0 25px 60px #5b41252b;
    perspective:800px;
}

.envelope:before {
    content:"";
    position:absolute;
    inset:0;
    background:linear-gradient(140deg,#f9eedc,#dfc7a2);
    clip-path:polygon(0 0,50% 55%,100% 0);
    transform-origin:top;
    transition:transform 1s;
    z-index:3;
}

.envelope.open:before {
    transform:rotateX(180deg);
}

.seal {
    position:absolute;
    z-index:4;
    top:80px;
    left:50%;
    transform:translateX(-50%);
    width:65px;
    height:65px;
    display:grid;
    place-items:center;
    border-radius:50%;
    color:#fff0d4;
    background:radial-gradient(circle,#c99b58,#865b30);
    border:3px solid #e2c48d;
    font-family:Georgia,serif;
    font-size:19px;
}

.envelope-button {
    margin-top:35px;
}

/* admin */

.admin {
    max-width:1150px;
    margin:25px auto;
    padding:15px;
}

.admin table {
    width:100%;
    border-collapse:collapse;
    background:white;
    font-size:13px;
}

.admin th,.admin td {
    border:1px solid #eadcc6;
    padding:9px;
    text-align:center;
}

.admin th {
    background:#f4ead9;
}

@media(max-width:650px) {
    .gallery {
        grid-template-columns:repeat(2,1fr);
    }

    .gallery img,.gallery video {
        height:150px;
    }

    section {
        padding:20px 12px;
    }

    .hero-card {
        padding:30px 14px;
    }

    nav {
        gap:10px;
    }

    nav a {
        font-size:11px;
    }
}
"""


# ---------------- MAIN PAGE ----------------

PAGE = r"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#fbf7ef">
<title>عروسی امیر و زهرا</title>
<style>""" + STYLE + r"""</style>
</head>

<body>

<div id="intro">
    <div style="text-align:center">
        <div class="eyebrow">A SPECIAL INVITATION</div>
        <div class="envelope" id="envelope">
            <div class="seal">A & Z</div>
        </div>
        <button class="envelope-button" onclick="openEnvelope()">
            باز کردن دعوت‌نامه
        </button>
    </div>
</div>

<div class="topline"></div>

<nav>
<a href="#home" data-fa="خانه" data-en="Home">خانه</a>
<a href="#story" data-fa="داستان ما" data-en="Our Story">داستان ما</a>
<a href="#details" data-fa="مراسم" data-en="Details">مراسم</a>
<a href="#gallery" data-fa="گالری" data-en="Gallery">گالری</a>
<a href="#rsvp" data-fa="پاسخ دعوت" data-en="RSVP">پاسخ دعوت</a>
<a href="#guestbook" data-fa="یادبود" data-en="Guestbook">یادبود</a>
<button class="btn light" onclick="toggleLang()">EN / فا</button>
</nav>

<header class="hero" id="home">
<div class="hero-card">
<div class="eyebrow">A CELEBRATION OF LOVE</div>
<div class="monogram">A <span style="font-size:24px">&</span> Z</div>
<h1>امیر و زهرا</h1>
<div class="goldline"></div>

<p class="sub"
data-fa="با کمال افتخار از شما دعوت می‌کنیم در جشن پیوند و آغاز زندگی مشترک امیر و زهرا، در کنار ما باشید."
data-en="With great joy, we invite you to celebrate the beginning of Amir and Zahra's life together.">
با کمال افتخار از شما دعوت می‌کنیم در جشن پیوند و آغاز زندگی مشترک امیر و زهرا، در کنار ما باشید.
</p>

<p>چهارشنبه، ۲ دی ۱۴۰۵</p>
<p>ساعت ۱۹:۰۰ تا ۲۲:۰۰</p>

<a class="btn" href="#details">مشاهده دعوت‌نامه</a>
</div>
</header>

<section id="story">
<div class="panel">
<div class="eyebrow">OUR STORY</div>
<h2>آغاز یک داستان زیبا</h2>
<div class="goldline"></div>

<p>
هر قصه زیبایی با یک لحظه ساده آغاز می‌شود؛
و امروز، با عشق و همراهی شما،
فصل تازه‌ای از داستان امیر و زهرا شروع می‌شود.
</p>

<div class="grid">
<div class="tile">
♡
<h3>آشنایی</h3>
شروع یک اتفاق قشنگ
</div>

<div class="tile">
✧
<h3>عهد عشق</h3>
انتخابی برای تمام فرداها
</div>

<div class="tile">
❀
<h3>جشن ما</h3>
خوشحالیم کنارمان هستید
</div>
</div>

<p class="note">
این متن نمونه است؛ می‌توانی بعداً داستان واقعی خودتان را جایگزین کنی.
</p>
</div>
</section>

<section id="details">
<div class="panel">
<h2>روز به‌یادماندنی ما</h2>
<div class="goldline"></div>

<div class="countdown" id="countdown"></div>

<div class="grid">
<div class="tile">
📅
<h3>تاریخ</h3>
چهارشنبه ۲ دی ۱۴۰۵
<br>
۲۳ دسامبر ۲۰۲۶
</div>

<div class="tile">
◷
<h3>ساعت</h3>
۱۹:۰۰ تا ۲۲:۰۰
</div>

<div class="tile">
♧
<h3>مکان</h3>
{{ venue }}
<br>
{{ address }}
</div>
</div>

<p style="margin-top:22px">
<a class="btn light" target="_blank"
href="https://www.google.com/maps/search/?api=1&query=تالار+پذیرایی+فریال+سمنان">
مسیریابی تالار
</a>

<a class="btn light" href="/calendar">
افزودن به تقویم
</a>
</p>
</div>
</section>

<section id="gallery">
<div class="panel">
<h2>قاب‌هایی از خاطره</h2>
<div class="goldline"></div>

<div class="gallery">
{% for i in range(1,7) %}
<a href="/static/photo{{i}}.jpg" target="_blank">
<img src="/static/photo{{i}}.jpg"
alt="عکس خاطره"
onerror="this.style.display='none'">
</a>
{% endfor %}

<video controls playsinline preload="metadata"
src="/static/wedding.mp4"></video>
</div>

<p class="note">
برای نمایش تصاویر، عکس‌ها را در پوشه static نگه دار.
</p>
</div>
</section>

<section id="rsvp">
<div class="panel">
<h2>پاسخ به دعوت</h2>
<div class="goldline"></div>

<p>حضور ارزشمندتان را به ما اطلاع دهید.</p>

<form method="post" action="/rsvp">

<label>نام و نام خانوادگی</label>
<input name="name" maxlength="100"
placeholder="نام شما" required>

<label>تعداد افراد همراه</label>
<input name="count" type="number"
min="1" max="20" value="1" required>

<label>وضعیت حضور</label>
<select name="status">
<option value="حضور دارم">با افتخار حضور دارم</option>
<option value="متأسفانه نمی‌توانم">
متأسفانه نمی‌توانم حضور داشته باشم
</option>
</select>

<button type="submit">ثبت پاسخ و دریافت دعوت‌نامه</button>
</form>
</div>
</section>

<section id="guestbook">
<div class="panel">
<h2>دفتر یادبود</h2>
<div class="goldline"></div>

<p>پیام و آرزوی زیبای خود را برای ما بنویسید.</p>

<form method="post" action="/message">
<input name="name" required maxlength="100"
placeholder="نام شما">

<textarea name="message" required maxlength="500"
placeholder="پیام شما..."></textarea>

<button type="submit">ثبت پیام</button>
</form>

{% for m in messages %}
<div class="tile" style="margin:10px auto;max-width:600px;text-align:right">
<b>{{ m.name }}</b>
<p>{{ m.message }}</p>
</div>
{% endfor %}
</div>
</section>

<section>
<div class="panel">
<h2>با مهر، امیر و زهرا</h2>
<p>از اینکه در شادی ما شریک هستید سپاسگزاریم.</p>

<button class="btn light" onclick="shareSite()">
اشتراک‌گذاری دعوت‌نامه
</button>

<p style="margin-top:15px">
<a href="/thanks">صفحه سپاسگزاری</a>
</p>
</div>
</section>

<footer>
Made with love · A & Z · 2026
</footer>

<audio id="music" src="/static/music.mp3" loop preload="none"></audio>

<button id="musicBtn"
style="position:fixed;bottom:18px;left:18px;z-index:40;border-radius:50%;width:52px;height:52px;padding:0"
onclick="toggleMusic()">
♫
</button>

<script>
const target = new Date(
    "2026-12-23T19:00:00+03:30"
).getTime();

function tick() {
    let d = target - Date.now();

    if (d < 0) {
        document.getElementById("countdown").innerHTML =
            "<b>روز جشن فرا رسیده است!</b>";
        return;
    }

    let values = [
        Math.floor(d / 86400000),
        Math.floor(d % 86400000 / 3600000),
        Math.floor(d % 3600000 / 60000),
        Math.floor(d % 60000 / 1000)
    ];

    let labels = ["روز", "ساعت", "دقیقه", "ثانیه"];

    document.getElementById("countdown").innerHTML =
        values.map((v, i) =>
            `<div class="time"><b>${v}</b>${labels[i]}</div>`
        ).join("");
}

tick();
setInterval(tick, 1000);

function openEnvelope() {
    document.getElementById("envelope").classList.add("open");

    setTimeout(() => {
        document.getElementById("intro").classList.add("hidden");
    }, 1000);
}

function toggleMusic() {
    const audio = document.getElementById("music");

    if (audio.paused) {
        audio.play().catch(() => {
            alert("برای پخش موسیقی دوباره دکمه را بزنید.");
        });
    } else {
        audio.pause();
    }
}

async function shareSite() {
    if (navigator.share) {
        try {
            await navigator.share({
                title: "دعوت‌نامه عروسی امیر و زهرا",
                url: location.href
            });
        } catch (e) {}
    } else {
        try {
            await navigator.clipboard.writeText(location.href);
            alert("لینک دعوت‌نامه کپی شد.");
        } catch (e) {
            alert(location.href);
        }
    }
}

let english = false;

function toggleLang() {
    english = !english;

    document.documentElement.lang = english ? "en" : "fa";
    document.documentElement.dir = english ? "ltr" : "rtl";

    document.querySelectorAll("[data-fa]").forEach(el => {
        el.textContent = english ? el.dataset.en : el.dataset.fa;
    });
}

for (let i = 0; i < 12; i++) {
    let f = document.createElement("span");

    f.className = "flower";
    f.textContent = "✿";
    f.style.left = Math.random() * 100 + "%";
    f.style.animationDuration = (7 + Math.random() * 8) + "s";
    f.style.animationDelay = Math.random() * 8 + "s";

    document.body.appendChild(f);
}
</script>

</body>
</html>
"""


# ---------------- INVITATION PAGE ----------------

INVITE_PAGE = r"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>دعوت‌نامه اختصاصی</title>
<style>""" + STYLE + r"""</style>
</head>
<body>
<div class="topline"></div>

<section>
<div class="panel">

<div class="monogram">A & Z</div>
<h1 style="font-size:48px">امیر و زهرا</h1>
<div class="goldline"></div>

<h2>دعوت‌نامه اختصاصی</h2>

<p>مهمان گرامی: <b>{{ guest.name }}</b></p>
<p>تعداد ثبت‌شده: {{ guest.count }} نفر</p>
<p>وضعیت: {{ guest.status }}</p>

<p>چهارشنبه ۲ دی ۱۴۰۵</p>
<p>ساعت ۱۹ تا ۲۲</p>

<p>{{ venue }}</p>
<p>{{ address }}</p>

<img src="{{ url_for('guest_qr', token=guest.token) }}"
alt="QR اختصاصی"
style="width:190px;max-width:80%;margin:15px auto">

<p class="note">
این QR کد اختصاصی دعوت‌نامه شماست.
</p>

<a class="btn light" href="/">صفحه اصلی</a>

</div>
</section>
</body>
</html>
"""


# ---------------- ADMIN PAGE ----------------

LOGIN_PAGE = r"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ورود مدیریت</title>
<style>""" + STYLE + r"""</style>
</head>
<body>
<section>
<div class="panel">
<h2>ورود به پنل مدیریت</h2>

<form method="post">
<label>رمز مدیریت</label>
<input type="password" name="password" required>
<button type="submit">ورود</button>
</form>

</div>
</section>
</body>
</html>
"""


ADMIN_PAGE = r"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>مدیریت عروسی امیر و زهرا</title>
<style>""" + STYLE + r"""</style>
</head>

<body>
<div class="admin">

<h1 style="font-size:38px">پنل مدیریت A & Z</h1>

<p>
<a class="btn light" href="{{ url_for('export_csv') }}">
دانلود CSV مهمان‌ها
</a>

<a class="btn light" href="{{ url_for('logout') }}">
خروج
</a>
</p>

<div class="grid">

<div class="tile">
<h3>تعداد دعوت‌نامه‌ها</h3>
<b>{{ stats.total }}</b>
</div>

<div class="tile">
<h3>مجموع نفرات</h3>
<b>{{ stats.people }}</b>
</div>

<div class="tile">
<h3>حضور تأییدشده</h3>
<b>{{ stats.yes }}</b>
</div>

<div class="tile">
<h3>ورود ثبت‌شده</h3>
<b>{{ stats.checked }}</b>
</div>

</div>

<h2 style="margin-top:28px">فهرست مهمان‌ها</h2>

<div style="overflow-x:auto">

<table>
<tr>
<th>نام</th>
<th>تعداد</th>
<th>وضعیت</th>
<th>میز</th>
<th>صندلی</th>
<th>ورود</th>
<th>دعوت‌نامه</th>
<th>عملیات</th>
</tr>

{% for g in guests %}
<tr>

<td>{{ g.name }}</td>
<td>{{ g.count }}</td>
<td>{{ g.status }}</td>

<td colspan="2">
<form method="post"
action="{{ url_for('update_seat', guest_id=g.id) }}"
style="display:flex;gap:4px">

<input name="table_no"
value="{{ g.table_no or '' }}"
placeholder="میز"
style="margin:0;padding:5px">

<input name="seat_no"
value="{{ g.seat_no or '' }}"
placeholder="صندلی"
style="margin:0;padding:5px">

<button type="submit" style="padding:5px">
ذخیره
</button>

</form>
</td>

<td>
{{ "ثبت شده" if g.checked_in else "ثبت نشده" }}
</td>

<td>
<a target="_blank"
href="{{ url_for('invite', token=g.token) }}">
دعوت‌نامه
</a>
<br>
<a target="_blank"
href="{{ url_for('guest_qr', token=g.token) }}">
QR
</a>
</td>

<td>
<form method="post"
action="{{ url_for('checkin', token=g.token) }}">

<button type="submit" style="padding:5px">
{{ "لغو ورود" if g.checked_in else "ثبت ورود" }}
</button>

</form>
</td>

</tr>
{% endfor %}

</table>
</div>

<h2 style="margin-top:28px">پیام‌های دفتر یادبود</h2>

{% for m in messages %}
<div class="tile" style="margin:8px 0;text-align:right">
<b>{{ m.name }}</b>
<p>{{ m.message }}</p>
</div>
{% endfor %}

</div>
</body>
</html>
"""


THANKS_PAGE = r"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>سپاسگزاریم</title>
<style>""" + STYLE + r"""</style>
</head>
<body>

<section style="margin-top:10vh">
<div class="panel">

<div class="monogram">A & Z</div>
<h1>سپاسگزاریم</h1>
<h2>برای همراهی و عشق شما</h2>

<p>حضور و مهرتان زیباترین یادگار جشن ماست.</p>

<a class="btn" href="/">بازگشت به دعوت‌نامه</a>

</div>
</section>

</body>
</html>
"""


# ---------------- WEBSITE ROUTES ----------------

@app.route("/")
def home():
    with connect_db() as con:
        messages = con.execute(
            "SELECT name,message FROM messages ORDER BY id DESC LIMIT 20"
        ).fetchall()

    return render_template_string(
        PAGE,
        venue=VENUE,
        address=ADDRESS,
        messages=messages
    )


@app.route("/rsvp", methods=["POST"])
def rsvp():

    name = request.form.get("name", "").strip()[:100]
    status = request.form.get("status", "حضور دارم")[:50]

    try:
        count = max(
            1,
            min(20, int(request.form.get("count", 1)))
        )
    except (ValueError, TypeError):
        count = 1

    if not name:
        abort(400)

    token = secrets.token_urlsafe(20)

    with connect_db() as con:
        con.execute("""
            INSERT INTO guests
            (name,count,status,created,token)
            VALUES(?,?,?,?,?)
        """, (
            name,
            count,
            status,
            datetime.now().isoformat(timespec="seconds"),
            token
        ))

    return redirect(url_for("invite", token=token))


@app.route("/invite/<token>")
def invite(token):

    guest = get_guest(token)

    if not guest:
        abort(404)

    return render_template_string(
        INVITE_PAGE,
        guest=guest,
        venue=VENUE,
        address=ADDRESS
    )


@app.route("/guest-qr/<token>.png")
def guest_qr(token):

    guest = get_guest(token)

    if not guest:
        abort(404)

    invitation_url = (
        request.url_root.rstrip("/")
        + url_for("invite", token=token)
    )

    qr = create_qr(invitation_url)

    return Response(
        qr.getvalue(),
        mimetype="image/png"
    )


@app.route("/message", methods=["POST"])
def message():

    name = request.form.get("name", "").strip()[:100]
    msg = request.form.get("message", "").strip()[:500]

    if name and msg:
        with connect_db() as con:
            con.execute("""
                INSERT INTO messages(name,message,created)
                VALUES(?,?,?)
            """, (
                name,
                msg,
                datetime.now().isoformat(timespec="seconds")
            ))

    return redirect(url_for("home") + "#guestbook")


@app.route("/calendar")
def calendar():

    content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Amir and Zahra//Wedding//FA
CALSCALE:GREGORIAN
BEGIN:VEVENT
DTSTART:20261223T153000Z
DTEND:20261223T183000Z
SUMMARY:Wedding of Amir and Zahra
LOCATION:Talare Ferial, Semnan, Iran
DESCRIPTION:Amir and Zahra wedding celebration
END:VEVENT
END:VCALENDAR"""

    return Response(
        content,
        mimetype="text/calendar",
        headers={
            "Content-Disposition":
            "attachment; filename=amir-zahra-wedding.ics"
        }
    )


@app.route("/thanks")
def thanks():
    return render_template_string(THANKS_PAGE)


# ---------------- ADMIN ROUTES ----------------

@app.route("/admin", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":

        supplied = request.form.get("password", "")

        if secrets.compare_digest(supplied, ADMIN_PASSWORD):
            session["admin"] = True
            session.permanent = True
            return redirect(url_for("admin_panel"))

    return render_template_string(LOGIN_PAGE)


@app.route("/admin/panel")
@admin_required
def admin_panel():

    with connect_db() as con:

        guests = con.execute(
            "SELECT * FROM guests ORDER BY id DESC"
        ).fetchall()

        messages = con.execute(
            "SELECT * FROM messages ORDER BY id DESC LIMIT 50"
        ).fetchall()

        stats = con.execute("""
            SELECT
                COUNT(*) AS total,
                COALESCE(SUM(count),0) AS people,
                COALESCE(SUM(
                    CASE WHEN status='حضور دارم'
                    THEN count ELSE 0 END
                ),0) AS yes,
                COALESCE(SUM(
                    CASE WHEN checked_in=1
                    THEN count ELSE 0 END
                ),0) AS checked
            FROM guests
        """).fetchone()

    return render_template_string(
        ADMIN_PAGE,
        guests=guests,
        messages=messages,
        stats=stats
    )


@app.route("/admin/guest/<int:guest_id>/seat", methods=["POST"])
@admin_required
def update_seat(guest_id):

    table_no = request.form.get("table_no", "").strip()[:30]
    seat_no = request.form.get("seat_no", "").strip()[:30]

    with connect_db() as con:
        con.execute("""
            UPDATE guests
            SET table_no=?, seat_no=?
            WHERE id=?
        """, (table_no, seat_no, guest_id))

    return redirect(url_for("admin_panel"))


@app.route("/admin/checkin/<token>", methods=["POST"])
@admin_required
def checkin(token):

    with connect_db() as con:

        guest = con.execute(
            "SELECT checked_in FROM guests WHERE token=?",
            (token,)
        ).fetchone()

        if guest:
            new_value = 0 if guest["checked_in"] else 1

            con.execute(
                "UPDATE guests SET checked_in=? WHERE token=?",
                (new_value, token)
            )

    return redirect(url_for("admin_panel"))


@app.route("/admin/export")
@admin_required
def export_csv():

    with connect_db() as con:
        rows = con.execute("""
            SELECT
                name,count,status,table_no,seat_no,
                checked_in,created
            FROM guests
            ORDER BY id
        """).fetchall()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "نام",
        "تعداد",
        "وضعیت",
        "میز",
        "صندلی",
        "ورود",
        "تاریخ ثبت"
    ])

    for row in rows:
        writer.writerow(list(row))

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition":
            "attachment; filename=amir-zahra-guests.csv"
        }
    )


@app.route("/admin/logout")
def logout():

    session.clear()

    return redirect(url_for("admin_login"))


# ---------------- START APP ----------------

@app.errorhandler(404)
def not_found(error):
    return "صفحه موردنظر پیدا نشد.", 404


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )
