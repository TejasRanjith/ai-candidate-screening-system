# The Hundred-Page Machine Learning Book (Andriy Burkov)
## Chapter 3: Fundamental Algorithms

### Linear and Logistic Regression
Linear regression models the conditional expectation of target $y$ given input $x$ as a linear combination of features:
$$\hat{y} = w^T x + b$$
The parameters $w$ (weights) and $b$ (bias) are obtained analytically via the Ordinary Least Squares (OLS) normal equation:
$$w^* = (X^T X)^{-1} X^T y$$
or iteratively via gradient descent when $X^T X$ is ill-conditioned or computationally intractable due to large dimensionalities.

Logistic regression adapts linear models to classification by passing the linear logit through the sigmoid activation function $\sigma(z) = \frac{1}{1 + e^{-z}}$:
$$P(Y=1|X=x) = \sigma(w^T x + b)$$
The weights are updated using gradient ascent on the log-likelihood or gradient descent on the binary cross-entropy loss. Because logistic regression produces calibrated probabilities, it serves as an interpretable baseline for binary decision problems.

### Support Vector Machines (SVM)
The Support Vector Machine constructs an optimal separating hyperplane that maximizes the margin—the geometric distance between the decision boundary and the closest data points of any class (the support vectors).
For linearly separable data, the primal optimization problem is:
$$\min_{w, b} \frac{1}{2} \|w\|^2 \quad \text{subject to} \quad y_i(w^T x_i + b) \geq 1, \, \forall i$$
For non-separable data, slack variables $\xi_i \geq 0$ and a regularization penalty $C$ allow soft-margin classification:
$$\min_{w, b, \xi} \frac{1}{2} \|w\|^2 + C \sum_{i=1}^N \xi_i \quad \text{subject to} \quad y_i(w^T x_i + b) \geq 1 - \xi_i$$
Through the Dual Formulation and the Kernel Trick (e.g., Radial Basis Function $K(x, z) = \exp(-\gamma \|x - z\|^2)$), SVMs map inputs into high-dimensional Hilbert spaces where non-linear boundaries become linear.

### Decision Trees and k-Nearest Neighbors (k-NN)
Decision trees perform recursive greedy partitioning of feature space using impurity measures such as Gini Impurity $G = 1 - \sum p_k^2$ or Information Entropy $H = -\sum p_k \log_2 p_k$. While highly interpretable, unpruned decision trees exhibit high variance and easily overfit noisy samples.
k-Nearest Neighbors (k-NN) is a non-parametric, instance-based lazy learning method where predictions for test point $x$ are calculated by majority vote or distance-weighted average over the $k$ nearest training samples using metric distances (Euclidean, Manhattan, or Cosine). k-NN suffers severely from the curse of dimensionality, where distance metrics lose discrimination power in sparse high-dimensional spaces.
