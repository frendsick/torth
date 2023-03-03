use crate::data_types::DataType;
use crate::intrinsics::Intrinsic;

use super::function::Function;
use super::token::Token;

pub struct Op<'a> {
    id: usize,
    typ: OpType,
    token: Token<'a>,
    function: Function<'a>,
}

pub enum OpType {
    Intrinsic(Intrinsic),
    Push(DataType)
}
