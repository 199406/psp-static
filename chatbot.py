from openai import OpenAI
import pinecone
import json
from tenacity import retry, wait_random_exponential, stop_after_attempt
from translate import gel_to_eng, eng_to_gel

from dotenv import load_dotenv
import os

# Load variables from the .env file into the environment
load_dotenv()

# Now you can access the variables using os.getenv()
pinecone_api_key = os.getenv("PINECONE_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

# Constants
GPT_MODEL = "gpt-3.5-turbo-0613"
INDEX_NAME = "psp-static-flow"


# Initialize OpenAI client
client = OpenAI(api_key=openai_api_key)

# Connect to Pinecone index
index = pinecone.Index(
    name=INDEX_NAME,
    host="https://psp-static-flow-s2jdw02.svc.aped-4627-b74a.pinecone.io",
    api_key=pinecone_api_key
)


@retry(wait=wait_random_exponential(multiplier=1, max=40), stop=stop_after_attempt(3))
def chat_completion_request(messages, functions, model=GPT_MODEL):
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            functions=functions,
            function_call='auto'
        )
        return response
    except Exception as e:
        print("Unable to generate ChatCompletion response")
        print(f"Exception: {e}")
        return e


def get_user_embeddings(query):
    response = client.embeddings.create(
        input=[query],
        model="text-embedding-ada-002",
    )
    return response.data[0].embedding


# Function to search Pinecone index
def get_answer(query_embd, top_k=2):
    similar_products = index.query(vector=query_embd, top_k=top_k, include_metadata=True)
    return similar_products["matches"]


available_functions = {
    "get_answer": get_answer
}

categories = ['raffle','breakdown of medications','purchase of medicine with insurance or referral number','price of unit medicine'
              'loyalty card', 'insurance','conversion of smiles into Lari','printed statement',
              'shipping price','delivery times','city to city shipping',
              'courier payment','combining two orders',
              'courier payment on returned order','voucher','payment methods','cash_payment','password recovery',
              'registration/authorization','order implementation','withdrawal service from the pharmacy','purchase with insurance/referral',
              'change of personal data','pomo code/all other questions regarding promo code'
              'amex','plus card','liberty social','discount periods','current discounts','future discounts','vacancies','promo code']

functions = [
    {
        "name": "get_answer",
        "description": f"User will ask questions about predefined categories. categories include :{categories},"
                       f"extract these categories. This will be later used to search"
                       f"in Pinecone for answers",
        "parameters": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "The category user asking question about",
                }
            },
            "required": ["category"],
        },
    }
]


def execute_function_call(function_name, arguments):
    function = available_functions.get(function_name, None)
    if function:
        arguments = json.loads(arguments)
        query = arguments["category"]
        query_embd = get_user_embeddings(query)
        results = function(query_embd)
    else:
        results = f"Error: function {function_name} does not exist"
    return results


def main():
    messages = [
        {"role": "system", "content": "You are a helpful assistant. You need to answer questions about"
                                      "some predefined categories. Answer customer questions only with the information you are provided "
                                      "from the database. If you don't have any answer return {NONE}"}
    ]

    while True:
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting the chatbot...")
            break

        georgian_to_english = gel_to_eng(user_input)
        # Add the user's input to the messages list
        messages.append({"role": "user", "content": georgian_to_english})

        # Initial chat completion request
        response = chat_completion_request(messages, functions=functions)
        print(response)

        if response.choices[0].message.function_call:
            function_name = response.choices[0].message.function_call.name
            arguments = response.choices[0].message.function_call.arguments

            function_response = execute_function_call(function_name, arguments)
            print(function_response)
            # Append the function response to the messages list
            messages.append({"role": "function", 'name': "get_answer", "content": str(function_response)})

            response = chat_completion_request(messages, functions)
            english_to_georgian = eng_to_gel(response.choices[0].message.content)
            print(english_to_georgian)
        else:
            english_to_georgian = eng_to_gel(response.choices[0].message.content)
            print(english_to_georgian)


if __name__ == "__main__":
    main()
