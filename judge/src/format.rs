use serde::{Deserialize, Deserializer, Serialize, Serializer};

#[derive(Debug)]
pub struct Position {
    x: u32,
    y: u32,
}

#[derive(Serialize, Deserialize, Debug)]
struct PositionHelper(u32, u32);

impl Serialize for Position {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        use serde::ser::SerializeSeq as _;

        let mut seq = serializer.serialize_seq(Some(2))?;
        seq.serialize_element(&self.x)?;
        seq.serialize_element(&self.y)?;
        seq.end()
    }
}

impl<'de> Deserialize<'de> for Position {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        Deserialize::deserialize(deserializer).map(|PositionHelper(x, y)| Position { x, y })
    }
}

#[derive(Serialize, Deserialize, Debug)]
pub struct EdgeId(u32);

#[derive(Debug)]
pub struct Edge {
    start: EdgeId,
    end: EdgeId,
}

#[derive(Serialize, Deserialize, Debug)]
struct EdgeHelper(EdgeId, EdgeId);

impl Serialize for Edge {
    fn serialize<S>(&self, serializer: S) -> Result<S::Ok, S::Error>
    where
        S: Serializer,
    {
        use serde::ser::SerializeSeq as _;

        let mut seq = serializer.serialize_seq(Some(2))?;
        seq.serialize_element(&self.start)?;
        seq.serialize_element(&self.end)?;
        seq.end()
    }
}

impl<'de> Deserialize<'de> for Edge {
    fn deserialize<D>(deserializer: D) -> Result<Self, D::Error>
    where
        D: Deserializer<'de>,
    {
        Deserialize::deserialize(deserializer).map(|EdgeHelper(start, end)| Edge { start, end })
    }
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Hole(Vec<Position>);

#[derive(Serialize, Deserialize, Debug)]
pub struct Figure {
    edges: Vec<Edge>,
    vertices: Vec<Position>,
}

#[derive(Serialize, Deserialize, Debug)]
pub struct Problem {
    hole: Hole,
    figure: Figure,
    epsilon: u32,
}
