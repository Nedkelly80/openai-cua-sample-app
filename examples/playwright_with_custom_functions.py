from agent.agent import Agent
from computers.config import *
from computers.default import *
from computers import computers_config

tools = [
    {
        "type": "function",
        "name": "back",
        "description": "Go back to the previous page.",
        "parameters": {},
    },
    {
        "type": "function",
        "name": "goto",
        "description": "Go to a specific URL.",
        "parameters": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Fully qualified URL to navigate to.",
                },
            },
            "additionalProperties": False,
            "required": ["url"],
        },
    },
]


def main():
    # Use the computers_config to get the LocalPlaywrightBrowser class
    ComputerClass = computers_config["local-playwright"]
    with ComputerClass() as computer:
        agent = Agent(computer=computer, tools=tools)
        items = [
            {
                "role": "developer",
                "content": "Use the additional back() and goto() functions to navigate the browser. If you see nothing, try going to bing.com.",
            }
        ]
        while True:
            user_input = input("> ")
            items.append({"role": "user", "content": user_input})
            output_items = agent.run_full_turn(items, show_images=False)
            items += output_items


if __name__ == "__main__":
    main()
