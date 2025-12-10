"""
Create a test Anki package (.apkg) file for testing the ApkgParser.
"""
import sqlite3
import zipfile
import json
import time
import os

def create_test_apkg(output_path: str):
    """Create a minimal but valid .apkg file for testing."""
    
    # Create the SQLite database
    db_path = "collection.anki2"
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create the schema (simplified version of Anki's schema)
    cursor.executescript("""
        CREATE TABLE col (
            id INTEGER PRIMARY KEY,
            crt INTEGER NOT NULL,
            mod INTEGER NOT NULL,
            scm INTEGER NOT NULL,
            ver INTEGER NOT NULL,
            dty INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            ls INTEGER NOT NULL,
            conf TEXT NOT NULL,
            models TEXT NOT NULL,
            decks TEXT NOT NULL,
            dconf TEXT NOT NULL,
            tags TEXT NOT NULL
        );
        
        CREATE TABLE notes (
            id INTEGER PRIMARY KEY,
            guid TEXT NOT NULL,
            mid INTEGER NOT NULL,
            mod INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            tags TEXT NOT NULL,
            flds TEXT NOT NULL,
            sfld TEXT NOT NULL,
            csum INTEGER NOT NULL,
            flags INTEGER NOT NULL,
            data TEXT NOT NULL
        );
        
        CREATE TABLE cards (
            id INTEGER PRIMARY KEY,
            nid INTEGER NOT NULL,
            did INTEGER NOT NULL,
            ord INTEGER NOT NULL,
            mod INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            type INTEGER NOT NULL,
            queue INTEGER NOT NULL,
            due INTEGER NOT NULL,
            ivl INTEGER NOT NULL,
            factor INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            lapses INTEGER NOT NULL,
            left INTEGER NOT NULL,
            odue INTEGER NOT NULL,
            odid INTEGER NOT NULL,
            flags INTEGER NOT NULL,
            data TEXT NOT NULL
        );
        
        CREATE TABLE revlog (
            id INTEGER PRIMARY KEY,
            cid INTEGER NOT NULL,
            usn INTEGER NOT NULL,
            ease INTEGER NOT NULL,
            ivl INTEGER NOT NULL,
            lastIvl INTEGER NOT NULL,
            factor INTEGER NOT NULL,
            time INTEGER NOT NULL,
            type INTEGER NOT NULL
        );
        
        CREATE TABLE graves (
            usn INTEGER NOT NULL,
            oid INTEGER NOT NULL,
            type INTEGER NOT NULL
        );
    """)
    
    # Current timestamp
    now = int(time.time())
    
    # Define decks
    decks = {
        "1": {"name": "Default", "id": 1},
        "1234567890": {"name": "Programming", "id": 1234567890},
        "1234567891": {"name": "Languages", "id": 1234567891}
    }
    
    # Define models (note types) with fields
    models = {
        "1234": {
            "name": "Basic",
            "id": 1234,
            "flds": [
                {"name": "Front", "ord": 0},
                {"name": "Back", "ord": 1}
            ],
            "tmpls": [{"name": "Card 1"}]
        },
        "1235": {
            "name": "Basic (with extra)",
            "id": 1235,
            "flds": [
                {"name": "Front", "ord": 0},
                {"name": "Back", "ord": 1},
                {"name": "Extra", "ord": 2}
            ],
            "tmpls": [{"name": "Card 1"}]
        }
    }
    
    # Insert collection data
    cursor.execute("""
        INSERT INTO col VALUES (1, ?, ?, ?, 11, 0, 0, 0, '{}', ?, ?, '{}', '{}')
    """, (now, now, now, json.dumps(models), json.dumps(decks)))
    
    # Sample flashcards - using \x1f as field separator
    notes_data = [
        # (id, guid, mid, tags, flds, deck_id)
        (1, "abc1", 1234, "python basics", "What is Python?\x1fA high-level programming language", 1234567890),
        (2, "abc2", 1234, "python oop", "What is a class?\x1fA blueprint for creating objects", 1234567890),
        (3, "abc3", 1234, "javascript web", "What is JavaScript?\x1fA scripting language for web browsers", 1234567890),
        (4, "abc4", 1235, "python advanced", "What is a decorator?\x1fA function that modifies another function\x1fUsed with @ syntax", 1234567890),
        (5, "abc5", 1234, "spanish", "Hello\x1fHola", 1234567891),
        (6, "abc6", 1234, "spanish", "Goodbye\x1fAdios", 1234567891),
        (7, "abc7", 1234, "cloze-test", "The capital of {{c1::France}} is {{c2::Paris}}\x1f(Cloze card)", 1234567890),
        (8, "abc8", 1234, "html-test", "<b>Bold question</b>\x1f<i>Italic answer</i>", 1234567890),
    ]
    
    for note_id, guid, mid, tags, flds, deck_id in notes_data:
        # Insert note
        cursor.execute("""
            INSERT INTO notes VALUES (?, ?, ?, ?, 0, ?, ?, ?, 0, 0, '')
        """, (note_id, guid, mid, now, tags, flds, flds.split('\x1f')[0]))
        
        # Insert card
        cursor.execute("""
            INSERT INTO cards VALUES (?, ?, ?, 0, ?, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '')
        """, (note_id * 10, note_id, deck_id, now))
    
    conn.commit()
    conn.close()
    
    # Create the .apkg file (ZIP containing the database)
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.write(db_path, "collection.anki2")
        # Add empty media file (required by Anki)
        zf.writestr("media", "{}")
    
    # Clean up
    os.remove(db_path)
    
    print(f"Created {output_path}")
    print(f"  - 3 decks: Default, Programming, Languages")
    print(f"  - 8 notes with various tags and content")
    print(f"  - Includes: cloze card, HTML card, extra fields")


if __name__ == "__main__":
    create_test_apkg("test_data/sample_deck.apkg")

