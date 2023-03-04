use strum_macros::{EnumCount, EnumIter};

use crate::data_types::ChunkSize;

#[derive(Debug, Clone, PartialEq)]
pub enum Intrinsic {
    Load(ChunkSize),
    Store(ChunkSize),
    And,
    Argc,
    Argv,
    Drop,
    Dup,
    Envp,
    Over,
    Print,
    Rot,
    Shl,
    Shr,
    Swap,
    Syscall(u8),
}

#[derive(Debug, Clone, PartialEq, EnumCount, EnumIter)]
pub enum Calculation {
    Addition,
    Division,
    Multiplication,
    Subtraction,
}

#[derive(Debug, Clone, PartialEq, EnumCount, EnumIter)]
pub enum Comparison {
    EQ,
    GE,
    GT,
    LE,
    LT,
    NE,
}
