import asyncio
import json
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from browser_use import Agent, Browser, BrowserConfig
from pydantic import SecretStr

# Load environment variables
load_dotenv()
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
api_key = os.getenv("GEMINI_API_KEY")

# Initialize browser
browser = Browser(
    config=BrowserConfig(
        chrome_instance_path="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    )
)

# Initialize the model
llm = ChatGoogleGenerativeAI(model='gemini-2.0-flash-exp', api_key=SecretStr(api_key))

# Define agent
agent = Agent(
    task="""Navigate to linkedin.com, collect the first 5 profiles from my connections, extract name and profile_url, 
            and export results as JSON""",
    llm=llm,
    browser=browser
)


async def main():
    history = await agent.run()  # Run the agent and store history

    # Extract the final result
    extracted_data = history.final_result()

    # Save the result as a JSON file
    json_file_path = "linkedin_connections.json"
    with open(json_file_path, "w", encoding="utf-8") as json_file:
        json.dump(extracted_data, json_file, indent=4)

    print(f"Extracted data saved to {json_file_path}")

    input('Press Enter to close the browser...')
    await browser.close()

if __name__ == '__main__':
    asyncio.run(main())
