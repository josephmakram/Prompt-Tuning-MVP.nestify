#!/usr/bin/env python
"""
Main entry point for the Speech-to-Task Prompt Tuning MVP.
Runs the complete demo workflow: data generation, optimization, and evaluation.
"""

import sys
from pathlib import Path

import dspy
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

from src.data.generator import FamilySpeechDataGenerator
from src.models.simulated_lm import DummyLM
from src.optimization.optimizer import PromptOptimizer

console = Console()


def print_header():
    """Print welcome header."""
    console.print()
    console.print(Panel.fit(
        "[bold blue]Speech-to-Task Prompt-Tuning MVP[/bold blue]\n"
        "[dim]Optimizing prompts for family speech commands[/dim]",
        border_style="blue"
    ))
    console.print()


def generate_data():
    """Generate simulated dataset."""
    console.print("[bold cyan]Step 1: Generating Simulated Dataset[/bold cyan]")
    
    data_path = Path("data/simulated_commands.json")
    
    # Check if data already exists
    if data_path.exists():
        console.print(f"[yellow]Dataset already exists at {data_path}[/yellow]")
        return str(data_path)
    
    generator = FamilySpeechDataGenerator(seed=42)
    
    with console.status("[bold green]Generating 100 diverse speech commands..."):
        dataset = generator.generate_dataset(total_samples=100)
        splits = generator.split_dataset(dataset, train_ratio=0.6, dev_ratio=0.2)
        generator.save_dataset(splits, str(data_path))
    
    console.print(f"[green]Dataset created: {data_path}[/green]")
    return str(data_path)


def run_optimization(data_path: str):
    """Run prompt optimization."""
    console.print("\n[bold cyan]Step 2: Running Prompt Optimization[/bold cyan]")
    
    # Configure DSPy with simulated LM
    console.print("[dim]Configuring simulated language model...[/dim]")
    lm = DummyLM()
    dspy.settings.configure(lm=lm)
    
    # Create optimizer
    optimizer = PromptOptimizer(data_path)
    
    # Run optimization workflow
    results_path = "results/optimization_results.json"
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("[cyan]Optimizing prompts...", total=None)
        results = optimizer.run_full_optimization(results_path)
    
    console.print(f"[green]Results saved to {results_path}[/green]")
    return results


def display_results(results: dict):
    """Display optimization results."""
    console.print("\n[bold cyan]Step 3: Results Summary[/bold cyan]")
    
    from rich.table import Table
    
    comparison = results.get("comparison", {})
    
    if not comparison:
        console.print("[red]No comparison data available[/red]")
        return
    
    # Create results table
    table = Table(title="Baseline vs Optimized Performance", show_header=True)
    table.add_column("Metric", style="cyan", width=20)
    table.add_column("Baseline", justify="right", style="yellow")
    table.add_column("Optimized", justify="right", style="green")
    table.add_column("Improvement", justify="right", style="magenta")
    
    for metric, values in comparison.items():
        baseline = values["baseline"]
        optimized = values["optimized"]
        improvement = values["improvement"]
        
        # Color code improvement
        if improvement > 0:
            imp_style = "green"
        elif improvement < 0:
            imp_style = "red"
        else:
            imp_style = "white"
        
        table.add_row(
            metric.replace("_", " ").title(),
            f"{baseline:.1%}",
            f"{optimized:.1%}",
            f"[{imp_style}]{improvement:+.1%}[/{imp_style}]"
        )
    
    console.print(table)
    
    # Summary
    overall_baseline = comparison.get("overall_accuracy", {}).get("baseline", 0)
    overall_optimized = comparison.get("overall_accuracy", {}).get("optimized", 0)
    overall_improvement = overall_optimized - overall_baseline
    
    console.print()
    if overall_improvement > 0.10:
        console.print(Panel(
            f"[bold green]Success![/bold green] Achieved {overall_improvement:.1%} improvement\n"
            f"Baseline: {overall_baseline:.1%} → Optimized: {overall_optimized:.1%}",
            title="Optimization Results",
            border_style="green"
        ))
    elif overall_improvement > 0:
        console.print(Panel(
            f"[yellow]Moderate improvement:[/yellow] {overall_improvement:.1%}\n"
            f"Baseline: {overall_baseline:.1%} → Optimized: {overall_optimized:.1%}",
            title="Optimization Results",
            border_style="yellow"
        ))
    else:
        console.print(Panel(
            f"[dim]No improvement detected.[/dim]\n"
            f"Note: With simulated LM, results may vary.",
            title="Optimization Results",
            border_style="dim"
        ))


def run_demo_examples():
    """Run some example predictions."""
    console.print("\n[bold cyan]Step 4: Demo Examples[/bold cyan]")
    
    from src.models.pipeline import DirectSpeechToTaskPipeline, format_task_output
    
    # Configure DSPy
    lm = DummyLM()
    dspy.settings.configure(lm=lm)
    
    pipeline = DirectSpeechToTaskPipeline()
    
    examples = [
        ("Set timer for 20 minutes", "parent"),
        ("Remind me to pick up kids at 3pm", "parent"),
        ("Play my bedtime story", "child"),
        ("Add milk to shopping list", "parent"),
    ]
    
    for speech, speaker in examples:
        console.print(f"\n[dim]Input:[/dim] [yellow]{speech}[/yellow] [dim](speaker: {speaker})[/dim]")
        
        try:
            result = pipeline(speech_input=speech, speaker_context=speaker)
            output = format_task_output(result)
            console.print(f"[dim]Output:[/dim]\n{output}")
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


def main():
    """Main demo workflow."""
    try:
        print_header()
        
        # Step 1: Generate data
        data_path = generate_data()
        
        # Step 2: Run optimization
        results = run_optimization(data_path)
        
        # Step 3: Display results
        display_results(results)
        
        # Step 4: Demo examples
        run_demo_examples()
        
        # Conclusion
        console.print()
        console.print(Panel(
            "[bold green]Demo Complete![/bold green]\n\n"
            "Next steps:\n"
            "- Review results in results/optimization_results.json\n"
            "- Explore the codebase in src/\n"
            "- Run tests with: pytest tests/\n"
            "- Try CLI commands (see README.md)",
            title="Success",
            border_style="green"
        ))
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted by user[/yellow]")
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
