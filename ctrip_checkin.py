#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""携程每日签到（云端 Actions 版）。凭据：CTRIP_TICKET（可选 CTRIP_UID）。"""
import json
import os
import random
import sys
import time
import urllib.request
import urllib.error

URL = "https://m.ctrip.com/restapi/soa2/22769/signToday"
UA = ("Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 "
      "(KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1")
EXIT_OK, EXIT_ALREADY, EXIT_COOKIE, EXIT_NET, EXIT_UNKNOWN = 0, 0, 2, 3, 4


def sign(ticket: str, uid: str = ""):
    body = json.dumps({"openId": ""}).encode()
    req = urllib.request.Request(URL, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Cookie": f"cticket={ticket}; login_uid={uid}" if uid else f"cticket={ticket}",
        "User-Agent": UA,
        "Referer": "https://m.ctrip.com/activitysetupapp/mkt/index/membersignin2021",
        "Origin": "https://m.ctrip.com",
    })
    with urllib.request.urlopen(req, timeout=25) as r:
        return r.status, json.loads(r.read().decode("utf-8", "replace"))


def main() -> int:
    ticket = os.environ.get("CTRIP_TICKET", "").strip()
    uid = os.environ.get("CTRIP_UID", "").strip()
    if not ticket:
        print("缺少 CTRIP_TICKET"); return EXIT_COOKIE
    # 打散执行时刻（0~10 分钟），避开整点
    time.sleep(random.uniform(0, 600))
    try:
        st, data = sign(ticket, uid)
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code}: {e.read().decode('utf-8','replace')[:200]}"); return EXIT_NET
    except Exception as e:
        print(f"网络异常 {type(e).__name__}: {e}"); return EXIT_NET

    code = str(data.get("code"))
    msg = str(data.get("message", ""))
    day = data.get("continueDay", "")
    print(f"HTTP {st} | code={code} | {msg} | 连续{day}天")
    if code == "0":
        print("✅ 签到成功"); return EXIT_OK
    if "已签" in msg or "重复" in msg:
        print("ℹ️ 今日已签"); return EXIT_ALREADY
    if "登录" in msg or code in ("404001",):
        print("❌ cticket 失效，需重新打开签到活动页获取"); return EXIT_COOKIE
    print(f"⚠️ 未识别响应：{json.dumps(data, ensure_ascii=False)[:200]}")
    return EXIT_UNKNOWN


if __name__ == "__main__":
    sys.exit(main())
