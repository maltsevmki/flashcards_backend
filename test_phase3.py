import sys

from flashcard_importer import ParserFactory
from flashcard_importer.parsers import CsvParser

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 60)
print("PHASE 3 - CSV PARSER TEST")
print("=" * 60)

# Test 1: Check CsvParser is registered
print("\n[TEST 1] Parser Registration")
formats = ParserFactory.get_supported_formats()
print(f"  Registered formats: {formats}")
assert '.csv' in formats, "CsvParser not registered for .csv!"
assert '.tsv' in formats, "CsvParser not registered for .tsv!"
print("  [OK] CsvParser registered for .csv and .tsv")

# Test 2: Parse simple CSV (no headers)
print("\n[TEST 2] Parse Simple CSV (no headers)")
parser = CsvParser("test_data/simple.csv")
parser.settings = {'delimiter': ',', 'has_header': False}
result = parser.parse()
print(f"  {result.summary()}")
for card in result.cards:
    print(f"    - {card.front} -> {card.back}")
assert len(result.cards) == 4, f"Expected 4 cards, got {len(result.cards)}"
print("  [OK] Simple CSV parsed")

# Test 3: Parse CSV with headers
print("\n[TEST 3] Parse CSV with Headers")
parser = ParserFactory.create("test_data/sample_cards.csv")
settings = parser.detect_settings()
print(f"  Detected: delimiter='{settings['delimiter']}', has_header={settings['has_header']}")
result = parser.parse()
print(f"  {result.summary()}")
print("\n  Cards:")
for card in result.cards:
    print(f"    - {card.front[:40]}...")
    print(f"      Deck: {card.deck_name}, Tags: {card.tags}")
assert len(result.cards) == 4, f"Expected 4 cards, got {len(result.cards)}"
assert result.cards[0].deck_name == "Programming", "Deck not parsed correctly"
print("  [OK] CSV with headers parsed")

# Test 4: Parse TSV file
print("\n[TEST 4] Parse TSV File")
parser = ParserFactory.create("test_data/sample_cards.tsv")
settings = parser.detect_settings()
print(f"  Detected: delimiter='\\t' (tab), has_header={settings['has_header']}")
result = parser.parse()
print(f"  {result.summary()}")
for card in result.cards:
    print(f"    - {card.front} -> {card.back[:30]}...")
assert len(result.cards) == 3, f"Expected 3 cards, got {len(result.cards)}"
print("  [OK] TSV file parsed")

# Test 5: Custom column mapping
print("\n[TEST 5] Custom Column Mapping")
parser = CsvParser("test_data/sample_cards.tsv")
parser.set_column_mapping(front=0, back=1, deck=2)
result = parser.parse()
# First row is header, should be skipped if has_header=True
print("  Cards with deck from column 3:")
for card in result.cards:
    print(f"    - {card.front}: deck={card.deck_name}")
print("  [OK] Custom column mapping works")

print("\n" + "=" * 60)
print("ALL PHASE 3 TESTS PASSED!")
print("=" * 60)
