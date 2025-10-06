"""
AI model management and inference for the multimodal system
"""
import torch
import requests
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from loguru import logger
from transformers import (
    AutoTokenizer, AutoModel, 
    BlipProcessor, BlipForConditionalGeneration,
    pipeline
)
from sentence_transformers import SentenceTransformer
import config

class LocalLLM:
    """Interface for local language model via Ollama"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.model.llm_model
        self.base_url = "http://localhost:11434"
        self._check_ollama_connection()
    
    def _check_ollama_connection(self):
        """Check if Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                model_names = [model["name"] for model in models]
                if self.model_name not in model_names:
                    logger.warning(f"Model {self.model_name} not found. Available: {model_names}")
                    logger.info("To install the model, run: ollama pull llama3.1:8b")
            else:
                logger.error("Ollama is not responding properly")
        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Please start Ollama service.")
            logger.info("Install Ollama from: https://ollama.ai/")
            raise
    
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text response from prompt"""
        try:
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", config.model.temperature),
                    "top_p": kwargs.get("top_p", config.model.top_p),
                    "num_predict": kwargs.get("max_tokens", config.model.max_tokens)
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "I'm sorry, I encountered an error generating a response."
                
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I'm sorry, I encountered an error generating a response."
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Generate response from conversation history"""
        try:
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": False,
                "options": {
                    "temperature": kwargs.get("temperature", config.model.temperature),
                    "top_p": kwargs.get("top_p", config.model.top_p),
                    "num_predict": kwargs.get("max_tokens", config.model.max_tokens)
                }
            }
            
            response = requests.post(
                f"{self.base_url}/api/chat",
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("message", {}).get("content", "")
            else:
                logger.error(f"Ollama API error: {response.status_code}")
                return "I'm sorry, I encountered an error generating a response."
                
        except Exception as e:
            logger.error(f"Error generating chat response: {e}")
            return "I'm sorry, I encountered an error generating a response."

class ImageProcessor:
    """Handle image processing tasks like OCR and captioning"""
    
    def __init__(self):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._load_models()
    
    def _load_models(self):
        """Load image processing models"""
        try:
            # Image captioning model
            self.caption_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-caption-base")
            self.caption_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-caption-base")
            self.caption_model.to(self.device)
            
            # OCR model
            self.ocr_reader = None
            try:
                import easyocr
                self.ocr_reader = easyocr.Reader(['en'])
            except ImportError:
                logger.warning("EasyOCR not available. OCR functionality will be limited.")
            
            logger.info("Image processing models loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading image models: {e}")
            raise
    
    def describe_image(self, image_path: Union[str, Path]) -> str:
        """Generate description of an image"""
        try:
            from PIL import Image
            image = Image.open(image_path).convert('RGB')
            
            inputs = self.caption_processor(image, return_tensors="pt").to(self.device)
            out = self.caption_model.generate(**inputs, max_length=50)
            caption = self.caption_processor.decode(out[0], skip_special_tokens=True)
            
            return caption
            
        except Exception as e:
            logger.error(f"Error describing image: {e}")
            return "I couldn't process this image."
    
    def extract_text_from_image(self, image_path: Union[str, Path]) -> str:
        """Extract text from image using OCR"""
        try:
            if self.ocr_reader is None:
                return "OCR functionality not available. Please install EasyOCR."
            
            results = self.ocr_reader.readtext(str(image_path))
            text = " ".join([result[1] for result in results])
            
            return text if text.strip() else "No text found in image."
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {e}")
            return "I couldn't extract text from this image."

class EmbeddingModel:
    """Handle text embeddings for semantic search and similarity"""
    
    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.model.embedding_model
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load the embedding model"""
        try:
            self.model = SentenceTransformer(self.model_name)
            logger.info(f"Embedding model {self.model_name} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def encode(self, texts: Union[str, List[str]]) -> torch.Tensor:
        """Generate embeddings for text(s)"""
        return self.model.encode(texts)
    
    def similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        embeddings = self.encode([text1, text2])
        similarity = torch.cosine_similarity(
            embeddings[0:1], embeddings[1:2]
        ).item()
        return similarity

class MultimodalAI:
    """Main AI coordinator for multimodal interactions"""
    
    def __init__(self):
        self.llm = LocalLLM()
        self.image_processor = ImageProcessor()
        self.embedding_model = EmbeddingModel()
        self.conversation_history = []
    
    def process_text(self, text: str, context: str = "") -> str:
        """Process text input and generate response"""
        if context:
            prompt = f"Context: {context}\n\nUser: {text}\n\nAssistant:"
        else:
            prompt = f"User: {text}\n\nAssistant:"
        
        response = self.llm.generate(prompt)
        self.conversation_history.append({"role": "user", "content": text})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def process_image(self, image_path: Union[str, Path], task: str = "describe") -> str:
        """Process image and generate response"""
        image_path = Path(image_path)
        
        if task == "describe":
            description = self.image_processor.describe_image(image_path)
            return f"I can see: {description}"
        
        elif task == "ocr":
            text = self.image_processor.extract_text_from_image(image_path)
            return f"Text in image: {text}"
        
        elif task == "both":
            description = self.image_processor.describe_image(image_path)
            text = self.image_processor.extract_text_from_image(image_path)
            return f"I can see: {description}\n\nText in image: {text}"
        
        else:
            return "Unknown image processing task."
    
    def process_multimodal(self, text: str = "", image_path: Union[str, Path] = None) -> str:
        """Process combined text and image input"""
        if image_path and Path(image_path).exists():
            image_info = self.process_image(image_path, "both")
            prompt = f"User sent an image and said: '{text}'\n\nImage analysis: {image_info}\n\nPlease respond to both the text and image content."
        else:
            prompt = f"User: {text}"
        
        response = self.llm.generate(prompt)
        self.conversation_history.append({"role": "user", "content": f"Text: {text}, Image: {image_path}"})
        self.conversation_history.append({"role": "assistant", "content": response})
        
        return response
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []