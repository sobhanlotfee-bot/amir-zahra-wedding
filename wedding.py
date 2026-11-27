
from flask import Flask, request, redirect
from pathlib import Path
from datetime import datetime
import csv
import html
import os
import urllib.request
import urllib.parse
import json

app = Flask(__name__)

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
STATIC_DIR.mkdir(exist_ok=True)

GUESTS_FILE = BASE_DIR / "guests.csv"

WEDDING_DATE = "چهارشنبه ۲ دی ۱۴۰۵"
WEDDING_TIME = "۱۹ تا ۲۲"
ADDRESS = "سمنان، میدان معلم، بلوار بسیج، جنب ورزشگاه الغدیر، تالار پذیرایی فریال"

MAP_URL = (
    "https://www.google.com/maps/dir/?api=1"
    "&destination=35.5868900%2C53.3861140"
    "&travelmode=driving&dir_action=navigate"
)

# --------------------------------------------------
# ارسال پیام تلگرام
# --------------------------------------------------

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
        urllib.request.urlopen(req, timeout=10)
    except Exception as error:
        print("Telegram error:", error)


# --------------------------------------------------
# محتوای صفحه
# --------------------------------------------------

PAGE = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
<meta name="theme-color" content="#f3e8d2">
<meta name="description" content="دعوت‌نامه عروسی امیر و زهرا">
<title>دعوت‌نامه عروسی امیر و زهرا</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;500;600&family=Vazirmatn:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
:root {
    --paper: #f3e8d2;
    --paper-light: #fbf4e7;
    --paper-dark: #e5d3b3;
    --gold: #bd9852;
    --gold-light: #dfc58c;
    --gold-dark: #85642e;
    --wine: #762d3c;
    --wine-dark: #4c1c2a;
    --ink: #49382d;
    --muted: #806b56;
    --shadow: rgba(67, 43, 24, .2);
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
    color: var(--ink);
    font-family: "Vazirmatn", sans-serif;
    background:
        radial-gradient(ellipse at 20% 10%, rgba(255,255,255,.55), transparent 40%),
        radial-gradient(ellipse at 90% 80%, rgba(189,152,82,.12), transparent 45%),
        var(--paper);
    overflow-x: hidden;
}

body.locked {
    overflow: hidden;
}

button, input, select {
    font: inherit;
}

button {
    cursor: pointer;
}

.nastaliq {
    font-family: "Noto Nastaliq Urdu", serif;
    font-weight: 500;
    line-height: 2.2;
}

.gold-text {
    color: var(--gold-dark);
}

.ornament {
    color: var(--gold-dark);
    letter-spacing: 8px;
    text-align: center;
    font-size: 19px;
    margin: 12px 0;
}

.paper-texture {
    background-color: var(--paper-light);
    background-image:
        radial-gradient(rgba(111,77,39,.09) .6px, transparent .7px),
        radial-gradient(rgba(255,255,255,.45) .7px, transparent .8px),
        linear-gradient(135deg, rgba(255,255,255,.25), rgba(151,111,55,.04));
    background-size: 7px 7px, 11px 11px, 100% 100%;
}

.gold-frame {
    position: relative;
    border: 1px solid var(--gold);
    outline: 1px solid rgba(189,152,82,.45);
    outline-offset: 5px;
}

.gold-frame::before,
.gold-frame::after {
    content: "❦";
    position: absolute;
    color: var(--gold-dark);
    font-size: 22px;
    z-index: 2;
}

.gold-frame::before {
    top: -15px;
    right: -12px;
}

.gold-frame::after {
    bottom: -15px;
    left: -12px;
    transform: rotate(180deg);
}

/* ----------------- پاکت تمام صفحه ----------------- */

#intro {
    position: fixed;
    inset: 0;
    z-index: 1000;
    width: 100%;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    background:
        radial-gradient(ellipse at center, #f8efdF 0%, #e8d6b7 100%);
    perspective: 1400px;
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
    background:
        radial-gradient(ellipse at 50% 45%, rgba(255,255,255,.5), transparent 65%),
        linear-gradient(145deg, #f7eedc, #e5d2b1);
    transform-style: preserve-3d;
}

.envelope::before {
    content: "";
    position: absolute;
    inset: 12px;
    border: 1px solid var(--gold);
    box-shadow:
        inset 0 0 0 4px rgba(255,255,255,.25),
        inset 0 0 0 6px rgba(189,152,82,.28);
    pointer-events: none;
    z-index: 5;
}

.envelope::after {
    content: "";
    position: absolute;
    inset: 22px;
    border: 1px solid rgba(133,100,46,.35);
    pointer-events: none;
    z-index: 5;
}

.envelope-paper {
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse at 50% 40%, rgba(255,255,255,.4), transparent 60%),
        repeating-linear-gradient(0deg, transparent 0 4px, rgba(110,80,40,.018) 5px);
}

.envelope-fold-left,
.envelope-fold-right {
    position: absolute;
    bottom: 0;
    width: 100%;
    height: 72%;
    background: linear-gradient(145deg, #f6ecd9, #e5d2b2);
    z-index: 2;
}

.envelope-fold-left {
    left: 0;
    clip-path: polygon(0 0, 100% 100%, 0 100%);
    filter: drop-shadow(2px -3px 5px rgba(75,50,25,.12));
}

.envelope-fold-right {
    right: 0;
    clip-path: polygon(100% 0, 100% 100%, 0 100%);
    filter: drop-shadow(-2px -3px 5px rgba(75,50,25,.12));
}

.envelope-bottom {
    position: absolute;
    inset: auto 0 0;
    height: 72%;
    background: linear-gradient(160deg, #ead9bc, #d9c29b);
    clip-path: polygon(0 100%, 50% 0, 100% 100%);
    z-index: 3;
    filter: drop-shadow(0 -5px 9px rgba(80,50,20,.14));
}

.envelope-flap {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 57%;
    background: linear-gradient(160deg, #fbf3e4, #e8d6b7);
    clip-path: polygon(0 0, 100% 0, 50% 100%);
    transform-origin: top center;
    z-index: 6;
    transition: transform 1.65s cubic-bezier(.68,-.08,.22,1);
    filter: drop-shadow(0 8px 7px rgba(75,48,20,.16));
}

.envelope-flap::after {
    content: "";
    position: absolute;
    inset: 10px 10px 0;
    border-top: 1px solid rgba(189,152,82,.55);
}

.intro-writing {
    position: absolute;
    z-index: 4;
    top: 23%;
    left: 8%;
    right: 8%;
    text-align: center;
    color: var(--gold-dark);
}

.intro-small {
    font-size: 12px;
    letter-spacing: 2px;
}

.intro-title {
    font-size: clamp(32px, 9vw, 52px);
    margin: 18px 0;
    color: var(--wine);
}

.intro-subtitle {
    font-size: 14px;
    color: #806b56;
}

.seal-button {
    position: absolute;
    z-index: 10;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 112px;
    height: 112px;
    border: 0;
    border-radius: 50%;
    color: #f4dfb4;
    font-size: 37px;
    background:
        radial-gradient(circle at 35% 25%, #a34a58, #762d3c 60%, #4c1c2a);
    box-shadow:
        0 9px 18px rgba(67,24,32,.3),
        inset 0 2px 5px rgba(255,255,255,.25),
        inset 0 -5px 8px rgba(30,0,10,.3);
    outline: 2px solid #bd9852;
    outline-offset: 5px;
    transition: transform .3s ease, opacity .5s ease;
}

.seal-button:active {
    transform: translate(-50%, -50%) scale(.94);
}

.seal-button span {
    display: block;
    font-size: 11px;
    margin-top: -3px;
    font-family: "Vazirmatn", sans-serif;
}

.open-hint {
    position: absolute;
    z-index: 8;
    top: calc(55% + 92px);
    left: 0;
    right: 0;
    text-align: center;
    color: var(--gold-dark);
    font-size: 12px;
    animation: breathe 2s infinite;
}

@keyframes breathe {
    0%, 100% { opacity: .55; transform: translateY(0); }
    50% { opacity: 1; transform: translateY(-4px); }
}

#intro.opening .envelope-flap {
    transform: rotateX(180deg);
}

#intro.opening .seal-button {
    opacity: 0;
    pointer-events: none;
    transform: translate(-50%, -50%) scale(1.7);
}

#intro.opening .envelope-fold-left {
    animation: foldLeft 1.5s 0.45s forwards;
}

#intro.opening .envelope-fold-right {
    animation: foldRight 1.5s 0.45s forwards;
}

#intro.opening .envelope-bottom {
    animation: foldBottom 1.5s 0.45s forwards;
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

/* ----------------- محتوای اصلی ----------------- */

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
    width: min(100%, 760px);
    margin: 0 auto;
    min-height: 100vh;
    overflow: hidden;
    background:
        radial-gradient(ellipse at 10% 5%, rgba(255,255,255,.5), transparent 35%),
        radial-gradient(ellipse at 90% 90%, rgba(189,152,82,.1), transparent 40%),
        var(--paper);
    box-shadow: 0 0 45px rgba(70,45,20,.12);
}

.page-paper::before {
    content: "";
    position: absolute;
    inset: 9px;
    border: 1px solid rgba(189,152,82,.7);
    pointer-events: none;
    z-index: 10;
}

.page-paper::after {
    content: "";
    position: absolute;
    inset: 17px;
    border: 1px solid rgba(133,100,46,.25);
    pointer-events: none;
    z-index: 10;
}

section {
    position: relative;
    padding: 66px 28px;
    text-align: center;
}

.hero {
    min-height: 92vh;
    min-height: 92dvh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 70px 28px;
}

.hero::before {
    content: "✧";
    position: absolute;
    top: 45px;
    font-size: 30px;
    color: var(--gold);
}

.hero-kicker {
    font-size: 13px;
    color: var(--muted);
    letter-spacing: 2px;
}

.hero-names {
    font-size: clamp(40px, 11vw, 65px);
    color: var(--wine);
    margin: 20px 0 8px;
}

.hero-and {
    color: var(--gold-dark);
    font-size: 20px;
    margin: 2px 0;
}

.hero-description {
    max-width: 430px;
    font-size: 14px;
    line-height: 2.4;
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
    font-size: clamp(28px, 7vw, 38px);
    color: var(--wine);
    margin: 0 0 10px;
}

.section-subtitle {
    color: var(--muted);
    font-size: 13px;
    line-height: 2.2;
}

.divider-ornament {
    display: flex;
    align-items: center;
    gap: 12px;
    justify-content: center;
    color: var(--gold-dark);
    margin: 18px 0 28px;
}

.divider-ornament::before,
.divider-ornament::after {
    content: "";
    height: 1px;
    width: 65px;
    background: linear-gradient(to left, transparent, var(--gold));
}

.divider-ornament::after {
    background: linear-gradient(to right, transparent, var(--gold));
}

/* کارت‌های تزیینی */

.ornate-card {
    position: relative;
    padding: 28px 20px;
    margin: 25px auto;
    max-width: 530px;
    background: rgba(255,250,239,.58);
    border: 1px solid var(--gold);
    outline: 1px solid rgba(189,152,82,.25);
    outline-offset: 5px;
    box-shadow: 0 12px 28px rgba(70,45,20,.08);
}

.ornate-card::before,
.ornate-card::after {
    content: "✧";
    position: absolute;
    color: var(--gold-dark);
    font-size: 21px;
}

.ornate-card::before {
    top: 7px;
    right: 10px;
}

.ornate-card::after {
    bottom: 7px;
    left: 10px;
}

/* ----------------- روزشمار مه‌آلود ----------------- */

.countdown-card {
    max-width: 550px;
    margin: 30px auto;
    position: relative;
    padding: 32px 16px;
    overflow: hidden;
    background: linear-gradient(145deg, #f8f0df, #e9d8b8);
    border: 1px solid var(--gold);
    box-shadow: 0 15px 35px rgba(80,50,20,.13);
}

.countdown-title {
    font-size: 21px;
    color: var(--wine);
    margin-bottom: 20px;
}

.countdown-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 7px;
    direction: rtl;
}

.time-unit {
    border: 1px solid rgba(189,152,82,.65);
    border-radius: 50%;
    aspect-ratio: 1;
    max-width: 105px;
    width: 100%;
    margin: auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    background: rgba(255,250,239,.65);
    box-shadow: inset 0 0 0 4px rgba(189,152,82,.1);
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

.fog-canvas {
    position: absolute;
    inset: 0;
    width: 100%;
    height: 100%;
    z-index: 5;
    cursor: crosshair;
    touch-action: pan-y;
}

.fog-hint {
    position: relative;
    z-index: 6;
    margin: 18px 0 0;
    color: var(--gold-dark);
    font-size: 11px;
    pointer-events: none;
}

/* ----------------- گالری ----------------- */

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 22px 16px;
    max-width: 600px;
    margin: 32px auto 0;
}

.gallery-item {
    position: relative;
    padding: 8px;
    background: linear-gradient(145deg, #fff8e9, #d8c194);
    border: 1px solid var(--gold-dark);
    box-shadow: 0 10px 22px rgba(67,43,24,.16);
    transform: rotate(-1deg);
    transition: transform .5s ease, box-shadow .5s ease;
}

.gallery-item:nth-child(even) {
    transform: rotate(1.3deg);
}

.gallery-item:hover {
    transform: translateY(-5px) rotate(0);
    box-shadow: 0 18px 30px rgba(67,43,24,.22);
}

.gallery-item img {
    display: block;
    width: 100%;
    aspect-ratio: 4 / 5;
    object-fit: cover;
    border: 1px solid rgba(133,100,46,.55);
    cursor: zoom-in;
}

.gallery-caption {
    font-family: "Noto Nastaliq Urdu", serif;
    color: var(--gold-dark);
    padding: 8px 0 2px;
    font-size: 14px;
}

#lightbox {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 2000;
    background: rgba(24,16,13,.92);
    align-items: center;
    justify-content: center;
    padding: 20px;
}

#lightbox.show {
    display: flex;
}

#lightbox img {
    max-width: 95%;
    max-height: 85vh;
    object-fit: contain;
    border: 5px solid var(--gold);
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
}

/* ----------------- ویدئو ----------------- */

.video-frame {
    max-width: 560px;
    margin: 28px auto;
    padding: 9px;
    background: linear-gradient(145deg, #e7d3a8, #a9823e);
    box-shadow: 0 12px 28px rgba(70,45,20,.16);
}

.video-frame video {
    display: block;
    width: 100%;
    max-height: 520px;
    background: #241a18;
    border: 1px solid var(--gold-dark);
}

/* ----------------- تاریخ ----------------- */

.calendar-card {
    width: min(100%, 340px);
    margin: 30px auto;
    background: #fbf4e7;
    border: 1px solid var(--gold);
    box-shadow: 0 15px 30px rgba(67,43,24,.13);
    transform-style: preserve-3d;
}

.calendar-top {
    background: linear-gradient(120deg, var(--wine-dark), var(--wine));
    color: #f8e9c8;
    padding: 15px;
    font-size: 14px;
    letter-spacing: 2px;
}

.calendar-body {
    padding: 24px 12px;
}

.calendar-day {
    font-size: 65px;
    color: var(--wine);
    line-height: 1.4;
    font-weight: 300;
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
    45% { transform: rotateX(-35deg); }
    100% { transform: rotateX(0); }
}

/* ----------------- آدرس ----------------- */

.address-card {
    max-width: 550px;
    margin: 30px auto;
    padding: 28px 20px;
    background: rgba(255,250,239,.65);
    border: 1px solid var(--gold);
    box-shadow: 0 12px 25px rgba(67,43,24,.09);
}

.address-icon {
    width: 66px;
    height: 66px;
    margin: 0 auto 15px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 2px solid var(--gold);
    outline: 1px solid rgba(189,152,82,.5);
    outline-offset: 4px;
    color: var(--wine);
    font-size: 29px;
    background: #f8edda;
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
    padding: 13px 25px;
    margin-top: 18px;
    border: 1px solid var(--gold-dark);
    color: #fff3d8;
    text-decoration: none;
    background: linear-gradient(135deg, #8b6935, #604521);
    box-shadow: 0 6px 15px rgba(70,45,20,.18);
    transition: transform .25s ease, box-shadow .25s ease;
}

.map-button:hover,
.submit-button:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 20px rgba(70,45,20,.22);
}

/* ----------------- فرم پاسخ ----------------- */

.rsvp-card {
    max-width: 550px;
    margin: 30px auto;
    padding: 30px 20px;
    border: 1px solid var(--gold);
    background: rgba(255,250,239,.7);
    box-shadow: 0 12px 28px rgba(67,43,24,.1);
}

.form-group {
    text-align: right;
    margin: 18px 0;
}

.form-group label {
    display: block;
    color: var(--gold-dark);
    font-size: 13px;
    margin-bottom: 8px;
}

.form-group input,
.form-group select {
    width: 100%;
    padding: 13px 12px;
    color: var(--ink);
    background: #fffaf0;
    border: 1px solid #c9ad76;
    border-radius: 2px;
    outline: none;
}

.form-group input:focus,
.form-group select:focus {
    border-color: var(--wine);
    box-shadow: 0 0 0 3px rgba(118,45,60,.08);
}

.submit-button {
    width: 100%;
    border-radius: 2px;
    font-weight: 500;
    font-size: 15px;
}

.success-message {
    color: #477044;
    background: #edf4e7;
    border: 1px solid #a9c59a;
    padding: 12px;
    margin-bottom: 18px;
    font-size: 13px;
}

/* ----------------- پایان صفحه ----------------- */

.footer {
    padding: 55px 20px 75px;
    text-align: center;
    color: var(--muted);
}

.footer-names {
    font-size: 33px;
    color: var(--wine);
    margin: 8px 0;
}

.footer-heart {
    color: var(--wine);
    font-size: 25px;
}

/* ----------------- افکت اسکرول ----------------- */

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

.float-decoration {
    position: absolute;
    color: rgba(133,100,46,.22);
    pointer-events: none;
    font-size: 28px;
}

.float-decoration.one {
    top: 30px;
    right: 20px;
}

.float-decoration.two {
    bottom: 30px;
    left: 20px;
}

@media (max-width: 380px) {
    section {
        padding: 55px 22px;
    }

    .countdown-grid {
        gap: 4px;
    }

    .time-label {
        font-size: 9px;
    }

    .time-number {
        font-size: 21px;
    }

    .seal-button {
        width: 100px;
        height: 100px;
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

<!-- پاکت ورودی -->
<div id="intro">
    <div class="envelope">
        <div class="envelope-paper"></div>

        <div class="intro-writing">
            <div class="intro-small">با عشق و احترام تقدیم می‌شود</div>
            <div class="intro-title nastaliq">دعوت‌نامه</div>
            <div class="intro-subtitle">برای یک شب به‌یادماندنی</div>
        </div>

        <div class="envelope-fold-left"></div>
        <div class="envelope-fold-right"></div>
        <div class="envelope-bottom"></div>
        <div class="envelope-flap"></div>

        <button class="seal-button" id="openSeal" aria-label="باز کردن دعوت‌نامه">
            ❦
            <span>باز کردن نامه</span>
        </button>
        <div class="open-hint">برای گشودن دعوت‌نامه لمس کنید</div>
    </div>
</div>

<!-- سایت اصلی -->
<div id="main-site">
<div class="page-paper paper-texture">

    <section class="hero">
        <div class="hero-kicker reveal">به نام عشق و زیبایی</div>

        <div class="hero-names nastaliq reveal">
            امیر
        </div>

        <div class="hero-and reveal">و</div>

        <div class="hero-names nastaliq reveal">
            زهرا
        </div>

        <div class="ornament reveal">❦ ✧ ❦</div>

        <p class="hero-description reveal">
            با قلبی سرشار از شادی، آغاز فصل تازه‌ای از زندگی‌مان را
            در کنار عزیزانمان جشن می‌گیریم.
            حضور شما، زیبایی این شب را دوچندان خواهد کرد.
        </p>

        <div class="scroll-cue">برای دیدن دعوت‌نامه به پایین بروید ↓</div>
    </section>

    <section>
        <span class="float-decoration one">✧</span>
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
            <div class="fog-hint">✧ انگشت خود را روی مه بکشید تا شمارش آشکار شود ✧</div>
        </div>
    </section>

    <section>
        <div class="reveal">
            <div class="section-title nastaliq">لحظه‌های ما</div>
            <div class="divider-ornament">❦</div>
            <p class="section-subtitle">
                قاب‌هایی از خاطرات و لحظه‌های دوست‌داشتنی
            </p>
        </div>

        <div class="gallery-grid">
            {{GALLERY}}
        </div>
    </section>

    {{VIDEO}}

    <section>
        <div class="reveal">
            <div class="section-title nastaliq">قرار دیدار ما</div>
            <div class="divider-ornament">❦</div>
            <p class="section-subtitle">منتظر قدم‌های پرمهر شما هستیم</p>
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
            <div class="gold-text">ساعت ۱۹ تا ۲۲</div>
        </div>
    </section>

    <section>
        <div class="reveal">
            <div class="section-title nastaliq">نشانی جشن</div>
            <div class="divider-ornament">❦</div>
        </div>

        <div class="address-card reveal">
            <div class="address-icon">⌖</div>
            <div class="section-title nastaliq">تالار پذیرایی فریال</div>
            <p class="address-text">{{ADDRESS}}</p>
            <a class="map-button" href="{{MAP_URL}}" target="_blank" rel="noopener">
                <span>⌖</span>
                مشاهده مسیر روی نقشه
            </a>
        </div>
    </section>

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
                        required
                    >
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
                        <option value="با افتخار می‌آیم">با افتخار می‌آیم ❤️</option>
                        <option value="متأسفانه امکان حضور ندارم">متأسفانه امکان حضور ندارم</option>
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

<div id="lightbox">
    <button class="lightbox-close" id="closeLightbox" aria-label="بستن">×</button>
    <img id="lightboxImage" src="" alt="تصویر بزرگ‌شده">
</div>

<audio id="weddingMusic" loop preload="auto">
    <source src="/static/music.mp3" type="audio/mpeg">
</audio>

<script>
/* ----------------- باز شدن پاکت ----------------- */

const intro = document.getElementById("intro");
const mainSite = document.getElementById("main-site");
const openSeal = document.getElementById("openSeal");
const music = document.getElementById("weddingMusic");

let opened = false;

openSeal.addEventListener("click", () => {
    if (opened) return;
    opened = true;

    intro.classList.add("opening");

    // تلاش برای پخش موزیک پس از لمس کاربر
    music.volume = 0.45;
    music.play().catch(() => {
        // در صورت محدودیت مرورگر، سایت بدون موزیک باز می‌شود.
    });

    setTimeout(() => {
        intro.classList.add("hidden");
        mainSite.classList.add("visible");
        document.body.classList.remove("locked");
        window.scrollTo(0, 0);
        initFog();
    }, 1900);
});


/* ----------------- شمارش معکوس ----------------- */

// زمان مراسم به وقت ایران: ۲۳ دسامبر ۲۰۲۶، ساعت ۱۹
const weddingDate = new Date("2026-12-23T19:00:00+03:30").getTime();

const persianDigits = number => {
    return String(number).replace(/\d/g, d => "۰۱۲۳۴۵۶۷۸۹"[d]);
};

function updateCountdown() {
    const now = Date.now();
    let distance = weddingDate - now;

    if (distance < 0) distance = 0;

    const days = Math.floor(distance / (1000 * 60 * 60 * 24));
    const hours = Math.floor((distance / (1000 * 60 * 60)) % 24);
    const minutes = Math.floor((distance / (1000 * 60)) % 60);
    const seconds = Math.floor((distance / 1000) % 60);

    document.getElementById("days").textContent = persianDigits(days);
    document.getElementById("hours").textContent = persianDigits(hours);
    document.getElementById("minutes").textContent = persianDigits(minutes);
    document.getElementById("seconds").textContent = persianDigits(seconds);
}

updateCountdown();
setInterval(updateCountdown, 1000);


/* ----------------- مه‌زدایی با لمس و کشیدن ----------------- */

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

        // مه کاغذی روی شمارش
        const gradient = ctx.createLinearGradient(0, 0, width, height);
        gradient.addColorStop(0, "rgba(241,229,205,0.98)");
        gradient.addColorStop(0.5, "rgba(231,216,187,0.97)");
        gradient.addColorStop(1, "rgba(247,237,216,0.98)");

        ctx.globalCompositeOperation = "source-over";
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);

        // نقش‌های لطیف روی مه
        ctx.fillStyle = "rgba(133,100,46,.12)";
        ctx.font = "22px serif";
        ctx.fillText("✧", 20, 35);
        ctx.fillText("❦", width - 45, height - 20);
    }

    function pointFromEvent(event) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: event.clientX - rect.left,
            y: event.clientY - rect.top
        };
    }

    function eraseAt(point) {
        ctx.save();
        ctx.globalCompositeOperation = "destination-out";

        const radius = 43;
        const gradient = ctx.createRadialGradient(
            point.x, point.y, 5,
            point.x, point.y, radius
        );

        gradient.addColorStop(0, "rgba(0,0,0,1)");
        gradient.addColorStop(0.72, "rgba(0,0,0,.95)");
        gradient.addColorStop(1, "rgba(0,0,0,0)");

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
        ctx.fill();

        ctx.restore();
    }

    canvas.addEventListener("pointerdown", event => {
        drawing = true;
        lastPoint = pointFromEvent(event);
        eraseAt(lastPoint);
    });

    canvas.addEventListener("pointermove", event => {
        if (!drawing) return;

        const point = pointFromEvent(event);

        if (lastPoint) {
            const dx = point.x - lastPoint.x;
            const dy = point.y - lastPoint.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const steps = Math.max(1, Math.ceil(distance / 14));

            for (let i = 1; i <= steps; i++) {
                const p = {
                    x: lastPoint.x + dx * i / steps,
                    y: lastPoint.y + dy * i / steps
                };
                eraseAt(p);
            }
        } else {
            eraseAt(point);
        }

        lastPoint = point;
    });

    function stopDrawing() {
        drawing = false;
        lastPoint = null;
    }

    canvas.addEventListener("pointerup", stopDrawing);
    canvas.addEventListener("pointercancel", stopDrawing);
    canvas.addEventListener("pointerleave", stopDrawing);

    resizeCanvas();

    window.addEventListener("resize", () => {
        // اندازه جدید را فقط در صورت تغییر ابعاد کارت اعمال می‌کنیم.
        resizeCanvas();
    });
}


/* ----------------- ظاهر شدن بخش‌ها هنگام اسکرول ----------------- */

const revealObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            revealObserver.unobserve(entry.target);
        }
    });
}, {
    threshold: 0.12
});

document.querySelectorAll(".reveal").forEach(element => {
    revealObserver.observe(element);
});


/* ----------------- افکت تقویم ----------------- */

const calendar = document.getElementById("calendarCard");

const calendarObserver = new IntersectionObserver(entries => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            calendar.classList.add("animate");
            calendarObserver.unobserve(calendar);
        }
    });
}, { threshold: 0.5 });

calendarObserver.observe(calendar);


/* ----------------- نمایش بزرگ عکس‌ها ----------------- */

const lightbox = document.getElementById("lightbox");
const lightboxImage = document.getElementById("lightboxImage");

document.querySelectorAll(".gallery-item img").forEach(img => {
    img.addEventListener("click", () => {
        lightboxImage.src = img.src;
        lightbox.classList.add("show");
    });
});

document.getElementById("closeLightbox").addEventListener("click", () => {
    lightbox.classList.remove("show");
    lightboxImage.src = "";
});

lightbox.addEventListener("click", event => {
    if (event.target === lightbox) {
        lightbox.classList.remove("show");
        lightboxImage.src = "";
    }
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") {
        lightbox.classList.remove("show");
        lightboxImage.src = "";
    }
});
</script>

</body>
</html>
"""


# --------------------------------------------------
# ساخت گالری تصاویر
# --------------------------------------------------

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
        photo_path = STATIC_DIR / filename

        if photo_path.exists():
            safe_name = html.escape(filename, quote=True)
            items.append(
                f"""
                <div class="gallery-item">
                    <img src="/static/{safe_name}"
                         alt="تصویر خاطره {index}"
                         loading="lazy">
                    <div class="gallery-caption">خاطره‌ای از عشق</div>
                </div>
                """
            )

    if not items:
        return """
        <div class="ornate-card" style="grid-column:1/-1">
            <p>تصاویر زیبای شما به‌زودی در این قسمت قرار می‌گیرند.</p>
        </div>
        """

    return "\n".join(items)


# --------------------------------------------------
# بخش ویدئو
# --------------------------------------------------

def build_video():
    video_path = STATIC_DIR / "wedding.mp4"

    if not video_path.exists():
        return ""

    return """
    <section>
        <div class="reveal">
            <div class="section-title nastaliq">لحظه‌ای برای تماشا</div>
            <div class="divider-ornament">❦</div>
        </div>

        <div class="video-frame reveal">
            <video controls playsinline preload="metadata">
                <source src="/static/wedding.mp4" type="video/mp4">
                مرورگر شما از پخش ویدئو پشتیبانی نمی‌کند.
            </video>
        </div>
    </section>
    """


# --------------------------------------------------
# مسیر اصلی سایت
# --------------------------------------------------

@app.route("/", methods=["GET", "POST"])
def home():
    success = ""

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        count = request.form.get("count", "").strip()
        attendance = request.form.get("attendance", "").strip()

        allowed_counts = {
            "۱ نفر", "۲ نفر", "۳ نفر",
            "۴ نفر", "۵ نفر", "بیش از ۵ نفر"
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

                send_telegram_message(name, count, attendance)

                success = (
                    '<div class="success-message">'
                    'پاسخ شما با موفقیت ثبت شد. از محبتتان سپاسگزاریم ❤️'
                    '</div>'
                )

            except Exception as error:
                print("RSVP save error:", error)
                success = (
                    '<div class="success-message">'
                    'ثبت پاسخ با مشکل روبه‌رو شد. لطفاً دوباره تلاش کنید.'
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
    page = page.replace("{{MAP_URL}}", html.escape(MAP_URL, quote=True))
    page = page.replace("{{SUCCESS}}", success)

    return page


# --------------------------------------------------
# اجرای محلی
# --------------------------------------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
