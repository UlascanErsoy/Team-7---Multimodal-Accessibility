# Contributing to TOPH

Toph is targetting `Python >= 3.10` , please ensure you have a version that matches this.

Toph is built on `scipy`, `numpy` and `pyaudio`. Please make sure you have `Pyaudio >= 2.14.0`. If you are on GNU / linux you may need to build from [source](https://github.com/CristiFati/pyaudio).

## Setup 

- Create a branch (from dev **not** main) with a short (but descriptive) name for your feature or fix.

1. *(Optional)* Create a virtualenvironment

```
python3.10 -m venv menv
```

```
source menv/bin/activate
```

2. Navigate into `toph/` and execute;

```
pip install .
```

3. Install development dependencies

```
pip install -r dev-requirements.txt
```

4. Install the pre-commit hooks

```
pre-commit install
```

5. *(Optional)* Test that your installation is working correctly by running some scripts from the examples/ folder

6. *(For spatial audio)* Download an HRIR file from the CIPIC database.

7. *(For spatial audio)* create a `.env` file in your work environment.

```
CIPIC_PATH=<path-to-your-hrir-file>
```

[CIPIC Github](https://github.com/amini-allight/cipic-hrtf-database/tree/master/standard_hrir_database)

6. **Develop** 

## Notes

- Unit tests are currently **not** required. Please write documentation and example cases (`examples/`) for your features.
- Type annotations are required, docstrings are greatly appreciated.
- All pull requests are to **dev** first.
- There is no **CI** currently (except pre-commit if you count that as CI)




