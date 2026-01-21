**Project Overview**

- **Purpose:** Simple vehicle counter using OpenCV background subtraction and lightweight tracking. Includes a CLI and an embedded Streamlit UI.

**Requirements**
- **Python:** 3.8+ recommended (virtualenv used in `.venv`)
- **Packages:** See `.venv/requirements.txt` (includes `numpy`, `opencv-python`, `streamlit`)

**Setup**
- **Create venv:**
```powershell
python -m venv .venv
```
- **Activate venv (PowerShell):**
```powershell
. .\.venv\Scripts\Activate.ps1
```
- **Install deps:**
```powershell
python -m pip install -r .venv\requirements.txt
```

**Usage (CLI)**
- **Run vehicle counter on a video (prints numeric count):**
```powershell
C:/.../.venv/Scripts/python.exe .\.venv\main.py "C:\path\to\video.mp4"
```
- **Tuning & debug output:** add optional flags to adjust detection and produce an annotated debug video:
```powershell
C:/.../.venv/Scripts/python.exe .\.venv\main.py "C:\path\to\video.avi" --min-area 600 --match-dist 60 --min-age 3 --max-lost 10 --debug-out debug.mp4
```
- **Behavior:** If the video file cannot be opened the script prints `0`.

**Usage (Streamlit UI)**
- **Start app:**
```powershell
streamlit run .venv\main.py
```
- **How it works:** Open the URL shown by Streamlit in your browser, upload a video file. If you upload an `.avi`, the app converts it to `.mp4` for browser playback before processing. The page displays the numeric vehicle count.

**Tuning & Debugging**
- **Parameters:** `min_area`, `match_dist`, `min_age_to_count`, `max_lost` can be adjusted via CLI to improve detection for your camera/view.
- **Debug video:** Use `--debug-out debug.mp4` to create an annotated video showing detections, IDs and the counting line to help diagnose misses/false positives.

**Notes**
- Converting and processing video can be CPU intensive — run on a machine with enough resources for longer videos.
- Results depend strongly on camera angle, lighting and scene motion; tuning parameters per-video is recommended.
