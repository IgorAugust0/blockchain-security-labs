# Selfish Mining Detector

## Overview

This Python script implements a permutation test to detect selfish mining behavior in blockchain networks. It analyzes sequences of consecutive mining by the most powerful miner to determine if they are statistically significant, which could indicate selfish mining practices.

## Features

- **Data Loading**: Reads mining data from numpy array files
- **Monthly Analysis**: Splits data into monthly segments for detailed analysis
- **Statistical Testing**: Implements permutation testing to detect unusual mining patterns
- **Visualization**: Plots computational power distribution over time
- **P-value Analysis**: Calculates statistical significance of mining sequences

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/IgorAugust0/tesi.git
   cd lab/selfish-mining
   ```

2. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

3. **Run the Script**:
   ```bash
   python selfmin.py
   ```
   or
   ```bash
   python paste.txt
   ```

## Usage

### Direct Script Execution

The script can be run directly with default parameters:

```python
python selfmin.py
```

### Custom Implementation

```python
from selfmin import load_data, split_into_months, get_most_powerful_miner

# Load your data
data = load_data("your_data.npy")

# Split into months
monthly_data = split_into_months(data)

# Analyze specific month (e.g., November)
november = monthly_data[10]  # 0-indexed

# Find most powerful miner
mp = get_most_powerful_miner(november)
```

## How It Works

1. **Data Processing**:

   - Loads blockchain mining data from a numpy array
   - Splits data into monthly segments
   - Identifies the most powerful miner

2. **Statistical Analysis**:

   - Generates random permutations of the mining sequence
   - Counts consecutive mining sequences
   - Calculates p-value through permutation testing

3. **Result Interpretation**:
   - If p-value < 0.05: Likely selfish mining
   - If p-value ≥ 0.05: No evidence of selfish mining

## Requirements

- Python 3.6+
- numpy
- matplotlib
- scipy

See `requirements.txt` for specific versions.

## Example Output

The script provides both visual and textual output:

- Graph showing computational power distribution
- P-value calculation
- Conclusion about potential selfish mining behavior

## License

This project is licensed under the MIT License. See the [LICENSE](../../LICENSE) file for details.
