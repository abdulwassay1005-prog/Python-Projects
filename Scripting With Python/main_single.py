# FILE: main_single.py  (pure standard library, no external deps)
from __future__ import annotations

import argparse, os, json, time, re
from datetime import datetime, timezone
from collections import Counter

# ---------- small helpers ----------
MENTION_RE = re.compile(r'@(\w+)', re.I)
HASHTAG_RE = re.compile(r'#(\w+)', re.I)

def extract_hashtags(text: str):
    return [h.lower() for h in HASHTAG_RE.findall(text or "")]

def contains_any(text: str, keywords: list[str]):
    t = (text or "").lower()
    return any(k.lower() in t for k in keywords)

def ensure_paths(root: str):
    paths = [
        os.path.join(root, "bot"),
        os.path.join(root, "data"),
    ]
    for p in paths:
        os.makedirs(p, exist_ok=True)

    # seed timeline
    seed_path = os.path.join(root, "data", "seed_timeline.json")
    if not os.path.exists(seed_path):
        seed_timeline = [
            {"id":"t1","user":"ali","text":"Hello world! Learning Python today. #python #learning","mentions":["@SimpleBot"],"timestamp":"2025-09-01T10:15:00"},
            {"id":"t2","user":"sara","text":"Any tips for study routine? #help #students","mentions":[], "timestamp":"2025-09-01T11:20:00"},
            {"id":"t3","user":"hamza","text":"Shukriya for the guide, folks! #gratitude","mentions":["@SimpleBot"],"timestamp":"2025-09-01T12:05:00"},
            {"id":"t4","user":"zain","text":"Madad chahiye VS Code extensions ke liye. #help","mentions":["@SimpleBot"],"timestamp":"2025-09-01T13:40:00"},
            {"id":"t5","user":"noor","text":"Hi everyone! First day of coding. #python","mentions":[], "timestamp":"2025-09-01T14:00:00"},
        ]
        with open(seed_path, "w", encoding="utf-8") as f:
            json.dump(seed_timeline, f, indent=2)

    # outbox
    outbox_path = os.path.join(root, "bot", "outbox.json")
    if not os.path.exists(outbox_path):
        with open(outbox_path, "w", encoding="utf-8") as f:
            json.dump({"posts": []}, f, indent=2)

    # schedule
    schedule_path = os.path.join(root, "bot", "schedule.json")
    if not os.path.exists(schedule_path):
        with open(schedule_path, "w", encoding="utf-8") as f:
            json.dump({"scheduled": []}, f, indent=2)

class MockTwitter:
    def __init__(self, root: str):
        self.root = root
        self.timeline_path = os.path.join(root, "data", "seed_timeline.json")
        self.outbox_path = os.path.join(root, "bot", "outbox.json")
        with open(self.timeline_path, "r", encoding="utf-8") as f:
            self.timeline = json.load(f)

    def get_timeline(self, limit=None):
        tl = list(self.timeline)
        return tl[:limit] if limit else tl

    def get_mentions_for(self, handle: str):
        handle = handle.lower().lstrip("@")
        results = []
        for t in self.timeline:
            mentions = [m.lower().lstrip("@") for m in (t.get("mentions") or [])]
            if handle in mentions:
                results.append(t)
        return results

    def post(self, text: str, meta=None):
        item = {
            "id": f"p{int(datetime.now(tz=timezone.utc).timestamp())}",
            "user": "SimpleBot",
            "text": text,
            "timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "meta": meta or {},
        }
        with open(self.outbox_path, "r+", encoding="utf-8") as f:
            box = json.load(f)
            box["posts"].append(item)
            f.seek(0); json.dump(box, f, indent=2); f.truncate()
        return item

def auto_replies(items, reply_rules, max_replies=5):
    replies = []
    for t in items:
        txt = (t.get("text") or "").strip()
        for rule in reply_rules:
            if contains_any(txt, rule["keywords"]):
                replies.append({"to": t["user"], "text": rule["reply"]})
                break
        if len(replies) >= max_replies:
            break
    return replies

def trending_hashtags(items, top_k=10):
    c = Counter()
    for t in items:
        for tag in extract_hashtags(t.get("text", "")):
            c[tag] += 1
    return c.most_common(top_k)

class Bot:
    def __init__(self, root: str):
        self.root = root
        self.driver = MockTwitter(root)
        # Hard-coded rules (no YAML needed)
        self.name = "SimpleBot"
        self.rules = [
            {"keywords": ["hello", "salam", "hi"], "reply": "Wa alaikum salam! 👋 SimpleBot here."},
            {"keywords": ["help", "guide", "madad"], "reply": "Need help? Use #help and I’ll try to assist."},
            {"keywords": ["python", "code"], "reply": "Python is love 🐍 — keep coding!"},
            {"keywords": ["thanks", "shukriya"], "reply": "You're welcome! ✨"},
        ]
        self.max_auto = 5
        self.trend_window = 50

    def process_timeline(self, limit=None):
        items = self.driver.get_timeline(limit)
        replies = auto_replies(items, self.rules, self.max_auto)
        for r in replies:
            self.driver.post(f"@{r['to']} {r['text']}", meta={"type": "auto-reply"})
        return replies

    def process_mentions(self):
        mentions = self.driver.get_mentions_for(self.name)
        replies = auto_replies(mentions, self.rules, self.max_auto)
        for r in replies:
            self.driver.post(f"@{r['to']} {r['text']}", meta={"type": "mention-reply"})
        return replies

    def trends(self, top_k=10):
        items = self.driver.get_timeline(limit=self.trend_window)
        return trending_hashtags(items, top_k)

    def post(self, text: str):
        return self.driver.post(text, meta={"type": "manual"})

    def schedule_add(self, at_hhmm: str, text: str):
        path = os.path.join(self.root, "bot", "schedule.json")
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        data["scheduled"].append({"at": at_hhmm, "text": text, "posted_today": False})
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def scheduler_loop(self, tick_seconds=30):
        path = os.path.join(self.root, "bot", "schedule.json")
        last_day = datetime.now().date()
        print("Scheduler running (Ctrl+C to stop)...")
        while True:
            now = datetime.now()
            if now.date() != last_day:
                with open(path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for s in data["scheduled"]:
                    s["posted_today"] = False
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
                last_day = now.date()

            hhmm = now.strftime("%H:%M")
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            changed = False
            for s in data["scheduled"]:
                if s.get("at") == hhmm and not s.get("posted_today", False):
                    self.post(s["text"])
                    s["posted_today"] = True
                    changed = True
            if changed:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=2)
            time.sleep(tick_seconds)

# ---------- CLI ----------
def make_bot():
    root = os.path.dirname(os.path.abspath(__file__))
    ensure_paths(root)
    return Bot(root)

def cmd_run(args):
    bot = make_bot()
    did = False
    if args.process_timeline:
        replies = bot.process_timeline()
        print(f"Timeline processed: {len(replies)} auto-replies posted")
        did = True
    if args.process_mentions:
        replies = bot.process_mentions()
        print(f"Mentions processed: {len(replies)} mention-replies posted")
        did = True
    if not did:
        print("Nothing to do. Add --process-timeline or --process-mentions")

def cmd_trends(args):
    bot = make_bot()
    top = bot.trends(top_k=args.top)
    print("Top Hashtags")
    for tag, count in top:
        print(f"- #{tag}: {count}")

def cmd_post(args):
    bot = make_bot()
    post = bot.post(args.text)
    print(f"Posted: {post['text']} at {post['timestamp']}")

def cmd_schedule(args):
    bot = make_bot()
    bot.schedule_add(args.at, args.text)
    print(f"Scheduled: '{args.text}' at {args.at} (daily)")
    if args.run_loop:
        try:
            bot.scheduler_loop(tick_seconds=args.tick)
        except KeyboardInterrupt:
            print("\nScheduler stopped by user")

def build_parser():
    p = argparse.ArgumentParser(description="Simple Twitter Bot (offline simulator, single-file)")
    sub = p.add_subparsers(dest="cmd")

    prun = sub.add_parser("run", help="Process timeline and/or mentions using auto-reply rules")
    prun.add_argument("--process-timeline", action="store_true")
    prun.add_argument("--process-mentions", action="store_true")
    prun.set_defaults(func=cmd_run)

    ptr = sub.add_parser("trends", help="Show trending hashtags from mock timeline")
    ptr.add_argument("--top", type=int, default=10)
    ptr.set_defaults(func=cmd_trends)

    ppost = sub.add_parser("post", help="Post a message immediately (to outbox)")
    ppost.add_argument("--text", required=True)
    ppost.set_defaults(func=cmd_post)

    ps = sub.add_parser("schedule", help="Schedule a daily post at HH:MM")
    ps.add_argument("--at", required=True, help="HH:MM (24h)")
    ps.add_argument("--text", required=True)
    ps.add_argument("--run-loop", action="store_true", help="Run the scheduler loop after adding")
    ps.add_argument("--tick", type=int, default=30, help="Scheduler tick seconds")
    ps.set_defaults(func=cmd_schedule)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
