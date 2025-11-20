"""Tests for optimization components."""

import pytest
import json
import dspy

from src.optimization.metrics import (
    intent_accuracy,
    parameter_accuracy,
    task_completeness,
    overall_accuracy
)


def test_intent_accuracy_correct():
    """Test intent accuracy with correct prediction."""
    example = {
        "intent": "set_timer",
        "expected_task": {"action": "set_timer"}
    }
    
    prediction = dspy.Prediction(
        task_json=json.dumps({"action": "set_timer", "parameters": {}, "priority": "medium"})
    )
    
    score = intent_accuracy(example, prediction)
    assert score == 1.0


def test_intent_accuracy_incorrect():
    """Test intent accuracy with incorrect prediction."""
    example = {
        "intent": "set_timer",
        "expected_task": {"action": "set_timer"}
    }
    
    prediction = dspy.Prediction(
        task_json=json.dumps({"action": "set_reminder", "parameters": {}, "priority": "medium"})
    )
    
    score = intent_accuracy(example, prediction)
    assert score == 0.0


def test_parameter_accuracy():
    """Test parameter accuracy."""
    example = {
        "expected_task": {
            "action": "set_timer",
            "parameters": {"duration": "20"}
        }
    }
    
    prediction = dspy.Prediction(
        task_json=json.dumps({
            "action": "set_timer",
            "parameters": {"duration": "20"},
            "priority": "medium"
        })
    )
    
    score = parameter_accuracy(example, prediction)
    assert score == 1.0


def test_task_completeness():
    """Test task completeness metric."""
    example = {}
    
    # Complete task
    prediction = dspy.Prediction(
        task_json=json.dumps({
            "action": "set_timer",
            "parameters": {"duration": "20"},
            "priority": "medium"
        })
    )
    
    score = task_completeness(example, prediction)
    assert score == 1.0
    
    # Incomplete task
    prediction_incomplete = dspy.Prediction(
        task_json=json.dumps({"action": "set_timer"})
    )
    
    score_incomplete = task_completeness(example, prediction_incomplete)
    assert score_incomplete < 1.0


def test_overall_accuracy():
    """Test overall accuracy metric."""
    example = {
        "intent": "set_timer",
        "expected_task": {
            "action": "set_timer",
            "parameters": {"duration": "20"},
            "priority": "medium"
        }
    }
    
    prediction = dspy.Prediction(
        task_json=json.dumps({
            "action": "set_timer",
            "parameters": {"duration": "20"},
            "priority": "medium"
        })
    )
    
    score = overall_accuracy(example, prediction)
    assert 0.0 <= score <= 1.0
    assert score > 0.5  # Should be high for good match


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
