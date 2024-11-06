import os
import json
from collections import defaultdict
from typing import Dict, List, Set, Iterator
from dataclasses import dataclass
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

@dataclass
class Transaction:
    hash: str
    time: int
    inputs: List[Dict]
    outputs: List[Dict]

class BitcoinClusterAnalyzer:
    def __init__(self, raw_addr_folder: str):
        """
        Initializes the BitcoinClusterAnalyzer object.
        Args:
            raw_addr_folder (str): Path to the folder containing JSON files of Bitcoin addresses.
        """
        self.raw_addr_folder = raw_addr_folder
        # Set to store all addresses that belong to the cluster.
        self.cluster: Set[str] = set()
        # Dictionary to store transactions, grouped by addresses.
        self.transactions: Dict[str, List[Transaction]] = defaultdict(list)
        # Stores the historical balance for the cluster over time, keyed by timestamp.
        self.historical_balance: Dict[int, int] = defaultdict(int)
        # Tracks any missing files during data loading.
        self.missing_files: Set[str] = set()

    def load_address_data(self, address: str) -> None:
        """
        Loads the transactions associated with a given Bitcoin address from a JSON file.
        Args:
            address (str): Bitcoin address to load data for.
        """
        filepath = os.path.join(self.raw_addr_folder, f"{address}.json")
        try:
            # Open the JSON file containing transaction data for the address.
            with open(filepath, 'r') as file:
                data = json.load(file)
                # Convert JSON transaction data into Transaction objects.
                self.transactions[address] = [
                    Transaction(
                        hash=tx['hash'],
                        time=tx['time'],
                        inputs=tx['inputs'],
                        outputs=tx['out']
                    ) for tx in data['txs']
                ]
        except FileNotFoundError:
            # Log missing files for further handling.
            self.missing_files.add(address)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for address {address}")
        except KeyError as e:
            print(f"Missing key in JSON data for address {address}: {e}")

    def cluster_address(self, start_address: str) -> None:
        """
        Builds a cluster of Bitcoin addresses that are linked through transactions.
        Args:
            start_address (str): The starting address to build the cluster from.
        """
        self.cluster.add(start_address)  # Add starting address to the cluster.
        to_process = {start_address}     # A set of addresses to process.

        # Process addresses iteratively until no more new addresses are added.
        while to_process:
            current_address = to_process.pop()
            self.load_address_data(current_address)  # Load transactions for the current address.

            for tx in self.transactions[current_address]:
                # Collect addresses from transaction inputs and outputs.
                new_addresses = set()
                new_addresses.update(inp['prev_out']['addr'] for inp in tx.inputs if 'prev_out' in inp and 'addr' in inp['prev_out'])
                new_addresses.update(out['addr'] for out in tx.outputs if 'addr' in out)
                
                # Add new addresses to the cluster and queue them for processing.
                new_cluster_addresses = new_addresses - self.cluster
                self.cluster.update(new_cluster_addresses)
                to_process.update(new_cluster_addresses)

    def calculate_historical_balance(self) -> None:
        """
        Calculates the balance of the entire cluster over time by tracking the transaction history.
        """
        balance = 0  # Start with a zero balance.
        
        # Iterate over each address in the cluster.
        for address in self.cluster:
            # Sort transactions by time and process them sequentially.
            for tx in sorted(self.transactions[address], key=lambda x: x.time):
                # Subtract values from the inputs (spending).
                for inp in tx.inputs:
                    if 'prev_out' in inp and inp['prev_out'].get('addr') == address:
                        balance -= inp['prev_out']['value']
                
                # Add values from the outputs (receiving).
                for out in tx.outputs:
                    if out.get('addr') == address:
                        balance += out['value']
                
                # Record the balance at the current transaction's timestamp.
                self.historical_balance[tx.time] = balance

    def _get_cluster_values(self) -> Iterator[int]:
        """
        Yields the net transaction flow values within the cluster (absolute values).
        Returns:
            Iterator[int]: An iterator of absolute transaction values.
        """
        for address in self.cluster:
            for tx in self.transactions[address]:
                # Calculate the net flow of values for each transaction.
                inputs_sum = sum(inp['prev_out']['value'] for inp in tx.inputs if 'prev_out' in inp and inp['prev_out'].get('addr') in self.cluster)
                outputs_sum = sum(out['value'] for out in tx.outputs if out.get('addr') in self.cluster)
                net_flow = outputs_sum - inputs_sum
                if net_flow != 0:
                    yield abs(net_flow)  # Return only non-zero absolute values.

    def calculate_gini(self, values: List[int]) -> float:
        """
        Calculates the Gini coefficient to measure inequality within the cluster.
        Remove the values parameter if using the method to get cluster values.
        Returns:
            float: The calculated Gini coefficient.
        """
        # Sort the cluster values (transaction net flows or balances) in ascending order.
        # values = sorted(self._get_cluster_values())
        values = sorted(values)
        n = len(values)  # Get the number of values.
        index = np.arange(1, n + 1)  # Create an array of indices for the values.
        
        # Calculate the Gini coefficient using the formula.
        return ((2 * np.sum(index * values) / (n * np.sum(values))) - (n + 1) / n)

    def apply_benfords_law(self) -> Dict[str, Dict[int, float]]:
        """
        Applies Benford's Law to check if the first digits of transaction values follow expected distribution.
        Returns:
            dict: A dictionary containing observed frequencies, expected frequencies, chi-square value, and p-value.
        """
        # Get the first digits of all cluster transaction values.
        values = [int(str(value)[0]) for value in self._get_cluster_values()]
        observed_freq = np.bincount(values)[1:] / len(values)  # Calculate observed frequencies (ignore zero).
        expected_freq = np.log10(1 + 1 / np.arange(1, 10))     # Calculate expected Benford's distribution.
        
        # Perform chi-square test to compare observed vs expected frequencies.
        chi_square, p_value = stats.chisquare(observed_freq, expected_freq)

        # Return observed frequencies, expected frequencies, and test results.
        return {
            "observed": dict(enumerate(observed_freq, 1)),
            "expected": dict(enumerate(expected_freq, 1)),
            "chi_square": chi_square,
            "p_value": p_value
        }

    def analyze(self, start_address: str) -> Dict:
        """
        Orchestrates the entire analysis of a Bitcoin address cluster.
        Args:
            start_address (str): The starting address to analyze.
        Returns:
            dict: A summary of the analysis, including cluster size, Gini coefficient, and Benford's Law analysis.
        """
        print(f"Starting analysis for address: {start_address}")
        self.cluster_address(start_address)  # Build the address cluster.
        print(f"Cluster size: {len(self.cluster)} addresses")
        
        # Calculate the historical balance of the cluster.
        self.calculate_historical_balance()
        print("Historical balance calculated")
        
        # Calculate the Gini coefficient for the cluster's transaction values.
        gini = self.calculate_gini(list(self.historical_balance.values()))
        print(f"Gini coefficient: {gini:.4f}")
        
        # Perform Benford's Law analysis on the cluster.
        benfords = self.apply_benfords_law()
        print(f"Benford's Law analysis completed. Chi-square: {benfords['chi_square']:.4f}, p-value: {benfords['p_value']:.4f}")

        # Generate cluster values list
        # cluster_values = list(self._get_cluster_values())

        # Notify the user if any files were missing during the analysis.
        if self.missing_files:
            print(f"\nAnalysis complete. {len(self.missing_files)} address files were not found.")
        else:
            print("\nAnalysis complete. All address files were found and processed.")

        # Return a detailed summary of the results.
        return {
            "cluster_size": len(self.cluster),
            "historical_balance": dict(self.historical_balance),
            # "cluster_values": cluster_values,
            "gini_coefficient": gini,
            "benfords_law": benfords,
            "addresses_without_data": len(self.missing_files)
        }

def plot_results(results: Dict) -> None:
    """
    Plots the results of the Bitcoin cluster analysis, including historical balance, Gini coefficient, and Benford's Law.
    Args:
        results (Dict): Dictionary containing the results of the analysis.
    """
    # Historical Balance Plot
    plt.figure(figsize=(10, 6))
    plt.plot(list(results['historical_balance'].keys()), list(results['historical_balance'].values()))
    plt.title("Historical Balance Over Time")
    plt.xlabel("Time")
    plt.ylabel("Balance")
    plt.show()

    # Gini Coefficient Visualization
    # cluster_values = results['cluster_values']
    # values = sorted(cluster_values)  # Sort cluster values.
    values = sorted(results['historical_balance'].values())  # Sort historical balance values.
    lorenz = np.cumsum(values) / np.sum(values)  # Calculate Lorenz curve for the Gini coefficient.
    plt.figure(figsize=(10, 6))
    plt.plot([0, 1], [0, 1], label="Perfect Equality")  # Line representing perfect equality.
    plt.plot(np.linspace(0, 1, len(lorenz)), lorenz, label=f"Lorenz Curve (Gini: {results['gini_coefficient']:.2f})")
    plt.title("Gini Coefficient Visualization")
    plt.xlabel("Cumulative Share of Addresses")
    plt.ylabel("Cumulative Share of Value")
    plt.legend()
    plt.show()

    # Benford's Law Visualization
    benford = results['benfords_law']
    plt.figure(figsize=(10, 6))
    plt.bar(benford['observed'].keys(), benford['observed'].values(), alpha=0.5, label="Observed")
    plt.plot(benford['expected'].keys(), benford['expected'].values(), 'r-', label="Expected (Benford's Law)")
    plt.title(f"Benford's Law Distribution Comparison\nChi-square: {benford['chi_square']:.2f}, p-value: {benford['p_value']:.4f}")
    plt.xlabel("First Digit")
    plt.ylabel("Frequency")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    # Initialize the BitcoinClusterAnalyzer with the path to address data.
    analyzer = BitcoinClusterAnalyzer('rawaddr')
    
    # Analyze the Bitcoin address cluster starting from a specific address.
    results = analyzer.analyze("1JHH1pmHujcVa1aXjRrA13BJ13iCfgfBqj")
    
    # Print detailed results of the analysis.
    print("\nDetailed Results:")
    print(json.dumps(results, indent=2))
    
    # Plot the results including historical balance, Gini coefficient, and Benford's Law.
    plot_results(results)

