from openpyxl import Workbook

# Create a workbook with sample flashcards
wb = Workbook()
ws = wb.active
ws.title = "Flashcards"

# Add headers
ws.append(["Front", "Back", "Deck", "Tags"])

# Add sample cards
cards = [
    ["What is Python?", "A high-level programming language", "Programming", "python, basics"],
    ["What is a class?", "A blueprint for creating objects", "Programming", "oop, python"],
    ["What is inheritance?", "A mechanism to derive new classes from existing ones", "OOP", "oop, inheritance"],
    ["What is {{c1::polymorphism}}?", "The ability of objects to take many forms", "OOP", "oop, concepts"],
    ["What is an API?", "Application Programming Interface", "Web Development", "api, web"],
]

for card in cards:
    ws.append(card)

# Create a second sheet with simple data
ws2 = wb.create_sheet("Simple")
ws2.append(["Question", "Answer"])
ws2.append(["1 + 1 = ?", "2"])
ws2.append(["2 * 3 = ?", "6"])
ws2.append(["10 / 2 = ?", "5"])

# Save the workbook
wb.save("test_data/sample_cards.xlsx")
print("Created test_data/sample_cards.xlsx")

