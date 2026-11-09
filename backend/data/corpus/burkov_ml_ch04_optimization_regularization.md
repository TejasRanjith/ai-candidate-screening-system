# The Hundred-Page Machine Learning Book (Andriy Burkov)
## Chapter 4: Anatomy of a Learning Algorithm

### Optimization and Gradient Descent
Virtually all parametric machine learning models solve an optimization problem where loss function $J(w)$ is minimized with respect to parameter vector $w$. 
In Batch Gradient Descent, parameters are updated using the exact gradient computed across the entire training dataset:
$$w \leftarrow w - \alpha \nabla_w J(w)$$
where $\alpha$ is the learning rate. While batch gradient descent provides smooth and deterministic convergence for convex functions, computing the full gradient over millions of examples per step is prohibitive.

Stochastic Gradient Descent (SGD) approximates the true gradient using a single randomly chosen training sample at each step:
$$w \leftarrow w - \alpha \nabla_w L_i(w)$$
SGD introduces high variance in updates, which introduces noisy oscillations but helps escape shallow local minima and saddle points. 
Mini-Batch Gradient Descent strikes the practical balance by computing gradients over small subsets (typically batches of 32 to 512 instances), leveraging vectorized GPU compute while maintaining low variance. Modern optimizers incorporate momentum (accumulating exponentially decaying past gradients), RMSProp (adaptive per-parameter learning rates based on moving average of squared gradients), and Adam (combining first and second moments).

### Overfitting, Regularization, and Generalization
Overfitting occurs when a model captures random noise and sampling variance rather than the general population distribution. To combat overfitting without reducing model capacity, regularization penalties are added to the objective function:
$$\min_w J(w) + \lambda \Omega(w)$$
- **L2 Regularization (Ridge / Weight Decay)**: $\Omega(w) = \frac{1}{2} \|w\|_2^2 = \frac{1}{2} \sum w_j^2$. L2 penalizes large weights proportionally, pulling weights smoothly toward zero and improving conditioning, but rarely setting coefficients strictly to zero.
- **L1 Regularization (Lasso)**: $\Omega(w) = \|w\|_1 = \sum |w_j|$. Because the diamond geometry of the L1 ball has sharp corners at coordinate axes, L1 induces sparsity by driving non-essential feature weights exactly to zero, performing intrinsic feature selection.
- **Elastic Net**: Combines convex combination of L1 and L2 penalties: $\lambda_1 \|w\|_1 + \lambda_2 \|w\|_2^2$, stabilizing feature selection when collinear features exist.

### Hyperparameter Tuning and Cross-Validation
Hyperparameters (such as learning rate $\alpha$, regularization strength $\lambda$, tree depth, and batch size) are parameters not learned by backpropagation or gradient descent. They must be tuned on an independent validation set. $K$-fold cross-validation partitions training data into $K$ disjoint folds, training on $K-1$ folds and evaluating on the held-out fold across $K$ rotations, generating robust, low-variance performance estimates.
