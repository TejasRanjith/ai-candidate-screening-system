# The Hundred-Page Machine Learning Book (Andriy Burkov)
## Chapter 5 & 7: Model Evaluation, Metrics, and Practice

### Classification Metrics & Class Imbalance
In real-world applications with skewed class distributions (e.g., fraud detection or rare medical diagnosis), raw accuracy $\frac{TP + TN}{TP + TN + FP + FN}$ is deceptively misleading.
Standard evaluation metrics derived from the Confusion Matrix include:
- **Precision**: $\frac{TP}{TP + FP}$ — Fraction of positive predictions that are truly positive. Critical when false alarms carry severe cost.
- **Recall (Sensitivity / True Positive Rate)**: $\frac{TP}{TP + FN}$ — Fraction of true positives captured by the classifier. Critical when missing a positive case carries catastrophic consequences.
- **F1 Score**: Harmonic mean of Precision and Recall: $F_1 = 2 \cdot \frac{\text{Precision} \cdot \text{Recall}}{\text{Precision} + \text{Recall}}$.
- **ROC and PR Curves**: Receiver Operating Characteristic (ROC) plots TPR against False Positive Rate (FPR) across discrimination thresholds. The Area Under the Curve (ROC-AUC) measures ranking ability invariant to class proportions. When positive class is extremely sparse, Precision-Recall AUC (PR-AUC) provides a more rigorous indicator of model quality.

To handle severe class imbalance:
1. Resampling techniques: Synthetic Minority Over-sampling Technique (SMOTE) interpolates synthetic instances between minority neighbors, while Random Under-Sampling drops majority samples.
2. Cost-sensitive learning: Weighting the loss function inversely proportional to class frequencies, forcing higher gradient penalties on minority misclassifications.
3. Focal Loss: Dynamically scales cross-entropy loss by $(1 - p_t)^\gamma$ to down-weight easy examples and focus training on difficult edge cases.

### Bias-Variance Tradeoff and Model Diagnostic
Total generalization error decomposes into three components:
$$\text{Expected Error} = \text{Bias}^2 + \text{Variance} + \text{Irreducible Error} (\sigma^2)$$
- **High Bias (Underfitting)**: Model fails to capture underlying patterns. Both training error and validation error are high and close together. Remedy: Increase model capacity, add engineered features, reduce regularization.
- **High Variance (Overfitting)**: Model memorizes training noise. Training error is very low, but validation error is significantly higher (large generalization gap). Remedy: Collect more training data, add L1/L2 regularization, apply dropout, prune decision trees, or employ ensemble methods.
