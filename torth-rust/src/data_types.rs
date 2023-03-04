#[derive(Debug, Clone, PartialEq)]
pub enum DataType {
    Boolean,
    Character,
    Integer(ChunkSize),
    Pointer,
    String,
}

#[derive(Debug, Clone, PartialEq)]
pub enum ChunkSize {
    Byte,
    Word,
    Dword,
    Qword,
}
