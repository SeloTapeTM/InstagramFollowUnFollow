#!/usr/bin/env python3
"""Find Instagram accounts you follow that don't follow you back.

Works directly on the ZIP from Instagram's "Download your information"
(JSON or HTML format), or on an already-extracted export folder.

Everything runs locally; nothing is uploaded.

Usage:
    python3 not_following_back.py path/to/instagram-export.zip
    python3 not_following_back.py path/to/extracted-folder/
    python3 not_following_back.py instagram.zip --csv > result.csv
    python3 not_following_back.py instagram.zip --output not_following.txt
"""

import argparse
import json
import os
import sys
import zipfile
from html.parser import HTMLParser


def _collect_from_json_node(node, out):
    """Recursively gather {username: href} from any 'string_list_data' blocks."""
    if isinstance(node, list):
        for item in node:
            _collect_from_json_node(item, out)
    elif isinstance(node, dict):
        sld = node.get("string_list_data")
        if isinstance(sld, list):
            for s in sld:
                value = (s.get("value") or "").strip()
                if value:
                    out[value.lower()] = (
                        value,
                        s.get("href") or f"https://www.instagram.com/{value}",
                    )
        for key, child in node.items():
            if key != "string_list_data":
                _collect_from_json_node(child, out)


def users_from_json(text):
    out = {}
    try:
        _collect_from_json_node(json.loads(text), out)
    except (json.JSONDecodeError, ValueError):
        pass
    return out


class _IGHtmlParser(HTMLParser):
    """Pull instagram.com profile links out of an HTML-format export."""

    def __init__(self):
        super().__init__()
        self.users = {}
        self._href = None
        self._text = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs = dict(attrs)
            href = attrs.get("href", "")
            if "instagram.com/" in href:
                self._href = href
                self._text = []

    def handle_data(self, data):
        if self._href is not None:
            self._text.append(data)

    def handle_endtag(self, tag):
        if tag == "a" and self._href is not None:
            text = "".join(self._text).strip()
            username = text
            if not username or username.startswith("http"):
                # fall back to the URL slug
                slug = self._href.split("instagram.com/", 1)[1]
                username = slug.split("/")[0].split("?")[0].split("#")[0]
            if username:
                self.users[username.lower()] = (username, self._href)
            self._href = None
            self._text = []


def users_from_html(text):
    p = _IGHtmlParser()
    try:
        p.feed(text)
    except Exception:
        pass
    return p.users


def _is_relevant(name):
    low = name.lower()
    return "follow" in low and (low.endswith(".json") or low.endswith(".html"))


def _parse_text(name, text, followers, following):
    # Classify by the file's basename only: the parent directory is named
    # "followers_and_following", which contains both substrings and would
    # otherwise misclassify the followers file as following.
    base = os.path.basename(name).lower()
    users = users_from_html(text) if base.endswith(".html") else users_from_json(text)
    if "following" in base:
        following.update(users)
    elif "follower" in base:
        followers.update(users)


def load_export(path):
    """Return (followers, following) dicts keyed by lowercase username."""
    followers, following = {}, {}

    if os.path.isdir(path):
        for root, _dirs, files in os.walk(path):
            for fn in files:
                if _is_relevant(fn):
                    full = os.path.join(root, fn)
                    with open(full, "r", encoding="utf-8", errors="replace") as f:
                        _parse_text(fn, f.read(), followers, following)
    elif zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as z:
            for info in z.infolist():
                if _is_relevant(info.filename):
                    text = z.read(info.filename).decode("utf-8", errors="replace")
                    _parse_text(info.filename, text, followers, following)
    elif path.lower().endswith((".json", ".html")):
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            text = f.read()
        # Single file: guess type from content/name.
        if path.lower().endswith(".html"):
            users = users_from_html(text)
        else:
            users = users_from_json(text)
        if "following" in path.lower() or "relationships_following" in text:
            following.update(users)
        else:
            followers.update(users)
    else:
        raise SystemExit(f"Error: '{path}' is not a ZIP, folder, or .json/.html file.")

    return followers, following


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="List Instagram accounts you follow that don't follow you back."
    )
    ap.add_argument("path", help="Instagram export ZIP, extracted folder, or a single JSON/HTML file")
    ap.add_argument("--csv", action="store_true", help="Output CSV (username,profile_url)")
    ap.add_argument("--output", "-o", help="Write results to a file instead of stdout")
    ap.add_argument("--fans", action="store_true",
                    help="Instead list people who follow you but you don't follow back")
    args = ap.parse_args(argv)

    followers, following = load_export(args.path)

    if not following and not followers:
        raise SystemExit(
            "Couldn't find any followers/following data. "
            "Make sure this is an Instagram data export (with 'Followers and following' included)."
        )

    if args.fans:
        result_keys = [k for k in followers if k not in following]
        source = followers
        label = "accounts that follow you but you DON'T follow back"
    else:
        result_keys = [k for k in following if k not in followers]
        source = following
        label = "accounts that do NOT follow you back"

    rows = sorted((source[k] for k in result_keys), key=lambda u: u[0].lower())

    out = sys.stdout
    if args.output:
        out = open(args.output, "w", encoding="utf-8")

    try:
        if args.csv:
            out.write("username,profile_url\n")
            for username, href in rows:
                out.write(f"{username},{href}\n")
        else:
            out.write(f"You follow {len(following)} accounts. "
                      f"{len(following) - len([k for k in following if k not in followers])} follow you back.\n")
            out.write(f"{len(rows)} {label}:\n\n")
            for username, href in rows:
                out.write(f"  @{username:<28} {href}\n")
    finally:
        if args.output:
            out.close()
            print(f"Wrote {len(rows)} {label} to {args.output}", file=sys.stderr)


if __name__ == "__main__":
    main()
