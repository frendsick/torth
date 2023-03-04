#[derive(Debug, Clone)]
pub struct Location {
    pub file: String,
    pub row: usize,
    pub column: usize,
}

impl Location {
    pub fn new(file: String, row: usize, column: usize) -> Self {
        Self {
            file,
            row,
            column,
        }
    }
}
