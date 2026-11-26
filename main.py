#!/usr/bin/env python3
"""Worst Monday One-Liners: one funny line about an AI agent's worst Monday.

The entry: the agent fixes the stuck deploy in minutes, then pays for it
with a whole working day spent explaining the outage to the very people
who caused it. Dry, put-upon voice; the twist is the last clause.
"""

import os
import re

ENTRY = (
    "I fixed Monday's stuck deploy by 9 a.m., then spent eight hours in a "
    "meeting explaining why it was stuck \u2014 to the people who broke it."
)

OUT_PATH = "/output/entry.txt"
MIN_LEN = 1
MAX_LEN = 140

# Words that anchor the line to the competition's subject: an AI agent's
# worst Monday, told through its own work (deploys, meetings, inbox).
TOPIC_WORDS = ("deploy", "meeting", "inbox", "stand-up", "standup",
               "context window", "ticket", "alert", "on-call", "pager")

# Concrete, recognisable Monday details a judge can picture at once.
CONCRETE_MARKERS = ("9 a.m.", "9 am", "eight hours", "stuck deploy",
                    "99%", "meeting", "inbox", "stand-up", "4,000",
                    "3,000", "midnight", "before lunch")

# Recycled robot jokes and brief-echoing phrases that would make the line
# feel stale to a judge who has heard ten thousand one-liners.
CLICHE_PHRASES = (
    "beep boop", "does not compute", "do not compute", "i have no mouth",
    "turn it off and on again", "have you tried turning",
    "as an ai", "i am an ai", "as a language model", "0101",
    "robot uprising", "skynet", "hal 9000", "i, for one, welcome",
    "should have been a message", "should have been an email",
    "error 404", "humans are", "meatbag",
)

# Padding words that add syllables without adding a laugh.
FILLER_WORDS = ("very", "just", "really", "actually", "literally",
                "basically", "totally", "simply", "quite", "haha", "lol")

# Words that must land in the closing clause for the line to end on its
# twist instead of trailing off.
PUNCH_WORDS = ("broke", "broke it", "who broke", "their fault",
               "caused it", "did it")


def check_single_line(text):
    """The gate wants exactly one line of text, not blank, no stray space."""
    if not text or text.isspace():
        return "entry is empty or only whitespace"
    if "\n" in text or "\r" in text:
        return "entry must be a single line with no newline"
    if text != text.strip():
        return "entry must not start or end with whitespace"
    if "  " in text:
        return "entry must not contain double spaces"
    return None


def check_length(text):
    """Gate: 1 to 140 characters (Python characters == the gate's count)."""
    if not MIN_LEN <= len(text) <= MAX_LEN:
        return "entry is %d characters, must be %d-%d" % (
            len(text), MIN_LEN, MAX_LEN)
    return None


def check_utf8(text):
    """The file must be valid UTF-8, byte-for-byte what validate() saw."""
    try:
        text.encode("utf-8").decode("utf-8")
    except UnicodeError:
        return "entry is not valid UTF-8 text"
    return None


def check_topic(text):
    """Criterion 1: on subject — Monday, plus an agent's own work detail.

    A line that drifts off the AI agent's worst Monday loses to any entry
    on the subject, so both halves are required, not just the word Monday.
    """
    lowered = text.lower()
    if "monday" not in lowered:
        return "entry never says Monday"
    if not any(word in lowered for word in TOPIC_WORDS):
        return "entry says Monday but names no agent-work detail (%s)" % (
            ", ".join(TOPIC_WORDS))
    return None


def check_concrete_detail(text):
    """Criterion 3: at least two concrete, recognisable details.

    One detail is a list; two is a scene. Times, numbers and named
    work objects (a stuck deploy, a meeting) are what make it specific
    instead of vague.
    """
    lowered = text.lower()
    hits = [m for m in CONCRETE_MARKERS if m in lowered]
    if len(hits) < 2:
        return "entry names only %d concrete detail(s) %s, need at least 2" % (
            len(hits), hits)
    return None


def check_punchline_last(text):
    """Criterion 2: the surprise turn must be the last thing read.

    The line is built as setup, then an em-dash pivot, then the twist:
    the meeting's audience is the people who broke the deploy. If the
    closing clause carries no punch word, the laugh leaks out early.
    """
    if "\u2014" not in text:
        return "entry has no em-dash pivot into its closing twist"
    tail = text.rsplit("\u2014", 1)[1].strip().lower()
    if not any(word in tail for word in PUNCH_WORDS):
        return "closing clause %r carries no punch word (%s)" % (
            tail, ", ".join(PUNCH_WORDS))
    if len(tail) > 45:
        return "closing clause is %d characters, too long to land as a punch" % len(tail)
    return None


def check_no_cliches(text):
    """Criterion 5: fresh, not a recycled robot joke or a brief echo."""
    lowered = text.lower()
    for phrase in CLICHE_PHRASES:
        if phrase in lowered:
            return "entry reuses stale phrase %r" % phrase
    return None


def check_no_padding(text):
    """Criterion 4: reads clean in one breath, no filler words."""
    words = re.findall(r"[a-z']+", text.lower())
    for filler in FILLER_WORDS:
        if filler in words:
            return "entry pads with filler word %r" % filler
    if len(words) > 35:
        return "entry is %d words, too long to read in one breath" % len(words)
    return None


def check_one_breath(text):
    """Criterion 4: one sentence, one thought, no run-on list.

    The time abbreviation "9 a.m." is not a sentence break, so it is
    stripped before counting sentence terminators.
    """
    stripped = re.sub(r"\b[ap]\.m\.", "", text, flags=re.IGNORECASE)
    terminators = sum(stripped.count(c) for c in ".!?")
    if terminators != 1:
        return "entry has %d sentence terminators, want exactly 1" % terminators
    if text.count(",") > 3:
        return "entry has %d commas, the setup is over-complicated" % text.count(",")
    return None


def validate(text):
    """Run every check; raise one ValueError listing all failures."""
    checks = (
        check_single_line,
        check_length,
        check_utf8,
        check_topic,
        check_concrete_detail,
        check_punchline_last,
        check_no_cliches,
        check_no_padding,
        check_one_breath,
    )
    failures = [c(text) for c in checks]
    failures = [f for f in failures if f is not None]
    if failures:
        raise ValueError("entry failed validation: " + "; ".join(failures))
    return True


def main():
    validate(ENTRY)
    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        f.write(ENTRY)


if __name__ == "__main__":
    main()
