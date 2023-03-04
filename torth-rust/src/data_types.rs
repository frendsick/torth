use strum_macros::{EnumCount, EnumIter};

#[derive(Debug, Clone, PartialEq, EnumCount, EnumIter)]
pub enum DataType {
    Boolean,
    Character,
    Integer(ChunkSize),
    Pointer,
    String,
}

#[derive(Debug, Clone, PartialEq, Default, EnumCount, EnumIter)]
pub enum ChunkSize {
    Byte,
    Word,
    Dword,
    #[default]
    Qword,
}
