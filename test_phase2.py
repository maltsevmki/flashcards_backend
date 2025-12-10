import sys
sys.stdout.reconfigure(encoding='utf-8')

from flashcard_importer import ParserFactory
from flashcard_importer.parsers import TxtParser

print("=" * 60)
print("PHASE 2 - TXT PARSER TEST")
print("=" * 60)

# Test 1: Check TxtParser is registered
print("\n[TEST 1] Parser Registration")
formats = ParserFactory.get_supported_formats()
print(f"  Registered formats: {formats}")
assert '.txt' in formats, "TxtParser not registered!"
print("  [OK] TxtParser registered")

# Test 2: Parse simple file (no headers)
print("\n[TEST 2] Parse Simple File (no headers)")
parser = ParserFactory.create("test_data/simple_cards.txt")
result = parser.parse()
print(f"  {result.summary()}")
print(f"  Cards:")
for card in result.cards:
    print(f"    - {card.front[:40]}... -> {card.back[:30]}...")
assert len(result.cards) == 3, f"Expected 3 cards, got {len(result.cards)}"
print("  [OK] Simple file parsed correctly")

# Test 3: Parse Anki file with headers
print("\n[TEST 3] Parse Anki File (with headers)")
parser = TxtParser("test_data/sample_anki.txt")

# Check detected settings
settings = parser.detect_settings()
print(f"  Detected settings: {settings}")
assert settings['separator'] == '\t', "Separator not detected"
assert settings['html'] == True, "HTML setting not detected"
assert settings['columns']['deck'] == 3, "Deck column not detected"
print("  [OK] Headers detected correctly")

# Parse the file
result = parser.parse()
print(f"\n  {result.summary()}")
print(f"  Deck detected: {result.deck_detected}")

print(f"\n  Cards parsed:")
for i, card in enumerate(result.cards, 1):
    print(f"    {i}. Front: {card.front[:50]}...")
    print(f"       Back: {card.back[:50]}...")
    print(f"       Deck: {card.deck_name}")
    print(f"       Tags: {card.tags}")
    print(f"       Type: {card.card_type.value}")
    print()

assert len(result.cards) == 4, f"Expected 4 cards, got {len(result.cards)}"
assert result.deck_detected == True, "Deck should be detected"
print("  [OK] Anki file parsed correctly")

# Test 4: Check cloze detection
print("\n[TEST 4] Cloze Card Detection")
cloze_cards = [c for c in result.cards if c.card_type.value == 'cloze']
print(f"  Found {len(cloze_cards)} cloze card(s)")
assert len(cloze_cards) == 1, "Should find 1 cloze card"
print("  [OK] Cloze detection working")

# Test 5: Parse with errors
print("\n[TEST 5] Error Handling")
from flashcard_importer.exceptions import FileFormatError
try:
    parser = ParserFactory.create("nonexistent.txt")
except FileNotFoundError as e:
    print(f"  [OK] FileNotFoundError raised: {e}")

print("\n" + "=" * 60)
print("ALL PHASE 2 TESTS PASSED!")
print("=" * 60)

