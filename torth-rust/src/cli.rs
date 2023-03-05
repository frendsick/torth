use clap::{Args, Parser, Subcommand};

/// Torth compiler
#[derive(Debug, Parser)]
#[command(author, version, about)]
pub struct TorthArgs {
    #[command(subcommand)]
    pub action: CliAction,
}

#[derive(Debug, Subcommand)]
pub enum CliAction {
    /// Compile a Torth program
    Compile(CompilationTarget),
}

#[derive(Debug, Args)]
pub struct CompilationTarget {
    /// Torth code file
    pub torth_file: String,
    /// Output file
    #[arg(short, long, value_name="FILE")]
    pub out: Option<String>,
    /// Save the generated assembly file
    #[arg(short, long)]
    pub save_asm: bool,
    /// Output compilation steps
    #[arg(short, long)]
    pub verbose: bool,
}
