"""
Simulated Language Model for offline testing.
This mock LM allows testing DSPy without external API calls.
"""

import re
import json
from typing import List, Dict, Any, Optional
import dspy


class SimulatedLM:
    """
    Mock language model that simulates responses based on rules.
    Allows testing prompt optimization without external API calls.
    """
    
    def __init__(self, error_rate: float = 0.1):
        """
        Initialize simulated LM.
        
        Args:
            error_rate: Probability of making an error (0.0 to 1.0)
        """
        self.error_rate = error_rate
        self.call_count = 0
        
        # Intent detection patterns
        self.intent_patterns = {
            "set_timer": r"timer|set.*timer|start.*timer",
            "set_reminder": r"remind|reminder|don't forget|don't let me forget",
            "add_to_shopping_list": r"add.*shopping|shopping.*list|we need|we're out",
            "control_device": r"turn on|turn off|switch|lights",
            "get_information": r"what's|what is|when|weather|time|date|day",
            "play_media": r"play|put on|start playing|watch|listen",
            "add_calendar_event": r"calendar|schedule|add.*calendar",
            "request_help": r"help|what's.*homework|need help"
        }
        
        # Parameter extraction patterns
        self.param_patterns = {
            "duration": r"(\d+)\s*(?:minute|min|hour|hr)",
            "time": r"(?:at\s+)?(\d+(?::\d+)?\s*(?:am|pm)?|tomorrow|today|morning|afternoon|evening|in\s+\d+\s+hours?)",
            "task": r"(?:to\s+)?(pick up|call|take|feed|start|check|water)\s+[\w\s]+",
            "item": r"(?:add|need|get|out of)\s+([\w\s]+?)(?:\s+to|\s+on|$)",
            "device": r"(?:on|off)\s+([\w\s]+?)(?:\s+lights?|\s*$)|(\w+\s+lights?)",
            "content": r"play\s+([\w\s]+)|my\s+([\w\s]+)",
            "event": r"(?:add|schedule)\s+([\w\s]+?)(?:\s+to|\s+at|\s+for)",
            "subject": r"help.*with\s+(\w+)|(\w+)\s+homework",
        }
    
    def __call__(self, prompt: str, **kwargs) -> List[str]:
        """
        Simulate LM call.

        Args:
            prompt: Input prompt
            **kwargs: Additional arguments (ignored for simulation)

        Returns:
            List containing single response string
        """
        self.call_count += 1

        # Extract the actual query from the prompt
        query = self._extract_query(prompt)

        # Determine task type based on prompt content
        prompt_lower = prompt.lower()

        # Check for DSPy signature patterns
        if "task_json" in prompt_lower and "confidence" in prompt_lower:
            # This is a direct speech-to-task request
            response = self._simulate_task_generation(query, prompt)
        elif "extract intent" in prompt_lower or ("intent" in prompt_lower and "confidence" in prompt_lower):
            # This is an intent extraction request
            response = self._simulate_intent_extraction(query, prompt)
        elif "convert" in prompt_lower or "task" in prompt_lower:
            # This is a task generation from intent
            response = self._simulate_task_generation(query, prompt)
        else:
            response = self._simulate_general_response(query)

        return [response]
    
    def _extract_query(self, prompt: str) -> str:
        """Extract the actual query/command from the prompt."""
        # Look for common patterns in DSPy prompts
        lines = prompt.split('\n')

        # Try to find speech_input field
        for line in lines:
            if 'speech_input:' in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()
            elif 'command:' in line.lower():
                parts = line.split(':', 1)
                if len(parts) > 1:
                    return parts[1].strip()

        # Look for fields in DSPy format (e.g., "[[ ## speech_input ## ]]")
        import re
        match = re.search(r'\[\[\s*##\s*speech_input\s*##\s*\]\]\s*\n\s*([^\n\[]+)', prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip()

        # If no pattern found, return last non-empty line before "---" or empty line
        significant_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('---') and not stripped.startswith('##'):
                significant_lines.append(stripped)

        if significant_lines:
            return significant_lines[-1]

        return prompt
    
    def _simulate_intent_extraction(self, query: str, full_prompt: str) -> str:
        """Simulate intent extraction from speech command."""
        query_lower = query.lower()
        
        # Find matching intent
        detected_intent = "unknown"
        max_score = 0
        
        for intent, pattern in self.intent_patterns.items():
            if re.search(pattern, query_lower):
                # Simple scoring based on pattern match
                score = len(re.findall(pattern, query_lower))
                if score > max_score:
                    max_score = score
                    detected_intent = intent
        
        # Simulate confidence
        confidence = 0.95 if max_score > 0 else 0.3
        
        # Introduce some errors
        import random
        if random.random() < self.error_rate:
            # Make an error - pick wrong intent
            all_intents = list(self.intent_patterns.keys())
            detected_intent = random.choice(all_intents)
            confidence = 0.6
        
        return f"intent: {detected_intent}\nconfidence: {confidence}"
    
    def _simulate_task_generation(self, query: str, full_prompt: str) -> str:
        """Simulate task JSON generation from intent and speech."""
        query_lower = query.lower()

        # Detect intent
        intent = "unknown"
        for intent_name, pattern in self.intent_patterns.items():
            if re.search(pattern, query_lower):
                intent = intent_name
                break

        # Extract parameters
        parameters = {}
        for param_name, pattern in self.param_patterns.items():
            match = re.search(pattern, query_lower)
            if match:
                # Get the first non-None group
                value = next((g for g in match.groups() if g), match.group(1) if match.lastindex else match.group(0))
                parameters[param_name] = value.strip()

        # Determine priority
        priority = "medium"
        if "urgent" in query_lower or "now" in query_lower:
            priority = "high"
        elif "when you can" in query_lower or "maybe" in query_lower:
            priority = "low"

        task = {
            "action": intent,
            "parameters": parameters,
            "priority": priority
        }

        task_json_str = json.dumps(task)

        # Check if the prompt is asking for JSON format with multiple fields (DSPy JSONAdapter)
        if "json" in full_prompt.lower() and ("task_json" in full_prompt.lower() or "confidence" in full_prompt.lower()):
            # Return in DSPy JSONAdapter expected format - a single JSON object with all fields
            import random
            confidence = round(0.85 + random.random() * 0.1, 2)  # Random confidence between 0.85 and 0.95

            response_obj = {
                "task_json": task_json_str,
                "confidence": confidence
            }

            # Check if reasoning is requested (ChainOfThought)
            if "reasoning" in full_prompt.lower():
                reasoning = f"Detected intent '{intent}' from the speech command. Extracted parameters and determined priority as '{priority}'."
                response_obj = {"reasoning": reasoning, **response_obj}

            return json.dumps(response_obj, indent=2)
        else:
            # Return just the task JSON
            return json.dumps(task, indent=2)
    
    def _simulate_general_response(self, query: str) -> str:
        """Simulate a general response."""
        return f"Processing: {query}"
    
    def reset_count(self):
        """Reset call counter."""
        self.call_count = 0
    
    def get_call_count(self) -> int:
        """Get number of calls made."""
        return self.call_count


class DummyLM(dspy.BaseLM):
    """
    Dummy LM for DSPy compatibility.
    Wraps SimulatedLM to match DSPy's expected interface.
    """

    def __init__(self, model: str = "simulated", **kwargs):
        """Initialize dummy LM."""
        super().__init__(model=model)
        self.kwargs = kwargs
        self.history = []
        self.sim_lm = SimulatedLM()
        self.provider = "simulated"

    def __call__(self, prompt: str = None, messages: List = None, **kwargs):
        """Call the LM."""
        if messages:
            prompt = messages[-1].get("content", "") if isinstance(messages[-1], dict) else str(messages[-1])

        response = self.sim_lm(prompt, **kwargs)
        self.history.append({"prompt": prompt, "response": response})
        return response

    def basic_request(self, prompt: str, **kwargs):
        """Basic request method required by DSPy."""
        response_text = self.sim_lm(prompt, **kwargs)[0]
        return {"choices": [{"text": response_text}]}

    def inspect_history(self, n: int = 1):
        """Inspect recent history."""
        return self.history[-n:] if self.history else []


def main():
    """Test simulated LM."""
    lm = SimulatedLM()
    
    # Test intent extraction
    prompt1 = """
    Extract intent from family speech command.
    
    speech_input: Set timer for 20 minutes
    speaker_context: parent
    
    Provide intent and confidence.
    """
    print("Test 1 - Intent Extraction:")
    print(lm(prompt1)[0])
    print()
    
    # Test task generation
    prompt2 = """
    Convert intent to executable task.
    
    speech_input: Remind me to pick up kids at 3pm
    intent: set_reminder
    
    Generate task in JSON format.
    """
    print("Test 2 - Task Generation:")
    print(lm(prompt2)[0])
    print()
    
    print(f"Total calls: {lm.get_call_count()}")


if __name__ == "__main__":
    main()
