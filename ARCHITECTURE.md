# Architecture Documentation

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Speech-to-Task MVP System                   │
└─────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   CLI Layer  │─────▶│ Pipeline     │─────▶│  Evaluation  │
│              │      │   Layer      │      │    Layer     │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     │                      │
       ▼                     ▼                      ▼
┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│  Data Layer  │      │ Model Layer  │      │ Optimization │
└──────────────┘      └──────────────┘      └──────────────┘
```

## Layer Breakdown

### 1. Data Layer (`src/data/`)

**Purpose**: Generate and manage speech command datasets

```
┌─────────────────────────────────────────┐
│         FamilySpeechDataGenerator       │
├─────────────────────────────────────────┤
│ • Templates (8 intent types)            │
│ • Variables (duration, tasks, etc.)     │
│ • Edge case generation                  │
│ • 100+ diverse examples                 │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│            DataLoader                   │
├─────────────────────────────────────────┤
│ • Load JSON datasets                    │
│ • Train/dev/test split (60/20/20)      │
│ • Statistics computation                │
│ • Filtering by intent/speaker          │
└─────────────────────────────────────────┘
```

**Data Flow**:
```
Templates + Variables → Examples → JSON File → Train/Dev/Test Sets
```

### 2. Model Layer (`src/models/`)

**Purpose**: Language model and DSPy pipeline definitions

```
┌─────────────────────────────────────────┐
│          SimulatedLM                    │
├─────────────────────────────────────────┤
│ • Rule-based intent detection           │
│ • Regex parameter extraction            │
│ • Configurable accuracy (0-1)           │
│ • No external API calls                 │
│ • DSPy-compatible interface             │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│        DSPy Signatures                  │
├─────────────────────────────────────────┤
│ • SpeechToIntent                        │
│ • IntentToTask                          │
│ • DirectSpeechToTask                    │
│ • Chain of Thought variants             │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│          Pipelines                      │
├─────────────────────────────────────────┤
│ • Two-step: Speech→Intent→Task          │
│ • Direct: Speech→Task                   │
│ • PipelineWrapper (helpers)             │
│ • Batch processing                      │
└─────────────────────────────────────────┘
```

**Pipeline Flow (Two-Step)**:
```
Speech Input
    │
    ▼
┌────────────────┐
│ SpeechToIntent │ → Intent + Confidence
└────────────────┘
    │
    ▼
┌────────────────┐
│ IntentToTask   │ → Structured Task JSON
└────────────────┘
    │
    ▼
{
  "action": "set_timer",
  "parameters": {"duration": "20 minutes"},
  "priority": "high"
}
```

### 3. Optimization Layer (`src/optimization/`)

**Purpose**: Evaluate and optimize pipeline performance

```
┌─────────────────────────────────────────┐
│      SpeechToTaskMetrics                │
├─────────────────────────────────────────┤
│ • Intent accuracy                       │
│ • Action accuracy                       │
│ • Parameter accuracy (fuzzy match)      │
│ • Priority accuracy                     │
│ • Exact match                           │
│ • Per-category breakdowns               │
│ • Error analysis                        │
└─────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────┐
│    SpeechToTaskOptimizer                │
├─────────────────────────────────────────┤
│ • BootstrapFewShot optimization         │
│ • Baseline evaluation                   │
│ • Optimized evaluation                  │
│ • Comparison & reporting                │
│ • Results serialization                 │
└─────────────────────────────────────────┘
```

**Optimization Flow**:
```
Train Data → Baseline Pipeline → Baseline Metrics
                    │
                    ▼
            BootstrapFewShot
                    │
                    ▼
         Optimized Pipeline → Optimized Metrics
                    │
                    ▼
              Comparison & Report
```

### 4. CLI Layer (`src/cli.py`)

**Purpose**: User interface and orchestration

```
┌─────────────────────────────────────────┐
│           CLI Commands                  │
├─────────────────────────────────────────┤
│ • generate-data                         │
│ • evaluate                              │
│ • optimize                              │
│ • compare                               │
│ • demo                                  │
└─────────────────────────────────────────┘
```

**Command Interactions**:
```
User → CLI → Data Layer → Model Layer → Optimization → Results
```

## Data Structures

### Input Example
```python
{
  "id": "example_001",
  "speech_input": "Set timer for 20 minutes",
  "speaker_context": "parent",
  "intent": "timer",
  "expected_task": {
    "action": "set_timer",
    "parameters": {"duration": "20 minutes"},
    "priority": "high"
  }
}
```

### Pipeline Prediction
```python
{
  "task": {
    "action": "set_timer",
    "parameters": {"duration": "20 minutes"},
    "priority": "high"
  },
  "intent": "timer",
  "confidence": 0.95
}
```

### Evaluation Metrics
```python
{
  "intent_accuracy": 0.82,
  "action_accuracy": 0.78,
  "parameter_accuracy": 0.71,
  "priority_accuracy": 0.75,
  "exact_match_accuracy": 0.68,
  "total_examples": 100
}
```

## Intent Categories

```
┌─────────────┬──────────────────────────────────────────┐
│ Intent      │ Example Commands                         │
├─────────────┼──────────────────────────────────────────┤
│ timer       │ "Set timer for 20 minutes"              │
│ reminder    │ "Remind me to pick up kids at 3pm"     │
│ shopping    │ "Add milk to shopping list"             │
│ smart_home  │ "Turn on living room lights"            │
│ information │ "What's the weather today"              │
│ entertainment│ "Play my bedtime story"                │
│ calendar    │ "Schedule dentist for tomorrow"         │
│ help        │ "Help me with math homework"            │
└─────────────┴──────────────────────────────────────────┘
```

## Speaker Contexts

```
┌─────────┬────────────────────────────────────────────┐
│ Speaker │ Characteristics                            │
├─────────┼────────────────────────────────────────────┤
│ parent  │ • Clear commands                           │
│         │ • Complex multi-parameter tasks            │
│         │ • Scheduling and reminders                 │
├─────────┼────────────────────────────────────────────┤
│ child   │ • Simple requests                          │
│         │ • Entertainment and help                   │
│         │ • Incomplete sentences                     │
├─────────┼────────────────────────────────────────────┤
│ teen    │ • Casual language                          │
│         │ • Smart home controls                      │
│         │ • Music and media                          │
└─────────┴────────────────────────────────────────────┘
```

## Optimization Strategy

### BootstrapFewShot

```
Initial Prompt (Baseline)
         │
         ▼
┌────────────────────┐
│  Training Examples │
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Select Demos      │ ← Metric-driven selection
└────────────────────┘
         │
         ▼
┌────────────────────┐
│  Optimized Prompt  │ ← Few-shot examples added
└────────────────────┘
         │
         ▼
   Better Performance
```

**Key Steps**:
1. Run baseline on training set
2. Select high-quality demonstrations
3. Bootstrap additional examples
4. Create optimized prompt with few-shot examples
5. Evaluate on test set

## Error Handling

```
┌─────────────────────────────────────────┐
│         Error Categories                │
├─────────────────────────────────────────┤
│ • File not found → Clear error message  │
│ • Malformed JSON → Fallback to default  │
│ • Import errors → Module path help      │
│ • Missing data → Generate data prompt   │
│ • Low accuracy → Suggest parameters     │
└─────────────────────────────────────────┘
```

## Testing Architecture

```
┌──────────────┐
│  test_data   │ → Data generation & loading
├──────────────┤
│ • Generator  │
│ • Loader     │
│ • Splitting  │
└──────────────┘

┌──────────────┐
│test_pipeline │ → Pipeline & LM functionality
├──────────────┤
│ • SimulatedLM│
│ • Signatures │
│ • Pipelines  │
└──────────────┘

┌──────────────┐
│test_optimization│ → Metrics & evaluation
├──────────────┤
│ • Metrics    │
│ • Accuracy   │
│ • Comparison │
└──────────────┘
```

## Extension Points

### Easy to Add:

1. **New Intent Type**:
   - Add to `templates` in generator.py
   - Add keywords to simulated_lm.py
   - Update documentation

2. **Real LLM**:
   - Create new class implementing LM interface
   - Replace `DSPySimulatedLM` with `OpenAILM`
   - Configure API keys

3. **New Optimizer**:
   - Import from `dspy.teleprompt`
   - Add method to `SpeechToTaskOptimizer`
   - Compare with BootstrapFewShot

4. **New Metric**:
   - Add to `SpeechToTaskMetrics`
   - Update `compute()` method
   - Include in summary

5. **Web UI**:
   - Add Flask/FastAPI endpoint
   - Wrap `PipelineWrapper`
   - Serve results as JSON

## Performance Characteristics

```
┌────────────────────┬─────────┬──────────┐
│ Operation          │ Time    │ Space    │
├────────────────────┼─────────┼──────────┤
│ Generate 100 ex    │ <1s     │ ~50KB    │
│ Load data          │ <1s     │ ~100KB   │
│ Single prediction  │ ~10ms   │ ~1KB     │
│ Evaluate 100 ex    │ ~2s     │ ~100KB   │
│ Optimize           │ 2-3min  │ ~1MB     │
└────────────────────┴─────────┴──────────┘
```

## Security Considerations

- ✅ No external API calls (offline)
- ✅ Local data only
- ✅ No credential storage
- ✅ Safe file operations
- ✅ Input validation throughout

## Scalability

**Current MVP**:
- 100+ examples
- 8 intent types
- Single-threaded
- In-memory processing

**Production Extension**:
- Database for examples
- Multi-threading for batch
- Caching for predictions
- Distributed optimization
- API rate limiting

---

This architecture supports:
- ✅ Easy testing
- ✅ Clear separation of concerns
- ✅ Modular components
- ✅ Simple extension
- ✅ Production readiness
