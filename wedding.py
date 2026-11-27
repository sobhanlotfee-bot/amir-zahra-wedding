
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
STATIC_DIR.mkdir(exist_ok=True)
GUESTS_FILE = BASE_DIR / "guests.csv"

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
        urllib.request.urlopen(req, timeout=10)
    except Exception as error:
        print("Telegram error:", error)


PAGE = r"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#f2e7d2">
<meta name="description" content="دعوت‌نامه عروسی امیر و زهرا">
<title>عروسی امیر و زهرا</title>

<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;500;600&family=Vazirmatn:wght@300;400;500;600;700&display=swap" rel="stylesheet">

<style>
:root {
    --paper: #f2e7d2;
    --paper-light: #fbf5e9;
    --paper-deep: #e7d6b8;
    --gold: #b99555;
    --gold-dark: #866633;
    --wine: #762f40;
    --wine-dark: #4c1c2a;
    --ink: #49382d;
    --muted: #89745e;
    --radius: 22px;
}

* { box-sizing: border-box; }

html {
    scroll-behavior: smooth;
    background: var(--paper);
}

body {
    margin: 0;
    overflow-x: hidden;
    color: var(--ink);
    font-family: "Vazirmatn", sans-serif;
    background:
        radial-gradient(ellipse at 15% 10%, rgba(255,255,255,.55), transparent 42%),
        radial-gradient(ellipse at 90% 85%, rgba(185,149,85,.12), transparent 40%),
        var(--paper);
}

body.locked { overflow: hidden; }

button, input, select { font: inherit; }
button { cursor: pointer; }

.nastaliq {
    font-family: "Noto Nastaliq Urdu", serif;
    font-weight: 500;
    line-height: 2.15;
}

.gold-text { color: var(--gold-dark); }

.ornament {
    text-align: center;
    color: var(--gold-dark);
    font-size: 19px;
    letter-spacing: 7px;
    margin: 16px 0;
}

/* بافت کاغذ */

.paper-texture {
    background-color: var(--paper-light);
    background-image:
        radial-gradient(rgba(111,77,39,.07) .6px, transparent .7px),
        radial-gradient(rgba(255,255,255,.4) .7px, transparent .8px),
        linear-gradient(135deg, rgba(255,255,255,.2), rgba(151,111,55,.035));
    background-size: 8px 8px, 13px 13px, 100% 100%;
}

/* ---------------- پاکت تمام صفحه ---------------- */

#intro {
    position: fixed;
    inset: 0;
    z-index: 1000;
    width: 100%;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    perspective: 1400px;
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
    background:
        radial-gradient(ellipse at 50% 40%, rgba(255,255,255,.5), transparent 65%),
        linear-gradient(145deg, #f8efdf, #e4d0ad);
    transform-style: preserve-3d;
}

.envelope::before {
    content: "";
    position: absolute;
    inset: 11px;
    border: 1px solid rgba(164,125,57,.8);
    box-shadow: inset 0 0 0 4px rgba(255,255,255,.2);
    z-index: 8;
    pointer-events: none;
}

.envelope::after {
    content: "";
    position: absolute;
    inset: 19px;
    border: 1px solid rgba(164,125,57,.28);
    z-index: 8;
    pointer-events: none;
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
    top: 24%;
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
    font-size: clamp(35px, 10vw, 55px);
    color: var(--wine);
    margin: 22px 0;
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
    filter: drop-shadow(2px -3px 5px rgba(75,50,25,.1));
}

.envelope-fold-right {
    right: 0;
    clip-path: polygon(100% 0, 100% 100%, 0 100%);
    filter: drop-shadow(-2px -3px 5px rgba(75,50,25,.1));
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

.envelope-flap::after {
    content: "";
    position: absolute;
    inset: 10px 10px 0;
    border-top: 1px solid rgba(189,152,82,.5);
}

/* مهر مومی ساده، بدون نوشته و نماد */

.seal-button {
    position: absolute;
    z-index: 10;
    top: 55%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 116px;
    height: 116px;
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
    outline-offset: 5px;
    transition: transform .3s ease, opacity .5s ease;
}

.seal-button::before {
    content: "";
    position: absolute;
    inset: 9px;
    border: 1px solid rgba(224,185,142,.3);
    border-radius: 48% 52% 47% 53% / 52% 46% 54% 48%;
    box-shadow: inset 0 0 8px rgba(35,0,10,.2);
}

.seal-button:active {
    transform: translate(-50%, -50%) scale(.94);
}

.open-hint {
    position: absolute;
    z-index: 8;
    top: calc(55% + 100px);
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

/* ---------------- صفحه اصلی ---------------- */

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
        radial-gradient(ellipse at 10% 5%, rgba(255,255,255,.5), transparent 35%),
        radial-gradient(ellipse at 90% 90%, rgba(189,152,82,.1), transparent 40%),
        var(--paper);
    box-shadow: 0 0 45px rgba(70,45,20,.1);
}

.page-paper::before {
    content: "";
    position: absolute;
    inset: 9px;
    border: 1px solid rgba(189,152,82,.65);
    border-radius: 5px;
    pointer-events: none;
    z-index: 10;
}

.page-paper::after {
    content: "";
    position: absolute;
    inset: 17px;
    border: 1px solid rgba(133,100,46,.2);
    border-radius: 4px;
    pointer-events: none;
    z-index: 10;
}

section {
    position: relative;
    padding: 68px 25px;
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

.hero-kicker {
    font-size: 13px;
    color: var(--muted);
    letter-spacing: 2px;
}

.hero-names {
    font-size: clamp(43px, 12vw, 68px);
    color: var(--wine);
    margin: 18px 0 6px;
}

.hero-and {
    color: var(--gold-dark);
    font-size: 20px;
    margin: 0;
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
    font-size: clamp(28px, 7vw, 39px);
    color: var(--wine);
    margin: 0 0 10px;
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

/* کارت‌های گرد و لطیف */

.ornate-card,
.address-card,
.rsvp-card {
    position: relative;
    padding: 30px 22px;
    margin: 27px auto;
    max-width: 550px;
    border: 1px solid rgba(185,149,85,.8);
    border-radius: 25px;
    background: rgba(255,250,239,.67);
    box-shadow: 0 10px 28px rgba(70,45,20,.08);
}

.ornate-card::before,
.ornate-card::after {
    content: "✧";
    position: absolute;
    color: var(--gold-dark);
    font-size: 19px;
}

.ornate-card::before { top: 10px; right: 15px; }
.ornate-card::after { bottom: 10px; left: 15px; }

/* ---------------- روزشمار ---------------- */

.countdown-card {
    max-width: 550px;
    margin: 30px auto;
    position: relative;
    padding: 34px 16px 28px;
    overflow: hidden;
    border: 1px solid var(--gold);
    border-radius: 28px;
    background: linear-gradient(145deg, #f8f0df, #e9d8b8);
    box-shadow: 0 12px 28px rgba(80,50,20,.1);
}

.countdown-title {
    font-size: 22px;
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
    border: 1px solid rgba(189,152,82,.7);
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
    box-shadow: inset 0 0 0 4px rgba(189,152,82,.08);
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

/* ---------------- عکس‌ها ---------------- */

.gallery-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 25px;
    max-width: 620px;
    margin: 32px auto 0;
}

.gallery-item {
    position: relative;
    width: 100%;
    padding: 9px;
    border-radius: 24px;
    background: linear-gradient(145deg, #fff8e9, #d8c194);
    border: 1px solid var(--gold);
    box-shadow: 0 12px 28px rgba(67,43,24,.13);
    transition: transform .45s ease, box-shadow .45s ease;
}

.gallery-item:nth-child(even) {
    transform: rotate(.5deg);
}

.gallery-item:nth-child(odd) {
    transform: rotate(-.5deg);
}

.gallery-item:hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 35px rgba(67,43,24,.18);
}

.gallery-item img {
    display: block;
    width: 100%;
    max-height: 620px;
    aspect-ratio: 4 / 3;
    object-fit: cover;
    border-radius: 17px;
    border: 1px solid rgba(133,100,46,.35);
    cursor: zoom-in;
}

.gallery-caption {
    font-family: "Noto Nastaliq Urdu", serif;
    color: var(--gold-dark);
    padding: 8px 0 2px;
    font-size: 15px;
}

#lightbox {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 2000;
    background: rgba(24,16,13,.93);
    align-items: center;
    justify-content: center;
    padding: 18px;
}

#lightbox.show { display: flex; }

#lightbox img {
    max-width: 96%;
    max-height: 88vh;
    object-fit: contain;
    border: 4px solid var(--gold);
    border-radius: 18px;
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

/* ---------------- ویدئو ---------------- */

.video-frame {
    max-width: 600px;
    margin: 28px auto;
    padding: 8px;
    background: linear-gradient(145deg, #e7d3a8, #a9823e);
    border-radius: 25px;
    box-shadow: 0 12px 28px rgba(70,45,20,.13);
}

.video-frame video {
    display: block;
    width: 100%;
    max-height: 560px;
    background: #241a18;
    border-radius: 18px;
}

/* ---------------- تاریخ ---------------- */

.calendar-card {
    width: min(100%, 350px);
    margin: 30px auto;
    overflow: hidden;
    border: 1px solid var(--gold);
    border-radius: 25px;
    background: #fbf4e7;
    box-shadow: 0 13px 28px rgba(67,43,24,.12);
    transform-style: preserve-3d;
}

.calendar-top {
    background: linear-gradient(120deg, var(--wine-dark), var(--wine));
    color: #f8e9c8;
    padding: 16px;
    font-size: 14px;
    letter-spacing: 2px;
}

.calendar-body { padding: 24px 12px; }

.calendar-day {
    font-size: 65px;
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

/* ---------------- آدرس ---------------- */

.address-icon {
    width: 68px;
    height: 68px;
    margin: 0 auto 17px;
    display: grid;
    place-items: center;
    border-radius: 50%;
    border: 1px solid var(--gold);
    outline: 1px solid rgba(189,152,82,.35);
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

/* ---------------- فرم پاسخ ---------------- */

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
    padding: 14px 13px;
    color: var(--ink);
    background: #fffaf0;
    border: 1px solid #c9ad76;
    border-radius: 14px;
    outline: none;
}

.form-group input:focus,
.form-group select:focus {
    border-color: var(--wine);
    box-shadow: 0 0 0 3px rgba(118,45,60,.08);
}

.submit-button {
    width: 100%;
    border-radius: 30px;
    font-weight: 500;
    font-size: 15px;
}

.success-message {
    color: #477044;
    background: #edf4e7;
    border: 1px solid #a9c59a;
    border-radius: 14px;
    padding: 13px;
    margin-bottom: 18px;
    font-size: 13px;
}

/* ---------------- پایان ---------------- */

.footer {
    padding: 55px 20px 75px;
    text-align: center;
    color: var(--muted);
}

.footer-names {
    font-size: 36px;
    color: var(--wine);
    margin: 8px 0;
}

.footer-heart {
    color: var(--wine);
    font-size: 25px;
}

/* ---------------- افکت اسکرول ---------------- */

.reveal {
    opacity: 0;
    transform: translateY(24px);
    transition: opacity .85s ease, transform .85s cubic-bezier(.2,.7,.2,1);
}

.reveal.visible {
    opacity: 1;
    transform: translateY(0);
}

@media (min-width: 560px) {
    .gallery-grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 22px;
    }

    .gallery-item img {
        aspect-ratio: 4 / 5;
    }
}

@media (max-width: 380px) {
    section { padding: 55px 20px; }
    .countdown-grid { gap: 4px; }
    .time-label { font-size: 9px; }
    .time-number { font-size: 21px; }
    .seal-button { width: 104px; height: 104px; }
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

        <button class="seal-button" id="openSeal" aria-label="باز کردن دعوت‌نامه"></button>
        <div class="open-hint">برای گشودن دعوت‌نامه لمس کنید</div>
    </div>
</div>

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

        <div class="scroll-cue">برای دیدن دعوت‌نامه به پایین بروید ↓</div>
    </section>

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

    <section>
        <div class="reveal">
            <div class="section-title nastaliq">لحظه‌های ما</div>
            <div class="divider-ornament">❦</div>
            <p class="section-subtitle">قاب‌هایی از خاطرات و لحظه‌های دوست‌داشتنی</p>
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
            <p class="section-subtitle">لطفاً ما را از افتخار حضورتان باخبر کنید</p>
        </div>

        <div class="rsvp-card reveal">
            {{SUCCESS}}

            <form method="POST" action="/">
                <div class="form-group">
                    <label for="guestName">نام و نام خانوادگی</label>
                    <input id="guestName" name="name" type="text"
                           placeholder="نام شما" maxlength="100" required>
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

                <button class="submit-button" type="submit">❦ ثبت پاسخ دعوت ❦</button>
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

const weddingDate = new Date("2026-12-23T19:00:00+03:30").getTime();

const persianDigits = number =>
    String(number).replace(/\d/g, d => "۰۱۲۳۴۵۶۷۸۹"[d]);

function updateCountdown() {
    let distance = Math.max(0, weddingDate - Date.now());

    const days = Math.floor(distance / 86400000);
    const hours = Math.floor((distance / 3600000) % 24);
    const minutes = Math.floor((distance / 60000) % 60);
    const seconds = Math.floor((distance / 1000) % 60);

    document.getElementById("days").textContent = persianDigits(days);
    document.getElementById("hours").textContent = persianDigits(hours);
    document.getElementById("minutes").textContent = persianDigits(minutes);
    document.getElementById("seconds").textContent = persianDigits(seconds);
}

updateCountdown();
setInterval(updateCountdown, 1000);


/* مه ظریف روزشمار */

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

        const gradient = ctx.createLinearGradient(0, 0, width, height);
        gradient.addColorStop(0, "rgba(241,229,205,.97)");
        gradient.addColorStop(.5, "rgba(231,216,187,.96)");
        gradient.addColorStop(1, "rgba(247,237,216,.97)");

        ctx.globalCompositeOperation = "source-over";
        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, width, height);

        ctx.fillStyle = "rgba(133,100,46,.1)";
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

        // شعاع کوچک‌تر برای پاک شدن ظریف‌تر مه
        const radius = 25;
        const gradient = ctx.createRadialGradient(
            point.x, point.y, 3,
            point.x, point.y, radius
        );

        gradient.addColorStop(0, "rgba(0,0,0,1)");
        gradient.addColorStop(.65, "rgba(0,0,0,.95)");
        gradient.addColorStop(1, "rgba(0,0,0,0)");

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
    }

    canvas.addEventListener("pointerdown", event => {
        drawing = true;
        lastPoint = getPoint(event);
        eraseAt(lastPoint);
    });

    canvas.addEventListener("pointermove", event => {
        if (!drawing) return;

        const point = getPoint(event);

        if (lastPoint) {
            const dx = point.x - lastPoint.x;
            const dy = point.y - lastPoint.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            const steps = Math.max(1, Math.ceil(distance / 10));

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
    canvas.addEventListener("pointerleave", stopDrawing);

    resizeCanvas();

    window.addEventListener("resize", resizeCanvas);
}


/* نمایان شدن بخش‌ها هنگام اسکرول */

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


/* افکت تقویم */

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

document.getElementById("closeLightbox").addEventListener("click", closeLightbox);

lightbox.addEventListener("click", event => {
    if (event.target === lightbox) closeLightbox();
});

document.addEventListener("keydown", event => {
    if (event.key === "Escape") closeLightbox();
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
                    <img src="/static/{safe_name}"
                         alt="تصویر خاطره {index}"
                         loading="lazy">
                    <div class="gallery-caption">خاطره‌ای از عشق</div>
                </div>
                """
            )

    if not items:
        return """
        <div class="ornate-card">
            <p>تصاویر زیبای شما به‌زودی در این قسمت قرار می‌گیرند.</p>
        </div>
        """

    return "\n".join(items)


def build_video():
    if not (STATIC_DIR / "wedding.mp4").exists():
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
                            "نام", "تعداد نفرات", "وضعیت حضور", "زمان ثبت"
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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
