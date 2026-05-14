import ollama

def research_topics(niche):

    prompt = f"""
            You are a professional YouTube strategist.
            Generate 10 high-CTR YouTube video ideas for the niche: {niche}

            Requirements:
            - optimized for shorts
            - emotionally engaging
            - modern trends
            - high click potential
            - beginner audience

                 Also include:
                 - estimated virality score out of 10
            """
    response = ollama.chat(
        model='llama3',
        messages=[
            {
                'role': 'user',
                'content': prompt
            }
        ]
    )

    return response['message']['content']