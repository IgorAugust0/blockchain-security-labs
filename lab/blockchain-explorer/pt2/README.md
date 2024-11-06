# Blockchain Explorer - Part 2

## Overview

This is the part two of the Blockchain Explorer project, which serve as comprehensive Python script designed to analyze Bitcoin transactions by identifying clusters of addresses and evaluating various financial metrics. This tool calculates historical balances, measures wealth inequality using the Gini coefficient, and applies Benford's Law to the first digits of transaction values to detect anomalies. UUnlike part one, which relied on the Blockchain.info API for real-time data, part two processes data locally from a provided dataset/cluster named "rawaddr". This approach allows for more in-depth and customizable analysis of Bitcoin transactions.

## Features

- **Cluster Addressing**: Identifies clusters of Bitcoin addresses based on transaction history.
- **Historical Balance Calculation**: Computes the historical balance of addresses over time.
- **Gini Coefficient Calculation**: Measures income inequality within the address cluster using the Gini coefficient.
- **Benford's Law Analysis**: Compares the distribution of first digits in transaction values against Benford's Law.
- **Visualization**: Plots historical balance, Gini coefficient, and Benford's Law distributions.

## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/IgorAugust0/tesi.git
   cd lab/blockchain-explorer/pt2
   ```

2. **Extract the compressed cluster**:

   ```bash
   tar -xzf rawaddr.tgz
   ```
   > This will create a 'rawaddr' directory needed for analysis

3. **Install Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Script**:

   ```bash
   python blockchain_explorer2.py
   ```
   or

   ```bash
   python paste.txt
   ```

   > This will analyze a specific Bitcoin address and display the results in the console.

## Usage

### Initialization

Create an instance of `BitcoinClusterAnalyzer` with the path to your address data.

```python
analyzer = BitcoinClusterAnalyzer('path/to/rawaddr')
```

### Analyze

Call the `analyze` method with the starting address for clustering.

```python
results = analyzer.analyze("1JHH1pmHujcVa1aXjRrA13BJ13iCfgfBqj")
```

### Results

The `analyze` method returns a dictionary with the following keys:

- `cluster_size`: Number of addresses in the cluster.
- `historical_balance`: Dictionary of historical balances over time.
- `gini_coefficient`: Calculated Gini coefficient.
- `benfords_law`: Results of Benford's Law analysis, including observed and expected frequencies, chi-square, and p-value.
- `addresses_without_data`: Number of addresses with missing data.

### Plotting Results

Use the `plot_results` function to visualize the results.

```python
plot_results(results)
```

## Code Explanation

- **Class `Transaction`**: Represents a Bitcoin transaction with hash, time, inputs, and outputs.
- **Class `BitcoinClusterAnalyzer`**:
  - `load_address_data(address)`: Loads transaction data for a given address.
  - `cluster_address(start_address)`: Builds clusters of addresses starting from a specified address.
  - `calculate_historical_balance()`: Computes the balance history for clustered addresses.
  - `_get_cluster_values()`: Yields net transaction flows for clustered addresses.
  - `calculate_gini()`: Computes the Gini coefficient based on transaction values.
  - `apply_benfords_law()`: Analyzes transaction values against Benford's Law.
  - `analyze(start_address)`: Orchestrates the analysis process and returns results.

## Gini Coefficient Calculation

When calculating the Gini coefficient for a Bitcoin cluster, you have two main options for determining the values to use in the calculation: `historical_balance` and the values obtained from `_get_cluster_values()`.

- **Historical Balance**: Measures long-term wealth inequality based on the historical balance over time for the entire cluster.
- **Cluster Values**: Measures transactional inequality based on the net flow of transaction values.

Both options are available in the script, but the `historical_balance` option is used by default. If you want to try the `cluster_values` option, you can uncomment the relevant lines in the script.

## Example

```python
if __name__ == "__main__":
    analyzer = BitcoinClusterAnalyzer('rawaddr')
    results = analyzer.analyze("1JHH1pmHujcVa1aXjRrA13BJ13iCfgfBqj")
    print("\nDetailed Results:")
    print(json.dumps(results, indent=2))
    plot_results(results)
```

## Requirements

- `numpy`
- `scipy`
- `matplotlib`
- `json`
- `dataclasses`
- `typing`

These dependencies are listed in the `requirements.txt` file. You can install them using the following command:

```bash
pip install -r requirements.txt
```

## License

This project is licensed under the [MIT Licence](../../../LICENSE). Feel free to use, modify, and distribute the code for educational or commercial purposes.
