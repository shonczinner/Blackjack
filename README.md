# Blackjack

This project contains files concerning the game Blackjack. BasicStrategyTrainer.py will show you some cards and a dealer's cardand ask you which action you should take according to the computed strategy. BlackjackAnalysis.py computes the strategy regarding hitting, standing, doubling down, and splitting as well as the expected value and variance of Blackjack assuming an infinite deck (drawing with replacement). BlackjackGame.py allows you to play Blackjack in the console. CardCountingTrainer.py shows some cards to you and asks you what the count would be. ComputeEffectOfRemoval.py computes the expected value of Blackjack with 1 card of 52 removed and is used to derive card counting.

Computed strategies might vary from other sources (for example due to simpifying the game by drawing cards with replacement or variations in game rules) but in these cases, the expected value differences would be small regardless.

https://sczinner.shinyapps.io/BlackjackTrainer/ is a similar implementation of the game and training apps above in R with a GUI.

The computed strategies will be in the following format,

![Split matrix shown here.](https://raw.githubusercontent.com/shonczinner/Blackjack/main/images/split_matrix.JPG)

The column names are the dealers shown hand. The row names are players hand. The hand format is the player's score counting all aces as 1, and then 0 if your hand contains an ace which could count as 11. Values of 'TRUE' mean the player should split if possible for the corresponding hand. 

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/shonczinner/Blackjack.git
    ```
2. Navigate to the project directory:
    ```bash
    cd Blackjack
    ```
3. (Optional) Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
4. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

```bash
python BlackjackGame.py
```
Or replace 'BlackjackGame.py' with the desired scripts. Necessary files (strategies and effect of removals) will be generated for the strategy and card counting scripts if necessary. 
