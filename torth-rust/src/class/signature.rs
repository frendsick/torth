use super::token::TokenType;

#[derive(Debug, Clone)]
pub struct Signature {
    param_types: Vec<TokenType>,
    return_types: Vec<TokenType>,
}
