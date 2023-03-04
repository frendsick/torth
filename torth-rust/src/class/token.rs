use super::location::Location;

#[derive(Debug, Clone)]
pub struct Token<'a> {
    pub value: &'a str,
    pub typ: TokenType,
    pub location: Location<'a>,
}

#[derive(Debug, Clone)]
pub enum TokenType {
    KEYWORD,
    WORD,
}
