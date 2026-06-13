# InfluxDB Integration Setup Guide

## Overview
The `model_to_db.py` script performs real-time anomaly detection using your trained LSTM autoencoder and writes results to InfluxDB.

**How it works:**
1. Queries the last 30 minutes of reactor data from InfluxDB
2. Scales the data using the training scaler
3. Feeds it through the LSTM autoencoder
4. Computes reconstruction error (anomaly score)
5. Flags as anomaly if error exceeds threshold
6. Writes results back to InfluxDB

## Prerequisites

### 1. Environment Variables
Create or update your `.env` file in the `/workspace/model/` directory:

```bash
INFLUXDB_URL=http://localhost:8086
INFLUXDB_TOKEN=your_influxdb_token_here
INFLUXDB_ORG=your_org_name
INFLUXDB_BUCKET=reactor_data
```

Get these from your InfluxDB Cloud/Server admin panel.

### 2. Trained Model Files
Ensure these files exist in `checkpoints/`:

- **best_model.pth** - Trained model weights ✓ (already present)
- **scaler.pkl** - Feature scaler from training ✗ (needs to be created)

### 3. Save the Scaler During Training

**Option A: Update your training script (recommended)**

After training, add this to your `main.py`:

```python
from src.utils import save_scaler

# ... your training code ...

# After training completes:
dataloader = RBMKDataLoader(data_path)
dataloader.load_and_preprocess()  # This fits the scaler

save_scaler(dataloader.scaler, "checkpoints/scaler.pkl")
```

**Option B: Quick fix (one-time)**

Run this Python snippet to save the current scaler:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(".") / "src"))

from dataset import RBMKDataLoader
from utils import save_scaler

# Load data (this will create the scaler)
dataloader = RBMKDataLoader(data_path="data/")
dataloader.load_and_preprocess()

# Save scaler
save_scaler(dataloader.scaler, "checkpoints/scaler.pkl")
print("✓ Scaler saved!")
```

## Configuration

Open `model_to_db.py` and adjust these parameters if needed:

```python
SEQ_LEN = 30              # Sequence length (must match training)
INPUT_SIZE = 4            # Number of features
HIDDEN_SIZE = 64          # Model hidden size (must match training)
NUM_LAYERS = 2            # Number of LSTM layers (must match training)
THRESHOLD = 0.5           # MSE threshold (adjust to reduce false alarms)
```

### Tuning the THRESHOLD
- **Threshold too low** → Many false alarms
- **Threshold too high** → Miss real anomalies
- **Typical range**: 0.3 - 1.0 depending on your data
- **Start with**: 0.5, then adjust based on results

## Running the Integration

### Start InfluxDB (if not running)
```bash
docker-compose up -d influxdb
```

### Run the inference script
```bash
cd /workspace/model
python model_to_db.py
```

### Expected Output
```
INFO:__main__:Model loaded from .../checkpoints/best_model.pth
INFO:__main__:Scaler loaded from .../checkpoints/scaler.pkl
INFO:__main__:Connected to InfluxDB
INFO:__main__:Starting anomaly detection inference loop...
INFO:__main__:Reconstruction error: 0.2345, Anomaly: 0
INFO:__main__:Reconstruction error: 0.2156, Anomaly: 0
INFO:__main__:Reconstruction error: 0.7832, Anomaly: 1  ← Anomaly detected!
...
```

### Stop the script
Press `Ctrl+C` to gracefully shutdown.

## Monitoring Results in InfluxDB

Query your anomalies in InfluxDB:

```flux
from(bucket: "reactor_data")
  |> range(start: -1h)
  |> filter(fn: (r) => r._measurement == "lstm_anomaly_detection")
  |> filter(fn: (r) => r._field == "is_anomaly")
```

## Troubleshooting

### Error: "Scaler not found at checkpoints/scaler.pkl"
**Solution**: Follow "Save the Scaler During Training" section above

### Error: "Failed to connect to InfluxDB"
**Check:**
- InfluxDB is running: `docker-compose ps`
- Credentials in `.env` are correct
- InfluxDB URL is accessible: `curl -I http://localhost:8086`

### Error: "No data retrieved"
**Check:**
- InfluxDB bucket name is correct in `.env`
- Data exists in InfluxDB: check data/measurement names
- Query measurement name matches: should be `reactor_sim`

### High reconstruction errors?
**Possible causes:**
- Different features or scaling than training
- New/unseen reactor conditions
- Model not trained well on your data
- **Solution**: Retrain the model on current data

### Too many false alarms?
**Solution**: Increase `THRESHOLD` value (e.g., 0.5 → 0.7)

## Data Flow Diagram

```
InfluxDB (raw reactor data)
         ↓
    Query 30-min window
         ↓
  Normalize with scaler
         ↓
 LSTM Autoencoder
         ↓
Reconstruction Error (MSE)
         ↓
Compare with threshold
         ↓
Write result to InfluxDB
         ↓
Repeat every 10 seconds
```

## Next Steps

1. ✓ Fix scaler saving (see above)
2. Run `python main.py --mode train` to train (this saves scaler)
3. Verify scaler was saved: `ls -la checkpoints/scaler.pkl`
4. Update `.env` with your InfluxDB credentials
5. Run `python model_to_db.py`
6. Monitor results in InfluxDB

## Advanced: Running as a Service

To run in background, use `nohup` or systemd:

```bash
# Option 1: nohup
nohup python model_to_db.py > anomaly_detection.log 2>&1 &

# Option 2: systemd (create /etc/systemd/system/anomaly-detector.service)
[Unit]
Description=RBMK Anomaly Detector
After=network.target

[Service]
Type=simple
User=username
WorkingDirectory=/workspace/model
ExecStart=/usr/bin/python3 model_to_db.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then: `sudo systemctl start anomaly-detector`
