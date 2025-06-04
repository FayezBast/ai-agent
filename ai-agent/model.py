from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

# Global model and tokenizer instances
_model = None
_tokenizer = None
_device = "cuda" if torch.cuda.is_available() else "cpu"

def load_model(model_path):
    """
    Load the model and tokenizer from the specified path.
    
    Args:
        model_path (str): Path to the directory containing the model files
    """
    global _model, _tokenizer, _device
    
    print(f"Loading model from {model_path}...")
    try:
        _tokenizer = AutoTokenizer.from_pretrained(model_path)
        _model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16 if _device == "cuda" else torch.float32,
            low_cpu_mem_usage=True
        )
        _model.to(_device)
        print(f"Model loaded successfully on {_device}")
        return True
    except Exception as e:
        print(f"Error loading model: {e}")
        return False

def get_ai_response(user_input, max_length=100, temperature=0.7):
    """
    Generate a response from the model based on user input.
    
    Args:
        user_input (str): The user's message
        max_length (int): Maximum length of generated response
        temperature (float): Controls randomness of generation
        
    Returns:
        str: The generated response
    """
    global _model, _tokenizer, _device
    
    # Check if model is loaded
    if _model is None or _tokenizer is None:
        return "Model not loaded. Please initialize the model first."
    
    try:
        # Prepare the input
        inputs = _tokenizer(user_input, return_tensors="pt").to(_device)
        
        # Generate the response
        with torch.no_grad():
            generated_ids = _model.generate(
                inputs.input_ids,
                max_length=max_length,
                temperature=temperature,
                do_sample=True,
                pad_token_id=_tokenizer.eos_token_id
            )
        
        # Decode and return the response
        response = _tokenizer.decode(generated_ids[0], skip_special_tokens=True)
        
        # Remove the input prompt from the response if it appears
        if response.startswith(user_input):
            response = response[len(user_input):].strip()
            
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        return f"Sorry, I couldn't generate a response: {str(e)}"

def unload_model():
    """Clean up resources and free memory."""
    global _model, _tokenizer
    
    # Free up memory
    if _model is not None:
        del _model
        _model = None
    
    if _tokenizer is not None:
        del _tokenizer
        _tokenizer = None
    
    # Clear CUDA cache if available
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    
    print("Model unloaded and resources freed")