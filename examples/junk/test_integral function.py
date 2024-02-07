
from scipy.stats import norm
import numpy as np

def approximate_integral(data, mean, std_dev):
    """
    Approximate the integral of the PDF over intervals around each point in the data array.

    Parameters:
    - data: numpy array of sample points.
    - mean: Mean of the normal distribution.
    - std_dev: Standard deviation of the normal distribution.
    - interval_width: Width of the interval around each sample point.

    Returns:
    - integral_approximation: Approximation of the integral of the PDF over the sample points.
    """
    interval_width = 1/500 #1 / data.size

    # Calculate the CDF at the upper and lower bounds of the intervals around each point
    upper_bounds = norm.cdf(data + interval_width , mean, std_dev)
    lower_bounds = norm.cdf(data - interval_width , mean, std_dev)

    # The probability of each interval is the difference between these CDF values
    interval_probabilities = upper_bounds - lower_bounds

    # Sum the probabilities to approximate the integral of the PDF over these intervals
    integral_approximation = np.sum(interval_probabilities)

    return integral_approximation


# Example usage
data = np.random.uniform(low=0.8, high=1.2, size=(100,))

mean = 1  # Mean of the normal distribution
std_dev = 0.1  # Standard deviation of the normal distribution

# Approximate the integral of the PDF over intervals around the sample points
integral_approximation = approximate_integral(data, mean, std_dev)

print(f"Approximated integral of the PDF over the sample points: {integral_approximation}")
