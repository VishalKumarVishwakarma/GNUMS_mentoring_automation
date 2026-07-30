"""
╔══════════════════════════════════════════════════════════════════╗
║   Parul University - Student Mentoring Meeting Automation         ║
║   v13 - Updated for the new UMS "V2" Dashboard + Observation form ║
╚══════════════════════════════════════════════════════════════════╝

WHAT CHANGED (old auto_v12 stopped working after the UMS update):
  • Dashboard moved to ...StaffDashBoardV2.aspx (old URL now UnderMaintenance)
  • Table columns shifted (name/gender/attendance are in new positions)
  • Observation form is now ...MentorObservationV2.aspx and saves in TWO steps:
        Step A: Meeting details -> "Save & Next Step"
        Step B: Question answers -> "Save"
  • Question-group dropdown id + Save button ids changed
  • Textareas are filled via JS (send_keys silently fails on this portal)

NEW FEATURE:
  • On start the script asks WHICH mentoring round to run (integer):
        1 = students whose current mentoring count is 0
        2 = students whose current mentoring count is 1  ... and so on
    (This also prevents accidentally mentoring an already-done student twice.)

HOW TO RUN:
───────────
STEP 1 - Install Selenium (run once in CMD):
    pip install selenium

STEP 2 - Open Chrome in Debug Mode (run in CMD):
    "C:/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/selenium_chrome"

STEP 3 - Us Chrome mein manually LOGIN karo UMS portal pe

STEP 4 - Script run karo:
    python auto_v12_LTS.py
"""

import time
import re
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# ══════════════════════════════════════════════════════
#  CONFIGURATION
# ══════════════════════════════════════════════════════
DASHBOARD_URL  = "https://ums.paruluniversity.ac.in/AdminPanel/Mentoring/MEN_StudentMentoring/MEN_StudentMentoring_StaffDashBoardV2.aspx"
WAIT_TIMEOUT   = 20
DELAY_BETWEEN  = 3     # seconds between each mentee
SHOW_FILL_DELAY = 0.4  # pause after filling each field so you can watch it (set 0 for fastest)

# ══════════════════════════════════════════════════════
#  EXACT ELEMENT IDs (from your inspection)
# ══════════════════════════════════════════════════════

# PAGE 1
ID_PLUS_BTN             = "ctl00_cphPageContent_rpData_ctl00_hlMentorObservation"  # dynamic per row

# PAGE 2
ID_SHOW_BTN             = "ctl00_cphPageContent_btnLoad"
ID_QUESTION_GROUP_SPAN  = "select2-ctl00_cphPageContent_ddlMentoringQuestionGroupID-container"
ID_QUESTION_GROUP_SELECT= "ctl00_cphPageContent_ddlMentoringQuestionGroupID"

# PAGE 3 - Static fields
ID_AGENDA               = "ctl00_cphPageContent_txtMentoringMeetingAgenda"
ID_ISSUES_DISCUSSED     = "ctl00_cphPageContent_txtIssuedDiscussed"
ID_MENTOR_OPINION       = "ctl00_cphPageContent_txtMentorsOpinion"

# PAGE 3 - Q1: Academic Category (Select2 dropdown)
ID_Q1_SPAN              = "select2-ctl00_cphPageContent_rpQuestionList_ctl00_ddlAnswer-container"
ID_Q1_SELECT            = "ctl00_cphPageContent_rpQuestionList_ctl00_ddlAnswer"

# PAGE 3 - Q2 to Q9 (textareas)
ID_Q2_PERSONALITY       = "ctl00_cphPageContent_rpQuestionList_ctl01_txtMentoringAnswer"
ID_Q3_GRIEVANCES        = "ctl00_cphPageContent_rpQuestionList_ctl02_txtMentoringAnswer"
ID_Q4_COCURRICULAR      = "ctl00_cphPageContent_rpQuestionList_ctl03_txtMentoringAnswer"
ID_Q5_ATTENDANCE        = "ctl00_cphPageContent_rpQuestionList_ctl04_txtMentoringAnswer"
ID_Q6_DIFFICULTIES      = "ctl00_cphPageContent_rpQuestionList_ctl05_txtMentoringAnswer"
ID_Q7_STUDY_PERF        = "ctl00_cphPageContent_rpQuestionList_ctl06_txtMentoringAnswer"

# PAGE 3 - Q8: Performance in Exams (Select2 dropdown)
ID_Q8_SPAN              = "select2-ctl00_cphPageContent_rpQuestionList_ctl07_ddlAnswer-container"
ID_Q8_SELECT            = "ctl00_cphPageContent_rpQuestionList_ctl07_ddlAnswer"

# PAGE 3 - Q9: Communication Problem (Select2 dropdown)
ID_Q9_SPAN              = "select2-ctl00_cphPageContent_rpQuestionList_ctl08_ddlAnswer-container"
ID_Q9_SELECT            = "ctl00_cphPageContent_rpQuestionList_ctl08_ddlAnswer"

# PAGE 3 - Q10: Suggestions (textarea)
ID_Q10_SUGGESTIONS      = "ctl00_cphPageContent_rpQuestionList_ctl09_txtMentoringAnswer"

# PAGE 3 - Meeting-details save (Step A) and Question save (Step B)
ID_SAVE_MEETING_BTN     = "ctl00_cphPageContent_lbtnSaveMeetingDetails"  # "Save & Next Step"
ID_SAVE_BTN             = "ctl00_cphPageContent_btnSaveQuestion"          # "Save" (questions)

# ══════════════════════════════════════════════════════
#  CONDITIONAL LOGIC
# ══════════════════════════════════════════════════════
def get_academic_category(att):
    # Based on CURRENT ATTENDANCE % (as shown on the dashboard):
    #   > 70%      -> A. Advanced Learner
    #   50% to 70% -> B. Mediocre Learner
    #   < 50%      -> C. Slow Learner
    if att > 70:    return "A. Advanced Learner"
    elif att >= 50: return "B. Mediocre Learner"
    else:           return "C. Slow Learner"

# Q2 Personality Attributes — pick a RANDOM option each time
PERSONALITY_OPTIONS = [
    "Well-disciplined",
    "Good moral sense",
    "Positive attitude",
    "Attitude needs to be improved",
    "Discipline is required",
    "Lack of enthusiasm",
]
def get_personality():
    return random.choice(PERSONALITY_OPTIONS)

def get_study_performance(att):
    if att >= 70:   return "Excellent"
    elif att >= 50: return "Very Good"
    else:           return "Good"

def get_performance_in_exams(att):
    if att >= 70:   return "Excellent"
    elif att >= 50: return "Good"
    else:           return "Average"

def get_suggestions(att):
    if att >= 70:
        return "Excellent attendance, maintain the same consistency and continue participating actively in classes."
    elif att >= 50:
        return "Attendance is satisfactory, but try to improve regularity to gain better understanding of subjects."
    else:
        return "Attendance is low, please attend classes regularly to improve academic performance and subject understanding."

# Q4 Interest in Co-curricular / Extra-curricular activities — GENDER based
def get_extracurricular(gender):
    if gender.strip().lower() == "female":
        return random.choice(["Singing", "Dancing", "Drawing"])
    else:
        return random.choice(["Cricket", "Football", "Basketball", "Volleyball", "Kho-Kho"])

def parse_attendance(text):
    # Handles "Attd. : 82.0% | Result: ..." => 82.0
    # Tie the number to the '%' so we never accidentally grab the SPI/result value.
    m = re.search(r"(\d+\.?\d*)\s*%", str(text))
    if m:
        return float(m.group(1))
    nums = re.findall(r"\d+\.?\d*", str(text))
    return float(nums[0]) if nums else 0.0

def parse_meeting_count(text):
    # Handles "Date : 03-07-2026 | Meeting : 1" => 1
    m = re.search(r"Meeting\s*:\s*(\d+)", str(text))
    return int(m.group(1)) if m else None

# ══════════════════════════════════════════════════════
#  SELENIUM HELPERS
# ══════════════════════════════════════════════════════
def get_driver():
    opts = Options()
    opts.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
    # Add timeouts so it doesn't hang forever
    from selenium.webdriver.chrome.service import Service
    from subprocess import DEVNULL
    try:
        driver = webdriver.Chrome(options=opts)
        driver.set_page_load_timeout(30)
        driver.set_script_timeout(30)
        driver.maximize_window()
        return driver
    except Exception as e:
        raise Exception(
            f"Chrome se connect nahi hua: {e}\n\n"
            "Yeh steps follow karo:\n"
            "1. Saara Chrome band karo (Task Manager se bhi)\n"
            "2. CMD mein run karo:\n"
            '   "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe" '
            '--remote-debugging-port=9222 --user-data-dir="C:\\selenium_chrome"\n'
            "3. Browser mein http://localhost:9222 kholo - JSON dikhna chahiye\n"
            "4. Phir script dobara run karo"
        )

def wait_for_id(driver, elem_id, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, elem_id))
    )

def wait_clickable_id(driver, elem_id, timeout=WAIT_TIMEOUT):
    return WebDriverWait(driver, timeout).until(
        EC.element_to_be_clickable((By.ID, elem_id))
    )

def js_click(driver, el):
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.3)
    try:
        el.click()
    except ElementClickInterceptedException:
        driver.execute_script("arguments[0].click();", el)

def fill_textarea(driver, elem_id, text):
    # NOTE: On this V2 portal (attached via remote-debugging), Selenium's
    # send_keys() silently fails on these textareas — it raises no error but
    # the value stays empty, which used to leave required fields blank. Setting
    # the value via JS + firing input/change events works reliably for both the
    # meeting-detail and question textareas.
    #
    # A yellow highlight + short pause is added so you can actually SEE each
    # field being filled while watching the automation. Tune with SHOW_FILL_DELAY.
    el = wait_for_id(driver, elem_id)
    driver.execute_script("""
        var el = arguments[0];
        el.scrollIntoView({block:'center'});
        el.focus();
        el.value = arguments[1];
        el.dispatchEvent(new Event('input',  {bubbles:true}));
        el.dispatchEvent(new Event('change', {bubbles:true}));
        // brief visual highlight
        var old = el.style.backgroundColor;
        el.style.backgroundColor = '#fff3a0';
        el.style.transition = 'background-color 0.6s';
        setTimeout(function(){ el.style.backgroundColor = old; }, 600);
        el.blur();
    """, el, text)
    time.sleep(SHOW_FILL_DELAY)

def select2_select(driver, span_id, select_id, visible_text):
    """
    Handle Select2 dropdowns:
    1. Click the span to open dropdown
    2. Select option from the list
    """
    # Click the Select2 span to open dropdown
    span = wait_clickable_id(driver, span_id)
    js_click(driver, span)
    time.sleep(1)

    # Try to find and click the option in dropdown list
    try:
        option = WebDriverWait(driver, 8).until(
            EC.element_to_be_clickable((
                By.XPATH,
                f"//li[contains(@class,'select2-results__option') and normalize-space()='{visible_text}']"
                f" | //li[contains(@class,'select2-results__option') and contains(.,'{visible_text}')]"
            ))
        )
        js_click(driver, option)
    except TimeoutException:
        # Fallback: use native select
        try:
            driver.execute_script("arguments[0].style.display='block';",
                                  driver.find_element(By.ID, select_id))
            sel = Select(driver.find_element(By.ID, select_id))
            try:    sel.select_by_visible_text(visible_text)
            except: sel.select_by_partial_text(visible_text)
        except Exception as e:
            print(f"      ⚠️  Select2 fallback also failed: {e}")

# ══════════════════════════════════════════════════════
#  PHASE 1: SCRAPE ALL MENTEES FROM DASHBOARD
# ══════════════════════════════════════════════════════
def scrape_mentees(driver):
    print("\n📋 Phase 1: Scraping mentee data from dashboard...")
    driver.get(DASHBOARD_URL)
    time.sleep(4)

    mentees = []

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[td]"))
        )
    except TimeoutException:
        print("❌ Dashboard table not loaded. Are you logged in?")
        return []

    # Get rows containing enrollment numbers
    rows = driver.find_elements(By.XPATH,
        "//table//tbody/tr[td[4][string-length(normalize-space()) >= 10]]")

    print(f"   Found {len(rows)} rows")

    for i, row in enumerate(rows):
        try:
            cols = row.find_elements(By.TAG_NAME, "td")
            # V2 dashboard main table has 13 columns per student row
            if len(cols) < 11:
                continue

            sr = cols[0].text.strip()
            if not sr.isdigit():
                continue

            # ── V2 dashboard column layout ──
            #  col[3]=Enrollment  col[5]=Name  col[7]=Gender
            #  col[8]=Attendance/Result   col[10]="Date : .. | Meeting : N"
            enrollment = cols[3].text.strip()
            name       = cols[5].text.strip()
            gender     = cols[7].text.strip()

            # Attendance column text: "Attd. : 82.0% | Result : 8.50 SPI"
            att_raw    = cols[8].text.strip()
            attendance = parse_attendance(att_raw)

            # Current mentoring status = how many meetings already done
            mentoring_count = parse_meeting_count(cols[10].text)

            # Get the "+" button href - contains StudentMentorID
            plus_btn = row.find_element(By.XPATH,
                ".//a[contains(@id,'hlMentorObservation')]")
            href = plus_btn.get_attribute("href")

            mentees.append({
                "sr"             : sr,
                "name"           : name,
                "enrollment"     : enrollment,
                "gender"         : gender,
                "attendance"     : attendance,
                "mentoring_count": mentoring_count,   # 0, 1, 2 ...
                "href"           : href,     # direct URL to form
                "btn_id"         : plus_btn.get_attribute("id"),
            })
            print(f"   ✅ [{sr:>2}] {name:<35} | {gender:<7} | Att: {attendance}% | Mentoring done: {mentoring_count}")

        except Exception as e:
            print(f"   ⚠️  Row {i} skipped: {e}")
            continue

    print(f"\n   ✅ Total mentees found: {len(mentees)}")
    return mentees

# ══════════════════════════════════════════════════════
#  SAFE NAVIGATION - handles renderer timeout
# ══════════════════════════════════════════════════════
def safe_navigate(driver, url, retries=3):
    """Navigate to URL with retry on timeout"""
    for attempt in range(retries):
        try:
            driver.set_page_load_timeout(40)
            driver.get(url)
            time.sleep(3)
            return True
        except TimeoutException:
            print(f"   ⚠️  Page load timeout (attempt {attempt+1}/{retries}), retrying...")
            try:
                driver.execute_script("window.stop();")  # Stop hanging load
            except: pass
            time.sleep(3)
        except Exception as e:
            print(f"   ⚠️  Navigation error (attempt {attempt+1}/{retries}): {e}")
            time.sleep(3)
    print(f"   ❌ Could not navigate to {url} after {retries} attempts")
    return False

# ══════════════════════════════════════════════════════
#  PHASE 2: OPEN FORM & SELECT QUESTION GROUP
# ══════════════════════════════════════════════════════
def open_form(driver, mentee):
    print(f"\n🔗 Phase 2: Opening form for {mentee['name']}...")

    # Navigate back to dashboard safely
    if not safe_navigate(driver, DASHBOARD_URL):
        # Last resort: try direct href
        if mentee.get("href"):
            print("   ⚠️  Dashboard failed, trying direct URL...")
            if not safe_navigate(driver, mentee["href"]):
                return False
            return _select_group_and_show(driver)
        return False

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//table//tbody/tr[td]"))
        )

        plus_btn = None
        # Prefer the exact stored button id (most reliable if row order changes)
        if mentee.get("btn_id"):
            try:
                plus_btn = driver.find_element(By.ID, mentee["btn_id"])
            except Exception:
                plus_btn = None
        # Fallback: locate the row by enrollment number
        if plus_btn is None:
            plus_btn = driver.find_element(By.XPATH,
                f"//table//tbody/tr[td[normalize-space()='{mentee['enrollment']}'] "
                f"or td[contains(normalize-space(),'{mentee['enrollment']}')]]"
                f"//a[contains(@id,'hlMentorObservation')]"
            )

        # The '+' is a plain <a href="...ObservationV2.aspx?...">. A native
        # click is flaky (sometimes doesn't navigate), so read the FRESH href
        # from the current DOM and navigate to it directly — deterministic.
        fresh_href = plus_btn.get_attribute("href")
        if fresh_href and "ObservationV2" in fresh_href:
            print(f"   ➡️  Opening observation form directly...")
            if not safe_navigate(driver, fresh_href):
                return False
        else:
            js_click(driver, plus_btn)
        print("   ✅ Observation form opened")
        time.sleep(2)

    except Exception as e:
        print(f"   ⚠️  Click failed ({e}), trying direct URL...")
        if mentee.get("href"):
            if not safe_navigate(driver, mentee["href"]):
                return False
        else:
            print("   ❌ No href available")
            return False

    return _select_group_and_show(driver)


def _group_option_ready(driver):
    return driver.execute_script("""
        var s = document.getElementById(arguments[0]);
        if (!s) return false;
        return Array.from(s.options).some(function(o){
            return o.textContent.indexOf('Group-1 - PIET-1') !== -1;
        });
    """, ID_QUESTION_GROUP_SELECT)


def _select_group_and_show(driver):
    """Select the Question Group and click Show.

    The 'Show' postback occasionally takes longer than the wait (server load),
    which used to fail the whole open and force a full form re-open. We now
    retry the select+Show a few times INTERNALLY with a longer wait, so a slow
    load just re-clicks Show instead of re-opening everything."""

    # Wait until the observation page is ready AND the group dropdown actually
    # has the 'Group-1 - PIET-1' option populated (selecting too early silently
    # selects nothing and Show then loads an empty form).
    try:
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, ID_QUESTION_GROUP_SELECT)))
        WebDriverWait(driver, 15).until(_group_option_ready)
    except TimeoutException:
        print("   ❌ Observation page / group dropdown did not load")
        return False

    for attempt in range(1, 4):
        try:
            tag = f" (try {attempt}/3)" if attempt > 1 else ""
            print(f"   📌 Selecting Mentoring Question Group...{tag}")

            # Set the Select2 value via jQuery — most reliable
            driver.execute_script("""
                var $sel = $('#' + arguments[0]);
                $sel.find('option').each(function() {
                    if ($(this).text().indexOf('Group-1 - PIET-1') !== -1) {
                        $sel.val($(this).val()).trigger('change');
                    }
                });
            """, ID_QUESTION_GROUP_SELECT)
            time.sleep(2)   # let the group-change partial postback settle

            try:
                picked = Select(driver.find_element(By.ID, ID_QUESTION_GROUP_SELECT)
                                ).first_selected_option.text.strip()
            except Exception:
                picked = "?"
            print(f"   ✅ Group selected: {picked}")

            # Click Show (fresh JS lookup — a cached element goes stale because
            # selecting the group refreshes the panel).
            print("   📌 Clicking Show...")
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, ID_SHOW_BTN)))
            driver.execute_script(
                "document.getElementById(arguments[0]).click();", ID_SHOW_BTN)
            print("   ✅ Show clicked")

            # Confirm the question form actually loaded (agenda textarea appears).
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.ID, ID_AGENDA)))
            time.sleep(1.5)
            print("   ✅ Question form loaded")
            return True

        except TimeoutException:
            print(f"   ⚠️  Form slow to load after Show (try {attempt}/3), re-trying Show...")
            try:
                driver.execute_script("window.stop();")
            except Exception:
                pass
            time.sleep(3)
        except Exception as e:
            # keep it to one short line (no giant chromedriver stacktrace)
            first = str(e).splitlines()[0][:80] if str(e).strip() else e.__class__.__name__
            print(f"   ⚠️  Group/Show issue (try {attempt}/3): {first}")
            time.sleep(3)

    print("   ❌ Question form did not load after Show (will re-open the form)")
    return False

# ══════════════════════════════════════════════════════
#  PHASE 3 & 4: FILL FORM  (V2 = TWO-STEP save)
#    Step A: meeting details  -> "Save & Next Step" (group 'Observation')
#    Step B: question answers -> "Save"             (group 'ObservationQuestion')
#  IMPORTANT: filling a question dropdown fires a partial postback that
#  wipes the meeting-detail textareas, so meeting details MUST be saved
#  BEFORE the questions are filled — otherwise the server rejects the
#  question save with "Meeting details not found".
# ══════════════════════════════════════════════════════
def _confirm_bootbox_yes(driver, timeout=10):
    """Click 'Yes' on the ConfirmSave bootbox modal (with fallbacks)."""
    try:
        yes = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@data-bb-handler='confirm']"))
        )
        driver.execute_script("arguments[0].click();", yes)
        return True
    except TimeoutException:
        for xp in ["//button[contains(@class,'btn-success') and normalize-space()='Yes']",
                   "//button[normalize-space()='Yes']"]:
            try:
                yes = WebDriverWait(driver, 4).until(
                    EC.element_to_be_clickable((By.XPATH, xp)))
                driver.execute_script("arguments[0].click();", yes)
                return True
            except TimeoutException:
                continue
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present())
            driver.switch_to.alert.accept()
            return True
        except TimeoutException:
            return False


def _page_messages(driver):
    """Collect any validation-summary / alert / toast text on the page."""
    return driver.execute_script("""
        var out='';
        document.querySelectorAll('.validation-summary-errors,.alert,.toast,'
            + '.sweet-alert,[id*=ValidationSummary]').forEach(function(e){
            var t=(e.textContent||'').trim(); if(t) out += t + ' | ';
        });
        return out;
    """) or ""


def fill_meeting_details(driver):
    """Step A: fill the meeting-details section (validation group 'Observation').
    Required fields are Agenda + Issues Discussed."""
    print("   📝 Step A: Meeting details...")
    wait_for_id(driver, ID_AGENDA, timeout=15)
    time.sleep(0.5)

    print("   📌 Agenda = Academics")
    fill_textarea(driver, ID_AGENDA, "Academics")

    print("   📌 Issues Discussed = Academics")
    fill_textarea(driver, ID_ISSUES_DISCUSSED, "Academics")

    print("   📌 Mentor's Opinion = No")
    try:
        driver.execute_script("""
            var el = document.getElementById(arguments[0]);
            if (el) {
                el.scrollIntoView({block:'center'});
                el.value = 'No';
                el.dispatchEvent(new Event('input',  {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
            }
        """, ID_MENTOR_OPINION)
    except Exception as e_mo:
        print(f"   ⚠️  Mentor Opinion: {e_mo}")
    return True


def save_meeting_details(driver):
    """Click 'Save & Next Step', confirm, and wait for the question step.
    Returns True if the meeting record was saved."""
    print("   💾 Saving meeting details ('Save & Next Step')...")

    # Client-side validate first; if it fails, no bootbox appears.
    valid = driver.execute_script(
        "try{return Page_ClientValidate('Observation');}catch(e){return null;}")
    if valid is False:
        print("   ❌ Meeting-details validation failed (a required field is empty)")
        return False

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, ID_SAVE_MEETING_BTN)))
    driver.execute_script(
        "document.getElementById(arguments[0]).click();", ID_SAVE_MEETING_BTN)
    time.sleep(1)

    if not _confirm_bootbox_yes(driver):
        print("   ⚠️  No confirm dialog appeared for meeting-details save")
    time.sleep(4)  # full postback

    # Question step is ready once the Q1 dropdown is present again
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.ID, ID_Q1_SELECT)))
        print("   ✅ Meeting details saved — question step ready")
    except TimeoutException:
        print("   ⚠️  Question section not detected (meeting likely still saved)")
    return True


# ══════════════════════════════════════════════════════
#  STEP B: FILL QUESTION ANSWERS
# ══════════════════════════════════════════════════════
def fill_questions(driver, mentee):
    att    = mentee["attendance"]
    gender = mentee["gender"]

    print(f"\n📝 Step B: Filling questions | Att={att}% | Gender={gender}")

    try:
        # Wait for the question section after the meeting-details save
        wait_for_id(driver, ID_Q1_SELECT, timeout=15)

        # The answers live inside the hidden "2. Questions Details" tab
        # (tab_QuestionsList, display:none). Activate that tab so the fields
        # become visible — this lets you WATCH the answers being filled and
        # ensures we interact with the shown controls.
        print("   📑 Switching to '2. Questions Details' tab...")
        driver.execute_script("""
            try { $('a[href="#tab_QuestionsList"]').tab('show'); }
            catch(e) {
                var a = document.querySelector('a[href="#tab_QuestionsList"]');
                if (a) a.click();
            }
            var pane = document.getElementById('tab_QuestionsList');
            if (pane) { pane.classList.add('active'); pane.style.display = 'block'; }
        """)
        time.sleep(1)

        # ── DYNAMIC FIELDS ──

        # Q1: Academic Category (Select2 dropdown) — based on ATTENDANCE %
        # Element: select2-ctl00_cphPageContent_rpQuestionList_ctl00_ddlAnswer-container
        category = get_academic_category(att)
        print(f"   📌 Q1: Academic Category = {category}  (att {att}%)")
        try:
            # Use jQuery Select2 API to set value — works on every iteration
            driver.execute_script("""
                var selectId = 'ctl00_cphPageContent_rpQuestionList_ctl00_ddlAnswer';
                var $sel = $('#' + selectId);

                // Find the option whose text matches
                var targetText = arguments[0];
                var matchedVal = null;
                $sel.find('option').each(function() {
                    if ($(this).text().trim() === targetText.trim()) {
                        matchedVal = $(this).val();
                    }
                });

                if (matchedVal !== null) {
                    // Set via Select2 API
                    $sel.val(matchedVal).trigger('change');
                } else {
                    // Fallback: match by partial text
                    $sel.find('option').each(function() {
                        if ($(this).text().indexOf(targetText.split(' ').pop()) !== -1) {
                            $sel.val($(this).val()).trigger('change');
                        }
                    });
                }
            """, category)
            time.sleep(0.5)
            print(f"   ✅ Q1 selected: {category}")
        except Exception as eq1:
            print(f"   ⚠️  Q1 jQuery failed, trying native select: {eq1}")
            try:
                q1_sel = driver.find_element(By.ID, ID_Q1_SELECT)
                driver.execute_script(
                    "arguments[0].style.display='block';"
                    "arguments[0].style.visibility='visible';"
                    "arguments[0].style.opacity='1';",
                    q1_sel
                )
                time.sleep(0.3)
                sel_obj = Select(q1_sel)
                for opt in sel_obj.options:
                    if opt.text.strip() == category.strip():
                        sel_obj.select_by_visible_text(opt.text)
                        break
                driver.execute_script(
                    "arguments[0].dispatchEvent(new Event('change', {bubbles:true}));",
                    q1_sel
                )
                print(f"   ✅ Q1 selected via native: {category}")
            except Exception as eq1b:
                print(f"   ❌ Q1 failed: {eq1b}")

        # Q2: Personality Attributes (textarea) — RANDOM option
        personality = get_personality()
        print(f"   📌 Q2: Personality = {personality}")
        fill_textarea(driver, ID_Q2_PERSONALITY, personality)

        # Q3: Students Grievances = "No"
        print("   📌 Q3: Students Grievances = No")
        fill_textarea(driver, ID_Q3_GRIEVANCES, "No")

        # Q4: Co-curricular (gender-based random)
        co = get_extracurricular(gender)
        print(f"   📌 Q4: Co-curricular = {co}")
        fill_textarea(driver, ID_Q4_COCURRICULAR, co)

        # Q5: Attendance value
        print(f"   📌 Q5: Attendance = {att}%")
        fill_textarea(driver, ID_Q5_ATTENDANCE, str(att))

        # Q6: Difficulties in Subjects = "No"
        print("   📌 Q6: Difficulties = No")
        fill_textarea(driver, ID_Q6_DIFFICULTIES, "No")

        # Q7: Study Performance (textarea)
        print(f"   📌 Q7: Study Performance = {get_study_performance(att)}")
        fill_textarea(driver, ID_Q7_STUDY_PERF, get_study_performance(att))

        # Q8: Performance in Exams (Select2 dropdown)
        perf = get_performance_in_exams(att)
        print(f"   📌 Q8: Performance in Exams = {perf}")
        try:
            driver.execute_script("""
                var $sel = $('#ctl00_cphPageContent_rpQuestionList_ctl07_ddlAnswer');
                var targetText = arguments[0];
                var matchedVal = null;
                $sel.find('option').each(function() {
                    if ($(this).text().trim() === targetText.trim()) {
                        matchedVal = $(this).val();
                    }
                });
                if (matchedVal !== null) {
                    $sel.val(matchedVal).trigger('change');
                } else {
                    $sel.find('option').each(function() {
                        if ($(this).text().indexOf(targetText) !== -1) {
                            $sel.val($(this).val()).trigger('change');
                        }
                    });
                }
            """, perf)
            time.sleep(0.5)
            print(f"   ✅ Q8 selected: {perf}")
        except Exception as eq8:
            print(f"   ⚠️  Q8 failed: {eq8}")

        # Q9: Communication Problem = "No"
        print("   📌 Q9: Communication Problem = No")
        try:
            driver.execute_script("""
                var $sel = $('#ctl00_cphPageContent_rpQuestionList_ctl08_ddlAnswer');
                var matchedVal = null;
                $sel.find('option').each(function() {
                    if ($(this).text().trim() === 'No') {
                        matchedVal = $(this).val();
                    }
                });
                if (matchedVal !== null) {
                    $sel.val(matchedVal).trigger('change');
                }
            """)
            time.sleep(0.5)
            print("   ✅ Q9 selected: No")
        except Exception as eq9:
            print(f"   ⚠️  Q9 failed: {eq9}")

        # Q10: Suggestions (textarea)
        print(f"   📌 Q10: Suggestions...")
        fill_textarea(driver, ID_Q10_SUGGESTIONS, get_suggestions(att))

        print("   ✅ All fields filled!")
        return True

    except Exception as e:
        print(f"   ❌ Form fill error: {e}")
        return False

# ══════════════════════════════════════════════════════
#  PHASE 5: SAVE QUESTIONS & CONFIRM
# ══════════════════════════════════════════════════════
def save_questions(driver):
    """Step B save: click the hidden 'Save' (btnSaveQuestion), confirm the
    bootbox, and verify the server did not reject it."""
    print("   💾 Saving questions ('Save')...")

    valid = driver.execute_script(
        "try{return Page_ClientValidate('ObservationQuestion');}catch(e){return null;}")
    if valid is False:
        print("   ❌ Question validation failed (a required answer is empty)")
        return False

    # btnSaveQuestion is a HIDDEN <input type=submit> (size 0x0). JS click
    # fires its onclick (ConfirmSave -> bootbox) regardless of visibility.
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, ID_SAVE_BTN)))
    driver.execute_script(
        "document.getElementById(arguments[0]).click();", ID_SAVE_BTN)
    time.sleep(1)

    if not _confirm_bootbox_yes(driver):
        print("   ⚠️  No confirm dialog appeared for question save")
    time.sleep(4)

    # Detect the known server rejection
    msg = _page_messages(driver)
    if "Meeting details not found" in msg:
        print(f"   ❌ Save rejected: {msg.strip(' |')}")
        return False
    print("   ✅ Questions saved")
    return True


def do_observation(driver, mentee):
    """Full V2 observation flow for one mentee:
       fill meeting details -> save -> fill questions -> save.
    Returns (success, meeting_saved). Once meeting_saved is True the caller
    must NOT re-open the form (that would create a duplicate meeting)."""
    if not fill_meeting_details(driver):
        return (False, False)
    if not save_meeting_details(driver):
        return (False, False)
    # From here a mentoring meeting record EXISTS for this mentee.
    if not fill_questions(driver, mentee):
        return (False, True)
    if not save_questions(driver):
        return (False, True)
    return (True, True)


# ══════════════════════════════════════════════════════
#  MAIN AUTOMATION LOOP
# ══════════════════════════════════════════════════════
def run():
    print("╔══════════════════════════════════════════════════════╗")
    print("║  PU Mentoring Meeting Automation  v13 (UMS V2)        ║")
    print("║  Two-step save + mentoring-round filter              ║")
    print("╚══════════════════════════════════════════════════════╝")

    print("\n⚙️  Connecting to Chrome on port 9222...")
    try:
        driver = get_driver()
        print("✅ Chrome connected!\n")
    except Exception as e:
        print(f"❌ Chrome connect failed: {e}")
        print('\n👉 CMD mein pehle yeh run karo:')
        print('   "C:/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/selenium_chrome"')
        return

    # Phase 1: Scrape all mentees
    mentees = scrape_mentees(driver)
    if not mentees:
        print("❌ No mentees found. Dashboard check karo / login karo.")
        return

    # ════════════════════════════════════════════════════════
    #  USER SE POOCHO: KAUNSI MENTORING KARNI HAI?
    #  Input N  ->  sirf un students ki jinki current mentoring
    #               count == (N - 1) hai.
    #    N = 1  -> jinki abhi tak 0 mentoring hui (Meeting : 0)
    #    N = 2  -> jinki 1 mentoring ho chuki hai (Meeting : 1)
    # ════════════════════════════════════════════════════════
    # Kitne students har count pe hain, ye dikha do (help ke liye)
    dist = {}
    for m in mentees:
        c = m.get("mentoring_count")
        dist[c] = dist.get(c, 0) + 1
    print(f"\n   ℹ️  Current mentoring status breakdown: "
          + ", ".join(f"{k} done → {v} students" for k, v in sorted(dist.items(), key=lambda x: (x[0] is None, x[0]))))

    while True:
        raw = input(
            "\n🔢 Kaunsi mentoring karni hai? Integer daalo\n"
            "   (1 = jinki abhi 0 mentoring hui, 2 = jinki 1 ho chuki, ...): "
        ).strip()
        try:
            choice = int(raw)
        except ValueError:
            print("   ⚠️  Sirf integer daalo (jaise 1, 2, 3).")
            continue
        if choice < 1:
            print("   ⚠️  1 ya usse bada number daalo.")
            continue
        break

    target_count = choice - 1
    filtered = [m for m in mentees if m.get("mentoring_count") == target_count]

    print(f"\n   🎯 Input = {choice}  →  jinki current mentoring count = {target_count} hai unki mentoring hogi")
    print(f"   ✅ {len(filtered)} students match hue ({len(mentees)} total me se)")

    if not filtered:
        print("   ❌ Koi student is condition pe match nahi hua. Kuch nahi karunga. Exit.")
        return

    print("\n   Selected students:")
    for m in filtered:
        print(f"      • [{m['sr']:>2}] {m['name']:<35} | done: {m['mentoring_count']}")

    mentees = filtered

    total   = len(mentees)
    success = 0
    failed  = []
    
    # ================================================
    # START KAHA SE KRE (KON SE STUDENT SE START KRE)
    # ================================================
    # mentees = mentees[33:]
    print(f"\n{'='*55}")
    print(f"  Starting automation for {total} mentees")
    print(f"{'='*55}")

    for idx, m in enumerate(mentees):
        print(f"\n{'─'*55}")
        print(f"  [{idx+1}/{total}] {m['name']}")
        print(f"  Enrollment: {m['enrollment']} | Att: {m['attendance']}% | Gender: {m['gender']}")
        print(f"{'─'*55}")

        # ── Retry loop: try each mentee up to 3 times ──
        #  SAFETY: once the meeting record is saved (Step A), we must NOT
        #  re-open the form on retry — that would create a DUPLICATE meeting
        #  (i.e. double mentoring). So we stop retrying as soon as a meeting
        #  has been saved for this mentee.
        max_attempts = 3
        done = False

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                print(f"\n  🔄 Retry attempt {attempt}/{max_attempts}...")
                time.sleep(5)

            meeting_saved = False
            try:
                # Clear any stuck alerts/dialogs before starting
                try:
                    driver.switch_to.alert.dismiss()
                except: pass

                if not open_form(driver, m):
                    print(f"  ⚠️  Attempt {attempt}: could not open form")
                else:
                    ok, meeting_saved = do_observation(driver, m)
                    if ok:
                        success += 1
                        print(f"  ✅ DONE! [{success}/{total} completed]")
                        done = True
                        break

            except TimeoutException as te:
                print(f"  ⚠️  Timeout on attempt {attempt}: {te}")
                try:
                    driver.execute_script("window.stop();")
                except: pass
                time.sleep(5)
            except Exception as ex:
                print(f"  ⚠️  Error on attempt {attempt}: {ex}")
                time.sleep(3)

            # If a meeting record was already created, do NOT retry (avoid
            # a duplicate meeting). Report it for manual follow-up.
            if meeting_saved:
                print("  ⛔ Meeting already saved but questions incomplete — "
                      "NOT retrying to avoid a duplicate meeting.")
                break

            print(f"  ⚠️  Attempt {attempt} failed, will retry...")
            try:
                driver.execute_script("window.stop();")
            except: pass
            time.sleep(3)

        if not done:
            failed.append(f"{m['name']} ({m['enrollment']})")
            print(f"  ❌ FAILED after {max_attempts} attempts — moving to next")
            # Navigate away to reset browser state
            try:
                driver.execute_script("window.stop();")
                time.sleep(2)
                safe_navigate(driver, DASHBOARD_URL)
            except: pass

        # Pause between mentees — longer every 10 to let browser breathe
        if idx < total - 1:
            if (idx + 1) % 10 == 0:
                print(f"\n  😴 Cooling down for 10s (every 10 mentees)...")
                time.sleep(10)
            else:
                print(f"\n  ⏳ Next mentee in {DELAY_BETWEEN}s...")
                time.sleep(DELAY_BETWEEN)

    # ── Final Report ──
    print(f"\n{'═'*55}")
    print(f"  ✅ AUTOMATION COMPLETE")
    print(f"  ✅ Successful : {success}/{total}")
    print(f"  ❌ Failed     : {len(failed)}")
    if failed:
        print(f"\n  Failed mentees:")
        for f in failed:
            print(f"    • {f}")
    print(f"{'═'*55}\n")


if __name__ == "__main__":
    run()
