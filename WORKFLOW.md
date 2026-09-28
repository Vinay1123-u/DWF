# Dictionary Word Finder & Vocabulary Studio — Complete Workflow Specification

This document provides a comprehensive end-to-end guide to the **Dictionary Word Finder & Vocabulary Studio** architecture, data flow, dictionary validation pipeline, interactive quiz system, database models, REST APIs, and deployment instructions.

---

## 1. System Architecture Overview

The system is built as a high-performance, zero-dependency full-stack application utilizing Python standard libraries (`http.server`, `sqlite3`, `urllib`) for the backend and modern vanilla HTML5, CSS3, and JavaScript for the frontend.

```
+-----------------------------------------------------------------------------------+
|                                  USER BROWSER                                     |
|  +-----------------------------------------------------------------------------+  |
|  | Single Page Application (HTML5 / Vanilla CSS / Modern JS / Web Audio API)    |  |
|  | - Dashboard & Word of the Day                                              |  |
|  | - Strict Verified Dictionary Search & Audio Pronunciation                   |  |
|  | - Interactive Vocabulary Quiz Engine (5 Modes, 3 Difficulties)              |  |
|  | - Saved Words (Bookmarks) Management                                       |  |
|  | - Search History & Quiz Performance History                                 |  |
|  | - User Authentication & Dark/Light Theme Switching                         |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------+-----------------------------------------+
                                          |
                           HTTP REST API  |  JSON Payload
                                          v
+-----------------------------------------------------------------------------------+
|                              PYTHON BACKEND SERVER                                |
|  (server.py on http://localhost:3000)                                             |
|                                                                                   |
|  +-----------------------------+       +---------------------------------------+  |
|  | RequestHandler              |       | Authentication Engine                 |  |
|  | (do_GET, do_POST, do_OPTIONS)       | (SHA-256 Password Hashing & Sessions) |  |
|  +--------------+--------------+       +---------------------------------------+  |
|                 |                                                                 |
|                 +-----------------------------------+                             |
|                 v                                   v                             |
|  +-------------------------------+   +-----------------------------------------+  |
|  | Strict Dictionary Engine      |   | Dynamic Quiz Generator                  |  |
|  | - Phonotactics & Plausibility |   | - Curated Master Lexicon (Easy/Med/Hard)|  |
|  | - Datamuse Lexicon & IPA      |   | - 4-Option Shuffled MCQs                |  |
|  | - Wiktionary Context          |   | - "My Saved Words" Custom Quiz Mode     |  |
|  | - Did-You-Mean Suggestions    |   | - Scoring & Streak Tracking             |  |
|  +---------------+---------------+   +--------------------+--------------------+  |
+------------------|----------------------------------------|-----------------------+
                   |                                        |
                   v                                        v
+------------------------------------+   +------------------------------------------+
|      EXTERNAL LEXICON APIS         |   |          SQLITE DATABASE                 |
|  - Datamuse API (Lexicon & IPA)    |   |  (database/dictionary.db)                |
|  - Wiktionary REST API             |   |  - users                                 |
|  - Datamuse Suggestions (/sug)     |   |  - search_history                        |
|                                    |   |  - saved_words                           |
|                                    |   |  - quiz_history                          |
+------------------------------------+   +------------------------------------------+
```

---

## 2. Strict Dictionary Validation & Word Lookup Workflow

### The Problem Solved
Traditional dictionaries or AI wrappers often hallucinate or invent dummy meanings for misspelled, nonsense, or keyboard-mash words (e.g., claiming `"asdfghjkl"` or `"xyz123"` is "recognized in modern vocabulary"). 

In this application, **only legitimate, meaningful English dictionary words present in standard Google / English lexicons are accepted**.

### The Multi-Stage Verification Pipeline:

```
[User Input Query]
       |
       v
[Stage 1: Cleansing & Normalization]
  - Strip whitespace, lowercase, enforce alphabetic format [a-zA-Z\- ]+
       |
       v
[Stage 2: Phonotactic & Plausibility Filtering]
  - Word length >= 2 characters
  - Must contain at least one vowel sound ([aeiouy])
  - Rejects >= 5 consecutive consonants
  - Rejects keyboard mash patterns ("asdf", "hjkl", "qwer", "zxcv", etc.)
       |
       +---> [Failed Plausibility] ---> Generate Datamuse spelling suggestions
       |                                Return { found: False, suggestions: [...] }
       v
[Stage 3: Curated Master Lexicon Check]
  - Instant lookup in built-in verified academic vocabulary bank
  - Returns definition, part of speech, IPA phonetic, synonyms, antonyms, examples
       |
       v (if not in curated bank)
[Stage 4: Authoritative Datamuse Lexicon Check]
  - Query: https://api.datamuse.com/words?sp={word}&qe=sp&md=dpfr&ipa=1&max=1
  - Verifies exact lemma existence in WordNet, CMU, and Webster's indexes
  - Extracts IPA pronunciation (/ˈkændɪd/)
  - Extracts grammatical parts of speech (n, v, adj, adv)
  - Extracts official dictionary definitions
       |
       v
[Stage 5: Wiktionary Context & Real Example Sentences]
  - Query: https://en.wiktionary.org/api/rest_v1/page/definition/{word}
  - Validates standard grammatical entries (Noun, Verb, Adjective, etc.)
  - Extracts real illustrative usage examples
       |
       v
[Stage 6: Final Decision & Thesaurus Expansion]
  - IF Definitions Found:
      * Query Datamuse rel_syn (Synonyms)
      * Query Datamuse rel_ant (Antonyms)
      * Query Datamuse ml (Related Lexicon Words)
      * Save to search_history (only verified words are recorded)
      * Return { found: True, word: {...} }
  - IF No Valid Definitions Found:
      * DO NOT save to history
      * Query Datamuse /sug?s={word} for 5 real spelling suggestions
      * Return { found: False, suggestions: [...], message: "Word not found..." }
```

---

## 3. Vocabulary Quiz System Workflow

The Quiz Section provides an engaging, educational game loop in both backend and frontend.

### 1. Quiz Modes / Categories:
1. **All-Round Mixed (`all`)**: Randomized mixture of Definitions, Reverse Definitions, Synonyms, and Antonyms.
2. **Definitions (`definition`)**: Given a target word, select its correct primary definition from 4 choices.
3. **Reverse Definitions (`reverse_definition`)**: Given an authoritative definition, select which word it defines.
4. **Synonyms Challenge (`synonym`)**: Identify the closest synonym for the given word.
5. **Antonyms Challenge (`antonym`)**: Identify the direct opposite/antonym for the given word.
6. **My Saved Words (`saved`)**: Dynamically quizzes the user on words they personally bookmarked in their account!

### 2. Difficulty Tiers:
- **Beginner (Easy)**: Everyday core vocabulary (*candid, diligent, serene, benevolent, frugal, vibrant, resilient, humble, empathy...*).
- **Intermediate (Medium)**: Academic & professional vocabulary (*ubiquitous, ephemeral, meticulous, superfluous, pragmatic, fastidious, gregarious, inevitable...*).
- **Advanced (Hard / GRE)**: Advanced literary and competitive exam words (*anachronistic, cacophony, grandiloquent, inchoate, juxtapose, loquacious, magnanimous, obsequious, pernicious, recalcitrant, sycophant, taciturn, veracity...*).

### 3. Interactive Quiz Gameplay Loop:
```
[User Selects Category, Difficulty, & Question Count (5 or 10)]
       |
       v
[Backend API: GET /api/quiz/questions]
  - Generates N randomized questions with 4 distinct options and 1 correct answer
       |
       v
[User Views Question in UI]
  - Displays Question Prompt, Progress Bar, Target Word, Phonetic badge
  - "🔊 Pronounce" button reads word aloud via Web SpeechSynthesis API
       |
       v
[User Clicks Option A, B, C, or D]
  - Web Audio API synthesizes instant acoustic chime:
      * Correct: High-frequency dual chime (587Hz -> 880Hz) + Streak increment + Points bonus
      * Incorrect: Low-frequency gentle boop (220Hz -> 164Hz) + Streak reset
  - Visual Feedback:
      * Selected button turns Emerald Green (if correct) or Crimson Red (if wrong)
      * Correct answer turns Green
  - Explanation Banner slides down:
      * Displays word, part of speech, exact definition, and example sentence
      * "☆ Save Word" button allows instant bookmarking of unfamiliar words!
  - "Next Question →" button appears
       |
       v
[After Final Question: Quiz Results Screen]
  - Displays circular animated percentage score
  - Awards performance badge (e.g., "Vocabulary Master 🏆", "Lexicon Champion ⭐")
  - Shows breakdown: Correct, Incorrect, Total Points
  - Automatically posts results to POST /api/quiz/submit
  - Logs session to SQLite quiz_history table
  - Updates Dashboard and Lobby stats
```

---

## 4. SQLite Database Schema

Located at `database/dictionary.db`:

```sql
-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 2. Search History Table (Only stores verified words)
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    searched_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Saved Words (Bookmarks) Table
CREATE TABLE IF NOT EXISTS saved_words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    word TEXT NOT NULL,
    saved_at TEXT NOT NULL,
    UNIQUE(user_id, word),
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 4. Quiz History Table
CREATE TABLE IF NOT EXISTS quiz_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL,
    difficulty TEXT NOT NULL,
    score INTEGER NOT NULL,
    total_questions INTEGER NOT NULL,
    percentage REAL NOT NULL,
    completed_at TEXT NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

---

## 5. REST API Documentation

### Search & Dictionary APIs
| Method | Endpoint | Query Parameters | Description |
|---|---|---|---|
| `GET` | `/api/search` | `word` (str), `user_id` (int) | Verifies word against Google/Datamuse/Wiktionary lexicons. Returns full definitions, phonetics, audio, synonyms, antonyms, examples, or suggestions if invalid. |
| `GET` | `/api/word_of_the_day` | none | Returns the featured Word of the Day with definition, part of speech, phonetic, and example. |

### Quiz APIs
| Method | Endpoint | Parameters / Body | Description |
|---|---|---|---|
| `GET` | `/api/quiz/questions` | `user_id` (int), `category` (str), `difficulty` (str), `count` (int) | Generates customized multiple-choice quiz questions with 4 options and explanations. |
| `POST` | `/api/quiz/submit` | JSON: `{ user_id, category, difficulty, score, total_questions }` | Records completed quiz session into SQLite database and returns calculated percentage. |
| `GET` | `/api/quiz/stats` | `user_id` (int) | Returns total quizzes completed and highest score percentage. |
| `GET` | `/api/quiz/history` | `user_id` (int) | Returns chronological list of past quiz attempts with date, category, difficulty, and scores. |

### User & Bookmarks APIs
| Method | Endpoint | Parameters / Body | Description |
|---|---|---|---|
| `POST` | `/api/register` | JSON: `{ username, email, password }` | Creates user account with secure SHA-256 password hash. |
| `POST` | `/api/login` | JSON: `{ email, password }` | Authenticates user against SQLite database. |
| `GET` | `/api/saved` | `user_id` (int) | Retrieves all bookmarked words for the user. |
| `POST` | `/api/toggle_save` | JSON: `{ user_id, word }` | Toggles bookmark status (adds or removes) for the word. |
| `GET` | `/api/history` | `user_id` (int) | Retrieves recent verified search history. |
| `POST` | `/api/clear_history` | JSON: `{ user_id }` | Clears search history for the user. |
| `GET` | `/api/stats` | `user_id` (int) | Retrieves summary stats: total searches, saved words, quizzes completed, and best score. |

---

## 6. Frontend Navigation & User Views

| Tab Name | Purpose & Features |
|---|---|
| **📊 Dashboard** | Welcome greeting, featured Word of the Day banner (with audio pronunciation button), quick search bar, 4 live stat cards, and Quick Quiz launcher. |
| **🔍 Word Search** | High-speed dictionary search. Renders word title, IPA phonetics, native audio speaker button, parts of speech, numbered definitions, real examples, synonym/antonym pills, and interactive "Did you mean:" suggestions for typos. |
| **🧠 Vocabulary Quiz** | Full quiz studio: Lobby with category selection, difficulty tiers, question counter, interactive gameplay HUD with streak multiplier, Web Audio chimes, instant feedback, explanation banners, and results screen. |
| **⭐ Saved Words** | List of all personal bookmarks with timestamps. Includes one-click "Quiz Me on My Saved Words" button. |
| **🕒 Search History** | Chronological log of past searches with one-click reload and "Clear History" button. |
| **👤 Profile** | User account information and learning status. |
| **⚙️ Settings** | Theme toggle between Modern Light and High-Contrast Dark Mode. |

---

## 7. How to Run and Test Locally

### Prerequisites
- Python 3.8+ (No external pip dependencies required).

### 1. Launch the Application
```bash
python server.py
```
Output:
```
Dictionary Word Finder Studio running on http://localhost:3000
```

### 2. Access in Web Browser
Open your browser and navigate to:
```
http://localhost:3000
```

### 3. Automated Endpoint Test Script
You can verify the backend endpoints at any time with:
```bash
python -c "
import urllib.request, json
# Test Word of the Day
with urllib.request.urlopen('http://localhost:3000/api/word_of_the_day') as r:
    print('WOTD:', json.loads(r.read())['word'])
# Test Word Verification
with urllib.request.urlopen('http://localhost:3000/api/search?word=serendipity&user_id=1') as r:
    print('Valid word found:', json.loads(r.read())['found'])
with urllib.request.urlopen('http://localhost:3000/api/search?word=asdfghjkl&user_id=1') as r:
    print('Fake word rejected:', not json.loads(r.read())['found'])
# Test Quiz Generation
with urllib.request.urlopen('http://localhost:3000/api/quiz/questions?count=5') as r:
    print('Quiz generated questions:', len(json.loads(r.read())))
"
```

---

## 8. Git & Remote Repository Workflow

### Repository URL:
`https://github.com/Vinay1123-u/DWF.git`

### Git Command Sequence:
```bash
# 1. Initialize repository
git init

# 2. Configure remote origin
git remote add origin https://github.com/Vinay1123-u/DWF.git

# 3. Rename branch to main
git branch -M main

# 4. Stage all files (sensitive files and build binaries are safely ignored by .gitignore)
git add .

# 5. Commit changes
git commit -m "feat: complete dictionary word finder with verified lexicon lookup, quiz section, and workflow documentation"

# 6. Push to remote
git push -u origin main
```
