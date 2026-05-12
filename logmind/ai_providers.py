#!/usr/bin/env python3
"""
LogMind AI Providers Module - AI服务提供商集成模块
支持OpenAI、Claude、Gemini、Ollama等多种AI服务
"""

import os
import json
import hashlib
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from pathlib import Path
from abc import ABC, abstractmethod

try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import anthropic
    HAS_ANTHROPIC = True
except ImportError:
    HAS_ANTHROPIC = False

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


@dataclass
class AIResponse:
    """AI响应数据结构"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    cost: Optional[float] = None
    cached: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class AIConfig:
    """AI配置"""
    provider: str = "openai"
    model: str = "gpt-4"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    max_retries: int = 3
    timeout: int = 60
    max_concurrency: int = 5
    
    @classmethod
    def from_env(cls) -> 'AIConfig':
        """从环境变量创建配置"""
        # 优先检查OpenAI
        api_key = os.getenv('OPENAI_API_KEY')
        if api_key:
            return cls(provider='openai', api_key=api_key, model='gpt-4')
        
        # 检查Anthropic
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            return cls(provider='anthropic', api_key=api_key, model='claude-3-5-sonnet-20241022')
        
        # 检查Gemini
        api_key = os.getenv('GEMINI_API_KEY')
        if api_key:
            return cls(provider='gemini', api_key=api_key, model='gemini-1.5-pro')
        
        # 检查Ollama（本地）
        return cls(provider='ollama', api_key=None, model='llama3.2', base_url='http://localhost:11434')


class BaseAIProvider(ABC):
    """AI服务提供商基类"""
    
    def __init__(self, config: AIConfig):
        """初始化提供商"""
        self.config = config
        self.cache: Dict[str, AIResponse] = {}
        self.cache_dir = Path.home() / '.logmind' / 'cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
    @abstractmethod
    def analyze_error(self, error_pattern: str, context: str) -> str:
        """分析错误模式"""
        pass
    
    @abstractmethod
    def generate_fix_suggestion(self, error_pattern: str) -> str:
        """生成修复建议"""
        pass
    
    def _get_cache_key(self, prompt: str) -> str:
        """生成缓存键"""
        content = f"{prompt}:{self.config.model}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _load_cache(self, cache_key: str) -> Optional[AIResponse]:
        """加载缓存"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return AIResponse(
                        content=data['content'],
                        model=data['model'],
                        provider=data['provider'],
                        cached=True,
                        timestamp=datetime.fromisoformat(data['timestamp'])
                    )
            except (json.JSONDecodeError, KeyError):
                pass
        return None
    
    def _save_cache(self, cache_key: str, response: AIResponse):
        """保存缓存"""
        cache_file = self.cache_dir / f"{cache_key}.json"
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'content': response.content,
                    'model': response.model,
                    'provider': response.provider,
                    'timestamp': response.timestamp.isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # 缓存失败不影响主流程
    
    def get_system_prompt(self) -> str:
        """获取系统提示词"""
        return """你是一个专业的日志分析和故障诊断专家。你的职责是：
1. 分析错误日志模式，理解错误原因
2. 提供简洁、准确的修复建议
3. 用中文回答，语言简洁专业
4. 如果需要更多上下文，明确说明

请基于以下错误日志进行分析："""


class OpenAIProvider(BaseAIProvider):
    """OpenAI服务提供商"""
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
        if not HAS_OPENAI:
            raise ImportError("请安装 openai: pip install openai")
        
        self.client = openai.OpenAI(
            api_key=config.api_key or os.getenv('OPENAI_API_KEY'),
            base_url=config.base_url,
            timeout=config.timeout
        )
    
    def analyze_error(self, error_pattern: str, context: str = "") -> str:
        """分析错误模式"""
        cache_key = self._get_cache_key(f"analyze:{error_pattern}")
        cached = self._load_cache(cache_key)
        if cached:
            return cached.content
        
        prompt = f"{self.get_system_prompt()}\n\n错误模式：\n{error_pattern}\n\n上下文信息：\n{context or '无额外上下文'}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的日志分析助手。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content or ""
            ai_response = AIResponse(
                content=content,
                model=self.config.model,
                provider='openai',
                tokens_used=response.usage.total_tokens if hasattr(response, 'usage') else None
            )
            
            self._save_cache(cache_key, ai_response)
            return content
            
        except Exception as e:
            return f"❌ OpenAI API调用失败: {str(e)}"
    
    def generate_fix_suggestion(self, error_pattern: str) -> str:
        """生成修复建议"""
        cache_key = self._get_cache_key(f"fix:{error_pattern}")
        cached = self._load_cache(cache_key)
        if cached:
            return cached.content
        
        prompt = f"""作为一个专业的开发工程师，请为以下错误提供修复建议：

错误模式：
{error_pattern}

请提供：
1. 可能的原因分析
2. 具体的修复步骤
3. 预防措施

用中文回答，语言简洁明了："""
        
        try:
            response = self.client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "你是一个经验丰富的开发工程师，擅长诊断和修复各种错误。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=800
            )
            
            content = response.choices[0].message.content or ""
            ai_response = AIResponse(
                content=content,
                model=self.config.model,
                provider='openai',
                tokens_used=response.usage.total_tokens if hasattr(response, 'usage') else None
            )
            
            self._save_cache(cache_key, ai_response)
            return content
            
        except Exception as e:
            return f"❌ OpenAI API调用失败: {str(e)}"


class AnthropicProvider(BaseAIProvider):
    """Anthropic Claude服务提供商"""
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
        if not HAS_ANTHROPIC:
            raise ImportError("请安装 anthropic: pip install anthropic")
        
        self.client = anthropic.Anthropic(
            api_key=config.api_key or os.getenv('ANTHROPIC_API_KEY'),
            timeout=config.timeout
        )
    
    def analyze_error(self, error_pattern: str, context: str = "") -> str:
        """分析错误模式"""
        cache_key = self._get_cache_key(f"analyze:{error_pattern}")
        cached = self._load_cache(cache_key)
        if cached:
            return cached.content
        
        prompt = f"{self.get_system_prompt()}\n\n错误模式：\n{error_pattern}\n\n上下文信息：\n{context or '无额外上下文'}"
        
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=500,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                system="你是一个专业的日志分析助手。"
            )
            
            content = response.content[0].text if response.content else ""
            ai_response = AIResponse(
                content=content,
                model=self.config.model,
                provider='anthropic'
            )
            
            self._save_cache(cache_key, ai_response)
            return content
            
        except Exception as e:
            return f"❌ Anthropic API调用失败: {str(e)}"
    
    def generate_fix_suggestion(self, error_pattern: str) -> str:
        """生成修复建议"""
        prompt = f"""作为一个专业的开发工程师，请为以下错误提供修复建议：

错误模式：
{error_pattern}

请提供：
1. 可能的原因分析
2. 具体的修复步骤
3. 预防措施

用中文回答："""
        
        try:
            response = self.client.messages.create(
                model=self.config.model,
                max_tokens=800,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            return response.content[0].text if response.content else ""
            
        except Exception as e:
            return f"❌ Anthropic API调用失败: {str(e)}"


class OllamaProvider(BaseAIProvider):
    """Ollama本地模型服务提供商"""
    
    def __init__(self, config: AIConfig):
        super().__init__(config)
        self.base_url = config.base_url or "http://localhost:11434"
    
    def analyze_error(self, error_pattern: str, context: str = "") -> str:
        """分析错误模式"""
        cache_key = self._get_cache_key(f"analyze:{error_pattern}")
        cached = self._load_cache(cache_key)
        if cached:
            return cached.content
        
        prompt = f"{self.get_system_prompt()}\n\n错误模式：\n{error_pattern}\n\n上下文：\n{context or '无'}"
        
        try:
            import urllib.request
            import urllib.parse
            
            data = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": 500
                }
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                content = result.get('response', '')
                
                ai_response = AIResponse(
                    content=content,
                    model=self.config.model,
                    provider='ollama'
                )
                
                self._save_cache(cache_key, ai_response)
                return content
                
        except Exception as e:
            return f"❌ Ollama调用失败: {str(e)}\n请确保Ollama服务正在运行: ollama serve"
    
    def generate_fix_suggestion(self, error_pattern: str) -> str:
        """生成修复建议"""
        prompt = f"""作为一个专业的开发工程师，请为以下错误提供修复建议：

错误模式：
{error_pattern}

请提供：
1. 可能的原因分析
2. 具体的修复步骤
3. 预防措施

用中文回答："""
        
        try:
            import urllib.request
            
            data = {
                "model": self.config.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.5,
                    "num_predict": 800
                }
            }
            
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=json.dumps(data).encode('utf-8'),
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
            
            with urllib.request.urlopen(req, timeout=self.config.timeout) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('response', '')
                
        except Exception as e:
            return f"❌ Ollama调用失败: {str(e)}"


class AIManager:
    """
    AI管理器
    统一管理多个AI服务提供商
    """
    
    PROVIDERS = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'ollama': OllamaProvider,
        'claude': AnthropicProvider,  # Claude是Anthropic的别名
    }
    
    def __init__(self, config: Optional[AIConfig] = None):
        """初始化AI管理器"""
        self.config = config or AIConfig.from_env()
        self.provider: Optional[BaseAIProvider] = None
        self._init_provider()
    
    def _init_provider(self):
        """初始化AI提供商"""
        provider_class = self.PROVIDERS.get(self.config.provider)
        if provider_class:
            try:
                self.provider = provider_class(self.config)
            except ImportError as e:
                print(f"⚠️ {e}")
                print(f"   建议安装对应包或切换到其他AI提供商")
        else:
            print(f"⚠️ 不支持的AI提供商: {self.config.provider}")
            print(f"   支持的提供商: {', '.join(self.PROVIDERS.keys())}")
    
    def is_available(self) -> bool:
        """检查AI服务是否可用"""
        return self.provider is not None
    
    def analyze_error(self, error_pattern: str, context: str = "") -> str:
        """分析错误"""
        if not self.provider:
            return "❌ AI服务未配置，请设置相应的API密钥"
        return self.provider.analyze_error(error_pattern, context)
    
    def generate_fix_suggestion(self, error_pattern: str) -> str:
        """生成修复建议"""
        if not self.provider:
            return "❌ AI服务未配置"
        return self.provider.generate_fix_suggestion(error_pattern)
    
    def batch_analyze(self, error_patterns: List[str], 
                     progress_callback: Optional[Callable[[int, int], None]] = None) -> List[str]:
        """批量分析错误"""
        if not self.provider:
            return ["❌ AI服务未配置"] * len(error_patterns)
        
        results = []
        for i, pattern in enumerate(error_patterns):
            results.append(self.analyze_error(pattern))
            if progress_callback:
                progress_callback(i + 1, len(error_patterns))
        
        return results


def create_ai_manager(provider: str = "auto", **kwargs) -> AIManager:
    """
    创建AI管理器工厂函数
    
    Args:
        provider: AI提供商名称 ("auto", "openai", "anthropic", "ollama")
        **kwargs: 其他配置参数
        
    Returns:
        配置好的AIManager实例
    """
    if provider == "auto":
        config = AIConfig.from_env()
    else:
        config = AIConfig(provider=provider, **kwargs)
    
    return AIManager(config)
