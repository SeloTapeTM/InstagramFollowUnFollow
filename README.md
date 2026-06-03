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

You can search/filter, **copy** the list, or **export CSV**.

> Uses the browser's built-in `DecompressionStream` to read the ZIP — no
> internet connection or third-party library required.

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

Both tools extract every `string_list_data[].value` from the followers and
following files, then compute the set difference
`following − followers` = accounts that don't follow you back.
