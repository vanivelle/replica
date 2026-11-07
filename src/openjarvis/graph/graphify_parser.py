"""
Graphify Integration - Agent Dependency Mapping & Discovery
Mapeia dependências entre agentes e habilidades
"""

import json
from typing import Dict, List, Set, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
from enum import Enum


class AgentCategory(Enum):
    """Categorias de agentes ECC"""
    CODE_REVIEW = "code_review"
    BUILD_TOOLS = "build_tools"
    RESEARCH = "research"
    ARCHITECTURE = "architecture"
    DEVOPS = "devops"
    DATA = "data"
    UTILITIES = "utilities"
    MONITORING = "monitoring"


@dataclass
class AgentNode:
    """Nó representando um agente na grafo"""
    agent_id: str
    name: str
    category: AgentCategory
    description: str
    capabilities: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    confidence_score: float = 1.0
    tags: Set[str] = field(default_factory=set)


@dataclass
class SkillNode:
    """Nó representando uma habilidade"""
    skill_id: str
    name: str
    description: str
    provider: str
    category: str
    version: str = "1.0.0"
    dependencies: List[str] = field(default_factory=list)


class DependencyGraph:
    """Grafo de dependências entre agentes e habilidades"""
    
    def __init__(self):
        self.agents: Dict[str, AgentNode] = {}
        self.skills: Dict[str, SkillNode] = {}
        self.agent_edges: Dict[str, Set[str]] = defaultdict(set)
        self.skill_edges: Dict[str, Set[str]] = defaultdict(set)
        self.agent_skill_edges: Dict[str, Set[str]] = defaultdict(set)
    
    def add_agent(self, agent: AgentNode) -> None:
        """Adiciona agente ao grafo"""
        self.agents[agent.agent_id] = agent
        for dep in agent.dependencies:
            self.agent_edges[agent.agent_id].add(dep)
    
    def add_skill(self, skill: SkillNode) -> None:
        """Adiciona habilidade ao grafo"""
        self.skills[skill.skill_id] = skill
        for dep in skill.dependencies:
            self.skill_edges[skill.skill_id].add(dep)
    
    def add_agent_skill_dependency(self, agent_id: str, skill_id: str) -> None:
        """Conecta agente a habilidade"""
        if agent_id not in self.agents:
            raise ValueError(f"Agente {agent_id} não existe")
        if skill_id not in self.skills:
            raise ValueError(f"Habilidade {skill_id} não existe")
        self.agent_skill_edges[agent_id].add(skill_id)
    
    def find_dependencies(self, agent_id: str, depth: Optional[int] = None) -> Dict[str, List[str]]:
        """BFS para encontrar todas as dependências transitivas"""
        if agent_id not in self.agents:
            return {}
        
        visited = set()
        queue = deque([(agent_id, 0)])
        result = {
            "direct_agents": [],
            "direct_skills": [],
            "transitive_agents": [],
            "transitive_skills": []
        }
        
        while queue:
            current_id, current_depth = queue.popleft()
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            if depth is not None and current_depth >= depth:
                continue
            
            if current_id in self.agents:
                for dep_agent in self.agent_edges.get(current_id, set()):
                    if current_depth == 0:
                        result["direct_agents"].append(dep_agent)
                    else:
                        if dep_agent not in result["transitive_agents"]:
                            result["transitive_agents"].append(dep_agent)
                    queue.append((dep_agent, current_depth + 1))
                
                for skill_id in self.agent_skill_edges.get(current_id, set()):
                    if current_depth == 0:
                        result["direct_skills"].append(skill_id)
                    else:
                        if skill_id not in result["transitive_skills"]:
                            result["transitive_skills"].append(skill_id)
        
        return result
    
    def find_dependents(self, agent_id: str) -> List[str]:
        """Encontra quais agentes dependem deste"""
        dependents = []
        for other_id, deps in self.agent_edges.items():
            if agent_id in deps:
                dependents.append(other_id)
        return dependents
    
    def detect_cycles(self) -> List[List[str]]:
        """Detecta ciclos nas dependências"""
        cycles = []
        visited = set()
        rec_stack = set()
        
        def visit(node: str, path: List[str]) -> None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)
            
            for neighbor in self.agent_edges.get(node, set()):
                if neighbor not in visited:
                    visit(neighbor, path.copy())
                elif neighbor in rec_stack:
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
            
            rec_stack.remove(node)
        
        for agent_id in self.agents:
            if agent_id not in visited:
                visit(agent_id, [])
        
        return cycles
    
    def get_critical_path(self) -> Tuple[str, int]:
        """Encontra caminho crítico (cadeia mais longa de dependências)"""
        max_depth = 0
        critical_agent = None
        
        visited_paths = {}
        
        def dfs_depth(node: str) -> int:
            if node in visited_paths:
                return visited_paths[node]
            
            max_child_depth = 0
            for neighbor in self.agent_edges.get(node, set()):
                child_depth = dfs_depth(neighbor)
                max_child_depth = max(max_child_depth, child_depth)
            
            result = max_child_depth + 1
            visited_paths[node] = result
            return result
        
        for agent_id in self.agents:
            depth = dfs_depth(agent_id)
            if depth > max_depth:
                max_depth = depth
                critical_agent = agent_id
        
        return critical_agent, max_depth
    
    def get_agents_by_category(self, category: AgentCategory) -> List[AgentNode]:
        """Retorna agentes filtrados por categoria"""
        return [a for a in self.agents.values() if a.category == category]
    
    def search_agents(self, query: str) -> List[AgentNode]:
        """Busca agentes por nome ou descrição"""
        query_lower = query.lower()
        results = []
        
        for agent in self.agents.values():
            if (query_lower in agent.name.lower() or
                query_lower in agent.description.lower() or
                any(query_lower in tag for tag in agent.tags)):
                results.append(agent)
        
        return results
    
    def get_graph_json(self) -> Dict:
        """Exporta grafo como JSON"""
        nodes = []
        edges = []
        
        for agent_id, agent in self.agents.items():
            nodes.append({
                "id": agent_id,
                "type": "agent",
                "name": agent.name,
                "category": agent.category.value,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "tags": list(agent.tags),
                "confidence": agent.confidence_score
            })
        
        for skill_id, skill in self.skills.items():
            nodes.append({
                "id": skill_id,
                "type": "skill",
                "name": skill.name,
                "provider": skill.provider,
                "category": skill.category,
                "version": skill.version
            })
        
        for source, targets in self.agent_edges.items():
            for target in targets:
                edges.append({
                    "source": source,
                    "target": target,
                    "type": "agent_dependency"
                })
        
        for agent_id, skills in self.agent_skill_edges.items():
            for skill_id in skills:
                edges.append({
                    "source": agent_id,
                    "target": skill_id,
                    "type": "uses_skill"
                })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "stats": {
                "total_agents": len(self.agents),
                "total_skills": len(self.skills),
                "total_connections": len(edges)
            }
        }
    
    def compute_agent_scores(self) -> Dict[str, float]:
        """Calcula score de importância para cada agente (PageRank-like)"""
        scores = {agent_id: 1.0 for agent_id in self.agents}
        damping_factor = 0.85
        
        for _ in range(10):
            new_scores = {}
            for agent_id in self.agents:
                incoming_edges = []
                for other_id, deps in self.agent_edges.items():
                    if agent_id in deps:
                        incoming_edges.append(other_id)
                
                if incoming_edges:
                    rank_sum = sum(scores[other_id] for other_id in incoming_edges)
                    new_scores[agent_id] = (1 - damping_factor) + damping_factor * rank_sum / len(incoming_edges)
                else:
                    new_scores[agent_id] = 1 - damping_factor
            
            scores = new_scores
        
        return scores
    
    def get_agent_cluster(self, agent_id: str) -> Set[str]:
        """Retorna cluster de agentes relacionados"""
        cluster = {agent_id}
        queue = deque([agent_id])
        
        while queue:
            current = queue.popleft()
            
            for neighbor in self.agent_edges.get(current, set()):
                if neighbor not in cluster:
                    cluster.add(neighbor)
                    queue.append(neighbor)
            
            for other_id, deps in self.agent_edges.items():
                if current in deps and other_id not in cluster:
                    cluster.add(other_id)
                    queue.append(other_id)
        
        return cluster


class GraphifyManager:
    """Gerenciador de grafo Graphify"""
    
    def __init__(self):
        self.graph = DependencyGraph()
    
    def load_ecc_agents(self, agents_data: List[Dict]) -> None:
        """Carrega agentes ECC no grafo"""
        for agent_data in agents_data:
            agent = AgentNode(
                agent_id=agent_data["id"],
                name=agent_data["name"],
                category=AgentCategory[agent_data.get("category", "UTILITIES").upper()],
                description=agent_data["description"],
                capabilities=agent_data.get("capabilities", []),
                required_skills=agent_data.get("required_skills", []),
                dependencies=agent_data.get("dependencies", []),
                confidence_score=agent_data.get("confidence", 1.0),
                tags=set(agent_data.get("tags", []))
            )
            self.graph.add_agent(agent)
    
    def load_skills(self, skills_data: List[Dict]) -> None:
        """Carrega habilidades no grafo"""
        for skill_data in skills_data:
            skill = SkillNode(
                skill_id=skill_data["id"],
                name=skill_data["name"],
                description=skill_data["description"],
                provider=skill_data.get("provider", "unknown"),
                category=skill_data.get("category", "general"),
                version=skill_data.get("version", "1.0.0"),
                dependencies=skill_data.get("dependencies", [])
            )
            self.graph.add_skill(skill)
    
    def link_agent_to_skills(self, agent_id: str, skill_ids: List[str]) -> None:
        """Conecta agente a múltiplas habilidades"""
        for skill_id in skill_ids:
            self.graph.add_agent_skill_dependency(agent_id, skill_id)
    
    def analyze_agent(self, agent_id: str) -> Dict:
        """Análise completa de um agente"""
        if agent_id not in self.graph.agents:
            return {}
        
        agent = self.graph.agents[agent_id]
        deps = self.graph.find_dependencies(agent_id)
        dependents = self.graph.find_dependents(agent_id)
        cluster = self.graph.get_agent_cluster(agent_id)
        scores = self.graph.compute_agent_scores()
        
        return {
            "agent": {
                "id": agent.agent_id,
                "name": agent.name,
                "category": agent.category.value,
                "description": agent.description,
                "capabilities": agent.capabilities,
                "tags": list(agent.tags),
                "confidence": agent.confidence_score
            },
            "dependencies": deps,
            "dependents": dependents,
            "cluster_size": len(cluster),
            "importance_score": scores.get(agent_id, 0.0),
            "critical_path_depth": self.graph.get_critical_path()[1]
        }
    
    def validate_consistency(self) -> Dict[str, any]:
        """Valida consistência do grafo"""
        cycles = self.graph.detect_cycles()
        missing_deps = []
        
        for agent_id, agent in self.graph.agents.items():
            for dep in agent.dependencies:
                if dep not in self.graph.agents:
                    missing_deps.append((agent_id, dep))
        
        return {
            "is_valid": len(cycles) == 0 and len(missing_deps) == 0,
            "cycle_count": len(cycles),
            "cycles": cycles,
            "missing_dependencies": missing_deps,
            "total_agents": len(self.graph.agents),
            "total_skills": len(self.graph.skills)
        }


if __name__ == "__main__":
    manager = GraphifyManager()
    
    sample_agents = [
        {
            "id": "code_reviewer_1",
            "name": "Code Review Agent",
            "category": "CODE_REVIEW",
            "description": "Analisa qualidade e segurança de código",
            "capabilities": ["review_code", "detect_vulnerabilities", "suggest_refactoring"],
            "required_skills": ["pylance", "security_scan"],
            "dependencies": []
        },
        {
            "id": "ecc_orchestrator",
            "name": "ECC Orchestrator",
            "category": "UTILITIES",
            "description": "Orquestra os 48 agentes",
            "capabilities": ["route_tasks", "manage_agents"],
            "required_skills": ["task_routing"],
            "dependencies": ["code_reviewer_1"]
        }
    ]
    
    manager.load_ecc_agents(sample_agents)
    print("✓ Grafo Graphify iniciado com sucesso")
    print(f"  Agentes: {len(manager.graph.agents)}")
