import lmstudio as lms
from openai import OpenAI
from pydantic import BaseModel
import json

response_schema = {
    "type": "object",
    "properties": {
        "meaning": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 10,
            "maxItems": 10
        }
    },
    "required": ["meaning"],
    "additionalProperties": False
}

class MeaningOfLife(BaseModel):
    meaning: list[str]


def using_openai(model_name):
    client = OpenAI(base_url="http://localhost:1234/v1", api_key="lmstudio")  # Adjust port if needed

    # using json schema
    # response = client.chat.completions.create(
    #     model=model_name,  
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": "What is the meaning of life your answer is a list of 10 meaning."}
    #     ],
    #     temperature=0.7,
    #     max_tokens=500,
    #     response_format = response_schema
    # )

    # using pydantic base model
    response = client.chat.completions.parse(
        model=model_name,  
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the meaning of life your answer is a list of 10 meaning."}
        ],
        temperature=0.7,
        max_tokens=500,
        response_format = MeaningOfLife
    )

    return response


def using_lms(model_name):
    model = lms.llm(model_name, config={"temperature":0.5})  

    # using json schema
    result = model.respond("""Return exactly 10 short meanings of life as JSON per the schema.
                              Output only JSON, no markdown fences, no prose."""
                           , response_format=response_schema)
    # using pydantic model
    # result = model.respond("""Return exactly 10 short meanings of life as JSON per the schema.
    #                           Output only JSON, no markdown fences, no prose."""
    #                        ,response_format=MeaningOfLife)
    return result


if __name__ == "__main__":
    model = "openai/gpt-oss-20b" # "google/gemma-3-12b" # "openai/gpt-oss-20b" 

    print(using_lms(model))

    print("-"*50)

    response = using_openai(model)
    print(response.choices[0].message.content)





