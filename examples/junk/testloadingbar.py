import time

def simple_loading_bar(iterations, total, length=50):
    for i in range(iterations):
        progress = (i + 1) / total  # Increment progress as the loop iterates
        bar_length = int(length * progress)
        loading_bar = "[" + "=" * bar_length + " " * (length - bar_length) + "]"
        percentage = int(progress * 100)
        print(f"\r{loading_bar} {percentage}% complete", end="", flush=True)
        time.sleep(0.1)  # Simulate some work being done

# Total number of iterations in your for loop
total_iterations = 100

# Run your for loop
for i in range(total_iterations):
    # Your loop logic here

    # Update the loading bar
    simple_loading_bar(i + 1, total_iterations)

# Print a newline to start a new line after the loading bar
print()
