
from flask import Flask, request
from pathlib import Path
from datetime import datetime
import csv
import html
import os
import urllib.request
import urllib.parse

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
FONT_DIR = STATIC_DIR / "fonts"
GUESTS_FILE = BASE_DIR / "guests.csv"

STATIC_DIR.mkdir(exist_ok=True)
FONT_DIR.mkdir(exist_ok=True)

WEDDING_DATE = "چهارشنبه ۲ دی ۱۴۰۵"
ADDRESS = "سمنان، میدان معلم، بلوار بسیج، جنب ورزشگاه الغدیر، تالار پذیرایی فریال"

MAP_URL = (
    "https://www.google.com/maps/dir/?api=1"
    "&destination=35.5868900%2C53.3861140"
    "&travelmode=driving&dir_action=navigate"
)


def send_telegram_message(name, count, attendance):
    token = os.environ.get("BOT_TOKEN")
    chat_id = os.environ.get("ADMIN_CHAT_ID")

    if not token or not chat_id:
        return

    message = (
        "💌 پاسخ جدید دعوت عروسی\n\n"
        f"👤 نام: {name}\n"
        f"👥 تعداد همراهان: {count}\n"
        f"📩 وضعیت حضور: {attendance}"
    )

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message
    }).encode("utf-8")

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10):
            pass
    except Exception as error:
        print("Telegram error:", error)


PAGE = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#efe2c9">
<meta name="description" content="دعوت‌نامه عروسی امیر و زهرا">
<title>عروسی امیر و زهرا</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
@font-face {
    font-family: "IranNastaliq";
    src: url("/static/fonts/IranNastaliq.ttf") format("truetype");
    font-weight: normal;
    font-style: normal;
    font-display: swap;
}

:root {
    --paper: #efe2c9;
    --paper-light: #fbf5e9;
    --paper-dark: #ddc9a5;
    --gold: #bd9852;
    --gold-light: #e8ce96;
    --gold-dark: #80602e;
    --wine: #762f40;
    --wine-dark: #4c1c2a;
    --ink: #49382d;
    --muted: #89745e;
}

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
    background: var(--paper);
}

body {
    margin: 0;
    overflow-x: hidden;
    color: var(--ink);
    font-family: "Vazirmatn", Tahoma, sans-serif;
    background:
        radial-gradient(ellipse at 12% 8%, rgba(255,255,255,.55), transparent 42%),
        radial-gradient(ellipse at 90% 85%, rgba(185,149,85,.12), transparent 40%),
        var(--paper);
}

body.locked {
    overflow: hidden;
}

button, input, select {
    font: inherit;
}

.nastaliq {
    font-family: "IranNastaliq", "Noto Nastaliq Urdu", serif;
    font-weight: normal;
    line-height: 2.2;
    padding-top: 5px;
}

.paper-texture {
    background-color: var(--paper-light);
    background-image:
        radial-gradient(rgba(111,77,39,.07) .6px, transparent .7px),
        radial-gradient(rgba(255,255,255,.4) .7px, transparent .8px),
        linear-gradient(135deg, rgba(255,255,255,.2), rgba(151,111,55,.035));
    background-size: 8px 8px, 13px 13px, 100% 100%;
}

.ornament {
    text-align: center;
    color: var(--gold-dark);
    font-size: 25px;
    letter-spacing: 8px;
    margin: 20px 0;
    text-shadow: 0 2px 8px rgba(189,152,82,.2);
}

/* =================================
   پاکت دعوت‌نامه
================================= */

#intro {
    position: fixed;
    inset: 0;
    z-index: 1000;
    width: 100%;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    perspective: 1500px;
    background: #e8d8bc;
    transition: opacity 1s ease, visibility 1s ease;
}

#intro.hidden {
    opacity: 0;
    visibility: hidden;
    pointer-events: none;
}

.envelope {
    position: absolute;
    inset: 0;
    overflow: hidden;
    transform-style: preserve-3d;
    background:
        radial-gradient(ellipse at 50% 40%, rgba(255,255,255,.55), transparent 65%),
        linear-gradient(145deg, #f8efdf, #e4d0ad);
}

.envelope::before {
    content: "";
    position: absolute;
    inset: 11px;
    border: 1px solid rgba(164,125,57,.85);
    box-shadow:
        inset 0 0 0 4px rgba(255,255,255,.2),
        inset 0 0 18px rgba(164,125,57,.12);
    z-index: 9;
    pointer-events: none;
    border-radius: 7px;
}

.envelope::after {
    content: "";
    position: absolute;
    inset: 19px;
    border: 1px solid rgba(164,125,57,.35);
    z-index: 9;
    pointer-events: none;
    border-radius: 5px;
}

.envelope-paper {
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 50% 45%, rgba(255,255,255,.38), transparent 65%),
        repeating-linear-gradient(0deg, transparent 0 5px, rgba(110,80,40,.018) 6px);
}

.intro-writing {
    position: absolute;
    z-index: 4;
    top: 20%;
    left: 8%;
    right: 8%;
    text-align: center;
    color: var(--gold-dark);
}

.intro-small {
    font-size: 14px;
    letter-spacing: 2px;
}

.intro-title {
    font-size: clamp(52px, 14vw, 78px);
    color: var(--wine);
    margin: 28px 0 12px;
    text-shadow: 0 4px 15px rgba(118,47,64,.12);
}

.intro-subtitle {
    font-size: 14px;
    color: #806b56;
}

.envelope-fold-left,
.envelope-fold-right {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 72%;
    background: linear-gradient(145deg, #f5ead6, #e3cfad);
    z-index: 2;
}

.envelope-fold-left {
    left: 0;
    clip-path: polygon(0 0, 100% 100%, 0 100%);
    filter: drop-shadow(4px -3px 8px rgba(80,50,20,.12));
}

.envelope-fold-right {
    right: 0;
    clip-path: polygon(100% 0, 100% 100%, 0 100%);
    filter: drop-shadow(-4px -3px 8px rgba(80,50,20,.12));
}

.envelope-bottom {
    position: absolute;
    inset: auto 0 0;
    height: 72%;
    background: linear-gradient(160deg, #ead9bc, #d9c29b);
    clip-path: polygon(0 100%, 50% 0, 100% 100%);
    z-index: 3;
    filter: drop-shadow(0 -5px 9px rgba(80,50,20,.12));
}

.envelope-flap {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 57%;
    background: linear-gradient(160deg, #fbf4e7, #e8d6b7);
    clip-path: polygon(0 0, 100% 0, 50% 100%);
    transform-origin: top center;
    z-index: 6;
    transition: transform 1.65s cubic-bezier(.68,-.08,.22,1);
    filter: drop-shadow(0 8px 7px rgba(75,48,20,.15));
}

/* مهر مومی ساده و بدون نوشته */
.seal-button {
    position: absolute;
    z-index: 10;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 122px;
    height: 122px;
    padding: 0;
    border: 0;
    border-radius: 48% 52% 47% 53% / 52% 46% 54% 48%;
    background:
        radial-gradient(ellipse at 33% 25%, rgba(255,255,255,.2), transparent 25%),
        radial-gradient(ellipse at 70% 75%, rgba(30,0,10,.3), transparent 35%),
        radial-gradient(circle at 42% 38%, #963f50 0%, #762b3c 53%, #4e1b29 100%);
    box-shadow:
        0 10px 20px rgba(67,24,32,.32),
        inset 0 3px 7px rgba(255,255,255,.18),
        inset 0 -7px 10px rgba(30,0,10,.3);
    outline: 1px solid #bd9852;
    outline-offset: 6px;
    cursor: pointer;
    animation: sealGlow 3s ease-in-out infinite;
}

.seal-button::before {
    content: "";
    position: absolute;
    inset: 9px;
    border: 1px solid rgba(224,185,142,.3);
    border-radius: inherit;
    box-shadow: inset 0 0 8px rgba(35,0,10,.2);
}

@keyframes sealGlow {
    0%, 100% {
        box-shadow:
            0 10px 20px rgba(67,24,32,.32),
            inset 0 3px 7px rgba(255,255,255,.18),
            inset 0 -7px 10px rgba(30,0,10,.3);
    }
    50% {
        box-shadow:
            0 12px 25px rgba(67,24,32,.4),
            inset 0 3px 7px rgba(255,255,255,.2),
            inset 0 -7px 10px rgba(30,0,10,.3),
            0 0 24px rgba(189,152,82,.3);
    }
}

.open-hint {
    position: absolute;
    z-index: 8;
    top: calc(55% + 112px);
    left: 0;
    right: 0;
    text-align: center;
    color: var(--gold-dark);
    font-size: 12px;
    animation: breathe 2s infinite;
}

@keyframes breathe {
    0%,100% { opacity: .55; transform: translateY(0); }
    50% { opacity: 1; transform: translateY(-4px); }
}

#intro.opening .envelope-flap {
    transform: rotateX(180deg);
}

#intro.opening .seal-button {
    opacity: 0;
    pointer-events: none;
    transform: translate(-50%, -50%) scale(1.5);
}

#intro.opening .envelope-fold-left {
    animation: foldLeft 1.5s .45s forwards;
}

#intro.opening .envelope-fold-right {
    animation: foldRight 1.5s .45s forwards;
}

#intro.opening .envelope-bottom {
    animation: foldBottom 1.5s .45s forwards;
}

@keyframes foldLeft {
    to { transform: translateX(-110%) rotateY(-30deg); opacity: .2; }
}

@keyframes foldRight {
    to { transform: translateX(110%) rotateY(30deg); opacity: .2; }
}

@keyframes foldBottom {
    to { transform: translateY(110%) rotateX(35deg); opacity: .2; }
}

/* =================================
   صفحه اصلی
================================= */

#main-site {
    opacity: 0;
    visibility: hidden;
    transition: opacity 1.2s ease;
}

#main-site.visible {
    opacity: 1;
    visibility: visible;
}

.page-paper {
    position: relative;
    width: min(100%, 780px);
    margin: 0 auto;
    min-height: 100vh;
    overflow: hidden;
    background:
        radial-gradient(ellipse at 10% 5%, rgba(255,255,255,.55), transparent 35%),
        radial-gradient(ellipse at 90% 90%, rgba(189,152,82,.13), transparent 40%),
        repeating-linear-gradient(0deg, transparent 0 7px, rgba(120,85,40,.012) 8px),
        linear-gradient(135deg, #f8efdf, #eee0c5);
    box-shadow: 0 0 45px rgba(70,45,20,.1);
}

.page-paper::before {
    content: "";
    position: absolute;
    inset: 9px;
    border: 1px solid rgba(189,152,82,.75);
    border-radius: 19px;
    pointer-events: none;
    z-index: 10;
}

.page-paper::after {
    content: "";
    position: absolute;
    inset: 17px;
    border: 1px solid rgba(133,100,46,.25);
    border-radius: 15px;
    pointer-events: none;
    z-index: 10;
}

section {
    position: relative;
    padding: 75px 25px;
    text-align: center;
}

section::before,
section::after {
    position: absolute;
    color: rgba(153,113,48,.35);
    font-family: serif;
    font-size: 30px;
    pointer-events: none;
    z-index: 1;
}

section::before {
    content: "❦";
    top: 20px;
    right: 25px;
}

section::after {
    content: "✧";
    bottom: 20px;
    left: 25px;
}

.hero {
    min-height: 94vh;
    min-height: 94dvh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 70px 28px;
}

.hero-kicker {
    font-size: 13px;
    color: var(--muted);
    letter-spacing: 2px;
}

.hero-names {
    font-size: clamp(65px, 16vw, 100px);
    color: var(--wine);
    margin: 5px 0;
    line-height: 1.8;
    text-shadow:
        0 2px 1px rgba(255,255,255,.55),
        0 5px 16px rgba(130,91,36,.12);
}

.hero-and {
    color: var(--gold-dark);
    font-size: 22px;
    margin: -5px 0;
}

.hero-description {
    max-width: 450px;
    font-size: 14px;
    line-height: 2.5;
    color: var(--muted);
    margin-top: 20px;
}

.scroll-cue {
    position: absolute;
    bottom: 32px;
    color: var(--gold-dark);
    font-size: 12px;
    animation: breathe 2s infinite;
}

.section-title {
    font-size: clamp(37px, 9vw, 53px);
    color: var(--wine);
    margin: 0 0 10px;
    text-shadow:
        0 2px 1px rgba(255,255,255,.55),
        0 5px 16px rgba(130,91,36,.12);
}

.section-subtitle {
    color: var(--muted);
    font-size: 13px;
    line-height: 2.3;
}

.divider-ornament {
    display: flex;
    align-items: center;
    gap: 12px;
    justify-content: center;
    color: var(--gold-dark);
    margin: 20px 0 30px;
}

.divider-ornament::before,
.divider-ornament::after {
    content: "";
    height: 1px;
    width: 70px;
    background: linear-gradient(
        90deg,
        transparent,
        #9b773c,
        #e7cb8d,
        #9b773c,
        transparent
    );
    background-size: 200% 100%;
    animation: goldFlow 5s linear infinite;
}

@keyframes goldFlow {
    from { background-position: 100% 0; }
    to { background-position: -100% 0; }
}

.ornate-card,
.address-card,
.rsvp-card {
    position: relative;
    padding: 32px 22px;
    margin: 30px auto;
    max-width: 550px;
    border: 1px solid rgba(185,149,85,.9);
    outline: 1px solid rgba(189,152,82,.22);
    outline-offset: 5px;
    border-radius: 28px;
    background: rgba(255,250,239,.75);
    box-shadow:
        0 12px 30px rgba(70,45,20,.1),
        inset 0 0 20px rgba(189,152,82,.08);
    transition: transform .5s ease, box-shadow .5s ease;
}

.ornate-card::before,
.ornate-card::after {
    content: "✧";
    position: absolute;
    color: var(--gold-dark);
    font-size: 20px;
}

.ornate-card::before {
    top: 10px;
    right: 15px;
}

.ornate-card::after {
    bottom: 10px;
    left: 15px;
}

.ornate-card:hover,
.address-card:hover,
.rsvp-card:hover {
    transform: translateY(-5px);
    box-shadow:
        0 20px 38px rgba(70,45,20,.16),
        inset 0 0 25px rgba(189,152,82,.12);
}

/* =================================
   شمارش معکوس و مه کاملاً مات
================================= */

.countdown-card {
    max-width: 550px;
    margin: 35px auto;
    position: relative;
    padding: 36px 16px 30px;
    overflow: hidden;
    border: 1px solid var(--gold);
    outline: 1px solid rgba(189,152,82,.3);
    outline-offset: 5px;
    border-radius: 30px;
    background: linear-gradient(145deg, #f8f0df, #e9d8b8);
    box-shadow:
        0 12px 28px rgba(80,50,20,.1),
        inset 0 0 20px rgba(189,152,82,.1);
}

.countdown-title {
    font-size: 36px;
    color: var(--wine);
    margin-bottom: 22px;
}

.countdown-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 9px;
    direction: rtl;
}

.time-unit {
    border: 1px solid rgba(189,152,82,.8);
    border-radius: 50%;
    aspect-ratio: 1;
    max-width: 105px;
    width: 100%;
    margin: auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: rgba(255,250,239,.72);
    box-shadow:
        inset 0 0 0 4px rgba(189,152,82,.08),
        0 5px 12px rgba(70,45,20,.06);
}

.time-number {
    font-size: clamp(21px, 6vw, 30px);
    color: var(--wine);
    font-weight: 600;
    font-variant-numeric: tabular-nums;
}

.time-label {
    font-size: 10px;
    color: var(--muted);
}

/* لایه مه روی اعداد */
.fog-canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 5;
    cursor: crosshair;
    touch-action: none;
}

.fog-hint {
    position: relative;
    z-index: 6;
    margin: 18px 0 0;
    color: var(--gold-dark);
    font-size: 11px;
    pointer-events: none;
}

/* =================================
   گالری تصاویر
================================= */

.gallery-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 27px;
    max-width: 650px;
    margin: 35px auto 0;
}

.gallery-item {
    position: relative;
    width: 100%;
    padding: 10px;
    border-radius: 27px;
    background: linear-gradient(145deg, #fff8e9, #d8c194);
    border: 1px solid var(--gold);
    outline: 1px solid rgba(189,152,82,.25);
    outline-offset: 4px;
    box-shadow: 0 12px 28px rgba(67,43,24,.13);
    transition: transform .45s ease, box-shadow .45s ease;
    overflow: hidden;
}

.gallery-item:nth-child(even) {
    transform: rotate(.5deg);
}

.gallery-item:nth-child(odd) {
    transform: rotate(-.5deg);
}

.gallery-item:hover {
    transform: translateY(-5px);
    box-shadow: 0 18px 35px rgba(67,43,24,.18);
}

.gallery-item::before {
    content: "✧";
    position: absolute;
    top: 13px;
    right: 17px;
    z-index: 2;
    color: #fff0c8;
    font-size: 23px;
    text-shadow: 0 2px 8px #503719;
    pointer-events: none;
}

.gallery-item img {
    display: block;
    width: 100%;
    max-height: 620px;
    aspect-ratio: 4 / 3;
    object-fit: cover;
    border-radius: 19px;
    border: 1px solid rgba(133,100,46,.35);
    cursor: zoom-in;
    transition: transform .8s cubic-bezier(.2,.7,.2,1);
}

.gallery-item:hover img {
    transform: scale(1.035);
}

.gallery-caption {
    font-family: "IranNastaliq", serif;
    color: var(--gold-dark);
    padding: 8px 0 2px;
    font-size: 25px;
}

#lightbox {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 2000;
    background: rgba(24,16,13,.95);
    align-items: center;
    justify-content: center;
    padding: 18px;
}

#lightbox.show {
    display: flex;
}

#lightbox img {
    max-width: 96%;
    max-height: 88vh;
    object-fit: contain;
    border: 4px solid var(--gold);
    border-radius: 20px;
    box-shadow: 0 0 35px rgba(0,0,0,.4);
}

.lightbox-close {
    position: absolute;
    top: 20px;
    left: 22px;
    border: 1px solid var(--gold);
    background: var(--wine);
    color: white;
    width: 42px;
    height: 42px;
    border-radius: 50%;
    font-size: 23px;
    cursor: pointer;
}

/* =================================
   ویدئو
================================= */

.video-frame {
    max-width: 600px;
    margin: 30px auto;
    padding: 9px;
    background: linear-gradient(145deg, #e7d3a8, #a9823e);
    border-radius: 28px;
    outline: 1px solid rgba(189,152,82,.3);
    outline-offset: 4px;
    box-shadow: 0 12px 28px rgba(70,45,20,.13);
}

.video-frame video {
    display: block;
    width: 100%;
    max-height: 560px;
    background: #241a18;
    border-radius: 20px;
}

/* =================================
   تقویم
================================= */

.calendar-card {
    width: min(100%, 350px);
    margin: 32px auto;
    overflow: hidden;
    border: 1px solid var(--gold);
    outline: 1px solid rgba(189,152,82,.25);
    outline-offset: 5px;
    border-radius: 28px;
    background: #fbf4e7;
    box-shadow: 0 13px 28px rgba(67,43,24,.12);
    transform-style: preserve-3d;
    transition: transform .5s ease, box-shadow .5s ease;
}

.calendar-card:hover {
    transform: perspective(900px) rotateX(3deg) translateY(-4px);
    box-shadow: 0 20px 35px rgba(67,43,24,.17);
}

.calendar-top {
    background: linear-gradient(120deg, var(--wine-dark), var(--wine));
    color: #f8e9c8;
    padding: 17px;
    font-size: 14px;
    letter-spacing: 2px;
}

.calendar-body {
    padding: 24px 12px;
}

.calendar-day {
    font-size: 95px;
    color: var(--wine);
    line-height: 1.4;
}

.calendar-month {
    color: var(--gold-dark);
    font-size: 18px;
}

.calendar-year {
    color: var(--muted);
    margin-top: 8px;
    font-size: 13px;
}

.calendar-card.animate {
    animation: calendarFlip .9s ease;
}

@keyframes calendarFlip {
    0% { transform: rotateX(0); }
    45% { transform: rotateX(-30deg); }
    100% { transform: rotateX(0); }
}

/* =================================
   نشانی و فرم حضور
================================= */

.address-icon {
    width: 72px;
    height: 72px;
    margin: 0 auto 20px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 1px solid var(--gold);
    outline: 1px solid rgba(189,152,82,.35);
    outline-offset: 5px;
    color: var(--wine);
    font-size: 30px;
    background: #f8edda;
    box-shadow: 0 7px 18px rgba(70,45,20,.1);
}

.address-text {
    line-height: 2.5;
    font-size: 14px;
    color: var(--ink);
}

.map-button,
.submit-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 9px;
    padding: 14px 25px;
    margin-top: 18px;
    border: 1px solid var(--gold-dark);
    border-radius: 30px;
    color: #fff3d8;
    text-decoration: none;
    background: linear-gradient(135deg, #8b6935, #604521);
    box-shadow: 0 6px 15px rgba(70,45,20,.15);
    transition: transform .25s ease, box-shadow .25s ease;
}

.map-button:hover,
.submit-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(70,45,20,.2);
}

.form-group {
    text-align: right;
    margin: 20px 0;
}

.form-group label {
    display: block;
    color: var(--gold-dark);
    font-size: 13px;
    margin-bottom: 9px;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 14px 13px;
    color: var(--ink);
    background: #fffaf0;
    border: 1px solid #c9ad76;
    border-radius: 16px;
    outline: none;
    transition: box-shadow .25s ease, border-color .25s ease;
}

.form-group input:focus,
.form-group select:focus {
    border-color: var(--wine);
    box-shadow: 0 0 0 4px rgba(118,45,60,.09);
}

.submit-button {
    width: 100%;
    border-radius: 30px;
    font-weight: 500;
    font-size: 15px;
    cursor: pointer;
}

.success-message {
    color: #477044;
    background: #edf4e7;
    border: 1px solid #a9c59a;
    border-radius: 17px;
    padding: 14px;
    margin-bottom: 18px;
    font-size: 13px;
}

.footer {
    padding: 55px 20px 75px;
    text-align: center;
    color: var(--muted);
}

.footer-names {
    font-size: 62px;
    color: var(--wine);
    margin: 8px 0;
}

.footer-heart {
    color: var(--wine);
    font-size: 27px;
}

/* =================================
   افکت‌های ظاهر شدن در اسکرول
================================= */

.reveal {
    opacity: 0;
    transform: translateY(28px);
    transition:
        opacity .9s ease,
        transform .9s cubic-bezier(.2,.7,.2,1);
}

.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}

@media (min-width: 560px) {
    .gallery-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 25px;
    }

    .gallery-item img {
        aspect-ratio: 4 / 5;
    }
}

@media (max-width: 380px) {
    section {
        padding: 58px 20px;
    }

    .countdown-grid {
        gap: 5px;
    }

    .time-label {
        font-size: 9px;
    }

    .time-number {
        font-size: 20px;
    }

    .seal-button {
        width: 108px;
        height: 108px;
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
}
</style>
</head>

<body class="locked">

<!-- پاکت دعوت‌نامه -->
<div id="intro">
    <div class="envelope">
        <div class="envelope-paper"></div>

        <div class="intro-writing">
            <div class="intro-small">دعوت‌نامه‌ای از جنس عشق</div>
            <div class="intro-title nastaliq">امیر و زهرا</div>
            <div class="intro-subtitle">برای یک شب به‌یادماندنی</div>
        </div>

        <div class="envelope-fold-left"></div>
        <div class="envelope-fold-right"></div>
        <div class="envelope-bottom"></div>
        <div class="envelope-flap"></div>

        <button
            class="seal-button"
            id="openSeal"
            aria-label="باز کردن دعوت‌نامه">
        </button>

        <div class="open-hint">برای گشودن دعوت‌نامه لمس کنید</div>
    </div>
</div>

<!-- محتوای اصلی -->
<div id="main-site">
<div class="page-paper paper-texture">

    <section class="hero">
        <div class="hero-kicker reveal">به نام عشق و زیبایی</div>

        <div class="hero-names nastaliq reveal">امیر</div>
        <div class="hero-and reveal">و</div>
        <div class="hero-names nastaliq reveal">زهرا</div>

        <div class="ornament reveal">❦ ✧ ❦</div>

        <p class="hero-description reveal">
            با قلبی سرشار از شادی، آغاز فصل تازه‌ای از زندگی‌مان را
            در کنار عزیزانمان جشن می‌گیریم.
            حضور شما، زیبایی این شب را دوچندان خواهد کرد.
        </p>

        <div class="scroll-cue">
            برای دیدن دعوت‌نامه به پایین بروید ↓
        </div>
    </section>

    <!-- روزشمار -->
    <section>
        <div class="reveal">
            <div class="section-title nastaliq">شمارش تا قرار عاشقانه</div>
            <div class="divider-ornament">❦</div>
            <p class="section-subtitle">
                غبار زمان را کنار بزنید و لحظه‌های باقی‌مانده را ببینید
            </p>
        </div>

        <div class="countdown-card reveal" id="countdownCard">
            <div class="countdown-title nastaliq">تا شب پیوندمان</div>

            <div class="countdown-grid">
                <div class="time-unit">
                    <div class="time-number" id="days">۰۰</div>
                    <div class="time-label">روز</div>
                </div>

                <div class="time-unit">
                    <div class="time-number" id="hours">۰۰</div>
                    <div class="time-label">ساعت</div>
                </div>

                <div class="time-unit">
                    <div class="time-number" id="minutes">۰۰</div>
                    <div class="time-label">دقیقه</div>
                </div>

                <div class="time-unit">
                    <div class="time-number" id="seconds">۰۰</div>
                    <div class="time-label">ثانیه</div>
                </div>
            </div>

            <canvas class="fog-canvas" id="fogCanvas"></canvas>
            <div class="fog-hint">✧ انگشت خود را روی مه بکشید ✧</div>
        </div>
    </section>

    <!-- گالری -->
    <section>
        <div class="reveal">
            <div class="section-title nastaliq">لحظه‌های ما</div>
            <div class="divider-ornament">❦</div>
            <p class="section-subtitle">
                قاب‌هایی از خاطرات و لحظه‌های دوست‌داشتنی
            </p>
        </div>

        <div class="gallery-grid">{{GALLERY}}</div>
    </section>

    <!-- ویدئو -->
    {{VIDEO}}

    <!-- تاریخ مراسم -->
    <section>
        <div class="reveal">
            <div class="section-title nastaliq">قرار دیدار ما</div>
            <div class="divider-ornament">❦</div>
            <p class="section-subtitle">
                منتظر قدم‌های پرمهر شما هستیم
            </p>
        </div>

        <div class="calendar-card reveal" id="calendarCard">
            <div class="calendar-top">روز پیوند عشق</div>

            <div class="calendar-body">
                <div class="calendar-day nastaliq">۲</div>
                <div class="calendar-month">دی ماه</div>
                <div class="calendar-year">یک‌هزار و چهارصد و پنج</div>
            </div>
        </div>

        <div class="ornament reveal">✧ ❦ ✧</div>

        <div class="ornate-card reveal">
            <div class="section-subtitle">چهارشنبه</div>
            <div class="section-title nastaliq">۲ دی ۱۴۰۵</div>
            <div>ساعت ۱۹ تا ۲۲</div>
        </div>
    </section>

    <!-- نشانی -->
    <section>
        <div class="reveal">
            <div class="section-title nastaliq">نشانی جشن</div>
            <div class="divider-ornament">❦</div>
        </div>

        <div class="address-card reveal">
            <div class="address-icon">⌖</div>

            <div class="section-title nastaliq">تالار پذیرایی فریال</div>

            <p class="address-text">{{ADDRESS}}</p>

            <a
                class="map-button"
                href="{{MAP_URL}}"
                target="_blank"
                rel="noopener">
                <span>⌖</span>
                مشاهده مسیر روی نقشه
            </a>
        </div>
    </section>

    <!-- فرم اعلام حضور -->
    <section>
        <div class="reveal">
            <div class="section-title nastaliq">پاسخ به دعوت</div>
            <div class="divider-ornament">❦</div>
            <p class="section-subtitle">
                لطفاً ما را از افتخار حضورتان باخبر کنید
            </p>
        </div>

        <div class="rsvp-card reveal">
            {{SUCCESS}}

            <form method="POST" action="/">
                <div class="form-group">
                    <label for="guestName">نام و نام خانوادگی</label>
                    <input
                        id="guestName"
                        name="name"
                        type="text"
                        placeholder="نام شما"
                        maxlength="100"
                        required>
                </div>

                <div class="form-group">
                    <label for="guestCount">تعداد نفرات</label>
                    <select id="guestCount" name="count" required>
                        <option value="۱ نفر">۱ نفر</option>
                        <option value="۲ نفر">۲ نفر</option>
                        <option value="۳ نفر">۳ نفر</option>
                        <option value="۴ نفر">۴ نفر</option>
                        <option value="۵ نفر">۵ نفر</option>
                        <option value="بیش از ۵ نفر">بیش از ۵ نفر</option>
                    </select>
                </div>

                <div class="form-group">
                    <label for="attendance">وضعیت حضور شما</label>
                    <select id="attendance" name="attendance" required>
                        <option value="با افتخار می‌آیم">
                            با افتخار می‌آیم ❤️
                        </option>
                        <option value="متأسفانه امکان حضور ندارم">
                            متأسفانه امکان حضور ندارم
                        </option>
                    </select>
                </div>

                <button class="submit-button" type="submit">
                    ❦ ثبت پاسخ دعوت ❦
                </button>
            </form>
        </div>
    </section>

    <div class="footer reveal">
        <div class="ornament">✧ ❦ ✧</div>
        <div class="footer-names nastaliq">امیر و زهرا</div>
        <div class="footer-heart">♥</div>
        <p>با مهر شما، این شب زیباتر می‌شود</p>
        <p class="section-subtitle">{{DATE}}</p>
    </div>

</div>
</div>

<!-- نمایش بزرگ تصاویر -->
<div id="lightbox">
    <button class="lightbox-close" id="closeLightbox" aria-label="بستن">
        ×
    </button>
    <img id="lightboxImage" src="" alt="تصویر بزرگ‌شده">
</div>

<!-- موزیک -->
<audio id="weddingMusic" loop preload="auto">
    <source src="/static/music.mp3" type="audio/mpeg">
</audio>

<script>
const intro = document.getElementById("intro");
const mainSite = document.getElementById("main-site");
const openSeal = document.getElementById("openSeal");
const music = document.getElementById("weddingMusic");

let opened = false;

openSeal.addEventListener("click", () => {
    if (opened) return;

    opened = true;
    intro.classList.add("opening");

    music.volume = 0.45;
    music.play().catch(() => {});

    setTimeout(() => {
        intro.classList.add("hidden");
        mainSite.classList.add("visible");
        document.body.classList.remove("locked");
        window.scrollTo(0, 0);
        initFog();
    }, 1900);
});

/* شمارش معکوس: ۲۳ دسامبر ۲۰۲۶، ساعت ۱۹ به وقت ایران */
const weddingDate = new Date(
    "2026-12-23T19:00:00+03:30"
).getTime();

const persianDigits = number =>
    String(number).replace(/\d/g, d => "۰۱۲۳۴۵۶۷۸۹"[d]);

function updateCountdown() {
    const distance = Math.max(0, weddingDate - Date.now());

    const days = Math.floor(distance / 86400000);
    const hours = Math.floor((distance / 3600000) % 24);
    const minutes = Math.floor((distance / 60000) % 60);
    const seconds = Math.floor((distance / 1000) % 60);

    document.getElementById("days").textContent =
        persianDigits(days);

    document.getElementById("hours").textContent =
        persianDigits(hours);

    document.getElementById("minutes").textContent =
        persianDigits(minutes);

    document.getElementById("seconds").textContent =
        persianDigits(seconds);
}

updateCountdown();
setInterval(updateCountdown, 1000);


/* مه کاملاً مات: فقط با حرکت انگشت یا ماوس آشکار می‌شود */
let fogInitialized = false;

function initFog() {
    if (fogInitialized) return;

    fogInitialized = true;

    const canvas = document.getElementById("fogCanvas");
    const card = document.getElementById("countdownCard");
    const ctx = canvas.getContext("2d");

    let width = 0;
    let height = 0;
    let drawing = false;
    let lastPoint = null;

    function resizeCanvas() {
        const rect = card.getBoundingClientRect();
        const dpr = Math.min(window.devicePixelRatio || 1, 2);

        width = rect.width;
        height = rect.height;

        canvas.width = Math.round(width * dpr);
        canvas.height = Math.round(height * dpr);

        canvas.style.width = width + "px";
        canvas.style.height = height + "px";

        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);

        const gradient = ctx.createLinearGradient(
            0, 0, width, height
        );

        gradient.addColorStop(0, "#e8d8b9");
        gradient.addColorStop(.45, "#ddc9a5");
        gradient.addColorStop(1, "#f0e2c7");

        ctx.globalCompositeOperation = "source-over";
        ctx.globalAlpha = 1;
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);

        /* بافت ظریف روی مه */
        for (let i = 0; i < 180; i++) {
            const x = Math.random() * width;
            const y = Math.random() * height;
            const radius = 3 + Math.random() * 12;

            ctx.beginPath();
            ctx.arc(x, y, radius, 0, Math.PI * 2);
            ctx.fillStyle = "rgba(255,250,235,0.12)";
            ctx.fill();
        }

        ctx.fillStyle = "rgba(133,100,46,.13)";
        ctx.font = "22px serif";
        ctx.fillText("✧", 20, 35);
        ctx.fillText("❦", width - 45, height - 20);
    }

    function getPoint(event) {
        const rect = canvas.getBoundingClientRect();

        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
    }

    function eraseAt(point) {
        ctx.save();
        ctx.globalCompositeOperation = "destination-out";

        const radius = 19;

        const gradient = ctx.createRadialGradient(
            point.x,
            point.y,
            2,
            point.x,
            point.y,
            radius
        );

        gradient.addColorStop(0, "rgba(0,0,0,1)");
        gradient.addColorStop(.8, "rgba(0,0,0,.98)");
        gradient.addColorStop(1, "rgba(0,0,0,0)");

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
    }

    canvas.addEventListener("pointerdown", event => {
        drawing = true;
        canvas.setPointerCapture(event.pointerId);
        lastPoint = getPoint(event);
        eraseAt(lastPoint);
    });

    canvas.addEventListener("pointermove", event => {
        if (!drawing) return;

        const point = getPoint(event);

        if (lastPoint) {
            const dx = point.x - lastPoint.x;
            const dy = point.y - lastPoint.y;
            const distance = Math.hypot(dx, dy);
            const steps = Math.max(1, Math.ceil(distance / 8));

            for (let i = 1; i <= steps; i++) {
                eraseAt({
                    x: lastPoint.x + dx * i / steps,
                    y: lastPoint.y + dy * i / steps
                });
            }
        }

        lastPoint = point;
    });

    function stopDrawing() {
        drawing = false;
        lastPoint = null;
    }

    canvas.addEventListener("pointerup", stopDrawing);
    canvas.addEventListener("pointercancel", stopDrawing);
    canvas.addEventListener("lostpointercapture", stopDrawing);

    resizeCanvas();

    /* هنگام تغییر اندازه، مه دوباره کامل می‌شود */
    window.addEventListener("resize", resizeCanvas);
}


/* نمایان شدن بخش‌ها هنگام اسکرول */
if ("IntersectionObserver" in window) {
    const revealObserver = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("visible");
                    revealObserver.unobserve(entry.target);
                }
            });
        },
        { threshold: 0.12 }
    );

    document.querySelectorAll(".reveal").forEach(element => {
        revealObserver.observe(element);
    });

    const calendar = document.getElementById("calendarCard");

    const calendarObserver = new IntersectionObserver(
        entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    calendar.classList.add("animate");
                    calendarObserver.unobserve(calendar);
                }
            });
        },
        { threshold: 0.5 }
    );

    calendarObserver.observe(calendar);
} else {
    document.querySelectorAll(".reveal").forEach(element => {
        element.classList.add("visible");
    });
}


/* نمایش بزرگ عکس‌ها */
const lightbox = document.getElementById("lightbox");
const lightboxImage = document.getElementById("lightboxImage");

document.querySelectorAll(".gallery-item img").forEach(img => {
    img.addEventListener("click", () => {
        lightboxImage.src = img.src;
        lightbox.classList.add("show");
    });
});

function closeLightbox() {
    lightbox.classList.remove("show");
    lightboxImage.src = "";
}

document.getElementById("closeLightbox").addEventListener(
    "click",
    closeLightbox
);

lightbox.addEventListener("click", event => {
    if (event.target === lightbox) {
        closeLightbox();
    }
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        closeLightbox();
    }
});
</script>

</body>
</html>
"""


def build_gallery():
    photo_names = [
        "wedding-photo.jpg",
        "photo1.jpg",
        "photo2.jpg",
        "photo3.jpg",
        "photo4.jpg",
        "photo5.jpg",
        "photo6.jpg",
    ]

    items = []

    for index, filename in enumerate(photo_names, start=1):
        if (STATIC_DIR / filename).exists():
            safe_name = html.escape(filename, quote=True)

            items.append(
                f"""
                <div class="gallery-item">
                    <img
                        src="/static/{safe_name}"
                        alt="تصویر خاطره {index}"
                        loading="lazy">
                    <div class="gallery-caption">
                        خاطره‌ای از عشق
                    </div>
                </div>
                """
            )

    if not items:
        return """
        <div class="ornate-card">
            <p>
                تصاویر زیبای شما به‌زودی در این قسمت قرار می‌گیرند.
            </p>
        </div>
        """

    return "\n".join(items)


def build_video():
    if not (STATIC_DIR / "wedding.mp4").exists():
        return ""

    return """
    <section>
        <div class="reveal">
            <div class="section-title nastaliq">
                لحظه‌ای برای تماشا
            </div>
            <div class="divider-ornament">❦</div>
        </div>

        <div class="video-frame reveal">
            <video controls playsinline preload="metadata">
                <source
                    src="/static/wedding.mp4"
                    type="video/mp4">
                مرورگر شما از پخش ویدئو پشتیبانی نمی‌کند.
            </video>
        </div>
    </section>
    """


@app.route("/", methods=["GET", "POST"])
def home():
    success = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        count = request.form.get("count", "").strip()
        attendance = request.form.get("attendance", "").strip()

        allowed_counts = {
            "۱ نفر",
            "۲ نفر",
            "۳ نفر",
            "۴ نفر",
            "۵ نفر",
            "بیش از ۵ نفر"
        }

        allowed_attendance = {
            "با افتخار می‌آیم",
            "متأسفانه امکان حضور ندارم"
        }

        if (
            name
            and len(name) <= 100
            and count in allowed_counts
            and attendance in allowed_attendance
        ):
            try:
                file_exists = GUESTS_FILE.exists()

                with open(
                    GUESTS_FILE,
                    "a",
                    newline="",
                    encoding="utf-8-sig"
                ) as file:
                    writer = csv.writer(file)

                    if not file_exists:
                        writer.writerow([
                            "نام",
                            "تعداد نفرات",
                            "وضعیت حضور",
                            "زمان ثبت"
                        ])

                    writer.writerow([
                        name,
                        count,
                        attendance,
                        datetime.now().isoformat(timespec="seconds")
                    ])

                send_telegram_message(
                    name,
                    count,
                    attendance
                )

                success = (
                    '<div class="success-message">'
                    'پاسخ شما با موفقیت ثبت شد. '
                    'از محبتتان سپاسگزاریم ❤️'
                    '</div>'
                )

            except Exception as error:
                print("RSVP save error:", error)

                success = (
                    '<div class="success-message">'
                    'ثبت پاسخ با مشکل روبه‌رو شد. '
                    'لطفاً دوباره تلاش کنید.'
                    '</div>'
                )

        else:
            success = (
                '<div class="success-message">'
                'لطفاً اطلاعات را به‌درستی وارد کنید.'
                '</div>'
            )

    page = PAGE

    page = page.replace("{{GALLERY}}", build_gallery())
    page = page.replace("{{VIDEO}}", build_video())
    page = page.replace("{{DATE}}", html.escape(WEDDING_DATE))
    page = page.replace("{{ADDRESS}}", html.escape(ADDRESS))
    page = page.replace(
        "{{MAP_URL}}",
        html.escape(MAP_URL, quote=True)
    )
    page = page.replace("{{SUCCESS}}", success)

    return page


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
