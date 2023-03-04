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
    Delimiter(Delimiter),
    Identifier,
    Literal(DataType),
    Keyword(Keyword),
    Operator(Operator),
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

#[derive(Debug, Clone, PartialEq, EnumCount, EnumIter)]
pub enum Symbol {
    Colon,
    EqualSign,
}

#[derive(Debug, Clone, PartialEq, EnumCount, EnumIter)]
pub enum Keyword {
    Break,
    Cast,
    Const,
    Continue,
    Do,
    Done,
    Elif,
    Else,
    Endif,
    Enum,
    Function,
    If,
    Include,
    Memory,
    Return,
    While,
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
    r"^break"           => TokenType::Keyword(Keyword::Break),
    r"^cast"            => TokenType::Keyword(Keyword::Cast),
    r"^const"           => TokenType::Keyword(Keyword::Const),
    r"^continue"        => TokenType::Keyword(Keyword::Continue),
    r"^done"            => TokenType::Keyword(Keyword::Done),
    r"^do"              => TokenType::Keyword(Keyword::Do),
    r"^elif"            => TokenType::Keyword(Keyword::Elif),
    r"^else"            => TokenType::Keyword(Keyword::Else),
    r"^endif"           => TokenType::Keyword(Keyword::Endif),
    r"^enum"            => TokenType::Keyword(Keyword::Enum),
    r"^function"        => TokenType::Keyword(Keyword::Function),
    r"^if"              => TokenType::Keyword(Keyword::If),
    r"^include"         => TokenType::Keyword(Keyword::Include),
    r"^memory"          => TokenType::Keyword(Keyword::Memory),
    r"^return"          => TokenType::Keyword(Keyword::Return),
    r"^while"           => TokenType::Keyword(Keyword::While),

    // Delimiters
    r"^\("              => TokenType::Delimiter(Delimiter::OpenCurly),
    r"^\)"              => TokenType::Delimiter(Delimiter::CloseCurly),
    r"^\."              => TokenType::Delimiter(Delimiter::Point),
    r"^->"              => TokenType::Delimiter(Delimiter::Arrow),

    // Comparison Operators
    r"^=="              => TokenType::Operator(Operator::Comparison(Comparison::EQ)),
    r"^>="              => TokenType::Operator(Operator::Comparison(Comparison::GE)),
    r"^>"               => TokenType::Operator(Operator::Comparison(Comparison::GT)),
    r"^<="              => TokenType::Operator(Operator::Comparison(Comparison::LE)),
    r"^<"               => TokenType::Operator(Operator::Comparison(Comparison::LT)),
    r"^!="              => TokenType::Operator(Operator::Comparison(Comparison::NE)),

    // Calculation Operators
    r"^\+"              => TokenType::Operator(Operator::Calculation(Calculation::Addition)),
    r"^-"               => TokenType::Operator(Operator::Calculation(Calculation::Subtraction)),
    r"^/"               => TokenType::Operator(Operator::Calculation(Calculation::Division)),
    r"^\*"              => TokenType::Operator(Operator::Calculation(Calculation::Multiplication)),

    // Symbols
    r"^:"               => TokenType::Symbol(Symbol::Colon),
    r"^="               => TokenType::Symbol(Symbol::EqualSign),

    // Identifier - Named value representing some value or other entity
    r"^[a-zA-Z_$][a-zA-Z_$0-9]*"             => TokenType::Identifier,
);
