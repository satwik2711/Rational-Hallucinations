from openai import OpenAI


# Load the environment variables

client = OpenAI(api_key="-")

MODEL_NAME = "gpt-4o"

def generate_response(system_prompt, user_prompt, model_name="gpt-4o", n=1, max_output_tokens=4096, temperature=1, top_p=0.95):
    completion = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        n=n,
        max_tokens=max_output_tokens,
        temperature=temperature,
        top_p=top_p
    )

    return [choice.message.content for choice in completion.choices]
