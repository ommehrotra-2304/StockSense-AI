from pathlib import Path
import subprocess, sys

ROOT = Path(__file__).resolve().parents[1]
steps = [
    "generate_data.py",
    "prepare_features.py",
    "train_model.py",
    "forecast_and_recommend.py",
    "build_database.py",
]
for step in steps:
    print(f"\n=== Running {step} ===")
    subprocess.run([sys.executable, str(ROOT / "scripts" / step)], check=True)
print("\nStockSense AI pipeline completed successfully.")
