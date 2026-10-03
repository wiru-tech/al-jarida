"""
Text-direction detection for user-authored (reader) blog content.

The newsroom's editorial Article model gets its RTL behaviour from the
*site's active language* (see static/css/rtl.css) — an editor picks
"Urdu" for the whole article. Reader-written BlogPosts have no such
per-article language field; a signed-in reader may write a title in
English and the body in Urdu (or vice-versa) in the same post, so each
field's direction is detected independently from what was actually typed.

Detection strategy: scan the string for the first "strong" directional
character — the first Arabic-script codepoint (which covers Urdu, since
Urdu is written in an extended Arabic script) or the first Latin letter,
whichever comes first. This mirrors how the Unicode bidi algorithm picks
a paragraph's base direction, and correctly handles text that starts
with punctuation, digits, or a mix of both scripts.
"""
import re

# Arabic, Arabic Supplement, Arabic Extended-A, Arabic Presentation Forms —
# covers standard Urdu text (which uses the Arabic script) as well as Arabic.
_RTL_CHAR = re.compile(r"[\u0600-\u06FF\u0750-\u077F\u08A0-\u08FF\uFB50-\uFDFF\uFE70-\uFEFF]")
_LTR_CHAR = re.compile(r"[A-Za-z]")

LTR = "ltr"
RTL = "rtl"


def detect_direction(text):
    """Return 'ltr' or 'rtl' for the given text, defaulting to 'ltr'
    for empty or direction-neutral text (pure numbers/punctuation)."""
    if not text:
        return LTR
    for ch in text:
        if _RTL_CHAR.match(ch):
            return RTL
        if _LTR_CHAR.match(ch):
            return LTR
    return LTR
