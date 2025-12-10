
import re
from typing import Optional, Tuple, List


class AnkiHeaderParser:
    """
    Parse Anki-specific header lines in TXT exports.

    Anki TXT files can contain headers like:
    - #separator:tab
    - #separator:comma
    - #html:true
    - #html:false
    - #deck column:1
    - #notetype column:2
    - #tags column:3
    """

    # Regex patterns for Anki headers
    SEPARATOR_PATTERN = re.compile(r'^#separator[:\s]+(\w+)', re.IGNORECASE)
    HTML_PATTERN = re.compile(r'^#html[:\s]+(true|false)', re.IGNORECASE)
    DECK_COLUMN_PATTERN = re.compile(r'^#deck\s+column[:\s]+(\d+)', re.IGNORECASE)
    NOTETYPE_COLUMN_PATTERN = re.compile(r'^#notetype\s+column[:\s]+(\d+)', re.IGNORECASE)
    TAGS_COLUMN_PATTERN = re.compile(r'^#tags\s+column[:\s]+(\d+)', re.IGNORECASE)
    GUID_COLUMN_PATTERN = re.compile(r'^#guid\s+column[:\s]+(\d+)', re.IGNORECASE)

    # Separator mappings
    SEPARATOR_MAP = {
        'tab': '\t',
        'comma': ',',
        'semicolon': ';',
        'space': ' ',
        'pipe': '|'
    }

    @classmethod
    def parse_separator(cls, line: str) -> Optional[str]:
        match = cls.SEPARATOR_PATTERN.match(line.strip())
        if match:
            sep_name = match.group(1).lower()
            return cls.SEPARATOR_MAP.get(sep_name, '\t')
        return None

    @classmethod
    def parse_html_setting(cls, line: str) -> Optional[bool]:

        match = cls.HTML_PATTERN.match(line.strip())
        if match:
            return match.group(1).lower() == 'true'
        return None

    @classmethod
    def parse_column_index(cls, line: str) -> Optional[Tuple[str, int]]:
        patterns = [
            ('deck', cls.DECK_COLUMN_PATTERN),
            ('notetype', cls.NOTETYPE_COLUMN_PATTERN),
            ('tags', cls.TAGS_COLUMN_PATTERN),
            ('guid', cls.GUID_COLUMN_PATTERN)
        ]

        for col_type, pattern in patterns:
            match = pattern.match(line.strip())
            if match:
                return (col_type, int(match.group(1)))
        return None

    @classmethod
    def is_header_line(cls, line: str) -> bool:
        return line.strip().startswith('#')

    @classmethod
    def parse_all_headers(cls, lines: List[str]) -> dict:
        settings = {
            'separator': '\t',  # Default
            'html': False,
            'columns': {}
        }

        for line in lines:
            if not cls.is_header_line(line):
                break  # Headers are at the top

            # Try to parse separator
            sep = cls.parse_separator(line)
            if sep is not None:
                settings['separator'] = sep
                continue

            # Try to parse HTML setting
            html = cls.parse_html_setting(line)
            if html is not None:
                settings['html'] = html
                continue

            # Try to parse column index
            col_info = cls.parse_column_index(line)
            if col_info is not None:
                col_type, col_index = col_info
                settings['columns'][col_type] = col_index

        return settings


class CardValidator:
    # Pattern to detect cloze deletions like {{c1::answer}} or {{c1::answer::hint}}
    CLOZE_PATTERN = re.compile(r'\{\{c(\d+)::(.+?)(?:::(.+?))?\}\}', re.DOTALL)

    # Pattern to detect HTML tags
    HTML_PATTERN = re.compile(r'<[^>]+>')

    # Pattern to detect image references
    IMAGE_PATTERN = re.compile(r'<img[^>]+src=["\']([^"\']+)["\']', re.IGNORECASE)

    # Pattern to detect sound references [sound:filename.mp3]
    SOUND_PATTERN = re.compile(r'\[sound:([^\]]+)\]')

    # Minimum content length for a valid card side
    MIN_CONTENT_LENGTH = 1

    # Maximum content length (prevent memory issues)
    MAX_CONTENT_LENGTH = 50000

    @classmethod
    def validate_content(cls, content: str) -> Tuple[bool, Optional[str]]:

        if not content or not content.strip():
            return False, "Content is empty"

        stripped = content.strip()

        if len(stripped) < cls.MIN_CONTENT_LENGTH:
            return False, f"Content too short (min {cls.MIN_CONTENT_LENGTH} chars)"

        if len(stripped) > cls.MAX_CONTENT_LENGTH:
            return False, f"Content too long (max {cls.MAX_CONTENT_LENGTH} chars)"

        return True, None

    @classmethod
    def is_cloze_card(cls, content: str) -> bool:

        return bool(cls.CLOZE_PATTERN.search(content))

    @classmethod
    def extract_cloze_answers(cls, content: str) -> List[Tuple[int, str, Optional[str]]]:

        results = []
        for match in cls.CLOZE_PATTERN.finditer(content):
            cloze_num = int(match.group(1))
            answer = match.group(2)
            hint = match.group(3)  # May be None
            results.append((cloze_num, answer, hint))
        return results

    @classmethod
    def contains_html(cls, content: str) -> bool:

        return bool(cls.HTML_PATTERN.search(content))

    @classmethod
    def strip_html(cls, content: str) -> str:

        # Also decode common HTML entities
        result = cls.HTML_PATTERN.sub('', content)
        # Handle common entities
        result = result.replace('&nbsp;', ' ')
        result = result.replace('&amp;', '&')
        result = result.replace('&lt;', '<')
        result = result.replace('&gt;', '>')
        result = result.replace('&quot;', '"')
        result = result.replace('<br>', '\n')
        result = result.replace('<br/>', '\n')
        result = result.replace('<br />', '\n')
        return result

    @classmethod
    def extract_media_references(cls, content: str) -> dict:

        return {
            'images': cls.IMAGE_PATTERN.findall(content),
            'sounds': cls.SOUND_PATTERN.findall(content)
        }


class TagParser:

    # Valid tag pattern: alphanumeric, underscores, hyphens, colons (for hierarchy)
    TAG_PATTERN = re.compile(r'[\w:_-]+')

    # Hierarchical tag pattern (e.g., "science::physics::quantum")
    HIERARCHICAL_TAG_PATTERN = re.compile(r'^[\w_-]+(::[\w_-]+)*$')

    @classmethod
    def parse_tags(cls, tag_string: str) -> List[str]:

        if not tag_string:
            return []

        # Split by spaces and filter valid tags
        tags = cls.TAG_PATTERN.findall(tag_string)
        return [tag.strip() for tag in tags if tag.strip()]

    @classmethod
    def validate_tag(cls, tag: str) -> bool:

        return bool(cls.TAG_PATTERN.fullmatch(tag.strip()))

    @classmethod
    def is_hierarchical(cls, tag: str) -> bool:

        return '::' in tag

    @classmethod
    def split_hierarchical_tag(cls, tag: str) -> List[str]:

        return tag.split('::')

    @classmethod
    def normalize_tags(cls, tags: List[str]) -> List[str]:

        normalized = set(tag.lower().strip() for tag in tags if tag.strip())
        return sorted(normalized)