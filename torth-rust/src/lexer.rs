use regex::{Captures, Match, Regex};

use crate::class::location::Location;
use crate::class::token::{Token, TokenType, TOKEN_REGEXES};

pub fn tokenize_code_file(file: &str) -> Vec<Token> {
    let code: String = std::fs::read_to_string(file)
        .expect("Failed to read the file")
        .as_str()
        .to_string();
    let mut tokens: Vec<Token> = vec![];
    let mut row: usize = 1;
    let mut column: usize = 1;
    let mut cursor: usize = 0;
    loop {
        let token: Option<Token> = get_next_token(&code, file, &mut cursor, &mut row, &mut column);
        if token.is_none() {
            break;
        }
        tokens.push(token.unwrap());
    }
    return tokens;
}

fn get_next_token(
    code: &str,
    code_file: &str,
    cursor: &mut usize,
    row: &mut usize,
    column: &mut usize,
) -> Option<Token> {
    if *cursor >= code.len() {
        return None;
    }

    // Test if the remaining code matches with any Token regex
    let unparsed_code: &str = code.split_at(*cursor).1;
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
            let token_row: usize = *row;
            let token_column: usize = *column;

            // Calculate the new row and column after the string
            let match_str = token_match.unwrap().as_str();
            let newline_count = match_str.matches("\n").count();
            if newline_count > 0 {
                *column = match_str.len() - match_str.rfind("\n").unwrap_or(0);
            } else {
                *column += match_str.len();
            }
            *row += newline_count;

            // Move cursor to the end of the parsed Token
            *cursor += whole_match.unwrap().end();

            // Token should be skipped, e.g. whitespace or comment
            if token_type == &TokenType::None {
                return get_next_token(code, code_file, cursor, row, column);
            }
            return Some(Token {
                value: match_str.to_string(),
                typ: get_token_type(match_str),
                location: Location::new(code_file.to_string(), token_row, token_column),
            });
        }
    }

    // TODO: Enhance error reporting
    panic!(
        "Unknown Token at the start of the following code:\n{}",
        unparsed_code
    )
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

#[cfg(test)]
mod tests {
    use strum::{EnumCount, IntoEnumIterator};

    use super::*;
    use crate::{data_types::DataType, class::token::Delimiter, intrinsics::{Calculation, Operator, Comparison}};

    const TEST_FOLDER: &str = "tests";

    #[test]
    #[should_panic(expected = "Failed to read the file")]
    fn lex_nonexistent_file() {
        tokenize_code_file("nonexistent.torth");
    }

    #[test]
    fn lex_empty_file() {
        let tokens: Vec<Token> = tokenize_code_file(&format!("{TEST_FOLDER}/lex_empty.torth"));
        assert!(tokens.is_empty())
    }

    #[test]
    fn lex_whitespace() {
        let tokens: Vec<Token> = tokenize_code_file(&format!("{TEST_FOLDER}/lex_whitespace.torth"));
        assert!(tokens.is_empty())
    }

    #[test]
    fn lex_comments() {
        let tokens: Vec<Token> = tokenize_code_file(&format!("{TEST_FOLDER}/lex_comments.torth"));
        assert!(tokens.is_empty())
    }

    #[test]
    fn lex_calculations() {
        let tokens: Vec<Token> = tokenize_code_file(&format!("{TEST_FOLDER}/lex_calculations.torth"));
        // Are all Calculation operators taken into account in the test file
        assert_eq!(tokens.len(), Calculation::COUNT);
        // Are tokens lexed correctly as certain calculation operations
        for (i, operation) in Calculation::iter().enumerate() {
            assert_eq!(TokenType::Operator(Operator::Calculation(operation)), tokens[i].typ)
        }
    }

    #[test]
    fn lex_comparisons() {
        let tokens: Vec<Token> = tokenize_code_file(&format!("{TEST_FOLDER}/lex_comparisons.torth"));
        // Are all Calculation operators taken into account in the test file
        assert_eq!(tokens.len(), Comparison::COUNT);
        // Are tokens lexed correctly as certain calculation operations
        for (i, operation) in Comparison::iter().enumerate() {
            assert_eq!(TokenType::Operator(Operator::Comparison(operation)), tokens[i].typ)
        }
    }

    #[test]
    fn lex_delimiters() {
        let tokens: Vec<Token> = tokenize_code_file(&format!("{TEST_FOLDER}/lex_delimiters.torth"));
        // Are all Delimiters taken into account in the test file
        assert_eq!(tokens.len(), Delimiter::COUNT);
        // Are tokens lexed correctly as certain delimiters
        for (i, delimiter) in Delimiter::iter().enumerate() {
            assert_eq!(TokenType::Delimiter(delimiter), tokens[i].typ)
        }
    }

    #[test]
    fn lex_literals() {
        let tokens: Vec<Token> = tokenize_code_file(&format!("{TEST_FOLDER}/lex_literals.torth"));
        // Are all DataTypes taken into account in the test file
        assert_eq!(tokens.len(), DataType::COUNT);
        // Are tokens lexed correctly as literal with certain type
        for (i, data_type) in DataType::iter().enumerate() {
            // Pointer literals do not exist
            if data_type == DataType::Pointer {
                continue;
            }
            assert_eq!(TokenType::Literal(data_type), tokens[i].typ)
        }
    }

    #[test]
    fn lex_keywords() {
        let tokens: Vec<Token> = tokenize_code_file(&format!("{TEST_FOLDER}/lex_keywords.torth"));
        assert!(!tokens.is_empty());
        for token in tokens {
            assert_eq!(
                TokenType::Keyword,
                token.typ,
                "Token '{}' was lexed as {:?}",
                token.value,
                token.typ
            );
        }
    }
}
