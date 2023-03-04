use regex::{Captures, Match, Regex};

use crate::class::token::{TOKEN_REGEXES, Token, TokenType};
use crate::class::location::Location;

#[derive(Debug)]
pub struct Parser<'a> {
    tokenizer: Tokenizer<'a>,
}

impl<'a> Parser<'a> {
    pub fn init(file: &'a str) -> Self {
        Self {
            tokenizer: Tokenizer::init(file),
        }
    }

    pub fn parse(&mut self) -> Vec<Token> {
        let mut tokens: Vec<Token> = vec![];
        loop {
            let token: Option<Token> = self.tokenizer.get_next_token();
            if token.is_none() {
                break;
            }
            tokens.push(token.unwrap());
        }
        return tokens;
    }
}

#[derive(Debug)]
struct Tokenizer<'a> {
    code: String,
    file: &'a str,
    row: usize,
    column: usize,
    cursor: usize,
}

impl<'a> Tokenizer<'a> {
    fn init(file: &'a str) -> Self {
        let code: String = std::fs::read_to_string(file)
            .expect("Failed to read the file")
            .as_str()
            .to_string();
        Self {
            code: code,
            file: file,
            row: 1,
            column: 1,
            cursor: 0,
        }
    }

    fn has_more_tokens(&self) -> bool {
        self.cursor < self.code.len()
    }

    fn get_next_token(&mut self) -> Option<Token> {
        if !self.has_more_tokens() {
            return None;
        }

        // Test if the remaining code matches with any Token regex
        let unparsed_code: &str = self.code.split_at(self.cursor).1;
        for (regex, token_type) in TOKEN_REGEXES.entries() {
            let captures: Option<Captures> = Regex::new(regex).unwrap().captures(unparsed_code);
            if !captures.is_none() {
                // Take match from capture group if it is explicitly specified
                let whole_match: Option<Match> = captures.as_ref().unwrap().get(0);
                let mut token_match: Option<Match> = captures.unwrap().get(1);
                if token_match.is_none() {
                    token_match = whole_match;
                }

                // Save the old row and column
                let row: usize = self.row;
                let column: usize = self.column;

                // Calculate the new row and column after the string
                let match_str = token_match
                    .unwrap()
                    .as_str();
                let newline_count = match_str
                    .matches("\n")
                    .count();
                if newline_count > 0 {
                    self.column = match_str.len() - match_str.rfind("\n").unwrap_or(0);
                } else {
                    self.column += match_str.len();
                }
                self.row += newline_count;

                // Move cursor to the end of the parsed Token
                self.cursor += whole_match.unwrap().end();

                // Token should be skipped, e.g. whitespace or comment
                if token_type == &TokenType::None {
                    return self.get_next_token();
                }
                return Some(Token{
                    value: match_str.to_string(),
                    typ: get_token_type(match_str),
                    location: Location::new(self.file.to_string(), row, column),
                });
            }
        }

        // TODO: Enhance error reporting
        panic!(
            "Unknown Token at the start of the following code:\n{}",
            unparsed_code
        )
    }
}

pub fn get_token_type(token: &str) -> TokenType {
    for (regex, token_type) in TOKEN_REGEXES.entries() {
        // Take match from capture group if it is explicitly specified
        let is_match: bool = Regex::new(regex).unwrap().is_match(token);
        if is_match {
            return token_type.clone();
        }
    }
    panic!("Did not get TokenType for '{}'", token);
}
