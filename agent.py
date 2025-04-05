import asyncio
import json
import os
import re
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
    browser=browser,
    save_conversation_path="logs/conversation"
)

async def main():
    history = await agent.run()
    try:
        # Direct extraction from controller output
        extracted = history.extracted_content()
        if extracted:
            # Clean markdown and parse last valid JSON
            for entry in reversed(extracted):
                clean_entry = re.sub(r'^```json\n|\n```$', '', entry).strip()
                try:
                    data = json.loads(clean_entry)
                    if isinstance(data, list):
                        with open("linkedin_connections.json", "w") as f:
                            json.dump(data[:5], f, indent=2)
                        print("Saved from extracted content!")
                        return
                except json.JSONDecodeError:
                    continue

        # Parse final result
        result_text = history.final_result()
        if result_text:
            # Extract JSON array and fix escaped quotes
            json_str = result_text.split(":\n")[-1].replace('\\"', '"')
            try:
                data = json.loads(json_str)
                with open("linkedin_connections.json", "w") as f:
                    json.dump(data, f, indent=2)
                print("Saved from final result!")
                return
            except json.JSONDecodeError:
                pass

        print("No valid JSON found in history")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        await browser.close()
        
if __name__ == '__main__':
    asyncio.run(main())
