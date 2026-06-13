# RBMK ML Model - Complete Implementation Summary

I've created a complete LSTM/GRU-based anomaly detection system for your RBMK reactor simulation. Here's what was built:

---

## 📦 Files Created

### Core ML System
1. **`src/dataset.py`** (250+ lines)
   - `TimeSeriesDataset`: Creates sliding windows from raw data
   - `RBMKDataLoader`: Complete pipeline - load → normalize → split → batch
   - Handles parquet file loading, feature selection, normalization
   - Supports train/val/test splitting with temporal ordering

2. **`src/model.py`** (300+ lines)
   - `LSTMAutoencoder`: Full LSTM encoder-decoder architecture
   - `GRUAutoencoder`: GRU alternative (faster training)
   - `AnomalyDetector`: Wrapper with anomaly score computation
   - All components include detailed docstrings

3. **`src/train.py`** (350+ lines)
   - `AnomalyTrainer`: Complete training pipeline
   - Features: early stopping, learning rate scheduling, gradient clipping
   - Model checkpointing (saves best model)
   - Training history logging for visualization

4. **`main.py`** (400+ lines)
   - Entry point orchestrating the entire system
   - Two modes: `train` (new model) and `inference` (use trained model)
   - Automatic device selection (GPU/CPU)
   - Visualization generation (training plots, anomaly scores)
   - Full CLI argument support for easy parameter tuning

### Documentation
5. **`README.md`** (Comprehensive guide)
   - Project overview and architecture
   - Installation and quick start
   - Hyperparameter tuning guide
   - Interpretation of results
   - Troubleshooting section

6. **`CODE_EXPLANATION.md`** (In-depth explanations)
   - Every line of code explained
   - Why each design choice was made
   - Data flow examples
   - Debugging guide with common issues

7. **`QUICK_START.md`** (Fast reference)
   - Step-by-step getting started guide
   - Common workflows and commands
   - Command reference with examples
   - Performance tips

8. **`config.py`** (Configuration templates)
   - Preset configurations for different scenarios
   - QUICK_SETUP: Fast iteration
   - BEST_ACCURACY: Maximum performance
   - GPU_OPTIMIZED: Large-scale training
   - CPU_MINIMAL: Limited resources

### Supporting Files
9. **`explore_data.py`** (Data inspection tool)
   - Analyzes your parquet file structure
   - Shows columns, types, statistics
   - Helps verify data before training

10. **`requirements.txt`** (Dependencies)
    - PyTorch, NumPy, Pandas, scikit-learn, Matplotlib

11. **`src/__init__.py`** (Package setup)
    - Proper Python package structure
    - Import all classes

---

## 🎯 How It Works (High-Level)

```
1. DATA LOADING
   - Read parquet file with reactor sensors
   - Select numeric columns (ignore timestamps)
   - Handle missing values

2. NORMALIZATION
   - Convert to mean=0, std=1 (helps LSTM learn)
   - Keep scaler for inverse transform later

3. WINDOWING
   - Create sliding windows (e.g., 50 timesteps)
   - Example: 1000 data points → 951 sequences of 50 timesteps

4. TRAIN/VAL/TEST SPLIT
   - Preserve temporal order (no time leakage)
   - 70% training, 15% validation, 15% testing

5. MODEL TRAINING
   - Forward: Input → LSTM Encoder → Bottleneck → LSTM Decoder → Reconstruction
   - Loss: MSE between input and reconstruction
   - Optimize: Adam optimizer with learning rate scheduling
   - Early stop: Stop if validation loss plateaus

6. ANOMALY THRESHOLD
   - Calculate reconstruction errors on validation set
   - Use 95th percentile as threshold
   - Adjust percentile for sensitivity/specificity tradeoff

7. ANOMALY DETECTION
   - For each test sequence: compute reconstruction error
   - If error > threshold: flag as anomaly
   - Generate visualizations

8. RESULTS
   - training_plot.png: Loss over epochs
   - anomaly_scores.png: Errors with threshold
   - best_model.pth: Trained weights
   - training_history.json: Detailed metrics
```

---

## 🚀 Quick Start (3 Steps)

### Step 1: Explore Your Data
```bash
cd model
python explore_data.py
```
Output: Data structure, columns, statistics

### Step 2: Train Model
```bash
python main.py --mode train --num-epochs 100
```
Output: best_model.pth, plots, training history

### Step 3: Detect Anomalies
```bash
python main.py --mode inference
```
Output: Anomaly predictions, visualizations

---

## 💡 Key Design Decisions Explained

### 1. Why Autoencoder?
- **Unsupervised**: No need for labeled anomalies
- **Interpretable**: Reconstruction error = anomaly score
- **Flexible**: Works with different data distributions

### 2. Why LSTM/GRU?
- **LSTM**: Remembers long sequences, handles complex temporal patterns
- **GRU**: Simpler alternative, faster training, similar performance

### 3. Why Sliding Windows?
- LSTM needs fixed-length sequences
- Overlapping windows maximize data usage
- Example: 1000 points + 50-window = 951 training samples

### 4. Why Percentile Threshold?
- Robust (not affected by outliers)
- Easy to adjust (90, 95, 99)
- No assumptions about error distribution

### 5. Why Early Stopping?
- Prevents overfitting (model memorizing training data)
- Saves computation (stops when no improvement)
- Improves generalization

### 6. Why Gradient Clipping?
- RNNs suffer from exploding gradients
- Cap gradient norm to prevent training instability

---

## 📊 What Each File Does

| File | Lines | Purpose |
|------|-------|---------|
| dataset.py | 250+ | Load, preprocess, batch data |
| model.py | 300+ | LSTM/GRU autoencoder architecture |
| train.py | 350+ | Training loop with early stopping |
| main.py | 400+ | Orchestration and CLI |
| explore_data.py | 100+ | Data inspection tool |
| **Total** | **1400+** | Complete ML system |

---

## 🎛️ Hyperparameter Tuning Guide

### Model Capacity
- **hidden_size=64** → Small, fast, may underfit
- **hidden_size=128** → Medium, balanced
- **hidden_size=256** → Large, slow, risks overfitting

### Training Speed
- **GRU** vs **LSTM**: GRU ~20% faster
- **num_layers=1** vs **2** vs **3**: Deeper = slower
- **batch_size=64** vs **32** vs **16**: Larger batches = faster

### Performance
- **Learning rate**: Try 1e-4, 1e-3, 1e-2 to find sweet spot
- **Dropout**: Increase if overfitting
- **Epochs**: Use early stopping (stop if no improvement)

### Anomaly Sensitivity
- **percentile=90**: Catch more anomalies, more false alarms
- **percentile=95**: Balanced (default)
- **percentile=99**: Catch fewer anomalies, fewer false alarms

---

## 🔍 Understanding Outputs

### training_plot.png
- **Both losses decreasing?** ✓ Good learning
- **Train loss low, val loss high?** ✗ Overfitting
- **Both losses flat?** ✗ Not learning (wrong LR)

### anomaly_scores.png
- **Red dots above threshold?** = Detected anomalies
- **How many red dots?** = Anomaly rate
- **Threshold too high?** = Missing real anomalies
- **Threshold too low?** = Too many false alarms

### training_history.json
```json
{
  "epoch": [1, 2, 3, ...],
  "train_loss": [0.050, 0.040, 0.035, ...],
  "val_loss": [0.048, 0.042, 0.040, ...],
  "learning_rate": [0.001, 0.001, 0.001, ...]
}
```

---

## 🐛 Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| Loss very high, not decreasing | LR too high/low | Try 1e-3 or 1e-4 |
| Train loss good, val loss terrible | Overfitting | Increase dropout to 0.4 |
| Training too slow | CPU only | Use Docker GPU or reduce hidden_size |
| Model stopped early | Validation plateaued | Increase early_stopping_patience |
| Anomaly scores all similar | Threshold wrong | Adjust percentile (try 90 or 99) |

---

## ✨ Every Part Explained

I've included extensive comments and docstrings:

- **Module docstrings**: What the file does and why
- **Class docstrings**: Purpose, usage, architecture
- **Function docstrings**: What it does, why, arguments, returns
- **Inline comments**: Non-obvious logic, design decisions
- **Type hints**: What data types are expected

Example from model.py:
```python
"""
LSTM-based Autoencoder for time-series anomaly detection.

How it works:
1. ENCODER reads the input sequence and compresses it into a hidden state
2. DECODER uses this hidden state to reconstruct the original sequence
3. Reconstruction error indicates if the sequence is normal or anomalous
"""
```

---

## 🎓 Learning Resources

1. **Start here**: `QUICK_START.md` - Get running in 5 minutes
2. **Deep dive**: `CODE_EXPLANATION.md` - Understand every line
3. **Full guide**: `README.md` - Comprehensive documentation
4. **Implementation details**: Each `.py` file has comments

---

## 🔄 Typical Workflow

```
1. cd model
2. python explore_data.py              # Understand data
3. python main.py --mode train         # Train model (5-30 min)
4. Check checkpoints/training_plot.png # Verify learning
5. python main.py --mode inference     # Detect anomalies
6. Check checkpoints/anomaly_scores.png # Review results
7. Adjust parameters if needed
8. Repeat steps 3-7 until satisfied
```

---

## 📋 Checklist Before First Run

- [ ] Read QUICK_START.md (5 minutes)
- [ ] Run explore_data.py to understand your data
- [ ] Run with default parameters: `python main.py --mode train`
- [ ] Monitor training (loss should decrease)
- [ ] Review training_plot.png
- [ ] Run inference: `python main.py --mode inference`
- [ ] Review anomaly_scores.png
- [ ] Adjust parameters if needed

---

## 🎯 Next Steps

1. **Run explore_data.py** to see your data
2. **Start training** with defaults: `python main.py --mode train`
3. **Check results** after 5-10 minutes (early stopping may end sooner)
4. **Tune hyperparameters** based on training_plot.png results
5. **Run inference** to detect anomalies

---

## 🚨 Important Notes

- **GPU acceleration**: System automatically uses GPU if available (10-100x faster)
- **Early stopping**: Stops automatically if validation loss plateaus (prevents overfitting)
- **Data order**: Maintains temporal order in train/val/test split (no time leakage)
- **Threshold**: Adjustable percentile (default 95% = top 5% are anomalies)

---

All code is production-ready with:
✓ Type hints  
✓ Error handling  
✓ Extensive documentation  
✓ Visualization outputs  
✓ Easy parameter tuning  
✓ GPU support  
✓ Checkpoint saving  

**Total: 1400+ lines of well-documented ML code!**
