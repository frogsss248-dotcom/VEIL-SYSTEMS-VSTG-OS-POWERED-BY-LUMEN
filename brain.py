import numpy as np

# Input training data
inputs = np.array([
    [0, 0],
    [0, 1],
    [1, 0],
    [1, 1]
])

# Expected outputs
outputs = np.array([
    [0],
    [1],
    [1],
    [1]
])

# Random starting weights
weights = np.random.rand(2, 1)

# Sigmoid activation function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))

# Derivative for learning
def sigmoid_derivative(x):
    return x * (1 - x)

# Training loop
for epoch in range(10000):

    # Forwrd pass
    layer = sigmoid(np.dot(inputs, weights))

    # Calculate error
    error = outputs - layer

    # Calculate adjustments
    adjustments = error * sigmoid_derivative(layer)

    # Adjust weights
    weights += np.dot(inputs.T, adjustments) * 0.1

# Final results
print("Final outputs:")
print(layer)

print("\nWeights:")
print(weights)