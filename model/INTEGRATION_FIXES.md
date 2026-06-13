# Model-to-InfluxDB Integration Fixes

## Issues Fixed

### 1. **Model Class** 
- **Before**: `YourLSTMClassifier(*args, **kwargs)` (undefined placeholder)
- **After**: `LSTMAutoencoder` imported from `src.model`
- **Reason**: Your model is an autoencoder for anomaly detection, not a classifier

### 2. **Model Loading**
- **Before**: `torch.load("model.pth", map_location="cpu")`
- **After**: Proper path handling using `Path(__file__).parent / "checkpoints" / "best_model.pth"`
- **Added**: Try-catch error handling for model loading

### 3. **Anomaly Detection Logic**
- **Before**: Treated as classification with `probs[0, 1]` (expects classifier output)
- **After**: Uses reconstruction error (MSE) as anomaly score
- **How it works**: 
  - Normal data → Low MSE
  - Anomalous data → High MSE  
  - Threshold comparison to flag anomalies

### 4. **Device Support**
- **Added**: GPU detection with fallback to CPU
- **Before**: Hardcoded `map_location="cpu"`
- **After**: `DEVICE = "cuda" if torch.cuda.is_available() else "cpu"`

### 5. **Configuration**
- **Added**: Explicit configuration section with all tunable parameters
- `SEQ_LEN = 30` - Sequence length
- `INPUT_SIZE = 4` - Number of features
- `THRESHOLD = 0.5` - MSE threshold for anomaly detection
- Can be adjusted based on your model training

### 6. **Error Handling**
- **Before**: No error handling
- **After**: 
  - Try-catch blocks for data loading and inference
  - Graceful handling of missing/insufficient data
  - Proper logging of all operations

### 7. **Logging**
- **Added**: Comprehensive logging for debugging
- `logger.info()` - Key operations
- `logger.warning()` - Missing/insufficient data
- `logger.error()` - Failures

### 8. **Main Loop Improvements**
- **Before**: Infinite loop with hardcoded 1-second sleep
- **After**: 
  - Structured `main()` function with proper flow control
  - Data validation before inference
  - Error recovery with backoff (10-second sleep on error)
  - Proper shutdown handling (Ctrl+C support)

### 9. **InfluxDB Integration**
- **Changed measurement name**: `lstm_classification` → `lstm_anomaly_detection`
- **Changed fields**: 
  - Removed: `anomaly_probability`
  - Added: `reconstruction_error`, `threshold`
- **Improved robustness**: Error handling for write failures

### 10. **New Dependencies/Functions**
- Added `logging` for debugging
- Added `pathlib.Path` for cross-platform file paths
- Added `sys` for path manipulation
- New functions:
  - `compute_reconstruction_error()` - Calculate anomaly score
  - `main()` - Structured inference loop

## Requirements to Run

Ensure your `.env` file has:
```
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_token
INFLUXDB_ORG=your_org
INFLUXDB_BUCKET=reactor_data
```

Ensure these files exist:
- `checkpoints/best_model.pth` - Trained model weights
- `checkpoints/scaler.pkl` - Feature scaler (from training)

## Configuration Tuning

Adjust these based on your model:
- `THRESHOLD`: Higher = fewer false alarms, may miss real anomalies
- `SEQ_LEN`: Must match training sequence length (typically 30)
- `HIDDEN_SIZE`, `NUM_LAYERS`: Must match your trained model

## Testing

Run with:
```bash
python model_to_db.py
```

Expected output:
```
INFO:__main__:Model loaded from .../checkpoints/best_model.pth
INFO:__main__:Scaler loaded from .../checkpoints/scaler.pkl
INFO:__main__:Connected to InfluxDB
INFO:__main__:Starting anomaly detection inference loop...
INFO:__main__:Reconstruction error: 0.1234, Anomaly: 0
```
