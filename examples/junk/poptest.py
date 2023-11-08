# Example dictionary where the key is a tuple
my_dict = {
    (1, 'a', 'X'): 'value1',
    (2, 'b', 'Y'): 'value2',
    (3, 'c', 'X'): 'value3',
    (4, 'd', 'Z'): 'value4',
    (5, 'e', 'X'): 'value5',
}

# The specific value for the last element in the tuple that we want to remove
value_to_remove = 'X'

# Create a list of keys to remove
keys_to_remove = [key for key in my_dict if key[-1] == value_to_remove]

# Pop elements from the dictionary
for key in keys_to_remove:
    my_dict.pop(key, None)  # The `None` is to avoid KeyError if the key is not found

# Print the modified dictionary
print(my_dict)
