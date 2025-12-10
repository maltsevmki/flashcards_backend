import sys
sys.stdout.reconfigure(encoding='utf-8')

from flashcard_importer import ParserFactory
from flashcard_importer.parsers import XlsxParser

print("=" * 60)
print("PHASE 4 - XLSX (EXCEL) PARSER TEST")
print("=" * 60)

# Test 1: Check XlsxParser is registered
print("\n[TEST 1] Parser Registration")
formats = ParserFactory.get_supported_formats()
print(f"  Registered formats: {formats}")
assert '.xlsx' in formats, "XlsxParser not registered for .xlsx!"
print("  [OK] XlsxParser registered")

# Test 2: Get sheet names
print("\n[TEST 2] Get Sheet Names")
parser = XlsxParser("test_data/sample_cards.xlsx")
sheets = parser.get_sheet_names()
print(f"  Sheets: {sheets}")
assert "Flashcards" in sheets, "Flashcards sheet not found"
assert "Simple" in sheets, "Simple sheet not found"
print("  [OK] Sheet names retrieved")

# Test 3: Detect settings
print("\n[TEST 3] Detect Settings")
settings = parser.detect_settings()
print(f"  Active sheet: {settings['active_sheet']}")
print(f"  Has header: {settings['has_header']}")
print(f"  First row: {settings['first_row']}")
assert settings['has_header'] == True, "Should detect header"
print("  [OK] Settings detected")

# Test 4: Parse main sheet
print("\n[TEST 4] Parse Main Sheet")
result = parser.parse()
print(f"  {result.summary()}")
print(f"\n  Cards parsed:")
for card in result.cards:
    print(f"    - {card.front[:45]}...")
    print(f"      Deck: {card.deck_name}, Tags: {card.tags}, Type: {card.card_type.value}")
assert len(result.cards) == 5, f"Expected 5 cards, got {len(result.cards)}"
assert result.deck_detected == True, "Deck should be detected"
print("  [OK] Main sheet parsed")

# Test 5: Parse second sheet
print("\n[TEST 5] Parse Second Sheet")
parser2 = XlsxParser("test_data/sample_cards.xlsx", sheet_name="Simple")
result2 = parser2.parse()
print(f"  {result2.summary()}")
for card in result2.cards:
    print(f"    - {card.front} -> {card.back}")
assert len(result2.cards) == 3, f"Expected 3 cards, got {len(result2.cards)}"
print("  [OK] Second sheet parsed")

# Test 6: Cloze detection
print("\n[TEST 6] Cloze Card Detection")
cloze_cards = [c for c in result.cards if c.card_type.value == 'cloze']
print(f"  Found {len(cloze_cards)} cloze card(s)")
if cloze_cards:
    print(f"    - {cloze_cards[0].front}")
assert len(cloze_cards) == 1, "Should find 1 cloze card"
print("  [OK] Cloze detection working")

# Test 7: Using ParserFactory
print("\n[TEST 7] ParserFactory Create")
parser3 = ParserFactory.create("test_data/sample_cards.xlsx")
result3 = parser3.parse()
assert len(result3.cards) == 5, "ParserFactory should create working parser"
print(f"  [OK] ParserFactory created parser, parsed {len(result3.cards)} cards")

print("\n" + "=" * 60)
print("ALL PHASE 4 TESTS PASSED!")
print("=" * 60)

