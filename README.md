# Wordle Solver – Python + Selenium
A tool to automatically solve the New York Times Wordle game using algorithmic logic

---

## Table of Contents
- Overview
- Features
- Technologies Used
- Installation
- Usage
- How It Works
- Project Status
- Future Improvements
- Acknowledgements
- Contact

---

## Overview
This project is a Python-based solver for the popular Wordle game by the New York Times.  
It uses the browser automation library Selenium to interact with the game UI, reads letter feedback (green, yellow, grey), and applies entropy-based scoring and hard-mode constraints to choose optimal guesses.  
The goal is to demonstrate algorithm design, search space reduction, and automated decision-making.

---

## Features
- Automatically opens Chrome and navigates to the Wordle web page
- Closes pop-up dialogues and begins gameplay
- Enters guesses, reads feedback from the grid, and updates internal state
- Applies filtering of possible answers and uses information-theoretic entropy to select the next guess
- Implements hard-mode logic (respecting known greens + yellow constraints)
- Logs and displays progress in the console

---

## Technologies Used
- Python 3.x
- [Selenium WebDriver](https://www.selenium.dev/) – for browser automation
- [webdriver-manager](https://pypi.org/project/webdriver-manager/) – to manage the ChromeDriver binary
- `wordle_answers.txt` – list of valid answer words
- `wordle_guesses.txt` – list of allowed guess words

---

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/<your-username>/WordleSolver.git
   cd WordleSolver

2. Create and activate a virtual environment (recommended):
  python3 -m venv venv
  source venv/bin/activate

3. Install dependencies:
  pip install -r requirements.txt

4. Ensure Google Chrome is installed (or change the browser in code if needed)

5. Place wordle_answers.txt and wordle_guesses.txt in the same folder as solver.py

---

## Usage
Run the solver:
python solver.py
   - The program will launch Chrome and navigate to the Wordle URL
   - It makes an initial guess (e.g., “grain”), reads the tile feedback, and iterates up to 6 attempts
   - All progress is logged to the console

---

## How It Works

1. Feedback Reading: get_feedback(guess, answer) returns a string of characters:
   - G for correct letter in correct position
   - Y for correct letter in wrong position
   - . for absent letters

2. Filtering Candidates: filter_words(candidates, guess, feedback) reduces the answer list to those consistent with the feedback.

3. Entropy Scoring: entropy_score(guess, candidates) computes for each possible guess how much information it would yield across remaining candidates; the guess with highest expected information is chosen.
   
4. Hard Mode Logic: enforce_hard_mode(guess, known_greens, known_yellows) ensures new guesses respect previously known constraints.
   
5. Main Loop: Repeats: make guess → read feedback → update state → filter candidates → pick next guess, until solved or attempts exhausted.

---

## Project Status

Complete – Version 1.0 The solver successfully automates the browser session and solves the Wordle game under current conditions (subject to UI changes on the official site). Minor tweaks (e.g., delays, UI selectors) may be required if the game site changes its HTML structure.

---

## Future Improvements
   - Add CLI fallback mode (no browser) to simulate solving offline
   - Integrate a graphical UI to visualise guess-by-guess progress
   - Improve performance of entropy calculations for larger word lists
   - Extend solver to support “Wordle clone” games for custom word lists
   - Add logging & analytics of guess sequences for research purposes

---

## Acknowledgements
   - The article “How to write a good README for your GitHub project” (Bulldog Job) provided guidelines on structure and clarity
   - The README-cheatsheet by Ritaly helped ensure clear sectioning and readability
   - Selenium WebDriver and webdriver-manager open-source libraries
   - Wordle entropy / solver logic inspired by Knutson-style community discussions (partitioning by feedback and expected information gain)
   - Python implementation informed by: "Python for Students" (Madecraft, 2024), Petzold (2023) 'Code: The Hidden Language of Computer Hardware and Software', and Berry (2011) 'What is Code?'
   - Iterative problem-solving and playful iteration inspired by Resnick & Robinson (2017) and Montfort et al. (2012)
   - Human-computer interaction and interface timing informed by Kuniavsky (2008, 2010) 'User Experience Design for Ubiquitous Computing', and Norman (1998) 'The Invisible Computer'

---

## Contact
Created by Lili Blazquez (liliblaz01@gmail.com)
