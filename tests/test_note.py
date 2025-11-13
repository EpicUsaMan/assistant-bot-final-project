"""Tests for Note model."""

import pytest
from src.models.note import Note
from src.models.tags import Tags


class TestNoteInitialization:
    """Tests for Note initialization."""
    
    def test_create_note_with_name_only(self):
        """Test creating a note with only a name."""
        note = Note("Meeting Notes")
        assert note.name == "Meeting Notes"
        assert note.content == ""
        assert isinstance(note.tags, Tags)
        assert note.tags_list() == []
    
    def test_create_note_with_name_and_content(self):
        """Test creating a note with name and content."""
        note = Note("Ideas", "This is my idea")
        assert note.name == "Ideas"
        assert note.content == "This is my idea"
        assert note.tags_list() == []
    
    def test_create_note_strips_whitespace_from_name(self):
        """Test that note name is stripped of whitespace."""
        note = Note("  Project Notes  ")
        assert note.name == "Project Notes"
    
    def test_create_note_with_empty_name_raises_error(self):
        """Test that creating note with empty name raises ValueError."""
        with pytest.raises(ValueError, match="Note name cannot be empty"):
            Note("")
    
    def test_create_note_with_whitespace_only_name_raises_error(self):
        """Test that creating note with whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="Note name cannot be empty"):
            Note("   ")


class TestNoteContentManagement:
    """Tests for note content management."""
    
    def test_update_content(self):
        """Test updating note content."""
        note = Note("Todo", "Initial content")
        note.update_content("Updated content")
        assert note.content == "Updated content"
    
    def test_update_content_to_empty_string(self):
        """Test updating content to empty string."""
        note = Note("Todo", "Some content")
        note.update_content("")
        assert note.content == ""


class TestNoteTagManagement:
    """Tests for note tag management."""
    
    def test_add_tag(self):
        """Test adding a tag to note."""
        note = Note("Ideas")
        note.add_tag("important")
        assert "important" in note.tags_list()
    
    def test_add_multiple_tags(self):
        """Test adding multiple tags."""
        note = Note("Ideas")
        note.add_tag("important")
        note.add_tag("work")
        note.add_tag("urgent")
        tags = note.tags_list()
        assert "important" in tags
        assert "work" in tags
        assert "urgent" in tags
    
    def test_add_tag_normalizes_to_lowercase(self):
        """Test that tags are normalized to lowercase."""
        note = Note("Ideas")
        note.add_tag("IMPORTANT")
        assert "important" in note.tags_list()
        assert "IMPORTANT" not in note.tags_list()
    
    def test_add_invalid_tag_raises_error(self):
        """Test that adding invalid tag raises ValueError."""
        note = Note("Ideas")
        with pytest.raises(ValueError, match="Invalid tag"):
            note.add_tag("")
    
    def test_remove_tag(self):
        """Test removing a tag from note."""
        note = Note("Ideas")
        note.add_tag("important")
        note.add_tag("work")
        note.remove_tag("important")
        assert "important" not in note.tags_list()
        assert "work" in note.tags_list()
    
    def test_remove_nonexistent_tag(self):
        """Test removing a tag that doesn't exist (should not raise error)."""
        note = Note("Ideas")
        note.add_tag("work")
        note.remove_tag("nonexistent")
        assert "work" in note.tags_list()
    
    def test_clear_tags(self):
        """Test clearing all tags from note."""
        note = Note("Ideas")
        note.add_tag("important")
        note.add_tag("work")
        note.add_tag("urgent")
        note.clear_tags()
        assert note.tags_list() == []
    
    def test_tags_list(self):
        """Test getting list of all tags."""
        note = Note("Ideas")
        note.add_tag("important")
        note.add_tag("work")
        tags = note.tags_list()
        assert isinstance(tags, list)
        assert len(tags) == 2


class TestNoteTagQueries:
    """Tests for note tag query methods."""
    
    def test_has_tags_all_with_all_tags_present(self):
        """Test has_tags_all returns True when all tags are present."""
        note = Note("Ideas")
        note.add_tag("important")
        note.add_tag("work")
        note.add_tag("urgent")
        assert note.has_tags_all(["important", "work"]) is True
    
    def test_has_tags_all_with_missing_tag(self):
        """Test has_tags_all returns False when a tag is missing."""
        note = Note("Ideas")
        note.add_tag("important")
        note.add_tag("work")
        assert note.has_tags_all(["important", "urgent"]) is False
    
    def test_has_tags_all_with_empty_list(self):
        """Test has_tags_all with empty list returns True."""
        note = Note("Ideas")
        note.add_tag("important")
        assert note.has_tags_all([]) is True
    
    def test_has_tags_any_with_one_tag_present(self):
        """Test has_tags_any returns True when at least one tag is present."""
        note = Note("Ideas")
        note.add_tag("important")
        note.add_tag("work")
        assert note.has_tags_any(["work", "urgent"]) is True
    
    def test_has_tags_any_with_no_tags_present(self):
        """Test has_tags_any returns False when no tags are present."""
        note = Note("Ideas")
        note.add_tag("important")
        assert note.has_tags_any(["urgent", "personal"]) is False
    
    def test_has_tags_any_with_empty_list(self):
        """Test has_tags_any with empty list returns False."""
        note = Note("Ideas")
        note.add_tag("important")
        assert note.has_tags_any([]) is False


class TestNoteStringRepresentation:
    """Tests for note string representations."""
    
    def test_str_with_short_content_and_no_tags(self):
        """Test string representation with short content and no tags."""
        note = Note("Todo", "Buy milk")
        result = str(note)
        assert "Todo" in result
        assert "Buy milk" in result
    
    def test_str_with_long_content(self):
        """Test string representation truncates long content."""
        note = Note("Todo", "A" * 100)
        result = str(note)
        assert "..." in result
        assert len(result) < 200
    
    def test_str_with_tags(self):
        """Test string representation includes tags."""
        note = Note("Todo", "Buy milk")
        note.add_tag("important")
        note.add_tag("urgent")
        result = str(note)
        assert "tags:" in result
        assert "important" in result or "urgent" in result
    
    def test_repr(self):
        """Test repr representation."""
        note = Note("Todo", "Buy milk")
        result = repr(note)
        assert "Note" in result
        assert "Todo" in result


class TestNoteEquality:
    """Tests for note equality comparison."""
    
    def test_notes_with_same_name_are_equal(self):
        """Test that notes with same name are equal."""
        note1 = Note("Todo", "Content 1")
        note2 = Note("Todo", "Content 2")
        assert note1 == note2
    
    def test_notes_with_different_names_are_not_equal(self):
        """Test that notes with different names are not equal."""
        note1 = Note("Todo", "Same content")
        note2 = Note("Ideas", "Same content")
        assert note1 != note2
    
    def test_note_equality_with_non_note_object(self):
        """Test that comparing note with non-note returns NotImplemented."""
        note = Note("Todo")
        assert (note == "not a note") is False


class TestNoteBackwardCompatibility:
    """Tests for backward compatibility with unpickling."""
    
    def test_setstate_adds_missing_tags(self):
        """Test that __setstate__ adds missing tags attribute."""
        note = Note("Todo", "Content")
        state = {"value": "Todo", "content": "Content"}
        note.__setstate__(state)
        assert hasattr(note, "tags")
        assert isinstance(note.tags, Tags)
    
    def test_setstate_adds_missing_name(self):
        """Test that __setstate__ adds missing name attribute from value."""
        note = Note("Todo", "Content")
        state = {"value": "Todo", "content": "Content", "tags": Tags()}
        note.__setstate__(state)
        assert hasattr(note, "name")
        assert note.name == "Todo"
    
    def test_setstate_preserves_existing_attributes(self):
        """Test that __setstate__ preserves existing attributes."""
        note = Note("Todo", "Content")
        tags = Tags()
        tags.add("important")
        state = {"value": "Todo", "name": "Todo", "content": "Updated", "tags": tags}
        note.__setstate__(state)
        assert note.name == "Todo"
        assert note.content == "Updated"
        assert "important" in note.tags_list()


