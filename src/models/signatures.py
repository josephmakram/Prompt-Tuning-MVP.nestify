"""
DSPy signatures for speech-to-task pipeline.
Defines input/output interfaces for each component.
"""

import dspy


class SpeechToIntent(dspy.Signature):
    """Extract intent from family speech command."""
    
    speech_input = dspy.InputField(desc="Raw speech transcription from family member")
    speaker_context = dspy.InputField(desc="Speaker context: parent, child, or teen")
    
    intent = dspy.OutputField(desc="Identified task intent (e.g., set_timer, set_reminder)")
    confidence = dspy.OutputField(desc="Confidence score between 0 and 1")


class IntentToTask(dspy.Signature):
    """Convert intent to executable task structure."""
    
    intent = dspy.InputField(desc="Identified intent from speech")
    speech_input = dspy.InputField(desc="Original speech command")
    speaker_context = dspy.InputField(desc="Speaker context: parent, child, or teen")
    
    task_json = dspy.OutputField(desc="Structured task in JSON format with action, parameters, and priority")


class SpeechToTaskDirect(dspy.Signature):
    """Direct conversion from speech to task (single-step)."""
    
    speech_input = dspy.InputField(desc="Raw speech transcription from family member")
    speaker_context = dspy.InputField(desc="Speaker context: parent, child, or teen")
    
    task_json = dspy.OutputField(desc="Complete task structure in JSON format")
    confidence = dspy.OutputField(desc="Confidence score between 0 and 1")


class TaskValidator(dspy.Signature):
    """Validate and refine extracted task."""
    
    task_json = dspy.InputField(desc="Extracted task in JSON format")
    speech_input = dspy.InputField(desc="Original speech command for context")
    
    is_valid = dspy.OutputField(desc="Whether the task is valid (yes/no)")
    refined_task = dspy.OutputField(desc="Refined task JSON with corrections if needed")


def main():
    """Display signature information."""
    print("DSPy Signatures for Speech-to-Task Pipeline")
    print("=" * 50)
    
    signatures = [
        ("SpeechToIntent", SpeechToIntent),
        ("IntentToTask", IntentToTask),
        ("SpeechToTaskDirect", SpeechToTaskDirect),
        ("TaskValidator", TaskValidator),
    ]
    
    for name, sig in signatures:
        print(f"\n{name}:")
        print(f"  Docstring: {sig.__doc__}")
        print(f"  Input fields: {list(sig.input_fields.keys())}")
        print(f"  Output fields: {list(sig.output_fields.keys())}")


if __name__ == "__main__":
    main()
