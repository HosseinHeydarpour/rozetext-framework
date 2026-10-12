import subprocess
import sys
import time
import re
import os
import urllib.request

sys.stdout.reconfigure(encoding='utf-8')

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(BASE_DIR)

def is_server_running(port=8765):
    try:
        with urllib.request.urlopen(f"http://127.0.0.1:{port}/publisher.html", timeout=1) as resp:
            return resp.status == 200
    except Exception:
        return False

def start_server_if_needed():
    if not is_server_running():
        print("⚡ سرور داخلی در حال اجرا نبود؛ در حال راه‌اندازی سرور server.py...")
        subprocess.Popen([sys.executable, "server.py"], cwd=BASE_DIR)
        for _ in range(10):
            time.sleep(0.5)
            if is_server_running():
                print("✅ سرور داخلی با موفقیت روی پورت 8765 روشن شد.")
                return True
        print("⚠️ سرور با تأخیر مواجه شد اما فرآیند ادامه می‌یابد.")
    else:
        print("✅ سرور داخلی هم‌اکنون روی پورت 8765 فعال است.")
    return True

def get_local_ip():
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

def run_tunnel():
    start_server_if_needed()
    local_ip = get_local_ip()

    print("\n" + "=" * 65)
    print("🚀 در حال ساخت تونل اینترنتی امن برای دسترسی از روی موبایل...")
    print("=" * 65)

    cmd = ["ssh", "-o", "StrictHostKeyChecking=no", "-R", "80:127.0.0.1:8765", "serveo.net"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    except Exception as e:
        print(f"❌ خطا در اجرای SSH: {e}")
        return

    public_url = None
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        match = re.search(r"https://[a-zA-Z0-9_-]+\.serveousercontent\.com", line)
        if match:
            public_url = match.group(0)
            break

    if public_url:
        mobile_url = f"{public_url}/publisher.html"
        local_wifi_url = f"http://{local_ip}:8765/publisher.html"

        print("\n" + "🌟" * 30, flush=True)
        print("🎉 تونل امن با موفقیت ایجاد شد! لینک‌های دسترسی روی گوشی:", flush=True)
        print("🌟" * 30, flush=True)
        print(f"\n📱 لینک اینترنتی (از هر جای شهر با اینترنت سیم‌کارت گوشی):\n👉 {mobile_url}\n", flush=True)
        print(f"🏠 لینک شبکه خانگی (وقتی گوشی به همین وای‌فای وصل است):\n👉 {local_wifi_url}\n", flush=True)
        print("=" * 65, flush=True)
        print("💡 نکته: این پنجره را نبندید تا اتصال گوشی قطع نشود.", flush=True)
        print("برای توقف، کلیدهای Ctrl + C را فشار دهید.", flush=True)
        print("=" * 65 + "\n", flush=True)

        try:
            while True:
                time.sleep(1)
                if proc.poll() is not None:
                    print("⚠️ تونل قطع شد. در حال اتصال مجدد...")
                    run_tunnel()
                    break
        except KeyboardInterrupt:
            print("\n🛑 تونل با درخواست شما متوقف شد.")
            proc.terminate()
    else:
        print("❌ دریافت لینک تونل با خطا مواجه شد. در حال تلاش مجدد...")
        time.sleep(2)
        run_tunnel()

if __name__ == "__main__":
    run_tunnel()
