# QuinaryRam

QuinaryRam is a dependency-free reference implementation of mutable integer memory controlled by five explicit operations: erase (`-2`), decay toward zero (`-1`), bypass (`0`), saturating accumulate (`1`), and bounded overwrite (`2`).

```bash
python -m quinaryram examples/program.json --out snapshot.json
```

Each step validates its complete control and operand matrices before changing memory, so malformed updates are atomic failures. Values are clamped to operator-defined integer bounds and every step reports changed cells, saturation events, and control counts. Versioned JSON snapshots round-trip deterministically.

## Honest scope

This is a readable reference kernel, not a tensor framework, trained model, differentiable estimator, or speed claim. It defines testable state-transition invariants that optimized implementations can compare against. It was independently implemented for this public repository and contains no private project code or pipelines.

## Test

`python -m unittest discover -s tests -v`

## Fund more development

Donations increase RequiredTruth development production. See [SUPPORT.md](SUPPORT.md); confirmed donors may claim a transaction hash in an issue and request a specific direction.

Apache-2.0 licensed.


## Install and run

```sh
chmod +x install.sh run.sh
./install.sh
./run.sh
./cli.sh --help
```


## Standard launcher

`./run.sh` is the normal entry point. It runs `./install.sh` automatically when setup is missing, then opens the PySide6 control panel with live output and actions for the bundled program, real test suite, repair, and stop. Use `./cli.sh` for CLI-only operation and `./test.sh` to run the same tests outside the GUI.
