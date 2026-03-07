# 🎓 Parul University — Student Mentoring Meeting Automation

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python)
![Selenium](https://img.shields.io/badge/Selenium-4.x-green?style=for-the-badge&logo=selenium)
![Automation](https://img.shields.io/badge/Type-Web%20Automation-orange?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=for-the-badge)

> **A fully automated Selenium-based Python script that navigates the UMS portal, extracts student data, and fills Mentoring Meeting observation forms for all 99 mentees — without any manual intervention.**

---

## 📌 Project Overview

Manually filling mentoring observation forms for 99+ students is a time-consuming and repetitive task. This automation script eliminates that entirely.

The bot:
- Logs into an already-authenticated Chrome session
- Scrapes all mentee data (name, enrollment, gender, attendance %) from the dashboard
- Opens each mentee's mentoring form
- Fills all 10+ fields intelligently based on conditional logic
- Saves each form and confirms the popup
- Retries automatically on failure or browser timeout
- Generates a final success/failure report

**Time saved:** ~4-5 hours of manual work → completed in ~30 minutes ⚡

---

## 🖥️ Tech Stack

| Technology | Purpose |
|---|---|
| Python 3.8+ | Core scripting language |
| Selenium WebDriver | Browser automation |
| jQuery (injected) | Select2 dropdown handling |
| Chrome DevTools Protocol | Connect to existing browser session |
| Regex | Attendance % parsing |

---

## ✨ Key Features

- ✅ **Zero manual input** — fully unattended after script start
- ✅ **Smart conditional logic** — fields filled based on attendance % and gender
- ✅ **Select2 dropdown handling** — via jQuery API injection
- ✅ **Auto-retry (3x)** — each mentee retried up to 3 times on failure
- ✅ **Browser crash recovery** — `safe_navigate()` handles renderer timeouts
- ✅ **Cooldown system** — 10s pause every 10 mentees to prevent Chrome overload
- ✅ **Fallback navigation** — uses direct URL if button click fails
- ✅ **Final report** — prints success/failure summary with names

---

## 📋 Automation Workflow

```
┌─────────────────────────────────────────────────────┐
│                    PHASE 1                          │
│         Scrape Dashboard (Page 1)                   │
│   Extract: Name, Enrollment, Gender, Attendance     │
└───────────────────┬─────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│                    PHASE 2                          │
│         Open Mentoring Form (Page 2)                │
│   Click '+' → Select Group → Click Show             │
└───────────────────┬─────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│                  PHASE 3 & 4                        │
│         Fill All Form Fields (Page 3)               │
│   Static fields + Dynamic conditional logic         │
└───────────────────┬─────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────┐
│                    PHASE 5                          │
│         Save & Confirm (Page 4)                     │
│   Click Save → Handle Bootbox popup → Click Yes     │
└─────────────────────────────────────────────────────┘
```

---

## 🧠 Conditional Logic

### Based on Attendance %

| Field | Att ≥ 70% | 50% ≤ Att < 70% | Att < 50% |
|---|---|---|---|
| Academic Category | A. Advance Learner | B. Mediocre Learner | C. Slow Learner |
| Personality | Well - disciplined | Good moral sense | Discipline is required |
| Study Performance | Excellent | Very Good | Good |
| Performance in Exams | Excellent | Good | Average |
| Suggestions | "Excellent attendance..." | "Attendance satisfactory..." | "Attendance is low..." |

### Based on Gender

| Field | Male | Female |
|---|---|---|
| Co-curricular Activities | Cricket / Football / Basketball / Volleyball / Kho-Kho *(random)* | Singing / Dancing / Drawing *(random)* |

---

## 🚀 Getting Started

### Prerequisites
```bash
pip install selenium
```

### Step 1 — Launch Chrome in Debug Mode
```bash
# Windows
"C:/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/selenium_chrome"
```

### Step 2 — Verify Debug Mode
Open in browser:
```
http://localhost:9222/json
```
You should see JSON output — this confirms debug mode is active ✅

### Step 3 — Login
Manually login to the UMS portal in that Chrome window.

### Step 4 — Run the Script
```bash
python mentoring_automation_v12.py
```

---

## 📁 Project Structure

```
mentoring-automation/
│
├── mentoring_automation_v12.py   # Main automation script
├── README.md                     # Project documentation
└── Mentoring_Blueprint_v12.docx  # Detailed process document (PDD)
```

---

## 📊 Sample Output

```
╔══════════════════════════════════════════════════════╗
║  PU Mentoring Meeting Automation  v12.0              ║
║  Robust - Auto Retry + Browser Recovery              ║
╚══════════════════════════════════════════════════════╝

✅ Chrome connected!

📋 Phase 1: Scraping mentee data from dashboard...
   ✅ [ 1] RATHOD JENI BHIKHUBHAI        | Male    | Att: 60.98%
   ✅ [ 2] BALDANIYA VIRANG GORDHANBHAI  | Male    | Att: 58.41%
   ✅ [ 3] BARAD SIDDHIRAJSINH JAGDISHSINH | Male  | Att: 70.0%
   ...
   ✅ Total mentees found: 99

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  [1/99] RATHOD JENI BHIKHUBHAI
  Enrollment: 2303031080162 | Att: 60.98% | Gender: Male
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   ✅ '+' button clicked
   ✅ Group-1 - PIET-1 selected
   ✅ Show clicked
   ✅ All fields filled!
   🎉 Bootbox Yes clicked! Saved for RATHOD JENI BHIKHUBHAI
   ✅ DONE! [1/99 completed]

═══════════════════════════════════════════════════════
  ✅ AUTOMATION COMPLETE
  ✅ Successful : 99/99
  ❌ Failed     : 0
═══════════════════════════════════════════════════════
```

---

## 🛡️ Robustness Features

| Feature | Description |
|---|---|
| `safe_navigate()` | 3 retries on TimeoutException, calls `window.stop()` between retries |
| Per-mentee retry | Each mentee attempted up to 3 times before marking as failed |
| Browser cooldown | 10 second pause every 10 mentees |
| jQuery Select2 | `$().val().trigger('change')` — works on every iteration |
| JS Click | `arguments[0].click()` bypasses overlay issues |
| Alert dismissal | Stuck alerts auto-dismissed before each attempt |
| href fallback | Direct URL navigation if button click fails |

---

## ⚙️ Configuration

At the top of the script, you can customize:

```python
DASHBOARD_URL  = "https://ums.paruluniversity.ac.in/..."  # Portal URL
WAIT_TIMEOUT   = 20    # Max wait for elements (seconds)
DELAY_BETWEEN  = 3     # Delay between each mentee (seconds)
QUESTION_GROUP = "Group-1 - PIET-1"  # Change if needed
```

---

## 🙋 Use Cases / Applications

This script can be adapted for any similar automation:
- **University portals** — bulk form submissions

---

## 👨‍💻 Author

**Vishalkumar Rajkumar Vishwakarma**
- 🔧 Python & Selenium Automation Developer
- 📧 Contact via GitHub

---

## 📄 License

This project is for educational and institutional use only.
The script is designed specifically for authorized users of the Parul University UMS portal.

---

> ⭐ **If this project helped you, please give it a star!**
