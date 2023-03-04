use phf::phf_ordered_map;
use strum_macros::{EnumCount, EnumIter};

use crate::data_types::{DataType, ChunkSize};
use crate::intrinsics::{Calculation, Comparison, Intrinsic};

use super::location::Location;

#[derive(Debug, Clone)]
pub struct Token {
    pub value: String,
    pub typ: TokenType,
    pub location: Location,
}

#[derive(Debug, Clone, PartialEq)]
pub enum TokenType {
    Calculation(Calculation),
    Comparison(Comparison),
    Delimiter(Delimiter),
    Identifier,
    Intrinsic(Intrinsic),
    Literal(DataType),
    Keyword(Keyword),
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

    // Intrinsics
    r"^and"             => TokenType::Intrinsic(Intrinsic::And),
    r"^argc"            => TokenType::Intrinsic(Intrinsic::Argc),
    r"^argv"            => TokenType::Intrinsic(Intrinsic::Argv),
    r"^drop"            => TokenType::Intrinsic(Intrinsic::Drop),
    r"^dup"             => TokenType::Intrinsic(Intrinsic::Dup),
    r"^envp"            => TokenType::Intrinsic(Intrinsic::Envp),
    r"^load_byte"       => TokenType::Intrinsic(Intrinsic::Load(ChunkSize::Byte)),
    r"^load_word"       => TokenType::Intrinsic(Intrinsic::Load(ChunkSize::Word)),
    r"^load_dword"      => TokenType::Intrinsic(Intrinsic::Load(ChunkSize::Dword)),
    r"^load_qword"      => TokenType::Intrinsic(Intrinsic::Load(ChunkSize::Qword)),
    r"^store_byte"      => TokenType::Intrinsic(Intrinsic::Store(ChunkSize::Byte)),
    r"^store_word"      => TokenType::Intrinsic(Intrinsic::Store(ChunkSize::Word)),
    r"^store_dword"     => TokenType::Intrinsic(Intrinsic::Store(ChunkSize::Dword)),
    r"^store_qword"     => TokenType::Intrinsic(Intrinsic::Store(ChunkSize::Qword)),
    r"^over"            => TokenType::Intrinsic(Intrinsic::Over),
    r"^print"           => TokenType::Intrinsic(Intrinsic::Print),
    r"^rot"             => TokenType::Intrinsic(Intrinsic::Rot),
    r"^shl"             => TokenType::Intrinsic(Intrinsic::Shl),
    r"^shr"             => TokenType::Intrinsic(Intrinsic::Shr),
    r"^swap"            => TokenType::Intrinsic(Intrinsic::Swap),
    r"^syscall[0-6]"    => TokenType::Intrinsic(Intrinsic::Syscall),

    // Delimiters
    r"^\("              => TokenType::Delimiter(Delimiter::OpenCurly),
    r"^\)"              => TokenType::Delimiter(Delimiter::CloseCurly),
    r"^\."              => TokenType::Delimiter(Delimiter::Point),
    r"^->"              => TokenType::Delimiter(Delimiter::Arrow),

    // Comparison Operators
    r"^=="              => TokenType::Comparison(Comparison::EQ),
    r"^>="              => TokenType::Comparison(Comparison::GE),
    r"^>"               => TokenType::Comparison(Comparison::GT),
    r"^<="              => TokenType::Comparison(Comparison::LE),
    r"^<"               => TokenType::Comparison(Comparison::LT),
    r"^!="              => TokenType::Comparison(Comparison::NE),

    // Calculation Operators
    r"^\+"              => TokenType::Calculation(Calculation::Addition),
    r"^-"               => TokenType::Calculation(Calculation::Subtraction),
    r"^/"               => TokenType::Calculation(Calculation::Division),
    r"^\*"              => TokenType::Calculation(Calculation::Multiplication),

    // Symbols
    r"^:"               => TokenType::Symbol(Symbol::Colon),
    r"^="               => TokenType::Symbol(Symbol::EqualSign),

    // Identifier - Named value representing some value or other entity
    r"^[a-zA-Z_$][a-zA-Z_$0-9]*" => TokenType::Identifier,
);
