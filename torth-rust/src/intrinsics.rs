use strum_macros::{EnumCount, EnumIter};

use crate::data_types::ChunkSize;

#[derive(Debug, Clone, PartialEq, EnumCount, EnumIter)]
pub enum Intrinsic {
    And,
    Argc,
    Argv,
    Drop,
    Dup,
    Envp,
    Load(ChunkSize),
    Nth,
    Over,
    Or,
    Print,
    Rot,
    Shl,
    Shr,
    Store(ChunkSize),
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
