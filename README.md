# Instagram — Who Doesn't Follow You Back

Find out which accounts **you follow that don't follow you back**, straight from
your official Instagram data export. Two ways to use it:

- **Web app** (`index.html`) — drag-and-drop your export ZIP, results in your browser.
- **CLI script** (`not_following_back.py`) — run it in a terminal.

> 🔒 **Privacy:** both options run **entirely on your machine**. Your Instagram
> data is never uploaded anywhere. The web app does all parsing in the browser
> with no server and no external libraries.

---

## 1. Get your Instagram data export

1. In the Instagram app or on the web, go to:
   **Settings → Accounts Center → Your information and permissions → Download your information**.
2. Click **Download or transfer information** → select your account.
3. Choose **Some of your information** and tick **Followers and following**
   (this keeps the file small). Or select everything — both work.
4. Set **Format: JSON** (recommended) — the HTML format is also supported.
5. Set **Date range: All time**, then submit the request.
6. Instagram emails you a download link (can take minutes to a day). Download
   the ZIP. **You do not need to unzip it.**

The relevant files inside are, for example:
```
connections/followers_and_following/following.json
connections/followers_and_following/followers_1.json   (followers_2.json, … if you have many)
```

---

## 2. Web app (recommended)

Just open `index.html` in any modern browser (Chrome, Edge, Firefox, Safari):

```bash
# from this folder
open index.html        # macOS
xdg-open index.html    # Linux
start index.html       # Windows
```

Then drag your `instagram-….zip` (or a single `following.json`/`followers.json`)
onto the page. You'll get:

- **Not following you back** — accounts you follow who don't follow you.
- **Fans** — accounts who follow you but you don't follow back.
- **Mutual** — follow each other.

Each row also shows **when the follow happened** (e.g. "you followed · 3y ago"),
taken from the export's own timestamp — handy for spotting old one-way follows
of big accounts you're happy to just be a fan of.

You can search/filter, **sort** (name A→Z / Z→A, or follow-date newest/oldest),
**copy** the list, or **export CSV** (the CSV includes the follow date and your
checkmarks). Each row has a **checkbox** to tick off accounts as you handle them
(e.g. after unfollowing) — your checks are saved locally in the browser so a
refresh won't lose your progress, and a counter shows how many you've done. The
site has a **dark / light theme** that follows your device and can be toggled
with the 🌙/☀️ button.

> Note: Instagram's export does **not** include follower counts for these
> accounts (only usernames, profile links, and follow dates), so the tool can't
> show how many followers each account has without contacting Instagram — which
> would break the "nothing leaves your browser" guarantee. Tap a username to
> open their profile if you want to check.

> Uses the browser's built-in `DecompressionStream` to read the ZIP — no
> internet connection or third-party library required. The ZIP is read with
> byte-range slicing, so only the tiny followers/following files are loaded —
> even a multi-GB export (with all your photos/videos) works without running
> out of memory.

### On iPhone / iPad (Safari or Chrome)

The page works on a phone — it just needs a URL to open. Two options:

1. **Host it (easiest):** enable **GitHub Pages** for this repo
   (*Settings → Pages → Build from branch → `main` / root*). GitHub gives you a
   link like `https://<you>.github.io/InstagramFollowUnFollow/`. Open that in
   Safari/Chrome on your iPhone. It's still 100% client-side — your data never
   leaves the phone, GitHub only serves the HTML.
2. **Open the file locally:** AirDrop / email `index.html` to yourself, save it
   to **Files**, and open it from there.

Then:
- Tap **“Tap to choose your instagram-….zip”**.
- Choose **Browse**, find the `instagram-….zip` in **Files** (where the Instagram
  app / email saved it), and select it. No need to unzip.
- Requires **iOS/iPadOS 16.4+** (for the built-in ZIP decompression). On iPhone,
  Chrome uses the same engine as Safari, so the version requirement is the same.

---

## 3. CLI script

Requires **Python 3.7+** (standard library only — no `pip install` needed).

```bash
# Point it at the ZIP directly (no need to unzip):
python3 not_following_back.py ~/Downloads/instagram-yourname.zip

# Or at an already-extracted export folder:
python3 not_following_back.py ~/Downloads/instagram-export/

# Save the result to a file:
python3 not_following_back.py instagram.zip --output not_following_back.txt

# Get CSV with profile links:
python3 not_following_back.py instagram.zip --csv > result.csv
```

Example output:
```
You follow 842 accounts. 791 follow you back.
51 accounts do NOT follow you back:

  @someaccount        https://www.instagram.com/someaccount
  @another_one        https://www.instagram.com/another_one
  ...
```

---

## How it works

Instagram stores your relationships in JSON like:

```json
// following.json
{ "relationships_following": [
    { "string_list_data": [ { "value": "username", "href": "https://...", "timestamp": 0 } ] }
] }
```

Both tools extract every username from the followers and following files
(handling the two different shapes Instagram uses — `value` for followers,
`title` + `_u/` links for following), then compute the set difference
`following − followers` = accounts that don't follow you back.

---

## Credits & license

Made by **[Omer Daniel](https://github.com/SeloTapeTM)**.

Released under the [MIT License](LICENSE) — free to use, modify, and share with
attribution.
