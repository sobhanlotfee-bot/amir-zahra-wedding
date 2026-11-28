import os
import csv
import html
import logging
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from flask import Flask, request, redirect, render_template_string, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
GUESTS_FILE = BASE_DIR / "guests.csv"

logging.basicConfig(level=logging.INFO)

# -------------------- اطلاعات مراسم --------------------

BRIDE = "زهرا"
GROOM = "امیر"

WEDDING_DATE = "چهارشنبه ۲ دی ۱۴۰۵"
WEDDING_TIME = "۱۹:۰۰ تا ۲۲:۰۰"

ADDRESS = (
    "سمنان، میدان معلم، بلوار بسیج، "
    "جنب ورزشگاه الغدیر، تالار پذیرایی فریال"
)

MAP_URL = (
    "https://www.google.com/maps/dir/?api=1"
    "&destination=35.5868900%2C53.3861140"
    "&travelmode=driving&dir_action=navigate"
)

# تاریخ میلادی مراسم: ۲۳ دسامبر ۲۰۲۶، ساعت ۱۹ به وقت ایران
COUNTDOWN_DATE = "2026-12-23T19:00:00+03:30"

# -------------------- فایل‌های رسانه‌ای --------------------

def existing_static_files(names):
    result = []
    for name in names:
        if (STATIC_DIR / name).is_file():
            result.append("/static/" + quote(name))
    return result


PHOTO_NAMES = [
    "wedding-photo.jpg",
    "photo1.jpg",
    "photo2.jpg",
    "photo3.jpg",
    "photo4.jpg",
    "photo5.jpg",
    "photo6.jpg",
]

VIDEO_EXISTS = (STATIC_DIR / "wedding.mp4").is_file()
MUSIC_EXISTS = (STATIC_DIR / "music.mp3").is_file()

# -------------------- پیام تلگرام --------------------

def send_telegram_message(message):
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("ADMIN_CHAT_ID")

    if not token or not chat_id:
        app.logger.info("Telegram credentials are not configured.")
        return False

    try:
        import json
        import urllib.request

        api_url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            api_url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200

    except Exception:
        app.logger.exception("Telegram message failed")
        return False


# -------------------- ذخیره پاسخ مهمان --------------------

def save_guest(name, count, attendance):
    file_exists = GUESTS_FILE.exists()

    with GUESTS_FILE.open(
        "a",
        newline="",
        encoding="utf-8-sig",
    ) as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "تاریخ ثبت",
                "نام مهمان",
                "تعداد نفرات",
                "وضعیت حضور",
            ])

        writer.writerow([
            datetime.now().isoformat(timespec="seconds"),
            name,
            count,
            attendance,
        ])


# -------------------- صفحه اصلی --------------------

PAGE = r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1, viewport-fit=cover">

    <meta name="theme-color" content="#501426">
    <meta name="description"
          content="دعوت‌نامه عروسی امیر و زهرا">

    <title>دعوت‌نامه عروسی امیر و زهرا</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>

    <link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700;800&display=swap"
          rel="stylesheet">

    <style>
    /* =====================================================
       رنگ‌ها و تنظیمات اصلی
    ===================================================== */

    :root {
        --wine: #501426;
        --wine-deep: #28151b;
        --ruby: #762b40;
        --gold: #b88a42;
        --gold-light: #e6ca8c;
        --champagne: #dcc9a8;
        --pearl: #f4ebdd;
        --paper: #fbf5e9;
        --ink: #3a2028;
        --muted: #806b62;
        --shadow: rgba(40, 21, 27, .18);
    }

    * {
        box-sizing: border-box;
    }

    html {
        scroll-behavior: smooth;
        background: var(--wine-deep);
    }

    body {
        margin: 0;
        color: var(--ink);
        font-family: "Vazirmatn", Tahoma, sans-serif;
        background:
            radial-gradient(ellipse at 50% 0%, #fff8eb 0%, transparent 65%),
            var(--pearl);
        overflow-x: hidden;
    }

    body.locked {
        overflow: hidden;
        height: 100dvh;
    }

    button, input, select {
        font: inherit;
    }

    button {
        cursor: pointer;
    }

    img {
        max-width: 100%;
    }

    a {
        color: inherit;
    }

    .nastaliq {
        font-family: "IranNastaliq", "Vazirmatn", serif;
        font-weight: normal;
    }

    @font-face {
        font-family: "IranNastaliq";
        src: url("/static/fonts/IranNastaliq.ttf") format("truetype");
        font-display: swap;
    }

    /* =====================================================
       بافت کاغذ و تزئینات
    ===================================================== */

    .paper-texture {
        background-color: var(--paper);
        background-image:
            linear-gradient(rgba(255,255,255,.2), rgba(255,255,255,.2)),
            url("/static/textures/pearl-paper.jpg");
        background-size: cover;
        background-position: center;
    }

    .gold-frame {
        position: relative;
        border: 1px solid rgba(184,138,66,.75);
        border-radius: 25px;
        outline: 1px solid rgba(184,138,66,.25);
        outline-offset: -8px;
        box-shadow:
            0 15px 40px rgba(40,21,27,.10),
            inset 0 0 25px rgba(184,138,66,.07);
    }

    .gold-frame::before {
        content: "";
        position: absolute;
        inset: 9px;
        border: 1px solid rgba(184,138,66,.35);
        border-radius: 18px;
        pointer-events: none;
    }

    .corner-decoration {
        position: absolute;
        width: 65px;
        height: 65px;
        background-image: url("/static/ornaments/gold-corners.png");
        background-size: contain;
        background-repeat: no-repeat;
        pointer-events: none;
        opacity: .8;
    }

    .corner-decoration.top-right {
        top: 5px;
        right: 5px;
    }

    .corner-decoration.top-left {
        top: 5px;
        left: 5px;
        transform: rotate(90deg);
    }

    .corner-decoration.bottom-right {
        bottom: 5px;
        right: 5px;
        transform: rotate(-90deg);
    }

    .corner-decoration.bottom-left {
        bottom: 5px;
        left: 5px;
        transform: rotate(180deg);
    }

    .ornament-divider {
        display: block;
        width: min(250px, 70%);
        height: 38px;
        margin: 18px auto;
        object-fit: contain;
        opacity: .85;
    }

    .gold-text {
        background: linear-gradient(
            110deg,
            #8b642e,
            #e6ca8c,
            #a87831,
            #f0d99f
        );
        -webkit-background-clip: text;
        background-clip: text;
        color: transparent;
    }

    .small-flower {
        color: var(--gold);
        font-size: 23px;
        text-align: center;
        letter-spacing: 8px;
        margin: 15px 0;
    }

    /* =====================================================
       پاکت تمام صفحه
    ===================================================== */

    #envelope-screen {
        position: fixed;
        inset: 0;
        z-index: 10000;
        width: 100%;
        height: 100vh;
        height: 100dvh;
        overflow: hidden;
        display: grid;
        place-items: center;
        background:
            radial-gradient(ellipse at center, #7a3348 0%, #501426 55%, #28151b 100%);
        transition:
            opacity 1.1s ease,
            visibility 1.1s ease;
    }

    #envelope-screen::before {
        content: "";
        position: absolute;
        inset: 10px;
        border: 1px solid rgba(230,202,140,.7);
        border-radius: 23px;
        box-shadow:
            inset 0 0 0 5px rgba(184,138,66,.12),
            inset 0 0 35px rgba(0,0,0,.2);
        pointer-events: none;
    }

    #envelope-screen::after {
        content: "";
        position: absolute;
        inset: 20px;
        border: 1px solid rgba(230,202,140,.28);
        border-radius: 17px;
        pointer-events: none;
    }

    .envelope-glow {
        position: absolute;
        width: 75vw;
        height: 75vw;
        max-width: 600px;
        max-height: 600px;
        border-radius: 50%;
        background: radial-gradient(
            circle,
            rgba(230,202,140,.14),
            transparent 70%
        );
        animation: glowPulse 5s ease-in-out infinite;
    }

    .envelope {
        position: relative;
        width: 100%;
        height: 100%;
        display: grid;
        place-items: center;
        perspective: 1200px;
    }

    .envelope-paper {
        position: absolute;
        inset: 0;
        background:
            linear-gradient(135deg, rgba(255,255,255,.04), transparent 40%),
            url("/static/textures/burgundy-paper.jpg"),
            linear-gradient(145deg, #6b263b, #3e101f);
        background-size: cover;
        background-position: center;
    }

    .envelope-inner-border {
        position: absolute;
        inset: 31px;
        border: 1px solid rgba(230,202,140,.65);
        border-radius: 17px;
        box-shadow:
            inset 0 0 0 5px rgba(184,138,66,.09),
            0 0 30px rgba(0,0,0,.15);
        pointer-events: none;
    }

    .envelope-inner-border::after {
        content: "";
        position: absolute;
        inset: 8px;
        border: 1px solid rgba(230,202,140,.24);
        border-radius: 12px;
    }

    .envelope-center {
        position: relative;
        z-index: 3;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 20px;
        transition: opacity .7s ease, transform .7s ease;
    }

    .envelope-label {
        color: var(--gold-light);
        font-size: clamp(14px, 3.5vw, 19px);
        letter-spacing: 2px;
        margin-bottom: 24px;
        text-shadow: 0 2px 8px rgba(0,0,0,.4);
    }

    .wax-seal {
        position: relative;
        width: 132px;
        height: 132px;
        border-radius: 50%;
        border: 5px solid #8e3b4e;
        background:
            radial-gradient(circle at 35% 27%, #bd6570, transparent 35%),
            radial-gradient(circle at 65% 70%, #68182e, transparent 60%),
            radial-gradient(circle at center, #8b263d, #4a1022 75%);
        box-shadow:
            0 12px 30px rgba(0,0,0,.4),
            inset 0 5px 10px rgba(255,255,255,.17),
            inset 0 -8px 14px rgba(0,0,0,.25),
            0 0 0 2px rgba(230,202,140,.8),
            0 0 0 7px rgba(184,138,66,.18);
        animation: sealFloat 3.5s ease-in-out infinite;
        display: grid;
        place-items: center;
        border-radius: 48% 52% 47% 53% / 52% 46% 54% 48%;
    }

    .wax-seal::before {
        content: "";
        position: absolute;
        inset: 9px;
        border: 1px solid rgba(230,202,140,.55);
        border-radius: 50%;
    }

    .wax-seal::after {
        content: "";
        position: absolute;
        top: 15px;
        left: 22px;
        width: 34px;
        height: 16px;
        border-radius: 50%;
        background: rgba(255,255,255,.13);
        filter: blur(7px);
        transform: rotate(-30deg);
    }

    .open-hint {
        margin-top: 30px;
        color: #f1dfbd;
        font-size: 13px;
        animation: hintPulse 2s infinite;
    }

    .envelope-flap {
        position: absolute;
        z-index: 4;
        top: 0;
        left: 0;
        width: 100%;
        height: 50%;
        transform-origin: top center;
        background: linear-gradient(160deg, #783149, #501426);
        clip-path: polygon(0 0, 100% 0, 50% 100%);
        border-bottom: 1px solid rgba(230,202,140,.5);
        transition: transform 1.3s cubic-bezier(.7,0,.2,1);
        pointer-events: none;
    }

    .envelope-bottom {
        position: absolute;
        z-index: 2;
        bottom: 0;
        width: 100%;
        height: 53%;
        background: linear-gradient(20deg, #3c101e, #65243a);
        clip-path: polygon(0 100%, 50% 0, 100% 100%);
        opacity: .65;
        pointer-events: none;
    }

    #envelope-screen.opening .envelope-flap {
        transform: rotateX(180deg);
    }

    #envelope-screen.opening .envelope-center {
        opacity: 0;
        transform: translateY(-35px) scale(.8);
    }

    #envelope-screen.opening {
        animation: envelopeDisappear 1.8s 1.1s forwards;
    }

    #envelope-screen.hidden {
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
    }

    /* =====================================================
       محتوای اصلی
    ===================================================== */

    #main-site {
        opacity: 0;
        visibility: hidden;
        transition: opacity 1.2s ease;
    }

    #main-site.visible {
        opacity: 1;
        visibility: visible;
    }

    .main-paper {
        position: relative;
        min-height: 100vh;
        padding: 20px 13px 50px;
        background:
            radial-gradient(ellipse at top, rgba(255,255,255,.8), transparent 65%),
            url("/static/textures/pearl-paper.jpg"),
            var(--pearl);
        background-size: cover;
        background-attachment: fixed;
    }

    .main-paper::before {
        content: "";
        position: fixed;
        z-index: 0;
        inset: 8px;
        border: 1px solid rgba(184,138,66,.5);
        border-radius: 24px;
        pointer-events: none;
    }

    .main-paper::after {
        content: "✧";
        position: fixed;
        z-index: 0;
        top: 12%;
        left: 5%;
        color: rgba(184,138,66,.15);
        font-size: 80px;
        pointer-events: none;
        animation: slowRotate 24s linear infinite;
    }

    .content {
        position: relative;
        z-index: 1;
        width: min(100%, 900px);
        margin: auto;
    }

    .section {
        position: relative;
        padding: clamp(28px, 6vw, 58px) clamp(17px, 5vw, 45px);
        margin: 25px auto;
        overflow: hidden;
        border-radius: 28px;
        background: rgba(251,245,233,.82);
        backdrop-filter: blur(8px);
    }

    .section::after {
        content: "❦";
        position: absolute;
        left: 15px;
        bottom: 5px;
        color: rgba(184,138,66,.14);
        font-size: 75px;
        transform: rotate(-25deg);
        pointer-events: none;
    }

    .section-title {
        text-align: center;
        color: var(--wine);
        font-size: clamp(21px, 5vw, 31px);
        font-weight: 700;
        margin: 0 0 12px;
    }

    .section-subtitle {
        text-align: center;
        color: var(--muted);
        font-size: 14px;
        line-height: 2.2;
    }

    .hero {
        text-align: center;
        padding-top: 65px;
        padding-bottom: 55px;
        background:
            radial-gradient(ellipse at top, rgba(255,255,255,.95), transparent 80%),
            url("/static/textures/pearl-paper.jpg"),
            var(--paper);
    }

    .hero-kicker {
        color: var(--gold);
        font-size: 14px;
        letter-spacing: 2px;
    }

    .hero-names {
        margin: 20px 0 5px;
        color: var(--wine);
        font-size: clamp(42px, 10vw, 75px);
        line-height: 1.8;
        text-shadow: 0 3px 1px rgba(184,138,66,.12);
    }

    .hero-and {
        color: var(--gold);
        font-size: 26px;
        margin: 0 8px;
    }

    .hero-description {
        color: var(--muted);
        line-height: 2.4;
        max-width: 600px;
        margin: 15px auto;
        font-size: 15px;
    }

    .hero-flower {
        font-size: 25px;
        color: var(--gold);
        margin-top: 12px;
    }

    /* =====================================================
       کارت تاریخ
    ===================================================== */

    .date-card {
        width: min(100%, 410px);
        margin: 28px auto 0;
        padding: 25px 20px;
        text-align: center;
        background: linear-gradient(145deg, #fffaf0, #eadbc1);
        border: 1px solid var(--gold);
        border-radius: 25px;
        box-shadow: 0 15px 35px rgba(80,20,38,.12);
        transform-style: preserve-3d;
        transition: transform .6s ease;
    }

    .date-card:hover {
        transform: perspective(800px) rotateX(3deg) rotateY(-3deg);
    }

    .date-card .weekday {
        color: var(--ruby);
        font-size: 17px;
    }

    .date-card .date-number {
        color: var(--wine);
        font-size: 55px;
        line-height: 1.5;
        font-weight: 800;
        text-shadow: 0 3px 0 rgba(184,138,66,.16);
    }

    .date-card .month {
        color: var(--gold);
        font-size: 20px;
        font-weight: 600;
    }

    .date-card .time {
        color: var(--muted);
        margin-top: 10px;
        font-size: 15px;
    }

    /* =====================================================
       شمارش معکوس و مه تعاملی
    ===================================================== */

    .countdown-card {
        position: relative;
        width: min(100%, 680px);
        margin: 28px auto 0;
        padding: 25px 15px 30px;
        border-radius: 25px;
        background:
            linear-gradient(145deg, #fff9ed, #e9d8bd);
        border: 1px solid var(--gold);
        box-shadow: 0 15px 35px rgba(80,20,38,.12);
        overflow: hidden;
    }

    .countdown-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 8px;
        direction: rtl;
    }

    .count-unit {
        padding: 13px 3px;
        border: 1px solid rgba(184,138,66,.45);
        border-radius: 17px;
        background: rgba(255,255,255,.5);
    }

    .count-number {
        display: block;
        font-size: clamp(22px, 6vw, 37px);
        font-weight: 800;
        color: var(--wine);
        font-variant-numeric: tabular-nums;
    }

    .count-label {
        display: block;
        color: var(--muted);
        font-size: 12px;
        margin-top: 4px;
    }

    .fog-wrap {
        position: relative;
        margin-top: 22px;
        border-radius: 18px;
        overflow: hidden;
        border: 1px solid rgba(184,138,66,.55);
        min-height: 112px;
        background: linear-gradient(145deg, #f8edda, #e8d4b5);
        touch-action: pan-y;
    }

    .fog-message {
        min-height: 112px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        text-align: center;
        padding: 18px;
        color: var(--wine);
        line-height: 2.1;
    }

    .fog-message strong {
        font-size: 18px;
    }

    .fog-message span {
        font-size: 12px;
        color: var(--muted);
    }

    #fog-canvas {
        position: absolute;
        inset: 0;
        z-index: 3;
        width: 100%;
        height: 100%;
        display: block;
        cursor: crosshair;
        touch-action: pan-y;
    }

    .fog-instruction {
        position: absolute;
        z-index: 4;
        bottom: 7px;
        left: 0;
        right: 0;
        text-align: center;
        font-size: 10px;
        color: rgba(80,20,38,.72);
        pointer-events: none;
        text-shadow: 0 1px 3px white;
    }

    /* =====================================================
       گالری عکس
    ===================================================== */

    .gallery-grid {
        display: grid;
        grid-template-columns: 1fr;
        gap: 23px;
        margin-top: 28px;
    }

    .gallery-item {
        position: relative;
        overflow: hidden;
        padding: 10px;
        border-radius: 23px;
        background: linear-gradient(145deg, #f9f0df, #d9c19a);
        border: 1px solid var(--gold);
        box-shadow:
            0 14px 30px rgba(40,21,27,.16),
            inset 0 0 0 3px rgba(255,255,255,.45);
        cursor: pointer;
        transition: transform .5s ease, box-shadow .5s ease;
    }

    .gallery-item:hover {
        transform: translateY(-6px) scale(1.01);
        box-shadow: 0 22px 40px rgba(40,21,27,.2);
    }

    .gallery-item img {
        display: block;
        width: 100%;
        aspect-ratio: 4 / 3;
        max-height: 620px;
        object-fit: cover;
        border-radius: 16px;
        border: 1px solid rgba(184,138,66,.5);
        background: #e8d9c2;
    }

    .gallery-item::after {
        content: "✧";
        position: absolute;
        top: 15px;
        right: 18px;
        color: #f4dfae;
        font-size: 25px;
        text-shadow: 0 2px 8px rgba(0,0,0,.5);
        pointer-events: none;
    }

    .gallery-caption {
        text-align: center;
        color: var(--wine);
        padding: 12px 5px 4px;
        font-size: 13px;
    }

    #lightbox {
        position: fixed;
        z-index: 11000;
        inset: 0;
        display: none;
        align-items: center;
        justify-content: center;
        padding: 15px;
        background: rgba(20,8,13,.94);
        backdrop-filter: blur(8px);
    }

    #lightbox.show {
        display: flex;
    }

    #lightbox img {
        max-width: 100%;
        max-height: 85vh;
        object-fit: contain;
        border-radius: 18px;
        border: 2px solid var(--gold);
        box-shadow: 0 15px 60px rgba(0,0,0,.5);
    }

    .lightbox-close {
        position: absolute;
        top: 20px;
        left: 20px;
        width: 44px;
        height: 44px;
        border-radius: 50%;
        border: 1px solid var(--gold);
        color: var(--gold-light);
        background: var(--wine);
        font-size: 24px;
    }

    /* =====================================================
       ویدئو
    ===================================================== */

    .video-frame {
        padding: 10px;
        margin-top: 25px;
        border-radius: 23px;
        border: 1px solid var(--gold);
        background: linear-gradient(145deg, #f8edda, #d9c19a);
        box-shadow: 0 15px 35px rgba(40,21,27,.13);
    }

    .video-frame video {
        width: 100%;
        display: block;
        max-height: 600px;
        border-radius: 16px;
        background: #1b1014;
    }

    /* =====================================================
       آدرس و نقشه
    ===================================================== */

    .address-card {
        position: relative;
        text-align: center;
        padding: 28px 18px;
        margin-top: 25px;
        border: 1px solid var(--gold);
        border-radius: 23px;
        background:
            linear-gradient(145deg, rgba(255,255,255,.65), rgba(220,201,168,.4));
        box-shadow: 0 12px 28px rgba(40,21,27,.1);
    }

    .address-icon {
        color: var(--gold);
        font-size: 35px;
    }

    .address-text {
        color: var(--wine);
        line-height: 2.4;
        margin: 10px 0 20px;
        font-size: 15px;
    }

    .gold-button {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        min-height: 48px;
        padding: 11px 24px;
        border-radius: 30px;
        border: 1px solid #d6b66e;
        color: #fff6e6;
        text-decoration: none;
        background: linear-gradient(135deg, #762b40, #501426);
        box-shadow:
            0 6px 15px rgba(80,20,38,.2),
            inset 0 1px 0 rgba(255,255,255,.2);
        transition: transform .3s ease, box-shadow .3s ease;
    }

    .gold-button:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 22px rgba(80,20,38,.28);
    }

    /* =====================================================
       فرم پاسخ به دعوت‌نامه
    ===================================================== */

    .rsvp-form {
        width: min(100%, 550px);
        margin: 25px auto 0;
        padding: 22px;
        border-radius: 24px;
        border: 1px solid var(--gold);
        background: linear-gradient(145deg, #fffaf0, #eadbc1);
        box-shadow: 0 14px 30px rgba(40,21,27,.12);
    }

    .form-group {
        margin-bottom: 17px;
    }

    .form-group label {
        display: block;
        color: var(--wine);
        font-size: 14px;
        margin-bottom: 8px;
    }

    .form-control {
        display: block;
        width: 100%;
        min-height: 49px;
        border: 1px solid rgba(184,138,66,.65);
        border-radius: 14px;
        padding: 10px 13px;
        outline: none;
        background: rgba(255,255,255,.78);
        color: var(--ink);
        transition: border-color .25s, box-shadow .25s;
    }

    .form-control:focus {
        border-color: var(--wine);
        box-shadow: 0 0 0 3px rgba(184,138,66,.16);
    }

    .rsvp-submit {
        width: 100%;
        min-height: 52px;
        border: 1px solid var(--gold-light);
        border-radius: 30px;
        color: #fff7e8;
        font-weight: 700;
        background: linear-gradient(135deg, #762b40, #501426);
        box-shadow: 0 8px 20px rgba(80,20,38,.2);
        transition: transform .25s ease;
    }

    .rsvp-submit:hover {
        transform: translateY(-2px);
    }

    .flash-message {
        padding: 13px;
        margin: 15px 0;
        text-align: center;
        border-radius: 15px;
        color: var(--wine);
        border: 1px solid var(--gold);
        background: #f8edd8;
        line-height: 2;
    }

    /* =====================================================
       پایان صفحه
    ===================================================== */

    .footer {
        text-align: center;
        padding: 35px 10px 15px;
        color: var(--muted);
        line-height: 2.4;
        font-size: 13px;
    }

    .footer-heart {
        color: var(--ruby);
        font-size: 22px;
    }

    /* =====================================================
       افکت ورود بخش‌ها
    ===================================================== */

    .reveal {
        opacity: 0;
        transform: translateY(35px);
        transition:
            opacity .9s ease,
            transform .9s cubic-bezier(.2,.7,.2,1);
    }

    .reveal.visible {
        opacity: 1;
        transform: translateY(0);
    }

    .sparkle {
        position: fixed;
        z-index: 2;
        pointer-events: none;
        width: 4px;
        height: 4px;
        border-radius: 50%;
        background: var(--gold);
        box-shadow: 0 0 10px 3px rgba(184,138,66,.3);
        animation: sparkleFloat 7s linear infinite;
        opacity: .45;
    }

    /* =====================================================
       انیمیشن‌ها
    ===================================================== */

    @keyframes glowPulse {
        0%, 100% { transform: scale(.9); opacity: .5; }
        50% { transform: scale(1.1); opacity: 1; }
    }

    @keyframes sealFloat {
        0%, 100% { transform: translateY(0) rotate(-2deg); }
        50% { transform: translateY(-8px) rotate(2deg); }
    }

    @keyframes hintPulse {
        0%, 100% { opacity: .55; }
        50% { opacity: 1; }
    }

    @keyframes envelopeDisappear {
        to {
            opacity: 0;
            visibility: hidden;
        }
    }

    @keyframes slowRotate {
        to { transform: rotate(335deg); }
    }

    @keyframes sparkleFloat {
        0% {
            transform: translateY(0) scale(.5);
            opacity: 0;
        }
        20% { opacity: .55; }
        80% { opacity: .35; }
        100% {
            transform: translateY(-100vh) scale(1.3);
            opacity: 0;
        }
    }

    /* =====================================================
       نمایشگرهای بزرگ‌تر
    ===================================================== */

    @media (min-width: 650px) {
        .main-paper {
            padding: 35px 25px 70px;
        }

        .gallery-grid {
            grid-template-columns: repeat(2, minmax(0, 1fr));
        }

        .gallery-item img {
            aspect-ratio: 4 / 3;
        }

        .section {
            margin: 35px auto;
        }
    }

    @media (max-width: 380px) {
        .countdown-grid {
            gap: 5px;
        }

        .count-unit {
            padding: 10px 2px;
        }

        .count-label {
            font-size: 10px;
        }

        .wax-seal {
            width: 115px;
            height: 115px;
        }
    }

    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            scroll-behavior: auto !important;
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: .01ms !important;
        }

        .reveal {
            opacity: 1;
            transform: none;
        }
    }
    </style>
</head>

<body class="locked">

    <!-- =================================================
         پاکت دعوت‌نامه
    ================================================== -->

    <div id="envelope-screen">
        <div class="envelope-glow"></div>

        <div class="envelope">
            <div class="envelope-paper"></div>
            <div class="envelope-inner-border"></div>
            <div class="envelope-bottom"></div>
            <div class="envelope-flap"></div>

            <div class="envelope-center">
                <div class="envelope-label nastaliq">
                    دعوت‌نامه‌ای از جنس عشق
                </div>

                <button
                    class="wax-seal"
                    id="open-envelope"
                    type="button"
                    aria-label="باز کردن دعوت‌نامه">
                </button>

                <div class="open-hint">
                    برای گشودن دعوت‌نامه لمس کنید
                </div>
            </div>
        </div>
    </div>

    <!-- =================================================
         محتوای اصلی سایت
    ================================================== -->

    <main id="main-site">
        <div class="main-paper">
            <div class="content">

                <!-- معرفی -->
                <section class="section gold-frame hero reveal">
                    <span class="corner-decoration top-right"></span>
                    <span class="corner-decoration top-left"></span>
                    <span class="corner-decoration bottom-right"></span>
                    <span class="corner-decoration bottom-left"></span>

                    <div class="hero-kicker">
                        به نام عشق و آغاز یک زندگی
                    </div>

                    <h1 class="hero-names nastaliq">
                        {{ groom }}
                        <span class="hero-and">&</span>
                        {{ bride }}
                    </h1>

                    <img
                        class="ornament-divider"
                        src="/static/ornaments/floral-divider.png"
                        alt=""
                        onerror="this.style.display='none'">

                    <p class="hero-description">
                        با قلبی سرشار از شادی، آغاز فصل تازه‌ای از
                        زندگی‌مان را جشن می‌گیریم و حضور گرم شما را
                        در این لحظه زیبا و به‌یادماندنی گرامی می‌داریم.
                    </p>

                    <div class="hero-flower">❦ ✧ ❦</div>
                </section>

                <!-- تاریخ و ساعت -->
                <section class="section gold-frame reveal">
                    <h2 class="section-title nastaliq">
                        قرار عاشقانه ما
                    </h2>

                    <p class="section-subtitle">
                        روزی که دوست داریم در کنار شما به خاطره تبدیل شود
                    </p>

                    <div class="date-card">
                        <div class="weekday">چهارشنبه</div>
                        <div class="date-number">۲</div>
                        <div class="month">دی‌ماه ۱۴۰۵</div>
                        <div class="time">از ساعت ۱۹:۰۰ تا ۲۲:۰۰</div>
                    </div>
                </section>

                <!-- شمارش معکوس -->
                <section class="section gold-frame reveal">
                    <h2 class="section-title nastaliq">
                        تا دیدارمان
                    </h2>

                    <p class="section-subtitle">
                        لحظه‌ها را می‌شماریم تا به جشن کنار هم بودن برسیم
                    </p>

                    <div class="countdown-card">
                        <div class="countdown-grid" id="countdown">
                            <div class="count-unit">
                                <span class="count-number" id="days">۰۰</span>
                                <span class="count-label">روز</span>
                            </div>

                            <div class="count-unit">
                                <span class="count-number" id="hours">۰۰</span>
                                <span class="count-label">ساعت</span>
                            </div>

                            <div class="count-unit">
                                <span class="count-number" id="minutes">۰۰</span>
                                <span class="count-label">دقیقه</span>
                            </div>

                            <div class="count-unit">
                                <span class="count-number" id="seconds">۰۰</span>
                                <span class="count-label">ثانیه</span>
                            </div>
                        </div>

                        <div class="fog-wrap" id="fog-wrap">
                            <div class="fog-message">
                                <strong class="nastaliq">
                                    قرار عاشقانه ما
                                </strong>
                                <span>
                                    تاریخ دیدارمان را با لمس مه آشکار کن
                                </span>
                            </div>

                            <canvas id="fog-canvas"></canvas>

                            <div class="fog-instruction">
                                انگشتت را روی مه حرکت بده
                            </div>
                        </div>
                    </div>
                </section>

                <!-- گالری -->
                {% if photos %}
                <section class="section gold-frame reveal">
                    <h2 class="section-title nastaliq">
                        قاب‌هایی از خاطره
                    </h2>

                    <p class="section-subtitle">
                        لحظه‌هایی که دوست داریم با شما شریک شویم
                    </p>

                    <div class="gallery-grid">
                        {% for photo in photos %}
                        <div class="gallery-item"
                             onclick="openLightbox('{{ photo }}')">
                            <img src="{{ photo }}"
                                 alt="عکس خاطره"
                                 loading="lazy">
                            <div class="gallery-caption">
                                ✧ لحظه‌ای برای همیشه ✧
                            </div>
                        </div>
                        {% endfor %}
                    </div>
                </section>
                {% endif %}

                <!-- ویدئو -->
                {% if video_exists %}
                <section class="section gold-frame reveal">
                    <h2 class="section-title nastaliq">
                        لحظه‌های متحرک ما
                    </h2>

                    <p class="section-subtitle">
                        تماشای خاطره‌ها در قاب تصویر
                    </p>

                    <div class="video-frame">
                        <video controls playsinline preload="metadata">
                            <source src="/static/wedding.mp4" type="video/mp4">
                            مرورگر شما از پخش ویدئو پشتیبانی نمی‌کند.
                        </video>
                    </div>
                </section>
                {% endif %}

                <!-- آدرس -->
                <section class="section gold-frame reveal">
                    <h2 class="section-title nastaliq">
                        نشانی جشن ما
                    </h2>

                    <p class="section-subtitle">
                        خوشحال می‌شویم مسیر شادی‌مان را با ما همراه شوید
                    </p>

                    <div class="address-card">
                        <div class="address-icon">⌖</div>

                        <div class="address-text">
                            {{ address }}
                        </div>

                        <a class="gold-button"
                           href="{{ map_url }}"
                           target="_blank"
                           rel="noopener">
                            مشاهده مسیر روی نقشه
                            <span>✧</span>
                        </a>
                    </div>
                </section>

                <!-- پاسخ به دعوت‌نامه -->
                <section class="section gold-frame reveal">
                    <h2 class="section-title nastaliq">
                        پاسخ به دعوت‌نامه
                    </h2>

                    <p class="section-subtitle">
                        لطفاً حضور یا عدم حضورتان را به ما اطلاع دهید
                    </p>

                    {% if message %}
                    <div class="flash-message">
                        {{ message }}
                    </div>
                    {% endif %}

                    <form class="rsvp-form" method="POST" action="/">
                        <div class="form-group">
                            <label for="guest-name">نام و نام خانوادگی</label>
                            <input
                                class="form-control"
                                type="text"
                                id="guest-name"
                                name="name"
                                maxlength="80"
                                required
                                placeholder="نام شما">
                        </div>

                        <div class="form-group">
                            <label for="guest-count">تعداد نفرات</label>
                            <select
                                class="form-control"
                                id="guest-count"
                                name="count"
                                required>
                                <option value="1">۱ نفر</option>
                                <option value="2">۲ نفر</option>
                                <option value="3">۳ نفر</option>
                                <option value="4">۴ نفر</option>
                                <option value="5">۵ نفر</option>
                                <option value="6">۶ نفر</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="attendance">وضعیت حضور</label>
                            <select
                                class="form-control"
                                id="attendance"
                                name="attendance"
                                required>
                                <option value="حضور دارم">با افتخار می‌آیم</option>
                                <option value="متأسفانه نمی‌توانم بیایم">
                                    متأسفانه امکان حضور ندارم
                                </option>
                            </select>
                        </div>

                        <button class="rsvp-submit" type="submit">
                            ثبت پاسخ و ارسال
                            ✧
                        </button>
                    </form>
                </section>

                <!-- پایان -->
                <footer class="footer reveal">
                    <div class="small-flower">❦ ✧ ❦</div>

                    <div class="nastaliq"
                         style="font-size:30px;color:var(--wine)">
                        چشم‌انتظار دیدار شما هستیم
                    </div>

                    <div>
                        با مهر، {{ groom }} و {{ bride }}
                    </div>

                    <div class="footer-heart">♥</div>
                </footer>

            </div>
        </div>
    </main>

    <!-- نمایش بزرگ عکس -->
    <div id="lightbox" onclick="closeLightbox()">
        <button class="lightbox-close"
                type="button"
                aria-label="بستن"
                onclick="closeLightbox()">×</button>

        <img id="lightbox-image" src="" alt="نمایش عکس">
    </div>

    <!-- موسیقی -->
    {% if music_exists %}
    <audio id="background-music"
           src="/static/music.mp3"
           loop
           preload="auto"></audio>
    {% endif %}

    <script>
    /* =====================================================
       باز کردن پاکت
    ===================================================== */

    const envelopeScreen = document.getElementById("envelope-screen");
    const openEnvelopeButton = document.getElementById("open-envelope");
    const mainSite = document.getElementById("main-site");

    let envelopeOpened = false;

    function openEnvelope() {
        if (envelopeOpened) return;
        envelopeOpened = true;

        envelopeScreen.classList.add("opening");

        const music = document.getElementById("background-music");
        if (music) {
            music.volume = 0.45;
            const playPromise = music.play();

            if (playPromise && typeof playPromise.catch === "function") {
                playPromise.catch(() => {});
            }
        }

        window.setTimeout(() => {
            envelopeScreen.classList.add("hidden");
            mainSite.classList.add("visible");
            document.body.classList.remove("locked");
            startReveal();
        }, 1700);
    }

    openEnvelopeButton.addEventListener("click", openEnvelope);

    /* =====================================================
       شمارش معکوس
    ===================================================== */

    const weddingTime = new Date(
        {{ countdown_date | tojson }}
    ).getTime();

    const digits = value =>
        String(value).padStart(2, "0")
        .replace(/\d/g, d => "۰۱۲۳۴۵۶۷۸۹"[Number(d)]);

    function updateCountdown() {
        const now = Date.now();
        let difference = weddingTime - now;

        if (difference < 0) difference = 0;

        const days = Math.floor(difference / 86400000);
        const hours = Math.floor((difference % 86400000) / 3600000);
        const minutes = Math.floor((difference % 3600000) / 60000);
        const seconds = Math.floor((difference % 60000) / 1000);

        document.getElementById("days").textContent = digits(days);
        document.getElementById("hours").textContent = digits(hours);
        document.getElementById("minutes").textContent = digits(minutes);
        document.getElementById("seconds").textContent = digits(seconds);
    }

    updateCountdown();
    window.setInterval(updateCountdown, 1000);

    /* =====================================================
       مه تعاملی شمارش معکوس
       پوشش کاملاً مات؛ پاک شدن فقط زیر انگشت
    ===================================================== */

    const fogCanvas = document.getElementById("fog-canvas");
    const fogWrap = document.getElementById("fog-wrap");
    const fogContext = fogCanvas.getContext("2d", {
        alpha: true,
        desynchronized: true
    });

    let fogWidth = 0;
    let fogHeight = 0;
    let isErasingFog = false;
    let lastFogPoint = null;

    function drawFog() {
        if (!fogCanvas || !fogContext || !fogWrap) return;

        const rect = fogWrap.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, 2);

        fogWidth = rect.width;
        fogHeight = rect.height;

        fogCanvas.width = Math.max(1, Math.round(fogWidth * dpr));
        fogCanvas.height = Math.max(1, Math.round(fogHeight * dpr));

        fogCanvas.style.width = fogWidth + "px";
        fogCanvas.style.height = fogHeight + "px";

        fogContext.setTransform(dpr, 0, 0, dpr, 0, 0);
        fogContext.globalCompositeOperation = "source-over";

        // مه کاملاً مات است و متن از زیر آن دیده نمی‌شود.
        fogContext.fillStyle = "#e7d6ba";
        fogContext.fillRect(0, 0, fogWidth, fogHeight);

        // بافت ظریف روی مه
        const gradient = fogContext.createLinearGradient(
            0, 0, fogWidth, fogHeight
        );

        gradient.addColorStop(0, "rgba(255,250,238,0.22)");
        gradient.addColorStop(1, "rgba(184,138,66,0.12)");

        fogContext.fillStyle = gradient;
        fogContext.fillRect(0, 0, fogWidth, fogHeight);

        // لبه ظریف
        fogContext.strokeStyle = "rgba(184,138,66,0.28)";
        fogContext.lineWidth = 1;
        fogContext.strokeRect(0.5, 0.5, fogWidth - 1, fogHeight - 1);

        fogContext.globalCompositeOperation = "destination-out";
    }

    function eraseFogAt(x, y) {
        if (!fogContext) return;

        const radius = 22;

        fogContext.save();
        fogContext.globalCompositeOperation = "destination-out";

        const gradient = fogContext.createRadialGradient(
            x, y, 2,
            x, y, radius
        );

        gradient.addColorStop(0, "rgba(0,0,0,1)");
        gradient.addColorStop(0.72, "rgba(0,0,0,0.95)");
        gradient.addColorStop(1, "rgba(0,0,0,0)");

        fogContext.fillStyle = gradient;
        fogContext.beginPath();
        fogContext.arc(x, y, radius, 0, Math.PI * 2);
        fogContext.fill();

        if (lastFogPoint) {
            fogContext.lineCap = "round";
            fogContext.lineJoin = "round";
            fogContext.strokeStyle = "rgba(0,0,0,0.9)";
            fogContext.lineWidth = radius * 1.2;
            fogContext.beginPath();
            fogContext.moveTo(lastFogPoint.x, lastFogPoint.y);
            fogContext.lineTo(x, y);
            fogContext.stroke();
        }

        fogContext.restore();
        fogContext.globalCompositeOperation = "destination-out";

        lastFogPoint = { x, y };
    }

    function fogPointerDown(event) {
        if (event.pointerType === "mouse" && event.button !== 0) return;

        isErasingFog = true;
        lastFogPoint = null;

        const rect = fogCanvas.getBoundingClientRect();
        eraseFogAt(
            event.clientX - rect.left,
            event.clientY - rect.top
        );

        if (fogCanvas.setPointerCapture) {
            try {
                fogCanvas.setPointerCapture(event.pointerId);
            } catch (_) {}
        }
    }

    function fogPointerMove(event) {
        if (!isErasingFog) return;

        const rect = fogCanvas.getBoundingClientRect();
        eraseFogAt(
            event.clientX - rect.left,
            event.clientY - rect.top
        );
    }

    function fogPointerUp() {
        isErasingFog = false;
        lastFogPoint = null;
    }

    if (fogCanvas && fogContext) {
        drawFog();

        fogCanvas.addEventListener("pointerdown", fogPointerDown);
        fogCanvas.addEventListener("pointermove", fogPointerMove);
        fogCanvas.addEventListener("pointerup", fogPointerUp);
        fogCanvas.addEventListener("pointercancel", fogPointerUp);
        fogCanvas.addEventListener("lostpointercapture", fogPointerUp);

        let resizeTimer;

        window.addEventListener("resize", () => {
            window.clearTimeout(resizeTimer);
            resizeTimer = window.setTimeout(drawFog, 180);
        });
    }

    /* =====================================================
       نمایش مرحله‌ای بخش‌ها هنگام اسکرول
    ===================================================== */

    function startReveal() {
        const revealItems = document.querySelectorAll(".reveal");

        if (!("IntersectionObserver" in window)) {
            revealItems.forEach(item => item.classList.add("visible"));
            return;
        }

        const observer = new IntersectionObserver((entries, obs) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    obs.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.12,
            rootMargin: "0px 0px -35px 0px"
        });

        revealItems.forEach(item => observer.observe(item));
    }

    /* =====================================================
       گالری و نمایش بزرگ عکس
    ===================================================== */

    const lightbox = document.getElementById("lightbox");
    const lightboxImage = document.getElementById("lightbox-image");

    function openLightbox(src) {
        lightboxImage.src = src;
        lightbox.classList.add("show");
        document.body.style.overflow = "hidden";
    }

    function closeLightbox() {
        lightbox.classList.remove("show");
        document.body.style.overflow = "";
    }

    document.addEventListener("keydown", event => {
        if (event.key === "Escape") {
            closeLightbox();
        }
    });

    /* =====================================================
       ذرات درخشان محدود و سبک
    ===================================================== */

    function createSparkles() {
        if (window.matchMedia &&
            window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
            return;
        }

        const count = window.innerWidth < 600 ? 7 : 12;

        for (let i = 0; i < count; i++) {
            const sparkle = document.createElement("span");
            sparkle.className = "sparkle";

            sparkle.style.left = (Math.random() * 100) + "%";
            sparkle.style.top = (Math.random() * 100) + "%";
            sparkle.style.animationDelay = (Math.random() * 7) + "s";
            sparkle.style.animationDuration =
                (6 + Math.random() * 6) + "s";

            document.body.appendChild(sparkle);
        }
    }

    createSparkles();

    </script>
</body>
</html>
"""


# -------------------- مسیر اصلی سایت --------------------

@app.route("/", methods=["GET", "POST"])
def home():
    message = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        count = request.form.get("count", "1").strip()
        attendance = request.form.get("attendance", "").strip()

        allowed_counts = {"1", "2", "3", "4", "5", "6"}
        allowed_attendance = {
            "حضور دارم",
            "متأسفانه نمی‌توانم بیایم",
        }

        if not name or len(name) > 80:
            message = "لطفاً نام خود را به‌درستی وارد کنید."

        elif count not in allowed_counts:
            message = "تعداد نفرات انتخاب‌شده معتبر نیست."

        elif attendance not in allowed_attendance:
            message = "لطفاً وضعیت حضور را انتخاب کنید."

        else:
            try:
                save_guest(name, count, attendance)

                safe_name = html.escape(name)

                telegram_message = (
                    "💌 پاسخ جدید دعوت‌نامه عروسی\n\n"
                    f"نام: {safe_name}\n"
                    f"تعداد نفرات: {count}\n"
                    f"وضعیت: {attendance}"
                )

                send_telegram_message(telegram_message)

                message = "پاسخ شما با موفقیت ثبت شد. از همراهی شما سپاسگزاریم."

            except Exception:
                app.logger.exception("Could not save RSVP")
                message = "ثبت پاسخ با مشکل روبه‌رو شد. لطفاً دوباره تلاش کنید."

    photos = existing_static_files(PHOTO_NAMES)

    return render_template_string(
        PAGE,
        groom=GROOM,
        bride=BRIDE,
        address=ADDRESS,
        map_url=MAP_URL,
        countdown_date=COUNTDOWN_DATE,
        photos=photos,
        video_exists=VIDEO_EXISTS,
        music_exists=MUSIC_EXISTS,
        message=message,
    )


# -------------------- اجرای محلی --------------------

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )