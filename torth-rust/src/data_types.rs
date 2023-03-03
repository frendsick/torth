pub enum DataType {
    BOOL,
    CHAR,
    INT(ChunkSize),
    PTR,
    STR,
}

pub enum ChunkSize {
    Byte,
    Word,
    Dword,
    Qword,
}
