use std::collections::{BTreeMap, BTreeSet};

use log::error;

use geo::{polygon, Point, Polygon, Coordinate};
use judge::format::{Figure, Position, Problem, Solution};

pub fn compute_bounded_integer_points(boundary: &Polygon<f32>) -> Vec<Point<f32>> {
    use geo::algorithm::euclidean_distance::EuclideanDistance;
    use geo::extremes::Extremes as _;

    let mut bounded_integer_points = vec![];
    let extremes = boundary.extremes().unwrap();
    for x in (extremes.x_min.coord.x as usize)..((extremes.x_max.coord.x + 1.0) as usize) {
        for y in (extremes.y_min.coord.y as usize)..((extremes.y_max.coord.y + 1.0)  as usize) {
            let point = Point(Coordinate {x: x as f32, y: y as f32});
            if point.euclidean_distance(boundary) < 0.00001 {
                bounded_integer_points.push(point)
            } else {
            }
        }
    }

    bounded_integer_points
}

// #[cfg(test)]
// #[test]
// fn test_problem_integer_points() {
//     use std::io::prelude::*;

//     let largest_problem_index = 106;
//     for i in 1..largest_problem_index {
//         let current_dir = std::env::current_dir().unwrap();
//         let mut problem_file_path = current_dir.clone();
//         problem_file_path.push(std::path::PathBuf::from(format!("../problems/{}.json", i)));
//         let problem_file_path = std::fs::canonicalize(problem_file_path).unwrap();

//         let problem_file = match std::fs::File::open(&problem_file_path) {
//             Ok(file) => file,
//             Err(err) => {
//                 panic!("\nFailed to open problem file ({:?}) with error: {}\n", problem_file_path, err);
//             }
//         };

//         let mut buf_reader = std::io::BufReader::new(problem_file);
//         let mut contents = String::new();
//         buf_reader.read_to_string(&mut contents).expect(&format!("Failed to read JSON file to string: {:?}", problem_file_path));

//         let problem: judge::format::Problem =
//             serde_json::from_str(&contents).expect("JSON was not well-formatted");

//         let hole_polygon = positions_to_polygon(&problem.hole);
//         let valid_pose_slots: Vec<Position> = compute_bounded_integer_points(&hole_polygon).iter()
//             .map(|p| Position {
//                 x: p.x() as u32,
//                 y: p.y() as u32,
//             }).collect();

//         let current_dir = std::env::current_dir().unwrap();
//         let mut pose_slot_file_path = current_dir.clone();
//         pose_slot_file_path.push(std::path::PathBuf::from("../valid_hole_slots/"));
//         let mut pose_slot_file_path = std::fs::canonicalize(pose_slot_file_path).unwrap();
//         pose_slot_file_path.push(std::path::PathBuf::from(format!("{}.json", i)));
//         let mut pose_slot_file = match std::fs::File::create(&pose_slot_file_path) {
//             Ok(file) => file,
//             Err(err) => {
//                 panic!("\nFailed to open problem file: {}\n", err);
//             }
//         };

//         let json = serde_json::to_string(&valid_pose_slots).expect("Failed to serialize valid points");
//         pose_slot_file.write_all(&json.as_bytes()).expect("Failed to write valid points to file");
//     }
// }

#[cfg(test)]
#[test]
fn test_compute_bounded_integer_points() {
    let unit_square: Polygon<f32> = polygon![
        (x: 0.0, y: 0.0),
        (x: 0.0, y: 2.0),
        (x: 2.0, y: 2.0),
        (x: 2.0, y: 0.0),
        (x: 0.0, y: 0.0),
    ];

    let mut expected: Vec<Position> = unit_square.exterior().points_iter()
        .map(|p| Position {
            x: p.x() as u32,
            y: p.y() as u32,
        }).collect();
    expected.append(&mut vec![
        Position {x: 0, y: 1},
        Position {x: 1, y: 0},
        Position {x: 1, y: 1},
        Position {x: 1, y: 2},
        Position {x: 2, y: 1},
    ]);
    expected.sort();
    expected.dedup();
    let expected: Vec<Point<f32>> = expected.iter()
        .map(|p| Point(geo::Coordinate {
            x: p.x as f32,
            y: p.y as f32,
        }))
        .collect();
    assert_eq!(compute_bounded_integer_points(&unit_square), expected);
}

fn positions_to_polygon(positions: &Vec<Position>) -> Polygon<f32> {
    let coords: Vec<geo::Coordinate<f32>> = positions
        .iter()
        .map(|p| geo::Coordinate {
            x: p.x as f32,
            y: p.y as f32,
        })
        .collect();

    geo::Polygon::new(geo::LineString::from(coords), vec![])
}

#[allow(unused)]
struct WaveFunction {
    // TODO(akesling): Implement
    // For all figure points:
    //   For all hole slots:
    //     For all figure points - {"root"}
    //       All paths to a given point
    states: BTreeMap<VertexId, BTreeMap<SlotId, BTreeMap<VertexId, BTreeSet<Vec<VertexId>>>>>
}

#[allow(unused)]
impl WaveFunction {
    fn from_figure_and_lattice(lattice: &Vec<Point<f32>>, figure: &Figure) -> WaveFunction {
        panic!("Not yet implemented.")
    }

    fn remove_derivative_images(&mut self, image: &WaveImage) -> Result<(), String> {
        panic!("Not yet implemented.")
    }

    fn take_image<'function>(&'function self) -> WaveImage {
        panic!("Not yet implemented.")
    }
}

struct WaveImage {
    // TODO(akesling): Implement
    function: std::rc::Rc<WaveFunction>,
}

#[derive(PartialOrd, Ord, PartialEq, Eq, Copy, Clone)]
struct VertexId(u8);
#[derive(PartialOrd, Ord, PartialEq, Eq, Copy, Clone)]
struct SlotId(u8);

#[allow(unused)]
impl WaveImage {
    fn collapse(&self, path: &Vec<VertexId>) -> WaveImage {
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

#[allow(unused)]
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

#[allow(unused)]
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
