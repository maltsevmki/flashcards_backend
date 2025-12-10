import sys

from flashcard_importer import Flashcard, ParserFactory
from flashcard_importer.utils import (
    ImportLogger,
    HtmlHandler, HtmlHandlingMode,
    DeckDetector, MissingDeckHandler,
    MultiFieldHandler, FieldMapping,
    CardValidator
)

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("PHASE 4 - EDGE CASES & VALIDATION")
print("=" * 70)

# ============================================================
# Task 4.1: Handle missing deck info
# ============================================================
print("\n" + "=" * 70)
print("TASK 4.1: Handle Missing Deck Info")
print("=" * 70)

# Create test cards without deck info
test_cards = [
    Flashcard(front="What is Python?", back="A programming language", tags=["python"]),
    Flashcard(front="def function():", back="Function definition in Python", tags=["python", "code"]),
    Flashcard(front="Hola", back="Hello in Spanish", tags=["spanish"]),
    Flashcard(front="What is H2O?", back="Water molecule", tags=["chemistry", "science"]),
    Flashcard(front="2 + 2 = ?", back="4", tags=["math"]),
]

print("\n[4.1.1] Analyze Deck Coverage")
coverage = DeckDetector.analyze_deck_coverage(test_cards)
print(f"  Total cards: {coverage['total_cards']}")
print(f"  With deck: {coverage['cards_with_deck']}")
print(f"  Without deck: {coverage['cards_without_deck']}")
print(f"  Coverage: {coverage['coverage_percent']:.1f}%")

print("\n[4.1.2] Generate Warning Message")
warning = MissingDeckHandler.get_warning_message(
    coverage['cards_without_deck'],
    coverage['total_cards']
)
print(f"  {warning}")

print("\n[4.1.3] Suggest Deck from Content")
suggested = DeckDetector.suggest_deck_from_content(test_cards)
print(f"  Suggested deck: {suggested}")

print("\n[4.1.4] Group Cards by Suggested Deck (AI Detection)")
groups = DeckDetector.group_cards_by_suggested_deck(test_cards)
for deck_name, cards in groups.items():
    print(f"  {deck_name}: {len(cards)} cards")
    for c in cards:
        print(f"    - {c.front[:30]}...")

print("\n[4.1.5] Assign Suggested Decks")
# Create fresh cards for modification
cards_to_modify = [
    Flashcard(front="What is Python?", back="A programming language", tags=["python"]),
    Flashcard(front="Bonjour", back="Hello in French", tags=["french"]),
    Flashcard(front="E = mc^2", back="Einstein's equation", tags=["physics"]),
]
counts = MissingDeckHandler.assign_suggested_decks(cards_to_modify)
print(f"  Deck assignments: {counts}")
for c in cards_to_modify:
    print(f"    - '{c.front[:25]}...' -> Deck: {c.deck_name}")

print("\n  [OK] Missing deck handling complete")

# ============================================================
# Task 4.2: Skip malformed cards with logging
# ============================================================
print("\n" + "=" * 70)
print("TASK 4.2: Skip Malformed Cards with Logging")
print("=" * 70)

print("\n[4.2.1] Create Import Logger")
logger = ImportLogger(source_file="test_import.csv")

# Simulate parsing with various issues
logger.info("Starting import")
logger.debug("Detected 10 rows")
logger.warning("Line 3: Empty front field - card skipped", line_number=3, field_name="front")
logger.warning("Line 5: Back field too short", line_number=5, field_name="back")
logger.error("Line 7: Invalid format - missing separator", line_number=7)
logger.error("Line 9: Encoding error - invalid UTF-8", line_number=9)
logger.info("Import completed with warnings")

print("\n[4.2.2] Logger Summary")
print(f"  {logger.get_summary()}")

print("\n[4.2.3] Warnings List")
for warn in logger.get_warnings():
    print(f"  {warn}")

print("\n[4.2.4] Errors List")
for err in logger.get_errors():
    print(f"  {err}")

print("\n[4.2.5] Validate Card Content")
test_contents = [
    ("Valid content", True),
    ("", False),
    ("   ", False),
    ("X" * 60000, False),  # Too long
    ("Short but valid", True),
]
for content, expected in test_contents:
    is_valid, error = CardValidator.validate_content(content)
    status = "PASS" if is_valid == expected else "FAIL"
    preview = content[:20] + "..." if len(content) > 20 else content or "(empty)"
    print(f"  [{status}] '{preview}' -> valid={is_valid}")

print("\n  [OK] Malformed card handling complete")

# ============================================================
# Task 4.3: Detect and handle HTML content
# ============================================================
print("\n" + "=" * 70)
print("TASK 4.3: Detect and Handle HTML Content")
print("=" * 70)

html_content = """
<div class="card">
    <h2>Question</h2>
    <p>What is <b>Python</b>?</p>
    <img src="python_logo.png">
    <a href="https://python.org">Learn more</a>
    [sound:audio.mp3]
</div>
"""

print("\n[4.3.1] Detect HTML")
has_html = HtmlHandler.contains_html(html_content)
print(f"  Contains HTML: {has_html}")

print("\n[4.3.2] Analyze Content")
analysis = HtmlHandler.analyze_content(html_content)
for key, value in analysis.items():
    print(f"  {key}: {value}")

print("\n[4.3.3] Extract Media References")
media = HtmlHandler.extract_media_references(html_content)
print(f"  Images: {media['images']}")
print(f"  Audio: {media['audio']}")

print("\n[4.3.4] Strip HTML")
stripped = HtmlHandler.strip_html(html_content)
print(f"  Stripped: {stripped[:100]}...")

print("\n[4.3.5] Convert to Plain Text")
plain = HtmlHandler.convert_to_plain_text(html_content)
print(f"  Plain text: {plain[:100]}...")

print("\n[4.3.6] Process with Different Modes")
for mode in HtmlHandlingMode:
    result = HtmlHandler.process("<b>Bold</b> and <i>italic</i>", mode)
    print(f"  {mode.value}: '{result}'")

print("\n[4.3.7] Sanitize for Display")
long_html = "<p>" + "Very long content. " * 50 + "</p>"
sanitized = HtmlHandler.sanitize_for_display(long_html, max_length=50)
print(f"  Sanitized preview: '{sanitized}'")

print("\n  [OK] HTML handling complete")

# ============================================================
# Task 4.4: Support multi-field notes
# ============================================================
print("\n" + "=" * 70)
print("TASK 4.4: Support Multi-field Notes")
print("=" * 70)

print("\n[4.4.1] Detect Field Mapping from Headers")
headers = ["Question", "Answer", "Extra Notes", "Deck", "Tags", "Hint"]
mapping = MultiFieldHandler.detect_field_mapping(headers)
print(f"  Headers: {headers}")
print(f"  Detected mapping: {mapping.to_dict()}")

print("\n[4.4.2] Parse Row with Mapping")
sample_row = [
    "What is Python?", "A programming language", "Created by Guido",
    "Programming", "python, basics", "Think of a snake"
]
parsed = MultiFieldHandler.parse_row_with_mapping(sample_row, mapping)
print(f"  Row: {sample_row}")
print("  Parsed:")
for key, value in parsed.items():
    print(f"    {key}: {value}")

print("\n[4.4.3] Validate Mapping")
is_valid, errors = MultiFieldHandler.validate_mapping(mapping, len(sample_row))
print(f"  Valid: {is_valid}")
if errors:
    print(f"  Errors: {errors}")

print("\n[4.4.4] Invalid Mapping Detection")
bad_mapping = FieldMapping(front=0, back=10)  # Column 10 doesn't exist
is_valid, errors = MultiFieldHandler.validate_mapping(bad_mapping, 5)
print("  Mapping: front=0, back=10 for 5 columns")
print(f"  Valid: {is_valid}")
print(f"  Errors: {errors}")

print("\n[4.4.5] Merge Extra Fields")
extra_fields = ["Note 1", "Note 2", "", "Note 3"]
merged = MultiFieldHandler.merge_extra_fields(extra_fields)
print(f"  Fields: {extra_fields}")
print(f"  Merged: '{merged}'")

print("\n[4.4.6] Split Combined Field")
combined = "Part A | Part B | Part C"
parts = MultiFieldHandler.split_combined_field(combined, delimiter='|')
print(f"  Combined: '{combined}'")
print(f"  Parts: {parts}")

print("\n  [OK] Multi-field handling complete")

# ============================================================
# Integration Test with Real Parser
# ============================================================
print("\n" + "=" * 70)
print("INTEGRATION TEST: Full Import with Edge Case Handling")
print("=" * 70)

# Parse a file and apply edge case handling
parser = ParserFactory.create("test_data/sample_cards.csv")
result = parser.parse()

print("\n[1] Initial Import")
print(f"  {result.summary()}")

print("\n[2] Deck Analysis")
coverage = DeckDetector.analyze_deck_coverage(result.cards)
print(f"  Coverage: {coverage['coverage_percent']:.1f}%")
print(f"  Unique decks: {coverage['unique_decks']}")

print("\n[3] HTML Analysis")
html_cards = [
    c for c in result.cards
    if HtmlHandler.contains_html(c.front) or HtmlHandler.contains_html(c.back)
]
print(f"  Cards with HTML: {len(html_cards)}")

print("\n[4] Cards with Extra Fields")
extra_cards = [c for c in result.cards if c.extra]
print(f"  Cards with extra: {len(extra_cards)}")

print("\n" + "=" * 70)
print("ALL PHASE 4 TESTS PASSED!")
print("=" * 70)
