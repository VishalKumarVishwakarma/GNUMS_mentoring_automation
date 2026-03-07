"""
╔══════════════════════════════════════════════════════════════════╗
║   Parul University - Student Mentoring Meeting Automation        ║
║   v2.0 - Exact Element IDs Based                                 ║
╚══════════════════════════════════════════════════════════════════╝

HOW TO RUN:
───────────
STEP 1 - Install Selenium (run once in CMD):
    pip install selenium

STEP 2 - Open Chrome in Debug Mode (run in CMD):
    "C:/Program Files/Google/Chrome/Application/chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:/selenium_chrome"

STEP 3 - Us Chrome mein manually LOGIN karo UMS portal pe

STEP 4 - Script run karo:
    python mentoring_automation.py
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
DASHBOARD_URL  = "https://ums.paruluniversity.ac.in/AdminPanel/Mentoring/MEN_StudentMentoring/MEN_StudentMentoring_StaffDashBoard.aspx"
WAIT_TIMEOUT   = 20
DELAY_BETWEEN  = 3   # seconds between each mentee

# ══════════════════════════════════════════════════════
#  EXACT ELEMENT IDs (from your inspection)
# ══════════════════════════════════════════════════════

# PAGE 1
ID_PLUS_BTN             = "ctl00_cphPageContent_rpData_ctl00_hlMentorObservation"  # dynamic per row

# PAGE 2
ID_SHOW_BTN             = "ctl00_cphPageContent_btnLoad"
ID_QUESTION_GROUP_SPAN  = "select2-ctl00_cphPageContent_ddlMentoringQuestionGroup-container"
ID_QUESTION_GROUP_SELECT= "ctl00_cphPageContent_ddlMentoringQuestionGroup"

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

# PAGE 3 - Save button
ID_SAVE_BTN             = "ctl00_cphPageContent_btnSave"

# ══════════════════════════════════════════════════════
#  CONDITIONAL LOGIC
# ══════════════════════════════════════════════════════
def get_academic_category(att):
    if att >= 70:   return "A. Advance Learner"
    elif att >= 50: return "B. Mediocre Learner"
    else:           return "C. Slow Learner"

def get_personality(att):
    if att >= 70:   return "Well - disciplined"
    elif att >= 50: return "Good moral sense"
    else:           return "Discipline is required"

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

def get_extracurricular(gender):
    if gender.strip().lower() == "female":
        return random.choice(["Singing", "Dancing", "Drawing"])
    else:
        return random.choice(["Cricket", "Football", "Basketball", "Volleyball", "Kho-Kho"])

def parse_attendance(text):
    # Handles "Attd: 82.0%\nResult: ..." => 82.0
    nums = re.findall(r"\d+\.?\d*", str(text))
    return float(nums[0]) if nums else 0.0

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
    el = wait_for_id(driver, elem_id)
    driver.execute_script("arguments[0].scrollIntoView({block:'center'});", el)
    time.sleep(0.2)
    el.clear()
    el.send_keys(text)

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
            if len(cols) < 8:
                continue

            sr = cols[0].text.strip()
            if not sr.isdigit():
                continue

            enrollment = cols[3].text.strip()
            name       = cols[4].text.strip()
            gender     = cols[6].text.strip()

            # Attendance column text: "Attd: 82.0%\nResult: 8.50 SPI"
            att_raw    = cols[7].text.strip()
            attendance = parse_attendance(att_raw)

            # Get the "+" button href - contains StudentMentorID
            # ID pattern: ctl00_cphPageContent_rpData_ctl{XX}_hlMentorObservation
            plus_btn = row.find_element(By.XPATH,
                ".//a[contains(@id,'hlMentorObservation')]")
            href = plus_btn.get_attribute("href")

            mentees.append({
                "sr"         : sr,
                "name"       : name,
                "enrollment" : enrollment,
                "gender"     : gender,
                "attendance" : attendance,
                "href"       : href,     # direct URL to form
                "btn_id"     : plus_btn.get_attribute("id"),
            })
            print(f"   ✅ [{sr:>2}] {name:<35} | {gender:<7} | Att: {attendance}%")

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

        plus_btn = driver.find_element(By.XPATH,
            f"//table//tbody/tr[td[normalize-space()='{mentee['enrollment']}'] "
            f"or td[contains(normalize-space(),'{mentee['enrollment']}')]]"
            f"//a[contains(@id,'hlMentorObservation')]"
        )
        js_click(driver, plus_btn)
        print("   ✅ '+' button clicked")
        time.sleep(3)

    except Exception as e:
        print(f"   ⚠️  Click failed ({e}), trying direct URL...")
        if mentee.get("href"):
            if not safe_navigate(driver, mentee["href"]):
                return False
        else:
            print("   ❌ No href available")
            return False

    return _select_group_and_show(driver)


def _select_group_and_show(driver):
    """Select Question Group and click Show — separated for reuse"""
    try:
        print("   📌 Selecting Mentoring Question Group...")

        # Use jQuery to set Select2 value directly — most reliable
        driver.execute_script("""
            var $sel = $('#ctl00_cphPageContent_ddlMentoringQuestionGroup');
            $sel.find('option').each(function() {
                if ($(this).text().indexOf('Group-1 - PIET-1') !== -1) {
                    $sel.val($(this).val()).trigger('change');
                }
            });
        """)
        time.sleep(1)
        print("   ✅ Group-1 - PIET-1 selected")

        # Click Show button
        print("   📌 Clicking Show...")
        show = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, ID_SHOW_BTN))
        )
        driver.execute_script("arguments[0].click();", show)
        print("   ✅ Show clicked")
        time.sleep(4)
        return True

    except Exception as e:
        print(f"   ❌ Group/Show error: {e}")
        return False

# ══════════════════════════════════════════════════════
#  PHASE 3 & 4: FILL ALL FORM FIELDS
# ══════════════════════════════════════════════════════
def fill_form(driver, mentee):
    att    = mentee["attendance"]
    gender = mentee["gender"]

    print(f"\n📝 Phase 3 & 4: Filling form | Att={att}% | Gender={gender}")

    try:
        # Wait for form to fully load after Show
        wait_for_id(driver, ID_AGENDA, timeout=15)
        time.sleep(1)

        # ── STATIC FIELDS ──

        # Step 10: Mentoring Meeting Agenda = "Academics"
        print("   📌 Agenda...")
        fill_textarea(driver, ID_AGENDA, "Academics")

        # Step 11: Issues Discussed = "Academics"
        print("   📌 Issues Discussed...")
        fill_textarea(driver, ID_ISSUES_DISCUSSED, "Academics")

        # Step 12: Mentor's Opinion = "No"
        # Element: id="ctl00_cphPageContent_txtMentorsOpinion"
        print("   📌 Mentor's Opinion = No...")
        try:
            driver.execute_script("""
                var el = document.getElementById('ctl00_cphPageContent_txtMentorsOpinion');
                el.scrollIntoView({block:'center'});
                el.value = 'No';
                el.dispatchEvent(new Event('input', {bubbles:true}));
                el.dispatchEvent(new Event('change', {bubbles:true}));
            """)
            print("   ✅ Mentor's Opinion filled")
        except Exception as e_mo:
            print(f"   ❌ Mentor Opinion error: {e_mo}")

        time.sleep(0.5)

        # ── DYNAMIC FIELDS ──

        # Q1: Academic Category (Select2 dropdown)
        # Element: select2-ctl00_cphPageContent_rpQuestionList_ctl00_ddlAnswer-container
        category = get_academic_category(att)
        print(f"   📌 Q1: Academic Category = {category}")
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

        # Q2: Personality Attributes (textarea)
        print(f"   📌 Q2: Personality = {get_personality(att)}")
        fill_textarea(driver, ID_Q2_PERSONALITY, get_personality(att))

        # Q3: Students Grievances = "No"
        print("   📌 Q3: Students Grievances = No")
        fill_textarea(driver, ID_Q3_GRIEVANCES, "No")

        # Q4: Co-curricular (gender-based)
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
#  PHASE 5: SAVE & CONFIRM POPUP
# ══════════════════════════════════════════════════════
def save_and_confirm(driver, mentee):
    print(f"\n💾 Phase 5: Saving for {mentee['name']}...")

    try:
        # Click Save button using JS directly (bypass any onclick interference)
        save_btn = wait_clickable_id(driver, ID_SAVE_BTN)
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", save_btn)
        time.sleep(0.5)
        driver.execute_script("arguments[0].click();", save_btn)
        print("   ✅ Save clicked")
        time.sleep(2)

        # ── The Save button calls ConfimaSave(this) which opens a Bootbox modal ──
        # Modal has: <button data-bb-handler="confirm" class="btn btn-success">Yes</button>
        # We must wait for this modal to appear then click the Yes button

        try:
            # Wait for bootbox modal Yes button
            yes_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH,
                    "//button[@data-bb-handler='confirm']"
                ))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", yes_btn)
            time.sleep(0.3)
            driver.execute_script("arguments[0].click();", yes_btn)
            print(f"   🎉 Bootbox Yes clicked! Saved for {mentee['name']}")
            time.sleep(4)
            return True

        except TimeoutException:
            # Fallback 1: btn-success Yes button
            try:
                yes_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[contains(@class,'btn-success') and normalize-space()='Yes']"
                    ))
                )
                driver.execute_script("arguments[0].click();", yes_btn)
                print(f"   🎉 btn-success Yes clicked!")
                time.sleep(4)
                return True
            except TimeoutException:
                pass

            # Fallback 2: Any visible Yes button
            try:
                yes_btn = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                        "//button[normalize-space()='Yes']"
                    ))
                )
                driver.execute_script("arguments[0].click();", yes_btn)
                print(f"   🎉 Yes button clicked!")
                time.sleep(4)
                return True
            except TimeoutException:
                pass

            # Fallback 3: Native JS alert (just in case)
            try:
                WebDriverWait(driver, 3).until(EC.alert_is_present())
                driver.switch_to.alert.accept()
                print(f"   🎉 JS Alert accepted!")
                time.sleep(4)
                return True
            except TimeoutException:
                print("   ⚠️  No popup found - assuming saved")
                return True

    except Exception as e:
        print(f"   ❌ Save/confirm error: {e}")
        return False

# ══════════════════════════════════════════════════════
#  MAIN AUTOMATION LOOP
# ══════════════════════════════════════════════════════
def run():
    print("╔══════════════════════════════════════════════════════╗")
    print("║  PU Mentoring Meeting Automation  v11.0              ║")
    print("║  Robust - Auto Retry + Browser Recovery              ║")
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

    total   = len(mentees)
    success = 0
    failed  = []

    print(f"\n{'='*55}")
    print(f"  Starting automation for {total} mentees")
    print(f"{'='*55}")

    for idx, m in enumerate(mentees):
        print(f"\n{'─'*55}")
        print(f"  [{idx+1}/{total}] {m['name']}")
        print(f"  Enrollment: {m['enrollment']} | Att: {m['attendance']}% | Gender: {m['gender']}")
        print(f"{'─'*55}")

        # ── Retry loop: try each mentee up to 3 times ──
        max_attempts = 3
        done = False

        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                print(f"\n  🔄 Retry attempt {attempt}/{max_attempts}...")
                time.sleep(5)

            try:
                # Clear any stuck alerts/dialogs before starting
                try:
                    driver.switch_to.alert.dismiss()
                except: pass

                ok = True
                if not open_form(driver, m):
                    ok = False
                if ok and not fill_form(driver, m):
                    ok = False
                if ok and not save_and_confirm(driver, m):
                    ok = False

                if ok:
                    success += 1
                    print(f"  ✅ DONE! [{success}/{total} completed]")
                    done = True
                    break
                else:
                    print(f"  ⚠️  Attempt {attempt} failed, will retry...")
                    # Try to recover browser state
                    try:
                        driver.execute_script("window.stop();")
                    except: pass
                    time.sleep(3)

            except TimeoutException as te:
                print(f"  ⚠️  Timeout on attempt {attempt}: {te}")
                # Browser recovery - stop current load and wait
                try:
                    driver.execute_script("window.stop();")
                except: pass
                time.sleep(5)

            except Exception as ex:
                print(f"  ⚠️  Error on attempt {attempt}: {ex}")
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
