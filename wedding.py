چ
import os
import io
import csv
import secrets
import sqlite3
from datetime import datetime
from functools import wraps

import qrcode
from flask import (
    Flask, request, redirect, url_for, session,
    flash, send_file, make_response, render_template_string
)
from werkzeug.security import check_password_hash, generate_password_hash


# =========================================================
# تنظیمات اصلی
# =========================================================

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

DATABASE = os.environ.get("DATABASE_PATH", "wedding.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "change-this-admin-password")

WEDDING_DATE = "2026-12-23T19:00:00+03:30"
WEDDING_DATE_FA = "چهارشنبه ۲ دی ۱۴۰۵"
WEDDING_TIME = "۱۹:۰۰ تا ۲۲:۰۰"
WEDDING_HALL = "تالار پذیرایی فریال"
WEDDING_ADDRESS = "استان سمنان، میدان معلم، بلوار بسیج، جنب ورزشگاه الغدیر"

INVITATION_TEXT = (
    "با کمال افتخار از شما دعوت می‌کنیم در جشن پیوند و آغاز "
    "زندگی مشترک امیر و زهرا، در کنار ما باشید."
)


# =========================================================
# پایگاه داده و مهاجرت ستون‌ها
# =========================================================

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            count INTEGER DEFAULT 1,
            attendance TEXT DEFAULT 'yes',
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT
        )
    """)

    # افزودن ستون‌های جدید بدون حذف اطلاعات قبلی
    existing = {
        row["name"]
        for row in cur.execute("PRAGMA table_info(guests)").fetchall()
    }

    migrations = {
        "token": "TEXT",
        "table_no": "TEXT",
        "seat_no": "TEXT",
        "checked_in": "INTEGER DEFAULT 0"
    }

    for column, definition in migrations.items():
        if column not in existing:
            cur.execute(
                f"ALTER TABLE guests ADD COLUMN {column} {definition}"
            )

    cur.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_guests_token
        ON guests(token)
    """)

    # برای مهمان‌های قدیمی که توکن ندارند
    rows = cur.execute("""
        SELECT id FROM guests
        WHERE token IS NULL OR token = ''
    """).fetchall()

    for row in rows:
        cur.execute(
            "UPDATE guests SET token = ? WHERE id = ?",
            (secrets.token_urlsafe(18), row["id"])
        )

    conn.commit()
    conn.close()


init_db()


# =========================================================
# ابزارهای عمومی
# =========================================================

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin"))
        return func(*args, **kwargs)
    return wrapper


def get_guest_by_token(token):
    conn = get_db()
    guest = conn.execute(
        "SELECT * FROM guests WHERE token = ?",
        (token,)
    ).fetchone()
    conn.close()
    return guest


def base_url():
    return request.url_root.rstrip("/")


# =========================================================
# قالب اصلی سایت
# =========================================================

PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#f6a6b8">
<title>عروسی امیر و زهرا 💗</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800;900&display=swap" rel="stylesheet">

<style>
:root {
    --pink: #ff7fa5;
    --rose: #ffb0c5;
    --peach: #ffc49f;
    --purple: #b9a2f5;
    --cyan: #8ce2df;
    --gold: #f4c66b;
    --ink: #543b5d;
    --white: #fffaff;
    --shadow: 0 15px 45px rgba(132, 83, 139, .14);
}

* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

html { scroll-behavior: smooth; }

body {
    font-family: "Vazirmatn", sans-serif;
    color: var(--ink);
    background:
        radial-gradient(circle at 8% 12%, #ffe0eb 0, transparent 25%),
        radial-gradient(circle at 90% 28%, #e7dcff 0, transparent 25%),
        radial-gradient(circle at 15% 80%, #d8f7f2 0, transparent 28%),
        linear-gradient(135deg, #fff9fc, #fff7ef 55%, #f8f3ff);
    overflow-x: hidden;
}

a { color: inherit; text-decoration: none; }

button, input, textarea, select {
    font-family: inherit;
}

button, .btn {
    border: none;
    cursor: pointer;
}

.container {
    width: min(1100px, 92%);
    margin: auto;
}

nav {
    position: sticky;
    top: 10px;
    z-index: 50;
    width: min(1050px, 94%);
    margin: 12px auto;
    padding: 12px 18px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    flex-wrap: wrap;
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(255,255,255,.9);
    border-radius: 22px;
    backdrop-filter: blur(16px);
    box-shadow: var(--shadow);
}

.logo {
    font-weight: 900;
    color: #d75d91;
    font-size: 19px;
}

.navlinks {
    display: flex;
    gap: 16px;
    flex-wrap: wrap;
    font-size: 13px;
    font-weight: 700;
}

.navlinks a:hover { color: #e65e9b; }

.hero {
    min-height: 690px;
    display: flex;
    justify-content: center;
    align-items: center;
    text-align: center;
    position: relative;
    padding: 70px 15px;
    overflow: hidden;
}

.hero::before, .hero::after {
    content: "✦";
    position: absolute;
    color: #e9b85c;
    font-size: 42px;
    animation: twinkle 2.5s infinite alternate;
}

.hero::before { top: 18%; right: 12%; }
.hero::after { bottom: 17%; left: 13%; animation-delay: 1s; }

.hero-content {
    max-width: 850px;
    position: relative;
    z-index: 2;
    animation: appear 1.2s ease both;
}

.eyebrow {
    display: inline-block;
    padding: 9px 19px;
    border-radius: 50px;
    background: #fff;
    color: #d65d91;
    box-shadow: var(--shadow);
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 24px;
}

.hero h1 {
    font-size: clamp(43px, 9vw, 88px);
    line-height: 1.5;
    font-weight: 900;
    background: linear-gradient(100deg, #e45e91, #aa7de0, #efaa79);
    -webkit-background-clip: text;
    color: transparent;
    filter: drop-shadow(0 8px 15px rgba(225,100,150,.12));
}

.hero h2 {
    font-size: clamp(18px, 3vw, 25px);
    color: #86628d;
    margin: 8px 0 20px;
}

.hero p {
    max-width: 650px;
    margin: 0 auto 25px;
    line-height: 2.2;
    font-size: 16px;
}

.heart {
    display: inline-block;
    color: #f16e9d;
    animation: heartbeat 1.5s infinite;
}

.btn {
    display: inline-block;
    padding: 13px 25px;
    border-radius: 50px;
    background: linear-gradient(110deg, #f17ca8, #b18ae7);
    color: white;
    font-weight: 800;
    box-shadow: 0 10px 24px rgba(213, 104, 160, .25);
    transition: .3s;
}

.btn:hover {
    transform: translateY(-4px) scale(1.03);
    box-shadow: 0 15px 30px rgba(213, 104, 160, .35);
}

.btn.secondary {
    background: linear-gradient(110deg, #73d6ce, #87b9f0);
}

.section {
    padding: 75px 0;
}

.section-title {
    text-align: center;
    font-size: clamp(26px, 5vw, 39px);
    font-weight: 900;
    color: #b35e9c;
    margin-bottom: 12px;
}

.section-subtitle {
    text-align: center;
    color: #987e9e;
    margin-bottom: 35px;
    font-size: 14px;
}

.card {
    background: rgba(255,255,255,.78);
    border: 1px solid rgba(255,255,255,.95);
    border-radius: 27px;
    padding: 27px;
    box-shadow: var(--shadow);
    transition: transform .35s, box-shadow .35s;
}

.card:hover {
    transform: translateY(-7px);
    box-shadow: 0 22px 55px rgba(132,83,139,.2);
}

.countdown {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 13px;
    max-width: 700px;
    margin: 25px auto 0;
}

.time-box {
    padding: 20px 8px;
    border-radius: 22px;
    background: linear-gradient(145deg, #fff, #ffe7f0);
    box-shadow: var(--shadow);
}

.time-box strong {
    display: block;
    color: #d95e96;
    font-size: clamp(25px, 5vw, 40px);
    font-weight: 900;
}

.time-box span {
    font-size: 13px;
    color: #957b9d;
}

.info-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 18px;
}

.info-icon {
    font-size: 38px;
    margin-bottom: 12px;
}

.info-card h3 { color: #c15f99; margin-bottom: 9px; }
.info-card p { line-height: 2; font-size: 14px; }

.invitation {
    max-width: 760px;
    margin: auto;
    text-align: center;
    position: relative;
    overflow: hidden;
}

.invitation::before {
    content: "❀";
    position: absolute;
    top: -20px;
    right: 20px;
    font-size: 75px;
    color: #f7c4d5;
    opacity: .45;
}

.invitation p {
    line-height: 2.5;
    font-size: 17px;
    position: relative;
}

.names {
    font-size: 33px;
    color: #d45e98;
    font-weight: 900;
    margin: 18px 0;
}

.gallery {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
}

.gallery img {
    width: 100%;
    height: 250px;
    object-fit: cover;
    border-radius: 23px;
    box-shadow: var(--shadow);
    transition: .4s;
}

.gallery img:hover {
    transform: scale(1.035) rotate(-1deg);
}

.form-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.field { margin-bottom: 15px; }

.field label {
    display: block;
    font-size: 14px;
    font-weight: 700;
    margin-bottom: 8px;
}

.field input, .field textarea, .field select {
    width: 100%;
    border: 1px solid #f0d6e6;
    background: #fffaff;
    border-radius: 14px;
    padding: 13px 14px;
    color: var(--ink);
    outline: none;
    transition: .2s;
}

.field input:focus, .field textarea:focus, .field select:focus {
    border-color: #dc80b0;
    box-shadow: 0 0 0 4px rgba(220,128,176,.12);
}

.field textarea {
    min-height: 110px;
    resize: vertical;
}

.full { grid-column: 1 / -1; }

.message-list {
    display: grid;
    gap: 13px;
    margin-top: 25px;
}

.message-item {
    padding: 18px;
    border-radius: 18px;
    background: #fff7fb;
    border-right: 4px solid #e99abb;
}

.message-item p { line-height: 2; }
.message-item strong { color: #c45f97; }

video {
    width: 100%;
    max-height: 500px;
    border-radius: 25px;
    box-shadow: var(--shadow);
    background: #f6e9f0;
}

footer {
    padding: 45px 15px;
    text-align: center;
    background: linear-gradient(110deg, #f9d9e6, #e7ddff, #d9f6f0);
    color: #795c82;
    line-height: 2.3;
}

.petal {
    position: fixed;
    top: -40px;
    z-index: 100;
    pointer-events: none;
    color: #f08eb5;
    opacity: .55;
    animation: fall linear infinite;
}

.reveal {
    opacity: 0;
    transform: translateY(28px);
    transition: opacity .8s, transform .8s;
}

.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}

@keyframes fall {
    to { transform: translateY(110vh) rotate(480deg); }
}
@keyframes heartbeat {
    0%,100% { transform: scale(1); }
    50% { transform: scale(1.2); }
}
@keyframes twinkle {
    from { opacity: .3; transform: scale(.8) rotate(0); }
    to { opacity: 1; transform: scale(1.2) rotate(25deg); }
}
@keyframes appear {
    from { opacity: 0; transform: translateY(25px); }
    to { opacity: 1; transform: translateY(0); }
}

@media(max-width:750px) {
    .info-grid { grid-template-columns: 1fr; }
    .gallery { grid-template-columns: repeat(2, 1fr); }
    .gallery img { height: 180px; }
    .form-grid { grid-template-columns: 1fr; }
    .countdown { gap: 7px; }
    .time-box { padding: 15px 4px; }
    nav { justify-content: center; }
    .navlinks { justify-content: center; }
    .hero { min-height: 600px; }
}

@media(max-width:400px) {
    .gallery { grid-template-columns: 1fr; }
}
</style>
</head>

<body>

<nav>
    <div class="logo">💗 امیر و زهرا</div>
    <div class="navlinks">
        <a href="#home">خانه</a>
        <a href="#invitation">دعوت‌نامه</a>
        <a href="#details">جزئیات جشن</a>
        <a href="#gallery">گالری</a>
        <a href="#rsvp">اعلام حضور</a>
        <a href="#messages">دفتر یادبود</a>
    </div>
</nav>

<header class="hero" id="home">
    <div class="hero-content">
        <div class="eyebrow">یک روز زیبا، یک شروع عاشقانه ✨</div>
        <h1>امیر <span class="heart">♥</span> زهرا</h1>
        <h2>آغاز قصه‌ای به زیبایی عشق</h2>
        <p>{{ invitation_text }}</p>
        <div style="margin-bottom:25px;font-weight:800;color:#a46c9d">
            {{ wedding_date }} | ساعت {{ wedding_time }}
        </div>
        <a class="btn" href="#invitation">دیدن دعوت‌نامه 💌</a>
    </div>
</header>

<section class="section reveal" id="invitation">
    <div class="container">
        <h2 class="section-title">دعوت‌نامه‌ای از جنس عشق 💌</h2>
        <p class="section-subtitle">حضور شما زیباترین هدیه برای ماست</p>
        <div class="card invitation">
            <div style="font-size:45px">🌸 💍 🌸</div>
            <div class="names">امیر و زهرا</div>
            <p>{{ invitation_text }}</p>
            <p style="margin-top:20px;color:#b66a9c;font-weight:800">
                منتظر دیدار گرم شما هستیم.
            </p>
            <div style="font-size:30px;margin-top:15px">🕊️ ✨ 🕊️</div>
        </div>
    </div>
</section>

<section class="section reveal" id="countdown">
    <div class="container">
        <h2 class="section-title">تا شروع جشن ما 💖</h2>
        <p class="section-subtitle">لحظه‌شماری برای یک شب فراموش‌نشدنی</p>
        <div class="countdown">
            <div class="time-box"><strong id="days">--</strong><span>روز</span></div>
            <div class="time-box"><strong id="hours">--</strong><span>ساعت</span></div>
            <div class="time-box"><strong id="minutes">--</strong><span>دقیقه</span></div>
            <div class="time-box"><strong id="seconds">--</strong><span>ثانیه</span></div>
        </div>
        <p id="countdown-message" style="text-align:center;margin-top:20px;color:#b45d96;font-weight:800"></p>
    </div>
</section>

<section class="section reveal" id="details">
    <div class="container">
        <h2 class="section-title">اطلاعات جشن</h2>
        <p class="section-subtitle">برای اینکه در کنار هم خاطره بسازیم</p>
        <div class="info-grid">
            <div class="card info-card" style="text-align:center">
                <div class="info-icon">📅</div>
                <h3>تاریخ جشن</h3>
                <p>{{ wedding_date }}</p>
                <p>۲۳ دسامبر ۲۰۲۶</p>
            </div>
            <div class="card info-card" style="text-align:center">
                <div class="info-icon">🕖</div>
                <h3>زمان جشن</h3>
                <p>{{ wedding_time }}</p>
            </div>
            <div class="card info-card" style="text-align:center">
                <div class="info-icon">📍</div>
                <h3>مکان جشن</h3>
                <p>{{ wedding_hall }}</p>
                <p>{{ wedding_address }}</p>
            </div>
        </div>
        <div style="text-align:center;margin-top:25px">
            <a class="btn secondary" href="{{ url_for('calendar') }}">افزودن به تقویم 📆</a>
        </div>
    </div>
</section>

<section class="section reveal" id="gallery">
    <div class="container">
        <h2 class="section-title">گالری خاطرات 🌷</h2>
        <p class="section-subtitle">چند قاب زیبا برای یک قصه زیباتر</p>
        <div class="gallery">
            {% for n in range(1,7) %}
            <img src="{{ url_for('static', filename='photo' ~ n ~ '.jpg') }}"
                 alt="عکس خاطره {{ n }}"
                 loading="lazy"
                 onerror="this.style.display='none'">
            {% endfor %}
        </div>
    </div>
</section>

<section class="section reveal" id="video">
    <div class="container">
        <h2 class="section-title">لحظه‌های ما 🎬</h2>
        <p class="section-subtitle">یک قاب کوچک از خاطرات شیرین</p>
        <div class="card">
            <video controls playsinline preload="metadata">
                <source src="{{ url_for('static', filename='wedding.mp4') }}" type="video/mp4">
                مرورگر شما از پخش ویدیو پشتیبانی نمی‌کند.
            </video>
        </div>
    </div>
</section>

<section class="section reveal" id="music">
    <div class="container">
        <div class="card" style="text-align:center;max-width:650px;margin:auto">
            <div style="font-size:38px">🎵</div>
            <h2 style="color:#bd619b;margin:10px 0">موسیقی جشن ما</h2>
            <p style="margin-bottom:18px">برای شنیدن موسیقی، دکمه پخش را بزنید.</p>
            <audio controls style="width:100%">
                <source src="{{ url_for('static', filename='music.mp3') }}" type="audio/mpeg">
                مرورگر شما از پخش موسیقی پشتیبانی نمی‌کند.
            </audio>
        </div>
    </div>
</section>

<section class="section reveal" id="rsvp">
    <div class="container">
        <h2 class="section-title">اعلام حضور شما 💌</h2>
        <p class="section-subtitle">لطفاً حضور یا عدم حضورتان را ثبت کنید</p>
        <div class="card" style="max-width:700px;margin:auto">
            <form method="POST" action="{{ url_for('rsvp') }}">
                <div class="form-grid">
                    <div class="field">
                        <label>نام و نام خانوادگی</label>
                        <input name="name" required maxlength="100" placeholder="نام شما">
                    </div>
                    <div class="field">
                        <label>شماره تماس</label>
                        <input name="phone" maxlength="30" placeholder="شماره تماس">
                    </div>
                    <div class="field">
                        <label>تعداد نفرات</label>
                        <select name="count">
                            {% for n in range(1,11) %}
                            <option value="{{ n }}">{{ n }} نفر</option>
                            {% endfor %}
                        </select>
                    </div>
                    <div class="field">
                        <label>وضعیت حضور</label>
                        <select name="attendance" required>
                            <option value="yes">با افتخار می‌آییم 💗</option>
                            <option value="no">متأسفانه امکان حضور نداریم</option>
                        </select>
                    </div>
                </div>
                <button class="btn" type="submit" style="width:100%">ثبت پاسخ من 🌸</button>
            </form>
        </div>
    </div>
</section>

<section class="section reveal" id="messages">
    <div class="container">
        <h2 class="section-title">دفتر یادبود 💝</h2>
        <p class="section-subtitle">پیام و آرزوی قشنگتان را برای ما بنویسید</p>
        <div class="card" style="max-width:700px;margin:auto">
            <form method="POST" action="{{ url_for('message') }}">
                <div class="field">
                    <label>نام شما</label>
                    <input name="name" required maxlength="100" placeholder="نام شما">
                </div>
                <div class="field">
                    <label>پیام شما</label>
                    <textarea name="message" required maxlength="1000"
                              placeholder="یک آرزوی زیبا برای امیر و زهرا..."></textarea>
                </div>
                <button class="btn secondary" type="submit" style="width:100%">ثبت پیام ✨</button>
            </form>

            <div class="message-list">
                {% for item in messages %}
                <div class="message-item">
                    <strong>{{ item.name }}</strong>
                    <p>{{ item.message }}</p>
                    <small>{{ item.created_at }}</small>
                </div>
                {% else %}
                <p style="text-align:center;color:#a88ca8">هنوز پیامی ثبت نشده است. اولین پیام را شما بنویسید 💗</p>
                {% endfor %}
            </div>
        </div>
    </div>
</section>

<footer>
    <div style="font-size:32px">💗 💍 💗</div>
    <strong>امیر و زهرا</strong>
    <p>با عشق، برای شروع یک زندگی مشترک</p>
    <p>حضور شما شادی این شب را چند برابر می‌کند.</p>
    <a href="{{ url_for('admin') }}" style="font-size:11px;opacity:.5">مدیریت</a>
</footer>

<script>
const targetDate = new Date("{{ wedding_date_iso }}").getTime();

function updateCountdown() {
    const now = Date.now();
    const distance = targetDate - now;

    if (distance <= 0) {
        ["days","hours","minutes","seconds"].forEach(
            id => document.getElementById(id).textContent = "۰"
        );
        document.getElementById("countdown-message").textContent =
            "جشن زیبای ما آغاز شده است! 💗";
        return;
    }

    const days = Math.floor(distance / 86400000);
    const hours = Math.floor((distance % 86400000) / 3600000);
    const minutes = Math.floor((distance % 3600000) / 60000);
    const seconds = Math.floor((distance % 60000) / 1000);

    document.getElementById("days").textContent = days;
    document.getElementById("hours").textContent = hours;
    document.getElementById("minutes").textContent = minutes;
    document.getElementById("seconds").textContent = seconds;
}
updateCountdown();
setInterval(updateCountdown, 1000);

// ظاهر شدن بخش‌ها هنگام اسکرول
const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
        }
    });
}, {threshold: 0.12});

document.querySelectorAll(".reveal").forEach(el => observer.observe(el));

// گلبرگ‌های شناور
const symbols = ["✿", "❀", "♥", "✧"];
for (let i = 0; i < 15; i++) {
    const petal = document.createElement("div");
    petal.className = "petal";
    petal.textContent = symbols[Math.floor(Math.random() * symbols.length)];
    petal.style.left = Math.random() * 100 + "vw";
    petal.style.fontSize = (12 + Math.random() * 17) + "px";
    petal.style.animationDuration = (9 + Math.random() * 13) + "s";
    petal.style.animationDelay = (-Math.random() * 15) + "s";
    document.body.appendChild(petal);
}
</script>
</body>
</html>
"""


# =========================================================
# صفحه دعوت اختصاصی مهمان
# =========================================================

INVITE_PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>دعوت‌نامه اختصاصی</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{
    margin:0;padding:25px;min-height:100vh;display:grid;place-items:center;
    font-family:Vazirmatn,sans-serif;color:#654765;
    background:linear-gradient(135deg,#ffe1ed,#e9ddff,#d9f7f1)
}
.card{
    width:min(600px,100%);padding:40px 25px;text-align:center;
    background:#ffffffdf;border-radius:30px;
    box-shadow:0 20px 60px #9e79a533
}
h1{font-size:42px;color:#d45e98}
p{line-height:2.3}
.name{font-size:24px;font-weight:900;color:#a16cbb}
img{max-width:180px;width:100%;margin:20px auto}
a{display:inline-block;padding:12px 22px;border-radius:30px;
background:#d875a8;color:white;text-decoration:none;font-weight:bold}
</style>
</head>
<body>
<div class="card">
    <div style="font-size:45px">💌</div>
    <h1>دعوت‌نامه اختصاصی</h1>
    <p>مهمان عزیز،</p>
    <div class="name">{{ guest.name }}</div>
    <p>با کمال افتخار از شما دعوت می‌کنیم در جشن پیوند و آغاز زندگی مشترک امیر و زهرا، در کنار ما باشید.</p>
    <p><strong>تاریخ:</strong> چهارشنبه ۲ دی ۱۴۰۵</p>
    <p><strong>ساعت:</strong> ۱۹:۰۰ تا ۲۲:۰۰</p>
    <p><strong>مکان:</strong> تالار پذیرایی فریال</p>
    <p>استان سمنان، میدان معلم، بلوار بسیج، جنب ورزشگاه الغدیر</p>
    <img src="{{ qr_url }}" alt="QR اختصاصی دعوت‌نامه">
    <p>این دعوت‌نامه مخصوص شماست.</p>
    <a href="{{ url_for('home') }}">رفتن به صفحه اصلی</a>
</div>
</body>
</html>
"""


# =========================================================
# صفحه ورود مدیریت
# =========================================================

LOGIN_PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ورود مدیریت</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap" rel="stylesheet">
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;
font-family:Vazirmatn,sans-serif;background:linear-gradient(135deg,#ffe0ec,#e8ddff,#d8f5f0);padding:20px}
.card{width:min(420px,100%);background:white;padding:35px;border-radius:25px;box-shadow:0 15px 50px #9e79a533;text-align:center}
h1{color:#c35d96}
input{width:100%;box-sizing:border-box;padding:14px;border:1px solid #eed3e3;border-radius:12px;margin:15px 0;font-family:inherit}
button{width:100%;padding:13px;border:0;border-radius:30px;background:linear-gradient(100deg,#ed80aa,#a88be6);color:white;font-family:inherit;font-weight:bold;cursor:pointer}
.error{color:#d33}
a{display:inline-block;margin-top:20px;color:#a66a9e}
</style>
</head>
<body>
<div class="card">
    <div style="font-size:45px">🔐</div>
    <h1>پنل مدیریت جشن</h1>
    {% with errors = get_flashed_messages() %}
      {% for error in errors %}<p class="error">{{ error }}</p>{% endfor %}
    {% endwith %}
    <form method="POST">
        <input type="password" name="password" placeholder="رمز عبور مدیریت" required>
        <button type="submit">ورود به پنل</button>
    </form>
    <a href="{{ url_for('home') }}">بازگشت به سایت</a>
</div>
</body>
</html>
"""


# =========================================================
# پنل مدیریت
# =========================================================

ADMIN_PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>مدیریت جشن</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{margin:0;padding:20px;font-family:Vazirmatn,sans-serif;background:#fff7fc;color:#604765}
.container{max-width:1100px;margin:auto}
h1,h2{color:#c15d98}
.card{background:white;padding:22px;border-radius:20px;box-shadow:0 10px 30px #9e79a522;margin:18px 0;overflow-x:auto}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px}
.stat{padding:18px;border-radius:16px;text-align:center;background:#fff0f6}
.stat strong{font-size:28px;color:#d65f98;display:block}
table{width:100%;border-collapse:collapse;min-width:800px}
td,th{padding:12px;border-bottom:1px solid #f0e2ec;text-align:center}
th{color:#bd6095}
input{padding:9px;border:1px solid #e8d2e2;border-radius:9px;font-family:inherit;width:85px}
button,.btn{padding:9px 13px;border:0;border-radius:10px;background:#d875a8;color:white;font-family:inherit;cursor:pointer;text-decoration:none;display:inline-block}
.btn.green{background:#6cb9a9}
.btn.gray{background:#9279bd}
small{color:#967f9c}
@media(max-width:600px){.stats{grid-template-columns:1fr}.card{padding:13px}}
</style>
</head>
<body>
<div class="container">
    <h1>🌸 پنل مدیریت جشن امیر و زهرا</h1>
    <p>مدیریت مهمان‌ها، میزها و ورود به جشن</p>

    <div class="stats">
        <div class="stat"><strong>{{ total }}</strong>کل ثبت‌نام‌ها</div>
        <div class="stat"><strong>{{ attending }}</strong>پاسخ‌های مثبت</div>
        <div class="stat"><strong>{{ people }}</strong>تعداد نفرات اعلام‌شده</div>
    </div>

    <div class="card">
        <h2>ابزارهای مدیریت</h2>
        <a class="btn green" href="{{ url_for('export') }}">دانلود فایل CSV مهمان‌ها</a>
        <a class="btn gray" href="{{ url_for('home') }}">مشاهده سایت</a>
        <a class="btn" href="{{ url_for('logout') }}">خروج از مدیریت</a>
    </div>

    <div class="card">
        <h2>فهرست مهمان‌ها</h2>
        <table>
            <thead>
                <tr>
                    <th>نام</th>
                    <th>تلفن</th>
                    <th>تعداد</th>
                    <th>حضور</th>
                    <th>میز</th>
                    <th>صندلی</th>
                    <th>ورود</th>
                    <th>دعوت‌نامه</th>
                    <th>ثبت چیدمان</th>
                </tr>
            </thead>
            <tbody>
            {% for g in guests %}
                <tr>
                    <td>{{ g.name }}</td>
                    <td>{{ g.phone or '-' }}</td>
                    <td>{{ g.count }}</td>
                    <td>{{ 'می‌آید' if g.attendance == 'yes' else 'نمی‌آید' }}</td>
                    <td>
                        <form method="POST" action="{{ url_for('seat', guest_id=g.id) }}">
                            <input name="table_no" value="{{ g.table_no or '' }}" placeholder="میز">
                    </td>
                    <td><input name="seat_no" value="{{ g.seat_no or '' }}" placeholder="صندلی"></td>
                    <td>
                        {% if g.checked_in %}
                            <span style="color:green">ثبت شده ✓</span>
                        {% else %}
                            <span style="color:#c77a42">ثبت نشده</span>
                        {% endif %}
                    </td>
                    <td><a class="btn gray" href="{{ url_for('invite', token=g.token) }}" target="_blank">مشاهده</a></td>
                    <td><button type="submit">ذخیره</button></form></td>
                </tr>
                <tr>
                    <td colspan="9">
                        <form method="POST" action="{{ url_for('checkin', token=g.token) }}">
                            <button class="btn green" type="submit">ثبت ورود {{ g.name }}</button>
                        </form>
                    </td>
                </tr>
            {% else %}
                <tr><td colspan="9">هنوز مهمانی ثبت نشده است.</td></tr>
            {% endfor %}
            </tbody>
        </table>
    </div>

    <div class="card">
        <h2>پیام‌های دفتر یادبود</h2>
        {% for m in messages %}
            <p><strong>{{ m.name }}</strong>: {{ m.message }} <small>({{ m.created_at }})</small></p>
            <hr style="border:0;border-top:1px solid #f0e2ec;margin:12px 0">
        {% else %}
            <p>هنوز پیامی وجود ندارد.</p>
        {% endfor %}
    </div>
</div>
</body>
</html>
"""


# =========================================================
# صفحه تشکر
# =========================================================

THANKS_PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>سپاس از شما</title>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;700;900&display=swap" rel="stylesheet">
<style>
body{margin:0;min-height:100vh;display:grid;place-items:center;text-align:center;padding:20px;
font-family:Vazirmatn,sans-serif;background:linear-gradient(135deg,#ffe0ed,#e8ddff,#d9f7f1);color:#654765}
.card{background:#ffffffdf;padding:40px 25px;border-radius:28px;max-width:550px;box-shadow:0 15px 50px #9e79a533}
h1{color:#d45e98;font-size:35px}
p{line-height:2.3}
a{display:inline-block;background:#d875a8;color:white;padding:12px 25px;border-radius:30px;text-decoration:none}
</style>
</head>
<body>
<div class="card">
    <div style="font-size:55px">💗</div>
    <h1>از شما سپاسگزاریم!</h1>
    <p>{{ message }}</p>
    <p>با مهر، امیر و زهرا 🌸</p>
    <a href="{{ url_for('home') }}">بازگشت به صفحه اصلی</a>
</div>
</body>
</html>
"""


# =========================================================
# صفحه اصلی
# =========================================================

@app.route("/")
def home():
    conn = get_db()
    messages = conn.execute("""
        SELECT * FROM messages ORDER BY id DESC LIMIT 20
    """).fetchall()
    conn.close()

    return render_template_string(
        PAGE,
        messages=messages,
        invitation_text=INVITATION_TEXT,
        wedding_date=WEDDING_DATE_FA,
        wedding_time=WEDDING_TIME,
        wedding_hall=WEDDING_HALL,
        wedding_address=WEDDING_ADDRESS,
        wedding_date_iso=WEDDING_DATE
    )


# =========================================================
# ثبت پاسخ حضور
# =========================================================

@app.route("/rsvp", methods=["POST"])
def rsvp():
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    attendance = request.form.get("attendance", "yes").strip()

    try:
        count = int(request.form.get("count", 1))
    except (TypeError, ValueError):
        count = 1

    count = max(1, min(count, 10))

    if not name:
        flash("لطفاً نام خود را وارد کنید.")
        return redirect(url_for("home") + "#rsvp")

    if attendance not in ("yes", "no"):
        attendance = "yes"

    token = secrets.token_urlsafe(18)

    conn = get_db()
    conn.execute("""
        INSERT INTO guests
        (name, phone, count, attendance, created_at, token)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        name,
        phone,
        count,
        attendance,
        datetime.now().strftime("%Y-%m-%d %H:%M"),
        token
    ))
    conn.commit()
    conn.close()

    return render_template_string(
        THANKS_PAGE,
        message="پاسخ شما با موفقیت ثبت شد. از اینکه به ما اطلاع دادید سپاسگزاریم."
    )


# =========================================================
# دعوت‌نامه اختصاصی
# =========================================================

@app.route("/invite/<token>")
def invite(token):
    guest = get_guest_by_token(token)

    if not guest:
        return "دعوت‌نامه پیدا نشد.", 404

    qr_url = url_for("guest_qr", token=token, _external=True)

    return render_template_string(
        INVITE_PAGE,
        guest=guest,
        qr_url=qr_url
    )


# =========================================================
# ساخت QR اختصاصی
# =========================================================

@app.route("/guest-qr/<token>.png")
def guest_qr(token):
    guest = get_guest_by_token(token)

    if not guest:
        return "دعوت‌نامه پیدا نشد.", 404

    invite_url = url_for("invite", token=token, _external=True)

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4
    )
    qr.add_data(invite_url)
    qr.make(fit=True)

    image = qr.make_image(fill_color="#674766", back_color="white")

    output = io.BytesIO()
    image.save(output, format="PNG")
    output.seek(0)

    return send_file(
        output,
        mimetype="image/png",
        download_name="invitation-qr.png"
    )


# =========================================================
# دفتر یادبود
# =========================================================

@app.route("/message", methods=["POST"])
def message():
    name = request.form.get("name", "").strip()
    text = request.form.get("message", "").strip()

    if not name or not text:
        return redirect(url_for("home") + "#messages")

    if len(name) > 100 or len(text) > 1000:
        return redirect(url_for("home") + "#messages")

    conn = get_db()
    conn.execute("""
        INSERT INTO messages (name, message, created_at)
        VALUES (?, ?, ?)
    """, (
        name,
        text,
        datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit()
    conn.close()

    return render_template_string(
        THANKS_PAGE,
        message="پیام زیبای شما در دفتر یادبود ثبت شد. ممنون از مهرتان!"
    )


# =========================================================
# افزودن رویداد به تقویم
# =========================================================

@app.route("/calendar")
def calendar():
    start = "20261223T153000Z"
    end = "20261223T183000Z"

    ics = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Amir and Zahra Wedding//FA
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:amir-zahra-wedding-2026@example.com
DTSTAMP:{datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')}
DTSTART:{start}
DTEND:{end}
SUMMARY:جشن عروسی امیر و زهرا
LOCATION:{WEDDING_HALL} - {WEDDING_ADDRESS}
DESCRIPTION:{INVITATION_TEXT}
END:VEVENT
END:VCALENDAR
"""

    response = make_response(ics)
    response.headers["Content-Type"] = "text/calendar; charset=utf-8"
    response.headers["Content-Disposition"] = (
        "attachment; filename=amir-zahra-wedding.ics"
    )
    return response


# =========================================================
# ورود مدیریت
# =========================================================

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin_panel"))

    if request.method == "POST":
        password = request.form.get("password", "")

        # رمز مدیریت از متغیر محیطی خوانده می‌شود.
        if secrets.compare_digest(password, ADMIN_PASSWORD):
            session.clear()
            session["admin_logged_in"] = True
            return redirect(url_for("admin_panel"))

        flash("رمز عبور اشتباه است.")

    return render_template_string(LOGIN_PAGE)


# =========================================================
# داشبورد مدیریت
# =========================================================

@app.route("/admin/panel")
@login_required
def admin_panel():
    conn = get_db()

    guests = conn.execute("""
        SELECT * FROM guests ORDER BY id DESC
    """).fetchall()

    messages = conn.execute("""
        SELECT * FROM messages ORDER BY id DESC
    """).fetchall()

    total = len(guests)
    attending = sum(1 for g in guests if g["attendance"] == "yes")
    people = sum(
        int(g["count"] or 1)
        for g in guests
        if g["attendance"] == "yes"
    )

    conn.close()

    return render_template_string(
        ADMIN_PAGE,
        guests=guests,
        messages=messages,
        total=total,
        attending=attending,
        people=people
    )


# =========================================================
# تعیین میز و صندلی مهمان
# =========================================================

@app.route("/admin/guest/<int:guest_id>/seat", methods=["POST"])
@login_required
def seat(guest_id):
    table_no = request.form.get("table_no", "").strip()
    seat_no = request.form.get("seat_no", "").strip()

    conn = get_db()
    conn.execute("""
        UPDATE guests
        SET table_no = ?, seat_no = ?
        WHERE id = ?
    """, (table_no, seat_no, guest_id))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


# =========================================================
# ثبت ورود مهمان
# =========================================================

@app.route("/admin/checkin/<token>", methods=["POST"])
@login_required
def checkin(token):
    conn = get_db()
    conn.execute("""
        UPDATE guests SET checked_in = 1 WHERE token = ?
    """, (token,))
    conn.commit()
    conn.close()

    return redirect(url_for("admin_panel"))


# =========================================================
# خروجی CSV
# =========================================================

@app.route("/admin/export")
@login_required
def export():
    conn = get_db()
    guests = conn.execute("""
        SELECT
            id, name, phone, count, attendance,
            created_at, token, table_no, seat_no, checked_in
        FROM guests
        ORDER BY id ASC
    """).fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "ID", "Name", "Phone", "Count", "Attendance",
        "Created At", "Token", "Table", "Seat", "Checked In"
    ])

    for g in guests:
        writer.writerow([
            g["id"],
            g["name"],
            g["phone"],
            g["count"],
            g["attendance"],
            g["created_at"],
            g["token"],
            g["table_no"],
            g["seat_no"],
            g["checked_in"]
        ])

    # BOM برای نمایش درست فارسی در Excel
    response = make_response("\ufeff" + output.getvalue())
    response.headers["Content-Type"] = "text/csv; charset=utf-8"
    response.headers["Content-Disposition"] = (
        "attachment; filename=wedding-guests.csv"
    )

    return response


# =========================================================
# خروج از مدیریت
# =========================================================

@app.route("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("admin"))


# =========================================================
# اجرای برنامه
# =========================================================

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
