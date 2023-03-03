use super::location::Location;

#[derive(Debug, Clone)]
pub enum TokenType {
    KEYWORD,
    WORD,
}

#[derive(Debug, Clone)]
pub struct Token<'a> {
    value: &'a str,
    typ: TokenType,
    location: Location<'a>,
}
