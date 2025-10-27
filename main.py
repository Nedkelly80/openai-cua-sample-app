from agent.agent import Agent
from computers.config import *
from computers.default import *
from computers import computers_config


def main(user_input=None):
    # Use the computers_config to get the LocalPlaywrightBrowser class
    ComputerClass = computers_config["local-playwright"]
    with ComputerClass() as computer:
        agent = Agent(computer=computer)
        items = []
        while True:
            user_input = input("> ")
            items.append({"role": "user", "content": user_input})
            output_items = agent.run_full_turn(items, debug=True, show_images=True)
            items += output_items


if __name__ == "__main__":
    main()
