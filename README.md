[![Python Version][python-image]][python-url]
[![PyTest Status][pytest-image]][pytest-url]
[![Star][star-image]][star-url]


______________________________________________________________________

# 🧊 CUBE: Dynamic Simulations in Customized Unity3D-Based Environments with Large Language Model-Based Multi-Agent Systems

## 📝 Overview

<p align="center">
  <img src='assets/intro.png' width=1000>
</p>
🧊 CUBE can assist LLM-powered agents in simulating human daily activities and social interactions within customized Unity3D environments. This could potentially be beneficial in evaluating architectural designs and multi-agent simulation management games. CUBE is an environment built on the foundation of [OASIS](https://github.com/camel-ai/oasis), and its agents are derived from [CAMEL](https://github.com/camel-ai/camel).

### Workflow

1️⃣ *Initialization Phase:* This phase involves the design and modeling of the environment, which is then imported into Unity3D for navigation mesh setup, and character models are imported as navigation agents. Room coordinates are configured in Python, and each agent's occupation, age, description, and other information are initialized in a JSON file.

2️⃣ *Experimentation Phase:* The virtual experiment begins at a specified time, with real-world time linearly mapped to the virtual-world  time. Each agent, based on a large model, decides its actions according to its profile, generated daily plan, and the simulated time. Social interactions are triggered when agents encounter each other.

3️⃣ *Evaluation Phase:* All data from the experiment are logged, and after multiple simulations, designers analyze the activities of the agents, such as comparing the impact of different environments and occupations on the degree of social participation of the agents.

### 🎬 Demo Video


### 🔧 Installation

### Step 1: Clone the Repository

```bash
git clone https://github.com/camel-ai/oasis.git

cd oasis
```

### Step 2: Create and Activate a Virtual Environment

Please choose one of the following methods to set up your environment. You only need to follow one of these methods.

- Option 1: Using Conda (Linux & macOS & windows)

```bash
conda create --name oasis python=3.10
conda activate oasis
```

- Option 2: Using venv (Linux & macOS)

```bash
python -m venv oasis-venv
source oasis-venv/bin/activate
```

- Option 3: Using venv (Windows)

```bash
python -m venv oasis-venv
oasis-venv\Scripts\activate
```

### Step 3: Install Necessary Packages

```bash
pip install --upgrade pip setuptools

pip install -e .  # This will install dependencies as specified in pyproject.toml
```

## 🏃Quickstart

### Step 1: Set Up Environment Variables

First, you need to add your OpenAI API key to the system's environment variables. You can obtain your OpenAI API key from [here](https://platform.openai.com/api-keys). Note that the method for doing this will vary depending on your operating system and the shell you are using.

- For Bash shell (Linux, macOS, Git Bash on Windows):\*\*

```bash
# Export your OpenAI API key
export OPENAI_API_KEY=<insert your OpenAI API key>
export OPENAI_API_BASE_URL=<insert your OpenAI API BASE URL>  #(Should you utilize an OpenAI proxy service, kindly specify this)
```

- For Windows Command Prompt:\*\*

```cmd
REM export your OpenAI API key
set OPENAI_API_KEY=<insert your OpenAI API key>
set OPENAI_API_BASE_URL=<insert your OpenAI API BASE URL>  #(Should you utilize an OpenAI proxy service, kindly specify this)
```

- For Windows PowerShell:\*\*

```powershell
# Export your OpenAI API key
$env:OPENAI_API_KEY="<insert your OpenAI API key>"
$env:OPENAI_API_BASE_URL="<insert your OpenAI API BASE URL>"  #(Should you utilize an OpenAI proxy service, kindly specify this)
```

Replace `<insert your OpenAI API key>` with your actual OpenAI API key in each case. Make sure there are no spaces around the `=` sign.

### Step 2: Modify the Configuration File (Optional)

If adjustments to the settings are necessary, you can specify the parameters in the `scripts/reddit_gpt_example/gpt_example.yaml` file. Explanations for each parameter are provided in the comments within the YAML file.

To import your own user and post data, please refer to the JSON file format located in the `/data/reddit/` directory of this repository. Then, update the `user_path` and `pair_path` in the YAML file to point to your data files.

### Step 3: Run the Main Program

```bash
# For Reddit
python scripts/reddit_gpt_example/reddit_simulation_gpt.py --config_path scripts/reddit_gpt_example/gpt_example.yaml

# For Twitter
python scripts/twitter_gpt_example/twitter_simulation_large.py --config_path scripts/twitter_gpt_example/gpt_example.yaml
```

Note: without modifying the Configuration File, running the reddit script requires approximately 14 API requests to call gpt-4, and the cost incurred is minimal. (October 29, 2024)

## 🔗 Paper

To be supplemented after the release on arXiv.

## 💡Tips

### For Twitter Simluation:

- Customizing temporal feature

When simulating on generated users, you can customizing temporal feature in `social_simulation/social_agent/agents_generator.py` by modifying `profile['other_info']['active_threshold']`. For example, you can set it to all 1 if you believe that the generated users should be active the entire time.

### For Reddit Simluation:

- Reddit recommendation system

The Reddit recommendation system is highly time-sensitive. Currently, one time step in the `reddit_simulation_xxx.py`simulates approximately two hours in the agent world, so essentially, new posts are recommended at every time step. To ensure that all posts made by controllable users can be seen by other agents, it is recommended that `the number of agents` × `activate_prob` > `max_rec_post_len` > `round_post_num`.

## 📢 News

<!-- - Public release of our dataset on Hugging Face (November 05, 2024) -->

- Initial release of CUBE github repository (November 23, 2024)


## 🔒 Limitation

We would like to thank Douglas for designing the logo of our project.

## 🗝️ Contributing to 🧊CUBE

We greatly appreciate your interest in contributing to our open-source initiative. To ensure a smooth collaboration and the success of contributions, we adhere to a set of contributing guidelines similar to those established by CAMEL. For a comprehensive understanding of the steps involved in contributing to our project, please refer to the CAMEL contributing guidelines [here](https://github.com/camel-ai/camel/blob/master/CONTRIBUTING.md). 🤝🚀
<p align="center">
  <img src='assets/communication.png' width=600>
</p>
An essential part of contributing involves not only submitting new features with accompanying tests (and, ideally, examples) but also ensuring that these contributions pass our automated pytest suite. This approach helps us maintain the project's quality and reliability by verifying compatibility and functionality.

## 🎉 Acknowledgment

Thanks to 🍓StrawberryKiller for the dedicated effort in illustrating the workflow diagram and meticulously decorating the scene in Unity3D.

[pytest-image]: https://github.com/camel-ai/camel/actions/workflows/pytest_package.yml/badge.svg
[pytest-url]: https://github.com/camel-ai/social-simulation/actions/workflows/pytest_package.yml
[python-image]: https://img.shields.io/badge/Python-3.10%2B-brightgreen.svg
[python-url]: https://docs.python.org/3.10/
[star-image]: https://img.shields.io/github/stars/yiyiyi0817/cube?label=stars&logo=github&color=brightgreen
[star-url]: https://github.com/yiyiyi0817/cube/stargazers
