import numpy as np
import matplotlib.pyplot as plt
from collections import Counter
from itertools import groupby
from scipy import stats

"""
This code implements a permutation test to check if the sequence of consecutive mining by the most powerful miner (MP) is significantly longer than expected by chance, given the computational power of the MP.

The permutation test is a way to test if the observation made in the data could have happened by chance. In this case, we are analyzing the longest sequence of consecutive mining by the MP in November. To determine if this sequence is significant, we generate 1000 permutations of the November data, keeping the computational power of the MP constant, and count the longest sequence of consecutive mining by the MP in each permutation. This gives us a distribution of the longest sequences we would expect to see by chance.

We compare the observed longest sequence with this distribution. If the observed sequence is longer than most of the sequences in the permutation distribution, this suggests that consecutive mining by the MP is unlikely to have occurred by chance and may be the result of selfish mining.

The calculated p-value is the proportion of permutations in which the longest sequence is equal to or greater than the observed sequence. If the p-value is small (usually less than 0.05), this indicates that the observed sequence is significantly longer than expected by chance, suggesting selfish mining.

Random permutation is used to generate the mining sequences for comparison. The function np.random.permutation creates a new random order of the mining data for each permutation. This creates a distribution of "alternative scenarios" that represent what could have happened if mining were a purely random process, without selfish mining. By comparing the real mining sequence with these alternative scenarios, we can determine if the real sequence is significantly different from what is expected by chance.
"""

# use: pip install scipy

# Constants
BLOCK = "block_integer_array.npy"
SIGNIFICANCE_LEVEL = 0.05


def load_data(filename):
    """CLoads the data from the specified file and returns it as a numpy array."""
    try:
        return np.load(filename)
    except FileNotFoundError:
        print(f"Erro: O arquivo {filename} não foi encontrado.")
        return None


def split_into_months(data_array):
    """Splits the data array into 12 parts, one for each month.
    However, if the number of elements is not divisible by 12,
    this function needs to be adapted to resize the data to the largest multiple of 12.
    """

    trunc_len = (len(data_array) // 360) * 360
    return data_array[:trunc_len].reshape(-1, 30)
    # return np.array_split(data_array, 12)


def get_month(monthly_data, month):
    return monthly_data[month - 1]  # 0-indexado


# def plot_data(monthly_data):
#     plt.hist(monthly_data, bins=30)
#     plt.title("Poder computacional por dia em Novembro")
#     plt.show()


def plot_data(monthly_data):
    # Extrai os dias e o poder computacional
    days = range(1, len(monthly_data) + 1)
    power = monthly_data

    plt.figure(figsize=(6, 4))
    plt.plot(days, power, alpha=0.7)
    plt.title("Poder computacional por dia em Novembro")
    plt.xlabel("Dia")
    plt.ylabel("Poder Computacional")
    plt.show()


def get_most_powerful_miner(monthly_data):
    """Returns the most powerful miner based on the provided monthly data,
    from the first element of the first tuple (most common) in the list
    of tuples returned by the most_common method of the Counter object."""
    counter = Counter(monthly_data)
    return counter.most_common(1)[0][0]


def count_sequences(month_data, miner):
    """Counts the number of consecutive mining sequences performed by the specified miner (mp).
    The groupby method from the itertools module is used to group consecutive elements in the data array.
    """
    return [sum(1 for _ in group) for key, group in groupby(month_data) if key == miner]


def generate_permutations(data, miner, num_permutations=1000):
    """Generates random permutations of the data and counts the number of consecutive mining sequences
    performed by the most powerful miner (mp) in each permutation."""
    perm_sequences = []
    for _ in range(num_permutations):
        perm = np.random.permutation(data)
        perm_sequences.append(count_sequences(perm, miner))
    return perm_sequences


def calc_pvalue(sequences, perm_sequences):
    """Calculates the p-value for the mining sequence of the most powerful miner
    based on the generated permutations and returns the percentile of the maximum
    sequence value of the mp relative to the permutations."""
    max_perm_sequences = [max(seq) for seq in perm_sequences]
    max_sequences = max(sequences)
    return stats.percentileofscore(max_perm_sequences, max_sequences)


def print_conclusion(pvalue, significance_level):
    pvalue_rounded = round(pvalue, 2)
    print(f"p-value: {pvalue_rounded}")
    if pvalue < significance_level:
        print(
            f"Selfish mining likely occurred (p-value: {pvalue_rounded} < {significance_level}).\nThe mining sequence of the most powerful miner is significantly longer than expected by chance, i.e., different from what would be expected if the null hypothesis were true."
        )
    else:
        print(
            f"Selfish mining likely did not occur (p-value: {pvalue_rounded} >= {significance_level}).\nThe mining sequence of the most powerful miner is not significantly longer than expected by chance, i.e., not different from what would be expected if the null hypothesis were true."
        )


def main():
    data_array = load_data(BLOCK)
    monthly_data = split_into_months(data_array)
    # november = get_month(monthly_data, 11)
    november = monthly_data[10]  # 0-indexed
    plot_data(november)
    mp = get_most_powerful_miner(november)
    sequences = count_sequences(november, mp)
    perm_sequences = generate_permutations(november, mp)
    pvalue = calc_pvalue(sequences, perm_sequences)
    print_conclusion(pvalue, SIGNIFICANCE_LEVEL)


if __name__ == "__main__":
    main()
