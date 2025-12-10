import re
from typing import Tuple, List
from enum import Enum
from html import unescape


class HtmlHandlingMode(Enum):
    KEEP = "keep"           # Keep HTML as-is
    STRIP = "strip"         # Remove all HTML tags
    CONVERT = "convert"     # Convert to plain text (preserve structure)


class HtmlHandler:
    """Handle HTML content in flashcards."""
    
    # Patterns
    TAG_PATTERN = re.compile(r'<[^>]+>')
    IMG_PATTERN = re.compile(r'<img[^>]*src=["\']([^"\']+)["\'][^>]*>', re.IGNORECASE)
    AUDIO_PATTERN = re.compile(r'\[sound:([^\]]+)\]')
    LINK_PATTERN = re.compile(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*>(.*?)</a>', re.IGNORECASE | re.DOTALL)
    
    # Block elements that should become newlines
    BLOCK_ELEMENTS = ['div', 'p', 'br', 'hr', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 
                      'ul', 'ol', 'li', 'table', 'tr', 'blockquote', 'pre']
    
    @classmethod
    def contains_html(cls, content: str) -> bool:
        """Check if content contains HTML tags."""
        return bool(cls.TAG_PATTERN.search(content))
    
    @classmethod
    def strip_html(cls, content: str) -> str:
        """Remove all HTML tags from content."""
        result = content
        
        # Handle line breaks
        result = re.sub(r'<br\s*/?>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'</p>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'</div>', '\n', result, flags=re.IGNORECASE)
        result = re.sub(r'</li>', '\n', result, flags=re.IGNORECASE)
        
        # Remove all remaining tags
        result = cls.TAG_PATTERN.sub('', result)
        
        # Decode HTML entities
        result = unescape(result)
        
        # Clean up whitespace
        result = re.sub(r'\n\s*\n', '\n\n', result)  # Multiple newlines -> double
        result = re.sub(r'[ \t]+', ' ', result)       # Multiple spaces -> single
        result = result.strip()
        
        return result
    
    @classmethod
    def convert_to_plain_text(cls, content: str) -> str:
        """Convert HTML to plain text while preserving structure."""
        result = content
        
        # Convert links to text with URL
        result = cls.LINK_PATTERN.sub(r'\2 (\1)', result)
        
        # Convert images to placeholder
        result = cls.IMG_PATTERN.sub(r'[Image: \1]', result)
        
        # Handle lists
        result = re.sub(r'<li[^>]*>', '• ', result, flags=re.IGNORECASE)
        
        # Handle headings
        for i in range(1, 7):
            result = re.sub(f'<h{i}[^>]*>(.*?)</h{i}>', r'\n\1\n' + '=' * (7-i), result, flags=re.IGNORECASE | re.DOTALL)
        
        # Strip remaining HTML
        result = cls.strip_html(result)
        
        return result
    
    @classmethod
    def process(cls, content: str, mode: HtmlHandlingMode) -> str:
        """Process HTML content based on the specified mode."""
        if mode == HtmlHandlingMode.KEEP:
            return content
        elif mode == HtmlHandlingMode.STRIP:
            return cls.strip_html(content)
        elif mode == HtmlHandlingMode.CONVERT:
            return cls.convert_to_plain_text(content)
        return content
    
    @classmethod
    def extract_media_references(cls, content: str) -> dict:
        """Extract all media file references from content."""
        return {
            'images': cls.IMG_PATTERN.findall(content),
            'audio': cls.AUDIO_PATTERN.findall(content)
        }
    
    @classmethod
    def sanitize_for_display(cls, content: str, max_length: int = 200) -> str:
        """Sanitize content for safe display (preview)."""
        # Strip HTML
        text = cls.strip_html(content)
        
        # Truncate if needed
        if len(text) > max_length:
            text = text[:max_length - 3] + "..."
        
        return text
    
    @classmethod
    def analyze_content(cls, content: str) -> dict:
        """Analyze content for HTML features."""
        return {
            'has_html': cls.contains_html(content),
            'has_images': bool(cls.IMG_PATTERN.search(content)),
            'has_audio': bool(cls.AUDIO_PATTERN.search(content)),
            'has_links': bool(cls.LINK_PATTERN.search(content)),
            'char_count': len(content),
            'char_count_plain': len(cls.strip_html(content))
        }

