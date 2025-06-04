from peft import PeftConfig

adapter_path = r"C:\Users\HCES\Documents\speech\trained-voice-llm"
config = PeftConfig.from_pretrained(adapter_path)
print("Base model needed:", config.base_model_name_or_path)
