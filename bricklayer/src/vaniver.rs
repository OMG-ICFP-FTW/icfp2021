use crate::util::{points_inside_hole, Point};
use judge::format::Position;
use std::{
    collections::{BTreeSet, HashSet},
    ops::Range,
};

fn dist(p: Point, q: Point) -> u32 {
    let dx = (p.x - q.x) as i32;
    let dy = (p.y - q.y) as i32;
    (dx * dx + dy * dy) as u32
}

fn dist_range(dist: u32, epsilon: u32) -> Range<f32> {
    (dist as f32 * (1.0 - (epsilon as f32) / 1000000.0))
        ..(dist as f32 * (1.0 + (epsilon as f32) / 1000000.0))
}

fn ring_quad_options(r1: f32, r2: f32) -> Vec<Point> {
    let mut res = Vec::new();

    for x in 0..=(r2.sqrt().floor() as u32) {
        let x2f = (x * x) as f32;
        let min_y = if x2f > r1 {
            0
        } else {
            (r1 - x2f).sqrt().ceil() as i16
        };
        let max_y = (r2 - x2f).sqrt().floor() as i16;
        for y in min_y..=max_y {
            res.push(Point { x: x as i16, y });
        }
    }
    res.sort();
    res
}

#[derive(Debug)]
struct Hole {
    vertices: Vec<Point>,
    inside: BTreeSet<Point>,
}

impl Hole {
    fn new(hole: &[Position]) -> Self {
        Hole {
            vertices: hole.iter().map(|p| Point::from_pos(*p)).collect(),
            inside: points_inside_hole(hole),
        }
    }
}

type VertIndex = usize;

#[derive(Debug)]
struct Edge {
    from: VertIndex,
    to: VertIndex,
    dist_range: Range<f32>,
    adj_vecs: Vec<Point>,
}

#[derive(Debug)]
struct Figure {
    edges: Vec<Edge>,
    /// adg_edges[from] = list of to edge indexes
    adj_edges: Vec<Vec<usize>>,
}

impl Figure {
    fn new(fig: &judge::format::Figure, epsilon: u32) -> Self {
        let edges: Vec<Edge> = fig
            .edges
            .iter()
            .map(|e| {
                let from_v = Point::from_pos(fig.vertices[e.start]);
                let to_v = Point::from_pos(fig.vertices[e.end]);
                let dist = dist(from_v, to_v);
                let dist_range = dist_range(dist, epsilon);
                Edge {
                    from: e.start,
                    to: e.end,
                    adj_vecs: ring_quad_options(dist_range.start, dist_range.end),
                    dist_range,
                }
            })
            .collect();
        let mut adj_edges: Vec<Vec<usize>> = (0..fig.vertices.len()).map(|_i| Vec::new()).collect();
        for (edge_i, e) in edges.iter().enumerate() {
            adj_edges[e.from].push(edge_i);
            adj_edges[e.to].push(edge_i);
        }

        Self { edges, adj_edges }
    }
}

#[derive(PartialEq, Eq, Hash, Clone)]
struct PartialFigure {
    locs: Vec<Option<Point>>,
    num_unfilled: usize,
}

impl PartialFigure {
    fn new(n_verts: usize) -> Self {
        Self {
            locs: vec![None; n_verts],
            num_unfilled: n_verts,
        }
    }

    // fn vertex_at_point(n_verts: usize, vert: usize, point: Point) -> Self {
    //     let mut res = Self::new(n_verts);
    //     res.locs[vert] = Some(point);
    //     res
    // }

    fn solution(&self) -> judge::format::Solution {
        judge::format::Solution {
            vertices: self.locs.iter().map(|p| p.unwrap().to_pos()).collect(),
        }
    }

    fn with_filled(&self, i: usize, p: Point) -> Self {
        let mut locs = self.locs.clone();
        locs[i] = Some(p);
        Self {
            locs,
            num_unfilled: self.num_unfilled - 1,
        }
    }

    /// Returns whether the expansions are complete
    fn for_each_expansion(
        &self,
        fig: &Figure,
        hole: &Hole,
        poss: &mut Vec<Point>,
        mut f: impl FnMut(PartialFigure),
    ) {
        for (i, _) in self
            .locs
            .iter()
            .cloned()
            .enumerate()
            .filter(|(_i, p)| p.is_none())
        {
            // poss.clear();
            let mut poss_started = false;
            // println!("filling {}", i);
            for edge_i in fig.adj_edges[i].iter().cloned() {
                let e = &fig.edges[edge_i];
                let other_v = if e.from == i { e.to } else { e.from };
                let base = match self.locs[other_v] {
                    None => continue,
                    Some(p) => p,
                };

                // println!("{} base: {:?} vecs: {:?}", edge_i, base, e.adj_vecs);
                if poss_started {
                    poss.retain(|p| {
                        let vec_to_p = base.sub(*p).abs();
                        e.adj_vecs.binary_search(&vec_to_p).is_ok()
                    });
                } else {
                    for vec in &e.adj_vecs {
                        for dx in [-1, 1] {
                            for dy in [-1, 1] {
                                let p = Point {
                                    x: base.x + vec.x * dx,
                                    y: base.y + vec.y * dy,
                                };
                                if hole.inside.contains(&p) {
                                    poss.push(p);
                                }
                                if vec.y == 0 {
                                    break;
                                }
                            }
                            if vec.x == 0 {
                                break;
                            }
                        }
                    }
                    // println!("possi: {:?}", poss);
                    poss_started = true;
                }
                // println!("poss {}: {:?}", edge_i, poss);
            }

            for p in poss.drain(..) {
                f(self.with_filled(i, p));
            }
        }
    }
}

pub struct Problem {
    problem: judge::format::Problem,
    hole: Hole,
    figure: Figure,
}

impl Problem {
    pub fn new(problem: judge::format::Problem) -> Self {
        Self {
            hole: Hole::new(&problem.hole),
            figure: Figure::new(&problem.figure, problem.epsilon),
            problem,
        }
    }

    pub fn search(&self) -> Option<(u32,judge::format::Solution)> {
        // println!("{:?}", self.figure);
        // println!("{:?}", self.hole);
        let mut candidates = Vec::new();
        let mut visited = HashSet::new();
        let n_verts = self.figure.adj_edges.len();
        for hole_pt in &self.hole.vertices {
            for vert in 0..n_verts {
                candidates.push(PartialFigure::new(n_verts).with_filled(vert, *hole_pt));
            }
        }

        let mut num_searched = 0;
        // TODO change from DFS
        let mut poss = Vec::new();
        let mut best_solution: Option<(u32, judge::format::Solution)> = None;
        while let Some(next_expansion) = candidates.pop() {
            // println!("{:?}", next_expansion.locs);
            // if next_expansion.locs[0] == Some(Point { x: 10, y: 0 })
            //     && next_expansion.locs[1] == Some(Point { x: 10, y: 10 })
            // {
            //     println!("WOW HI ==========================================");
            // }
            if num_searched % 1000 == 0 {
                println!("{}: {} candidates, best = {:?}", num_searched, candidates.len(), best_solution.as_ref().map(|(x,_)| x));
            }

            next_expansion.for_each_expansion(&self.figure, &self.hole, &mut poss, |pf| {
                if pf.num_unfilled == 0 {
                    // TODO check validity for concave holes
                    let solution = pf.solution();
                    let dislikes = judge::dislikes::compute_dislikes(&self.problem, &solution);
                    let valid = judge::dislikes::figure_is_valid(&self.problem, &solution);

                    // println!("FOUND {:?} ({:?}) {:?}", valid, dislikes, pf.locs);
                    match (dislikes, valid, &best_solution) {
                        (Ok(dislikes), Ok(()), Some((best_dislikes, _))) => {
                            if dislikes < *best_dislikes {
                                best_solution = Some((dislikes, solution));
                            }
                        }
                        (Ok(dislikes), Ok(()), None) => {
                            best_solution = Some((dislikes, solution));
                        }
                        _ => ()
                    };
                } else if !visited.contains(&pf) {
                    // TODO deduplicate with visited set of some kind?
                    visited.insert(pf.clone());
                    candidates.push(pf);
                }
            });
            num_searched += 1;
        }

        best_solution
    }
}
