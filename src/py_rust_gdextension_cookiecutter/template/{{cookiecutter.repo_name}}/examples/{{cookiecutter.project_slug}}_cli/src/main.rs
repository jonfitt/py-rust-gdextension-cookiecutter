use {{ cookiecutter.project_slug }}::greet;

fn main() {
    match greet("native demo") {
        Ok(message) => println!("{message}"),
        Err(error) => eprintln!("error: {error}"),
    }
}
