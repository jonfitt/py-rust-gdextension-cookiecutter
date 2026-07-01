# Architecture

<!-- TODO: Describe how the core library, GDExtension, and demos relate. -->

## Workspace overview

```text
{{ cookiecutter.project_slug }} (core library)
    └── extensions/{{ cookiecutter.gd_crate_name }} (Godot GDExtension cdylib)

examples/{{ cookiecutter.project_slug }}_cli (native CLI demo)
{% if cookiecutter.include_bevy_demo == "yes" %}
examples/{{ cookiecutter.project_slug }}_visualizer (Bevy demo)
{% endif %}
```

## Core library

<!-- TODO: List modules and responsibilities. -->

## GDExtension

<!-- TODO: Document which core APIs are exposed to Godot. -->

See also [`godot.md`](godot.md) for the Godot-facing API.
