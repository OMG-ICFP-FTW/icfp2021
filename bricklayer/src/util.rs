use std::collections::BTreeSet;

use geo::{Coordinate, Polygon};
use judge::format::{Position};

pub fn compute_bounded_integer_points(boundary: &Polygon<f32>) -> Vec<geo::Point<f32>> {
    use geo::algorithm::euclidean_distance::EuclideanDistance;
    use geo::extremes::Extremes as _;

    let mut bounded_integer_points = vec![];
    let extremes = boundary.extremes().unwrap();
    for x in (extremes.x_min.coord.x as usize)..((extremes.x_max.coord.x + 1.0) as usize) {
        for y in (extremes.y_min.coord.y as usize)..((extremes.y_max.coord.y + 1.0) as usize) {
            let point = geo::Point(Coordinate {
                x: x as f32,
                y: y as f32,
            });
            if point.euclidean_distance(boundary) < 0.00001 {
                bounded_integer_points.push(point)
            } else {
            }
        }
    }

    bounded_integer_points
}

pub fn positions_to_polygon(positions: &[Position]) -> Polygon<f32> {
    let coords: Vec<geo::Coordinate<f32>> = positions
        .iter()
        .map(|p| geo::Coordinate {
            x: p.x as f32,
            y: p.y as f32,
        })
        .collect();

    geo::Polygon::new(geo::LineString::from(coords), vec![])
}

#[derive(PartialEq, Eq, PartialOrd, Ord, Debug, Clone, Copy, Hash)]
pub struct Point {
    pub x: i16,
    pub y: i16,
}

impl Point {
    pub fn from_pos(pos: judge::format::Position) -> Self {
        Point {
            x: pos.x as i16,
            y: pos.y as i16,
        }
    }

    pub fn to_pos(self) -> judge::format::Position {
        Position {
            x: self.x as u32,
            y: self.y as u32,
        }
    }

    pub fn sub(self, other: Point) -> Self {
        Self { x: self.x - other.x, y: self.y - other.y }
    }

    pub fn abs(self) -> Self {
        Self { x: self.x.abs(), y: self.y.abs() }
    }

    // pub fn add(self, other: Point) -> Self {
    //     Self { x: self.x + other.x, y: self.y + other.y }
    // }
}

pub fn points_inside_hole(hole: &[Position]) -> BTreeSet<Point> {
    let hole_polygon = positions_to_polygon(hole);
    let float_points = compute_bounded_integer_points(&hole_polygon);
    float_points
        .into_iter()
        .map(|p| Point {
            x: p.x() as i16,
            y: p.y() as i16,
        })
        .collect()
}
