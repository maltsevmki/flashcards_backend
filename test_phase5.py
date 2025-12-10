import sys

from flashcard_importer import ParserFactory
from flashcard_importer.parsers import ApkgParser

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("PHASE 5 - APKG (ANKI PACKAGE) PARSER TEST")
print("=" * 60)

# Test 1: Check ApkgParser is registered
print("\n[TEST 1] Parser Registration")
formats = ParserFactory.get_supported_formats()
print(f"  Registered formats: {formats}")
assert '.apkg' in formats, "ApkgParser not registered for .apkg!"
assert '.colpkg' in formats, "ApkgParser not registered for .colpkg!"
print("  [OK] ApkgParser registered for .apkg and .colpkg")

# Test 2: Detect settings
print("\n[TEST 2] Detect Settings")
parser = ApkgParser("test_data/sample_deck.apkg")
settings = parser.detect_settings()
print(f"  Note count: {settings['note_count']}")
print(f"  Card count: {settings['card_count']}")
print(f"  Decks: {settings['decks']}")
print(f"  Models: {settings['models']}")
assert settings['note_count'] == 8, f"Expected 8 notes, got {settings['note_count']}"
print("  [OK] Settings detected")

# Test 3: Get decks
print("\n[TEST 3] Get Decks")
decks = parser.get_decks()
print(f"  Available decks: {list(decks.values())}")
assert "Programming" in decks.values(), "Programming deck not found"
assert "Languages" in decks.values(), "Languages deck not found"
print("  [OK] Decks retrieved")

# Test 4: Parse all cards
print("\n[TEST 4] Parse All Cards")
result = parser.parse()
print(f"  {result.summary()}")
print("\n  Sample cards:")
for card in result.cards[:5]:
    print(f"    - {card.front[:40]}...")
    print(f"      Deck: {card.deck_name}, Tags: {card.tags}")
assert len(result.cards) == 8, f"Expected 8 cards, got {len(result.cards)}"
assert result.deck_detected is True, "Decks should be detected"
print("  [OK] All cards parsed")

# Test 5: Filter by deck
print("\n[TEST 5] Filter by Deck")
parser2 = ApkgParser("test_data/sample_deck.apkg")
result_filtered = parser2.parse(deck_filter="Languages")
print(f"  Cards in 'Languages' deck: {len(result_filtered.cards)}")
for card in result_filtered.cards:
    print(f"    - {card.front} -> {card.back}")
assert len(result_filtered.cards) == 2, f"Expected 2 cards, got {len(result_filtered.cards)}"
print("  [OK] Deck filter works")

# Test 6: Cloze detection
print("\n[TEST 6] Cloze Card Detection")
cloze_cards = [c for c in result.cards if c.card_type.value == 'cloze']
print(f"  Found {len(cloze_cards)} cloze card(s)")
if cloze_cards:
    print(f"    - {cloze_cards[0].front}")
assert len(cloze_cards) == 1, "Should find 1 cloze card"
print("  [OK] Cloze detection working")

# Test 7: HTML detection
print("\n[TEST 7] HTML Content Detection")
html_cards = [c for c in result.cards if c.html_enabled]
print(f"  Found {len(html_cards)} card(s) with HTML")
assert len(html_cards) >= 1, "Should find at least 1 HTML card"
print("  [OK] HTML detection working")

# Test 8: Extra fields
print("\n[TEST 8] Extra Fields")
cards_with_extra = [c for c in result.cards if c.extra]
print(f"  Found {len(cards_with_extra)} card(s) with extra fields")
if cards_with_extra:
    print(f"    - Extra: {cards_with_extra[0].extra}")
assert len(cards_with_extra) >= 1, "Should find at least 1 card with extra"
print("  [OK] Extra fields parsed")

# Test 9: Tags parsing
print("\n[TEST 9] Tags Parsing")
all_tags = set()
for card in result.cards:
    all_tags.update(card.tags)
print(f"  All tags found: {sorted(all_tags)}")
assert "python" in all_tags, "python tag not found"
assert "spanish" in all_tags, "spanish tag not found"
print("  [OK] Tags parsed correctly")

# Test 10: Using ParserFactory
print("\n[TEST 10] ParserFactory Create")
parser3 = ParserFactory.create("test_data/sample_deck.apkg")
result3 = parser3.parse()
assert len(result3.cards) == 8, "ParserFactory should create working parser"
print(f"  [OK] ParserFactory created parser, parsed {len(result3.cards)} cards")

print("\n" + "=" * 60)
print("ALL PHASE 5 TESTS PASSED!")
print("=" * 60)
