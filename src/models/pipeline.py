"""
Speech-to-Task pipeline using DSPy.
Chains together components for end-to-end processing.
"""

import dspy
import json
from typing import Dict, Any, Optional

from .signatures import SpeechToIntent, IntentToTask, SpeechToTaskDirect


class SpeechToTaskPipeline(dspy.Module):
    """
    Two-stage pipeline: Speech -> Intent -> Task.
    More modular and easier to optimize.
    """
    
    def __init__(self):
        """Initialize pipeline components."""
        super().__init__()
        self.intent_extractor = dspy.ChainOfThought(SpeechToIntent)
        self.task_generator = dspy.ChainOfThought(IntentToTask)
    
    def forward(self, speech_input: str, speaker_context: str) -> dspy.Prediction:
        """
        Process speech command through pipeline.
        
        Args:
            speech_input: Raw speech transcription
            speaker_context: Speaker context (parent/child/teen)
        
        Returns:
            Prediction with task_json and confidence
        """
        # Step 1: Extract intent
        intent_result = self.intent_extractor(
            speech_input=speech_input,
            speaker_context=speaker_context
        )
        
        # Step 2: Generate task
        task_result = self.task_generator(
            intent=intent_result.intent,
            speech_input=speech_input,
            speaker_context=speaker_context
        )
        
        # Combine results
        return dspy.Prediction(
            intent=intent_result.intent,
            confidence=intent_result.confidence,
            task_json=task_result.task_json
        )


class DirectSpeechToTaskPipeline(dspy.Module):
    """
    Single-stage pipeline: Speech -> Task directly.
    Simpler but potentially less accurate.
    """
    
    def __init__(self):
        """Initialize pipeline."""
        super().__init__()
        self.task_extractor = dspy.ChainOfThought(SpeechToTaskDirect)
    
    def forward(self, speech_input: str, speaker_context: str) -> dspy.Prediction:
        """
        Process speech command directly to task.
        
        Args:
            speech_input: Raw speech transcription
            speaker_context: Speaker context (parent/child/teen)
        
        Returns:
            Prediction with task_json and confidence
        """
        result = self.task_extractor(
            speech_input=speech_input,
            speaker_context=speaker_context
        )
        
        return result


class SimplePredictPipeline(dspy.Module):
    """
    Baseline pipeline using simple Predict instead of ChainOfThought.
    Used as baseline for comparison.
    """
    
    def __init__(self):
        """Initialize baseline pipeline."""
        super().__init__()
        self.task_extractor = dspy.Predict(SpeechToTaskDirect)
    
    def forward(self, speech_input: str, speaker_context: str) -> dspy.Prediction:
        """Process speech command."""
        result = self.task_extractor(
            speech_input=speech_input,
            speaker_context=speaker_context
        )
        
        return result


def extract_task_from_prediction(prediction: dspy.Prediction) -> Optional[Dict[str, Any]]:
    """
    Extract task dictionary from prediction.
    
    Args:
        prediction: DSPy prediction object
    
    Returns:
        Task dictionary or None if parsing fails
    """
    try:
        task_json = prediction.task_json
        
        # If it's already a dict, return it
        if isinstance(task_json, dict):
            return task_json
        
        # Try to parse as JSON
        if isinstance(task_json, str):
            # Clean up the string
            task_json = task_json.strip()
            
            # Handle code blocks
            if task_json.startswith("```"):
                lines = task_json.split('\n')
                task_json = '\n'.join(lines[1:-1]) if len(lines) > 2 else task_json
            
            # Parse JSON
            return json.loads(task_json)
        
        return None
    
    except (json.JSONDecodeError, AttributeError, KeyError) as e:
        print(f"Warning: Failed to parse task JSON: {e}")
        return None


def format_task_output(prediction: dspy.Prediction) -> str:
    """
    Format prediction output for display.
    
    Args:
        prediction: DSPy prediction object
    
    Returns:
        Formatted string
    """
    task = extract_task_from_prediction(prediction)
    
    if task is None:
        return f"Error: Could not parse task\nRaw output: {prediction.task_json}"
    
    output = []
    output.append(f"Action: {task.get('action', 'unknown')}")
    output.append(f"Priority: {task.get('priority', 'unknown')}")
    
    params = task.get('parameters', {})
    if params:
        output.append("Parameters:")
        for key, value in params.items():
            output.append(f"  {key}: {value}")
    
    if hasattr(prediction, 'confidence'):
        output.append(f"Confidence: {prediction.confidence}")
    
    return '\n'.join(output)


def main():
    """Test pipeline with example."""
    from ..models.simulated_lm import DummyLM
    
    # Configure DSPy with simulated LM
    lm = DummyLM()
    dspy.settings.configure(lm=lm)
    
    # Create pipeline
    pipeline = SpeechToTaskPipeline()
    
    # Test example
    speech = "Set timer for 20 minutes"
    speaker = "parent"
    
    print(f"Input: {speech}")
    print(f"Speaker: {speaker}")
    print()
    
    # Run pipeline
    result = pipeline(speech_input=speech, speaker_context=speaker)
    
    print("Output:")
    print(format_task_output(result))


if __name__ == "__main__":
    main()
