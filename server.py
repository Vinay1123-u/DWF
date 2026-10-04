import os
import sys
import json
import re
import sqlite3
import hashlib
import random
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import urllib.error

PORT = 3000
DB_DIR = os.path.join(os.path.dirname(__file__), "database")
DB_PATH = os.path.join(DB_DIR, "dictionary.db")
ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")

def get_env_value(key_name):
    val = os.environ.get(key_name)
    if val:
        return val.strip()
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key_name}="):
                    return line[len(key_name) + 1:].strip()
    return ""

def set_env_value(key_name, val):
    clean_val = val.strip() if val else ""
    os.environ[key_name] = clean_val
    lines = []
    found = False
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip().startswith(f"{key_name}="):
                    lines.append(f"{key_name}={clean_val}\n")
                    found = True
                else:
                    lines.append(line)
    if not found:
        lines.append(f"{key_name}={clean_val}\n")
    with open(ENV_PATH, "w", encoding="utf-8") as f:
        f.writelines(lines)

def init_db():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            searched_at TEXT NOT NULL,
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS saved_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            word TEXT NOT NULL,
            saved_at TEXT NOT NULL,
            UNIQUE(user_id, word),
            FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)
    cur.execute("""
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
        )
    """)
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

# Curated High-Quality Master Vocabulary Bank for Verified Quizzes & Word-of-the-Day
VOCABULARY_BANK = {
    "easy": [
        {"word": "candid", "pos": "Adjective", "phonetic": "/ˈkændɪd/", "def": "Truthful, straightforward, and sincere in expression.", "syn": "frank", "ant": "deceptive", "ex": "She gave a candid assessment of the proposal."},
        {"word": "diligent", "pos": "Adjective", "phonetic": "/ˈdɪlɪdʒənt/", "def": "Showing constant and persistent effort in work or study.", "syn": "industrious", "ant": "lazy", "ex": "A diligent student consistently achieves strong results."},
        {"word": "serene", "pos": "Adjective", "phonetic": "/səˈriːn/", "def": "Calm, peaceful, and untroubled by noise or stress.", "syn": "tranquil", "ant": "chaotic", "ex": "The mountain lake looked serene at sunrise."},
        {"word": "benevolent", "pos": "Adjective", "phonetic": "/bəˈnɛvələnt/", "def": "Well-meaning, kind-hearted, and charitable toward others.", "syn": "generous", "ant": "malevolent", "ex": "A benevolent benefactor funded the school library."},
        {"word": "frugal", "pos": "Adjective", "phonetic": "/ˈfruːɡəl/", "def": "Prudent and economical in saving resources or money.", "syn": "thrifty", "ant": "wasteful", "ex": "Her frugal lifestyle allowed her to travel the world."},
        {"word": "lucid", "pos": "Adjective", "phonetic": "/ˈluːsɪd/", "def": "Expressed clearly and easy to comprehend; rational.", "syn": "clear", "ant": "obscure", "ex": "The professor gave a lucid explanation of quantum theory."},
        {"word": "vibrant", "pos": "Adjective", "phonetic": "/ˈvaɪbrənt/", "def": "Full of energy, enthusiasm, life, or bright color.", "syn": "lively", "ant": "dull", "ex": "The market was vibrant with colors and aromatic spices."},
        {"word": "resilient", "pos": "Adjective", "phonetic": "/rɪˈzɪliənt/", "def": "Able to quickly withstand and recover from hardship.", "syn": "adaptable", "ant": "fragile", "ex": "Communities proved resilient in rebuilding after the storm."},
        {"word": "humble", "pos": "Adjective", "phonetic": "/ˈhʌmbəl/", "def": "Having a modest estimate of one's own importance.", "syn": "modest", "ant": "arrogant", "ex": "Despite his monumental success, he remained humble."},
        {"word": "empathy", "pos": "Noun", "phonetic": "/ˈɛmpəθi/", "def": "The psychological capacity to share another person's feelings.", "syn": "compassion", "ant": "apathy", "ex": "Great leaders demonstrate empathy when listening to others."},
        {"word": "cordial", "pos": "Adjective", "phonetic": "/ˈkɔːrdiəl/", "def": "Warm, friendly, and deeply polite.", "syn": "genial", "ant": "hostile", "ex": "We received a cordial welcome at the embassy."},
        {"word": "zenith", "pos": "Noun", "phonetic": "/ˈzɛnɪθ/", "def": "The highest, most peak or successful point.", "syn": "pinnacle", "ant": "nadir", "ex": "His athletic career reached its zenith at the Olympics."},
        {"word": "novel", "pos": "Adjective", "phonetic": "/ˈnɒvəl/", "def": "Strikingly new, original, or unusual.", "syn": "innovative", "ant": "traditional", "ex": "She proposed a novel solution to urban congestion."},
        {"word": "placid", "pos": "Adjective", "phonetic": "/ˈplæsɪd/", "def": "Not easily upset or excited; calm and peaceful.", "syn": "composed", "ant": "agitated", "ex": "The horse possessed an unusually placid temperament."},
        {"word": "adept", "pos": "Adjective", "phonetic": "/əˈdɛpt/", "def": "Very skilled or proficient at a specialized task.", "syn": "expert", "ant": "clumsy", "ex": "He is adept at translating complex data into insights."}
    ],
    "medium": [
        {"word": "ubiquitous", "pos": "Adjective", "phonetic": "/juːˈbɪkwɪtəs/", "def": "Present, appearing, or found everywhere simultaneously.", "syn": "omnipresent", "ant": "rare", "ex": "Smartphones have become ubiquitous across modern society."},
        {"word": "ephemeral", "pos": "Adjective", "phonetic": "/ɪˈfɛmərəl/", "def": "Lasting for a very short, transient period of time.", "syn": "transient", "ant": "permanent", "ex": "The beauty of cherry blossoms is notoriously ephemeral."},
        {"word": "meticulous", "pos": "Adjective", "phonetic": "/mɪˈtɪkjʊləs/", "def": "Showing great attention to detail; exceptionally careful.", "syn": "scrupulous", "ant": "careless", "ex": "The architect prepared meticulous blueprints for the tower."},
        {"word": "superfluous", "pos": "Adjective", "phonetic": "/suːˈpɜːrfluəs/", "def": "Unnecessary, especially through being more than enough.", "syn": "redundant", "ant": "essential", "ex": "Clear writing eliminates superfluous words and filler."},
        {"word": "pragmatic", "pos": "Adjective", "phonetic": "/præɡˈmætɪk/", "def": "Dealing with things sensibly and realistically based on practice.", "syn": "practical", "ant": "idealistic", "ex": "They took a pragmatic approach to balancing the budget."},
        {"word": "fastidious", "pos": "Adjective", "phonetic": "/fæˈstɪdiəs/", "def": "Very attentive to accuracy and extreme neatness.", "syn": "demanding", "ant": "sloppy", "ex": "The chef was fastidious about the plating of each dish."},
        {"word": "gregarious", "pos": "Adjective", "phonetic": "/ɡrɪˈɡɛəriəs/", "def": "Fond of company; sociable and outgoing.", "syn": "sociable", "ant": "introverted", "ex": "Her gregarious personality made her popular at networking events."},
        {"word": "inevitable", "pos": "Adjective", "phonetic": "/ɪnˈɛvɪtəbəl/", "def": "Certain to happen; unavoidable.", "syn": "unavoidable", "ant": "preventable", "ex": "Change is an inevitable part of technological progress."},
        {"word": "ostentatious", "pos": "Adjective", "phonetic": "/ˌɒstɛnˈteɪʃəs/", "def": "Characterized by vulgar or pretentious show in order to impress.", "syn": "flamboyant", "ant": "understated", "ex": "The mansion was decorated in an ostentatious display of wealth."},
        {"word": "reticent", "pos": "Adjective", "phonetic": "/ˈrɛtɪsənt/", "def": "Not revealing one's thoughts or feelings readily; reserved.", "syn": "reserved", "ant": "loquacious", "ex": "He was reticent about his private life during interviews."},
        {"word": "scrutinize", "pos": "Verb", "phonetic": "/ˈskruːtɪnaɪz/", "def": "To examine or inspect closely and thoroughly.", "syn": "inspect", "ant": "glance", "ex": "Auditors scrutinized the company's financial ledgers."},
        {"word": "voracious", "pos": "Adjective", "phonetic": "/vəˈreɪʃəs/", "def": "Having a very eager, insatiable approach to an activity.", "syn": "insatiable", "ant": "apathetic", "ex": "She has been a voracious reader since early childhood."},
        {"word": "mitigate", "pos": "Verb", "phonetic": "/ˈmɪtɪɡeɪt/", "def": "To make less severe, serious, or painful.", "syn": "alleviate", "ant": "aggravate", "ex": "Measures were taken to mitigate environmental risks."},
        {"word": "tenacious", "pos": "Adjective", "phonetic": "/təˈneɪʃəs/", "def": "Tending to keep a firm hold of something; persistent.", "syn": "resolute", "ant": "yielding", "ex": "Her tenacious defense of human rights inspired thousands."},
        {"word": "complacent", "pos": "Adjective", "phonetic": "/kəmˈpleɪsənt/", "def": "Smug or uncritical satisfaction with oneself or achievements.", "syn": "self-satisfied", "ant": "vigilant", "ex": "Championship teams cannot afford to become complacent."}
    ],
    "hard": [
        {"word": "anachronistic", "pos": "Adjective", "phonetic": "/əˌnækrəˈnɪstɪk/", "def": "Belonging or appropriate to a period other than that in which it exists.", "syn": "outmoded", "ant": "contemporary", "ex": "Wearing Victorian garments today looks delightfully anachronistic."},
        {"word": "cacophony", "pos": "Noun", "phonetic": "/kəˈkɒfəni/", "def": "A harsh, discordant, jarring mixture of loud sounds.", "syn": "discord", "ant": "harmony", "ex": "A cacophony of car horns echoed through the busy intersection."},
        {"word": "grandiloquent", "pos": "Adjective", "phonetic": "/ɡrænˈdɪləkwənt/", "def": "Pompous or extravagant in language, style, or manner.", "syn": "bombastic", "ant": "unpretentious", "ex": "His grandiloquent speech failed to impress the practical crowd."},
        {"word": "inchoate", "pos": "Adjective", "phonetic": "/ɪnˈkoʊɪt/", "def": "Just begun and so not fully formed or developed; rudimentary.", "syn": "rudimentary", "ant": "developed", "ex": "His ideas for the novel were brilliant but still inchoate."},
        {"word": "juxtapose", "pos": "Verb", "phonetic": "/ˈdʒʌkstəpoʊz/", "def": "To place close together for contrasting effect.", "syn": "collocate", "ant": "isolate", "ex": "The exhibition juxtaposes contemporary art with ancient relics."},
        {"word": "loquacious", "pos": "Adjective", "phonetic": "/loʊˈkweɪʃəs/", "def": "Tending to talk a great deal; talkative.", "syn": "garrulous", "ant": "taciturn", "ex": "The loquacious host kept guests entertained throughout dinner."},
        {"word": "magnanimous", "pos": "Adjective", "phonetic": "/mæɡˈnænɪməs/", "def": "Very generous or forgiving, especially toward a rival or less powerful person.", "syn": "forgiving", "ant": "vindictive", "ex": "She was magnanimous in victory and praised her opponents."},
        {"word": "obsequious", "pos": "Adjective", "phonetic": "/əbˈsiːkwiəs/", "def": "Obedient or attentive to an excessive or servile degree.", "syn": "servile", "ant": "assertive", "ex": "The dictator was surrounded by obsequious courtiers."},
        {"word": "pernicious", "pos": "Adjective", "phonetic": "/pərˈnɪʃəs/", "def": "Having a harmful effect, especially in a gradual or subtle way.", "syn": "destructive", "ant": "beneficial", "ex": "Misinformation can exert a pernicious influence on public trust."},
        {"word": "recalcitrant", "pos": "Adjective", "phonetic": "/rɪˈkælsɪtrənt/", "def": "Having an obstinately uncooperative attitude toward authority.", "syn": "defiant", "ant": "compliant", "ex": "The recalcitrant witness refused to answer questions."},
        {"word": "sycophant", "pos": "Noun", "phonetic": "/ˈsɪkəfænt/", "def": "A person who acts obsequiously toward someone important to gain advantage.", "syn": "flatterer", "ant": "critic", "ex": "He despised sycophants who praised his every decree."},
        {"word": "taciturn", "pos": "Adjective", "phonetic": "/ˈtæsɪtɜːrn/", "def": "Reserved or uncommunicative in speech; saying little.", "syn": "uncommunicative", "ant": "talkative", "ex": "The taciturn detective observed everything without uttering a word."},
        {"word": "veracity", "pos": "Noun", "phonetic": "/vəˈræsɪti/", "def": "Conformity to facts; accuracy and habitual truthfulness.", "syn": "truthfulness", "ant": "falsehood", "ex": "Investigators verified the veracity of the witness testimony."},
        {"word": "alacrity", "pos": "Noun", "phonetic": "/əˈlækrɪti/", "def": "Brisk and cheerful readiness to act.", "syn": "eagerness", "ant": "reluctance", "ex": "She accepted the promotion with unmistakable alacrity."},
        {"word": "pellucid", "pos": "Adjective", "phonetic": "/pəˈluːsɪd/", "def": "Translucently clear; easily understood.", "syn": "transparent", "ant": "murky", "ex": "The river water was pellucid, revealing smooth pebbles beneath."}
    ]
}

def is_plausible_word(word):
    if len(word) < 2:
        return False
    if not re.search(r"[aeiouy]", word):
        return False
    if re.search(r"[^aeiouy]{5,}", word):
        return False
    mash_patterns = ["asdf", "hjkl", "qwer", "zxcv", "tyui", "uiop", "ghjk", "dfgh", "jkl;"]
    if any(p in word for p in mash_patterns):
        return False
    return True

def lookup_dictionary_word(word):
    """
    Authoritative dictionary lookup.
    Validates strictly against recognized English lexicons (Datamuse & Wiktionary).
    Only returns valid words present in standard English dictionaries.
    Returns found=False and spelling suggestions for non-existent or typo words.
    """
    if not word:
        return {"found": False, "word": "", "message": "Please enter a word to search."}
    
    # Strip any punctuation, symbols, whitespace commonly appended by speech recognition (e.g. "wait.", "hello,")
    clean_word = re.sub(r"^[^a-zA-Z]+|[^a-zA-Z]+$", "", word.strip()).strip().lower()
    if not clean_word or not re.match(r"^[a-zA-Z\- ]+$", clean_word) or not is_plausible_word(clean_word):
        suggestions = []
        try:
            sug_url = f"https://api.datamuse.com/sug?s={urllib.parse.quote(clean_word or word.strip())}"
            req = urllib.request.Request(sug_url, headers={"User-Agent": "DictionaryWordFinder/2.0"})
            with urllib.request.urlopen(req, timeout=4) as r:
                sugs = json.loads(r.read().decode("utf-8"))
                suggestions = [s["word"] for s in sugs[:5] if s.get("word") and s["word"].lower() != clean_word and is_plausible_word(s["word"].lower())]
        except Exception:
            pass

        return {
            "found": False,
            "word": clean_word,
            "message": f"'{clean_word}' is not a recognized English dictionary word. Please verify the spelling.",
            "suggestions": suggestions
        }

    # 1. First check our curated bank for instantaneous authoritative response if present
    for tier in VOCABULARY_BANK.values():
        for item in tier:
            if item["word"].lower() == clean_word:
                return {
                    "found": True,
                    "word": clean_word,
                    "pronunciation": item.get("phonetic", f"/{clean_word}/"),
                    "part_of_speech": item.get("pos", "Noun"),
                    "definitions": [item["def"]],
                    "synonyms": [item["syn"]],
                    "antonyms": [item["ant"]] if item.get("ant") else [],
                    "examples": [item["ex"]] if item.get("ex") else [],
                    "related_words": [item["syn"], "lexicon", "vocabulary"]
                }

    definitions = []
    part_of_speech = "Noun"
    pronunciation = ""
    examples = []
    synonyms = []
    antonyms = []
    related_words = []

    pos_map = {
        "n": "Noun", "v": "Verb", "adj": "Adjective", "adv": "Adverb", "u": "Interjection"
    }

    # 2. Query Free Dictionary API (Comprehensive definitions, synonyms, antonyms, examples, phonetics)
    try:
        f_url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{urllib.parse.quote(clean_word)}"
        req = urllib.request.Request(f_url, headers={"User-Agent": "DictionaryWordFinder/2.0 (Mozilla/5.0)"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            f_data = json.loads(resp.read().decode("utf-8"))
            if isinstance(f_data, list) and len(f_data) > 0:
                entry = f_data[0]
                if "phonetic" in entry and entry["phonetic"]:
                    pronunciation = entry["phonetic"]
                elif "phonetics" in entry:
                    for ph in entry["phonetics"]:
                        if ph.get("text"):
                            pronunciation = ph["text"]
                            break
                for m in entry.get("meanings", []):
                    pos_name = m.get("partOfSpeech", "")
                    if pos_name and (not part_of_speech or part_of_speech == "Noun"):
                        part_of_speech = pos_name.capitalize()
                    for def_obj in m.get("definitions", []):
                        d_text = def_obj.get("definition", "").strip()
                        if d_text and d_text not in definitions:
                            definitions.append(d_text)
                        ex_text = def_obj.get("example", "").strip()
                        if ex_text and ex_text not in examples:
                            examples.append(ex_text)
                        for syn in def_obj.get("synonyms", []):
                            if syn.lower() not in [s.lower() for s in synonyms] and syn.lower() != clean_word:
                                synonyms.append(syn)
                        for ant in def_obj.get("antonyms", []):
                            if ant.lower() not in [a.lower() for a in antonyms] and ant.lower() != clean_word:
                                antonyms.append(ant)
                    for syn in m.get("synonyms", []):
                        if syn.lower() not in [s.lower() for s in synonyms] and syn.lower() != clean_word:
                            synonyms.append(syn)
                    for ant in m.get("antonyms", []):
                        if ant.lower() not in [a.lower() for a in antonyms] and ant.lower() != clean_word:
                            antonyms.append(ant)
    except Exception:
        pass

    # 3. Query Datamuse Lexicon with IPA transcription & definitions
    try:
        url = f"https://api.datamuse.com/words?sp={urllib.parse.quote(clean_word)}&qe=sp&md=dpfr&ipa=1&max=1"
        req = urllib.request.Request(url, headers={"User-Agent": "DictionaryWordFinder/2.0 (Mozilla/5.0)"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            if data and data[0].get("word", "").lower() == clean_word:
                entry = data[0]
                tags = entry.get("tags", [])
                for t in tags:
                    if t.startswith("ipa_pron:") and not pronunciation:
                        pronunciation = "/" + t[9:].strip() + "/"
                    elif t in pos_map and not part_of_speech:
                        part_of_speech = pos_map[t]

                raw_defs = entry.get("defs", [])
                for rd in raw_defs:
                    if "\t" in rd:
                        p, d_text = rd.split("\t", 1)
                        if p in pos_map and not part_of_speech:
                            part_of_speech = pos_map[p]
                        d_clean = d_text.strip()
                        if d_clean and d_clean not in definitions:
                            definitions.append(d_clean)
                    else:
                        d_clean = rd.strip()
                        if d_clean and d_clean not in definitions:
                            definitions.append(d_clean)
    except Exception as e:
        pass

    # 3. Query Wiktionary for rich context, grammar & real examples
    try:
        url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{urllib.parse.quote(clean_word)}"
        req = urllib.request.Request(url, headers={"User-Agent": "DictionaryWordFinder/2.0 (Mozilla/5.0)"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            en_entries = data.get("en", [])
            for entry in en_entries:
                if not part_of_speech or part_of_speech == "Noun":
                    pos_cand = entry.get("partOfSpeech", "")
                    if pos_cand and pos_cand.lower() in ["noun", "verb", "adjective", "adverb", "preposition"]:
                        part_of_speech = pos_cand.capitalize()
                for d in entry.get("definitions", []):
                    raw_def = d.get("definition", "")
                    clean_def = re.sub(r"<.*?>", "", raw_def).strip()
                    if clean_def and not clean_def.startswith("(") and len(clean_def) > 4:
                        if clean_def not in definitions:
                            definitions.append(clean_def)
                    for ex in d.get("examples", []):
                        clean_ex = re.sub(r"<.*?>", "", ex).strip()
                        if clean_ex and len(clean_ex) > 6 and clean_ex not in examples:
                            examples.append(clean_ex)
    except Exception:
        pass

    # 4. Strict Dictionary Check: If NO valid definitions found, it is NOT a real dictionary word!
    if not definitions:
        suggestions = []
        try:
            sug_url = f"https://api.datamuse.com/sug?s={urllib.parse.quote(clean_word)}"
            req = urllib.request.Request(sug_url, headers={"User-Agent": "DictionaryWordFinder/2.0"})
            with urllib.request.urlopen(req, timeout=4) as r:
                sugs = json.loads(r.read().decode("utf-8"))
                suggestions = [s["word"] for s in sugs[:5] if s.get("word") and s["word"].lower() != clean_word]
        except Exception:
            pass

        return {
            "found": False,
            "word": clean_word,
            "message": f"'{clean_word}' was not found in standard English dictionaries. Please verify the spelling.",
            "suggestions": suggestions
        }

    # 5. Retrieve real synonyms, antonyms, and related words
    try:
        syn_url = f"https://api.datamuse.com/words?rel_syn={urllib.parse.quote(clean_word)}&max=8"
        req = urllib.request.Request(syn_url, headers={"User-Agent": "DictionaryWordFinder/2.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            syn_data = json.loads(resp.read().decode("utf-8"))
            synonyms = [w["word"] for w in syn_data if "word" in w]

        ant_url = f"https://api.datamuse.com/words?rel_ant={urllib.parse.quote(clean_word)}&max=6"
        req = urllib.request.Request(ant_url, headers={"User-Agent": "DictionaryWordFinder/2.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            ant_data = json.loads(resp.read().decode("utf-8"))
            antonyms = [w["word"] for w in ant_data if "word" in w]

        rel_url = f"https://api.datamuse.com/words?ml={urllib.parse.quote(clean_word)}&max=8"
        req = urllib.request.Request(rel_url, headers={"User-Agent": "DictionaryWordFinder/2.0"})
        with urllib.request.urlopen(req, timeout=4) as resp:
            rel_data = json.loads(resp.read().decode("utf-8"))
            related_words = [w["word"] for w in rel_data if "word" in w and w["word"] not in synonyms][:6]
    except Exception:
        pass

    if not pronunciation:
        pronunciation = f"/{clean_word}/"

    return {
        "found": True,
        "word": clean_word,
        "pronunciation": pronunciation,
        "part_of_speech": part_of_speech,
        "definitions": definitions[:6],
        "synonyms": synonyms,
        "antonyms": antonyms,
        "examples": examples[:4],
        "related_words": related_words
    }

def generate_quiz_questions(user_id=1, category="all", difficulty="easy", count=5):
    """
    Generates rich, authentic multiple-choice quiz questions with 4 distinct options,
    randomized answers, explanations, and native dictionary definitions.
    Supports categories: 'all', 'definition', 'reverse_definition', 'synonym', 'antonym', and 'saved'.
    """
    count = max(3, min(int(count), 15))
    difficulty = difficulty.lower() if difficulty in ["easy", "medium", "hard"] else "easy"
    
    # Pool selection
    pool = list(VOCABULARY_BANK.get(difficulty, VOCABULARY_BANK["easy"]))
    
    # If category is 'saved', pull from user's saved words and supplement
    is_saved_mode = (category == "saved")
    if is_saved_mode:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT word FROM saved_words WHERE user_id=? ORDER BY id DESC LIMIT 20", (user_id,))
        saved_rows = cur.fetchall()
        conn.close()
        saved_words = [r[0].lower() for r in saved_rows]
        
        saved_items = []
        for sw in saved_words:
            # find in bank or lookup
            found_in_bank = False
            for tier in VOCABULARY_BANK.values():
                for item in tier:
                    if item["word"].lower() == sw:
                        saved_items.append(item)
                        found_in_bank = True
                        break
                if found_in_bank:
                    break
            if not found_in_bank:
                # generate basic entry
                info = lookup_dictionary_word(sw)
                if info.get("found") and info.get("definitions"):
                    saved_items.append({
                        "word": sw,
                        "pos": info.get("part_of_speech", "Noun"),
                        "phonetic": info.get("pronunciation", f"/{sw}/"),
                        "def": info["definitions"][0],
                        "syn": info["synonyms"][0] if info.get("synonyms") else "expression",
                        "ant": info["antonyms"][0] if info.get("antonyms") else "",
                        "ex": info["examples"][0] if info.get("examples") else f"The word '{sw}' is well defined."
                    })
        if saved_items:
            pool = saved_items + pool
    
    if len(pool) < 4:
        pool = VOCABULARY_BANK["easy"]

    random.shuffle(pool)
    selected_targets = pool[:count]
    questions = []

    for i, target in enumerate(selected_targets):
        word = target["word"]
        pos = target["pos"]
        phonetic = target.get("phonetic", f"/{word}/")
        definition = target["def"]
        synonym = target.get("syn", "")
        antonym = target.get("ant", "")
        example = target.get("ex", "")

        # Determine question type
        q_type = category
        if category in ["all", "saved"]:
            valid_types = ["definition", "reverse_definition"]
            if synonym:
                valid_types.append("synonym")
            if antonym:
                valid_types.append("antonym")
            q_type = random.choice(valid_types)

        # Distractor pool
        distractors = [w for w in pool if w["word"] != word]
        random.shuffle(distractors)
        wrong = distractors[:3]

        if q_type == "definition":
            q_prompt = f"What is the primary definition of the word \"{word.capitalize()}\"?"
            options = [definition] + [w["def"] for w in wrong]
            random.shuffle(options)
            correct_idx = options.index(definition)
            explanation = f"\"{word.capitalize()}\" ({pos}) means: {definition}"

        elif q_type == "reverse_definition":
            q_prompt = f"Which word matches this definition: \"{definition}\"?"
            options = [word.capitalize()] + [w["word"].capitalize() for w in wrong]
            random.shuffle(options)
            correct_idx = options.index(word.capitalize())
            explanation = f"\"{word.capitalize()}\" is the correct term. {example}"

        elif q_type == "synonym":
            if not synonym:
                synonym = target.get("syn", "synonym")
            q_prompt = f"Which word is the closest SYNONYM for \"{word.capitalize()}\"?"
            # Generate options with wrong words
            options = [synonym.capitalize()] + [w["word"].capitalize() for w in wrong]
            random.shuffle(options)
            correct_idx = options.index(synonym.capitalize())
            explanation = f"\"{synonym.capitalize()}\" is a direct synonym for \"{word.capitalize()}\". Definition: {definition}"

        elif q_type == "antonym":
            if not antonym:
                antonym = target.get("ant", "antonym")
            q_prompt = f"Which word is the direct ANTONYM (opposite) of \"{word.capitalize()}\"?"
            options = [antonym.capitalize()] + [w["word"].capitalize() for w in wrong]
            random.shuffle(options)
            correct_idx = options.index(antonym.capitalize())
            explanation = f"\"{antonym.capitalize()}\" expresses the opposite of \"{word.capitalize()}\" ({pos}: {definition})."

        else:
            q_prompt = f"What is the definition of \"{word.capitalize()}\"?"
            options = [definition] + [w["def"] for w in wrong]
            random.shuffle(options)
            correct_idx = options.index(definition)
            explanation = f"\"{word.capitalize()}\" means {definition}"

        questions.append({
            "id": i + 1,
            "type": q_type,
            "question": q_prompt,
            "word": word,
            "part_of_speech": pos,
            "phonetic": phonetic,
            "options": options,
            "correct_index": correct_idx,
            "explanation": explanation,
            "example": example
        })

    return questions

def get_word_of_the_day():
    day_num = datetime.now().timetuple().tm_yday
    combined = VOCABULARY_BANK["easy"] + VOCABULARY_BANK["medium"] + VOCABULARY_BANK["hard"]
    item = combined[day_num % len(combined)]
    return item



HTML_PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Dictionary Word Finder & Vocabulary Studio</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Space+Grotesk:wght@600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #f8fafc;
      --surface: #ffffff;
      --sidebar-bg: #f1f5f9;
      --text: #0f172a;
      --text-muted: #64748b;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-gradient: linear-gradient(135deg, #2563eb, #4f46e5);
      --border: #e2e8f0;
      --card-border: #e2e8f0;
      --accent: #dbeafe;
      --success: #10b981;
      --danger: #ef4444;
      --warning: #f59e0b;
      --card-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.05);
    }
    body.dark {
      --bg: #0b0f19;
      --surface: #131c2e;
      --sidebar-bg: #090d16;
      --text: #f8fafc;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #60a5fa;
      --primary-gradient: linear-gradient(135deg, #3b82f6, #6366f1);
      --border: #1e293b;
      --card-border: #1e293b;
      --accent: #1e3a8a;
      --card-shadow: 0 4px 25px -2px rgba(0, 0, 0, 0.35);
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
      font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
      background: var(--bg);
      color: var(--text);
      display: flex;
      height: 100vh;
      overflow: hidden;
      transition: background 0.2s, color 0.2s;
    }

    /* Auth Screen Modal */
    #auth-screen {
      position: fixed;
      inset: 0;
      background: radial-gradient(circle at 20% 20%, #3b82f61a 0%, transparent 40%),
                  radial-gradient(circle at 80% 80%, #6366f11a 0%, transparent 45%),
                  radial-gradient(circle at 50% 50%, #0b0f19 0%, #030712 100%);
      z-index: 1000;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: hidden;
    }
    .auth-bg-blob {
      position: absolute;
      width: 500px;
      height: 500px;
      border-radius: 50%;
      filter: blur(80px);
      opacity: 0.35;
      animation: floatBlobs 12s infinite alternate ease-in-out;
      pointer-events: none;
    }
    .blob-1 { background: #2563eb; top: -100px; left: -100px; }
    .blob-2 { background: #7c3aed; bottom: -120px; right: -100px; animation-duration: 15s; }
    .blob-3 { background: #06b6d4; top: 40%; left: 60%; width: 350px; height: 350px; animation-duration: 10s; }
    @keyframes floatBlobs {
      0% { transform: translate(0, 0) scale(1); }
      50% { transform: translate(40px, 30px) scale(1.1); }
      100% { transform: translate(-30px, -20px) scale(0.95); }
    }
    .auth-card {
      position: relative;
      background: rgba(255, 255, 255, 0.04);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 28px;
      padding: 44px 40px;
      width: 440px;
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.15);
      animation: cardEnter 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
      color: #ffffff;
    }
    @keyframes cardEnter {
      from { opacity: 0; transform: translateY(24px) scale(0.96); }
      to { opacity: 1; transform: translateY(0) scale(1); }
    }
    .auth-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 6px 14px;
      border-radius: 30px;
      background: rgba(59, 130, 246, 0.15);
      border: 1px solid rgba(59, 130, 246, 0.3);
      color: #93c5fd;
      font-size: 12px;
      font-weight: 700;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 14px;
    }
    .auth-title {
      font-size: 28px;
      font-weight: 800;
      letter-spacing: -0.6px;
      margin-bottom: 6px;
      background: linear-gradient(135deg, #ffffff 30%, #93c5fd 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }
    .auth-subtitle { color: #94a3b8; font-size: 14px; margin-bottom: 26px; }
    .form-group { margin-bottom: 18px; }
    .form-group label { display: block; font-size: 13px; font-weight: 600; color: #cbd5e1; margin-bottom: 7px; }
    .form-control {
      width: 100%;
      padding: 14px 18px;
      border-radius: 14px;
      border: 1px solid rgba(255, 255, 255, 0.14);
      background: rgba(255, 255, 255, 0.05);
      color: #ffffff;
      font-size: 15px;
      font-family: inherit;
      outline: none;
      transition: all 0.2s;
    }
    .form-control::placeholder { color: #64748b; }
    .form-control:focus {
      border-color: #3b82f6;
      background: rgba(255, 255, 255, 0.09);
      box-shadow: 0 0 0 4px rgba(59, 130, 246, 0.25);
    }
    .btn {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 14px 22px;
      border-radius: 14px;
      border: none;
      background: var(--primary-gradient);
      color: white;
      font-weight: 700;
      font-size: 15px;
      cursor: pointer;
      box-shadow: 0 10px 24px -5px rgba(37, 99, 235, 0.45);
      transition: all 0.2s cubic-bezier(0.16, 1, 0.3, 1);
      font-family: inherit;
      text-decoration: none;
    }
    .btn:hover {
      box-shadow: 0 14px 30px -5px rgba(37, 99, 235, 0.6);
      transform: translateY(-2px);
      filter: brightness(1.08);
    }
    .btn:active { transform: scale(0.98); }
    .auth-footer { margin-top: 22px; text-align: center; font-size: 14px; color: #94a3b8; }
    .auth-footer a { color: #60a5fa; font-weight: 600; text-decoration: none; cursor: pointer; }
    .auth-footer a:hover { color: #93c5fd; text-decoration: underline; }
    .error-msg { color: #f87171; font-size: 13px; margin-top: 10px; min-height: 18px; font-weight: 500; }

    /* Layout */
    .sidebar {
      width: 270px;
      background: var(--sidebar-bg);
      border-right: 1px solid var(--border);
      padding: 24px 16px;
      display: flex;
      flex-direction: column;
      gap: 20px;
      flex-shrink: 0;
    }
    .brand {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 0 8px;
    }
    .brand-icon {
      width: 42px;
      height: 42px;
      background: var(--primary-gradient);
      color: white;
      border-radius: 12px;
      display: grid;
      place-items: center;
      font-weight: 800;
      font-size: 20px;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
    }
    .brand-text { font-size: 18px; font-weight: 800; letter-spacing: -0.4px; }
    .user-pill {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 10px 14px;
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 14px;
      font-weight: 600;
      box-shadow: var(--card-shadow);
    }
    .nav-list { list-style: none; display: flex; flex-direction: column; gap: 4px; }
    .nav-item {
      padding: 12px 14px;
      border-radius: 12px;
      font-size: 14px;
      font-weight: 600;
      color: var(--text-muted);
      cursor: pointer;
      display: flex;
      align-items: center;
      gap: 12px;
      transition: all 0.15s;
    }
    .nav-item:hover { background: rgba(37,99,235,0.08); color: var(--primary); }
    .nav-item.active { background: var(--accent); color: var(--primary); font-weight: 700; }
    .main-content {
      flex: 1;
      overflow-y: auto;
      padding: 36px 48px;
      position: relative;
    }
    .view { display: none; }
    .view.active { display: block; animation: fadeIn 0.2s ease; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

    /* Common Typography & Search */
    .hero-title { font-size: 32px; font-weight: 800; letter-spacing: -0.6px; margin-bottom: 6px; }
    .hero-sub { color: var(--text-muted); font-size: 15px; margin-bottom: 28px; }
    .search-bar-wrap {
      display: flex;
      gap: 12px;
      margin-bottom: 28px;
      max-width: 820px;
    }
    .search-input {
      flex: 1;
      padding: 16px 20px;
      font-size: 16px;
      border-radius: 14px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      outline: none;
      font-family: inherit;
      transition: all 0.2s;
      box-shadow: var(--card-shadow);
    }
    .search-input:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(37,99,235,0.18); }
    .search-btn {
      width: auto;
      padding: 0 32px;
      font-size: 16px;
      border-radius: 14px;
    }

    /* Cards & Stats */
    .stats-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
      gap: 16px;
      margin-top: 24px;
      max-width: 860px;
    }
    .stat-card {
      background: var(--surface);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 22px;
      box-shadow: var(--card-shadow);
      transition: transform 0.2s;
    }
    .stat-card:hover { transform: translateY(-2px); }
    .stat-label { font-size: 12px; color: var(--text-muted); font-weight: 700; text-transform: uppercase; letter-spacing: 0.6px; }
    .stat-val { font-size: 32px; font-weight: 800; margin-top: 6px; color: var(--primary); }

    /* Word of the Day Hero Banner */
    .wotd-banner {
      background: linear-gradient(135deg, rgba(37, 99, 235, 0.08) 0%, rgba(99, 102, 241, 0.12) 100%);
      border: 1px solid rgba(59, 130, 246, 0.25);
      border-radius: 20px;
      padding: 26px 30px;
      margin-bottom: 30px;
      max-width: 860px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      gap: 20px;
    }
    .wotd-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      padding: 4px 12px;
      border-radius: 20px;
      background: var(--primary);
      color: white;
      font-size: 11px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      margin-bottom: 8px;
    }
    .wotd-word { font-size: 28px; font-weight: 800; text-transform: capitalize; }
    .wotd-def { color: var(--text-muted); font-size: 14px; margin-top: 6px; line-height: 1.5; }

    /* Word Result Card */
    .result-card {
      background: var(--surface);
      border: 1px solid var(--card-border);
      border-radius: 22px;
      padding: 32px;
      max-width: 860px;
      margin-top: 24px;
      box-shadow: var(--card-shadow);
      animation: cardEnter 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }
    .word-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      border-bottom: 1px solid var(--border);
      padding-bottom: 20px;
      margin-bottom: 22px;
      flex-wrap: wrap;
      gap: 16px;
    }
    .word-title { font-size: 38px; font-weight: 800; text-transform: capitalize; letter-spacing: -0.6px; }
    .word-phonetic-row { display: flex; align-items: center; gap: 12px; margin-top: 4px; }
    .word-phonetic { font-size: 17px; color: var(--primary); font-weight: 600; font-family: 'Space Grotesk', monospace; }
    .btn-audio {
      background: var(--accent);
      color: var(--primary);
      border: none;
      padding: 6px 12px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 700;
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.15s;
    }
    .btn-audio:hover { transform: scale(1.05); filter: brightness(1.1); }
    .tag {
      background: var(--accent);
      color: var(--primary);
      padding: 6px 14px;
      border-radius: 20px;
      font-size: 12px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.6px;
    }
    .btn-bookmark {
      background: transparent;
      border: 1px solid var(--border);
      padding: 10px 18px;
      border-radius: 12px;
      font-weight: 700;
      cursor: pointer;
      color: var(--text);
      display: flex;
      align-items: center;
      gap: 8px;
      font-family: inherit;
      transition: all 0.15s;
    }
    .btn-bookmark:hover { background: var(--bg); border-color: var(--primary); color: var(--primary); }
    .btn-bookmark.saved { background: #fef3c7; color: #b45309; border-color: #fde68a; font-weight: 800; }
    body.dark .btn-bookmark.saved { background: #78350f; color: #fef08a; border-color: #b45309; }

    .section-title {
      font-size: 13px;
      font-weight: 800;
      text-transform: uppercase;
      letter-spacing: 0.8px;
      color: var(--text-muted);
      margin: 22px 0 12px 0;
    }
    .def-item {
      padding: 12px 16px;
      background: var(--bg);
      border-radius: 12px;
      margin-bottom: 10px;
      line-height: 1.55;
      font-size: 15px;
      border-left: 3px solid var(--primary);
    }
    .pill-list { display: flex; flex-wrap: wrap; gap: 8px; }
    .pill {
      background: var(--bg);
      border: 1px solid var(--border);
      padding: 7px 16px;
      border-radius: 20px;
      font-size: 13px;
      font-weight: 600;
      cursor: pointer;
      transition: 0.15s;
    }
    .pill:hover { border-color: var(--primary); color: var(--primary); background: var(--accent); }

    /* Word Not Found / Error Banner */
    .not-found-card {
      background: var(--surface);
      border: 1px solid #fed7aa;
      border-radius: 20px;
      padding: 28px 32px;
      max-width: 860px;
      margin-top: 24px;
      box-shadow: var(--card-shadow);
      border-left: 5px solid #f97316;
    }
    body.dark .not-found-card { border-color: #7c2d12; border-left-color: #ea580c; }
    .not-found-title { font-size: 20px; font-weight: 800; color: #ea580c; display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
    .not-found-desc { color: var(--text-muted); font-size: 15px; line-height: 1.5; margin-bottom: 18px; }

    /* QUIZ SECTION STYLES */
    .quiz-container { max-width: 860px; }
    .quiz-lobby-card {
      background: var(--surface);
      border: 1px solid var(--card-border);
      border-radius: 24px;
      padding: 36px;
      box-shadow: var(--card-shadow);
    }
    .quiz-category-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 18px 0 28px 0;
    }
    .quiz-cat-item {
      background: var(--bg);
      border: 2px solid var(--border);
      border-radius: 16px;
      padding: 16px;
      cursor: pointer;
      transition: all 0.2s;
      text-align: center;
    }
    .quiz-cat-item:hover { border-color: var(--primary); transform: translateY(-2px); }
    .quiz-cat-item.active { border-color: var(--primary); background: var(--accent); color: var(--primary); font-weight: 700; }
    .quiz-cat-icon { font-size: 26px; margin-bottom: 6px; }
    .quiz-cat-title { font-size: 14px; font-weight: 700; }

    .quiz-difficulty-wrap {
      display: flex;
      gap: 10px;
      margin: 12px 0 28px 0;
    }
    .quiz-diff-btn {
      flex: 1;
      padding: 12px 14px;
      border-radius: 12px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      font-weight: 700;
      cursor: pointer;
      font-family: inherit;
      transition: 0.15s;
      text-align: center;
    }
    .quiz-diff-btn.active {
      border-color: var(--primary);
      background: var(--primary);
      color: white;
      box-shadow: 0 4px 14px rgba(37, 99, 235, 0.3);
    }

    /* Active Quiz Screen */
    .quiz-play-card {
      background: var(--surface);
      border: 1px solid var(--card-border);
      border-radius: 24px;
      padding: 36px;
      box-shadow: var(--card-shadow);
      display: none;
    }
    .quiz-hud {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
      font-size: 14px;
      font-weight: 700;
    }
    .quiz-progress-bar-wrap {
      width: 100%;
      height: 8px;
      background: var(--bg);
      border-radius: 8px;
      overflow: hidden;
      margin-bottom: 28px;
    }
    .quiz-progress-bar-fill {
      height: 100%;
      width: 0%;
      background: var(--primary-gradient);
      transition: width 0.3s ease;
    }
    .quiz-question-box {
      margin-bottom: 28px;
    }
    .quiz-q-prompt {
      font-size: 22px;
      font-weight: 800;
      line-height: 1.4;
      margin-bottom: 14px;
    }
    .quiz-q-target {
      display: inline-flex;
      align-items: center;
      gap: 10px;
      padding: 6px 16px;
      background: var(--accent);
      color: var(--primary);
      border-radius: 20px;
      font-size: 16px;
      font-weight: 800;
      margin-bottom: 16px;
    }
    .quiz-options-list {
      display: flex;
      flex-direction: column;
      gap: 12px;
    }
    .quiz-opt-btn {
      padding: 16px 20px;
      border-radius: 14px;
      border: 2px solid var(--border);
      background: var(--surface);
      color: var(--text);
      font-size: 15px;
      font-weight: 600;
      cursor: pointer;
      text-align: left;
      font-family: inherit;
      display: flex;
      align-items: center;
      gap: 14px;
      transition: all 0.15s;
    }
    .quiz-opt-btn:hover:not(:disabled) {
      border-color: var(--primary);
      background: var(--bg);
      transform: translateX(4px);
    }
    .quiz-opt-btn .opt-badge {
      width: 28px;
      height: 28px;
      border-radius: 8px;
      background: var(--bg);
      border: 1px solid var(--border);
      display: grid;
      place-items: center;
      font-size: 13px;
      font-weight: 800;
      flex-shrink: 0;
    }
    .quiz-opt-btn.correct {
      border-color: #10b981 !important;
      background: rgba(16, 185, 129, 0.12) !important;
      color: #059669 !important;
    }
    .quiz-opt-btn.correct .opt-badge { background: #10b981; color: white; border-color: #10b981; }
    .quiz-opt-btn.wrong {
      border-color: #ef4444 !important;
      background: rgba(239, 68, 68, 0.12) !important;
      color: #dc2626 !important;
    }
    .quiz-opt-btn.wrong .opt-badge { background: #ef4444; color: white; border-color: #ef4444; }

    .quiz-explanation-card {
      margin-top: 20px;
      padding: 18px 22px;
      background: var(--bg);
      border-radius: 14px;
      border-left: 4px solid var(--primary);
      display: none;
      animation: fadeIn 0.2s ease;
    }
    .quiz-explanation-text { font-size: 14px; line-height: 1.5; color: var(--text); margin-bottom: 10px; }

    /* Quiz Results Screen */
    .quiz-result-card {
      background: var(--surface);
      border: 1px solid var(--card-border);
      border-radius: 24px;
      padding: 40px;
      text-align: center;
      box-shadow: var(--card-shadow);
      display: none;
      animation: cardEnter 0.4s ease;
    }
    .result-score-circle {
      width: 130px;
      height: 130px;
      border-radius: 50%;
      background: var(--primary-gradient);
      color: white;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      margin: 0 auto 20px auto;
      box-shadow: 0 10px 25px -4px rgba(37, 99, 235, 0.5);
    }
    .result-score-val { font-size: 38px; font-weight: 800; line-height: 1; }
    .result-score-label { font-size: 13px; font-weight: 700; opacity: 0.9; margin-top: 4px; }
    .result-badge {
      display: inline-block;
      padding: 6px 18px;
      border-radius: 20px;
      background: var(--accent);
      color: var(--primary);
      font-weight: 800;
      font-size: 14px;
      margin-bottom: 12px;
    }
    .result-breakdown-grid {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 16px;
      margin: 28px 0;
      text-align: center;
    }

    /* Word Lists */
    .word-list { list-style: none; display: flex; flex-direction: column; gap: 10px; max-width: 860px; }
    .word-list-item {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px 20px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      font-weight: 600;
      cursor: pointer;
      transition: 0.15s;
    }
    .word-list-item:hover { transform: translateX(4px); border-color: var(--primary); }
    .danger-btn {
      background: #fee2e2;
      color: #b91c1c;
      border: none;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 12px;
      cursor: pointer;
    }
    .danger-btn:hover { background: #fecaca; }

    /* Tables */
    .history-table {
      width: 100%;
      border-collapse: collapse;
      margin-top: 14px;
    }
    .history-table th {
      text-align: left;
      padding: 12px;
      font-size: 12px;
      text-transform: uppercase;
      letter-spacing: 0.6px;
      color: var(--text-muted);
      border-bottom: 1px solid var(--border);
    }
    .history-table td {
      padding: 14px 12px;
      font-size: 14px;
      font-weight: 600;
      border-bottom: 1px solid var(--border);
    }
  </style>
</head>
<body>
  <!-- Auth Screen Modal -->
  <div id="auth-screen">
    <div class="auth-bg-blob blob-1"></div>
    <div class="auth-bg-blob blob-2"></div>
    <div class="auth-bg-blob blob-3"></div>

    <div class="auth-card" id="login-box">
      <div class="auth-badge">✨ Dictionary Studio</div>
      <h2 class="auth-title">Welcome Back</h2>
      <p class="auth-subtitle">Sign in to your Dictionary Word Finder account</p>
      <div class="form-group">
        <label>Email Address</label>
        <input type="email" id="login-email" class="form-control" placeholder="user@example.com" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" id="login-password" class="form-control" placeholder="••••••••" />
      </div>
      <div class="error-msg" id="login-error"></div>
      <button class="btn" style="width:100%; margin-top: 10px;" onclick="handleLogin()">Sign In</button>
      <div class="auth-footer">
        Don't have an account? <a onclick="showRegister()">Create account</a>
      </div>
    </div>

    <div class="auth-card" id="register-box" style="display:none;">
      <div class="auth-badge">🚀 Get Started</div>
      <h2 class="auth-title">Create Account</h2>
      <p class="auth-subtitle">Start searching with verified dictionary & interactive quizzes</p>
      <div class="form-group">
        <label>Username</label>
        <input type="text" id="reg-username" class="form-control" placeholder="johndoe" />
      </div>
      <div class="form-group">
        <label>Email Address</label>
        <input type="email" id="reg-email" class="form-control" placeholder="user@example.com" />
      </div>
      <div class="form-group">
        <label>Password</label>
        <input type="password" id="reg-password" class="form-control" placeholder="••••••••" />
      </div>
      <div class="error-msg" id="reg-error"></div>
      <button class="btn" style="width:100%; margin-top: 10px;" onclick="handleRegister()">Create Account</button>
      <div class="auth-footer">
        Already have an account? <a onclick="showLogin()">Sign in</a>
      </div>
    </div>
  </div>

  <!-- Sidebar -->
  <aside class="sidebar">
    <div class="brand">
      <div class="brand-icon">D</div>
      <div class="brand-text">Word Finder</div>
    </div>
    <div class="user-pill">
      <span>👤</span>
      <span id="current-user-display">Guest</span>
    </div>
    <ul class="nav-list">
      <li class="nav-item active" onclick="switchTab('dashboard')"><span>📊</span> Dashboard</li>
      <li class="nav-item" onclick="switchTab('search')"><span>🔍</span> Word Search</li>
      <li class="nav-item" onclick="switchTab('quiz')"><span>🧠</span> Vocabulary Quiz</li>
      <li class="nav-item" onclick="switchTab('saved')"><span>⭐</span> Saved Words</li>
      <li class="nav-item" onclick="switchTab('history')"><span>🕒</span> Search History</li>
      <li class="nav-item" onclick="switchTab('profile')"><span>👤</span> Profile</li>
      <li class="nav-item" onclick="switchTab('settings')"><span>⚙️</span> Settings</li>
      <li class="nav-item" style="margin-top:auto; color: #ef4444;" onclick="logout()"><span>🚪</span> Logout</li>
    </ul>
  </aside>

  <!-- Main Content -->
  <main class="main-content">
    <!-- DASHBOARD VIEW -->
    <div id="view-dashboard" class="view active">
      <h1 class="hero-title" id="dash-greeting">Good day 👋</h1>
      <p class="hero-sub">Explore authentic definitions, expand your vocabulary, and test yourself.</p>

      <!-- Word of the Day Banner -->
      <div class="wotd-banner" id="wotd-box">
        <div>
          <div class="wotd-badge">🌟 Word of the Day</div>
          <div style="display:flex; align-items:center; gap: 12px;">
            <div class="wotd-word" id="wotd-word">Serendipity</div>
            <span class="tag" id="wotd-pos">Noun</span>
            <button class="btn-audio" onclick="playPronunciation(document.getElementById('wotd-word').innerText)">🔊 Pronounce</button>
          </div>
          <div class="wotd-def" id="wotd-def">Finding valuable or agreeable things not sought for; happy chance.</div>
        </div>
        <div>
          <button class="btn" onclick="quickSearchWotd()">View Full Meaning →</button>
        </div>
      </div>

      <!-- Quick Search -->
      <div class="search-bar-wrap">
        <input type="text" id="dash-search-input" class="search-input" placeholder="Search any verified word (e.g. candid, eloquent, serendipity)..." onkeydown="if(event.key==='Enter') quickSearch('dash-search-input')" />
        <button class="btn search-btn" onclick="quickSearch('dash-search-input')">Search</button>
      </div>

      <!-- Stats Grid -->
      <div class="stats-grid">
        <div class="stat-card">
          <div class="stat-label">Total Searches</div>
          <div class="stat-val" id="stat-total-searches">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Saved Words</div>
          <div class="stat-val" id="stat-saved-words">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Quizzes Completed</div>
          <div class="stat-val" id="stat-quiz-completed">0</div>
        </div>
        <div class="stat-card">
          <div class="stat-label">Best Quiz Score</div>
          <div class="stat-val" id="stat-quiz-best">0%</div>
        </div>
      </div>

      <div style="margin-top: 32px; max-width: 860px;">
        <div class="stat-card" style="display:flex; justify-content:space-between; align-items:center;">
          <div>
            <h3 style="font-size:18px; font-weight:800; margin-bottom:4px;">Ready to test your vocabulary?</h3>
            <p style="color:var(--text-muted); font-size:14px;">Take an adaptive 5-question quiz on definitions, synonyms, or your own saved words.</p>
          </div>
          <button class="btn" onclick="switchTab('quiz')">Start a Quiz 🎯</button>
        </div>
      </div>
    </div>

    <!-- SEARCH VIEW -->
    <div id="view-search" class="view">
      <h1 class="hero-title">Search Dictionary</h1>
      <p class="hero-sub">Only authentic, verified English words with official meanings, phonetics, audio, and examples.</p>
      
      <div class="search-bar-wrap">
        <input type="text" id="main-search-input" class="search-input" placeholder="Enter word to search..." onkeydown="if(event.key==='Enter') executeSearch()" />
        <button class="btn search-btn" id="search-action-btn" onclick="executeSearch()">Search</button>
      </div>

      <div id="search-status" style="color: var(--text-muted); margin-bottom: 16px; font-weight: 600;"></div>
      <div id="search-result-container"></div>
    </div>

    <!-- QUIZ VIEW -->
    <div id="view-quiz" class="view">
      <div class="quiz-container">
        <!-- Quiz Lobby -->
        <div class="quiz-lobby-card" id="quiz-lobby">
          <h1 class="hero-title">Vocabulary Master Quiz</h1>
          <p class="hero-sub">Select your quiz preferences to test your knowledge against authentic dictionary terms.</p>

          <div class="section-title">1. Choose Category</div>
          <div class="quiz-category-grid">
            <div class="quiz-cat-item active" data-cat="all" onclick="selectQuizCategory('all', this)">
              <div class="quiz-cat-icon">🎯</div>
              <div class="quiz-cat-title">All-Round Mixed</div>
            </div>
            <div class="quiz-cat-item" data-cat="definition" onclick="selectQuizCategory('definition', this)">
              <div class="quiz-cat-icon">📖</div>
              <div class="quiz-cat-title">Definitions</div>
            </div>
            <div class="quiz-cat-item" data-cat="synonym" onclick="selectQuizCategory('synonym', this)">
              <div class="quiz-cat-icon">🔄</div>
              <div class="quiz-cat-title">Synonyms</div>
            </div>
            <div class="quiz-cat-item" data-cat="antonym" onclick="selectQuizCategory('antonym', this)">
              <div class="quiz-cat-icon">⚡</div>
              <div class="quiz-cat-title">Antonyms</div>
            </div>
            <div class="quiz-cat-item" data-cat="saved" onclick="selectQuizCategory('saved', this)">
              <div class="quiz-cat-icon">⭐</div>
              <div class="quiz-cat-title">My Saved Words</div>
            </div>
          </div>

          <div class="section-title">2. Choose Difficulty</div>
          <div class="quiz-difficulty-wrap">
            <button class="quiz-diff-btn active" data-diff="easy" onclick="selectQuizDifficulty('easy', this)">🟢 Beginner</button>
            <button class="quiz-diff-btn" data-diff="medium" onclick="selectQuizDifficulty('medium', this)">🟡 Intermediate</button>
            <button class="quiz-diff-btn" data-diff="hard" onclick="selectQuizDifficulty('hard', this)">🔴 Advanced / GRE</button>
          </div>

          <div class="section-title">3. Question Count</div>
          <div style="display:flex; gap:12px; margin-bottom: 28px;">
            <button class="quiz-diff-btn active" id="btn-count-5" onclick="selectQuizCount(5)">5 Questions</button>
            <button class="quiz-diff-btn" id="btn-count-10" onclick="selectQuizCount(10)">10 Questions</button>
          </div>

          <button class="btn" style="width: 100%; padding: 18px; font-size: 17px;" onclick="startQuizSession()">🚀 Launch Vocabulary Quiz</button>

          <!-- Past Quiz History Table in Lobby -->
          <div style="margin-top: 40px; padding-top: 24px; border-top: 1px solid var(--border);">
            <h3 style="font-size: 18px; font-weight: 800; margin-bottom: 12px;">Your Recent Quiz Records</h3>
            <div id="quiz-history-table-container">
              <p style="color:var(--text-muted); font-size:14px;">No quizzes completed yet. Take your first quiz today!</p>
            </div>
          </div>
        </div>

        <!-- Active Quiz Play Card -->
        <div class="quiz-play-card" id="quiz-player">
          <div class="quiz-hud">
            <div>
              <span id="quiz-hud-counter" style="color:var(--primary);">Question 1 of 5</span>
              <span id="quiz-hud-streak" style="margin-left: 14px; color:#f59e0b;">🔥 Streak: 0</span>
            </div>
            <div>
              <span id="quiz-hud-score" style="color:var(--text); font-weight:800;">Score: 0</span>
            </div>
          </div>

          <div class="quiz-progress-bar-wrap">
            <div class="quiz-progress-bar-fill" id="quiz-hud-progress"></div>
          </div>

          <div class="quiz-question-box">
            <div id="quiz-hud-target-wrap" style="display:none; margin-bottom: 12px;">
              <span class="quiz-q-target" id="quiz-hud-word">Target</span>
              <button class="btn-audio" id="quiz-hud-audio" onclick="playCurrentQuizAudio()">🔊 Pronounce</button>
            </div>
            <div class="quiz-q-prompt" id="quiz-hud-prompt">Question loading...</div>
          </div>

          <div class="quiz-options-list" id="quiz-options-box"></div>

          <div class="quiz-explanation-card" id="quiz-explanation-box">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom: 6px;">
              <strong id="quiz-explanation-title" style="color:var(--primary); font-size: 14px;">Explanation</strong>
              <button class="btn-bookmark" id="quiz-save-word-btn" style="padding: 4px 10px; font-size: 12px;" onclick="saveQuizCurrentWord()">☆ Save Word</button>
            </div>
            <div class="quiz-explanation-text" id="quiz-explanation-desc"></div>
          </div>

          <div style="margin-top: 24px; display:flex; justify-content:flex-end;">
            <button class="btn" id="quiz-next-btn" style="display:none;" onclick="nextQuizQuestion()">Next Question →</button>
          </div>
        </div>

        <!-- Quiz Results Card -->
        <div class="quiz-result-card" id="quiz-results">
          <div class="result-score-circle">
            <div class="result-score-val" id="res-score-pct">100%</div>
            <div class="result-score-label" id="res-score-pts">5/5 Correct</div>
          </div>
          <div class="result-badge" id="res-badge">Vocabulary Master 🏆</div>
          <h2 style="font-size:26px; font-weight:800; margin-bottom: 8px;" id="res-heading">Sensational Knowledge!</h2>
          <p style="color:var(--text-muted); font-size:15px;" id="res-sub">You have conquered this vocabulary challenge.</p>

          <div class="result-breakdown-grid">
            <div class="stat-card">
              <div class="stat-label">Correct Answers</div>
              <div class="stat-val" style="color:#10b981;" id="res-stat-correct">5</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Incorrect</div>
              <div class="stat-val" style="color:#ef4444;" id="res-stat-wrong">0</div>
            </div>
            <div class="stat-card">
              <div class="stat-label">Total Points</div>
              <div class="stat-val" id="res-stat-points">500</div>
            </div>
          </div>

          <div style="display:flex; gap: 14px; justify-content:center;">
            <button class="btn" onclick="resetQuizToLobby()">Play Another Quiz 🎯</button>
            <button class="btn-bookmark" onclick="switchTab('saved')">Review Saved Words ⭐</button>
          </div>
        </div>
      </div>
    </div>

    <!-- SAVED WORDS VIEW -->
    <div id="view-saved" class="view">
      <h1 class="hero-title">My Saved Words</h1>
      <p class="hero-sub">Revisit, study, and quiz yourself on your personal vocabulary library.</p>
      <div style="margin-bottom: 20px;">
        <button class="btn" onclick="startSavedWordsQuiz()">Quiz Me on My Saved Words 🧠</button>
      </div>
      <ul class="word-list" id="saved-list-container"></ul>
    </div>

    <!-- HISTORY VIEW -->
    <div id="view-history" class="view">
      <div style="display:flex; justify-content:space-between; align-items:center; max-width:860px; margin-bottom: 24px;">
        <div>
          <h1 class="hero-title">Search History</h1>
          <p class="hero-sub" style="margin-bottom:0;">Past authenticated dictionary discoveries.</p>
        </div>
        <button class="danger-btn" onclick="clearHistory()">Clear History</button>
      </div>
      <ul class="word-list" id="history-list-container"></ul>
    </div>

    <!-- PROFILE VIEW -->
    <div id="view-profile" class="view">
      <h1 class="hero-title">User Profile</h1>
      <p class="hero-sub">Account details, study statistics, and vocabulary progress.</p>
      <div class="stat-card" style="max-width: 600px; line-height: 1.8;">
        <div style="font-size: 13px; color: var(--text-muted); font-weight:700;">USERNAME</div>
        <div style="font-size: 22px; font-weight: 800;" id="prof-username">-</div>
        <div style="font-size: 13px; color: var(--text-muted); font-weight:700; margin-top: 16px;">EMAIL</div>
        <div style="font-size: 18px; font-weight: 600;" id="prof-email">-</div>
        <div style="font-size: 13px; color: var(--text-muted); font-weight:700; margin-top: 16px;">STUDENT STATUS</div>
        <div style="font-size: 16px; font-weight: 700; color:var(--primary);">Active Learner ⭐</div>
      </div>
    </div>

    <!-- SETTINGS VIEW -->
    <div id="view-settings" class="view">
      <h1 class="hero-title">Settings</h1>
      <p class="hero-sub">Appearance mode and application preferences.</p>
      <div class="stat-card" style="max-width: 600px;">
        <div style="font-weight: 800; font-size:16px; margin-bottom: 14px;">Theme Mode</div>
        <label style="display:flex; align-items:center; gap: 10px; margin-bottom: 12px; cursor: pointer; font-size: 15px; font-weight: 600;">
          <input type="radio" name="theme" value="light" checked onchange="setTheme('light')" /> Light Theme (Default)
        </label>
        <label style="display:flex; align-items:center; gap: 10px; cursor: pointer; font-size: 15px; font-weight: 600;">
          <input type="radio" name="theme" value="dark" onchange="setTheme('dark')" /> Dark Mode (High Contrast Studio)
        </label>
        <div style="margin-top: 26px; padding-top: 18px; border-top: 1px solid var(--border); font-size: 13px; color: var(--text-muted); line-height: 1.6;">
          Dictionary Word Finder Web Studio v2.0.0<br/>
          Verified Google / Lexicon English Vocabulary Engine with Interactive Quiz Section.
        </div>
      </div>
    </div>
  </main>

  <script>
    let currentUser = null;
    let currentWordData = null;

    // Web Audio Sound Synthesis for Instant Interactive Feedback
    function playAudioTone(isCorrect) {
      try {
        const AudioCtx = window.AudioContext || window.webkitAudioContext;
        if (!AudioCtx) return;
        const ctx = new AudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.connect(gain);
        gain.connect(ctx.destination);
        if (isCorrect) {
          osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5
          osc.frequency.setValueAtTime(880, ctx.currentTime + 0.08); // A5
          gain.gain.setValueAtTime(0.12, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.35);
          osc.start();
          osc.stop(ctx.currentTime + 0.35);
        } else {
          osc.frequency.setValueAtTime(220, ctx.currentTime); // A3
          osc.frequency.setValueAtTime(164.81, ctx.currentTime + 0.1); // E3
          gain.gain.setValueAtTime(0.15, ctx.currentTime);
          gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.28);
          osc.start();
          osc.stop(ctx.currentTime + 0.28);
        }
      } catch (e) {}
    }

    // Native Speech Synthesis for Authentic English Pronunciation
    function playPronunciation(word) {
      if (!word) return;
      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(word);
        utterance.lang = 'en-US';
        utterance.rate = 0.88;
        window.speechSynthesis.speak(utterance);
      }
    }

    // Auth Screen Functions
    function showRegister() {
      document.getElementById('login-box').style.display = 'none';
      document.getElementById('register-box').style.display = 'block';
    }
    function showLogin() {
      document.getElementById('register-box').style.display = 'none';
      document.getElementById('login-box').style.display = 'block';
    }

    async function handleRegister() {
      const u = document.getElementById('reg-username').value.trim();
      const e = document.getElementById('reg-email').value.trim();
      const p = document.getElementById('reg-password').value;
      const err = document.getElementById('reg-error');
      err.innerText = '';
      if(!u || !e || !p) { err.innerText = 'Please fill all fields.'; return; }

      const res = await fetch('/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, email: e, password: p })
      });
      const data = await res.json();
      if(data.success) {
        loginSuccess(data.user);
      } else {
        err.innerText = data.message || 'Registration failed.';
      }
    }

    async function handleLogin() {
      const e = document.getElementById('login-email').value.trim();
      const p = document.getElementById('login-password').value;
      const err = document.getElementById('login-error');
      err.innerText = '';
      if(!e || !p) { err.innerText = 'Please enter email and password.'; return; }

      const res = await fetch('/api/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: e, password: p })
      });
      const data = await res.json();
      if(data.success) {
        loginSuccess(data.user);
      } else {
        err.innerText = data.message || 'Invalid credentials.';
      }
    }

    function loginSuccess(user) {
      currentUser = user;
      document.getElementById('auth-screen').style.display = 'none';
      document.getElementById('current-user-display').innerText = user.username;
      document.getElementById('dash-greeting').innerText = `Good day, ${user.username} 👋`;
      document.getElementById('prof-username').innerText = user.username;
      document.getElementById('prof-email').innerText = user.email;
      loadStats();
      loadWordOfTheDay();
      loadQuizHistory();
    }

    function logout() {
      currentUser = null;
      document.getElementById('auth-screen').style.display = 'flex';
      showLogin();
    }

    // Navigation & Tabs
    function switchTab(tabName) {
      document.querySelectorAll('.nav-item').forEach(el => el.classList.remove('active'));
      document.querySelectorAll('.view').forEach(el => el.classList.remove('active'));
      const activeNav = Array.from(document.querySelectorAll('.nav-item')).find(el => el.innerText.toLowerCase().includes(tabName));
      if(activeNav) activeNav.classList.add('active');
      const v = document.getElementById('view-' + tabName);
      if(v) v.classList.add('active');

      if(tabName === 'saved') loadSavedWords();
      if(tabName === 'history') loadHistory();
      if(tabName === 'dashboard') { loadStats(); loadWordOfTheDay(); }
      if(tabName === 'quiz') { loadQuizHistory(); resetQuizToLobby(); }
    }

    async function loadWordOfTheDay() {
      try {
        const res = await fetch('/api/word_of_the_day');
        const data = await res.json();
        document.getElementById('wotd-word').innerText = data.word;
        document.getElementById('wotd-pos').innerText = data.pos;
        document.getElementById('wotd-def').innerText = data.def;
      } catch(e) {}
    }

    function quickSearchWotd() {
      const w = document.getElementById('wotd-word').innerText;
      searchPill(w);
    }

    function quickSearch(inputId) {
      const val = document.getElementById(inputId).value.trim();
      if(!val) return;
      document.getElementById('main-search-input').value = val;
      switchTab('search');
      executeSearch();
    }

    // Word Search & Authoritative Verification Engine
    async function executeSearch() {
      const word = document.getElementById('main-search-input').value.trim();
      if(!word) return;
      const statusEl = document.getElementById('search-status');
      const container = document.getElementById('search-result-container');
      const btn = document.getElementById('search-action-btn');

      statusEl.innerText = `Verifying dictionary for "${word}"...`;
      btn.disabled = true;
      btn.innerText = 'Verifying...';

      try {
        const res = await fetch(`/api/search?word=${encodeURIComponent(word)}&user_id=${currentUser ? currentUser.id : 1}`);
        const data = await res.json();
        statusEl.innerText = '';
        if(data.found) {
          currentWordData = data.word;
          renderWordResult(data.word, data.is_saved);
          loadStats();
        } else {
          renderWordNotFound(data);
        }
      } catch (err) {
        statusEl.innerText = 'Error fetching word details. Please try again.';
      } finally {
        btn.disabled = false;
        btn.innerText = 'Search';
      }
    }

    function renderWordResult(w, isSaved) {
      const container = document.getElementById('search-result-container');
      const defs = (w.definitions || []).map(d => `<div class="def-item">• ${d}</div>`).join('');
      const syns = (w.synonyms || []).map(s => `<span class="pill" onclick="searchPill('${s}')">${s}</span>`).join('');
      const ants = (w.antonyms || []).map(a => `<span class="pill" onclick="searchPill('${a}')">${a}</span>`).join('');
      const exms = (w.examples || []).map(x => `<div class="def-item" style="font-style:italic; border-left-color:#8b5cf6;">"${x}"</div>`).join('');
      const rels = (w.related_words || []).map(r => `<span class="pill" onclick="searchPill('${r}')">${r}</span>`).join('');

      container.innerHTML = `
        <div class="result-card">
          <div class="word-header">
            <div>
              <div class="word-title">${w.word}</div>
              <div class="word-phonetic-row">
                <span class="word-phonetic">${w.pronunciation || ''}</span>
                <button class="btn-audio" onclick="playPronunciation('${w.word}')">🔊 Listen</button>
              </div>
            </div>
            <div style="display:flex; align-items:center; gap: 12px;">
              ${w.part_of_speech ? `<span class="tag">${w.part_of_speech}</span>` : ''}
              <button class="btn-bookmark ${isSaved ? 'saved' : ''}" id="btn-save-toggle" onclick="toggleSaveCurrent()">
                ${isSaved ? '★ Saved' : '☆ Save Word'}
              </button>
            </div>
          </div>

          <div class="section-title">Authoritative Definitions</div>
          <div>${defs || '<p style="color:var(--text-muted)">No definitions found.</p>'}</div>

          ${exms ? `<div class="section-title">Real Example Sentences</div><div>${exms}</div>` : ''}
          ${syns ? `<div class="section-title">Synonyms</div><div class="pill-list">${syns}</div>` : ''}
          ${ants ? `<div class="section-title">Antonyms</div><div class="pill-list">${ants}</div>` : ''}
          ${rels ? `<div class="section-title">Related Lexicon Words</div><div class="pill-list">${rels}</div>` : ''}
        </div>
      `;
    }

    function renderWordNotFound(data) {
      const container = document.getElementById('search-result-container');
      const sugs = (data.suggestions || []).map(s => `<span class="pill" onclick="searchPill('${s}')">${s}</span>`).join('');
      container.innerHTML = `
        <div class="not-found-card">
          <div class="not-found-title">⚠️ Word Not Found in English Dictionary</div>
          <div class="not-found-desc">${data.message || 'We could not verify this term as a legitimate English dictionary word.'}</div>
          ${sugs ? `
            <div style="font-weight:700; font-size:14px; margin-bottom: 8px;">Did you mean one of these verified words?</div>
            <div class="pill-list">${sugs}</div>
          ` : `
            <p style="font-size:13px; color:var(--text-muted);">Please check the spelling or try searching for a standard English word.</p>
          `}
        </div>
      `;
    }

    function searchPill(word) {
      document.getElementById('main-search-input').value = word;
      switchTab('search');
      executeSearch();
    }

    async function toggleSaveCurrent() {
      if(!currentWordData || !currentUser) return;
      const btn = document.getElementById('btn-save-toggle');

      const res = await fetch('/api/toggle_save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: currentUser.id, word: currentWordData.word })
      });
      const data = await res.json();
      if(data.saved) {
        btn.classList.add('saved');
        btn.innerText = '★ Saved';
      } else {
        btn.classList.remove('saved');
        btn.innerText = '☆ Save Word';
      }
      loadStats();
    }

    async function loadStats() {
      if(!currentUser) return;
      const res = await fetch(`/api/stats?user_id=${currentUser.id}`);
      const d = await res.json();
      document.getElementById('stat-total-searches').innerText = d.total_searches;
      document.getElementById('stat-saved-words').innerText = d.saved_words;
      document.getElementById('stat-quiz-completed').innerText = d.total_quizzes;
      document.getElementById('stat-quiz-best').innerText = d.best_quiz_score + '%';
    }

    async function loadSavedWords() {
      if(!currentUser) return;
      const res = await fetch(`/api/saved?user_id=${currentUser.id}`);
      const list = await res.json();
      const c = document.getElementById('saved-list-container');
      if(!list.length) {
        c.innerHTML = '<p style="color:var(--text-muted); padding: 12px 0;">No saved words yet. Bookmark words from search to review them!</p>';
        return;
      }
      c.innerHTML = list.map(item => `
        <li class="word-list-item" onclick="searchPill('${item.word}')">
          <span style="font-size:17px; text-transform:capitalize;">${item.word}</span>
          <span style="font-size:12px; color:var(--text-muted);">${item.saved_at}</span>
        </li>
      `).join('');
    }

    async function loadHistory() {
      if(!currentUser) return;
      const res = await fetch(`/api/history?user_id=${currentUser.id}`);
      const list = await res.json();
      const c = document.getElementById('history-list-container');
      if(!list.length) {
        c.innerHTML = '<p style="color:var(--text-muted); padding: 12px 0;">No verified search history found.</p>';
        return;
      }
      c.innerHTML = list.map(item => `
        <li class="word-list-item" onclick="searchPill('${item.word}')">
          <span style="font-size:17px; text-transform:capitalize;">${item.word}</span>
          <span style="font-size:12px; color:var(--text-muted);">${item.searched_at}</span>
        </li>
      `).join('');
    }

    async function clearHistory() {
      if(!currentUser) return;
      if(!confirm("Are you sure you want to permanently clear your search history?")) return;
      try {
        const res = await fetch('/api/clear_history', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ user_id: currentUser.id })
        });
        const data = await res.json();
        if(data.success) {
          const c = document.getElementById('history-list-container');
          if(c) c.innerHTML = '<p style="color:var(--text-muted); padding: 12px 0;">No history found.</p>';
          loadStats();
        }
      } catch (e) {
        console.error("Failed to clear history:", e);
      }
    }

    // ================= QUIZ ENGINE CLIENT LOGIC =================
    let quizCategory = 'all';
    let quizDifficulty = 'easy';
    let quizCount = 5;
    let quizQuestions = [];
    let currentQIndex = 0;
    let quizScore = 0;
    let quizStreak = 0;
    let quizAnswered = false;

    function selectQuizCategory(cat, el) {
      quizCategory = cat;
      document.querySelectorAll('.quiz-cat-item').forEach(e => e.classList.remove('active'));
      el.classList.add('active');
    }

    function selectQuizDifficulty(diff, el) {
      quizDifficulty = diff;
      document.querySelectorAll('.quiz-diff-btn').forEach(e => e.classList.remove('active'));
      el.classList.add('active');
    }

    function selectQuizCount(n) {
      quizCount = n;
      document.getElementById('btn-count-5').classList.toggle('active', n === 5);
      document.getElementById('btn-count-10').classList.toggle('active', n === 10);
    }

    function startSavedWordsQuiz() {
      quizCategory = 'saved';
      switchTab('quiz');
      document.querySelectorAll('.quiz-cat-item').forEach(e => {
        if(e.dataset.cat === 'saved') e.classList.add('active');
        else e.classList.remove('active');
      });
      startQuizSession();
    }

    async function startQuizSession() {
      const uid = currentUser ? currentUser.id : 1;
      const lobby = document.getElementById('quiz-lobby');
      const player = document.getElementById('quiz-player');
      const results = document.getElementById('quiz-results');

      lobby.style.display = 'none';
      results.style.display = 'none';
      player.style.display = 'block';

      currentQIndex = 0;
      quizScore = 0;
      quizStreak = 0;

      try {
        const url = `/api/quiz/questions?user_id=${uid}&category=${quizCategory}&difficulty=${quizDifficulty}&count=${quizCount}`;
        const res = await fetch(url);
        quizQuestions = await res.json();
        if(!quizQuestions || !quizQuestions.length) {
          alert("Could not load questions for this category. Please try another category.");
          resetQuizToLobby();
          return;
        }
        renderQuizQuestion();
      } catch(err) {
        alert("Error loading quiz questions.");
        resetQuizToLobby();
      }
    }

    function renderQuizQuestion() {
      quizAnswered = false;
      const q = quizQuestions[currentQIndex];
      const total = quizQuestions.length;

      document.getElementById('quiz-hud-counter').innerText = `Question ${currentQIndex + 1} of ${total}`;
      document.getElementById('quiz-hud-streak').innerText = `🔥 Streak: ${quizStreak}`;
      document.getElementById('quiz-hud-score').innerText = `Score: ${quizScore}`;
      document.getElementById('quiz-hud-progress').style.width = `${((currentQIndex) / total) * 100}%`;

      document.getElementById('quiz-hud-prompt').innerText = q.question;

      const targetWrap = document.getElementById('quiz-hud-target-wrap');
      if(q.word) {
        targetWrap.style.display = 'flex';
        document.getElementById('quiz-hud-word').innerText = `${q.word} (${q.part_of_speech || ''}) ${q.phonetic || ''}`;
      } else {
        targetWrap.style.display = 'none';
      }

      document.getElementById('quiz-explanation-box').style.display = 'none';
      document.getElementById('quiz-next-btn').style.display = 'none';

      const letters = ['A', 'B', 'C', 'D'];
      const optBox = document.getElementById('quiz-options-box');
      optBox.innerHTML = q.options.map((opt, idx) => `
        <button class="quiz-opt-btn" onclick="submitQuizOption(${idx})">
          <span class="opt-badge">${letters[idx]}</span>
          <span>${opt}</span>
        </button>
      `).join('');
    }

    function playCurrentQuizAudio() {
      const q = quizQuestions[currentQIndex];
      if(q && q.word) playPronunciation(q.word);
    }

    async function saveQuizCurrentWord() {
      const q = quizQuestions[currentQIndex];
      if(!q || !q.word || !currentUser) return;
      const btn = document.getElementById('quiz-save-word-btn');
      const res = await fetch('/api/toggle_save', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ user_id: currentUser.id, word: q.word })
      });
      const data = await res.json();
      if(data.saved) {
        btn.innerText = '★ Saved';
        btn.style.background = '#fef3c7';
        btn.style.color = '#b45309';
      } else {
        btn.innerText = '☆ Save Word';
        btn.style.background = 'transparent';
      }
      loadStats();
    }

    function submitQuizOption(selectedIdx) {
      if(quizAnswered) return;
      quizAnswered = true;
      const q = quizQuestions[currentQIndex];
      const optButtons = document.querySelectorAll('.quiz-opt-btn');

      const isCorrect = (selectedIdx === q.correct_index);
      playAudioTone(isCorrect);

      if(isCorrect) {
        quizScore += 100 + (quizStreak * 20);
        quizStreak += 1;
        optButtons[selectedIdx].classList.add('correct');
      } else {
        quizStreak = 0;
        optButtons[selectedIdx].classList.add('wrong');
        optButtons[q.correct_index].classList.add('correct');
      }

      optButtons.forEach(b => b.disabled = true);

      document.getElementById('quiz-hud-streak').innerText = `🔥 Streak: ${quizStreak}`;
      document.getElementById('quiz-hud-score').innerText = `Score: ${quizScore}`;

      const expBox = document.getElementById('quiz-explanation-box');
      document.getElementById('quiz-explanation-title').innerText = isCorrect ? '🎉 Correct!' : '💡 Incorrect!';
      document.getElementById('quiz-explanation-desc').innerText = q.explanation;
      document.getElementById('quiz-save-word-btn').innerText = '☆ Save Word';
      expBox.style.display = 'block';

      const nextBtn = document.getElementById('quiz-next-btn');
      nextBtn.style.display = 'inline-flex';
      nextBtn.innerText = (currentQIndex === quizQuestions.length - 1) ? 'Finish Quiz 🏁' : 'Next Question →';
    }

    async function nextQuizQuestion() {
      currentQIndex++;
      if(currentQIndex < quizQuestions.length) {
        renderQuizQuestion();
      } else {
        finishQuizSession();
      }
    }

    async function finishQuizSession() {
      document.getElementById('quiz-player').style.display = 'none';
      const results = document.getElementById('quiz-results');
      results.style.display = 'block';

      const total = quizQuestions.length;
      const ptsPerQ = 100;
      const correctCount = Math.round(quizScore / ptsPerQ);
      const actualCorrect = Math.min(correctCount, total);
      const pct = Math.round((actualCorrect / total) * 100);

      document.getElementById('res-score-pct').innerText = `${pct}%`;
      document.getElementById('res-score-pts').innerText = `${actualCorrect}/${total} Correct`;
      document.getElementById('res-stat-correct').innerText = actualCorrect;
      document.getElementById('res-stat-wrong').innerText = total - actualCorrect;
      document.getElementById('res-stat-points').innerText = quizScore;

      let badge = "Keep Practicing! 📚";
      let heading = "Good Effort!";
      let sub = "Keep reviewing words to strengthen your lexicon.";

      if(pct === 100) {
        badge = "Vocabulary Master 🏆";
        heading = "Flawless Performance!";
        sub = "You mastered every single word in this challenge.";
      } else if(pct >= 80) {
        badge = "Lexicon Champion ⭐";
        heading = "Outstanding Knowledge!";
        sub = "Your vocabulary command is top-tier.";
      } else if(pct >= 60) {
        badge = "Solid Word Power ⚡";
        heading = "Well Done!";
        sub = "A solid score. Try another round to reach 100%!";
      }

      document.getElementById('res-badge').innerText = badge;
      document.getElementById('res-heading').innerText = heading;
      document.getElementById('res-sub').innerText = sub;

      // Submit results to backend database
      try {
        await fetch('/api/quiz/submit', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            user_id: currentUser ? currentUser.id : 1,
            category: quizCategory,
            difficulty: quizDifficulty,
            score: actualCorrect,
            total_questions: total
          })
        });
        loadStats();
        loadQuizHistory();
      } catch(e) {}
    }

    function resetQuizToLobby() {
      document.getElementById('quiz-player').style.display = 'none';
      document.getElementById('quiz-results').style.display = 'none';
      document.getElementById('quiz-lobby').style.display = 'block';
      loadQuizHistory();
    }

    async function loadQuizHistory() {
      if(!currentUser) return;
      try {
        const res = await fetch(`/api/quiz/history?user_id=${currentUser.id}`);
        const rows = await res.json();
        const container = document.getElementById('quiz-history-table-container');
        if(!rows.length) {
          container.innerHTML = '<p style="color:var(--text-muted); font-size:14px;">No quizzes completed yet. Take your first quiz today!</p>';
          return;
        }
        container.innerHTML = `
          <table class="history-table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Category</th>
                <th>Difficulty</th>
                <th>Score</th>
                <th>Accuracy</th>
              </tr>
            </thead>
            <tbody>
              ${rows.map(r => `
                <tr>
                  <td>${r.completed_at}</td>
                  <td style="text-transform:capitalize;">${r.category}</td>
                  <td style="text-transform:capitalize;">${r.difficulty}</td>
                  <td>${r.score}/${r.total_questions}</td>
                  <td style="color:${r.percentage >= 80 ? '#10b981' : (r.percentage >= 60 ? '#f59e0b' : '#ef4444')}; font-weight:800;">
                    ${Math.round(r.percentage)}%
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        `;
      } catch(e) {}
    }

    function setTheme(mode) {
      if(mode === 'dark') document.body.classList.add('dark');
      else document.body.classList.remove('dark');
    }
  </script>
</body>
</html>
"""

class RequestHandler(BaseHTTPRequestHandler):
    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        try:
            self.wfile.write(json.dumps(data).encode("utf-8"))
        except (BrokenPipeError, ConnectionAbortedError):
            pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        url_parts = self.path.split("?")
        path = url_parts[0]
        params = {}
        if len(url_parts) > 1:
            for p in url_parts[1].split("&"):
                if "=" in p:
                    k, v = p.split("=", 1)
                    params[k] = urllib.parse.unquote_plus(v)

        if path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            try:
                html_file_path = os.path.join(os.path.dirname(__file__), "index.html")
                if os.path.exists(html_file_path):
                    with open(html_file_path, "rb") as f:
                        self.wfile.write(f.read())
                else:
                    self.wfile.write(HTML_PAGE.encode("utf-8"))
            except (BrokenPipeError, ConnectionAbortedError):
                pass
            return

        if path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        if path == "/api/search":
            word = params.get("word", "").strip()
            user_id = params.get("user_id", "1")
            word_info = lookup_dictionary_word(word)

            if word_info.get("found"):
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("INSERT INTO search_history (user_id, word, searched_at) VALUES (?, ?, ?)", (user_id, word, now))
                conn.commit()

            cur.execute("SELECT id FROM saved_words WHERE user_id=? AND LOWER(word)=LOWER(?)", (user_id, word))
            is_saved = cur.fetchone() is not None

            conn.close()
            self._send_json({
                "found": word_info.get("found", False),
                "word": word_info,
                "is_saved": is_saved,
                "suggestions": word_info.get("suggestions", []),
                "message": word_info.get("message", "")
            })
            return

        if path == "/api/word_of_the_day":
            conn.close()
            self._send_json(get_word_of_the_day())
            return

        if path == "/api/quiz/questions":
            user_id = params.get("user_id", "1")
            category = params.get("category", "all")
            difficulty = params.get("difficulty", "easy")
            count = int(params.get("count", 5))
            conn.close()
            questions = generate_quiz_questions(user_id=user_id, category=category, difficulty=difficulty, count=count)
            self._send_json(questions)
            return

        if path == "/api/quiz/history":
            user_id = params.get("user_id", "1")
            cur.execute("""
                SELECT category, difficulty, score, total_questions, percentage, completed_at
                FROM quiz_history
                WHERE user_id=?
                ORDER BY id DESC LIMIT 20
            """, (user_id,))
            rows = cur.fetchall()
            conn.close()
            self._send_json([
                {
                    "category": r[0],
                    "difficulty": r[1],
                    "score": r[2],
                    "total_questions": r[3],
                    "percentage": r[4],
                    "completed_at": r[5]
                }
                for r in rows
            ])
            return

        if path == "/api/quiz/stats":
            user_id = params.get("user_id", "1")
            cur.execute("SELECT COUNT(*), MAX(percentage) FROM quiz_history WHERE user_id=?", (user_id,))
            row = cur.fetchone()
            tot = row[0] if row else 0
            best = row[1] if row and row[1] is not None else 0
            conn.close()
            self._send_json({"total_quizzes": tot, "best_score": round(best, 1)})
            return

        if path == "/api/saved":
            user_id = params.get("user_id", "1")
            cur.execute("SELECT word, saved_at FROM saved_words WHERE user_id=? ORDER BY id DESC", (user_id,))
            rows = cur.fetchall()
            conn.close()
            self._send_json([{"word": r[0], "saved_at": r[1]} for r in rows])
            return

        if path == "/api/history":
            user_id = params.get("user_id", "1")
            cur.execute("SELECT word, searched_at FROM search_history WHERE user_id=? ORDER BY id DESC LIMIT 50", (user_id,))
            rows = cur.fetchall()
            conn.close()
            self._send_json([{"word": r[0], "searched_at": r[1]} for r in rows])
            return

        if path == "/api/stats":
            user_id = params.get("user_id", "1")
            cur.execute("SELECT COUNT(*) FROM search_history WHERE user_id=?", (user_id,))
            tot_searches = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM saved_words WHERE user_id=?", (user_id,))
            sav_words = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*), MAX(percentage) FROM quiz_history WHERE user_id=?", (user_id,))
            q_row = cur.fetchone()
            tot_quizzes = q_row[0] if q_row else 0
            best_quiz = q_row[1] if q_row and q_row[1] is not None else 0
            conn.close()
            self._send_json({
                "total_searches": tot_searches,
                "saved_words": sav_words,
                "total_quizzes": tot_quizzes,
                "best_quiz_score": round(best_quiz)
            })
            return

        conn.close()
        self.send_error(404, "Not Found")

    def do_POST(self):
        url_parts = self.path.split("?")
        path = url_parts[0]
        params = {}
        if len(url_parts) > 1:
            for p in url_parts[1].split("&"):
                if "=" in p:
                    k, v = p.split("=", 1)
                    params[k] = urllib.parse.unquote_plus(v)

        content_len = int(self.headers.get("Content-Length", 0))
        post_body = self.rfile.read(content_len) if content_len > 0 else b""
        data = json.loads(post_body.decode("utf-8")) if post_body else {}

        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()

        if path == "/api/register":
            username = data.get("username", "").strip()
            email = data.get("email", "").strip()
            password = data.get("password", "")
            if not username or not email or not password:
                conn.close()
                self._send_json({"success": False, "message": "All fields are required."})
                return

            p_hash = hash_password(password)
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                cur.execute(
                    "INSERT INTO users (username, email, password_hash, created_at, updated_at) VALUES (?, ?, ?, ?, ?)",
                    (username, email, p_hash, now, now)
                )
                conn.commit()
                uid = cur.lastrowid
                conn.close()
                self._send_json({"success": True, "user": {"id": uid, "username": username, "email": email}})
            except sqlite3.IntegrityError:
                conn.close()
                self._send_json({"success": False, "message": "Username or email already exists."})
            return

        if path == "/api/login":
            identifier = (data.get("email") or data.get("username") or "").strip()
            password = data.get("password", "")
            p_hash = hash_password(password)
            cur.execute("SELECT id, username, email FROM users WHERE (email=? OR username=?) AND password_hash=?", (identifier, identifier, p_hash))
            row = cur.fetchone()
            conn.close()
            if row:
                self._send_json({"success": True, "user": {"id": row[0], "username": row[1], "email": row[2]}})
            else:
                self._send_json({"success": False, "message": "Invalid username/email or password."})
            return

        if path == "/api/toggle_save":
            user_id = data.get("user_id") or params.get("user_id")
            word = data.get("word", "").strip().lower()
            cur.execute("SELECT id FROM saved_words WHERE user_id=? AND LOWER(word)=?", (user_id, word))
            row = cur.fetchone()
            if row:
                cur.execute("DELETE FROM saved_words WHERE id=?", (row[0],))
                saved = False
            else:
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cur.execute("INSERT INTO saved_words (user_id, word, saved_at) VALUES (?, ?, ?)", (user_id, word, now))
                saved = True
            conn.commit()
            conn.close()
            self._send_json({"saved": saved})
            return

        if path == "/api/clear_history":
            user_id = data.get("user_id") or params.get("user_id")
            cur.execute("DELETE FROM search_history WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()
            self._send_json({"success": True})
            return

        if path == "/api/quiz/submit":
            user_id = data.get("user_id", 1)
            category = data.get("category", "all")
            difficulty = data.get("difficulty", "easy")
            score = int(data.get("score", 0))
            total = int(data.get("total_questions", 5))
            pct = round((score / total) * 100, 2) if total > 0 else 0
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            cur.execute("""
                INSERT INTO quiz_history (user_id, category, difficulty, score, total_questions, percentage, completed_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (user_id, category, difficulty, score, total, pct, now))
            conn.commit()
            conn.close()
            self._send_json({"success": True, "percentage": pct})
            return

        conn.close()
        self.send_error(404, "Not Found")

def run():
    init_db()
    server_address = ('', PORT)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Dictionary Word Finder Studio running on http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

if __name__ == '__main__':
    run()
