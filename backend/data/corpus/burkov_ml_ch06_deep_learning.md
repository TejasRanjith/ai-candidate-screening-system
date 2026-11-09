# The Hundred-Page Machine Learning Book (Andriy Burkov)
## Chapter 6: Neural Networks and Deep Learning

### Multilayer Perceptron and Backpropagation
A Deep Neural Network (DNN) is a composition of non-linear parameter transformations. A multilayer perceptron (MLP) with $L$ layers computes:
$$h^{(l)} = \sigma(W^{(l)} h^{(l-1)} + b^{(l)})$$
where $h^{(0)} = x$, $W^{(l)}$ is the layer weight matrix, $b^{(l)}$ is the bias vector, and $\sigma(\cdot)$ is an element-wise activation function. Without non-linear activations, composing arbitrary numbers of linear transformations collapses into a single trivial linear mapping.
Common activations include:
- **Sigmoid / Tanh**: Saturates at extreme values, causing vanishing gradients where derivatives approach zero.
- **Rectified Linear Unit (ReLU)**: $f(z) = \max(0, z)$. Resolves vanishing gradient in the positive domain and enables fast convergence, but can suffer from "dying ReLU" if activations remain negative.
- **Leaky ReLU / GELU**: Mitigates dead neurons by maintaining small non-zero gradients in negative domains.

Backpropagation applies the calculus chain rule backward from output loss to compute exact partial derivatives $\frac{\partial J}{\partial W^{(l)}}$ and $\frac{\partial J}{\partial b^{(l)}}$. 

### Convolutional and Recurrent Architectures
Convolutional Neural Networks (CNNs) replace general matrix multiplications with discrete convolution kernels, enforcing translation equivariance and local spatial weight sharing across image patches or audio spectrograms. Pooling layers (Max Pooling, Average Pooling) progressively reduce spatial dimensionality and provide translational invariance.
Recurrent Neural Networks (RNNs) and Long Short-Term Memory (LSTM) cells process sequential inputs by maintaining hidden recurrent states $h_t = f(W x_t + U h_{t-1} + b)$. LSTMs resolve exploding/vanishing gradients over long temporal dependencies through additive cell state memory controlled by input, forget, and output gates.

### Modern Deep Learning Regularization: Dropout & Normalization
- **Dropout**: Randomly drops units along with their connections during training with probability $p$. This prevents co-adaptation of hidden features and approximates an exponential ensemble of subnetworks.
- **Batch Normalization (BatchNorm)**: Normalizes layer inputs across the current mini-batch to have zero mean and unit variance, followed by learnable scale $\gamma$ and shift $\beta$ parameters. It stabilizes internal covariate shift, smooths the optimization landscape, and accelerates deep network training.
- **Layer Normalization (LayerNorm)**: Computes normalization statistics across feature channels for each independent instance rather than across batch samples, making it ideal for recurrent models and transformer architectures.
