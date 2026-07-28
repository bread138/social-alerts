#!/usr/bin/env python3
"""
Social media post checker for tradesbysci.
Checks Instagram, X (Twitter), and YouTube for new posts and fires
a push notification via ntfy.sh the moment something new is found.

State (last-seen post IDs) is stored in state.json and committed back
to the repo by the GitHub Actions workflow so it persists between runs.
"""

import json
import os
import sys
import requests
import feedparser

STATE_FILE = "state.json"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "braden-alerts-tradesbysci-all")
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

USERNAMES = {
    "instagram": "tradesbysci",
    "twitter": "tradesbysci",
    "youtube_channel_id": "UClsS3T1SnsX__1g9COtfKCQ",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def send_alert(platform, message, url=None):
    body = message
    headers = {"Title": f"New {platform} post — tradesbysci".encode("utf-8")}
    if url:
        headers["Click"] = url
    try:
        requests.post(NTFY_URL, data=body.encode("utf-8"), headers=headers, timeout=15)
        print(f"[ALERT SENT] {platform}: {message}")
    except Exception as e:
        print(f"[ERROR] Failed to send ntfy alert for {platform}: {e}")


def check_youtube(state):
    channel_id = USERNAMES["youtube_channel_id"]
    feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
    try:
        feed = feedparser.parse(feed_url)
        if not feed.entries:
            print("[YouTube] No entries found.")
            return
        latest = feed.entries[0]
        latest_id = latest.get("yt_videoid") or latest.get("id")
        last_seen = state.get("youtube")
        if latest_id != last_seen:
            if last_seen is not None:  # don't alert on first-ever run
                send_alert("YouTube", latest.get("title", "New video"), latest.get("link"))
            state["youtube"] = latest_id
    except Exception as e:
        print(f"[ERROR] YouTube check failed: {e}")


def check_instagram(state):
    username = USERNAMES["instagram"]
    url = f"https://www.instagram.com/{username}/"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"[Instagram] Non-200 response: {resp.status_code} (likely blocked/login wall)")
            return
        html = resp.text
        # Instagram embeds post data in a JSON blob within <script type="application/ld+json">
        # This is fragile and may need updating if Instagram changes its page structure.
        marker = '"shortcode":"'
        idx = html.find(marker)
        if idx == -1:
            print("[Instagram] Could not locate post data in page — Instagram may be blocking this request.")
            return
        start = idx + len(marker)
        end = html.find('"', start)
        latest_shortcode = html[start:end]
        last_seen = state.get("instagram")
        if latest_shortcode != last_seen:
            if last_seen is not None:
                post_url = f"https://www.instagram.com/p/{latest_shortcode}/"
                send_alert("Instagram", f"New Instagram post from {username}", post_url)
            state["instagram"] = latest_shortcode
    except Exception as e:
        print(f"[ERROR] Instagram check failed: {e}")


def check_twitter(state):
    username = USERNAMES["twitter"]
    # Uses Twitter's unofficial embedded-timeline syndication endpoint.
    # No auth required, but unofficial and may break without notice.
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        if resp.status_code != 200:
            print(f"[Twitter/X] Non-200 response: {resp.status_code}")
            return
        html = resp.text
        marker = '"id_str":"'
        idx = html.find(marker)
        if idx == -1:
            print("[Twitter/X] Could not locate tweet data — endpoint may have changed.")
            return
        start = idx + len(marker)
        end = html.find('"', start)
        latest_id = html[start:end]
        last_seen = state.get("twitter")
        if latest_id != last_seen:
            if last_seen is not None:
                tweet_url = f"https://x.com/{username}/status/{latest_id}"
                send_alert("X (Twitter)", f"New X post from {username}", tweet_url)
            state["twitter"] = latest_id
    except Exception as e:
        print(f"[ERROR] Twitter/X check failed: {e}")


def main():
    state = load_state()
    check_youtube(state)
    check_instagram(state)
    check_twitter(state)
    save_state(state)


if __name__ == "__main__":
    main()
