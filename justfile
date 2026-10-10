# show available recipes
default:
    @just --list --unsorted

# Run the CLI from the checkout (e.g. `just slips Alice Bob > slips.typ`)
slips *args:
    ./gpg-key2typ {{args}}

# Generate slips and compile them into slips.pdf (e.g. `just pdf Alice Bob`)
pdf *args:
    ./gpg-key2typ {{args}} | typst compile - slips.pdf

# Run the unit tests
test:
    python3 -m unittest discover -s tests -v

# Symlink the CLI into ~/.local/bin
install:
    install -d "{{ env_var_or_default('HOME', '~') }}/.local/bin"
    ln -sfn "{{ justfile_directory() }}/gpg-key2typ" "{{ env_var_or_default('HOME', '~') }}/.local/bin/gpg-key2typ"
