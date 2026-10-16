from langchain_ollama import ChatOllama

def create_model(model:str , temp:float) -> ChatOllama:
    return ChatOllama(
        model = model,
        temperature = temp
    )