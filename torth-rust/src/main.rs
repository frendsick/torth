use clap::Parser;

use class::token::Token;
use lexer::tokenize_code_file;
use cli::TorthArgs;

mod class;
mod cli;
mod data_types;
mod intrinsics;
mod lexer;

fn main() {
    // TODO: Parse command line arguments
    let args = TorthArgs::parse();
    dbg!(&args);
    // TODO: Get code file name from command line arguments
    const CODE_FILE: &str = "test.torth";
    // let mut parser = Parser::init(&CODE_FILE);
    let tokens: Vec<Token> = tokenize_code_file(CODE_FILE);
    dbg!(&tokens);
    // TODO: Type check the program
    // TODO: Generate Assembly
    // TODO: Compile the program
}
