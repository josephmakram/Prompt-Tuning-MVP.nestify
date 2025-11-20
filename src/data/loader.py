"""
Data loader for family speech command dataset.
Loads and prepares data for training and evaluation.
"""

import json
from typing import List, Dict, Any, Optional
from pathlib import Path


class DataLoader:
    """Loads and manages family speech command dataset."""
    
    def __init__(self, data_path: str):
        """
        Initialize data loader.
        
        Args:
            data_path: Path to JSON file containing dataset
        """
        self.data_path = Path(data_path)
        self.data = None
        self.train = None
        self.dev = None
        self.test = None
    
    def load(self) -> Dict[str, List[Dict[str, Any]]]:
        """Load dataset from file."""
        if not self.data_path.exists():
            raise FileNotFoundError(f"Dataset not found at {self.data_path}")
        
        with open(self.data_path, 'r') as f:
            self.data = json.load(f)
        
        self.train = self.data.get("train", [])
        self.dev = self.data.get("dev", [])
        self.test = self.data.get("test", [])
        
        print(f"Loaded dataset from {self.data_path}")
        print(f"  Train: {len(self.train)} samples")
        print(f"  Dev: {len(self.dev)} samples")
        print(f"  Test: {len(self.test)} samples")
        
        return self.data
    
    def get_train(self) -> List[Dict[str, Any]]:
        """Get training set."""
        if self.train is None:
            self.load()
        return self.train
    
    def get_dev(self) -> List[Dict[str, Any]]:
        """Get development set."""
        if self.dev is None:
            self.load()
        return self.dev
    
    def get_test(self) -> List[Dict[str, Any]]:
        """Get test set."""
        if self.test is None:
            self.load()
        return self.test
    
    def get_examples(self, split: str = "train", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get examples from a specific split.
        
        Args:
            split: Which split to get ('train', 'dev', or 'test')
            limit: Maximum number of examples to return
        
        Returns:
            List of examples
        """
        if split == "train":
            examples = self.get_train()
        elif split == "dev":
            examples = self.get_dev()
        elif split == "test":
            examples = self.get_test()
        else:
            raise ValueError(f"Unknown split: {split}")
        
        if limit:
            return examples[:limit]
        return examples
    
    def get_stats(self) -> Dict[str, Any]:
        """Get dataset statistics."""
        if self.data is None:
            self.load()
        
        stats = {
            "total": len(self.train) + len(self.dev) + len(self.test),
            "train": len(self.train),
            "dev": len(self.dev),
            "test": len(self.test),
        }
        
        # Count intents
        intents = {}
        for example in self.train + self.dev + self.test:
            intent = example.get("intent", "unknown")
            intents[intent] = intents.get(intent, 0) + 1
        
        stats["intents"] = intents
        
        # Count speakers
        speakers = {}
        for example in self.train + self.dev + self.test:
            speaker = example.get("speaker_context", "unknown")
            speakers[speaker] = speakers.get(speaker, 0) + 1
        
        stats["speakers"] = speakers
        
        return stats
    
    def print_stats(self):
        """Print dataset statistics."""
        stats = self.get_stats()
        
        print("\n=== Dataset Statistics ===")
        print(f"Total samples: {stats['total']}")
        print(f"Train: {stats['train']}")
        print(f"Dev: {stats['dev']}")
        print(f"Test: {stats['test']}")
        
        print("\nIntent distribution:")
        for intent, count in sorted(stats['intents'].items()):
            print(f"  {intent}: {count}")
        
        print("\nSpeaker distribution:")
        for speaker, count in sorted(stats['speakers'].items()):
            print(f"  {speaker}: {count}")


def main():
    """Load and display dataset statistics."""
    loader = DataLoader("data/simulated_commands.json")
    loader.load()
    loader.print_stats()


if __name__ == "__main__":
    main()
