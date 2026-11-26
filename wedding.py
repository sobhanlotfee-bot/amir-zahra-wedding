
import os
import csv
import sqlite3
from datetime import datetime
from flask import Flask, request, redirect, session, render_template_string, Response
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key")
DB = os.environ.get("DATABASE_PATH", "wedding.db")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "ChangeMe123!")

WEDDING_DATE = "2026-12-23T19:00:00+03:30"
ADDRESS = "استان سمنان، میدان معلم، بلوار بسیج، جنب ورزشگاه الغدیر"

def db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with db() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS guests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            count INTEGER NOT NULL,
            status TEXT NOT NULL,
            created TEXT
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            message TEXT NOT NULL,
            created TEXT
        )""")

init_db()

PAGE = """
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>دعوت‌نامه عروسی امیر و زهرا</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#f8f1e8;color:#514033;font-family:Tahoma,Arial;text-align:center}
header{padding:65px 15px;background:linear-gradient(135deg,#fffaf2,#ead8c2)}
h1{font-size:38px;color:#a77b42;margin:15px}
h2{color:#a77b42}
section{max-width:720px;margin:25px auto;padding:25px;background:#fffdf9;border:1px solid #d9bd91;border-radius:18px;box-shadow:0 8px 25px #8b6b3920}
button{background:#a77b42;color:white;border:0;padding:12px 25px;border-radius:25px;cursor:pointer}
input,textarea,select{width:100%;padding:12px;margin:8px 0;border:1px solid #d8c4a7;border-radius:10px;font:inherit}
a{color:#9b713c}
#countdown{font-size:24px;color:#a77b42;font-weight:bold}
.gallery{display:grid;grid-template-columns:repeat(2,1fr);gap:10px}
.gallery img,.gallery video{width:100%;border-radius:12px}
.flower{position:fixed;top:-20px;animation:fall 8s linear infinite;pointer-events:none}
@keyframes fall{to{transform:translateY(110vh) rotate(360deg)}}
</style>
</head>
<body>
<header>
<div style="font-size:45px">❀</div>
<p>دعوت‌نامه جشن پیوند</p>
<h1>امیر و زهرا</h1>
<p>با کمال افتخار از شما دعوت می‌کنیم در جشن پیوند و آغاز زندگی مشترک امیر و زهرا، در کنار ما باشید.</p>
<button onclick="document.getElementById('invite').scrollIntoView({behavior:'smooth'})">مشاهده دعوت‌نامه</button>
</header>

<section id="invite">
<h2>شمارش معکوس تا آغاز زندگی مشترک</h2>
<div id="countdown">در حال محاسبه...</div>
<h2>چهارشنبه، ۲ دی ۱۴۰۵</h2>
<p>ساعت ۱۹:۰۰ تا ۲۲:۰۰</p>
<p>تالار پذیرایی فریال</p>
<p>{{ address }}</p>
<a target="_blank" href="https://www.google.com/maps/search/?api=1&query=تالار+پذیرایی+فریال+سمنان">مشاهده نقشه</a>
<p><a href="/calendar">افزودن مراسم به تقویم</a></p>
</section>

<section>
<h2>لحظه‌های ما</h2>
<div class="gallery">
{% for i in range(1,7) %}
<img src="/static/photo{{i}}.jpg" alt="عکس خاطره">
{% endfor %}
<video controls playsinline src="/static/wedding.mp4"></video>
</div>
</section>

<section>
<h2>ثبت پاسخ دعوت</h2>
<form method="post" action="/rsvp">
<input name="name" placeholder="نام و نام خانوادگی" required>
<input name="count" type="number" min="1" max="20" value="1" required>
<select name="status">
<option value="حضور دارم">با افتخار حضور دارم</option>
<option value="متأسفانه نمی‌توانم">متأسفانه نمی‌توانم حضور داشته باشم</option>
</select>
<button type="submit">ثبت پاسخ</button>
</form>
</section>

<section>
<h2>دفتر یادبود</h2>
<form method="post" action="/message">
<input name="name" placeholder="نام شما" required>
<textarea name="message" placeholder="پیام و آرزوی زیبای شما..." required></textarea>
<button type="submit">ثبت پیام</button>
</form>
{% for m in messages %}
<p>🌹 <b>{{m.name}}</b>: {{m.message}}</p>
{% endfor %}
</section>

<section>
<h2>با مهر، امیر و زهرا</h2>
<p>از اینکه در شادی ما شریک هستید سپاسگزاریم.</p>
<p><a href="/qr.png">نمایش کد QR دعوت‌نامه</a></p>
</section>

<script>
const target = new Date("2026-12-23T19:00:00+03:30").getTime();
function update(){
 let diff=target-Date.now();
 if(diff<=0){document.getElementById("countdown").textContent="روز جشن فرا رسیده است!";return;}
 let d=Math.floor(diff/86400000);
 let h=Math.floor(diff%86400000/3600000);
 let m=Math.floor(diff%3600000/60000);
 let s=Math.floor(diff%60000/1000);
 document.getElementById("countdown").textContent=`${d} روز و ${h} ساعت و ${m} دقیقه و ${s} ثانیه`;
}
update();setInterval(update,1000);
for(let i=0;i<12;i++){
 let f=document.createElement("div");f.className="flower";f.textContent="✿";
 f.style.left=Math.random()*100+"%";f.style.animationDelay=Math.random()*8+"s";
 document.body.appendChild(f);
}
</script>
</body>
</html>
"""

@app.route("/")
def home():
    with db() as con:
        messages = con.execute(
            "SELECT name,message FROM messages ORDER BY id DESC LIMIT 30"
        ).fetchall()
    return render_template_string(PAGE, address=ADDRESS, messages=messages)

@app.route("/rsvp", methods=["POST"])
def rsvp():
    name = request.form.get("name", "").strip()[:100]
    status = request.form.get("status", "حضور دارم")[:50]
    try:
        count = max(1, min(20, int(request.form.get("count", 1))))
    except ValueError:
        count = 1
    if name:
        with db() as con:
            con.execute(
                "INSERT INTO guests(name,count,status,created) VALUES(?,?,?,?)",
                (name, count, status, datetime.now().isoformat())
            )
    return redirect("/")

@app.route("/message", methods=["POST"])
def message():
    name = request.form.get("name", "").strip()[:100]
    msg = request.form.get("message", "").strip()[:500]
    if name and msg:
        with db() as con:
            con.execute(
                "INSERT INTO messages(name,message,created) VALUES(?,?,?)",
                (name, msg, datetime.now().isoformat())
            )
    return redirect("/")

@app.route("/calendar")
def calendar():
    content = """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Amir and Zahra//Wedding//FA
BEGIN:VEVENT
DTSTART:20261223T153000Z
DTEND:20261223T183000Z
SUMMARY:Wedding of Amir and Zahra
LOCATION:Talare Ferial, Semnan, Iran
END:VEVENT
END:VCALENDAR"""
    return Response(content, mimetype="text/calendar",
                    headers={"Content-Disposition":"attachment; filename=wedding.ics"})

@app.route("/qr.png")
def qr():
    import qrcode
    from io import BytesIO
    img = qrcode.make(request.url_root)
    output = BytesIO()
    img.save(output, format="PNG")
    return Response(output.getvalue(), mimetype="image/png")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password", "")
        if check_password_hash(ADMIN_PASSWORD, password) if ADMIN_PASSWORD.startswith("pbkdf2:") else password == ADMIN_PASSWORD:
            session["admin"] = True
            return redirect("/admin/panel")
    return """<form method="post"><h2>ورود مدیریت</h2>
    <input type="password" name="password" placeholder="رمز مدیریت">
    <button>ورود</button></form>"""

@app.route("/admin/panel")
def panel():
    if not session.get("admin"):
        return redirect("/admin")
    with db() as con:
        guests = con.execute("SELECT * FROM guests ORDER BY id DESC").fetchall()
    rows = "".join(
        f"<tr><td>{g['name']}</td><td>{g['count']}</td><td>{g['status']}</td></tr>"
        for g in guests
    )
    return f"""<h2>مهمان‌ها</h2><table border="1">
    <tr><th>نام</th><th>تعداد</th><th>وضعیت</th></tr>{rows}</table>
    <p><a href="/admin/export">دریافت فایل CSV</a></p>
    <a href="/admin/logout">خروج</a>"""

@app.route("/admin/export")
def export():
    if not session.get("admin"):
        return redirect("/admin")
    with db() as con:
        guests = con.execute("SELECT name,count,status,created FROM guests").fetchall()
    output = "نام,تعداد,وضعیت,تاریخ\n"
    for g in guests:
        output += ",".join('"' + str(x).replace('"','""') + '"' for x in g) + "\n"
    return Response("\ufeff" + output, mimetype="text/csv",
                    headers={"Content-Disposition":"attachment; filename=guests.csv"})

@app.route("/admin/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == "__main__":
    app.run()
