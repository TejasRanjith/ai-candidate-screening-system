# The Hundred-Page Machine Learning Book (Andriy Burkov)
## Chapter 2: Notation, Definitions, and Fundamental Concepts

### Supervised Learning Foundations
Supervised learning is a machine learning paradigm where an algorithm learns a mapping function from input features $X$ to output targets $Y$ based on labeled training pairs $(x_i, y_i)_{i=1}^N$. The feature vector $x \in \mathbb{R}^D$ represents the attributes of an instance, while $y$ can be a continuous scalar (in regression) or a discrete categorical label (in classification).

The true underlying data-generating distribution is denoted as $P(X, Y)$. The goal of the learning algorithm is to select a hypothesis function $h \in \mathcal{H}$ that minimizes the expected risk (or generalization error), defined as:
$$R(h) = \mathbb{E}_{(x, y) \sim P}[L(h(x), y)]$$
where $L(\cdot, \cdot)$ is a non-negative loss function measuring discrepancy between predicted and true labels.

Because the true joint distribution $P(X, Y)$ is unknown, the algorithm minimizes the Empirical Risk over the observed training set $S$:
$$R_{emp}(h) = \frac{1}{N} \sum_{i=1}^N L(h(x_i), y_i)$$
Minimizing this empirical quantity is known as Empirical Risk Minimization (ERM). However, direct ERM without constraints often leads to overfitting, where the chosen model fits idiosyncrasies and noise in the training sample rather than generalizable structure.

### Classification vs Regression
In binary classification, $y \in \{-1, +1\}$ or $y \in \{0, 1\}$. Multi-class classification extends this to $y \in \{1, \dots, C\}$. Regression tasks predict a real-valued outcome $y \in \mathbb{R}$. 
Common loss functions include:
- Mean Squared Error (MSE): $L(y, \hat{y}) = \frac{1}{2}(y - \hat{y})^2$, optimal under Gaussian error assumptions.
- Binary Cross-Entropy (Log Loss): $L(y, \hat{y}) = - [y \log \hat{y} + (1 - y) \log(1 - \hat{y})]$, representing the negative log-likelihood of Bernoulli variables.
- Hinge Loss: $L(y, \hat{y}) = \max(0, 1 - y \cdot \hat{y})$, used in Support Vector Machines to construct maximum margin classifiers.
