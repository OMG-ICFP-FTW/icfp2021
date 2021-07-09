/// [Competition Requirements](https://icfpcontest2021.github.io/spec-v1.1.pdf):
/// a. If line segments connect in the original figure, they must also connect in the assumed
///     pose. The list of connections is explicitly indicated in the problem.
/// b. Edges cannot be compressed or stretched arbitrarily. The amount that an edge can be
///     stretched depends on the original edge length. We define the squared distance d in between
///     two points p and q as: d(p, q) = (p_x − q_x)^2 + (p_y − q_y)^2
///
///     Let’s assume an edge between vertices v_i and v_j exists in the original figure, and v'_i
///     and v'_j are the new positions of these points in the assumed pose. We then require that
///     the ratio between the two squared lengths is at most ε/1,000,000 away from 1:
///
///         (d(v'_i, v'_j) / d(v_i v_j)) − 1 ≤ ε/1,000,000
///
///     ε is an integer specified per problem
///
/// Furthermore, if a pose is to be considered by the judges, the figure must of course fit in the
/// hole once the figure assumes the pose.
///
/// c. Every point located on any line segment of the figure in the assumed pose must either lay
///     inside the hole, or on its boundary.

use crate::format::*;

pub struct RawEdge {
    start: Position,
    end: Position,
}

impl RawEdge {
    pub fn length(&self) -> u32 {
        distance(&self.start, &self.end)
    }

    pub fn deformation(&self, other: &RawEdge) -> f32 {
        self.length() as f32 / other.length() as f32 - 1.0
    }
}

pub fn distance(p: &Position, q: &Position) -> u32 {
    (p.x - q.x).pow(2) + (p.y - q.y).pow(2)
}

pub fn edge_deformation_constraint(epsilon: u32, original: &RawEdge, moved: &RawEdge) -> bool {
    original.deformation(moved) <= epsilon as f32 / 1_000_000.0
}
