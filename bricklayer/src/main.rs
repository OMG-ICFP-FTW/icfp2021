use clap::{App, Arg, SubCommand};

use log::{error, info};
use log::{Level, Metadata, Record};
use log::{LevelFilter, SetLoggerError};

mod solver;

static LOGGER: SimpleLogger = SimpleLogger;

const RELEASE_VERSION: &str = env!("CARGO_PKG_VERSION");

const SOLVE_SUBCOMMAND: &str = "solve";
const SOLVE_FILE_FLAG: &str = "file";

fn argument_config<'a, 'b>() -> App<'a, 'b> {
    App::new("ICFP2021 Solution Builder Program")
        .version(RELEASE_VERSION)
        .author("Alex K. <alex@kesling.co>")
        .about("Work with problem and solution files.")
        .subcommand(
            SubCommand::with_name(SOLVE_SUBCOMMAND)
                .about("Parse and print debug info for problem files.")
                .arg(
                    Arg::with_name(SOLVE_FILE_FLAG)
                        .help("Sufficient information about how to copy data.")
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
        Some(SOLVE_SUBCOMMAND) => {
            info!("Parsing file...");
            let problem_file_path = if let Some(parse_matches) = matches.subcommand_matches(SOLVE_SUBCOMMAND) {
                if let Some(problem_file_path) = parse_matches.value_of(SOLVE_FILE_FLAG) {
                    problem_file_path
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

            let file = match std::fs::File::open(problem_file_path) {
                Ok(file) => file,
                Err(err) => {
                    println!("\nFailed to open problem file: {}\n", err);
                    print_long_help();
                    ::std::process::exit(1);
                }
            };

            let mut buf_reader = std::io::BufReader::new(file);
            let mut contents = String::new();
            buf_reader.read_to_string(&mut contents)?;

            let problem: judge::format::Problem =
                serde_json::from_str(&contents).expect("JSON was not well-formatted");
            println!("{:?}", problem);

            Ok(())
        }
        _ => {
            error!("No subcommand was provided");
            print_long_help();
            ::std::process::exit(1);
        }
    }
}
