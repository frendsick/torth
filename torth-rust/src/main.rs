use crate::class::token::Token;
use crate::lexer::tokenize_code;

mod class;
mod data_types;
mod intrinsics;
mod lexer;

fn main() -> Result<(), std::io::Error>{
    // TODO: Parse command line arguments
    // TODO: Get code file name from command line arguments
    const code_file: &str = "test.torth";
    let code: String = std::fs::read_to_string(code_file)?;
    // TODO: Perform lexical analysis
    let tokens: Vec<Token> = tokenize_code(&code, code_file);
    dbg!(&tokens);
    // TODO: Type check the program
    // TODO: Generate Assembly
    // TODO: Compile the program
    Ok(())
}
