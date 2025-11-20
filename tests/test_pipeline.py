"""Tests for pipeline components."""

import pytest
import dspy

from src.models.simulated_lm import SimulatedLM, DummyLM
from src.models.pipeline import (
    DirectSpeechToTaskPipeline, 
    extract_task_from_prediction
)


def test_simulated_lm():
    """Test simulated LM responses."""
    lm = SimulatedLM()
    
    prompt = "Extract intent from: Set timer for 20 minutes"
    response = lm(prompt)
    
    assert isinstance(response, list)
    assert len(response) > 0
    assert isinstance(response[0], str)


def test_pipeline_execution():
    """Test that pipeline executes without errors."""
    # Configure DSPy
    lm = DummyLM()
    dspy.settings.configure(lm=lm)
    
    # Create pipeline
    pipeline = DirectSpeechToTaskPipeline()
    
    # Test execution
    result = pipeline(
        speech_input="Set timer for 20 minutes",
        speaker_context="parent"
    )
    
    assert result is not None
    assert hasattr(result, "task_json")


def test_task_extraction():
    """Test task extraction from predictions."""
    import json
    
    # Test with valid JSON
    task_dict = {"action": "set_timer", "parameters": {"duration": "20"}}
    prediction = dspy.Prediction(task_json=json.dumps(task_dict))
    
    extracted = extract_task_from_prediction(prediction)
    assert extracted is not None
    assert extracted["action"] == "set_timer"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
