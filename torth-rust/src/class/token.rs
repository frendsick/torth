use phf::phf_ordered_map;
use strum_macros::{EnumCount, EnumIter};

use crate::data_types::{ChunkSize, DataType};
use crate::intrinsics::{Calculation, Comparison, Operator};

use super::location::Location;

#[derive(Debug, Clone)]
pub struct Token {
    pub value: String,
    pub typ: TokenType,
    pub location: Location,
}

#[derive(Debug, Clone, PartialEq)]
pub enum TokenType {
    Calculation(Operator),
    Comparison(Operator),
    Delimiter(Delimiter),
    Identifier,
    Literal(DataType),
    Keyword,
    Symbol(Symbol),
    None,
}

#[derive(Debug, Clone, PartialEq, EnumCount, EnumIter)]
pub enum Delimiter {
    Arrow,
    Point,
    OpenCurly,
    CloseCurly,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Symbol {
    Colon,
    EqualSign,
}

pub const TOKEN_REGEXES: phf::OrderedMap<&str, TokenType> = phf_ordered_map!(
    r"^\s+"             => TokenType::None,

    // Comments
    r"^//.*"            => TokenType::None, // Single-line comment
    r"^/\*[\s\S]*?\*/"  => TokenType::None, // Multi-line comment

    // Literals
    r"(?i)^true"        => TokenType::Literal(DataType::Boolean),
    r"(?i)^false"       => TokenType::Literal(DataType::Boolean),
    r"^'[^']'"          => TokenType::Literal(DataType::Character),
    r"^\d+"             => TokenType::Literal(DataType::Integer(ChunkSize::Qword)),
    r#"^"[^"]*""#       => TokenType::Literal(DataType::String),

    // Keywords
    r"^break"           => TokenType::Keyword,
    r"^cast"            => TokenType::Keyword,
    r"^const"           => TokenType::Keyword,
    r"^continue"        => TokenType::Keyword,
    r"^done"            => TokenType::Keyword,
    r"^do"              => TokenType::Keyword,
    r"^elif"            => TokenType::Keyword,
    r"^else"            => TokenType::Keyword,
    r"^endif"           => TokenType::Keyword,
    r"^enum"            => TokenType::Keyword,
    r"^function"        => TokenType::Keyword,
    r"^if"              => TokenType::Keyword,
    r"^include"         => TokenType::Keyword,
    r"^memory"          => TokenType::Keyword,
    r"^return"          => TokenType::Keyword,
    r"^while"           => TokenType::Keyword,

    // Delimiters
    r"^\("              => TokenType::Delimiter(Delimiter::OpenCurly),
    r"^\)"              => TokenType::Delimiter(Delimiter::CloseCurly),
    r"^\."              => TokenType::Delimiter(Delimiter::Point),
    r"^->"              => TokenType::Delimiter(Delimiter::Arrow),

    // Comparison Operators
    r"^=="              => TokenType::Comparison(Operator::Comparison(Comparison::EQ)),
    r"^>="              => TokenType::Comparison(Operator::Comparison(Comparison::GE)),
    r"^>"               => TokenType::Comparison(Operator::Comparison(Comparison::GT)),
    r"^<="              => TokenType::Comparison(Operator::Comparison(Comparison::LE)),
    r"^<"               => TokenType::Comparison(Operator::Comparison(Comparison::LT)),
    r"^!="              => TokenType::Comparison(Operator::Comparison(Comparison::NE)),

    // Calculation Operators
    r"^\+"              => TokenType::Calculation(Operator::Calculation(Calculation::Addition)),
    r"^-"               => TokenType::Calculation(Operator::Calculation(Calculation::Subtraction)),
    r"^/"               => TokenType::Calculation(Operator::Calculation(Calculation::Division)),
    r"^\*"              => TokenType::Calculation(Operator::Calculation(Calculation::Multiplication)),

    // Symbols
    r"^:"               => TokenType::Symbol(Symbol::Colon),
    r"^="               => TokenType::Symbol(Symbol::EqualSign),

    // Identifier - Named value representing some value or other entity
    r"^[a-zA-Z_$][a-zA-Z_$0-9]*"             => TokenType::Identifier,
);
