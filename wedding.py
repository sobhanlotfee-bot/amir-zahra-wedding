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
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

DB_PATH = os.environ.get("DATABASE_PATH", "wedding.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "CHANGE_THIS_ADMIN_PASSWORD")

WEDDING_DATE = "2026-12-23T19:00:00+03:30"
VENUE = "تالار پذیرایی فریال"
ADDRESS = "استان سمنان، میدان معلم، بلوار بسیج، جنب ورزشگاه الغدیر"


# =========================================================
# DATABASE
# =========================================================

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

        columns = {
            row["name"]
            for row in con.execute(
                "PRAGMA table_info(guests)"
            ).fetchall()
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


# =========================================================
# SECURITY & HELPERS
# =========================================================

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


# =========================================================
# LUXURY DESIGN SYSTEM
# =========================================================

STYLE = r"""
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&family=Vazirmatn:wght@300;400;500;600;700;800&display=swap');

:root {
    --cream: #fffaf4;
    --cream2: #f8eee4;
    --rose: #d9aaa0;
    --rose-dark: #a96f69;
    --gold: #bd965d;
    --gold-light: #ead6ad;
    --brown: #60483d;
    --muted: #9a8275;
    --white: #fffefa;
    --shadow: 0 22px 65px rgba(99, 65, 48, .10);
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
    scroll-padding-top: 85px;
}

body {
    margin: 0;
    color: var(--brown);
    font-family: 'Vazirmatn', Tahoma, sans-serif;
    line-height: 2;
    background:
        radial-gradient(ellipse at 5% 5%, rgba(224,183,169,.25), transparent 32%),
        radial-gradient(ellipse at 95% 25%, rgba(229,205,163,.28), transparent 34%),
        linear-gradient(145deg, #fffaf4, #f7eee5);
    background-attachment: fixed;
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    z-index: -1;
    opacity: .25;
    background-image:
        radial-gradient(#bd965d 0.55px, transparent 0.55px);
    background-size: 17px 17px;
}

a {
    color: inherit;
}

button, input, select, textarea {
    font: inherit;
}

button, .btn {
    -webkit-tap-highlight-color: transparent;
}

.topline {
    height: 4px;
    background: linear-gradient(
        90deg,
        #a87948,
        #f1dfb9,
        #d3a77b,
        #f6e7c8,
        #a87948
    );
    background-size: 200% 100%;
    animation: goldShimmer 5s linear infinite;
}

@keyframes goldShimmer {
    to { background-position: 200% 0; }
}

/* NAVIGATION */

nav {
    position: sticky;
    top: 0;
    z-index: 50;
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 9px;
    padding: 12px 15px;
    background: rgba(255, 250, 244, .86);
    backdrop-filter: blur(18px);
    border-bottom: 1px solid rgba(189,150,93,.18);
    box-shadow: 0 5px 25px rgba(95,65,45,.04);
}

nav a {
    position: relative;
    padding: 5px 12px;
    text-decoration: none;
    color: #806657;
    font-size: 13px;
    transition: .3s;
}

nav a::after {
    content: "";
    position: absolute;
    bottom: 0;
    right: 50%;
    width: 0;
    height: 1px;
    background: var(--gold);
    transition: .3s;
}

nav a:hover {
    color: var(--rose-dark);
}

nav a:hover::after {
    width: 70%;
    right: 15%;
}

/* BUTTONS */

.btn, button {
    display: inline-flex;
    justify-content: center;
    align-items: center;
    gap: 8px;
    border: 0;
    border-radius: 50px;
    padding: 12px 25px;
    color: white;
    text-decoration: none;
    cursor: pointer;
    background: linear-gradient(120deg, #a87948, #d5b27a, #a87948);
    background-size: 180% 100%;
    box-shadow: 0 9px 24px rgba(153,110,61,.20);
    transition: transform .3s, box-shadow .3s, background-position .5s;
}

.btn:hover, button:hover {
    transform: translateY(-3px);
    box-shadow: 0 14px 30px rgba(153,110,61,.28);
    background-position: 100% 0;
}

.btn.light, button.light {
    color: #896b53;
    background: rgba(255,255,255,.72);
    border: 1px solid #e6d3b7;
    box-shadow: none;
}

.btn.light:hover, button.light:hover {
    background: #fff;
    box-shadow: 0 8px 22px rgba(120,83,52,.10);
}

/* HERO */

.hero {
    min-height: 92vh;
    display: grid;
    place-items: center;
    position: relative;
    isolation: isolate;
    overflow: hidden;
    padding: 65px 18px;
    background:
        radial-gradient(ellipse at center, rgba(255,255,255,.95), rgba(250,238,224,.68) 55%, transparent 78%);
}

.hero::before,
.hero::after {
    content: "❀";
    position: absolute;
    z-index: -1;
    color: #c18c80;
    opacity: .19;
    font-size: clamp(130px, 24vw, 270px);
    animation: flowerDrift 9s ease-in-out infinite;
}

.hero::before {
    top: 2%;
    right: -35px;
}

.hero::after {
    content: "✿";
    bottom: -40px;
    left: -35px;
    animation-delay: -4s;
}

@keyframes flowerDrift {
    0%,100% { transform: translateY(0) rotate(-12deg); }
    50% { transform: translateY(-22px) rotate(12deg); }
}

.hero-card {
    position: relative;
    width: 100%;
    max-width: 790px;
    padding: 60px 28px;
    text-align: center;
    border: 1px solid rgba(189,150,93,.55);
    outline: 1px solid rgba(189,150,93,.22);
    outline-offset: 9px;
    border-radius: 48% 48% 32px 32px / 13% 13% 32px 32px;
    background:
        linear-gradient(145deg, rgba(255,255,255,.96), rgba(250,239,224,.94));
    box-shadow: 0 35px 90px rgba(103,68,48,.13);
    animation: heroAppear 1.2s cubic-bezier(.2,.8,.2,1) both;
}

@keyframes heroAppear {
    from { opacity: 0; transform: translateY(35px) scale(.97); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

.hero-card::before,
.hero-card::after {
    content: "✧";
    position: absolute;
    color: var(--gold);
    font-size: 28px;
    opacity: .75;
}

.hero-card::before {
    top: 24px;
    right: 35px;
}

.hero-card::after {
    bottom: 22px;
    left: 35px;
}

.eyebrow {
    color: #a98252;
    letter-spacing: 3px;
    font-size: 11px;
    font-weight: 500;
}

.monogram {
    color: var(--gold);
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 58px;
    line-height: 1.5;
    letter-spacing: 5px;
    text-shadow: 0 5px 20px rgba(189,150,93,.15);
}

h1 {
    margin: 5px 0 12px;
    color: #a77950;
    font-family: 'Vazirmatn', Tahoma, sans-serif;
    font-size: clamp(42px, 8vw, 76px);
    font-weight: 400;
    line-height: 1.5;
}

h2 {
    color: #a77950;
    font-size: clamp(25px, 5vw, 34px);
    font-weight: 500;
    margin: 8px 0 12px;
}

h3 {
    color: #a77950;
    font-weight: 600;
    margin: 7px 0;
}

.goldline {
    width: 95px;
    height: 2px;
    margin: 22px auto;
    background: linear-gradient(90deg, transparent, #bd965d, transparent);
    position: relative;
}

.goldline::after {
    content: "✧";
    position: absolute;
    left: 50%;
    top: 50%;
    transform: translate(-50%,-50%);
    padding: 0 8px;
    background: #fffaf4;
    color: #bd965d;
}

/* SECTIONS */

section {
    width: min(1100px, 100%);
    margin: 42px auto;
    padding: 25px 20px;
    text-align: center;
}

.panel {
    position: relative;
    overflow: hidden;
    padding: clamp(25px, 5vw, 48px);
    border-radius: 35px;
    border: 1px solid rgba(189,150,93,.24);
    background:
        linear-gradient(145deg, rgba(255,255,255,.95), rgba(251,242,231,.94));
    box-shadow: var(--shadow);
}

.panel::before,
.panel::after {
    content: "❀";
    position: absolute;
    color: #c18c80;
    opacity: .13;
    font-size: 62px;
    pointer-events: none;
}

.panel::before {
    top: 3px;
    right: 12px;
}

.panel::after {
    bottom: 0;
    left: 12px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(190px, 1fr));
    gap: 17px;
    margin-top: 25px;
}

.tile {
    position: relative;
    padding: 22px 16px;
    border: 1px solid #ead9c4;
    border-radius: 24px;
    background: linear-gradient(145deg, #fffefa, #f8eee3);
    box-shadow: 0 9px 25px rgba(110,76,49,.045);
    transition: transform .35s, box-shadow .35s;
}

.tile:hover {
    transform: translateY(-7px);
    box-shadow: 0 17px 35px rgba(110,76,49,.11);
}

/* COUNTDOWN */

.countdown {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 12px;
    margin: 28px auto;
}

.time {
    min-width: 85px;
    padding: 15px 12px;
    border: 1px solid #e6d3b7;
    border-radius: 22px;
    background: linear-gradient(145deg, #fffefa, #f5e8d8);
    color: #987349;
    box-shadow: 0 8px 20px rgba(120,83,52,.06);
}

.time b {
    display: block;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 30px;
    line-height: 1.5;
    font-weight: 500;
}

/* GALLERY */

.gallery {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 15px;
    margin-top: 25px;
}

.gallery a {
    display: block;
    overflow: hidden;
    border-radius: 25px;
    border: 5px solid white;
    box-shadow: 0 10px 30px rgba(75,50,35,.12);
    aspect-ratio: 4 / 5;
    background: #f0e2d2;
}

.gallery img,
.gallery video {
    display: block;
    width: 100%;
    height: 100%;
    object-fit: cover;
    transition: transform .6s;
}

.gallery a:hover img {
    transform: scale(1.09);
}

.gallery video {
    border: 5px solid white;
    border-radius: 25px;
    background: #ead9c7;
    box-shadow: 0 10px 30px rgba(75,50,35,.12);
}

/* FORMS */

form {
    max-width: 540px;
    margin: 22px auto 0;
    text-align: right;
}

label {
    display: block;
    margin: 12px 4px 4px;
    color: #866a55;
    font-size: 14px;
}

input, select, textarea {
    width: 100%;
    padding: 13px 16px;
    margin: 6px 0 13px;
    color: var(--brown);
    background: rgba(255,255,255,.85);
    border: 1px solid #e4d1b9;
    border-radius: 17px;
    outline: none;
    transition: border .25s, box-shadow .25s;
}

input:focus, select:focus, textarea:focus {
    border-color: #c49a68;
    box-shadow: 0 0 0 4px rgba(196,154,104,.12);
}

textarea {
    min-height: 120px;
    resize: vertical;
}

form button {
    width: 100%;
    margin-top: 7px;
}

.note {
    color: #9a8777;
    font-size: 12px;
}

/* FOOTER */

footer {
    position: relative;
    margin-top: 65px;
    padding: 55px 18px 35px;
    text-align: center;
    color: #896c56;
    background: linear-gradient(145deg, #f3e5d6, #ead7c5);
    border-radius: 65px 65px 0 0;
}

footer .monogram {
    font-size: 34px;
}

/* PETALS */

.flower {
    position: fixed;
    top: -35px;
    z-index: 35;
    pointer-events: none;
    color: #c58e83;
    opacity: .0;
    text-shadow: 0 3px 12px rgba(185,134,125,.35);
    animation: petalFall linear infinite;
}

@keyframes petalFall {
    0% {
        transform: translate(0,-8vh) rotate(0);
        opacity: 0;
    }
    12% { opacity: .65; }
    50% {
        transform: translate(35px,50vh) rotate(190deg);
    }
    100% {
        transform: translate(-25px,110vh) rotate(390deg);
        opacity: 0;
    }
}

/* ENVELOPE INTRO */

#intro {
    position: fixed;
    inset: 0;
    z-index: 200;
    display: grid;
    place-items: center;
    padding: 20px;
    background:
        radial-gradient(ellipse at center, #fffaf2, #ead7c2);
    transition: opacity 1s ease, visibility 1s ease;
}

#intro.hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
}

.intro-content {
    text-align: center;
    animation: introEnter 1s ease both;
}

@keyframes introEnter {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.envelope {
    position: relative;
    width: min(350px, 82vw);
    height: 220px;
    margin: 28px auto 0;
    border: 1px solid #b99465;
    border-radius: 10px 10px 24px 24px;
    background: linear-gradient(145deg, #f7e8d1, #d9bd96);
    box-shadow: 0 28px 70px rgba(91,65,37,.25);
    perspective: 900px;
    animation: envelopeFloat 4s ease-in-out infinite;
}

.envelope::before {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 4;
    background: linear-gradient(145deg, #fff1d9, #d9bd96);
    clip-path: polygon(0 0, 50% 58%, 100% 0);
    transform-origin: top center;
    transition: transform 1s ease;
}

.envelope.open::before {
    transform: rotateX(180deg);
}

.envelope::after {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 2;
    background: linear-gradient(35deg, #d8bd96, #f8e9d0);
    clip-path: polygon(0 100%, 50% 48%, 100% 100%);
}

.envelope-paper {
    position: absolute;
    left: 8%;
    top: 12%;
    width: 84%;
    height: 78%;
    display: grid;
    place-items: center;
    color: #a77950;
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 24px;
    background: #fffaf0;
    box-shadow: 0 5px 15px rgba(80,50,30,.1);
}

.seal {
    position: absolute;
    z-index: 6;
    top: 77px;
    left: 50%;
    transform: translateX(-50%);
    width: 67px;
    height: 67px;
    display: grid;
    place-items: center;
    border: 3px solid #e8cc99;
    border-radius: 50%;
    color: #fff2d9;
    background: radial-gradient(circle at 35% 30%, #d6ae70, #84582f);
    box-shadow: 0 9px 24px rgba(80,50,30,.28);
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 19px;
    transition: opacity .4s;
}

.envelope.open .seal {
    opacity: 0;
}

@keyframes envelopeFloat {
    0%,100% { transform: translateY(0); }
    50% { transform: translateY(-10px); }
}

.envelope-button {
    margin-top: 28px;
}

/* MUSIC BUTTON */

#musicBtn {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 70;
    width: 53px;
    height: 53px;
    padding: 0;
    border-radius: 50%;
    font-size: 22px;
}

#musicBtn.playing {
    animation: musicPulse 1.7s infinite;
}

@keyframes musicPulse {
    50% { box-shadow: 0 0 0 10px rgba(189,150,93,.15); }
}

/* REVEAL ON SCROLL */

.reveal {
    opacity: 0;
    transform: translateY(28px);
    transition: opacity .8s ease, transform .8s ease;
}

.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}

/* ADMIN */

.admin {
    width: min(1200px, 100%);
    margin: 25px auto;
    padding: 18px;
}

.admin table {
    width: 100%;
    border-collapse: collapse;
    background: white;
    font-size: 13px;
}

.admin th, .admin td {
    border: 1px solid #eadcc6;
    padding: 9px;
    text-align: center;
}

.admin th {
    background: #f4ead9;
    color: #80613f;
}

.admin .tile b {
    font-size: 25px;
    color: #a77950;
}

.admin input {
    min-width: 65px;
}

.admin .panel {
    margin-bottom: 22px;
}

/* INVITATION */

.invitation-card {
    max-width: 650px;
    margin: 30px auto;
    padding: 38px 20px;
    border: 1px solid #d9bd96;
    outline: 1px solid rgba(189,150,93,.25);
    outline-offset: 7px;
    border-radius: 35px;
    background: linear-gradient(145deg, #fffefa, #f8eddf);
    box-shadow: var(--shadow);
}

.invitation-card img {
    display: block;
    width: 190px;
    max-width: 80%;
    margin: 22px auto;
    padding: 10px;
    border: 1px solid #e5d2b5;
    border-radius: 15px;
    background: white;
}

/* RESPONSIVE */

@media (max-width: 700px) {
    nav {
        gap: 3px;
        padding: 9px 5px;
    }

    nav a {
        font-size: 11px;
        padding: 5px 7px;
    }

    .hero {
        min-height: 82vh;
        padding: 40px 17px;
    }

    .hero-card {
        padding: 48px 18px;
        border-radius: 42% 42% 25px 25px / 12% 12% 25px 25px;
    }

    .monogram {
        font-size: 45px;
    }

    section {
        margin: 24px auto;
        padding: 17px 12px;
    }

    .panel {
        padding: 25px 17px;
        border-radius: 27px;
    }

    .grid {
        grid-template-columns: repeat(2, minmax(0,1fr));
        gap: 10px;
    }

    .tile {
        padding: 17px 10px;
        border-radius: 19px;
        font-size: 13px;
    }

    .gallery {
        grid-template-columns: repeat(2, 1fr);
        gap: 9px;
    }

    .gallery a {
        border-radius: 17px;
        border-width: 3px;
    }

    .time {
        min-width: 70px;
        padding: 10px 7px;
        border-radius: 17px;
        font-size: 12px;
    }

    .time b {
        font-size: 25px;
    }

    footer {
        border-radius: 40px 40px 0 0;
    }
}

@media (max-width: 390px) {
    .grid {
        grid-template-columns: 1fr;
    }

    .hero-card {
        padding: 42px 13px;
    }

    nav a {
        font-size: 10px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: .01ms !important;
        animation-iteration-count: 1 !important;
        scroll-behavior: auto !important;
        transition-duration: .01ms !important;
    }
}
"""


# =========================================================
# MAIN PAGE
# =========================================================

PAGE = r"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#fffaf4">
<meta name="description" content="دعوت‌نامه جشن پیوند امیر و زهرا">
<title>عروسی امیر و زهرا | دعوت‌نامه</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<style>""" + STYLE + r"""</style>
</head>

<body>

<div id="intro">
    <div class="intro-content">
        <div class="eyebrow">A SPECIAL INVITATION</div>
        <div class="monogram">A <span style="font-size:25px">&</span> Z</div>
        <p style="color:#987650">دعوت‌نامه‌ای برای یک روز خاص</p>

        <div class="envelope" id="envelope">
            <div class="envelope-paper">Amir & Zahra</div>
            <div class="seal">A & Z</div>
        </div>

        <button class="envelope-button" onclick="openEnvelope()">
            ✧ باز کردن دعوت‌نامه ✧
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

        <div class="monogram">
            A <span style="font-size:26px">&</span> Z
        </div>

        <h1>امیر و زهرا</h1>

        <div class="goldline"></div>

        <p class="sub"
           data-fa="با کمال افتخار از شما دعوت می‌کنیم در جشن پیوند و آغاز زندگی مشترک امیر و زهرا، در کنار ما باشید."
           data-en="With great joy, we invite you to celebrate the beginning of Amir and Zahra's life together.">
            با کمال افتخار از شما دعوت می‌کنیم در جشن پیوند و آغاز زندگی مشترک امیر و زهرا، در کنار ما باشید.
        </p>

        <p style="color:#987650;font-size:17px">
            چهارشنبه، ۲ دی ۱۴۰۵
        </p>

        <p style="color:#987650">
            ساعت ۱۹:۰۰ تا ۲۲:۰۰
        </p>

        <a class="btn" href="#details">مشاهده جزئیات مراسم</a>
    </div>
</header>

<section id="story" class="reveal">
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
                <div style="font-size:29px;color:#bd965d">♡</div>
                <h3>آشنایی</h3>
                شروع یک اتفاق قشنگ
            </div>

            <div class="tile">
                <div style="font-size:29px;color:#bd965d">✧</div>
                <h3>عهد عشق</h3>
                انتخابی برای تمام فرداها
            </div>

            <div class="tile">
                <div style="font-size:29px;color:#bd965d">❀</div>
                <h3>جشن ما</h3>
                خوشحالیم کنارمان هستید
            </div>
        </div>

        <p class="note">
            این متن نمونه است؛ می‌توانی بعداً داستان واقعی خودتان را جایگزین کنی.
        </p>
    </div>
</section>

<section id="details" class="reveal">
    <div class="panel">
        <div class="eyebrow">SAVE THE DATE</div>
        <h2>روز به‌یادماندنی ما</h2>
        <div class="goldline"></div>

        <div class="countdown" id="countdown"></div>

        <div class="grid">
            <div class="tile">
                <div style="font-size:27px">✧</div>
                <h3>تاریخ</h3>
                چهارشنبه ۲ دی ۱۴۰۵
                <br>
                ۲۳ دسامبر ۲۰۲۶
            </div>

            <div class="tile">
                <div style="font-size:27px">◷</div>
                <h3>ساعت</h3>
                ۱۹:۰۰ تا ۲۲:۰۰
            </div>

            <div class="tile">
                <div style="font-size:27px">❀</div>
                <h3>مکان</h3>
                {{ venue }}
                <br>
                {{ address }}
            </div>
        </div>

        <p style="margin-top:28px">
            <a class="btn light"
               target="_blank"
               rel="noopener"
               href="https://www.google.com/maps/search/?api=1&query=تالار+پذیرایی+فریال+سمنان">
                مشاهده مسیر تالار
            </a>

            <a class="btn light" href="/calendar">
                افزودن به تقویم
            </a>
        </p>
    </div>
</section>

<section id="gallery" class="reveal">
    <div class="panel">
        <div class="eyebrow">OUR MEMORIES</div>
        <h2>قاب‌هایی از خاطره</h2>
        <div class="goldline"></div>

        <div class="gallery">
            {% for i in range(1,7) %}
            <a href="/static/photo{{i}}.jpg" target="_blank" rel="noopener">
                <img
                    src="/static/photo{{i}}.jpg"
                    alt="عکس خاطره {{i}}"
                    loading="lazy"
                    onerror="this.parentElement.style.display='none'">
            </a>
            {% endfor %}

            <video controls playsinline preload="metadata"
                   src="/static/wedding.mp4"></video>
        </div>

        <p class="note">
            عکس‌ها و ویدیوهای خودتان را در پوشه static قرار دهید.
        </p>
    </div>
</section>

<section id="rsvp" class="reveal">
    <div class="panel">
        <div class="eyebrow">KINDLY RESPOND</div>
        <h2>پاسخ به دعوت</h2>
        <div class="goldline"></div>

        <p>
            حضور ارزشمندتان را به ما اطلاع دهید.
            منتظر دیدارتان هستیم.
        </p>

        <form method="post" action="/rsvp">
            <label>نام و نام خانوادگی</label>
            <input name="name"
                   maxlength="100"
                   placeholder="نام شما"
                   required>

            <label>تعداد افراد همراه</label>
            <input name="count"
                   type="number"
                   min="1"
                   max="20"
                   value="1"
                   required>

            <label>وضعیت حضور</label>
            <select name="status">
                <option value="حضور دارم">با افتخار حضور دارم</option>
                <option value="متأسفانه نمی‌توانم">متأسفانه نمی‌توانم حضور داشته باشم</option>
            </select>

            <button type="submit">ثبت پاسخ و دریافت دعوت‌نامه</button>
        </form>
    </div>
</section>

<section id="guestbook" class="reveal">
    <div class="panel">
        <div class="eyebrow">LEAVE A WISH</div>
        <h2>دفتر یادبود</h2>
        <div class="goldline"></div>

        <p>پیام و آرزوی زیبای خود را برای ما بنویسید.</p>

        <form method="post" action="/message">
            <label>نام شما</label>
            <input name="name"
                   required
                   maxlength="100"
                   placeholder="نام شما">

            <label>پیام شما</label>
            <textarea name="message"
                      required
                      maxlength="500"
                      placeholder="پیام و آرزوی زیبای شما..."></textarea>

            <button type="submit">ثبت پیام</button>
        </form>

        {% for m in messages %}
        <div class="tile"
             style="margin:14px auto;max-width:650px;text-align:right">
            <b style="color:#a77950">{{ m.name }}</b>
            <p style="margin:5px 0">{{ m.message }}</p>
        </div>
        {% endfor %}
    </div>
</section>

<section class="reveal">
    <div class="panel">
        <div class="monogram">A & Z</div>
        <h2>با مهر، امیر و زهرا</h2>
        <div class="goldline"></div>

        <p>
            از اینکه در شادی ما شریک هستید سپاسگزاریم.
            حضور شما زیباترین هدیه ماست.
        </p>

        <button class="btn light" onclick="shareSite()">
            اشتراک‌گذاری دعوت‌نامه
        </button>

        <p style="margin-top:18px">
            <a href="/thanks" style="color:#987650">
                صفحه سپاسگزاری
            </a>
        </p>
    </div>
</section>

<footer>
    <div class="monogram">A & Z</div>
    <p>یک آغاز، یک عشق، یک زندگی</p>
    <div class="goldline"></div>
    Made with love · 2026
</footer>

<audio id="music" src="/static/music.mp3" loop preload="none"></audio>

<button id="musicBtn"
        aria-label="موسیقی"
        onclick="toggleMusic()">♫</button>

<script>
const target = new Date("2026-12-23T19:00:00+03:30").getTime();

function tick() {
    const element = document.getElementById("countdown");
    if (!element) return;

    let distance = target - Date.now();

    if (distance <= 0) {
        element.innerHTML = "<div class='tile'>روز جشن فرا رسیده است! ♡</div>";
        return;
    }

    const values = [
        Math.floor(distance / 86400000),
        Math.floor((distance % 86400000) / 3600000),
        Math.floor((distance % 3600000) / 60000),
        Math.floor((distance % 60000) / 1000)
    ];

    const labels = ["روز", "ساعت", "دقیقه", "ثانیه"];

    element.innerHTML = values.map((value, index) => `
        <div class="time">
            <b>${value}</b>
            ${labels[index]}
        </div>
    `).join("");
}

tick();
setInterval(tick, 1000);


function openEnvelope() {
    const envelope = document.getElementById("envelope");
    const intro = document.getElementById("intro");

    envelope.classList.add("open");

    setTimeout(() => {
        intro.classList.add("hidden");
    }, 950);
}


const music = document.getElementById("music");
const musicBtn = document.getElementById("musicBtn");

function toggleMusic() {
    if (music.paused) {
        music.play().then(() => {
            musicBtn.classList.add("playing");
            musicBtn.textContent = "♫";
        }).catch(() => {
            alert("برای پخش موسیقی، دوباره دکمه موسیقی را انتخاب کنید.");
        });
    } else {
        music.pause();
        musicBtn.classList.remove("playing");
        musicBtn.textContent = "♫";
    }
}


async function shareSite() {
    if (navigator.share) {
        try {
            await navigator.share({
                title: "دعوت‌نامه عروسی امیر و زهرا",
                text: "با افتخار دعوتید در جشن عروسی امیر و زهرا کنار ما باشید.",
                url: location.href
            });
        } catch (error) {}
    } else {
        try {
            await navigator.clipboard.writeText(location.href);
            alert("لینک دعوت‌نامه کپی شد.");
        } catch (error) {
            prompt("لینک دعوت‌نامه:", location.href);
        }
    }
}


let english = false;

function toggleLang() {
    english = !english;

    document.documentElement.lang = english ? "en" : "fa";
    document.documentElement.dir = english ? "ltr" : "rtl";

    document.querySelectorAll("[data-fa]").forEach(element => {
        element.textContent = english
            ? element.dataset.en
            : element.dataset.fa;
    });
}


// Scroll reveal animation
const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            revealObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.12 });

document.querySelectorAll(".reveal").forEach(element => {
    revealObserver.observe(element);
});


// Floating petals
const petalSymbols = ["✿", "❀", "✧", "❁"];

for (let i = 0; i < 17; i++) {
    const petal = document.createElement("span");

    petal.className = "flower";
    petal.textContent = petalSymbols[
        Math.floor(Math.random() * petalSymbols.length)
    ];

    petal.style.left = Math.random() * 100 + "%";
    petal.style.fontSize = (13 + Math.random() * 17) + "px";
    petal.style.animationDuration = (9 + Math.random() * 11) + "s";
    petal.style.animationDelay = (Math.random() * 12) + "s";

    document.body.appendChild(petal);
}
</script>

</body>
</html>
"""


# =========================================================
# PERSONAL INVITATION
# =========================================================

INVITE_PAGE = r"""
<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#fffaf4">
<title>دعوت‌نامه اختصاصی امیر و زهرا</title>
<style>""" + STYLE + r"""</style>
</head>

<body>
<div class="topline"></div>

<section>
    <div class="invitation-card">
        <div class="eyebrow">A PERSONAL INVITATION</div>
        <div class="monogram">A & Z</div>
        <h1 style="font-size:45px">امیر و زهرا</h1>
        <div class="goldline"></div>

        <h2>دعوت‌نامه اختصاصی</h2>

        <p>مهمان گرامی: <b>{{ guest.name }}</b></p>
        <p>تعداد ثبت‌شده: {{ guest.count }} نفر</p>
        <p>وضعیت: {{ guest.status }}</p>

        <div class="goldline"></div>

        <p>چهارشنبه ۲ دی ۱۴۰۵</p>
        <p>ساعت ۱۹:۰۰ تا ۲۲:۰۰</p>
        <p>{{ venue }}</p>
        <p>{{ address }}</p>

        <img src="{{ url_for('guest_qr', token=guest.token) }}"
             alt="QR اختصاصی دعوت‌نامه">

        <p class="note">
            این QR کد اختصاصی دعوت‌نامه شماست.
        </p>

        <a class="btn light"
           target="_blank"
           rel="noopener"
           href="https://www.google.com/maps/search/?api=1&query=تالار+پذیرایی+فریال+سمنان">
            مسیریابی تالار
        </a>

        <p style="margin-top:20px">
            <a class="btn" href="/">صفحه اصلی</a>
        </p>
    </div>
</section>

</body>
</html>
"""


# =========================================================
# ADMIN LOGIN
# =========================================================

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
<div class="topline"></div>

<section style="margin-top:9vh">
    <div class="panel">
        <div class="monogram">A & Z</div>
        <h2>پنل مدیریت</h2>
        <div class="goldline"></div>
        <p>برای ورود، رمز مدیریت را وارد کنید.</p>

        <form method="post">
            <label>رمز مدیریت</label>
            <input type="password"
                   name="password"
                   autocomplete="current-password"
                   required>

            <button type="submit">ورود به پنل</button>
        </form>
    </div>
</section>

</body>
</html>
"""


# =========================================================
# ADMIN DASHBOARD
# =========================================================

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
<div class="topline"></div>

<div class="admin">

    <div class="panel">
        <div class="eyebrow">AMIR & ZAHRA</div>
        <h1 style="font-size:38px">پنل مدیریت</h1>
        <div class="goldline"></div>

        <a class="btn light" href="{{ url_for('export_csv') }}">
            دانلود فهرست مهمان‌ها
        </a>

        <a class="btn light" href="{{ url_for('logout') }}">
            خروج از مدیریت
        </a>
    </div>

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

    <div class="panel" style="margin-top:25px">
        <h2>فهرست مهمان‌ها</h2>
        <div class="goldline"></div>

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
                              style="display:flex;gap:4px;min-width:180px;margin:0">

                            <input name="table_no"
                                   value="{{ g.table_no or '' }}"
                                   placeholder="میز"
                                   style="margin:0;padding:5px;min-width:60px">

                            <input name="seat_no"
                                   value="{{ g.seat_no or '' }}"
                                   placeholder="صندلی"
                                   style="margin:0;padding:5px;min-width:60px">

                            <button type="submit" style="padding:5px 9px">
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
                              action="{{ url_for('checkin', token=g.token) }}"
                              style="margin:0">

                            <button type="submit" style="padding:6px 10px">
                                {{ "لغو ورود" if g.checked_in else "ثبت ورود" }}
                            </button>
                        </form>
                    </td>
                </tr>
                {% endfor %}
            </table>
        </div>
    </div>

    <div class="panel" style="margin-top:25px">
        <h2>پیام‌های دفتر یادبود</h2>
        <div class="goldline"></div>

        {% for m in messages %}
        <div class="tile" style="margin:10px 0;text-align:right">
            <b>{{ m.name }}</b>
            <p>{{ m.message }}</p>
            <small class="note">{{ m.created or "" }}</small>
        </div>
        {% else %}
        <p>هنوز پیامی ثبت نشده است.</p>
        {% endfor %}
    </div>

</div>
</body>
</html>
"""


# =========================================================
# THANK YOU PAGE
# =========================================================

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
<div class="topline"></div>

<section style="margin-top:10vh">
    <div class="panel">
        <div class="monogram">A & Z</div>
        <h1>سپاسگزاریم</h1>
        <h2>برای همراهی و عشق شما</h2>
        <div class="goldline"></div>

        <p>حضور و مهرتان زیباترین یادگار جشن ماست.</p>

        <a class="btn" href="/">بازگشت به دعوت‌نامه</a>
    </div>
</section>

</body>
</html>
"""


# =========================================================
# WEBSITE ROUTES
# =========================================================

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

    allowed_statuses = {
        "حضور دارم",
        "متأسفانه نمی‌توانم"
    }

    if status not in allowed_statuses:
        status = "حضور دارم"

    try:
        count = max(1, min(20, int(request.form.get("count", 1))))
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


# =========================================================
# ADMIN ROUTES
# =========================================================

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


# =========================================================
# ERROR HANDLERS & START
# =========================================================

@app.errorhandler(404)
def not_found(error):
    return "صفحه موردنظر پیدا نشد.", 404


@app.errorhandler(500)
def server_error(error):
    return "خطای داخلی سرور رخ داده است.", 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000))
    )