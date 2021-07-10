use clap::{App, Arg, SubCommand};

use log::{error, info};
use log::{Level, Metadata, Record};
use log::{LevelFilter, SetLoggerError};

mod dislikes;
mod format;

static LOGGER: SimpleLogger = SimpleLogger;

const RELEASE_VERSION: &str = env!("CARGO_PKG_VERSION");

const PARSE_SUBCOMMAND: &str = "parse";
const PARSE_FILE_FLAG: &str = "file";

const VALIDATE_SUBCOMMAND: &str = "validate";
const VALIDATE_PROBLEM_FILE_FLAG: &str = "problem";
const VALIDATE_SOLUTION_FILE_FLAG: &str = "solution";

fn argument_config<'a, 'b>() -> App<'a, 'b> {
    App::new("ICFP2021 Judge Program")
        .version(RELEASE_VERSION)
        .author("Alex K. <alex@kesling.co>")
        .about("Work with problem and solution files.")
        .subcommand(
            SubCommand::with_name(PARSE_SUBCOMMAND)
                .about("Parse and print debug info for problem files.")
                .arg(
                    Arg::with_name(PARSE_FILE_FLAG)
                        .help("Sufficient information about how to copy data.")
                        .required(true),
                ),
        )
        .subcommand(
            SubCommand::with_name(VALIDATE_SUBCOMMAND)
                .about("Validate a solution file for a problem")
                .arg(
                    Arg::with_name(VALIDATE_PROBLEM_FILE_FLAG)
                        .help("The problem file to validate against")
                        .required(true),
                )
                .arg(
                    Arg::with_name(VALIDATE_SOLUTION_FILE_FLAG)
                        .help("The solution file to validate")
                        .required(true),
                ),
        )
}

struct SimpleLogger;

impl log::Log for SimpleLogger {
    fn enabled(&self, metadata: &Metadata) -> bool {
        metadata.level() <= Level::Info
    }

    fn log(&self, record: &Record) {
        if self.enabled(record.metadata()) {
            println!("{}: {}", record.level(), record.args());
        }
    }

    fn flush(&self) {}
}

#[allow(clippy::clippy::missing_errors_doc)]
pub fn init_logger() -> Result<(), SetLoggerError> {
    log::set_logger(&LOGGER).map(|()| log::set_max_level(LevelFilter::Info))
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    use std::io::prelude::*;

    match init_logger() {
        Ok(_) => (),
        Err(err) => {
            panic!("Logger failed to initialize with error: {}", err);
        }
    };

    let cli_config = argument_config();

    let print_long_help = || {
        let mut out_buffer = vec![];
        let _ = argument_config().write_long_help(&mut out_buffer);
        info!("\n{}", String::from_utf8(out_buffer).unwrap());
    };

    let matches = cli_config.get_matches();
    match matches.subcommand_name() {
        Some(PARSE_SUBCOMMAND) => {
            info!("Parsing file...");
            let file = if let Some(parse_matches) = matches.subcommand_matches(PARSE_SUBCOMMAND) {
                if let Some(problem_file_path) = parse_matches.value_of(PARSE_FILE_FLAG) {
                    match std::fs::File::open(problem_file_path) {
                        Ok(file) => file,
                        Err(err) => {
                            println!("\nFailed to open problem file: {}\n", err);
                            print_long_help();
                            ::std::process::exit(1);
                        }
                    }
                } else {
                    error!("No problem file was provided.");
                    print_long_help();
                    ::std::process::exit(1);
                }
            } else {
                error!("Unknown error occurred.");
                print_long_help();
                ::std::process::exit(1);
            };

            let mut buf_reader = std::io::BufReader::new(file);
            let mut contents = String::new();
            buf_reader.read_to_string(&mut contents)?;

            let problem: format::Problem =
                serde_json::from_str(&contents).expect("JSON was not well-formatted");
            println!("{:?}", problem);

            Ok(())
        }
        Some(VALIDATE_SUBCOMMAND) => {
            let problem_file =
                if let Some(validate_matches) = matches.subcommand_matches(VALIDATE_SUBCOMMAND) {
                    if let Some(problem_file_path) =
                        validate_matches.value_of(VALIDATE_PROBLEM_FILE_FLAG)
                    {
                        match std::fs::File::open(problem_file_path) {
                            Ok(file) => file,
                            Err(err) => {
                                println!("\nFailed to open problem file: {}\n", err);
                                print_long_help();
                                ::std::process::exit(1);
                            }
                        }
                    } else {
                        error!("No problem file was provided.");
                        print_long_help();
                        ::std::process::exit(1);
                    }
                } else {
                    error!("Unknown error occurred when matching problem flag.");
                    print_long_help();
                    ::std::process::exit(1);
                };

            let solution_file =
                if let Some(validate_matches) = matches.subcommand_matches(VALIDATE_SUBCOMMAND) {
                    if let Some(solution_file_path) =
                        validate_matches.value_of(VALIDATE_SOLUTION_FILE_FLAG)
                    {
                        match std::fs::File::open(solution_file_path) {
                            Ok(file) => file,
                            Err(err) => {
                                println!("\nFailed to open solution file: {}\n", err);
                                print_long_help();
                                ::std::process::exit(1);
                            }
                        }
                    } else {
                        error!("No solution file was provided.");
                        print_long_help();
                        ::std::process::exit(1);
                    }
                } else {
                    error!("Unknown error occurred when matching solution flag.");
                    print_long_help();
                    ::std::process::exit(1);
                };

            let mut problem_buf_reader = std::io::BufReader::new(problem_file);
            let mut problem_contents = String::new();
            problem_buf_reader.read_to_string(&mut problem_contents)?;
            let problem: format::Problem =
                serde_json::from_str(&problem_contents).expect("JSON was not well-formatted");

            let mut solution_buf_reader = std::io::BufReader::new(solution_file);
            let mut solution_contents = String::new();
            solution_buf_reader.read_to_string(&mut solution_contents)?;
            let solution: format::Solution =
                serde_json::from_str(&solution_contents).expect("JSON was not well-formatted");

            println!(
                "Solution was valid: {:?}",
                dislikes::figure_is_valid(&problem, &solution)
            );

            Ok(())
        }
        _ => {
            error!("No subcommand was provided");
            print_long_help();
            ::std::process::exit(1);
        }
    }
}
