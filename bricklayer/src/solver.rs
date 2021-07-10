use std::collections::{BTreeSet, BTreeMap};

use log::{error, info};

use geo::{Point, Polygon, polygon};
use judge::format::{Position, Problem, Solution, Figure};

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

    fn collapse_from_image(image: &WaveImage) -> Result<(), String> {
        panic!("Not yet implemented.")
    }

    fn take_image(&self) -> WaveImage {
        panic!("Not yet implemented.")
    }
}

struct WaveImage {
    // TODO(akesling): Implement
}

struct VertexId(u8);

impl WaveImage {
    fn collapse(&mut self, path: &Vec<VertexId>) -> WaveImage {
        panic!("Not yet implemented.")
    }

    fn get_min_entropy_paths(&self) -> Vec<&Vec<VertexId>> {
        panic!("Not yet implemented.")
    }
}

struct PartialPose {
}

impl PartialPose {
    fn new(root: VertexId) -> PartialPose {
        PartialPose{}
    }

    fn add(edge: (VertexId, VertexId)) -> Result<(), String> {
        panic!("Not yet implemented.")
    }

    fn add_if_valid(edge: (VertexId, VertexId)) -> Result<Option<()>, String> {
        panic!("Not yet implemented.")
    }

    fn get_remainder(&self, vertex: &Vec<VertexId>) -> (VertexId, VertexId) {
        panic!("Not yet implemented.")
    }
}

pub fn solve(problem: &Problem) -> Result<Solution, String> {

    let hole_polygon = positions_to_polygon(&problem.hole);
    let valid_pose_slots = compute_bounded_integer_points(&hole_polygon);

    let mut possibilities = WaveFunction::from_figure_and_lattice(&valid_pose_slots, &problem.figure);
    let mut image_stack = vec![possibilities.take_image()];
    for pose_vertex_index in 0..problem.figure.vertices.len() {
        let root = VertexId(pose_vertex_index as u8);

        let mut solution = PartialPose::new(root);
        loop {
            let mut current_image = image_stack.pop().unwrap();
            let candidates =  current_image.get_min_entropy_paths();
            if candidates.is_empty() {
                break;
            }

            let new_edge = solution.get_remainder(candidates[0]);
            if let Err(err) = solution.add_if_valid(new_edge) {
            }
            image_stack.push(current_image);
            break;
        }
    }

    panic!("Not yet implemented")
}
