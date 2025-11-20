"""
Data generator for simulated family speech commands.
Generates realistic training/dev/test data for prompt optimization.
"""

import json
import random
from typing import List, Dict, Any
from pathlib import Path


class FamilySpeechDataGenerator:
    """Generates simulated family speech command dataset."""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed for reproducibility."""
        random.seed(seed)
        self.seed = seed
        
        # Define task templates by category
        self.templates = {
            "timer": {
                "parent": [
                    "Set timer for {duration} minutes",
                    "Start a {duration} minute timer",
                    "Timer for {duration} minutes please",
                    "Can you set a timer for {duration} minutes",
                    "Set {duration} minute timer",
                ],
                "child": [
                    "Timer {duration} minutes",
                    "Start timer {duration}",
                    "Can I have a timer for {duration} minutes",
                ],
                "intents": ["set_timer"],
                "params": {"duration": [5, 10, 15, 20, 25, 30, 45, 60]},
                "priority": "medium"
            },
            "reminder": {
                "parent": [
                    "Remind me to {task} at {time}",
                    "Set a reminder for {task} at {time}",
                    "Don't let me forget to {task} at {time}",
                    "Reminder to {task} {time}",
                    "Can you remind me to {task} at {time}",
                ],
                "child": [
                    "Remind me {task}",
                    "Don't forget {task}",
                ],
                "intents": ["set_reminder"],
                "params": {
                    "task": ["pick up kids", "call dentist", "take medication", "feed the dog", 
                            "start dinner", "check homework", "water plants"],
                    "time": ["3pm", "4:30", "tomorrow morning", "in 2 hours", "6 o'clock"]
                },
                "priority": "high"
            },
            "shopping": {
                "parent": [
                    "Add {item} to shopping list",
                    "Put {item} on the shopping list",
                    "We need {item}",
                    "Add {item} to the list",
                    "Shopping list add {item}",
                ],
                "child": [
                    "We're out of {item}",
                    "Can we get {item}",
                ],
                "intents": ["add_to_shopping_list"],
                "params": {
                    "item": ["milk", "eggs", "bread", "cereal", "juice", "apples", 
                            "chicken", "pasta", "cheese", "yogurt"]
                },
                "priority": "low"
            },
            "smart_home": {
                "parent": [
                    "Turn on {device}",
                    "Turn off {device}",
                    "Switch on the {device}",
                    "Can you turn on {device}",
                    "{device} on",
                    "{device} off",
                ],
                "child": [
                    "Turn on {device}",
                    "Lights on in {device}",
                ],
                "intents": ["control_device"],
                "params": {
                    "device": ["living room lights", "bedroom lights", "kitchen lights", 
                              "thermostat", "TV", "fan"]
                },
                "priority": "medium"
            },
            "information": {
                "parent": [
                    "What's the weather today",
                    "What's the forecast",
                    "What time is it",
                    "What's today's date",
                    "What day is it",
                ],
                "child": [
                    "What's the weather",
                    "Is it going to rain",
                    "What time is it",
                    "When is my birthday",
                ],
                "intents": ["get_information"],
                "params": {},
                "priority": "low"
            },
            "entertainment": {
                "parent": [
                    "Play {content}",
                    "Put on {content}",
                    "Start playing {content}",
                ],
                "child": [
                    "Play my bedtime story",
                    "Play {content}",
                    "Can I watch {content}",
                    "I want to hear {content}",
                ],
                "intents": ["play_media"],
                "params": {
                    "content": ["music", "bedtime story", "cartoons", "the news", 
                               "my playlist", "kids songs"]
                },
                "priority": "low"
            },
            "calendar": {
                "parent": [
                    "Add {event} to calendar for {time}",
                    "Schedule {event} at {time}",
                    "Put {event} on the calendar {time}",
                ],
                "intents": ["add_calendar_event"],
                "params": {
                    "event": ["dentist appointment", "soccer practice", "parent teacher meeting",
                             "birthday party", "doctor visit"],
                    "time": ["tomorrow at 3pm", "Friday morning", "next week", "this weekend"]
                },
                "priority": "high"
            },
            "help": {
                "child": [
                    "Help with {subject} homework",
                    "I need help with {subject}",
                    "Can you help me with {subject}",
                    "What's {question}",
                ],
                "intents": ["request_help"],
                "params": {
                    "subject": ["math", "reading", "science", "spelling"],
                    "question": ["5 times 7", "how to spell beautiful", "the capital of France"]
                },
                "priority": "medium"
            },
        }
    
    def generate_command(self, category: str, speaker: str) -> Dict[str, Any]:
        """Generate a single command for a given category and speaker."""
        template_data = self.templates[category]
        
        # Get templates for this speaker (fallback to parent if not available)
        speaker_templates = template_data.get(speaker, template_data.get("parent", []))
        if not speaker_templates:
            speaker_templates = template_data["parent"]
        
        template = random.choice(speaker_templates)
        
        # Fill in parameters
        params = {}
        speech_input = template
        for param_name, param_values in template_data["params"].items():
            if f"{{{param_name}}}" in template:
                value = random.choice(param_values)
                params[param_name] = value
                speech_input = speech_input.replace(f"{{{param_name}}}", str(value))
        
        # Determine intent
        intent = random.choice(template_data["intents"])
        
        # Add variations (incomplete sentences, filler words, etc.)
        if random.random() < 0.2:  # 20% chance of variation
            fillers = ["um", "uh", "please", "now"]
            speech_input = f"{random.choice(fillers)} {speech_input}"
        
        return {
            "speech_input": speech_input,
            "speaker_context": speaker,
            "intent": intent,
            "expected_task": {
                "action": intent,
                "parameters": params,
                "priority": template_data["priority"],
                "category": category
            }
        }
    
    def generate_dataset(self, total_samples: int = 100) -> List[Dict[str, Any]]:
        """Generate complete dataset with diverse examples."""
        dataset = []
        categories = list(self.templates.keys())
        speakers = ["parent", "child", "teen"]
        
        for _ in range(total_samples):
            category = random.choice(categories)
            speaker = random.choice(speakers)
            
            # Teen uses similar patterns to parent
            if speaker == "teen":
                speaker_for_template = random.choice(["parent", "child"])
            else:
                speaker_for_template = speaker
            
            command = self.generate_command(category, speaker_for_template)
            command["speaker_context"] = speaker  # Keep original speaker
            dataset.append(command)
        
        return dataset
    
    def split_dataset(self, dataset: List[Dict[str, Any]], 
                     train_ratio: float = 0.6, 
                     dev_ratio: float = 0.2) -> Dict[str, List[Dict[str, Any]]]:
        """Split dataset into train/dev/test sets."""
        random.shuffle(dataset)
        
        n = len(dataset)
        train_size = int(n * train_ratio)
        dev_size = int(n * dev_ratio)
        
        return {
            "train": dataset[:train_size],
            "dev": dataset[train_size:train_size + dev_size],
            "test": dataset[train_size + dev_size:]
        }
    
    def save_dataset(self, dataset: Dict[str, List[Dict[str, Any]]], 
                    output_path: str):
        """Save dataset to JSON file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(dataset, f, indent=2)
        
        print(f"Dataset saved to {output_path}")
        print(f"  Train: {len(dataset['train'])} samples")
        print(f"  Dev: {len(dataset['dev'])} samples")
        print(f"  Test: {len(dataset['test'])} samples")


def main():
    """Generate and save dataset."""
    generator = FamilySpeechDataGenerator(seed=42)
    dataset = generator.generate_dataset(total_samples=100)
    splits = generator.split_dataset(dataset)
    generator.save_dataset(splits, "data/simulated_commands.json")


if __name__ == "__main__":
    main()
