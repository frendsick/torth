use clap::Parser;

use class::token::Token;
use lexer::tokenize_code_file;
use cli::{CliAction, TorthArgs};

mod class;
mod cli;
mod data_types;
mod intrinsics;
mod lexer;

fn main() {
    cli_action(TorthArgs::parse());
}

fn cli_action(args: TorthArgs) {
    match args.action {
        // ./torth-rust compile <TORTH_FILE>
        CliAction::Compile(target) => compile_torth_file(target.torth_file, target.out),
    }
}

fn compile_torth_file(torth_file: String, _out_file: Option<String>) {
    let tokens: Vec<Token> = tokenize_code_file(&torth_file);
    dbg!(&tokens);
    // TODO: Type check the program
    // TODO: Generate Assembly
    // TODO: Compile the program
}
