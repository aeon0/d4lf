# D4 Loot Filter

## Linting
The CI will fail if the linter would change any files. You can run linting by with:
```bash
conda activate d4lf
black .
```
To ignore certain code parts from formatting
```python
# fmt: off
# ...
# fmt: on

# fmt: skip
# ...
```
Setup vs-code by using the black formater extension. Also turn on "trim trailing whitespaces" is vs-code settings.
