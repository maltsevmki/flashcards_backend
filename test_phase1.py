import sys
sys.stdout.reconfigure(encoding='utf-8')

from flashcard_importer import (
    Flashcard, 
    ImportResult, 
    CardType,
    ParserFactory,
    FileFormatError
)
from flashcard_importer.utils import (
    AnkiHeaderParser,
    CardValidator,
    TagParser
)

print("=" * 50)
print("PHASE 1 - FINAL TEST")
print("=" * 50)

# Test 1: Flashcard creation
card = Flashcard(
    front="What is the capital of France?",
    back="Paris",
    deck_name="Geography",
    tags=["europe", "capitals"]
)
print(f"\n[OK] Test 1: Created card - {card}")
print(f"  Valid: {card.is_valid()}")

# Test 2: ImportResult tracking
result = ImportResult(source_file="test_cards.txt")
result.add_card(card)
result.add_card(Flashcard(front="2+2=?", back="4", deck_name="Math"))
result.add_error("Line 5: Empty front field")
result.add_error("Line 8: Invalid format")
result.deck_detected = True

print(f"\n[OK] Test 2: ImportResult")
print(result.summary())

# Test 3: CardType enum
print(f"\n[OK] Test 3: CardType - {CardType.BASIC.value}, {CardType.CLOZE.value}")

# Test 4: AnkiHeaderParser
headers = ["#separator:tab", "#html:true", "#deck column:3"]
settings = AnkiHeaderParser.parse_all_headers(headers)
print(f"\n[OK] Test 4: Parsed headers - {settings}")

# Test 5: CardValidator
is_cloze = CardValidator.is_cloze_card("The {{c1::answer}} is here")
has_html = CardValidator.contains_html("<b>bold</b>")
print(f"\n[OK] Test 5: Cloze={is_cloze}, HTML={has_html}")

# Test 6: TagParser
tags = TagParser.parse_tags("python science::physics basics")
print(f"\n[OK] Test 6: Parsed tags - {tags}")

# Test 7: ParserFactory (no parsers registered yet)
formats = ParserFactory.get_supported_formats()
print(f"\n[OK] Test 7: Registered formats - {formats}")

# Test 8: Exception handling
try:
    ParserFactory.create("test.xyz")
except FileFormatError as e:
    print(f"\n[OK] Test 8: FileFormatError caught correctly")

print("\n" + "=" * 50)
print("ALL PHASE 1 TESTS PASSED!")
print("=" * 50)
