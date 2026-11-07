"""
Archify Integration Module - Architecture Diagram Generator for OpenJarvis
Gera diagramas visuais da arquitetura usando Archify + Graphviz
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
try:
    import networkx as nx
except ImportError:
    nx = None


@dataclass
class ArchComponent:
    """Componente arquitetural"""
    id: str
    name: str
    layer: str
    component_type: str
    description: str
    color: Optional[str] = None


@dataclass
class ArchConnection:
    """Conexão entre componentes"""
    source: str
    target: str
    connection_type: str
    label: Optional[str] = None


class ArchifyGenerator:
    """Gera diagramas de arquitetura em múltiplos formatos"""
    
    LAYER_COLORS = {
        "router": "#FF6B6B",
        "skills": "#4ECDC4",
        "execution": "#45B7D1",
        "memory": "#FFA502",
        "security": "#8B0000",
        "automation": "#6C5CE7",
        "voice": "#00B894",
        "database": "#34495E"
    }
    
    COMPONENT_TYPES = {
        "agent": "🤖",
        "skill": "⚙️",
        "tool": "🛠️",
        "service": "🔧",
        "database": "💾",
        "router": "🔀",
        "queue": "📦",
        "cache": "⚡"
    }
    
    def __init__(self, output_dir: str = "J:\\tasksorobon\\jarvis\\diagrams"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.graph = nx.DiGraph()
        self.components: Dict[str, ArchComponent] = {}
        self.connections: List[ArchConnection] = []
    
    def add_component(self, component: ArchComponent) -> None:
        """Adiciona componente ao diagrama"""
        self.components[component.id] = component
        color = component.color or self.LAYER_COLORS.get(component.layer, "#CCCCCC")
        self.graph.add_node(
            component.id,
            label=f"{component.name}\n({component.component_type})",
            color=color,
            description=component.description,
            layer=component.layer
        )
    
    def add_connection(self, connection: ArchConnection) -> None:
        """Adiciona conexão entre componentes"""
        self.connections.append(connection)
        self.graph.add_edge(
            connection.source,
            connection.target,
            label=connection.label or connection.connection_type,
            connection_type=connection.connection_type
        )
    
    def generate_mermaid(self) -> str:
        """Gera diagrama em formato Mermaid"""
        lines = ["graph TD"]
        
        by_layer = {}
        for comp_id, comp in self.components.items():
            layer = comp.layer
            if layer not in by_layer:
                by_layer[layer] = []
            by_layer[layer].append(comp)
        
        for layer, comps in by_layer.items():
            lines.append(f"  subgraph {layer.upper()}")
            for comp in comps:
                icon = self.COMPONENT_TYPES.get(comp.component_type, "•")
                lines.append(f"    {comp.id}[\"{icon} {comp.name}\"]")
            lines.append("  end")
        
        for conn in self.connections:
            arrow = "-->|" + (conn.label or conn.connection_type) + "|"
            lines.append(f"  {conn.source} {arrow} {conn.target}")
        
        return "\n".join(lines)
    
    def generate_dot(self) -> str:
        """Gera diagrama em formato DOT (Graphviz)"""
        lines = ["digraph OpenJarvisArchitecture {"]
        lines.append("  rankdir=LR;")
        lines.append("  node [shape=box, style=rounded];")
        
        for comp_id, comp in self.components.items():
            icon = self.COMPONENT_TYPES.get(comp.component_type, "•")
            label = f"{icon} {comp.name}\\n{comp.component_type}"
            color = self.LAYER_COLORS.get(comp.layer, "#CCCCCC")
            lines.append(f"  \"{comp_id}\" [label=\"{label}\", fillcolor=\"{color}\", style=filled];")
        
        for conn in self.connections:
            label = conn.label or conn.connection_type
            style = "solid" if conn.connection_type == "sync" else "dashed"
            lines.append(f"  \"{conn.source}\" -> \"{conn.target}\" [label=\"{label}\", style={style}];")
        
        lines.append("}")
        return "\n".join(lines)
    
    def generate_json(self) -> str:
        """Exporta como JSON para frontend"""
        nodes = []
        for comp_id, comp in self.components.items():
            nodes.append({
                **asdict(comp),
                "color": comp.color or self.LAYER_COLORS.get(comp.layer, "#CCCCCC")
            })
        
        edges = [
            {
                "source": conn.source,
                "target": conn.target,
                "type": conn.connection_type,
                "label": conn.label
            }
            for conn in self.connections
        ]
        
        return json.dumps({
            "nodes": nodes,
            "edges": edges,
            "layers": list(self.LAYER_COLORS.keys())
        }, indent=2)
    
    def save_all_formats(self, base_name: str = "openjarvis_architecture") -> Dict[str, str]:
        """Salva diagrama em todos os formatos"""
        outputs = {}
        
        mermaid_content = self.generate_mermaid()
        mermaid_file = self.output_dir / f"{base_name}.md"
        mermaid_file.write_text(f"```mermaid\n{mermaid_content}\n```")
        outputs["mermaid"] = str(mermaid_file)
        
        dot_content = self.generate_dot()
        dot_file = self.output_dir / f"{base_name}.dot"
        dot_file.write_text(dot_content)
        outputs["dot"] = str(dot_file)
        
        json_content = self.generate_json()
        json_file = self.output_dir / f"{base_name}.json"
        json_file.write_text(json_content)
        outputs["json"] = str(json_file)
        
        return outputs
    
    def get_network_stats(self) -> Dict:
        """Retorna estatísticas da rede"""
        return {
            "total_nodes": len(self.components),
            "total_connections": len(self.connections),
            "by_layer": {
                layer: sum(1 for c in self.components.values() if c.layer == layer)
                for layer in set(c.layer for c in self.components.values())
            },
            "by_type": {
                comp_type: sum(1 for c in self.components.values() if c.component_type == comp_type)
                for comp_type in set(c.component_type for c in self.components.values())
            }
        }


def create_openjarvis_architecture_diagram() -> ArchifyGenerator:
    """Cria diagrama completo da arquitetura OpenJarvis"""
    gen = ArchifyGenerator()
    
    # ROUTER LAYER
    gen.add_component(ArchComponent(
        id="ponytail_bridge", name="Ponytail Bridge", layer="router",
        component_type="service", description="CLI tunelado + context compression"
    ))
    gen.add_component(ArchComponent(
        id="omni_router", name="OmniRoute", layer="router",
        component_type="router", description="Model selection + cost optimization"
    ))
    gen.add_component(ArchComponent(
        id="graphify", name="Graphify", layer="router",
        component_type="service", description="Agent discovery + dependency mapping"
    ))
    
    # SKILLS LAYER
    gen.add_component(ArchComponent(
        id="agent_skills_lib", name="Agent-Skills Library", layer="skills",
        component_type="skill", description="1900+ reusable skills"
    ))
    gen.add_component(ArchComponent(
        id="agency_agents", name="Agency Agents", layer="skills",
        component_type="skill", description="Persona-based composition"
    ))
    gen.add_component(ArchComponent(
        id="agent_reach", name="Agent-Reach", layer="skills",
        component_type="service", description="Dynamic skill discovery"
    ))
    
    # EXECUTION LAYER
    gen.add_component(ArchComponent(
        id="ecc_parser", name="ECC Parser", layer="execution",
        component_type="service", description="Parse 48 specs"
    ))
    gen.add_component(ArchComponent(
        id="agent_factory", name="AgentFactory", layer="execution",
        component_type="service", description="Dynamic instantiation"
    ))
    gen.add_component(ArchComponent(
        id="ecc_agents", name="ECC Agents (48)", layer="execution",
        component_type="agent", description="Specialized squad"
    ))
    
    # MEMORY LAYER
    gen.add_component(ArchComponent(
        id="codebase_memory", name="Codebase Memory MCP", layer="memory",
        component_type="service", description="Semantic context"
    ))
    gen.add_component(ArchComponent(
        id="context_compressor", name="Context-Mode", layer="memory",
        component_type="service", description="Token budget"
    ))
    gen.add_component(ArchComponent(
        id="memory_db", name="SQLite Memory", layer="database",
        component_type="database", description="State persistence"
    ))
    
    # SECURITY LAYER
    gen.add_component(ArchComponent(
        id="hallmark_validator", name="Hallmark", layer="security",
        component_type="service", description="Hallucination detection"
    ))
    gen.add_component(ArchComponent(
        id="rea_reasoner", name="REA", layer="security",
        component_type="service", description="Structured reasoning"
    ))
    gen.add_component(ArchComponent(
        id="security_auditor", name="Security Audit", layer="security",
        component_type="service", description="Vulnerability scanning"
    ))
    
    # AUTOMATION LAYER
    gen.add_component(ArchComponent(
        id="n8n_workflows", name="n8n", layer="automation",
        component_type="queue", description="1500+ integrations"
    ))
    gen.add_component(ArchComponent(
        id="survival_llm", name="Survival-LLM", layer="automation",
        component_type="service", description="Fallback strategies"
    ))
    
    # VOICE LAYER
    gen.add_component(ArchComponent(
        id="whisper_stt", name="Whisper STT", layer="voice",
        component_type="service", description="Speech-to-text"
    ))
    gen.add_component(ArchComponent(
        id="voicestudio_tts", name="VoiceStudio TTS", layer="voice",
        component_type="service", description="Text-to-speech"
    ))
    
    # CONNECTIONS
    gen.add_connection(ArchConnection("ponytail_bridge", "omni_router", "async", "request"))
    gen.add_connection(ArchConnection("omni_router", "graphify", "sync", "query"))
    gen.add_connection(ArchConnection("graphify", "agent_reach", "sync", "discover"))
    gen.add_connection(ArchConnection("agent_reach", "agent_skills_lib", "sync", "load"))
    gen.add_connection(ArchConnection("omni_router", "ecc_parser", "sync", "route"))
    gen.add_connection(ArchConnection("ecc_parser", "agent_factory", "sync", "create"))
    gen.add_connection(ArchConnection("agent_factory", "ecc_agents", "sync", "instantiate"))
    gen.add_connection(ArchConnection("ecc_agents", "codebase_memory", "sync", "context"))
    gen.add_connection(ArchConnection("codebase_memory", "context_compressor", "sync", "compress"))
    gen.add_connection(ArchConnection("context_compressor", "memory_db", "async", "persist"))
    gen.add_connection(ArchConnection("ecc_agents", "hallmark_validator", "sync", "validate"))
    gen.add_connection(ArchConnection("hallmark_validator", "rea_reasoner", "sync", "reason"))
    gen.add_connection(ArchConnection("rea_reasoner", "security_auditor", "sync", "audit"))
    gen.add_connection(ArchConnection("security_auditor", "n8n_workflows", "event", "trigger"))
    gen.add_connection(ArchConnection("n8n_workflows", "survival_llm", "async", "fallback"))
    gen.add_connection(ArchConnection("whisper_stt", "ponytail_bridge", "sync", "transcribe"))
    gen.add_connection(ArchConnection("security_auditor", "voicestudio_tts", "async", "speak"))
    
    return gen


if __name__ == "__main__":
    gen = create_openjarvis_architecture_diagram()
    outputs = gen.save_all_formats("openjarvis_architecture")
    
    print("✓ Diagramas gerados:")
    for fmt, path in outputs.items():
        print(f"  {fmt}: {path}")
    
    stats = gen.get_network_stats()
    print(f"\n✓ Estatísticas: {stats['total_nodes']} componentes, {stats['total_connections']} conexões")
