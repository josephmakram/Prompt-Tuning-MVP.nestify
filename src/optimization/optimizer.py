"""
Prompt optimizer using DSPy optimization strategies.
Optimizes prompts for improved accuracy on speech-to-task conversion.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import dspy

from ..data.loader import DataLoader
from ..models.pipeline import SpeechToTaskPipeline, DirectSpeechToTaskPipeline, SimplePredictPipeline
from .metrics import overall_accuracy, MetricEvaluator


class PromptOptimizer:
    """Handles prompt optimization workflow."""
    
    def __init__(self, data_path: str):
        """
        Initialize optimizer.
        
        Args:
            data_path: Path to dataset JSON file
        """
        self.data_loader = DataLoader(data_path)
        self.data_loader.load()
        
        self.baseline_pipeline = None
        self.optimized_pipeline = None
        
        self.baseline_results = None
        self.optimized_results = None
    
    def create_dspy_examples(self, examples: List[Dict[str, Any]]) -> List[dspy.Example]:
        """
        Convert dataset examples to DSPy Example format.
        
        Args:
            examples: List of raw examples
        
        Returns:
            List of dspy.Example objects
        """
        dspy_examples = []
        
        for ex in examples:
            # Create example with inputs and outputs
            example = dspy.Example(
                speech_input=ex["speech_input"],
                speaker_context=ex["speaker_context"],
                intent=ex.get("intent", ""),
                task_json=json.dumps(ex.get("expected_task", {}))
            ).with_inputs("speech_input", "speaker_context")
            
            dspy_examples.append(example)
        
        return dspy_examples
    
    def evaluate_baseline(self) -> Dict[str, Any]:
        """
        Evaluate baseline (unoptimized) pipeline.
        
        Returns:
            Evaluation results
        """
        print("\n=== Evaluating Baseline ===")
        
        # Create baseline pipeline
        self.baseline_pipeline = SimplePredictPipeline()
        
        # Evaluate on dev set
        dev_examples = self.data_loader.get_dev()
        evaluator = MetricEvaluator(self.baseline_pipeline)
        
        results = evaluator.evaluate_all_metrics(dev_examples)
        self.baseline_results = results
        
        print("\nBaseline Results:")
        for metric, score in results.items():
            print(f"  {metric}: {score:.2%}")
        
        return results
    
    def optimize_prompts(self, max_examples: int = 20) -> dspy.Module:
        """
        Optimize prompts using DSPy BootstrapFewShot.
        
        Args:
            max_examples: Maximum number of examples for optimization
        
        Returns:
            Optimized pipeline
        """
        print("\n=== Optimizing Prompts ===")
        
        # Get training examples
        train_examples = self.data_loader.get_train()[:max_examples]
        dspy_train = self.create_dspy_examples(train_examples)
        
        print(f"Training on {len(dspy_train)} examples...")
        
        # Create optimizer
        # Using BootstrapFewShot with overall_accuracy metric
        optimizer = dspy.BootstrapFewShot(
            metric=overall_accuracy,
            max_bootstrapped_demos=4,
            max_labeled_demos=4,
        )
        
        # Create pipeline to optimize
        pipeline = DirectSpeechToTaskPipeline()
        
        try:
            # Optimize
            print("Running optimization...")
            self.optimized_pipeline = optimizer.compile(
                pipeline,
                trainset=dspy_train
            )
            print("Optimization complete!")
            
        except Exception as e:
            print(f"Optimization error (using baseline): {e}")
            self.optimized_pipeline = pipeline
        
        return self.optimized_pipeline
    
    def evaluate_optimized(self) -> Dict[str, Any]:
        """
        Evaluate optimized pipeline.
        
        Returns:
            Evaluation results
        """
        if self.optimized_pipeline is None:
            raise ValueError("Must run optimize_prompts() first")
        
        print("\n=== Evaluating Optimized Pipeline ===")
        
        # Evaluate on dev set
        dev_examples = self.data_loader.get_dev()
        evaluator = MetricEvaluator(self.optimized_pipeline)
        
        results = evaluator.evaluate_all_metrics(dev_examples)
        self.optimized_results = results
        
        print("\nOptimized Results:")
        for metric, score in results.items():
            print(f"  {metric}: {score:.2%}")
        
        return results
    
    def compare_results(self) -> Dict[str, Any]:
        """
        Compare baseline vs optimized results.
        
        Returns:
            Comparison dictionary
        """
        if self.baseline_results is None or self.optimized_results is None:
            raise ValueError("Must evaluate both baseline and optimized first")
        
        print("\n=== Comparison: Baseline vs Optimized ===")
        
        comparison = {}
        for metric in self.baseline_results.keys():
            baseline_score = self.baseline_results[metric]
            optimized_score = self.optimized_results[metric]
            improvement = optimized_score - baseline_score
            improvement_pct = (improvement / baseline_score * 100) if baseline_score > 0 else 0
            
            comparison[metric] = {
                "baseline": baseline_score,
                "optimized": optimized_score,
                "improvement": improvement,
                "improvement_pct": improvement_pct
            }
            
            print(f"\n{metric}:")
            print(f"  Baseline:    {baseline_score:.2%}")
            print(f"  Optimized:   {optimized_score:.2%}")
            print(f"  Improvement: {improvement:+.2%} ({improvement_pct:+.1f}%)")
        
        return comparison
    
    def save_results(self, output_path: str):
        """
        Save optimization results to file.
        
        Args:
            output_path: Path to save results JSON
        """
        results = {
            "baseline": self.baseline_results,
            "optimized": self.optimized_results,
            "comparison": self.compare_results() if self.baseline_results and self.optimized_results else None
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\nResults saved to {output_path}")
    
    def run_full_optimization(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run complete optimization workflow.
        
        Args:
            output_path: Optional path to save results
        
        Returns:
            Complete results dictionary
        """
        print("=== Starting Full Optimization Workflow ===")
        
        # Step 1: Baseline
        self.evaluate_baseline()
        
        # Step 2: Optimize
        self.optimize_prompts()
        
        # Step 3: Evaluate optimized
        self.evaluate_optimized()
        
        # Step 4: Compare
        comparison = self.compare_results()
        
        # Step 5: Save if requested
        if output_path:
            self.save_results(output_path)
        
        return {
            "baseline": self.baseline_results,
            "optimized": self.optimized_results,
            "comparison": comparison
        }


def main():
    """Run optimization."""
    from ..models.simulated_lm import DummyLM
    
    # Configure DSPy
    lm = DummyLM()
    dspy.settings.configure(lm=lm)
    
    # Run optimization
    optimizer = PromptOptimizer("data/simulated_commands.json")
    results = optimizer.run_full_optimization("results/optimization_results.json")
    
    print("\n=== Optimization Complete ===")


if __name__ == "__main__":
    main()
