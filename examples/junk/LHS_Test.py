import numpy as np
from scipy.stats import norm
from pyDOE import lhs

# Define your parameters and their distributions
# Assuming 'parameters' is a dictionary containing your parameters, mean, and std deviation as a percentage of the mean
# Example:
# parameters = {
#     'param1': {'mean': 100, 'std_percent': 5},
#     'param2': {'mean': 50, 'std_percent': 10},
#     ...
# }

parameters = {
    'param1': {'mean': 100, 'std_percent': 5},
    'param2': {'mean': 50, 'std_percent': 10},
    # Add more parameters as needed
}

num_params = len(parameters)
num_samples = 100

# Generate LHS sample
lhs_sample = lhs(num_params, samples=num_samples)

# Prepare to store sampled values
sampled_values = np.zeros((num_samples, num_params))

# Convert LHS samples to match the specified distributions
for i, (param, stats) in enumerate(parameters.items()):
    mean = stats['mean']
    std_dev = (stats['std_percent'] / 100.0) * mean
    # Convert uniform sample (lhs_sample) to the distribution of the parameter
    # For normal distribution, use the ppf (percent point function, or inverse of cdf)
    sampled_values[:, i] = norm.ppf(lhs_sample[:, i], loc=mean, scale=std_dev)

# sampled_values now contains your sampled combinations
