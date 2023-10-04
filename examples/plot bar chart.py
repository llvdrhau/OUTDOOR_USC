import matplotlib.pyplot as plt

# Data
labels = ['D1', 'D2', 'D3', 'Dn']
values = [2, 3, 7, 1]

# Create a bar plot
plt.bar(labels, values)

# Adding labels and title
plt.xlabel('Designs')
plt.ylabel('# Occurences')
plt.title('Distribution of pathways')

# Display the plot
plt.show()
