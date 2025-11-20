"""Tests for data generation and loading."""

import pytest
import json
import tempfile
from pathlib import Path

from src.data.generator import FamilySpeechDataGenerator
from src.data.loader import DataLoader


def test_generator_creates_valid_commands():
    """Test that generator creates valid command structures."""
    generator = FamilySpeechDataGenerator(seed=42)
    
    # Generate a single command
    command = generator.generate_command("timer", "parent")
    
    assert "speech_input" in command
    assert "speaker_context" in command
    assert "intent" in command
    assert "expected_task" in command
    assert isinstance(command["expected_task"], dict)


def test_generator_creates_dataset():
    """Test dataset generation."""
    generator = FamilySpeechDataGenerator(seed=42)
    dataset = generator.generate_dataset(total_samples=50)
    
    assert len(dataset) == 50
    assert all("speech_input" in ex for ex in dataset)


def test_dataset_split():
    """Test dataset splitting."""
    generator = FamilySpeechDataGenerator(seed=42)
    dataset = generator.generate_dataset(total_samples=100)
    splits = generator.split_dataset(dataset, train_ratio=0.6, dev_ratio=0.2)
    
    assert "train" in splits
    assert "dev" in splits
    assert "test" in splits
    
    total = len(splits["train"]) + len(splits["dev"]) + len(splits["test"])
    assert total == 100


def test_data_loader():
    """Test data loader functionality."""
    # Create temporary dataset
    generator = FamilySpeechDataGenerator(seed=42)
    dataset = generator.generate_dataset(total_samples=30)
    splits = generator.split_dataset(dataset)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(splits, f)
        temp_path = f.name
    
    try:
        # Load dataset
        loader = DataLoader(temp_path)
        loader.load()
        
        assert len(loader.get_train()) > 0
        assert len(loader.get_dev()) > 0
        assert len(loader.get_test()) > 0
        
        # Test stats
        stats = loader.get_stats()
        assert "total" in stats
        assert "intents" in stats
        
    finally:
        Path(temp_path).unlink()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
