import os
import openai
import json

from textwrap import TextWrapper

s1 = '''
Juliet is a professor of Literature at a university and knows about many things. 
'''
s2 = '''
John is a university professor, but a real idiot who doesn't know much but likes \
to think he knows everything.
'''
s3 = '''
Write a short conversation between Juliet and John about Romance literature in which \
John really demonstrates how insufferable he is and Juliet tells him how stupid he is \
and everybody gets upset about it.
'''

if __name__ == "__main__":
    with open("keys.json", "r") as file:
        config = json.load(file)
    openai.organization = config["org"]
    openai.api_key = config["key"]

    a = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user", "content": s1,
                "role": "user", "content": s2,
                "role": "user", "content": s3
            },
        ]
    )

    conv = a["choices"][0]["message"]["content"]

    subsequent_indent = "".join([" "] * (len("Juliet:") + 1))
    tw = TextWrapper(width=80, subsequent_indent=subsequent_indent)
    for line in conv.split("\n"):
        print(tw.fill(line))