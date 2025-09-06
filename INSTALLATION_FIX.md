Hello. I am truly sorry that you are still facing this installation issue. I have been investigating further, and I am now confident that the root cause of the problem is the Python version you are using (3.13). It is a very new version, and it is common for complex packages like `matplotlib` to not have stable, pre-built versions (wheels) ready for it on macOS. This forces your system to try and build it from source, which is failing.

**This is my final and strongest recommendation to fix this issue.** We need to switch to a more established and stable version of Python for this project. The best way to do this on a Mac is with a tool called `pyenv`, which lets you have multiple versions of Python installed at the same time.

Please follow these steps carefully. This is a complete, fresh start for the environment.

### Step 1: Install `pyenv`

If you don't have `pyenv` installed, you can install it easily with Homebrew:
```bash
brew install pyenv
```
After it installs, you may need to add a line to your shell configuration file (like `~/.zshrc`, `~/.bash_profile`, or `~/.bashrc`) to initialize `pyenv`. The installer will give you the exact command, but it usually looks like this:
```bash
# Add this to the end of your ~/.zshrc or ~/.bash_profile
eval "$(pyenv init -)"
```
After adding it, **restart your terminal**.

### Step 2: Install Python 3.11

Now, use `pyenv` to install Python 3.11. This may take a few minutes as it will build Python from source.
```bash
pyenv install 3.11
```

### Step 3: Set the Python Version for Your Project

Navigate into your project directory in the terminal. Once you are inside the `aoi-app` directory, run this command:
```bash
pyenv local 3.11
```
This command creates a `.python-version` file in your directory, telling `pyenv` to always use Python 3.11 for this project.

### Step 4: Create a New Virtual Environment

Since we've changed the Python version, we need a new virtual environment. If you have an old `venv` directory, you can remove it first (`rm -rf venv`).
```bash
# Make sure you are using the pyenv-managed Python
# The command `which python` should point to the pyenv shims.

# Create the new virtual environment
python -m venv venv
```

### Step 5: Activate and Install Requirements

Finally, activate the new virtual environment and install the requirements. With Python 3.11, there should be pre-built wheels available, and the installation should be smooth.
```bash
# Activate the new environment
source venv/bin/activate

# Install the packages
pip install -r requirements.txt
```

If all these steps complete successfully, you will have a stable environment for this project. You can then run the app as before with `streamlit run app.py`.

Thank you for your immense patience. I am confident this will resolve the issue.
