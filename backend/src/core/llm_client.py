import time
import json
from typing import List, Dict, Any, Optional, Type, TypeVar
from pydantic import BaseModel
import openai
from langfuse import Langfuse
from langfuse import observe

from src.config.settings import LLMConfig, LangfuseConfig
import logging

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)

class InsufficientCreditsError(Exception):
    """Raised when the request exceeds the affordable token budget."""
    pass

class LLMClient:
    
    def __init__(self):
        self.client = openai.OpenAI(
            base_url=LLMConfig.BASE_URL,
            api_key=LLMConfig.API_KEY,
        )
        
        self.langfuse = None
        if LangfuseConfig.ENABLED and LangfuseConfig.PUBLIC_KEY:
            try:
                self.langfuse = Langfuse(
                    public_key=LangfuseConfig.PUBLIC_KEY,
                    secret_key=LangfuseConfig.SECRET_KEY,
                    host=LangfuseConfig.HOST
                )
                logger.info("✅ Langfuse initialized")
            except Exception as e:
                logger.warning(f"⚠️ Langfuse init failed: {e}")
        
        self.call_count = 0
        self.total_cost = 0.0
        self.affordable_tokens = 10000 # Jury-level safeguard budget
    
    @observe(name="LLM Call")
    def get_completion(
        self,
        messages: List[Dict[str, str]],
        model_type: str = "fast",
        temperature: float = 0.3,
        max_tokens: int = 800
    ) -> str:
        
        # --- PRE-FLIGHT CHECK (Jury-Level) ---
        estimated_prompt_tokens = sum(len(m.get("content", "")) for m in messages) // 3
        total_estimated = estimated_prompt_tokens + max_tokens
        
        if total_estimated > self.affordable_tokens:
            raise InsufficientCreditsError(
                f"Request requires ~{total_estimated} tokens, which exceeds limit of {self.affordable_tokens}. "
                "Reduce max_tokens or top up credits."
            )
        # ------------------------------------

        models = LLMConfig.MODELS.get(model_type, LLMConfig.MODELS["fast"])
        last_error = None
        
        for model in models:
            try:
                logger.debug(f"🔄 Trying model: {model}")
                
                response = self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    timeout=LLMConfig.TIMEOUT
                )
                
                self.call_count += 1
                if response.choices and response.choices[0].message.content:
                    content = response.choices[0].message.content
                    logger.debug(f"✅ Success with {model}")
                    return content
                else:
                    raise Exception("Empty response from LLM")
                
            except Exception as e:
                err_str = str(e).lower()
                # Stop retrying on cost/access issues
                if "402" in err_str or "payment" in err_str or "insufficient" in err_str:
                     logger.critical(f"💰 {model} PAYMENT REQUIRED: {e}")
                     raise InsufficientCreditsError(str(e))
                     
                if "429" in err_str or "rate" in err_str:
                    logger.warning(f"⚠️ Rate limit on {model}, waiting...")
                    time.sleep(LLMConfig.RETRY_DELAY)
                    last_error = e
                    continue
                
                logger.warning(f"❌ {model} failed: {str(e)[:100]}")
                last_error = e
                continue
        
        error_msg = f"All models failed. Last error: {last_error}"
        logger.error(error_msg)
        raise Exception(error_msg)
    
    @observe(name="Structured LLM Call")
    def get_structured_completion(
        self,
        messages: List[Dict[str, str]],
        response_model: Type[T],
        model_type: str = "structured",
        temperature: float = 0.2,
        max_retries: int = 3
    ) -> T:
        
        schema = response_model.model_json_schema()
        
        clean_schema = {
            "type": "object",
            "properties": {
                k: {"type": v.get("type", "string")} 
                for k, v in schema.get("properties", {}).items()
            },
            "required": schema.get("required", [])
        }
        
        schema_prompt = f"""
    CRITICAL: Respond with ONLY a valid JSON object. No explanations, no schema definitions.

    Example format:
    {json.dumps(clean_schema, indent=2)}

    Your response must be ACTUAL DATA matching this structure, not the schema itself.
    """
        
        enhanced_messages = messages.copy()
        if enhanced_messages and enhanced_messages[0]["role"] == "system":
            enhanced_messages[0]["content"] += "\n\n" + schema_prompt
        else:
            enhanced_messages.insert(0, {"role": "system", "content": schema_prompt})
    
        
        for attempt in range(max_retries):
            try:
                raw_response = self.get_completion(
                    messages=enhanced_messages,
                    model_type=model_type,
                    temperature=temperature,
                    max_tokens=800
                )
                
                cleaned = raw_response.strip()
                if cleaned.startswith("```json"):
                    cleaned = cleaned[7:]
                if cleaned.startswith("```"):
                    cleaned = cleaned[3:]
                if cleaned.endswith("```"):
                    cleaned = cleaned[:-3]
                cleaned = cleaned.strip()
                
                parsed_json = json.loads(cleaned)
                
                result = response_model(**parsed_json)
                
                logger.debug(f"✅ Structured output parsed successfully")
                return result
                
            except json.JSONDecodeError as e:
                logger.warning(f"⚠️ JSON parse failed (attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise ValueError(f"Failed to parse JSON after {max_retries} attempts. Raw: {raw_response[:200]}")
                time.sleep(1)
                
            except Exception as e:
                logger.warning(f"⚠️ Validation failed (attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    raise
                time.sleep(1)
        
        raise Exception("Should not reach here")
    
    def flush_traces(self):
        """Ensure all Langfuse traces are sent"""
        if self.langfuse:
            self.langfuse.flush()
            logger.info("📤 Langfuse traces flushed")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_calls": self.call_count,
            "estimated_cost_usd": self.total_cost
        }