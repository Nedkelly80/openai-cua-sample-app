from agent import Agent
from computers.config import *
from computers.default import *
from computers import computers_config

# Use the computers_config to get the ScrapybaraBrowser class
ComputerClass = computers_config["scrapybara-browser"]
with ComputerClass() as computer:
    agent = Agent(computer=computer)
    input_items = [{"role": "user", "content": "what is the weather in sf"}]
    response_items = agent.run_full_turn(input_items, debug=True, show_images=True)
    print(response_items[-1]["content"][0]["text"])
