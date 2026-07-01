//! {{ cookiecutter.project_name_display }} — core library.
//!
//! <!-- TODO: Describe what this library does and its public API. -->

#![deny(missing_docs)]

/// Error types for library operations.
pub mod error;

mod core;

pub use core::greet;
pub use error::ProjectError;
