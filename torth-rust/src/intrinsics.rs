use crate::data_types::ChunkSize;

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

pub enum Calculation {
    Addition,
    Division,
    Multiplication,
    Subtraction,
}

pub enum Comparison {
    EQ,
    GE,
    GT,
    LE,
    LT,
    NE,
}
