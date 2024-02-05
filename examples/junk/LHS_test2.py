import numpy as np
from scipy.stats import norm, uniform
from pyDOE import lhs

# Define your parameters and their distributions
# Now, also specify the type of distribution ('uniform' or 'normal')
# Example:
# parameters = {
#     'param1': {'mean': 100, 'std_percent': 5, 'type': 'normal'},
#     'param2': {'lower': 30, 'upper': 60, 'type': 'uniform'},
#     ...
# }

parameters = {
    'param1': {'mean': 100, 'std_percent': 5, 'type': 'normal'},
    'param2': {'lower': 30, 'upper': 60, 'type': 'uniform'},
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
    distribution_type = stats['type']
    if distribution_type == 'normal':
        mean = stats['mean']
        std_dev = (stats['std_percent'] / 100.0) * mean
        # Convert uniform sample (lhs_sample) to normal distribution
        sampled_values[:, i] = norm.ppf(lhs_sample[:, i], loc=mean, scale=std_dev)
    elif distribution_type == 'uniform':
        lower = stats['lower']
        upper = stats['upper']
        # Scale LHS sample to the range of the uniform distribution
        sampled_values[:, i] = uniform.ppf(lhs_sample[:, i], loc=lower, scale=upper-lower)
    else:
        raise ValueError(f"Unsupported distribution type: {distribution_type}")

# sampled_values now contains your sampled combinations
