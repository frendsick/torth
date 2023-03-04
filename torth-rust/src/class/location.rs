#[derive(Debug, Clone, PartialEq)]
pub struct Location {
    pub row: usize,
    pub column: usize,
    pub file: Option<String>,
}

impl Location {
    pub fn new(row: usize, column: usize, file: Option<String>) -> Self {
        Self {
            row,
            column,
            file,
        }
    }
}
