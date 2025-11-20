"""
Command-line interface for the prompt tuning MVP.
Provides commands for data generation, optimization, and evaluation.
"""

import argparse
import sys
from pathlib import Path

import dspy
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

from .data.generator import FamilySpeechDataGenerator
from .data.loader import DataLoader
from .models.simulated_lm import DummyLM
from .models.pipeline import DirectSpeechToTaskPipeline, format_task_output
from .optimization.optimizer import PromptOptimizer

console = Console()


def generate_data(args):
    """Generate simulated dataset."""
    console.print("\n[bold blue]Generating Simulated Dataset[/bold blue]")
    
    generator = FamilySpeechDataGenerator(seed=args.seed)
    dataset = generator.generate_dataset(total_samples=args.count)
    splits = generator.split_dataset(dataset, train_ratio=0.6, dev_ratio=0.2)
    generator.save_dataset(splits, args.output)
    
    console.print(f"\n[green]Dataset generated successfully![/green]")


def evaluate(args):
    """Evaluate pipeline on dataset."""
    console.print("\n[bold blue]Evaluating Pipeline[/bold blue]")
    
    # Configure DSPy
    lm = DummyLM()
    dspy.settings.configure(lm=lm)
    
    # Load data
    loader = DataLoader(args.data)
    loader.load()
    
    # Create pipeline
    pipeline = DirectSpeechToTaskPipeline()
    
    # Evaluate
    from .optimization.metrics import MetricEvaluator
    evaluator = MetricEvaluator(pipeline)
    
    split_name = args.split
    examples = loader.get_examples(split_name, limit=args.limit)
    
    console.print(f"Evaluating on {len(examples)} examples from {split_name} set...")
    
    results = evaluator.evaluate_all_metrics(examples)
    
    # Display results
    table = Table(title=f"Evaluation Results ({split_name})")
    table.add_column("Metric", style="cyan")
    table.add_column("Score", style="green")
    
    for metric, score in results.items():
        table.add_row(metric, f"{score:.2%}")
    
    console.print(table)


def optimize(args):
    """Run prompt optimization."""
    console.print("\n[bold blue]Running Prompt Optimization[/bold blue]")
    
    # Configure DSPy
    lm = DummyLM()
    dspy.settings.configure(lm=lm)
    
    # Create optimizer
    optimizer = PromptOptimizer(args.data)
    
    # Run optimization
    output_path = Path(args.output) / "optimization_results.json"
    results = optimizer.run_full_optimization(str(output_path))
    
    console.print("\n[green]Optimization complete![/green]")


def compare(args):
    """Compare optimization results."""
    import json
    
    console.print("\n[bold blue]Comparing Results[/bold blue]")
    
    # Load results
    with open(args.results, 'r') as f:
        data = json.load(f)
    
    comparison = data.get("comparison", {})
    
    if not comparison:
        console.print("[red]No comparison data found in results file[/red]")
        return
    
    # Display comparison
    table = Table(title="Baseline vs Optimized Comparison")
    table.add_column("Metric", style="cyan")
    table.add_column("Baseline", style="yellow")
    table.add_column("Optimized", style="green")
    table.add_column("Improvement", style="magenta")
    
    for metric, values in comparison.items():
        baseline = values["baseline"]
        optimized = values["optimized"]
        improvement = values["improvement"]
        
        table.add_row(
            metric,
            f"{baseline:.2%}",
            f"{optimized:.2%}",
            f"{improvement:+.2%}"
        )
    
    console.print(table)


def demo(args):
    """Run demo with example input."""
    console.print("\n[bold blue]Speech-to-Task Demo[/bold blue]")
    
    # Configure DSPy
    lm = DummyLM()
    dspy.settings.configure(lm=lm)
    
    # Create pipeline
    pipeline = DirectSpeechToTaskPipeline()
    
    # Process input
    speech = args.input
    speaker = args.speaker
    
    console.print(Panel(
        f"[yellow]Speech:[/yellow] {speech}\n[yellow]Speaker:[/yellow] {speaker}",
        title="Input"
    ))
    
    # Run pipeline
    result = pipeline(speech_input=speech, speaker_context=speaker)
    
    # Display output
    output = format_task_output(result)
    
    console.print(Panel(
        output,
        title="Extracted Task",
        border_style="green"
    ))


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Prompt Tuning MVP for Speech-to-Task",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Generate data command
    gen_parser = subparsers.add_parser("generate-data", help="Generate simulated dataset")
    gen_parser.add_argument("--output", default="data/simulated_commands.json",
                           help="Output path for dataset")
    gen_parser.add_argument("--count", type=int, default=100,
                           help="Number of samples to generate")
    gen_parser.add_argument("--seed", type=int, default=42,
                           help="Random seed for reproducibility")
    gen_parser.set_defaults(func=generate_data)
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate pipeline")
    eval_parser.add_argument("--data", required=True,
                            help="Path to dataset JSON")
    eval_parser.add_argument("--split", default="dev",
                            choices=["train", "dev", "test"],
                            help="Which split to evaluate")
    eval_parser.add_argument("--limit", type=int, default=None,
                            help="Limit number of examples")
    eval_parser.set_defaults(func=evaluate)
    
    # Optimize command
    opt_parser = subparsers.add_parser("optimize", help="Optimize prompts")
    opt_parser.add_argument("--data", required=True,
                           help="Path to dataset JSON")
    opt_parser.add_argument("--output", default="results",
                           help="Output directory for results")
    opt_parser.set_defaults(func=optimize)
    
    # Compare command
    cmp_parser = subparsers.add_parser("compare", help="Compare results")
    cmp_parser.add_argument("--results", required=True,
                           help="Path to optimization results JSON")
    cmp_parser.set_defaults(func=compare)
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demo with example")
    demo_parser.add_argument("--input", required=True,
                            help="Speech input text")
    demo_parser.add_argument("--speaker", default="parent",
                            choices=["parent", "child", "teen"],
                            help="Speaker context")
    demo_parser.set_defaults(func=demo)
    
    # Parse and execute
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    args.func(args)


if __name__ == "__main__":
    main()
