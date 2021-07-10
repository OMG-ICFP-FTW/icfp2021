/// [Competition Requirements](https://icfpcontest2021.github.io/spec-v1.1.pdf):
/// A. If line segments connect in the original figure, they must also connect in the assumed
///     pose. The list of connections is explicitly indicated in the problem.
/// B. Edges cannot be compressed or stretched arbitrarily. The amount that an edge can be
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
/// C. Every point located on any line segment of the figure in the assumed pose must either lay
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

pub fn edge_deformation_constraint(original: &RawEdge, moved: &RawEdge, epsilon: u32) -> bool {
    original.deformation(moved) <= epsilon as f32 / 1_000_000.0
}

/// Constraint A
pub fn figures_are_consistent(original: &Figure, moved: &Figure) -> bool {
    if original.edges.len() != moved.edges.len() {
        return false;
    }

    let mut oedge_sorted = original.edges.clone();
    oedge_sorted.sort();
    let mut medge_sorted = moved.edges.clone();
    medge_sorted.sort();

    (0..original.edges.len()).all(|i| oedge_sorted[i] == medge_sorted[i])
}

/// Constraint B
pub fn figure_is_within_deformation_bounds(
    original: &Figure,
    moved: &Figure,
    epsilon: u32,
) -> bool {
    if original.vertices.len() != moved.vertices.len() {
        return false;
    }
    if original.edges.len() != moved.edges.len() {
        return false;
    }

    for edge in original.edges.iter() {
        let original_edge = RawEdge {
            start: original.vertices[edge.start].clone(),
            end: original.vertices[edge.end].clone(),
        };
        let moved_edge = RawEdge {
            start: moved.vertices[edge.start].clone(),
            end: moved.vertices[edge.end].clone(),
        };
        if !edge_deformation_constraint(&original_edge, &moved_edge, epsilon) {
            return false;
        }
    }

    return true;
}

/// Given a point cloud, return the convex hull
fn convex_hull(points: &Vec<Position>) -> Vec<Position> {
    use geo::convex_hull::ConvexHull as _;

    let coords: Vec<geo::Coordinate<f32>> = points.iter().map(|p| geo::Coordinate{x: p.x as f32, y: p.y as f32}).collect();
    let poly = geo::Polygon::new(geo::LineString::from(coords), vec![]);
    let hull = poly.convex_hull();

    let mut hull_points: Vec<Position> = hull.exterior().points_iter().map(|p| Position {
        x: p.x() as u32,
        y: p.y() as u32,
    }).collect();

    hull_points.split_last().unwrap().1.to_vec()
}

#[cfg(test)]
#[test]
fn test_convex_hull() {
    let mut diamond = vec![
        Position { x: 1, y: 2 },
        Position { x: 2, y: 1 },
        Position { x: 1, y: 0 },
        Position { x: 0, y: 1 },
    ];
    let mut diamond_hull = convex_hull(&diamond);
    diamond.sort();
    diamond_hull.sort();
    assert_eq!(diamond_hull, diamond);

    let mut square = vec![
        Position { x: 0, y: 0 },
        Position { x: 0, y: 2 },
        Position { x: 2, y: 2 },
        Position { x: 2, y: 0 },
    ];
    let mut square_hull = convex_hull(&square);
    square.sort();
    square_hull.sort();
    assert_eq!(square_hull, square);

    let mut square_with_interior_point = vec![
        Position { x: 0, y: 0 },
        Position { x: 0, y: 2 },
        Position { x: 2, y: 2 },
        Position { x: 2, y: 0 },
        Position { x: 1, y: 1 },
    ];
    let mut square_with_interior_point_hull = convex_hull(&square_with_interior_point);
    square_with_interior_point.sort();
    square_with_interior_point_hull.sort();
    assert_eq!(square_with_interior_point_hull, square);
}

/// Find the bounding polygon for this figure
fn bounding_polygon(figure: &Figure, hull: &Vec<Position>) -> Vec<Position> {
    panic!("Not yet implemented");
}

fn subtract_polygons(lead: &Vec<Position>, follow: &Vec<Position>) -> Vec<Position> {
    panic!("Not yet implemented");
}

/// Constraint C
pub fn figure_is_within_hole(figure: &Figure, hole: &Vec<Position>) -> bool {
    let hull = convex_hull(&figure.vertices);
    let bounds = bounding_polygon(figure, &hull);

    subtract_polygons(&bounds, hole).len() == 0
}

/// Apply all three constaints of A, B, and C
pub fn figure_is_valid(problem: &Problem, solution: &Solution) -> bool {
    let original_figure = &problem.figure;
    let moved_figure = Figure {
        edges: original_figure.edges.clone(),
        vertices: solution.vertices.clone(),
    };

    figures_are_consistent(original_figure, &moved_figure)
        && figure_is_within_deformation_bounds(original_figure, &moved_figure, problem.epsilon)
        && figure_is_within_hole(&moved_figure, &problem.hole)
}
