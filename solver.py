"""
Wordle Solver in Python

Acknowledgements:
- Wordle entropy / solver logic: inspired by Knutson-style community discussions 
  (partitioning by feedback and expected information gain).
- Selenium automation: uses Selenium WebDriver for browser control and 
  `webdriver-manager` (ChromeDriverManager) to automatically fetch the ChromeDriver.
  See Selenium documentation (https://www.selenium.dev/documentation/) and 
  webdriver-manager docs (https://pypi.org/project/webdriver-manager/).
- Python implementation informed by: "Python for Students" (Madecraft, 2024), 
  Petzold (2023) 'Code: The Hidden Language of Computer Hardware and Software*, 
  and Berry (2011) *What is Code?'.
- Iterative problem-solving inspired by Resnick & Robinson (2017)and Montfort et al. (2012)'.
- Human-computer interaction and interface timing informed by Kuniavsky (2008, 2010) 'User Experience Design for Ubiquitous Computing', 
  and Norman (1998) 'The Invisible Computer'.
"""

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import math
from collections import defaultdict

# ---------------------------
# Load your word lists
# ---------------------------

# POSSIBLE_ANSWERS:
# - list of valid target words (Wordle solutions)
# - separates solution space from allowed guesses to enable scoring heuristics
with open("wordle_answers.txt") as f:
    POSSIBLE_ANSWERS = [w.strip().lower() for w in f if len(w.strip()) == 5]

# ALLOWED_GUESSES:
# - complete set of guesses allowed by the game
# - provides additional choices for high-entropy guesses beyond the solution list
with open("wordle_guesses.txt") as f:
    ALLOWED_GUESSES = [w.strip().lower() for w in f if len(w.strip()) == 5]

# Ensure that every official answer is in the allowed guesses
assert set(POSSIBLE_ANSWERS).issubset(ALLOWED_GUESSES), "Answers must be subset of guesses."

# ---------------------------
# Wordle logic functions
# ---------------------------

def get_feedback(guess, answer):
    """
    Determine Wordle-style feedback for a guess.
    Returns a 5-character string using:
        'G' = green (correct letter, correct position)
        'Y' = yellow (letter present, wrong position)
        '.' = grey/absent (letter not present)
    
    Inspired by Resnick & Robinson (2017) concept of playful iteration:
    iteratively tests feedback logic for pruning candidates.
    """
    feedback = ["." for _ in range(5)]
    answer_chars = list(answer)  # mutable copy to track used letters

    # First pass: mark greens
    for i in range(5):
        if guess[i] == answer[i]:
            feedback[i] = "G"
            answer_chars[i] = None  # consume matched letter

    # Second pass: mark yellows
    for i in range(5):
        if feedback[i] == "." and guess[i] in answer_chars:
            feedback[i] = "Y"
            answer_chars[answer_chars.index(guess[i])] = None

    return "".join(feedback)


def filter_words(candidates, guess, feedback):
    """
    Prune candidate words consistent with feedback.

    Why:
    - Reflects Berry (2011) 'What is Code?' abstraction: the rules of Wordle
      are represented in software form for logical deduction.
    - Mirrors Montfort et al. (2012) stochastic exploration: filtering reduces
      uncertainty in solution space.
    """
    return [w for w in candidates if get_feedback(guess, w) == feedback]


def enforce_hard_mode(guess, known_greens, known_yellows):
    """
    Enforce 'hard mode' constraints:
      - Greens must match their positions.
      - Yellows must appear but not in forbidden positions.

    known_greens: dict of index -> confirmed letter
    known_yellows: dict of letter -> set(forbidden_positions)
    
    Why:
    - Aligns solver behaviour with human constraints.
    - Connects to iterative problem-solving ethos from Resnick & Robinson (2017).
    """
    # Check greens
    for i, ch in known_greens.items():
        if guess[i] != ch:
            return False

    # Check yellows
    for ch, forbidden_positions in known_yellows.items():
        if ch not in guess:
            return False
        if any(guess[pos] == ch for pos in forbidden_positions):
            return False

    return True


def entropy_score(guess, candidates):
    """
    Compute expected information gain (entropy) of a guess over remaining candidates.

    Mid-technical explanation:
    - Partition candidates by feedback for this guess.
    - p = partition_size / total candidates
    - Entropy = sum(-p*log2(p)) over partitions
    - High entropy indicates guess is likely to reduce uncertainty the most.

    Inspired by Knutson-style entropy approaches in Wordle solver literature.
    """
    partitions = defaultdict(int)
    for ans in candidates:
        fb = get_feedback(guess, ans)
        partitions[fb] += 1

    total = len(candidates)
    entropy = 0
    for count in partitions.values():
        p = count / total
        entropy -= p * math.log2(p)
    return entropy

# ---------------------------
# Selenium helper functions
# ---------------------------

def enter_guess(driver, guess):
    """
    Simulate typing a guess in the Wordle page using Selenium.

    Inspired by Norman (1998) UX principles to respect interface expectations.
    """
    body = driver.find_element(By.TAG_NAME, "body")
    for letter in guess:
        body.send_keys(letter)
        time.sleep(0.05)  # small delay for animation / realism
    body.send_keys(Keys.ENTER)


def read_feedback(driver, attempt_num):
    """
    Read tile feedback from the page DOM for a given attempt.

    UX-informed delay (Norman, Kuniavsky): allows animation to complete
    and reflects realistic interaction timings.

    Returns:
      'G', 'Y', '.' string representing feedback.
    """
    time.sleep(2)
    rows = driver.find_elements(By.CSS_SELECTOR, 'div[class^="Row-module_row__"]')
    if attempt_num >= len(rows):
        return None

    tiles = rows[attempt_num].find_elements(By.CSS_SELECTOR, 'div[class^="Tile-module_tile__"]')
    feedback = ""
    for tile in tiles:
        evaluation = tile.get_attribute("data-state")  # correct, present, absent
        if evaluation == "correct":
            feedback += "G"
        elif evaluation == "present":
            feedback += "Y"
        else:
            feedback += "."
    return feedback

# ---------------------------
# Main Wordle solver
# ---------------------------

def play_wordle():
    """
    Main automation loop for playing NYTimes Wordle with entropy-based solver.

    Methodological acknowledgements:
    - Wordle entropy logic: Knutson-style inspiration (expected information gain)
    - Selenium automation: ChromeDriverManager + Selenium WebDriver docs
    - Python foundations: Petzold (2023), "Python for Students" (2024)
    - Iterative problem-solving: Montfort et al. (2012)
    - UI timing: Norman (1998), Kuniavsky (2008, 2010)
    """
    driver = webdriver.Chrome()
    driver.get("https://www.nytimes.com/games/wordle/index.html")
    wait = WebDriverWait(driver, 1)

    # Click Play button
    try:
        play_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[data-testid="Play"]'))
        )
        play_button.click()
        time.sleep(0.2)
    except Exception as e:
        print("Play button not found:", e)

    # Close How To Play popup
    try:
        close_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[aria-label="Close"]'))
        )
        close_button.click()
        time.sleep(0.3)
    except Exception as e:
        print("Close button not found:", e)

    print("✅ Ready to start guessing!")

    # ---------------------------
    # Game loop
    # ---------------------------

    candidates = POSSIBLE_ANSWERS.copy()
    known_greens = {}  # index -> confirmed letter
    known_yellows = defaultdict(set)  # letter -> forbidden positions
    previous_guesses = set()  # set of all guesses already made
    attempts = 0

    guess = "grain"  # first seed guess

    while attempts < 6:
        print(f"Attempt {attempts+1}: {guess.upper()}")
        enter_guess(driver, guess)
        feedback = read_feedback(driver, attempts)
        if feedback is None:
            print("Could not read feedback.")
            break
        print(f"Feedback: {feedback}")

        if feedback == "GGGGG":
            print("🎉 Wordle solved!")
            break

        # Update known greens and yellows
        for i, f in enumerate(feedback):
            if f == "G":
                known_greens[i] = guess[i]
            elif f == "Y":
                known_yellows[guess[i]].add(i)

        # Prune candidates
        candidates = filter_words(candidates, guess, feedback)
        previous_guesses.add(guess)

        # Select next guess with entropy and hard mode constraints
        guess_pool = [g for g in ALLOWED_GUESSES if enforce_hard_mode(g, known_greens, known_yellows)]
        guess_pool = [g for g in guess_pool if g not in previous_guesses]

        if not guess_pool:
            print("No valid guesses left!")
            break

        best_score = -1
        next_guess = None
        for g in guess_pool:
            e = entropy_score(g, candidates)
            if e > best_score:
                best_score = e
                next_guess = g

        guess = next_guess
        attempts += 1

    driver.quit()

# ---------------------------
# Run the solver
# ---------------------------
if __name__ == "__main__":
    play_wordle()
