# aray
====

Gradient descent based optimization.

## Objective Components

We separately compute a bunch of objectives which are then combined.

### Stretch:

"Stretch" is the ratio of a resulting edge with its original length.

The problem specifies a maximum stretch, and there is no benefit to having a stretch which is smaller than the maximum. 

The ratio to stay within is `epsilon/1_000_000` where `epsilon` is given for the problem.

We compute this for edge `a, b` with `stretch = max(abs(d(a', b') / d(a, b) - 1) * 1e6 - epsilon), 0)`, where

- `a` and `b` are the original points
- `a'` and `b'` are the new points
- `d(a, b)` is the squared distance function `d(a, b) = (a[0] - b[0])**2 + (a[1] - b[1])**2`

### Dislikes:

This is the sum of the squared distance from every point in the hole to the closest vertex in the solution.

We smooth this with softmax to get a gradient.

Start with the vector of hole point components `Hx` and `Hy` and solution vertex components `Vx` and `Vy`.

First we compute the squared distance matrix `D = np.subtract.outer(Hx, Vx)**2 + np.subtract.outer(Hy, Vy)**2`.

Then we get the weight matrix to measure how much each distance contributes to that hole.

The weight matrix is computed as `W = softmax(-D, dim=0, beta)` where `dim` specifies the hole dimension, `beta` is the temperature.

Finally the resulting objective is the element sum of the pointwise product of the two matrices.

`dislikes = (D * W).sum()`

### Barrier:

The solution must lie entirely within our (possibly concave) hole.  We enforce this with barrier functions.

We have two sets of barrier functions: barriers from the hole to the solution and barriers from the solution to the hole.

The objective assumes every point is valid.  To enforce this, we occasionally check if there are invalid points, and then abort if found.

For each point in the body, we add barrier loss for every edge that is < 1 distance away.

Distance is calculated as normal euclidean distance `dist(a, b) = ((a[0] - b[0])**2 + (a[1] - b[1])**2)**0.5`.

This barrier loss is logarithmic: `barrier = - gamma * log(dist)`, with `gamma` controlling the sharpness.

(TODO: should try inverse barrier as well, `barrier = gamma / dist`)

## Intialization

To initialize, we shrink down the body to less than 1x1, and then add noise to all of the coordinates.

For now, rejection sample from the hole bounding box until all of our points are in the body.