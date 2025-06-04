# Fixed Model Manager with LoRA Adapter Support
# Add this cell to your notebook to replace the existing ModelManager

import os
import torch
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

# Complete imports for transformers
from transformers import (
    AutoTokenizer, AutoModelForCausalLM, 
    AutoModelForSequenceClassification, 
    AutoModelForQuestionAnswering,
    AutoModelForTokenClassification,
    AutoConfig, AutoModel,
    pipeline
)

# Try to import PEFT for LoRA adapters
try:
    from peft import PeftModel, PeftConfig, get_peft_model, LoraConfig, TaskType
    PEFT_AVAILABLE = True
    print("✅ PEFT available for LoRA adapter support")
except ImportError:
    PEFT_AVAILABLE = False
    print("⚠️ PEFT not available - installing for LoRA support...")
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'peft'])
        from peft import PeftModel, PeftConfig, get_peft_model, LoraConfig, TaskType
        PEFT_AVAILABLE = True
        print("✅ PEFT installed and imported successfully")
    except Exception as e:
        print(f"❌ Could not install PEFT: {e}")
        PEFT_AVAILABLE = False

class AdvancedModelManager:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.model_configs = {}
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.upload_dir = "/content/uploaded_models"
        os.makedirs(self.upload_dir, exist_ok=True)
        print(f"🔧 Using device: {self.device}")
        print(f"📁 Model upload directory: {self.upload_dir}")
    
    def upload_model_complete(self, model_name: str = None):
        """Complete model upload system - handles all model types including LoRA adapters"""
        print("🚀 ADVANCED MODEL UPLOAD SYSTEM")
        print("=" * 50)
        print("📋 This system supports:")
        print("  • HuggingFace models (config.json, pytorch_model.bin, tokenizer files)")
        print("  • LoRA Adapters (adapter_config.json, adapter_model.safetensors)")
        print("  • PyTorch models (.pt, .pth files)")
        print("  • Safetensors format (.safetensors)")
        print("  • ONNX models (.onnx)")
        print("  • Custom model architectures")
        print("=" * 50)
        
        # Step 1: Upload files
        print("📁 Please select and upload ALL your model files:")
        print("   - Model weights (.bin, .safetensors, .pt, .pth)")
        print("   - Configuration files (config.json, adapter_config.json)")
        print("   - Tokenizer files (tokenizer.json, vocab.txt, etc.)")
        print("   - Any other required files")
        
        from google.colab import files
        uploaded = files.upload()
        
        if not uploaded:
            print("❌ No files uploaded!")
            return False
        
        # Step 2: Analyze uploaded files
        file_info = self._analyze_uploaded_files(uploaded)
        
        # Step 3: Get model name
        if not model_name:
            model_name = input("🏷️ Enter a name for this model: ").strip()
            if not model_name:
                model_name = f"custom_model_{len(self.models)}"
        
        # Step 4: Create model directory
        model_dir = os.path.join(self.upload_dir, model_name)
        os.makedirs(model_dir, exist_ok=True)
        
        # Step 5: Move files to model directory
        for filename in uploaded.keys():
            src_path = filename
            dst_path = os.path.join(model_dir, filename)
            if os.path.exists(src_path):
                import shutil
                shutil.move(src_path, dst_path)
                print(f"📁 Moved {filename} to {model_dir}")
        
        # Step 6: Load the model
        success = self._load_uploaded_model(model_name, model_dir, file_info)
        
        if success:
            print(f"🎉 Model '{model_name}' uploaded and loaded successfully!")
            return True
        else:
            print(f"❌ Failed to load model '{model_name}'")
            return False
    
    def _analyze_uploaded_files(self, uploaded_files):
        """Analyze uploaded files to determine model type and structure"""
        file_info = {
            'model_files': [],
            'config_files': [],
            'tokenizer_files': [],
            'vocab_files': [],
            'adapter_files': [],
            'other_files': [],
            'model_type': 'unknown',
            'is_adapter': False
        }
        
        for filename in uploaded_files.keys():
            filename_lower = filename.lower()
            
            # Check for adapter files first
            if filename_lower == 'adapter_config.json':
                file_info['adapter_files'].append(filename)
                file_info['is_adapter'] = True
            elif filename_lower == 'adapter_model.safetensors' or filename_lower == 'adapter_model.bin':
                file_info['adapter_files'].append(filename)
                file_info['is_adapter'] = True
            
            # Model weight files
            elif any(ext in filename_lower for ext in ['.bin', '.safetensors', '.pt', '.pth', '.onnx']):
                file_info['model_files'].append(filename)
                
            # Configuration files
            elif any(name in filename_lower for name in ['config.json', 'model_config.json']):
                file_info['config_files'].append(filename)
                
            # Tokenizer files
            elif any(name in filename_lower for name in ['tokenizer.json', 'tokenizer_config.json']):
                file_info['tokenizer_files'].append(filename)
                
            # Vocabulary files
            elif any(name in filename_lower for name in ['vocab.txt', 'vocab.json', 'merges.txt', 'tokenizer.model']):
                file_info['vocab_files'].append(filename)
                
            else:
                file_info['other_files'].append(filename)
        
        # Determine model type
        if file_info['is_adapter']:
            file_info['model_type'] = 'lora_adapter'
        elif file_info['config_files'] and file_info['tokenizer_files']:
            file_info['model_type'] = 'huggingface'
        elif any('.pt' in f or '.pth' in f for f in file_info['model_files']):
            file_info['model_type'] = 'pytorch'
        elif any('.safetensors' in f for f in file_info['model_files']):
            file_info['model_type'] = 'safetensors'
        elif any('.onnx' in f for f in file_info['model_files']):
            file_info['model_type'] = 'onnx'
        
        print(f"🔍 Detected model type: {file_info['model_type']}")
        if file_info['is_adapter']:
            print("🔗 LoRA Adapter detected!")
        
        print(f"📊 File analysis:")
        for category, files in file_info.items():
            if files and category != 'model_type' and category != 'is_adapter':
                print(f"  {category}: {files}")
        
        return file_info
    
    def _load_uploaded_model(self, model_name: str, model_dir: str, file_info: dict):
        """Load the uploaded model based on its type"""
        try:
            if file_info['model_type'] == 'lora_adapter':
                return self._load_lora_adapter(model_name, model_dir, file_info)
            
            elif file_info['model_type'] == 'huggingface':
                return self._load_huggingface_model(model_name, model_dir)
            
            elif file_info['model_type'] == 'pytorch':
                return self._load_pytorch_model(model_name, model_dir, file_info)
            
            elif file_info['model_type'] == 'safetensors':
                return self._load_safetensors_model(model_name, model_dir, file_info)
            
            elif file_info['model_type'] == 'onnx':
                return self._load_onnx_model(model_name, model_dir, file_info)
            
            else:
                return self._load_custom_model(model_name, model_dir, file_info)
                
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            print("🔧 Trying alternative loading methods...")
            return self._try_alternative_loading(model_name, model_dir, file_info)
    
    def _load_lora_adapter(self, model_name: str, model_dir: str, file_info: dict):
        """Load LoRA adapter model"""
        if not PEFT_AVAILABLE:
            print("❌ PEFT library not available for LoRA adapters")
            return False
        
        try:
            print(f"🔗 Loading LoRA adapter from {model_dir}")
            
            # Load adapter config
            adapter_config_path = os.path.join(model_dir, 'adapter_config.json')
            with open(adapter_config_path, 'r') as f:
                adapter_config = json.load(f)
            
            print(f"📋 Adapter config: {adapter_config}")
            
            # Get base model name
            base_model_name = adapter_config.get('base_model_name_or_path', '')
            if not base_model_name:
                print("🤔 Base model not specified in config. Please enter base model name:")
                base_model_name = input("Enter HuggingFace model name (e.g., 'microsoft/DialoGPT-medium'): ").strip()
                
                if not base_model_name:
                    print("❌ Base model name required for LoRA adapter")
                    return False
            
            print(f"📥 Loading base model: {base_model_name}")
            
            # Load tokenizer
            try:
                tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
                print("✅ Tokenizer loaded from adapter directory")
            except:
                try:
                    tokenizer = AutoTokenizer.from_pretrained(base_model_name)
                    print("✅ Tokenizer loaded from base model")
                except Exception as e:
                    print(f"❌ Could not load tokenizer: {e}")
                    return False
            
            # Load base model
            try:
                base_model = AutoModelForCausalLM.from_pretrained(
                    base_model_name,
                    torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                    device_map="auto" if self.device == "cuda" else None
                )
                print("✅ Base model loaded successfully")
            except Exception as e:
                print(f"❌ Could not load base model: {e}")
                return False
            
            # Load adapter
            try:
                model = PeftModel.from_pretrained(base_model, model_dir)
                print("✅ LoRA adapter loaded and merged with base model")
            except Exception as e:
                print(f"❌ Could not load adapter: {e}")
                return False
            
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            self.model_configs[model_name] = {
                'type': 'lora_adapter',
                'path': model_dir,
                'base_model': base_model_name,
                'adapter_config': adapter_config
            }
            
            return True
            
        except Exception as e:
            print(f"❌ LoRA adapter loading failed: {e}")
            return False
    
    def _load_huggingface_model(self, model_name: str, model_dir: str):
        """Load HuggingFace format model"""
        try:
            print(f"🤗 Loading HuggingFace model from {model_dir}")
            
            # Load tokenizer
            tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
            print("✅ Tokenizer loaded successfully")
            
            # Try different model classes
            model_classes = [
                AutoModelForCausalLM,
                AutoModelForSequenceClassification,
                AutoModelForQuestionAnswering,
                AutoModelForTokenClassification,
                AutoModel
            ]
            
            model = None
            for model_class in model_classes:
                try:
                    model = model_class.from_pretrained(
                        model_dir,
                        local_files_only=True,
                        torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                        device_map="auto" if self.device == "cuda" else None
                    )
                    print(f"✅ Model loaded successfully with {model_class.__name__}")
                    break
                except Exception as e:
                    print(f"⚠️ {model_class.__name__} failed: {e}")
                    continue
            
            if model is None:
                raise Exception("Could not load model with any AutoModel class")
            
            self.models[model_name] = model
            self.tokenizers[model_name] = tokenizer
            self.model_configs[model_name] = {
                'type': 'huggingface',
                'path': model_dir,
                'model_class': type(model).__name__
            }
            
            return True
            
        except Exception as e:
            print(f"❌ HuggingFace loading failed: {e}")
            return False
    
    def _load_pytorch_model(self, model_name: str, model_dir: str, file_info: dict):
        """Load PyTorch model"""
        try:
            print(f"🔥 Loading PyTorch model from {model_dir}")
            
            # Find the model file
            model_file = None
            for filename in file_info['model_files']:
                if '.pt' in filename or '.pth' in filename:
                    model_file = os.path.join(model_dir, filename)
                    break
            
            if not model_file:
                raise Exception("No PyTorch model file found")
            
            # Load the model
            checkpoint = torch.load(model_file, map_location=self.device)
            print(f"✅ Loaded PyTorch model from {model_file}")
            
            # Store the model
            self.models[model_name] = checkpoint
            self.model_configs[model_name] = {
                'type': 'pytorch',
                'path': model_file,
                'keys': list(checkpoint.keys()) if isinstance(checkpoint, dict) else ['model_state']
            }
            
            print(f"📊 Model contains: {list(checkpoint.keys()) if isinstance(checkpoint, dict) else 'Direct model object'}")
            
            return True
            
        except Exception as e:
            print(f"❌ PyTorch loading failed: {e}")
            return False
    
    def _load_safetensors_model(self, model_name: str, model_dir: str, file_info: dict):
        """Load Safetensors model"""
        try:
            print("🔒 Loading Safetensors model...")
            
            # Try to import safetensors
            try:
                from safetensors import safe_open
            except ImportError:
                print("❌ Safetensors library not available. Installing...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'safetensors'])
                from safetensors import safe_open
            
            # Find safetensors file
            safetensors_file = None
            for filename in file_info['model_files']:
                if '.safetensors' in filename:
                    safetensors_file = os.path.join(model_dir, filename)
                    break
            
            if not safetensors_file:
                raise Exception("No safetensors file found")
            
            # Load the model
            tensors = {}
            with safe_open(safetensors_file, framework="pt", device=self.device) as f:
                for key in f.keys():
                    tensors[key] = f.get_tensor(key)
            
            self.models[model_name] = tensors
            self.model_configs[model_name] = {
                'type': 'safetensors',
                'path': safetensors_file,
                'keys': list(tensors.keys())
            }
            
            print(f"✅ Loaded Safetensors model with {len(tensors)} tensors")
            return True
            
        except Exception as e:
            print(f"❌ Safetensors loading failed: {e}")
            return False
    
    def _load_onnx_model(self, model_name: str, model_dir: str, file_info: dict):
        """Load ONNX model"""
        try:
            print("🧠 Loading ONNX model...")
            
            # Try to import onnxruntime
            try:
                import onnxruntime as ort
            except ImportError:
                print("❌ ONNX Runtime not available. Installing...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'onnxruntime'])
                import onnxruntime as ort
            
            # Find ONNX file
            onnx_file = None
            for filename in file_info['model_files']:
                if '.onnx' in filename:
                    onnx_file = os.path.join(model_dir, filename)
                    break
            
            if not onnx_file:
                raise Exception("No ONNX file found")
            
            # Create ONNX session
            session = ort.InferenceSession(onnx_file)
            
            self.models[model_name] = session
            self.model_configs[model_name] = {
                'type': 'onnx',
                'path': onnx_file,
                'inputs': [input.name for input in session.get_inputs()],
                'outputs': [output.name for output in session.get_outputs()]
            }
            
            print(f"✅ Loaded ONNX model")
            print(f"📊 Inputs: {self.model_configs[model_name]['inputs']}")
            print(f"📊 Outputs: {self.model_configs[model_name]['outputs']}")
            
            return True
            
        except Exception as e:
            print(f"❌ ONNX loading failed: {e}")
            return False
    
    def _load_custom_model(self, model_name: str, model_dir: str, file_info: dict):
        """Load custom model format"""
        print("🔧 Attempting to load as custom model...")
        
        # Try to load any model files as raw data
        loaded_files = {}
        for filename in file_info['model_files']:
            file_path = os.path.join(model_dir, filename)
            try:
                if filename.endswith(('.json',)):
                    with open(file_path, 'r') as f:
                        loaded_files[filename] = json.load(f)
                elif filename.endswith(('.txt',)):
                    with open(file_path, 'r') as f:
                        loaded_files[filename] = f.read()
                else:
                    # Try to load as binary
                    with open(file_path, 'rb') as f:
                        loaded_files[filename] = f.read()
                
                print(f"✅ Loaded {filename} as raw data")
            except Exception as e:
                print(f"❌ Failed to load {filename}: {e}")
        
        if loaded_files:
            self.models[model_name] = loaded_files
            self.model_configs[model_name] = {
                'type': 'custom',
                'path': model_dir,
                'files': list(loaded_files.keys())
            }
            return True
        
        return False
    
    def _try_alternative_loading(self, model_name: str, model_dir: str, file_info: dict):
        """Try alternative loading methods as fallback"""
        print("🔄 Trying alternative loading methods...")
        
        # Method 1: Try loading as generic transformer
        try:
            config = AutoConfig.from_pretrained(model_dir, local_files_only=True)
            model = AutoModel.from_pretrained(model_dir, config=config, local_files_only=True)
            
            self.models[model_name] = model
            self.model_configs[model_name] = {
                'type': 'huggingface_fallback',
                'path': model_dir
            }
            print("✅ Loaded using AutoModel as fallback")
            return True
        except Exception as e:
            print(f"⚠️ AutoModel fallback failed: {e}")
        
        # Method 2: Load all files as raw data for manual processing
        try:
            all_files = {}
            for filename in os.listdir(model_dir):
                file_path = os.path.join(model_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        # Try different loading methods
                        if filename.endswith('.json'):
                            with open(file_path, 'r') as f:
                                all_files[filename] = json.load(f)
                        elif filename.endswith(('.bin', '.pt', '.pth')):
                            all_files[filename] = torch.load(file_path, map_location='cpu')
                        else:
                            with open(file_path, 'rb') as f:
                                all_files[filename] = f.read()
                    except:
                        pass
            
            if all_files:
                self.models[model_name] = all_files
                self.model_configs[model_name] = {
                    'type': 'raw_files',
                    'path': model_dir,
                    'files': list(all_files.keys())
                }
                print("✅ Loaded all files as raw data for manual processing")
                return True
        except Exception as e:
            print(f"⚠️ Raw file loading failed: {e}")
        
        return False
    
    def use_model(self, model_name: str, input_text: str = None):
        """Use a loaded model for inference"""
        if model_name not in self.models:
            return f"❌ Model '{model_name}' not found. Available models: {list(self.models.keys())}"
        
        model = self.models[model_name]
        config = self.model_configs.get(model_name, {})
        model_type = config.get('type', 'unknown')
        
        try:
            if model_type in ['huggingface', 'lora_adapter'] and model_name in self.tokenizers:
                if not input_text:
                    input_text = input("Enter text for the model: ")
                
                tokenizer = self.tokenizers[model_name]
                
                # Handle special tokens
                if tokenizer.pad_token is None:
                    tokenizer.pad_token = tokenizer.eos_token
                
                inputs = tokenizer.encode(input_text, return_tensors='pt').to(self.device)
                
                with torch.no_grad():
                    outputs = model.generate(
                        inputs,
                        max_length=inputs.shape[1] + 100,
                        num_return_sequences=1,
                        temperature=0.7,
                        do_sample=True,
                        pad_token_id=tokenizer.pad_token_id,
                        eos_token_id=tokenizer.eos_token_id
                    )
                
                generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
                
                # Remove the input text from the output for cleaner response
                if generated_text.startswith(input_text):
                    generated_text = generated_text[len(input_text):].strip()
                
                return f"🤖 Model output:\n{generated_text}"
            
            elif model_type == 'onnx':
                return f"🧠 ONNX model loaded. Use custom inference code with inputs: {config['inputs']}"
            
            else:
                return f"📊 Model '{model_name}' loaded successfully. Type: {model_type}\nConfig: {config}"
                
        except Exception as e:
            return f"❌ Error using model: {e}"
    
    def list_models(self):
        """List all available models"""
        if not self.models:
            print("📭 No models loaded yet.")
        else:
            print("🤖 Available models:")
            for name, model in self.models.items():
                config = self.model_configs.get(name, {})
                model_type = config.get('type', 'unknown')
                print(f"  - {name} (Type: {model_type})")
                if 'base_model' in config:
                    print(f"    Base Model: {config['base_model']}")
                if 'path' in config:
                    print(f"    Path: {config['path']}")
    
    def get_model_info(self, model_name: str):
        """Get detailed information about a specific model"""
        if model_name not in self.models:
            return f"❌ Model '{model_name}' not found."
        
        config = self.model_configs.get(model_name, {})
        info = f"📊 Model Information for '{model_name}':\n"
        info += f"  Type: {config.get('type', 'unknown')}\n"
        info += f"  Path: {config.get('path', 'N/A')}\n"
        
        if 'base_model' in config:
            info += f"  Base Model: {config['base_model']}\n"
        if 'keys' in config:
            info += f"  Keys: {config['keys']}\n"
        if 'inputs' in config:
            info += f"  Inputs: {config['inputs']}\n"
        if 'outputs' in config:
            info += f"  Outputs: {config['outputs']}\n"
        if 'adapter_config' in config:
            info += f"  Adapter Config: {config['adapter_config']}\n"
        
        return info

# Replace the old model manager with the new one
print("🔄 Updating model manager with LoRA adapter support...")
model_manager = AdvancedModelManager()

# Update the agent to use the new model manager
if 'agent' in globals():
    agent.model_manager = model_manager
    agent.action_executor.model_manager = model_manager
    print("✅ Agent updated with new model manager")

print("🎉 Advanced Model Manager with LoRA support is ready!")
print("📝 To upload your LoRA adapter, run:")
print("model_manager.upload_model_complete()")