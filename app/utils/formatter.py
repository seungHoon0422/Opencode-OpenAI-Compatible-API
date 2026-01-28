import json
from datetime import datetime

def format_openai_stream_chunk(chunk, model_name):
    """LiteLLM 청크를 OpenAI 호환 포맷으로 변환"""
    chunk_data = {
        "id": getattr(chunk, 'id', f"chatcmpl-{hash(str(chunk))}"),
        "object": "chat.completion.chunk",
        "created": getattr(chunk, 'created', int(datetime.now().timestamp())),
        "model": model_name,
        "choices": []
    }
    
    if chunk.choices:
        choice = chunk.choices[0]
        choice_data = {
            "index": 0,
            "delta": {},
            "finish_reason": getattr(choice, 'finish_reason', None)
        }
        
        if hasattr(choice, 'delta'):
            delta = choice.delta
            if hasattr(delta, 'role') and delta.role:
                choice_data["delta"]["role"] = delta.role
            if hasattr(delta, 'content') and delta.content:
                choice_data["delta"]["content"] = delta.content
            if hasattr(delta, 'tool_calls') and delta.tool_calls:
                choice_data["delta"]["tool_calls"] = [
                    {
                        "index": getattr(tc, 'index', 0),
                        "id": getattr(tc, 'id', None),
                        "type": getattr(tc, 'type', "function"),
                        "function": {
                            "name": getattr(tc.function, 'name', None),
                            "arguments": getattr(tc.function, 'arguments', None)
                        }
                    } for tc in delta.tool_calls
                ]
        
        chunk_data["choices"].append(choice_data)
    return f"data: {json.dumps(chunk_data)}\n\n"
