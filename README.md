# Mode used for my paper "Optimal configurations of Minimally Intelligent additive manufacturing machines for Makerspace production environments"

Create a virtual environment.

```
python -m venv .venv

```

Load the virtual environment

```
source .venv/bin/activate
```

Install the package into the environment.

```
pip install -e .
```

Make the `out` directory to store the results

```
mkdir out
```

Examples of running the model are in the `expts` folder

```
python expts/getting_started.py
```