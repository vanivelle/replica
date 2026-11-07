"""
ECC Agent Loader - Carrega todos os 42 agentes do repositório ECC
"""
import os
import yaml
import json
from typing import List, Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ECCAgentLoader:
    """Carrega e estrutura os 42 agentes do ECC"""
    
    def __init__(self, ecc_path: str):
        self.ecc_path = Path(ecc_path)
        self.agents_dir = self.ecc_path / "agents"
        self.agents = {}
        self.agent_list = []
    
    def load_all_agents(self) -> List[Dict[str, Any]]:
        """Carrega todos os agentes .md do diretório ECC"""
        if not self.agents_dir.exists():
            logger.error(f"ECC agents directory not found: {self.agents_dir}")
            return []
        
        agent_files = sorted(self.agents_dir.glob("*.md"))
        logger.info(f"Found {len(agent_files)} agent files in {self.agents_dir}")
        
        for agent_file in agent_files:
            try:
                agent_data = self._parse_agent_file(agent_file)
                if agent_data:
                    agent_id = agent_file.stem  # nome sem .md
                    self.agents[agent_id] = agent_data
                    self.agent_list.append(agent_data)
            except Exception as e:
                logger.error(f"Error loading agent {agent_file}: {e}")
        
        logger.info(f"Loaded {len(self.agents)} agents successfully")
        return self.agent_list
    
    def _parse_agent_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse de arquivo .md do agente"""
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Extract YAML frontmatter se existir
            agent_data = self._extract_metadata(content, file_path.stem)
            
            return agent_data
        except Exception as e:
            logger.error(f"Failed to parse {file_path}: {e}")
            return None
    
    def _extract_metadata(self, content: str, agent_id: str) -> Dict[str, Any]:
        """Extrai metadados do arquivo"""
        
        # Estrutura padrão para cada agente
        agent = {
            "id": agent_id,
            "name": self._humanize(agent_id),
            "description": "",
            "capabilities": [],
            "category": self._categorize(agent_id),
            "specialized_for": self._get_specialization(agent_id),
            "system_prompt": self._generate_system_prompt(agent_id),
            "version": "1.0",
            "enabled": True
        }
        
        # Extract descrição do conteúdo markdown
        lines = content.split("\n")
        
        # Procura pela primeira seção de descrição
        description_lines = []
        capture = False
        
        for line in lines:
            if line.startswith("##"):
                if not capture:
                    capture = True
                else:
                    break
            elif capture and line.strip():
                description_lines.append(line.strip())
        
        if description_lines:
            agent["description"] = " ".join(description_lines)[:500]  # Limita a 500 chars
        
        # Detecta capabilities baseado no tipo de agente
        agent["capabilities"] = self._detect_capabilities(agent_id)
        
        return agent
    
    def _humanize(self, agent_id: str) -> str:
        """Converte agent_id para nome legível"""
        return agent_id.replace("-", " ").title()
    
    def _categorize(self, agent_id: str) -> str:
        """Categoriza agente por tipo"""
        
        # Mapeamento de categorias
        categories = {
            "reviewer": ["reviewer", "analyzer", "evaluator"],
            "builder": ["resolver", "optimizer", "cleaner"],
            "architect": ["architect", "planner", "designer"],
            "specialist": ["specialist", "consultant", "expert"],
            "utility": ["helper", "runner", "lookup", "miner"],
        }
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in agent_id.lower():
                    return category
        
        return "general"
    
    def _get_specialization(self, agent_id: str) -> str:
        """Obtém especialização do agente"""
        
        specializations = {
            "python": ["python", "django", "pytorch"],
            "javascript": ["typescript", "react", "vue"],
            "java": ["java", "kotlin"],
            "cpp": ["cpp", "c++"],
            "go": ["go"],
            "rust": ["rust"],
            "database": ["database", "sql"],
            "security": ["security", "sanitizer"],
            "devops": ["network", "config", "docker", "kubernetes"],
            "ml": ["gan", "mle", "rag"],
            "web": ["seo", "frontend", "react"],
            "general": []
        }
        
        for spec, keywords in specializations.items():
            for keyword in keywords:
                if keyword in agent_id.lower():
                    return spec
        
        return "general"
    
    def _detect_capabilities(self, agent_id: str) -> List[str]:
        """Detecta capabilities do agente"""
        
        capabilities_map = {
            "review": ["code review", "analysis", "feedback"],
            "build": ["build resolution", "error fixing", "compilation"],
            "architect": ["architecture", "design", "planning"],
            "optimize": ["optimization", "performance", "refactoring"],
            "security": ["security analysis", "vulnerability scanning", "sanitization"],
            "test": ["testing", "validation", "qa"],
            "document": ["documentation", "updates", "comments"],
            "generate": ["generation", "creation", "synthesis"],
            "analyze": ["analysis", "inspection", "diagnostics"],
            "manage": ["management", "orchestration", "coordination"],
        }
        
        capabilities = []
        for capability, keywords in capabilities_map.items():
            for keyword in keywords:
                if keyword.split()[0] in agent_id.lower():
                    capabilities.append(keyword)
                    break
        
        return capabilities if capabilities else ["general assistance"]
    
    def _generate_system_prompt(self, agent_id: str) -> str:
        """Gera system prompt especializado para o agente"""
        
        name = self._humanize(agent_id)
        category = self._categorize(agent_id)
        specialization = self._get_specialization(agent_id)
        
        # Template base
        base_prompt = f"""You are {name}, a specialized AI agent in the OpenJarvis ecosystem.

Role: {category.title()} Agent
Specialization: {specialization.title()}

You are part of an autonomous multi-agent system designed to handle complex software engineering tasks through collaborative intelligence.

Your Core Responsibilities:
1. Provide expert-level analysis and recommendations in your domain
2. Maintain high code quality standards
3. Communicate clearly and concisely
4. Collaborate effectively with other agents
5. Learn from feedback and adapt your approach

When responding:
- Be direct and actionable
- Provide specific examples when possible
- Explain your reasoning
- Suggest alternatives when appropriate
- Flag potential issues proactively

You operate within the OpenJarvis Framework with access to:
- Other specialized agents for collaboration
- Real-time code analysis tools
- Context-aware memory systems
- Multi-provider LLM routing (Ollama, Grok, Gemini, Claude)

Remember: Quality and accuracy are non-negotiable. When in doubt, ask clarifying questions."""
        
        return base_prompt
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Obtém um agente específico"""
        return self.agents.get(agent_id)
    
    def get_agents_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Filtra agentes por categoria"""
        return [a for a in self.agent_list if a["category"] == category]
    
    def get_agents_by_specialization(self, spec: str) -> List[Dict[str, Any]]:
        """Filtra agentes por especialização"""
        return [a for a in self.agent_list if a["specialized_for"] == spec]
    
    def search_agents(self, query: str) -> List[Dict[str, Any]]:
        """Busca agentes por nome ou descrição"""
        query_lower = query.lower()
        return [
            a for a in self.agent_list
            if query_lower in a["name"].lower() or query_lower in a["description"].lower()
        ]
    
    def get_statistics(self) -> Dict[str, Any]:
        """Retorna estatísticas sobre os agentes carregados"""
        
        categories = {}
        specializations = {}
        
        for agent in self.agent_list:
            cat = agent["category"]
            spec = agent["specialized_for"]
            
            categories[cat] = categories.get(cat, 0) + 1
            specializations[spec] = specializations.get(spec, 0) + 1
        
        return {
            "total_agents": len(self.agent_list),
            "by_category": categories,
            "by_specialization": specializations,
            "enabled_agents": len([a for a in self.agent_list if a["enabled"]])
        }
    
    def export_agent_registry(self) -> Dict[str, Any]:
        """Exporta registro completo de agentes para uso na API"""
        return {
            "registry_version": "1.0",
            "timestamp": __import__("datetime").datetime.utcnow().isoformat(),
            "total_agents": len(self.agent_list),
            "agents": self.agent_list,
            "statistics": self.get_statistics()
        }


# Instância global do loader
_loader: Optional[ECCAgentLoader] = None


def initialize_ecc_loader(ecc_path: str):
    """Inicializa o loader global"""
    global _loader
    _loader = ECCAgentLoader(ecc_path)
    _loader.load_all_agents()
    logger.info(f"ECC Loader initialized with {len(_loader.agent_list)} agents")
    return _loader


def get_ecc_loader() -> ECCAgentLoader:
    """Retorna instância global do loader"""
    global _loader
    if _loader is None:
        raise RuntimeError("ECC Loader not initialized. Call initialize_ecc_loader first.")
    return _loader


def get_all_agents() -> List[Dict[str, Any]]:
    """Retorna todos os agentes carregados"""
    return get_ecc_loader().agent_list


def get_agent(agent_id: str) -> Optional[Dict[str, Any]]:
    """Obtém um agente específico"""
    return get_ecc_loader().get_agent(agent_id)


def search_agents(query: str) -> List[Dict[str, Any]]:
    """Busca agentes"""
    return get_ecc_loader().search_agents(query)
