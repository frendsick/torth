use lazy_static::lazy_static;
use regex::Regex;

use crate::class::{token::{Token, TokenType}, location::Location};

pub fn tokenize_code<'a>(code: &'a str, code_file: &'a str) -> Vec<Token<'a>> {
    lazy_static! {
        static ref RE: Regex = Regex::new(r#"".*?"|'.*?'|\S+"#).unwrap();
    }
    let mut matches = RE.find_iter(code);
    let mut tokens: Vec<Token> = vec![];
    loop {
        let token_match = matches.next();
        if token_match.is_none() { break }
        let value = token_match.unwrap().as_str();
        tokens.push(
            Token {
                value,
                // TODO: Parse correct TokenType
                typ: TokenType::WORD,
                // TODO: Parse correct Location
                location: Location::new(code_file, 1, 1),
            }
        )

    }
    tokens
}
