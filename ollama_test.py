# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import ollama
def get_answer(context,model_name):
    completion = ollama.chat(
      model=model_name,
      messages=[
        {"role": "user", "content": context}
      ],
      stream=True
    )
    chunk_messages=[]
    for chunk in completion:
        chunk_message = chunk['message']['content']
        chunk_messages.append(chunk_message)
    full_reply_content = ''.join([m for m in chunk_messages])
    return full_reply_content