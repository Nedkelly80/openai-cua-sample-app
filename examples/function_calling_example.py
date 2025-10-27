from agent import Agent
from computers.config import *
from computers.default import *
from computers import computers_config

tools = [
    {
        "type": "function",
        "name": "get_weather",
        "description": "Determine weather in my location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["c", "f"]},
            },
            "additionalProperties": False,
            "required": ["location", "unit"],
        },
    }
]


def main():
    # Use the computers_config to get the ScrapybaraBrowser class
    ComputerClass = computers_config["scrapybara-browser"]
    with ComputerClass() as computer:
        agent = Agent(tools=tools, computer=computer)
        items = []
        while True:
            user_input = input("> ")
            items.append({"role": "user", "content": user_input})
            output_items = agent.run_full_turn(items)
            items += output_items


if __name__ == "__main__":
    main()
