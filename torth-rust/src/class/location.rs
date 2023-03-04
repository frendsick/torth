#[derive(Debug, Clone)]
pub struct Location<'a> {
    pub file: &'a str,
    pub row: usize,
    pub column: usize,
}

impl<'a> Location<'a> {
    pub fn new(file: &'a str, row: usize, column: usize) -> Self {
        Self {
            file,
            row,
            column,
        }
    }
}
