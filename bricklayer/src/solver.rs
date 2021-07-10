use std::collections::{BTreeMap, BTreeSet};

use log::{error, info};

use geo::{polygon, Point, Polygon};
use judge::format::{Figure, Position, Problem, Solution};

pub fn compute_bounded_integer_points(boundary: &Polygon<u32>) -> Vec<Point<u32>> {
    panic!("Not yet implemented")
}

#[cfg(test)]
#[test]
fn test_compute_bounded_integer_points() {
    let unit_square: Polygon<u32> = polygon![
        (x: 0, y: 0),
        (x: 0, y: 1),
        (x: 1, y: 1),
    ];

    let expected: Vec<Point<u32>> = unit_square.exterior().points_iter().collect();
    assert_eq!(compute_bounded_integer_points(&unit_square), expected);
}

fn positions_to_polygon(positions: &Vec<Position>) -> Polygon<u32> {
    let coords: Vec<geo::Coordinate<u32>> = positions
        .iter()
        .map(|p| geo::Coordinate {
            x: p.x as u32,
            y: p.y as u32,
        })
        .collect();

    geo::Polygon::new(geo::LineString::from(coords), vec![])
}

struct WaveFunction {
    // TODO(akesling): Implement
}

impl WaveFunction {
    fn from_figure_and_lattice(lattice: &Vec<Point<u32>>, figure: &Figure) -> WaveFunction {
        panic!("Not yet implemented.")
    }

    fn remove_derivative_images(&mut self, image: &WaveImage) -> Result<(), String> {
        panic!("Not yet implemented.")
    }

    fn take_image(&self) -> WaveImage {
        panic!("Not yet implemented.")
    }
}

struct WaveImage {
    // TODO(akesling): Implement
}

#[derive(PartialOrd, Ord, PartialEq, Eq, Copy, Clone)]
struct VertexId(u8);

impl WaveImage {
    fn collapse(&mut self, path: &Vec<VertexId>) -> WaveImage {
        panic!("Not yet implemented.")
    }

    fn get_min_entropy_extensions(&self, query: &PartialPose) -> Vec<Vec<VertexId>> {
        panic!("Not yet implemented.")
    }

    fn remove_derivative_images(&self, context: &PartialPose, extension: (VertexId, VertexId)) {
        panic!("Not yet implemented.")
    }
}

struct PartialPose {
    pub vertices: BTreeSet<VertexId>,
}

impl PartialPose {
    fn new(root: VertexId) -> PartialPose {
        let mut vertices = BTreeSet::new();
        vertices.insert(root);

        PartialPose { vertices }
    }

    fn add(&mut self, edge: (VertexId, VertexId)) -> Result<(), String> {
        panic!("Not yet implemented.")
    }

    fn add_if_valid(&mut self, edge: (VertexId, VertexId)) -> Result<Option<()>, String> {
        panic!("Not yet implemented.")
    }

    fn get_remainder(&self, vertex: &Vec<VertexId>) -> (VertexId, VertexId) {
        panic!("Not yet implemented.")
    }
}

pub fn solve(problem: &Problem) -> Result<Option<Solution>, String> {
    let hole_polygon = positions_to_polygon(&problem.hole);
    let valid_pose_slots = compute_bounded_integer_points(&hole_polygon);

    let mut possibilities =
        WaveFunction::from_figure_and_lattice(&valid_pose_slots, &problem.figure);
    for pose_vertex_index in 0..problem.figure.vertices.len() {
        let root = VertexId(pose_vertex_index as u8);
        let mut image_stack = vec![possibilities.take_image()];

        let mut solution = PartialPose::new(root);
        loop {
            let mut current_image = image_stack.pop().unwrap();
            let candidates = current_image.get_min_entropy_extensions(&solution);
            if candidates.is_empty() {
                // We've exhausted this search avenue and so...
                if solution.vertices.len() == problem.figure.vertices.len() {
                    //  1) We've succeeded
                    // TODO(akesling): Continue finding other solutions instead of bailing early.
                    return Ok(Some(Solution {
                        vertices: solution
                            .vertices
                            .iter()
                            .map(|vert_index| -> Position {
                                problem.figure.vertices[vert_index.0 as usize].clone()
                            })
                            .collect(),
                    }));
                } else if solution.vertices.len() == 1 {
                    //  2) We've exhausted this root
                    possibilities.remove_derivative_images(&current_image);
                    while !image_stack.is_empty() {
                        possibilities.remove_derivative_images(&image_stack.pop().unwrap());
                    }
                    break;
                } else {
                    //  3) Back track
                    possibilities.remove_derivative_images(&current_image);
                    continue;
                }
            }

            let new_path = &candidates[0];
            let new_edge = solution.get_remainder(new_path);
            match solution.add_if_valid(new_edge.clone()) {
                Ok(Some(())) => {
                    // Success!! We must go deeper....
                    let next_image = current_image.collapse(new_path);
                    image_stack.push(current_image);
                    image_stack.push(next_image);
                    continue;
                }
                Ok(None) => {
                    // Whoops, let's try this again.
                    current_image.remove_derivative_images(&solution, new_edge);
                    image_stack.push(current_image);
                    continue;
                }
                Err(err) => {
                    error!(
                        "An error occurred {:?} adding edge to candidate solution.",
                        err
                    );
                    break;
                }
            }
        }
    }

    Ok(None)
}
