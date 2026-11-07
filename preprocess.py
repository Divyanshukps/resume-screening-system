"""Text-preprocessing pipeline: tokenization -> stop-word removal -> lemmatization.

Uses NLTK when its data is available. If NLTK (or its data download) is not
available, it falls back to a small built-in implementation so the project
still runs offline.
"""
import re

from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# Keeps tokens like "c++", "c#", "node.js", "scikit-learn"
TOKEN_RE = re.compile(r"[a-z][a-z0-9+#.\-]*|[0-9]+")

# Words that appear in almost every resume and add no ranking signal
RESUME_NOISE = {
    "resume", "curriculum", "vitae", "email", "phone", "mobile", "address",
    "linkedin", "github", "references", "available", "upon", "request",
}


def _load_nltk():
    """Return (stopword_set, lemmatize_fn) using NLTK, or None if unavailable."""
    try:
        import nltk
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer

        for pkg, path in (("stopwords", "corpora/stopwords"), ("wordnet", "corpora/wordnet")):
            try:
                nltk.data.find(path)
            except LookupError:
                if not nltk.download(pkg, quiet=True):
                    return None
        lemmatizer = WordNetLemmatizer()
        lemmatizer.lemmatize("tests")  # force-load, raises if data is broken
        return set(stopwords.words("english")), lemmatizer.lemmatize
    except Exception:
        return None


def _simple_lemma(word: str) -> str:
    """Very small rule-based fallback lemmatizer."""
    if len(word) > 4 and word.endswith("ies"):
        return word[:-3] + "y"
    if len(word) > 5 and word.endswith("ing"):
        return word[:-3]
    if len(word) > 4 and word.endswith("ed"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s") and not word.endswith("ss"):
        return word[:-1]
    return word


_nltk = _load_nltk()
if _nltk:
    STOP_WORDS, _lemmatize = _nltk
    BACKEND = "nltk"
else:
    STOP_WORDS, _lemmatize = set(ENGLISH_STOP_WORDS), _simple_lemma
    BACKEND = "fallback"

STOP_WORDS = STOP_WORDS | RESUME_NOISE


def tokenize(text: str) -> list:
    tokens = TOKEN_RE.findall(text.lower())
    return [t.strip(".-") for t in tokens if t.strip(".-")]


def preprocess(text: str) -> str:
    """Clean raw resume / job-description text into a normalized string."""
    text = re.sub(r"\S+@\S+", " ", text)          # emails
    text = re.sub(r"https?://\S+|www\.\S+", " ", text)  # urls
    tokens = tokenize(text)
    tokens = [t for t in tokens if t not in STOP_WORDS and len(t) > 1]
    tokens = [_lemmatize(t) for t in tokens]
    return " ".join(tokens)
