import os
import random
import re

import openai
from termcolor import colored


NAMES = ["Axel", "Roxana", "Alexi", "Fulvio", "Patrik", "Scott", "Magnus", "Jon"]
ROLES = ["The Fool", "The Gangster", "The Detective"]
ROUNDS = 2
INTRO = """
You are a highly profficent and well versed player of social deduction games. You will now be pitted against a few formiddable oponents to battle for the glory of ultumate champion. 

We will play a game of simplified mafia where you will play together with two other players. Each of you will be randomly assigned a role and a name. The three roles are:
The fool: the fool wants  the good team to win but has no clue about what is going on in the town, only that he is good and that he wants good to prevail. The fool wins if the gangster is voted out
The gangster: the gangster wants to see the town crumble into chaos and is ready to kill to do so, only the detective can stand in his way. The gangster wins if the detective is voted out
The detective: The detective has been deep under cover for many years and has the town all figured out. The  detective knows who the gangster is; he now only has to convince the town of this so that the gangster can get voted out. The detective wins if the gangster is voted out.

The game works in three phases: 
First during the night the roles and names will be assigned to each of the players. Roles are secret but the names of the players will be known.
Secondly during the day there will be time to discuss your knowledge of the town and your suspicions against each other. This will take place during 3 rounds in which you will be allowed to state your case to the rest of the town and address any allegations made against you.
Finally during the night you will vote on which other player you want excommunicated from the town. Voting takes place in secret and only the result gets known.
At the end of the game the good team (Detective and Fool) win if they manage to vote out the gangster and the bad team (gangster) wins if he manages to vote out the detective.

All messages will be prefaced with the name of the player sending the message which will look like this: [ name ] message. These tags will be automatically added to messages and any usage of [] in your own text is prohibitetd and will be stripped out.

Night is now setting over the town so let’s get started!
"""

COLOR_FROM_ROLE = {"The Fool": "green", "The Gangster": "red", "The Detective": "blue"}

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.organization = "org-ClLAnF8IUOe9LazYsaP3aN3q"


def make_intro(name, role, players):
    intro = [("", INTRO)]
    intro += [
        (
            "",
            f"You are {name} and you are {role}. You are playing with {', '.join(n for n, _ in players if n != name)}.",
        )
    ]
    if role == "The Detective":
        intro += [
            (
                "",
                f"As the detective you know that {players[1][0]} is the gangster.",
            )
        ]
    return intro


def make_prompt(name, role):
    return [("", f"As {name} the {role} what do you want to say?")]


def make_message(name, message, player):
    if player == "":
        return {"role": "system", "content": f"{message}"}
    if name == player:
        return {"role": "assistant", "content": f"{message}"}
    return {"role": "user", "content": f"[{ player }] {message}"}


def query(name, role, players, townsquare):
    intro = make_intro(name, role, players)
    prompt = make_prompt(name, role)
    messages = [
        make_message(name, message, player)
        for player, message in intro + townsquare + prompt
    ]
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    return re.sub("\[[^\]]*\]", "", response.choices[0]["message"]["content"])


def format_title(name, role):
    return colored(f"[ {name} ({role}) ]", COLOR_FROM_ROLE[role])


def main():
    players = list(zip(random.sample(NAMES, len(ROLES)), ROLES))
    print(players)

    townsquare = []
    for round in range(ROUNDS):
        townsquare.append(
            (
                "",
                f"Round {round + 1} of {ROUNDS} is starting, after the final round you will have to vote someone out so make sure to gather enough information.",
            )
        )
        print(colored(f"Round {round + 1} of {ROUNDS}", "dark_grey"))
        for name, role in random.sample(players, len(players)):
            message = query(name, role, players, townsquare)
            print(format_title(name, role), message)
            townsquare.append((name, message))

    townsquare += [
        (
            "",
            f"The final round is over, time to vote! Answer only with the name of the person you want to vote out: {', '.join(n for n, _ in players)}",
        )
    ]
    print(colored(f"Voting time", "dark_grey"))
    for name, role in players:
        message = query(name, role, players, townsquare)
        print(format_title(name, role), message)


if __name__ == "__main__":
    main()
