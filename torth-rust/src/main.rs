use crate::class::token::Token;
use crate::lexer::Parser;

mod class;
mod data_types;
mod intrinsics;
mod lexer;

fn main() -> Result<(), std::io::Error>{
    // TODO: Parse command line arguments
    // TODO: Get code file name from command line arguments
    const CODE_FILE: &str = "test.torth";
    let mut parser = Parser::init(&CODE_FILE);
    let tokens: Vec<Token> = parser.parse();
    dbg!(&tokens);
    // TODO: Type check the program
    // TODO: Generate Assembly
    // TODO: Compile the program
    Ok(())
}
