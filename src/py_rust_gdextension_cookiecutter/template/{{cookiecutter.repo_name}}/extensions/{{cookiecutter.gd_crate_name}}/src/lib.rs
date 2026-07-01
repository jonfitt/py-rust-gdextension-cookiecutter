//! Godot 4 GDExtension for [`{{ cookiecutter.project_slug }}`].

use {{ cookiecutter.project_slug }}::greet;
use godot::prelude::*;

struct {{ cookiecutter.project_name_display | replace(' ', '') }}Extension;

#[gdextension]
unsafe impl ExtensionLibrary for {{ cookiecutter.project_name_display | replace(' ', '') }}Extension {}

/// Example Godot class that delegates to the core library.
#[derive(GodotClass)]
#[class(base = RefCounted)]
struct {{ cookiecutter.project_name_display | replace(' ', '') }}Api {
    base: Base<RefCounted>,
}

#[godot_api]
impl IRefCounted for {{ cookiecutter.project_name_display | replace(' ', '') }}Api {
    fn init(base: Base<RefCounted>) -> Self {
        Self { base }
    }
}

#[godot_api]
impl {{ cookiecutter.project_name_display | replace(' ', '') }}Api {
    /// Return a greeting from the Rust core library.
    #[func]
    fn greet(&self, name: String) -> String {
        match greet(name.as_str()) {
            Ok(message) => message,
            Err(error) => format!("error: {error}"),
        }
    }
}
