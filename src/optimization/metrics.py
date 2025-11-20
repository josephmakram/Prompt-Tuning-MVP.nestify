"""
Evaluation metrics for prompt optimization.
Measures accuracy and performance of speech-to-task pipeline.
"""

import json
from typing import Dict, Any, List, Optional
import dspy


def extract_task_dict(task_json: Any) -> Optional[Dict[str, Any]]:
    """
    Extract task dictionary from various formats.
    
    Args:
        task_json: Task in various formats (dict, str, etc.)
    
    Returns:
        Task dictionary or None
    """
    if isinstance(task_json, dict):
        return task_json
    
    if isinstance(task_json, str):
        try:
            # Clean up string
            cleaned = task_json.strip()
            
            # Remove code blocks
            if cleaned.startswith("```"):
                lines = cleaned.split('\n')
                cleaned = '\n'.join(lines[1:-1]) if len(lines) > 2 else cleaned
            
            return json.loads(cleaned)
        except json.JSONDecodeError:
            return None
    
    return None


def intent_accuracy(example: Dict[str, Any], prediction: dspy.Prediction, 
                    trace: Any = None) -> float:
    """
    Metric: Check if predicted intent matches expected intent.
    
    Args:
        example: Ground truth example with 'intent' field
        prediction: Model prediction with 'task_json' or 'intent' field
        trace: Optional trace (unused)
    
    Returns:
        1.0 if match, 0.0 otherwise
    """
    expected_intent = example.get("intent", "")
    
    # Try to get intent from prediction
    if hasattr(prediction, "intent"):
        predicted_intent = prediction.intent
    else:
        # Extract from task_json
        task = extract_task_dict(getattr(prediction, "task_json", {}))
        if task is None:
            return 0.0
        predicted_intent = task.get("action", "")
    
    return 1.0 if predicted_intent == expected_intent else 0.0


def parameter_accuracy(example: Dict[str, Any], prediction: dspy.Prediction,
                      trace: Any = None) -> float:
    """
    Metric: Check if parameters match expected values.
    
    Args:
        example: Ground truth with 'expected_task' containing parameters
        prediction: Model prediction with 'task_json'
        trace: Optional trace (unused)
    
    Returns:
        Ratio of matching parameters (0.0 to 1.0)
    """
    expected_task = example.get("expected_task", {})
    expected_params = expected_task.get("parameters", {})
    
    # Extract predicted task
    task = extract_task_dict(getattr(prediction, "task_json", {}))
    if task is None:
        return 0.0
    
    predicted_params = task.get("parameters", {})
    
    # If no parameters expected, check if none predicted
    if not expected_params:
        return 1.0 if not predicted_params else 0.5
    
    # Count matching parameters
    matches = 0
    total = len(expected_params)
    
    for key, expected_value in expected_params.items():
        if key in predicted_params:
            predicted_value = str(predicted_params[key]).lower().strip()
            expected_value_str = str(expected_value).lower().strip()
            
            # Fuzzy match - check if values are similar
            if predicted_value == expected_value_str or \
               predicted_value in expected_value_str or \
               expected_value_str in predicted_value:
                matches += 1
    
    return matches / total if total > 0 else 1.0


def task_completeness(example: Dict[str, Any], prediction: dspy.Prediction,
                     trace: Any = None) -> float:
    """
    Metric: Check if task has required fields.
    
    Args:
        example: Ground truth example
        prediction: Model prediction with 'task_json'
        trace: Optional trace (unused)
    
    Returns:
        Ratio of required fields present (0.0 to 1.0)
    """
    task = extract_task_dict(getattr(prediction, "task_json", {}))
    if task is None:
        return 0.0
    
    required_fields = ["action", "parameters", "priority"]
    present = sum(1 for field in required_fields if field in task)
    
    return present / len(required_fields)


def overall_accuracy(example: Dict[str, Any], prediction: dspy.Prediction,
                    trace: Any = None) -> float:
    """
    Combined metric: Weighted average of all metrics.
    
    Args:
        example: Ground truth example
        prediction: Model prediction
        trace: Optional trace (unused)
    
    Returns:
        Weighted accuracy score (0.0 to 1.0)
    """
    intent_score = intent_accuracy(example, prediction, trace)
    param_score = parameter_accuracy(example, prediction, trace)
    complete_score = task_completeness(example, prediction, trace)
    
    # Weighted average: intent is most important
    weights = {"intent": 0.5, "params": 0.3, "completeness": 0.2}
    
    return (weights["intent"] * intent_score + 
            weights["params"] * param_score + 
            weights["completeness"] * complete_score)


class MetricEvaluator:
    """Evaluates pipeline performance on a dataset."""
    
    def __init__(self, pipeline: dspy.Module):
        """
        Initialize evaluator.
        
        Args:
            pipeline: DSPy pipeline to evaluate
        """
        self.pipeline = pipeline
    
    def evaluate(self, examples: List[Dict[str, Any]], 
                metric_fn: callable = overall_accuracy) -> Dict[str, Any]:
        """
        Evaluate pipeline on examples.
        
        Args:
            examples: List of examples to evaluate
            metric_fn: Metric function to use
        
        Returns:
            Dictionary with evaluation results
        """
        scores = []
        predictions = []
        errors = 0
        
        for example in examples:
            try:
                # Run pipeline
                prediction = self.pipeline(
                    speech_input=example["speech_input"],
                    speaker_context=example["speaker_context"]
                )
                
                # Calculate metric
                score = metric_fn(example, prediction)
                scores.append(score)
                predictions.append({
                    "example": example,
                    "prediction": prediction,
                    "score": score
                })
                
            except Exception as e:
                print(f"Error evaluating example: {e}")
                errors += 1
                scores.append(0.0)
        
        avg_score = sum(scores) / len(scores) if scores else 0.0
        
        return {
            "average_score": avg_score,
            "scores": scores,
            "predictions": predictions,
            "num_examples": len(examples),
            "num_errors": errors,
            "metric_name": metric_fn.__name__
        }
    
    def evaluate_all_metrics(self, examples: List[Dict[str, Any]]) -> Dict[str, float]:
        """
        Evaluate with all available metrics.
        
        Args:
            examples: List of examples to evaluate
        
        Returns:
            Dictionary mapping metric names to scores
        """
        metrics = {
            "intent_accuracy": intent_accuracy,
            "parameter_accuracy": parameter_accuracy,
            "task_completeness": task_completeness,
            "overall_accuracy": overall_accuracy,
        }
        
        results = {}
        for name, metric_fn in metrics.items():
            eval_result = self.evaluate(examples, metric_fn)
            results[name] = eval_result["average_score"]
        
        return results
    
    def print_results(self, results: Dict[str, Any]):
        """Pretty print evaluation results."""
        print("\n=== Evaluation Results ===")
        print(f"Metric: {results['metric_name']}")
        print(f"Examples: {results['num_examples']}")
        print(f"Errors: {results['num_errors']}")
        print(f"Average Score: {results['average_score']:.2%}")
        
        # Show score distribution
        scores = results['scores']
        if scores:
            print(f"Min Score: {min(scores):.2%}")
            print(f"Max Score: {max(scores):.2%}")


def main():
    """Test metrics."""
    # Example data
    example = {
        "speech_input": "Set timer for 20 minutes",
        "speaker_context": "parent",
        "intent": "set_timer",
        "expected_task": {
            "action": "set_timer",
            "parameters": {"duration": "20"},
            "priority": "medium"
        }
    }
    
    # Mock prediction
    prediction = dspy.Prediction(
        task_json=json.dumps({
            "action": "set_timer",
            "parameters": {"duration": "20"},
            "priority": "medium"
        })
    )
    
    print("Testing metrics with perfect match:")
    print(f"Intent Accuracy: {intent_accuracy(example, prediction):.2%}")
    print(f"Parameter Accuracy: {parameter_accuracy(example, prediction):.2%}")
    print(f"Task Completeness: {task_completeness(example, prediction):.2%}")
    print(f"Overall Accuracy: {overall_accuracy(example, prediction):.2%}")


if __name__ == "__main__":
    main()
