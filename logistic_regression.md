# Weighted Aggregate Logistic Regression

## Background
One approach to calibrating predictions from differentially private aggregate data is to utilize a large number of breakdown buckets. This approach has been explored in the context of charting out the future of advertising in a post-cookie world: [Criteo Competition](https://competitions.codalab.org/competitions/31485).

The benefit of utilizing noisy breakdowns is that a private measurement standard designed to support ad measurement use-cases will already be capable of producing such noisy breakdown buckets. The main disadvantages of bucketization are:

- High cardinality, large amount of LR training features and large number of model parameters.
- Bucketization coarsens the original granular features.

We propose a new LR training algorithm (WALR) that exhibits the following properties:

- **Weighted aggregation**: the WALR model assumes a private measurement system can achieve global weighted aggregation over all attribution outcomes (conversion or no conversion). The weights are to be supplied by the API consumer. 
- **Global DP**: Gaussian noise will be injected to weighted aggregates before the private measurement system releases the outputs to the API consumer. 
- **One time aggregation**: Per training cadence, the aforementioned computation and addition of gaussian noise only needs to be performed one time.
- **Consume granular features**: Granular features can be perfectly utilized without any kind of discretization.

## Design Principle

The design and key privacy-related properties of the WALR model are based on the derivation for non-private, gradient-based LR model training. We re-derive these details and introduce notation before discussing privacy aspects and implementation details of the model.

### LR Model Gradient-Based Training Overview

The following gives an overview of the standard (non-private) gradient derivation for logistic regression models, which is the foundation of WALR:

- Our training dataset is comprised of N,  k-dimensional (normalized) feature vectors \
$X^{(1)}, X^{(2)}, ... , X^{(N)}$, \
and N binary labels \
$y^{(1)}, y^{(2)}, ... , y^{(N)} \in \\{0, 1\\}$.
- We want to train a logistic regression model $\theta \in R^k$.
- We consider the loss function \
 $L(\theta, \\{ X^{(i)} \\}, \\{ y^{(i)} \\} )=\frac{1}{N} \cdot \sigma ( \sum\limits_{i=1}^{n}l_{i}(\theta,X^{(i)},y^{(i)})$ \
where each $l_i$ is the cross entropy loss \
$l_i(\theta, X^{(i)}, y^{(i)}) = -[y^{(i)} \log(p_i) + (1-y^{(i)})\log(1-p_i)]$. \
Here, we let $p_i = \sigma(\theta^TX^{(i)})$, where $\sigma(\cdot)$ denotes the sigmoid function. 
- The gradient of $L$ with regard to $\theta$ is then given by \
	$\nabla L(\theta)=(\frac{1}{N} \cdot \sum\limits_{i=1}^{N} \sigma(\theta^TX^{(i)}) X^{(i)}) - (\frac{1}{N} \cdot \sum\limits_{i=1}^{N} y^{(i)} X^{(i)} )$.
- In the absence of any computational or privacy constraints, the model  can be trained via full-batch gradient descent of the form, where here $\text{lr}$ is the learning rate.:
  1. initialize model vector $\theta$
  2. while not converged: \
  $\text{set } \theta = \theta - \text{lr} \cdot ((\frac{1}{N} \cdot \sum\limits_{i=1}^{N} \sigma(\theta^T X^{(i)}) X^{(i)} ) - \frac{1}{N} \cdot \sum\limits_{i=1}^{N} y^{(i)} X^{(i)} ))$
 
  4. output $\theta$

### Privacy Properties of WALR: Label "Blindness"

The WALR model assumes the presence of a *private measurement system*. This private measurement system has access to conversion labels (to perform aggregation and add DP noise), but the API consumer does not.

To this end, the key observation in the calculation of $\nabla L(\theta)$ above is that this vector can be expressed as the difference of two sums, where only the right-hand term (which we refer to as **dot-product**) involves the set of labels $\\{ y^{(i)} \\}$. Additionally, with respect to changes in $\theta$, the **dot-product** vector is fixed. 

This means that iterative optimization algorithms like gradient descent only require computing **dot-product** once. 

In the context of model training and label privacy, this motivates viewing $\nabla L$ in the form \
$\nabla L(\theta, \text{dot-product}) = (\frac{1}{N} \sum\limits_{i=1}^{N} \sigma(\theta^{T}X^{(i)}) X^{(i)}) - \text{dot-product} $,\
where $\text{dot-product} = \frac{1}{N} \sum\limits_{i=1}^{N} y^{(i)} X^{(i)}$.\
In this perspective, gradient descent-based training algorithms that (re)-compute $\nabla L$ at every iteration requires no direct access to labels if we assume that a private measurement system can provide the pre-computed **dot-product** vector at training time.

- **Question:** why is this quantity referred to as "dot-product"?\
**Answer:** Note that the expression\
$\frac{1}{N} \sum\limits_{i=1}^{N} y^{(i)} X^{(i)}$ \
is a linear combination of k-dimensional vectors, where k is the number of features. If we let\
$X = (X^{(1)}, ..., X^{(N)}) \in [0, 1]^{N*k}$ and $y = (y^{(1)}, ..., y^{(N)})^T \in \\{0, 1\\}^N$ \
denote the *(N \* k)*-dimensional feature *matrix* and *N*-dimensional label vector respectively,  then we have 

$\text{dot-product} = \frac{1}{N} \sum\limits_{i=1}^{N} y^{(i)} X^{(i)} = \frac{1}{N} \cdot Xy$ ,\
which is a matrix-vector multiply. Thus every i'th coordinate of this sum is the dot product between the i'th row vector of $X^T$ and the label vector $y$. Here, every row vector of $X^T$ can be interpreted as the set of weights for the i'th feature across all *N* samples in the dataset. 

Thus the **dot-product** vector can be interpreted as $k$ independent dot products between each row vector of $X^T$ and the label vector $y$ (hence its name), or equivalently as a matrix-vector multiply, respectively producing $k$ weighted sums.

**Note:** the exact naming convention may be subject to change.

## Privacy Properties of WALR: Label Differential Privacy

We can also ensure that the final model vector $\theta$ is *label-differentially private* by using a label-differentially-private approximation of **dot-product** in the $\nabla L$ computation. 

Our privacy model assumes the private measurement system has access to training labels. Our definition of $(\epsilon, \delta)$-label differential privacy is the standard:

> A randomized training algorithm $A$ taking as input a dataset is said to be $(\epsilon, \delta)$*-label differentially private* ($(\epsilon, \delta)\text{-LabelDP}$) if for any two training datasets $D$ and $D^{\prime}$ that differ in the label of a single example, and for any subset $S$ of outputs of $A$, it is the case that $Pr[A(D) \in S] \leq e^{\epsilon} \cdot Pr[A(D^{\prime}) \in S] + \delta$. If $\delta=0$, then $A$ is said to be $\epsilon$ -label differentially private ($\epsilon\text{-LabelDP}$).

In the presence of a private measurement system that computes the (non-private) **dot-product** vector, label-DP can be achieved via a single-occurrence output perturbation of the form:

$\text{noisy-dot-product} = \text{dot-product} + \text{gaussian-noise}$,

where $\text{gaussian-noise}$ is a vector of iid normal random variables with variance calibrated to the l2 label-sensitivity of **dot-product** (more details below).

In total, the WALR model will consider the following *noisy* gradient approximation\
$\text{noisy-}\nabla L(\theta) = (\frac{1}{N} \cdot \sum\limits_{i=1}^{N} \sigma(\theta^{T}X^{(i)}) X^{(i)} ) - \text{noisy-dot-product}$,\
which is both label-blind (i.e., no direct label access required) and label-DP.

We emphasize that the **noisy-dot-product only needs to be computed once**. When training the WALR model, we will assume that this vector is computed by the private measurement system and supplied as a parameter to the training algorithm.

- **Question:** *what is the variance of each normal RV in the* $\text{gaussian-noise}$ *vector?*\
**Answer:** Using the classic Gaussian Mechanism for differential privacy (see Dwork+11 textbook), we can ensure $\text{noisy-dot-product}$ is a label-DP approximation of $\text{dot-product}$ by setting each coordinate of $\text{gaussian-noise}$ to have variance calibrated to the l2-sensitivity $s$ of $\text{dot-product}$.\
  \
To this end, under the assumption that all feature vectors $X^{(i)}$ have coordinates in the range $[0, 1]$, we have the following upper bound on $s^2$:\
$s^2 = \frac{1}{N^2}\max\limits_{i \in [N]} \lVert X^{(i)} \rVert^2 \leq \frac{k}{N^2}$.\
\
This comes from the fact that when a single binary label vector $y^{(i)}$ flips its value, then the difference in the dot-product sum is simply the feature vector $X^{(i)}$ corresponding to that sample. After factoring out the $\frac{1}{N}$ multiplicative term, we have that the L2 (squared) sensitivity is equal to the maximum (over all samples) squared 2-norm of any feature vector. Because all features are normalized in the [0,1] range, the upper bound follows.\
\
Then each coordinate of the vector gaussian-noise can be set as an iid, zero-mean normal random variable with variance\
$\sigma^2 = s^2 \cdot \frac{2\log(1.25/\delta)}{\epsilon^2}$\
where $(\epsilon, \delta)$ are the privacy parameters.\
\
It follows by the privacy guarantee of the Gaussian Mechanism that $\text{noisy-dot-product}$ is $(\epsilon, \delta)\text{-label-DP}$.

- **Question:** if $\text{noisy-} \nabla L(\theta)$ is used in place of $\nabla L(\theta)$ within a gradient descent update rule, how many times do we need to add noise? Is the final output model vector $\theta$ private?\
**Answer:** The $\text{gaussian-noise}$ vector need only be generated and computed **once** in order to produce the label-DP $\text{noisy-dot-product}$ vector.\
\
Any additional computations used to update $\text{noisy-} \nabla L(\theta)$  (as in a gradient descent procedure) will still be label-DP (with the same privacy parameters) due to the Post Processing Theorem of DP (see Dwork+11 text).

- **Question:** is $\text{noisy-dot-product}$ efficiently computable?\
**Answer:** Yes, computing this vector requires just one pass through the set of feature vectors, and $k$ random draws from a Gaussian distribution. 

## WALR Trainer Implementation: "Hybrid" Minibatch GD

To train the WALR model, our implementation will apply a gradient descent procedure that uses the vector $\text{noisy-} \nabla L(\theta)$ as a label-DP approximation of $\nabla L(\theta)$.

Recall that in the absence of practical computational constraints, this label-DP training algorithm could proceed using the following "full-batch" gradient descent approach:

1. initialize model vector $\theta$
2. while not converged:\
$\text{set } \theta = \theta - lr \cdot ((\frac{1}{N} \cdot \sum\limits_{i=1}^{N} p_i X^{(i)} ) - \text{noisy-dot-product})$
3. output $\theta$

As mentioned, we assume the vector $\text{noisy-dot-product}$ is computed once and supplied by the *private measurent system* at training time. However, in the pseudocode above, every iteration of the `while` loop requires computing the term $(\frac{1}{N} \cdot \sum\limits_{i=1}^{N} p_i X^{(i)} )$. 
Here, $N$ is the total number of samples in the training dataset, which could be quite large. Thus computing this term exactly at every optimization step is likely too computationally expensive.

To circumvent this computational issue, we use a simple **"hybrid"-minibatch gradient** computation that we describe here. 

First, we define the terms $\text{LHS}$ and $\text{RHS}$ as\
$\sum\text{LHS} = \sum\limits_{i=1}^{N} p_i X^{(i)}$\
$\sum\text{RHS} = \sum\limits_{i=1}^{N} y^{(i)} X^{(i)}$

which means that we can express $\nabla L(\theta)$ and $\text{noisy-} \nabla L(\theta)$ in the form\
$\nabla L(\theta) = (\frac{1}{N}) \cdot (\sum LHS) – (\frac{1}{N}) \cdot (\sum RHS)$\
$\text{noisy-} \nabla L(\theta) = (\frac{1}{N}) \cdot (\sum LHS) – (\frac{1}{N}) \cdot (\sum RHS) - \text{gaussian-noise}$. 

To avoid computing $\text{LHS}$ at every optimization step, we approximate this term using a minibatch of size $m$.  Specifically, at every gradient descent step, we sample a minibatch $M$ of size $m$, and we compute\
$\text{mini-}\sum\text{LHS} = \sum\limits_{j=1}^{m} p_j X^{(j)}$,\
where the sum is over every index $j$ in the current step's minibatch.

Then the corresponding "hybrid" and "noisy-hybrid"-minibatch gradient steps become:

$\text{hybrid-} \nabla L(\theta) = (\frac{1}{m}) \cdot (\text{mini-} \sum\text{LHS}) – (\frac{1}{N}) \cdot \text{RHS}$\
$\text{noisy-hybrid-} \nabla L(\theta) = (\frac{1}{m}) \cdot (\text{mini-} \sum\text{LHS}) - (\frac{1}{N}) \cdot \text{RHS} – \text{gaussian-noise}$. 

- **Question:** *why is this referred to as a "hybrid" minibatch?*\
**Answer:** The term "hybrid" is used to emphasize the fact that the left-hand term is an average over a minibatch of size $m \leq N$, while the right-hand term is an average over the entire set of $N$ samples.\
\
This is in contrast to a full-batch gradient (where both terms would average over all $N$ samples) and a traditional minibatch gradient (where both terms would average over the same minibatch of size $m$). 

Intuitively, the full-batch, private, one-time computation of the right hand term (i.e., the **dot-product** or **noisy-dot-product**) should lead to better approximations of the true gradients at each optimization step, and the minibatch computation of the left hand term should lead to computational gains. 

The final noisy-hybrid-minibatch gradient descent procedure for WALR model training will then proceed by:

1. initialize model vector $\theta$
2. while not converged:\
sample minibatch of size $m$, and\
$\text{set } \theta = \theta - lr \cdot ( \text{noisy-hybrid-} \nabla L(\theta))\$
3. output $\theta$

## Acknowledgements
Many thanks to original authors Sen Yuan & John Lazarsfeld, who developed the WALR algorithm.

Thanks also to reviewers Prasad Buddhavarapu and Huanyu Zhang who helped review this algorithm and writeup.

We would also like to recognize Kamalika Chaudhuri, Claire Monteleoni and Anand D. Sarwate, the authors of [“Differentially Private Empirical Risk Minimization”](https://jmlr.org/papers/volume12/chaudhuri11a/chaudhuri11a.pdf). The WALR algorithm can be viewed as a label DP version of the objective perturbation in DP machine learning, as described in this paper and the follow-up works on this topic.

Finally, we would like to thank Criteo for hosting the “Criteo Privacy Preserving ML Competition @ AdKDD”, and for their continued publications on their research into privacy-preserving machine learning. These contributions have continued to help move the industry forward in this emerging space.
