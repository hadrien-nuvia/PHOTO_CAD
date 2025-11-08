"""Tests for the learning module."""

import json
import pytest
from pathlib import Path
import tempfile
import os

from src.learning import FeedbackEntry, LearningSystem


class TestFeedbackEntry:
    """Tests for FeedbackEntry class."""
    
    def test_create_feedback_entry(self):
        """Test creating a feedback entry."""
        entry = FeedbackEntry(
            image_path="test.jpg",
            parameters={"snap_angle": 15, "low_threshold": 50},
            rating=5,
            user_notes="Great result!"
        )
        
        assert entry.image_path == "test.jpg"
        assert entry.parameters["snap_angle"] == 15
        assert entry.rating == 5
        assert entry.user_notes == "Great result!"
        assert entry.timestamp is not None
    
    def test_feedback_entry_to_dict(self):
        """Test converting feedback entry to dictionary."""
        entry = FeedbackEntry(
            image_path="test.jpg",
            parameters={"snap_angle": 15},
            rating=4,
            timestamp="2025-01-01T12:00:00"
        )
        
        data = entry.to_dict()
        assert data["image_path"] == "test.jpg"
        assert data["parameters"]["snap_angle"] == 15
        assert data["rating"] == 4
        assert data["timestamp"] == "2025-01-01T12:00:00"
    
    def test_feedback_entry_from_dict(self):
        """Test creating feedback entry from dictionary."""
        data = {
            "image_path": "test.jpg",
            "parameters": {"snap_angle": 20},
            "rating": 3,
            "user_notes": "Needs adjustment",
            "timestamp": "2025-01-01T12:00:00"
        }
        
        entry = FeedbackEntry.from_dict(data)
        assert entry.image_path == "test.jpg"
        assert entry.parameters["snap_angle"] == 20
        assert entry.rating == 3
        assert entry.user_notes == "Needs adjustment"


class TestLearningSystem:
    """Tests for LearningSystem class."""
    
    @pytest.fixture
    def temp_feedback_file(self):
        """Create a temporary feedback file."""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        # Cleanup
        if os.path.exists(path):
            os.unlink(path)
    
    def test_initialize_learning_system(self, temp_feedback_file):
        """Test initializing the learning system."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        assert system.feedback_file == Path(temp_feedback_file)
        assert isinstance(system.feedback_history, list)
    
    def test_add_feedback(self, temp_feedback_file):
        """Test adding feedback."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        
        system.add_feedback(
            image_path="test.jpg",
            parameters={"snap_angle": 15, "low_threshold": 50},
            rating=5,
            user_notes="Perfect!"
        )
        
        assert len(system.feedback_history) == 1
        assert system.feedback_history[0].rating == 5
    
    def test_add_invalid_rating(self, temp_feedback_file):
        """Test adding feedback with invalid rating."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        
        with pytest.raises(ValueError):
            system.add_feedback(
                image_path="test.jpg",
                parameters={},
                rating=6  # Invalid rating
            )
        
        with pytest.raises(ValueError):
            system.add_feedback(
                image_path="test.jpg",
                parameters={},
                rating=0  # Invalid rating
            )
    
    def test_save_and_load_feedback(self, temp_feedback_file):
        """Test saving and loading feedback."""
        system1 = LearningSystem(feedback_file=temp_feedback_file)
        
        system1.add_feedback(
            image_path="test1.jpg",
            parameters={"snap_angle": 15},
            rating=5
        )
        system1.add_feedback(
            image_path="test2.jpg",
            parameters={"snap_angle": 20},
            rating=4
        )
        
        # Create new system instance to test loading
        system2 = LearningSystem(feedback_file=temp_feedback_file)
        
        assert len(system2.feedback_history) == 2
        assert system2.feedback_history[0].image_path == "test1.jpg"
        assert system2.feedback_history[1].rating == 4
    
    def test_get_default_parameters_no_history(self, temp_feedback_file):
        """Test getting parameters with no history."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        
        params = system.get_suggested_parameters()
        
        assert "snap_angle" in params
        assert "low_threshold" in params
        assert params["snap_angle"] == 15  # Default value
    
    def test_get_suggested_parameters_with_good_ratings(self, temp_feedback_file):
        """Test getting suggested parameters from good ratings."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        
        # Add feedback with different parameters
        system.add_feedback(
            image_path="test1.jpg",
            parameters={"snap_angle": 10, "low_threshold": 40},
            rating=5
        )
        system.add_feedback(
            image_path="test2.jpg",
            parameters={"snap_angle": 20, "low_threshold": 60},
            rating=5
        )
        
        params = system.get_suggested_parameters(min_rating=4)
        
        # Should get average of the two
        assert params["snap_angle"] == 15  # (10 + 20) / 2
        assert params["low_threshold"] == 50  # (40 + 60) / 2
    
    def test_get_suggested_parameters_filters_low_ratings(self, temp_feedback_file):
        """Test that low ratings are filtered out."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        
        # Add one good and one bad rating
        system.add_feedback(
            image_path="test1.jpg",
            parameters={"snap_angle": 10},
            rating=5
        )
        system.add_feedback(
            image_path="test2.jpg",
            parameters={"snap_angle": 30},
            rating=2  # Bad rating
        )
        
        params = system.get_suggested_parameters(min_rating=4)
        
        # Should only use the good rating
        assert params["snap_angle"] == 10
    
    def test_get_statistics(self, temp_feedback_file):
        """Test getting statistics."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        
        # Initially empty
        stats = system.get_statistics()
        assert stats["total_feedback"] == 0
        assert stats["average_rating"] == 0
        
        # Add some feedback
        system.add_feedback("test1.jpg", {}, rating=5)
        system.add_feedback("test2.jpg", {}, rating=4)
        system.add_feedback("test3.jpg", {}, rating=5)
        
        stats = system.get_statistics()
        assert stats["total_feedback"] == 3
        assert stats["average_rating"] == pytest.approx(4.666, rel=0.01)
        assert stats["rating_distribution"][5] == 2
        assert stats["rating_distribution"][4] == 1
    
    def test_clear_history(self, temp_feedback_file):
        """Test clearing history."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        
        system.add_feedback("test.jpg", {}, rating=5)
        assert len(system.feedback_history) == 1
        
        system.clear_history()
        assert len(system.feedback_history) == 0
        assert not Path(temp_feedback_file).exists()
    
    def test_similar_image_detection(self, temp_feedback_file):
        """Test similar image detection."""
        system = LearningSystem(feedback_file=temp_feedback_file)
        
        # Add feedback for similar images
        system.add_feedback(
            image_path="orthophoto_001.jpg",
            parameters={"snap_angle": 10},
            rating=5
        )
        system.add_feedback(
            image_path="different_image.jpg",
            parameters={"snap_angle": 30},
            rating=5
        )
        
        # Should prefer similar image parameters
        params = system.get_suggested_parameters(
            image_path="orthophoto_002.jpg",
            min_rating=4
        )
        
        assert params["snap_angle"] == 10
