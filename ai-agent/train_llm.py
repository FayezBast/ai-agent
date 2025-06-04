from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer, DataCollatorForLanguageModeling
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, TaskType
import torch


dataset = load_dataset("json", data_files="commands.jsonl")["train"]


model_name = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)


def tokenize(sample):
    prompt = f"User: {sample['instruction']}\nAssistant: {sample['response']}"
    result = tokenizer(prompt, truncation=True, padding="max_length", max_length=256)
    result["labels"] = result["input_ids"].copy()
    return result

tokenized = dataset.map(tokenize)


lora = LoraConfig(
    r=8, lora_alpha=16, lora_dropout=0.05, bias="none",
    task_type=TaskType.CAUSAL_LM,
    target_modules=["q_proj", "v_proj"]
)
model = get_peft_model(model, lora)

# Training settings
args = TrainingArguments(
    output_dir="./trained-voice-llm",
    per_device_train_batch_size=4,
    num_train_epochs=3,
    learning_rate=2e-4,
    logging_steps=10,
    fp16=True,
    save_strategy="epoch"
)

trainer = Trainer(
    model=model,
    args=args,
    train_dataset=tokenized,
    tokenizer=tokenizer,
    data_collator=DataCollatorForLanguageModeling(tokenizer, mlm=False),
)

trainer.train()

# Save your model
model.save_pretrained("trained-voice-llm")
tokenizer.save_pretrained("trained-voice-llm")
