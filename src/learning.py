"""Learning module for parameter optimization based on user feedback."""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import numpy as np


class FeedbackEntry:
    """Represents a single feedback entry."""

    def __init__(
        self,
        image_path: str,
        parameters: Dict[str, Any],
        rating: int,
        user_notes: Optional[str] = None,
        timestamp: Optional[str] = None,
    ):
        """
        Initialize a feedback entry.

        Args:
            image_path: Path to the image that was processed
            parameters: Dictionary of parameters used
            rating: User rating (1-5 stars)
            user_notes: Optional user notes about the result
            timestamp: ISO format timestamp (auto-generated if not provided)
        """
        self.image_path = image_path
        self.parameters = parameters
        self.rating = rating
        self.user_notes = user_notes
        self.timestamp = timestamp or datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "image_path": self.image_path,
            "parameters": self.parameters,
            "rating": self.rating,
            "user_notes": self.user_notes,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FeedbackEntry":
        """Create from dictionary."""
        return cls(
            image_path=data["image_path"],
            parameters=data["parameters"],
            rating=data["rating"],
            user_notes=data.get("user_notes"),
            timestamp=data.get("timestamp"),
        )


class LearningSystem:
    """System for learning optimal parameters from user feedback."""

    def __init__(self, feedback_file: str = "feedback_history.json"):
        """
        Initialize the learning system.

        Args:
            feedback_file: Path to the feedback history file
        """
        self.feedback_file = Path(feedback_file)
        self.feedback_history: List[FeedbackEntry] = []
        self.load_feedback()

    def load_feedback(self):
        """Load feedback history from file."""
        if self.feedback_file.exists():
            try:
                with open(self.feedback_file, "r") as f:
                    data = json.load(f)
                    self.feedback_history = [FeedbackEntry.from_dict(entry) for entry in data]
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Warning: Could not load feedback history: {e}")
                self.feedback_history = []
        else:
            self.feedback_history = []

    def save_feedback(self):
        """Save feedback history to file."""
        # Create directory if it doesn't exist
        self.feedback_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.feedback_file, "w") as f:
            data = [entry.to_dict() for entry in self.feedback_history]
            json.dump(data, f, indent=2)

    def add_feedback(
        self,
        image_path: str,
        parameters: Dict[str, Any],
        rating: int,
        user_notes: Optional[str] = None,
    ):
        """
        Add user feedback to the history.

        Args:
            image_path: Path to the processed image
            parameters: Parameters used for processing
            rating: User rating (1-5)
            user_notes: Optional notes about the result

        Raises:
            ValueError: If rating is not between 1 and 5
        """
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5")

        entry = FeedbackEntry(image_path, parameters, rating, user_notes)
        self.feedback_history.append(entry)
        self.save_feedback()

    def get_suggested_parameters(
        self, image_path: Optional[str] = None, min_rating: int = 4
    ) -> Dict[str, Any]:
        """
        Get suggested parameters based on historical feedback.

        Args:
            image_path: Optional image path to get suggestions for similar images
            min_rating: Minimum rating to consider (default: 4)

        Returns:
            Dictionary of suggested parameters
        """
        if not self.feedback_history:
            return self._get_default_parameters()

        # Filter by rating
        good_results = [entry for entry in self.feedback_history if entry.rating >= min_rating]

        if not good_results:
            return self._get_default_parameters()

        # If image path provided, try to find similar images
        if image_path:
            # For now, use exact matches or similar filenames
            # In future, could use image similarity
            similar_results = [
                entry
                for entry in good_results
                if self._is_similar_image(entry.image_path, image_path)
            ]
            if similar_results:
                good_results = similar_results

        # Calculate average of each parameter from good results
        return self._average_parameters(good_results)

    def _is_similar_image(self, path1: str, path2: str) -> bool:
        """
        Check if two images are similar (basic implementation).

        Args:
            path1: First image path
            path2: Second image path

        Returns:
            True if images are considered similar
        """
        # Simple implementation: check if base names share common prefix
        name1 = Path(path1).stem.lower()
        name2 = Path(path2).stem.lower()

        # Extract common prefix (e.g., "orthophoto" from "orthophoto_001")
        # Split by common separators
        import re

        parts1 = re.split(r"[_\-\s.]", name1)
        parts2 = re.split(r"[_\-\s.]", name2)

        # If they share at least one non-trivial common part at the beginning
        if parts1 and parts2:
            # Check if first significant part matches (at least 4 chars)
            if len(parts1[0]) >= 4 and len(parts2[0]) >= 4:
                return parts1[0] == parts2[0]

        # Fallback to exact match
        return name1 == name2

    def _average_parameters(self, entries: List[FeedbackEntry]) -> Dict[str, Any]:
        """
        Calculate average parameters from feedback entries.

        Args:
            entries: List of feedback entries

        Returns:
            Dictionary with averaged parameters
        """
        if not entries:
            return self._get_default_parameters()

        # Collect all parameter values
        param_values: Dict[str, List] = {}
        for entry in entries:
            for key, value in entry.parameters.items():
                if key not in param_values:
                    param_values[key] = []
                if isinstance(value, (int, float)):
                    param_values[key].append(value)

        # Calculate averages
        averaged = {}
        for key, values in param_values.items():
            if values:
                averaged[key] = int(np.mean(values))

        # Fill in any missing defaults
        defaults = self._get_default_parameters()
        for key, value in defaults.items():
            if key not in averaged:
                averaged[key] = value

        return averaged

    def _get_default_parameters(self) -> Dict[str, Any]:
        """Get default parameters."""
        return {
            "snap_angle": 15,
            "low_threshold": 50,
            "high_threshold": 150,
            "line_threshold": 100,
            "min_line_length": 100,
            "max_line_gap": 10,
        }

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about the feedback history.

        Returns:
            Dictionary with statistics
        """
        if not self.feedback_history:
            return {
                "total_feedback": 0,
                "average_rating": 0,
                "rating_distribution": {},
                "most_recent": None,
            }

        ratings = [entry.rating for entry in self.feedback_history]
        rating_dist = {i: ratings.count(i) for i in range(1, 6)}

        return {
            "total_feedback": len(self.feedback_history),
            "average_rating": sum(ratings) / len(ratings),
            "rating_distribution": rating_dist,
            "most_recent": self.feedback_history[-1].timestamp if self.feedback_history else None,
        }

    def clear_history(self):
        """Clear all feedback history."""
        self.feedback_history = []
        if self.feedback_file.exists():
            self.feedback_file.unlink()
