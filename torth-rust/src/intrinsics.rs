use crate::data_types::ChunkSize;

#[derive(Debug, Clone)]
pub enum Intrinsic {
    Calculation(Calculation),
    Comparison(Comparison),
    Load(ChunkSize),
    Store(ChunkSize),
    Syscall(u8), // Syscalls have 0-6 parameters
    AND,
    DIV,
    DROP,
    DUP,
    MINUS,
    MOD,
    MUL,
    OVER,
    PLUS,
    PRINT,
    ROT,
    SHL,
    SHR,
    SWAP,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Calculation {
    Addition,
    Division,
    Multiplication,
    Subtraction,
}

#[derive(Debug, Clone, PartialEq)]
pub enum Comparison {
    EQ,
    GE,
    GT,
    LE,
    LT,
    NE,
}