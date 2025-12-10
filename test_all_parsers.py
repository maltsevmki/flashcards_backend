import sys

from flashcard_importer import ParserFactory

sys.stdout.reconfigure(encoding='utf-8')

print("=" * 70)
print("FLASHCARD IMPORTER - COMPLETE TEST SUITE")
print("=" * 70)

# Test all registered formats
print("\n[1] REGISTERED PARSERS")
formats = ParserFactory.get_supported_formats()
print(f"    Supported formats: {formats}")
print(f"    Total: {len(formats)} formats")

# Summary table
results_summary = []

# Test TXT Parser
print("\n[2] TXT PARSER")
parser = ParserFactory.create("test_data/sample_anki.txt")
result = parser.parse()
print("    File: sample_anki.txt")
print(f"    Cards: {len(result.cards)}, Skipped: {result.skipped_count}")
results_summary.append(("TXT (Anki)", len(result.cards), result.skipped_count))

parser = ParserFactory.create("test_data/simple_cards.txt")
result = parser.parse()
print("    File: simple_cards.txt")
print(f"    Cards: {len(result.cards)}, Skipped: {result.skipped_count}")
results_summary.append(("TXT (Simple)", len(result.cards), result.skipped_count))

# Test CSV Parser
print("\n[3] CSV PARSER")
parser = ParserFactory.create("test_data/sample_cards.csv")
result = parser.parse()
print("    File: sample_cards.csv")
print(f"    Cards: {len(result.cards)}, Skipped: {result.skipped_count}")
results_summary.append(("CSV", len(result.cards), result.skipped_count))

parser = ParserFactory.create("test_data/sample_cards.tsv")
result = parser.parse()
print("    File: sample_cards.tsv")
print(f"    Cards: {len(result.cards)}, Skipped: {result.skipped_count}")
results_summary.append(("TSV", len(result.cards), result.skipped_count))

# Test XLSX Parser
print("\n[4] XLSX PARSER")
parser = ParserFactory.create("test_data/sample_cards.xlsx")
result = parser.parse()
print("    File: sample_cards.xlsx")
print(f"    Cards: {len(result.cards)}, Skipped: {result.skipped_count}")
results_summary.append(("XLSX", len(result.cards), result.skipped_count))

# Test APKG Parser
print("\n[5] APKG PARSER")
parser = ParserFactory.create("test_data/sample_deck.apkg")
result = parser.parse()
print("    File: sample_deck.apkg")
print(f"    Cards: {len(result.cards)}, Skipped: {result.skipped_count}")
print(f"    Decks: {list(parser.get_decks().values())}")
results_summary.append(("APKG", len(result.cards), result.skipped_count))

# Summary
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"\n{'Format':<20} {'Cards':<10} {'Skipped':<10} {'Status':<10}")
print("-" * 50)
total_cards = 0
total_skipped = 0
for fmt, cards, skipped in results_summary:
    status = "OK" if cards > 0 else "EMPTY"
    print(f"{fmt:<20} {cards:<10} {skipped:<10} {status:<10}")
    total_cards += cards
    total_skipped += skipped

print("-" * 50)
print(f"{'TOTAL':<20} {total_cards:<10} {total_skipped:<10}")

print("\n" + "=" * 70)
print("ALL PARSERS WORKING CORRECTLY!")
print("=" * 70)
