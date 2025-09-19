sudo apt update && sudo apt upgrade -y && \
sudo apt install -y python3 python3-pip python3-venv && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install pyTelegramBotAPI psutil requests speedtest-cli requests && \
python bot.py




#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import subprocess
import time
import random
import threading
import psutil
import platform
import telebot
from telebot import types

# ==============================
# 🔧 KONFIGURASI
# ==============================
TOKEN = "8210971207:AAGyKHLKgYixobM0Ww2oNZN9sR5J6fs1SfQ"
ALLOWED_USER_IDS = [231997940]
HOSTNAME = platform.node()
bot = telebot.TeleBot(TOKEN, parse_mode="HTML")

# ==============================
# GLOBAL STATE
# ==============================
heartbeat_running = False
monitor_running = False
bandwidth_running = False
HEARTBEAT_EMOJIS = ["💓","⚡","🔥","✨","🔋","🟢"]
prev_bytes_sent = psutil.net_io_counters().bytes_sent
prev_bytes_recv = psutil.net_io_counters().bytes_recv
prev_time = time.time()

# ==============================
# 🌊 ANIMASI WAVE LOADING
# ==============================
def wave_loading():
    text = "LOADING..."
    wave = ["_", "^", "~", ""]
    idx = 0
    while True:
        sys.stdout.write("\033c")
        animated = "".join(ch + wave[(idx + i) % len(wave)] for i, ch in enumerate(text))
        print(f"[{HOSTNAME}] Bot VPS Aktif!\n{animated}")
        idx += 1
        time.sleep(0.2)

# ==============================
# 💓 HEARTBEAT
# ==============================
def heartbeat_loop(interval=60):
    global heartbeat_running
    while heartbeat_running:
        emoji = random.choice(HEARTBEAT_EMOJIS)
        for uid in ALLOWED_USER_IDS:
            try:
                bot.send_message(uid, f"[{HOSTNAME}] {emoji} Bot masih aktif...")
            except Exception as e:
                print(f"Heartbeat error: {e}")
        time.sleep(interval)

# ==============================
# 🖥 HARDWARE INFO
# ==============================
def get_hardware_info():
    cpu_model = platform.processor() or "Unknown CPU"
    cpu_cores = psutil.cpu_count(logical=True)
    ram_gb = round(psutil.virtual_memory().total / (1024**3), 2)
    disk_gb = round(psutil.disk_usage('/').total / (1024**3), 2)
    try:
        gpu_info = subprocess.check_output(
            "nvidia-smi --query-gpu=name --format=csv,noheader",
            shell=True, text=True
        ).split("\n")[0]
    except Exception:
        gpu_info = "Tidak terdeteksi"
    os_name = platform.system()
    kernel = platform.release()
    arch = platform.machine()
    return (
        f"[{HOSTNAME}] 🖥 <b>Hardware Info</b>:\n"
        f"• CPU: {cpu_model} ({cpu_cores} thread)\n"
        f"• RAM: {ram_gb} GB\n"
        f"• Disk: {disk_gb} GB\n"
        f"• GPU: {gpu_info}\n"
        f"• OS: {os_name}\n"
        f"• Kernel: {kernel}\n"
        f"• Arsitektur: {arch}"
    )

# ==============================
# 📊 MONITOR REALTIME
# ==============================
def usage_bar(percent, length=10):
    filled = int(percent/100*length)
    empty = length - filled
    return "█"*filled + "░"*empty

def get_realtime_status():
    cpu_usage = psutil.cpu_percent(interval=1)
    vm = psutil.virtual_memory()
    ram_used = round(vm.used/(1024**3),2)
    ram_total = round(vm.total/(1024**3),2)
    du = psutil.disk_usage('/')
    disk_used = round(du.used/(1024**3),2)
    disk_total = round(du.total/(1024**3),2)
    try:
        load1, load5, load15 = os.getloadavg()
        loadavg = f"{load1:.2f}, {load5:.2f}, {load15:.2f}"
    except:
        loadavg = "N/A"
    uptime_hr = round((time.time() - psutil.boot_time())/3600,2)
    try:
        screen_list = subprocess.check_output("screen -ls", shell=True, text=True)
    except:
        screen_list = "Tidak ada/tidak terdeteksi"
    return (
        f"[{HOSTNAME}] 📊 <b>Status Realtime</b>:\n"
        f"• CPU Usage: {cpu_usage}% [{usage_bar(cpu_usage)}]\n"
        f"• RAM Usage: {ram_used}/{ram_total} GB [{usage_bar(ram_used/ram_total*100)}]\n"
        f"• Disk Usage: {disk_used}/{disk_total} GB\n"
        f"• Load Avg: {loadavg}\n"
        f"• Uptime: {uptime_hr} jam\n"
        f"• Screen:\n<pre>{screen_list.strip()}</pre>"
    )

def monitor_loop(interval=60):
    global monitor_running
    while monitor_running:
        for uid in ALLOWED_USER_IDS:
            try:
                bot.send_message(uid, get_realtime_status())
            except Exception as e:
                print(f"Monitor error: {e}")
        time.sleep(interval)

# ==============================
# 🌐 BANDWIDTH
# ==============================
def get_bandwidth_status():
    global prev_bytes_sent, prev_bytes_recv, prev_time
    current_time = time.time()
    net = psutil.net_io_counters()
    sent, recv = net.bytes_sent, net.bytes_recv
    interval = current_time - prev_time
    upload_speed = (sent - prev_bytes_sent) / interval
    download_speed = (recv - prev_bytes_recv) / interval
    prev_bytes_sent, prev_bytes_recv, prev_time = sent, recv, current_time
    upload_mbps = upload_speed / (1024**2)
    download_mbps = download_speed / (1024**2)
    return (
        f"[{HOSTNAME}] 🌐 <b>Bandwidth VPS</b>:\n"
        f"• Upload: {upload_mbps:.2f} MB/s\n"
        f"• Download: {download_mbps:.2f} MB/s"
    )

def bandwidth_loop(interval=60):
    global bandwidth_running
    while bandwidth_running:
        for uid in ALLOWED_USER_IDS:
            try:
                bot.send_message(uid, get_bandwidth_status())
            except Exception as e:
                print(f"Bandwidth error: {e}")
        time.sleep(interval)

# ==============================
# ⏱ UPTIME VPS
# ==============================
def get_uptime():
    uptime_seconds = time.time() - psutil.boot_time()
    days=int(uptime_seconds//86400)
    hours=int((uptime_seconds%86400)//3600)
    minutes=int((uptime_seconds%3600)//60)
    seconds=int(uptime_seconds%60)
    return f"{days} hari, {hours} jam, {minutes} menit, {seconds} detik"

# ==============================
# 🐳 DOCKER AKTIF
# ==============================
def get_docker_status():
    try:
        output = subprocess.check_output(
            "docker ps --format 'table {{.Names}}\t{{.Status}}'",
            shell=True, text=True
        )
        if not output.strip():
            output = "Tidak ada container berjalan"
    except:
        output = "Docker tidak terinstall/tidak terdeteksi"
    return f"[{HOSTNAME}] 🐳 <b>Docker Aktif</b>:\n<pre>{output}</pre>"

# ==============================
# 🖥 SCREEN AKTIF
# ==============================
def get_screen_status():
    try:
        output = subprocess.check_output("screen -ls", shell=True, text=True)
        if not output.strip():
            output = "Tidak ada screen session"
    except:
        output = "Screen tidak terdeteksi"
    return f"[{HOSTNAME}] 🖥 <b>Screen Aktif</b>:\n<pre>{output}</pre>"

# ==============================
# 💻 CMD CUSTOM
# ==============================
def run_cmd(message):
    try:
        output = subprocess.check_output(message.text, shell=True, stderr=subprocess.STDOUT, text=True, timeout=10)
        if not output.strip():
            output = "(Tidak ada output)"
    except Exception as e:
        output = str(e)
    if len(output) > 3500:
        output = output[:3500] + "\n...(terpotong)"
    bot.reply_to(message, f"<pre>{output}</pre>")

# ==============================
# ℹ️ ABOUT ME
# ==============================
def about_me_message():
    return (
        f"[{HOSTNAME}] ℹ️ <b>About Me</b>\n"
        "• Developer: Maskurniawan\n"
        "• Telegram: @maskurniwan1\n"
        "• Versi Bot: 1.0\n"
        "• Tujuan: Monitoring VPS & Info Hardware\n"
        "• Sistem: Multi-VPS Compatible"
    )

# ==============================
# 📜 HANDLER MENU
# ==============================
@bot.message_handler(commands=["start","menu"])
def main_menu(message):
    if message.from_user.id not in ALLOWED_USER_IDS:
        return bot.reply_to(message,"⛔ Kamu tidak diizinkan.")
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("💓 Start Heartbeat","💔 Stop Heartbeat")
    markup.add("📊 Start Monitor","⏹ Stop Monitor")
    markup.add("📡 Start Bandwidth","⏹ Stop Bandwidth")
    markup.add("🖥 Hardware Info","⏱ Uptime VPS")
    markup.add("🖥 Screen Aktif","🐳 Docker Aktif","💻 CMD Custom")
    markup.add("ℹ️ About Me","⬅️ Kembali")
    bot.reply_to(message,f"[{HOSTNAME}] 🤖 Pilih menu:",reply_markup=markup)

@bot.message_handler(func=lambda msg: True)
def handle_menu(message):
    global heartbeat_running, monitor_running, bandwidth_running
    text = message.text

    if text == "💓 Start Heartbeat":
        if not heartbeat_running:
            heartbeat_running=True
            threading.Thread(target=heartbeat_loop, daemon=True).start()
            bot.reply_to(message,f"[{HOSTNAME}] ✅ Heartbeat dimulai.")
        else:
            bot.reply_to(message,f"[{HOSTNAME}] ❗ Heartbeat sudah berjalan.")

    elif text == "💔 Stop Heartbeat":
        heartbeat_running=False
        bot.reply_to(message,f"[{HOSTNAME}] ⛔ Heartbeat dihentikan.")

    elif text == "📊 Start Monitor":
        if not monitor_running:
            monitor_running=True
            threading.Thread(target=monitor_loop, daemon=True).start()
            bot.reply_to(message,f"[{HOSTNAME}] ✅ Monitor Realtime dimulai tiap 60 detik.")
        else:
            bot.reply_to(message,f"[{HOSTNAME}] ❗ Monitor sudah Active")

    elif text == "⏹ Stop Monitor":
        monitor_running=False
        bot.reply_to(message,f"[{HOSTNAME}] ⛔ Monitor Stop.")

    elif text == "📡 Start Bandwidth":
        if not bandwidth_running:
            bandwidth_running=True
            threading.Thread(target=bandwidth_loop, daemon=True).start()
            bot.reply_to(message,f"[{HOSTNAME}] ✅ Bandwidth monitor dimulai tiap 60 detik.")
        else:
            bot.reply_to(message,f"[{HOSTNAME}] ❗ Bandwidth sudah berjalan.")

    elif text == "⏹ Stop Bandwidth":
        bandwidth_running=False
        bot.reply_to(message,f"[{HOSTNAME}] ⛔ Bandwidth monitor dihentikan.")

    elif text == "🖥 Hardware Info":
        bot.reply_to(message,get_hardware_info())

    elif text == "⏱ Uptime VPS":
        bot.reply_to(message,get_uptime())

    elif text == "🖥 Screen Aktif":
        bot.reply_to(message,get_screen_status())

    elif text == "🐳 Docker Aktif":
        bot.reply_to(message,get_docker_status())

    elif text == "💻 CMD Custom":
        msg = bot.reply_to(message,f"[{HOSTNAME}] 💻 Masukkan perintah shell:")
        bot.register_next_step_handler(msg, run_cmd)

    elif text == "ℹ️ About Me":
        bot.reply_to(message, about_me_message())

    elif text == "⬅️ Kembali":
        main_menu(message)

    else:
        bot.reply_to(message,"⚠️ Menu belum tersedia.")

# ==============================
# 🚀 MAIN
# ==============================
if __name__=="__main__":
    threading.Thread(target=wave_loading, daemon=True).start()
    print(f"[{HOSTNAME}] 🚀 Bot VPS Running...")
    bot.infinity_polling()
