from flask import Blueprint, request, jsonify, Response, current_app
from litellm import completion
from ..utils.model_resolver import resolve_model
from ..utils.formatter import format_openai_stream_chunk
import logging
import json
import os

chat_bp = Blueprint('chat', __name__)
logger = logging.getLogger(__name__)

@chat_bp.route("/chat/completions", methods=["POST"])
@chat_bp.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    print("\n" + "="*80, flush=True)
    print("🚀 ENDPOINT CALLED: /chat/completions", flush=True)
    print("="*80, flush=True)
    
    data = request.get_json()
    
    # 📥 Request Body 요약 출력
    def truncate_long_strings(obj, max_length=100):
        """긴 문자열을 잘라서 요약"""
        if isinstance(obj, dict):
            return {k: truncate_long_strings(v, max_length) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [truncate_long_strings(item, max_length) for item in obj]
        elif isinstance(obj, str) and len(obj) > max_length:
            return obj[:max_length] + f"... (총 {len(obj)}자)"
        return obj
    
    print("\n📥 REQUEST BODY (요약):", flush=True)
    summarized_data = data.copy()
    
    # Tools는 첫 번째만 전체 표시, 나머지는 name만
    if 'tools' in summarized_data and isinstance(summarized_data['tools'], list):
        tools = summarized_data['tools']
        if len(tools) > 0:
            summarized_tools = [tools[0]]  # 첫 번째 tool 전체
            for tool in tools[1:]:
                tool_name = tool.get('function', {}).get('name', 'unknown')
                summarized_tools.append({'type': 'function', 'function': {'name': tool_name}})
            summarized_data['tools'] = summarized_tools
    
    # 나머지 긴 문자열 truncate
    summarized_data = truncate_long_strings(summarized_data, max_length=100)
    
    print(json.dumps(summarized_data, indent=2, ensure_ascii=False), flush=True)
    
    # Tools 요약 정보
    if 'tools' in data and isinstance(data['tools'], list):
        print(f"\n🔧 Tools: {len(data['tools'])} tools (첫 번째만 전체 표시, 나머지는 name만)", flush=True)
        for i, tool in enumerate(data['tools']):
            tool_name = tool.get('function', {}).get('name', 'unknown')
            if i == 0:
                print(f"  [0] {tool_name} (전체 표시됨)", flush=True)
            else:
                print(f"  [{i}] {tool_name}", flush=True)
    
    print("=" * 80 + "\n", flush=True)
    
    if not data or "messages" not in data:
        print("❌ Invalid request - missing messages", flush=True)
        return jsonify({"error": {"message": "Invalid request", "type": "invalid_request_error"}}), 400

    # 1. 파라미터 추출 및 모델 매핑
    user_model = data.get("model", "default")
    target_model = resolve_model(user_model, current_app.config['MODEL_MAPPING'])
    
    litellm_params = {
        "model": target_model,
        "messages": data.get("messages", []),
        "temperature": data.get("temperature", 0.7),
        "max_tokens": data.get("max_tokens", 1000),
        "api_key": current_app.config['GEMINI_API_KEY'],
        "api_base": current_app.config['GEMINI_API_BASE'],
        "stream": data.get("stream", False),
        "custom_llm_provider": "openai"
    }

    # Tool 설정 추가
    if "tools" in data:
        litellm_params["tools"] = data["tools"]
        litellm_params["tool_choice"] = data.get("tool_choice", "auto")
    
    # 📝 LiteLLM Params (요약)
    print("=" * 80, flush=True)
    print("🔵 LITELLM PARAMS (요약):", flush=True)
    print("=" * 80, flush=True)
    
    # API 키 마스킹 + 긴 내용 truncate
    debug_params = truncate_long_strings(litellm_params.copy(), max_length=100)
    debug_params['api_key'] = f"{litellm_params['api_key'][:10]}...{litellm_params['api_key'][-4:]}"
    print(json.dumps(debug_params, indent=2, ensure_ascii=False), flush=True)
    
    # 실제 사용되는 전체 API 키
    print(f"\n🔑 FULL API KEY: {litellm_params['api_key']}", flush=True)
    print(f"🔑 API KEY from env: {os.getenv('GEMINI_API_KEY')}", flush=True)
    print(f"🔑 API KEY from config: {current_app.config['GEMINI_API_KEY']}", flush=True)
    print("=" * 80 + "\n", flush=True)

    try:
        # 2. 모델 호출
        if litellm_params["stream"]:
            def generate():
                try:
                    print("\n🔵 Starting streaming response...", flush=True)
                    response_stream = completion(**litellm_params)
                    chunk_count = 0
                    
                    for chunk in response_stream:
                        chunk_count += 1
                        
                        # 🔍 각 청크를 JSON 형식으로 출력
                        print(f"\n📦 Chunk #{chunk_count} (RAW):", flush=True)
                        
                        # chunk 객체를 dict로 변환 (가능한 모든 속성)
                        chunk_dict = {}
                        if hasattr(chunk, 'id'):
                            chunk_dict['id'] = chunk.id
                        if hasattr(chunk, 'model'):
                            chunk_dict['model'] = chunk.model
                        if hasattr(chunk, 'created'):
                            chunk_dict['created'] = chunk.created
                        if hasattr(chunk, 'object'):
                            chunk_dict['object'] = chunk.object
                        
                        if hasattr(chunk, 'choices') and chunk.choices:
                            chunk_dict['choices'] = []
                            for choice in chunk.choices:
                                choice_dict = {
                                    'index': getattr(choice, 'index', 0),
                                    'finish_reason': getattr(choice, 'finish_reason', None)
                                }
                                
                                if hasattr(choice, 'delta'):
                                    delta = choice.delta
                                    delta_dict = {}
                                    if hasattr(delta, 'role') and delta.role:
                                        delta_dict['role'] = delta.role
                                    if hasattr(delta, 'content') and delta.content is not None:
                                        delta_dict['content'] = delta.content
                                    if hasattr(delta, 'tool_calls') and delta.tool_calls:
                                        delta_dict['tool_calls'] = [
                                            {
                                                'index': getattr(tc, 'index', 0),
                                                'id': getattr(tc, 'id', None),
                                                'type': getattr(tc, 'type', 'function'),
                                                'function': {
                                                    'name': getattr(tc.function, 'name', None) if hasattr(tc, 'function') else None,
                                                    'arguments': getattr(tc.function, 'arguments', None) if hasattr(tc, 'function') else None
                                                }
                                            } for tc in delta.tool_calls
                                        ]
                                    choice_dict['delta'] = delta_dict
                                
                                chunk_dict['choices'].append(choice_dict)
                        
                        print(json.dumps(chunk_dict, indent=2, ensure_ascii=False), flush=True)
                        
                        # Formatted chunk도 출력
                        formatted_chunk = format_openai_stream_chunk(chunk, user_model)
                        print(f"\n📤 Formatted Chunk #{chunk_count}:", flush=True)
                        print(formatted_chunk.strip(), flush=True)
                        
                        yield formatted_chunk
                    
                    yield "data: [DONE]\n\n"
                    print(f"\n✅ Streaming completed: {chunk_count} total chunks\n", flush=True)
                    
                except Exception as e:
                    import traceback
                    error_msg = f"❌ Stream error: {str(e)}\n{traceback.format_exc()}"
                    print(error_msg, flush=True)
                    logger.error(error_msg)
                    yield f"data: {json.dumps({'error': str(e)})}\n\n"
            
            return Response(generate(), mimetype='text/event-stream')
        
        else:
            # 3. 비스트리밍 응답
            print("\n🔵 Calling LiteLLM (non-streaming)...", flush=True)
            response = completion(**litellm_params)
            
            # 📤 LiteLLM Response (JSON 형식 그대로)
            print("\n" + "=" * 80, flush=True)
            print("🟢 LITELLM RESPONSE (RAW JSON):", flush=True)
            print("=" * 80, flush=True)
            
            # Response 객체를 dict로 변환
            response_dict = {
                'id': response.id,
                'object': getattr(response, 'object', 'chat.completion'),
                'created': response.created,
                'model': response.model,
                'choices': []
            }
            
            for choice in response.choices:
                choice_dict = {
                    'index': choice.index,
                    'finish_reason': choice.finish_reason,
                    'message': {
                        'role': choice.message.role,
                        'content': choice.message.content
                    }
                }
                
                if hasattr(choice.message, 'tool_calls') and choice.message.tool_calls:
                    choice_dict['message']['tool_calls'] = [
                        {
                            'id': getattr(tc, 'id', None),
                            'type': getattr(tc, 'type', 'function'),
                            'function': {
                                'name': getattr(tc.function, 'name', None) if hasattr(tc, 'function') else None,
                                'arguments': getattr(tc.function, 'arguments', None) if hasattr(tc, 'function') else None
                            }
                        } for tc in choice.message.tool_calls
                    ]
                
                response_dict['choices'].append(choice_dict)
            
            if hasattr(response, 'usage'):
                response_dict['usage'] = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens
                }
            
            print(json.dumps(response_dict, indent=2, ensure_ascii=False), flush=True)
            print("=" * 80 + "\n", flush=True)
            
            # 메시지 구성
            message = {
                "role": "assistant",
                "content": response.choices[0].message.content
            }
            
            # tool_calls 처리
            if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
                tool_calls = response.choices[0].message.tool_calls
                message["tool_calls"] = [
                    {
                        "id": getattr(tc, 'id', None),
                        "type": getattr(tc, 'type', "function"),
                        "function": {
                            "name": getattr(tc.function, 'name', None) if hasattr(tc, 'function') else None,
                            "arguments": getattr(tc.function, 'arguments', None) if hasattr(tc, 'function') else None
                        }
                    } for tc in tool_calls
                ]
            
            result = {
                "id": f"chatcmpl-{response.id}",
                "object": "chat.completion",
                "created": int(response.created),
                "model": user_model,
                "choices": [{
                    "index": 0,
                    "message": message,
                    "finish_reason": response.choices[0].finish_reason or "stop"
                }],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            }
            
            # 📤 최종 응답 (JSON 형식 그대로)
            print("\n" + "=" * 80, flush=True)
            print("📤 FINAL RESPONSE (JSON):", flush=True)
            print("=" * 80, flush=True)
            print(json.dumps(result, indent=2, ensure_ascii=False), flush=True)
            print("=" * 80 + "\n", flush=True)
            
            return jsonify(result)

    except Exception as e:
        import traceback
        error_msg = str(e)
        error_type = type(e).__name__
        
        print(f"\n❌ ERROR OCCURRED:", flush=True)
        print(f"Type: {error_type}", flush=True)
        print(f"Message: {error_msg}", flush=True)
        print(f"Traceback:\n{traceback.format_exc()}", flush=True)
        
        logger.error(f"API Error: {error_msg}")
        
        # OpenAI 표준 에러 형식
        return jsonify({
            "error": {
                "message": error_msg,
                "type": error_type.lower().replace("error", "_error"),
                "code": 429 if "RateLimitError" in error_type or "429" in error_msg else 500
            }
        }), 429 if "RateLimitError" in error_type or "429" in error_msg else 500
