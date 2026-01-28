def resolve_model(model_name, mapping):
    """입력된 모델 이름을 실제 호출할 모델 경로로 변환"""
    mapped_model = mapping.get(model_name, mapping.get("default"))
    
    # LiteLLM용 OpenAI 호환 포맷으로 변환
    if mapped_model.startswith("gemini/"):
        return mapped_model.replace("gemini/", "openai/")
    return f"openai/{mapped_model}"
