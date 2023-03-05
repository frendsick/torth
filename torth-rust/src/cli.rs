use clap::{Args, Parser, Subcommand};

#[derive(Debug, Parser)]
#[clap(author, version, about)]
pub struct TorthArgs {
    #[command(subcommand)]
    pub action: Action,
}

#[derive(Debug, Subcommand)]
pub enum Action {
    /// Compile a Torth program
    Compile(CompilationTarget),
    /// Compile and run a Torth program
    Run(CompilationTarget),
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
