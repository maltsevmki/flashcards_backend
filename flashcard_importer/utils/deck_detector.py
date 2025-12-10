from typing import List, Optional, Dict
from collections import Counter


class DeckDetector:
    """
    Detect and suggest deck names when missing from import files.
    Uses content analysis and pattern matching.
    """

    # Common category keywords and their suggested deck names
    CATEGORY_PATTERNS = {
        'programming': [
            'python', 'java', 'javascript', 'code', 'function', 'class',
            'variable', 'loop', 'algorithm', 'api', 'database', 'sql'
        ],
        'languages': [
            'spanish', 'french', 'german', 'japanese', 'chinese', 'english',
            'vocabulary', 'grammar', 'conjugation', 'translation'
        ],
        'science': [
            'biology', 'chemistry', 'physics', 'atom', 'molecule', 'cell',
            'energy', 'force', 'evolution', 'dna', 'element'
        ],
        'math': [
            'equation', 'formula', 'calculate', 'number', 'algebra', 'geometry',
            'calculus', 'derivative', 'integral', 'function', 'graph'
        ],
        'history': [
            'war', 'century', 'empire', 'king', 'president', 'revolution',
            'ancient', 'medieval', 'dynasty', 'civilization'
        ],
        'geography': [
            'country', 'capital', 'continent', 'ocean', 'mountain', 'river',
            'population', 'climate', 'region', 'border'
        ],
        'medicine': [
            'disease', 'symptom', 'treatment', 'drug', 'anatomy', 'diagnosis',
            'patient', 'surgery', 'therapy', 'medical'
        ],
    }
    
    @classmethod
    def suggest_deck_from_content(cls, cards: List) -> Optional[str]:
        """Analyze card content and suggest a deck name."""
        if not cards:
            return None
        
        # Collect all text content
        all_text = []
        for card in cards:
            all_text.append(card.front.lower())
            all_text.append(card.back.lower())
            all_text.extend([t.lower() for t in card.tags])
        
        combined_text = ' '.join(all_text)
        
        # Count matches for each category
        category_scores = {}
        for category, keywords in cls.CATEGORY_PATTERNS.items():
            score = sum(1 for kw in keywords if kw in combined_text)
            if score > 0:
                category_scores[category] = score
        
        if category_scores:
            best_category = max(category_scores, key=category_scores.get)
            return best_category.title()
        
        return None
    
    @classmethod
    def suggest_deck_from_tags(cls, cards: List) -> Optional[str]:
        """Suggest deck name based on most common tags."""
        all_tags = []
        for card in cards:
            all_tags.extend(card.tags)
        
        if not all_tags:
            return None
        
        # Find most common tag
        tag_counts = Counter(all_tags)
        most_common = tag_counts.most_common(1)
        
        if most_common:
            return most_common[0][0].title()
        
        return None
    
    @classmethod
    def group_cards_by_suggested_deck(cls, cards: List) -> Dict[str, List]:
        """Group cards by their suggested deck (based on content analysis)."""
        groups = {}
        
        for card in cards:
            # Try to determine category from card content
            text = f"{card.front} {card.back} {' '.join(card.tags)}".lower()
            
            suggested = None
            for category, keywords in cls.CATEGORY_PATTERNS.items():
                if any(kw in text for kw in keywords):
                    suggested = category.title()
                    break
            
            if not suggested:
                suggested = "General"
            
            if suggested not in groups:
                groups[suggested] = []
            groups[suggested].append(card)
        
        return groups
    
    @classmethod
    def analyze_deck_coverage(cls, cards: List) -> Dict:
        """Analyze how many cards have deck information."""
        total = len(cards)
        with_deck = sum(1 for c in cards if c.deck_name)
        without_deck = total - with_deck
        
        unique_decks = set(c.deck_name for c in cards if c.deck_name)
        
        return {
            'total_cards': total,
            'cards_with_deck': with_deck,
            'cards_without_deck': without_deck,
            'coverage_percent': (with_deck / total * 100) if total > 0 else 0,
            'unique_decks': list(unique_decks),
            'needs_deck_assignment': without_deck > 0
        }


class MissingDeckHandler:
    """Handle cards that are missing deck information."""
    
    @classmethod
    def get_warning_message(cls, cards_without_deck: int, total_cards: int) -> str:
        """Generate warning message for missing deck info."""
        percent = (cards_without_deck / total_cards * 100) if total_cards > 0 else 0
        
        if cards_without_deck == total_cards:
            return (
                f"Warning: All {total_cards} cards are missing deck information. "
                f"They will be imported to a default deck. "
                f"Consider organizing them into decks after import."
            )
        elif cards_without_deck > 0:
            return (
                f"Warning: {cards_without_deck} of {total_cards} cards ({percent:.1f}%) "
                f"are missing deck information. These will be imported to a default deck."
            )
        return ""
    
    @classmethod
    def assign_default_deck(cls, cards: List, default_name: str = "Imported") -> int:
        """Assign a default deck name to cards without one. Returns count of modified cards."""
        modified = 0
        for card in cards:
            if not card.deck_name:
                card.deck_name = default_name
                modified += 1
        return modified
    
    @classmethod
    def assign_suggested_decks(cls, cards: List) -> Dict[str, int]:
        """Assign AI-suggested deck names to cards. Returns deck assignment counts."""
        groups = DeckDetector.group_cards_by_suggested_deck(cards)
        counts = {}
        
        for deck_name, deck_cards in groups.items():
            for card in deck_cards:
                if not card.deck_name:
                    card.deck_name = deck_name
            counts[deck_name] = len([c for c in deck_cards if c.deck_name == deck_name])
        
        return counts

