use crate::util::{points_inside_hole, Point};
use judge::format::Position;
use std::{collections::BTreeSet, ops::Range};

fn dist(p: Point, q: Point) -> u32 {
    let dx = (p.x - q.x) as i32;
    let dy = (p.y - q.y) as i32;
    (dx * dx + dy * dy) as u32
}

fn dist_range(dist: u32, epsilon: u32) -> Range<f32> {
    (dist as f32 * (1.0 - (epsilon as f32) / 1000000.0))
        ..(dist as f32 * (1.0 + (epsilon as f32) / 1000000.0))
}

// def ring_quad_options(r1, r2):
//     """Given two squared radii, yield all integer lattice points in the first quadrant of that ring."""
//     for x in range(math.floor(math.sqrt(r2))):
//         if x ** 2 > r1:
//             min_y1 = 0
//         else:
//             min_y1 = math.ceil(math.sqrt(r1 - x**2))
//         max_y2 = math.floor(math.sqrt(r2 - x**2))
//         for y in range(min_y1, max_y2+1):
//             yield (x, y)
fn ring_quad_options(r1: f32, r2: f32) -> BTreeSet<Point> {
    let mut res = BTreeSet::new();
    
    res
}

struct Hole {
    vertices: Vec<Point>,
    inside: BTreeSet<Point>,
}

impl Hole {
    fn new(hole: Vec<Position>) -> Self {
        Hole {
            vertices: hole.iter().map(|p| Point::from_pos(p)).collect(),
            inside: points_inside_hole(hole),
        }
    }
}

type VertIndex = usize;

struct Edge {
    from: VertIndex,
    to: VertIndex,
    dist_range: Range<f32>,
    adj_vecs: Vec<Point>,
}

struct Figure {
    edges: Vec<Edge>,
    /// adg_edges[from] = list of to edge indexes
    adj_edges: Vec<Vec<usize>>,
}

impl Figure {
    fn new(fig: judge::format::Figure, epsilon: u32) -> Self {
        let edges = fig
            .edges
            .iter()
            .map(|e| {
                let from_v = Point::from_pos(fig.vertices[e.start]);
                let to_v = Point::from_pos(fig.vertices[e.end]);
                let dist = dist(from_v, to_v);
                Edge {
                    from: e.start,
                    to: e.end,
                    dist_range: dist_range(dist, epsilon),
                    adj_vecs: (),
                }
            })
            .collect();
        let mut adj_edges = (0..fig.vertices.len()).map(|i| Vec::new()).collect();
        for e in &edges {
            adj_edges[e.from].push(e.to);
        }

        Self { edges, adj_edges }
    }
}

struct PartialFigure {
    locs: Vec<Option<Point>>,
}

struct Problem {
    hole: Hole,
    figure: Figure,
}

impl Problem {
    fn new(problem: judge::format::Problem) -> Self {
        Self {
            hole: Hole::new(problem.hole),
            figure: Figure::new(problem.figure, problem.epsilon),
        }
    }
}
