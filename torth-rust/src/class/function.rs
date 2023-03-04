use super::signature::Signature;
use super::token::Token;

#[derive(Debug, Clone)]
pub struct Function<'a> {
    name: &'a str,
    signature: Signature,
    tokens: Vec<Token>,
}
