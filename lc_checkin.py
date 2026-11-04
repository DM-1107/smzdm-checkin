#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""嘉立创（m.jlc.com）每日签到。凭据：JLC_TOKEN（X-JLC-AccessToken，localStorage 里抓）。
接口取自 Foticing/LC-AutoSign（已审计，仅官方域）。"""
import json
import os
import random
import sys
import time
import urllib.request
import urllib.error

SIGN = "https://m.jlc.com/api/activity/sign/signIn?source=3"
ASSETS = "https://m.jlc.com/api/appPlatform/center/assets/selectPersonalAssetsInfo"
VOUCHER = "https://m.jlc.com/api/activity/sign/receiveVoucher"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Mobile/15E148")
EXIT_OK, EXIT_ALREADY, EXIT_TOKEN, EXIT_NET, EXIT_UNKNOWN = 0, 0, 2, 3, 4


def call(url: str, token: str) -> dict:
    req = urllib.request.Request(url, headers={
        "X-JLC-AccessToken": token, "User-Agent": UA, "Referer": "https://m.jlc.com/"})
    with urllib.request.urlopen(req, timeout=25) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def log_gain(row: dict):
    import csv, datetime, pathlib
    f = pathlib.Path("gains.csv")
    new = not f.exists()
    with f.open("a", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        if new:
            w.writerow(["date", "site", "status", "gain_beans", "voucher_balance", "note"])
        w.writerow([datetime.date.today().isoformat(), "jlc", row.get("status", ""),
                    row.get("gain_beans", 0), row.get("voucher", 0), row.get("note", "")])


def main() -> int:
    token = os.environ.get("JLC_TOKEN", "").strip().split(",")[0]
    if not token:
        print("缺少 JLC_TOKEN"); return EXIT_TOKEN
    time.sleep(random.uniform(0, 480))  # 0~8 分钟随机
    try:
        signed = call(SIGN, token)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}"); return EXIT_NET
    except Exception as e:
        print(f"网络异常 {type(e).__name__}: {e}"); return EXIT_NET
    print("签到响应:", json.dumps(signed, ensure_ascii=False)[:200])
    gain = signed.get("data", {}).get("gainNum", 0)
    status = signed.get("data", {}).get("status")
    voucher = 0
    try:
        assets = call(ASSETS, token)
        voucher = assets.get("data", {}).get("integralVoucher", 0)
    except Exception:
        pass
    row = {"status": "SUCCESS" if signed.get("success") else "FAIL",
           "gain_beans": gain, "voucher": voucher,
           "note": f"status={status}"}
    log_gain(row)
    if signed.get("success") and status in (0, 1):
        print(f"✅ 签到成功 +{gain} 金豆，打样券余额 ¥{voucher}")
        return EXIT_OK
    if "重复" in str(signed) or "已签" in str(signed):
        print("ℹ️ 今日已签"); return EXIT_ALREADY
    print("⚠️ 未识别响应"); return EXIT_UNKNOWN


if __name__ == "__main__":
    sys.exit(main())
