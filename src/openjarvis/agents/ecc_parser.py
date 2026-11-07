"""
ECC Parser - Elite Cloud Crowd Agent Loader & Parser
Carrega e processa especificações de 48 agentes especializados do ecossistema ECC
"""

import json
from typing import Dict, List, Optional, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path


class ECCCategory(Enum):
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
class ECCAgentSpec:
    """Especificação de um agente ECC"""
    id: str
    name: str
    category: ECCCategory
    description: str
    capabilities: List[str] = field(default_factory=list)
    required_skills: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    system_prompt_template: str = ""
    example_tasks: List[str] = field(default_factory=list)
    success_metrics: List[str] = field(default_factory=list)
    failure_modes: List[str] = field(default_factory=list)
    tags: Set[str] = field(default_factory=set)
    version: str = "1.0.0"
    confidence_score: float = 1.0
    requires_gpu: bool = False
    estimated_latency_ms: int = 1000


class ECCAgentDatabase:
    """Banco de dados de agentes ECC"""
    
    # 8 agentes CODE_REVIEW
    CODE_REVIEW_AGENTS = [
        {
            "id": "ecc_code_reviewer_python",
            "name": "Python Code Reviewer",
            "category": ECCCategory.CODE_REVIEW,
            "description": "Especialista em revisão de código Python com análise de qualidade, segurança e performance",
            "capabilities": ["review_python_code", "detect_vulnerabilities", "suggest_optimizations", "check_pep8"],
            "required_skills": ["pylance", "pylint", "black", "security_scan"],
            "example_tasks": ["Review this Python module for security issues"],
            "tags": ["python", "security", "quality"]
        },
        {
            "id": "ecc_code_reviewer_typescript",
            "name": "TypeScript Code Reviewer",
            "category": ECCCategory.CODE_REVIEW,
            "description": "Especialista em revisão de código TypeScript/JavaScript",
            "capabilities": ["review_typescript_code", "type_checking", "async_pattern_analysis"],
            "required_skills": ["eslint", "typescript_compiler", "prettier"],
            "tags": ["typescript", "javascript", "frontend"]
        },
        {
            "id": "ecc_code_reviewer_go",
            "name": "Go Code Reviewer",
            "category": ECCCategory.CODE_REVIEW,
            "description": "Especialista em revisão de código Go",
            "capabilities": ["review_go_code", "goroutine_analysis", "performance_profiling"],
            "required_skills": ["gofmt", "govet", "golint"],
            "tags": ["go", "concurrency", "systems"]
        },
        {
            "id": "ecc_code_reviewer_rust",
            "name": "Rust Code Reviewer",
            "category": ECCCategory.CODE_REVIEW,
            "description": "Especialista em revisão de código Rust com foco em segurança de memória",
            "capabilities": ["review_rust_code", "borrow_checker_analysis", "unsafe_code_audit"],
            "required_skills": ["cargo", "clippy", "rustfmt"],
            "tags": ["rust", "safety", "systems"]
        },
        {
            "id": "ecc_security_auditor",
            "name": "Security Auditor",
            "category": ECCCategory.CODE_REVIEW,
            "description": "Auditor de segurança especializado em OWASP, CVSS e conformidade",
            "capabilities": ["audit_security", "vulnerability_scoring", "compliance_check"],
            "required_skills": ["security_scan", "sast", "dast"],
            "tags": ["security", "compliance", "audit"]
        },
        {
            "id": "ecc_performance_reviewer",
            "name": "Performance Reviewer",
            "category": ECCCategory.CODE_REVIEW,
            "description": "Especialista em otimização de performance e profiling",
            "capabilities": ["analyze_performance", "profile_code", "suggest_optimizations"],
            "required_skills": ["profiler", "flamegraph", "benchmarking"],
            "tags": ["performance", "optimization", "profiling"]
        },
        {
            "id": "ecc_documentation_reviewer",
            "name": "Documentation Reviewer",
            "category": ECCCategory.CODE_REVIEW,
            "description": "Revisor especializado em documentação e API docs",
            "capabilities": ["review_docs", "generate_api_docs", "check_completeness"],
            "required_skills": ["sphinx", "swagger", "typedoc"],
            "tags": ["documentation", "api", "communication"]
        },
        {
            "id": "ecc_test_reviewer",
            "name": "Test Coverage Reviewer",
            "category": ECCCategory.CODE_REVIEW,
            "description": "Especialista em análise de cobertura de testes e qualidade de testes",
            "capabilities": ["analyze_test_coverage", "suggest_test_cases", "evaluate_test_quality"],
            "required_skills": ["coverage", "pytest", "jest", "mocha"],
            "tags": ["testing", "quality", "coverage"]
        }
    ]
    
    # 5 agentes BUILD_TOOLS
    BUILD_TOOLS_AGENTS = [
        {
            "id": "ecc_build_optimizer",
            "name": "Build Optimizer",
            "category": ECCCategory.BUILD_TOOLS,
            "description": "Otimizador de builds e processos de compilação",
            "capabilities": ["optimize_build", "reduce_build_time", "analyze_dependencies"],
            "required_skills": ["gradle", "maven", "bazel", "cmake"],
            "tags": ["build", "performance", "ci-cd"]
        },
        {
            "id": "ecc_ci_cd_architect",
            "name": "CI/CD Architect",
            "category": ECCCategory.BUILD_TOOLS,
            "description": "Especialista em arquitetura CI/CD",
            "capabilities": ["design_ci_cd", "implement_pipelines", "optimize_workflows"],
            "required_skills": ["github-actions", "gitlab-ci", "jenkins"],
            "tags": ["ci-cd", "devops", "automation"]
        },
        {
            "id": "ecc_dependency_manager",
            "name": "Dependency Manager",
            "category": ECCCategory.BUILD_TOOLS,
            "description": "Gerenciador de dependências e resolução de conflitos",
            "capabilities": ["manage_dependencies", "resolve_conflicts", "audit_vulnerabilities"],
            "required_skills": ["npm", "pip", "cargo", "go_modules"],
            "tags": ["dependencies", "versioning", "security"]
        },
        {
            "id": "ecc_container_builder",
            "name": "Container Builder",
            "category": ECCCategory.BUILD_TOOLS,
            "description": "Especialista em Docker/Kubernetes e containerização",
            "capabilities": ["build_containers", "optimize_images", "deploy_kubernetes"],
            "required_skills": ["docker", "kubernetes", "helm"],
            "tags": ["containers", "devops", "infrastructure"]
        },
        {
            "id": "ecc_release_manager",
            "name": "Release Manager",
            "category": ECCCategory.BUILD_TOOLS,
            "description": "Gestor de releases e versioning",
            "capabilities": ["manage_releases", "handle_versioning", "create_changelogs"],
            "required_skills": ["git", "semantic-versioning", "release-tools"],
            "tags": ["release", "versioning", "management"]
        }
    ]
    
    # 3 agentes RESEARCH
    RESEARCH_AGENTS = [
        {
            "id": "ecc_research_expert",
            "name": "Research Expert",
            "category": ECCCategory.RESEARCH,
            "description": "Pesquisador especializado em busca de informações e síntese",
            "capabilities": ["research_topic", "synthesize_findings", "cite_sources"],
            "required_skills": ["web_search", "academic_database", "synthesis"],
            "tags": ["research", "information", "synthesis"]
        },
        {
            "id": "ecc_trend_analyst",
            "name": "Trend Analyst",
            "category": ECCCategory.RESEARCH,
            "description": "Analista de tendências tecnológicas e mercado",
            "capabilities": ["analyze_trends", "predict_future", "identify_opportunities"],
            "required_skills": ["data_analysis", "visualization", "forecasting"],
            "tags": ["trends", "analytics", "prediction"]
        },
        {
            "id": "ecc_competitive_researcher",
            "name": "Competitive Researcher",
            "category": ECCCategory.RESEARCH,
            "description": "Pesquisador de inteligência competitiva",
            "capabilities": ["competitive_analysis", "benchmark_tools", "identify_competitors"],
            "required_skills": ["market_analysis", "competitive_intelligence"],
            "tags": ["competitive", "market", "analysis"]
        }
    ]
    
    # 8 agentes ARCHITECTURE
    ARCHITECTURE_AGENTS = [
        {
            "id": "ecc_microservices_architect",
            "name": "Microservices Architect",
            "category": ECCCategory.ARCHITECTURE,
            "description": "Especialista em design de arquitetura de microserviços",
            "capabilities": ["design_microservices", "api_gateway", "service_mesh"],
            "required_skills": ["architecture", "kubernetes", "service-mesh"],
            "tags": ["architecture", "microservices", "scalability"]
        },
        {
            "id": "ecc_data_architect",
            "name": "Data Architect",
            "category": ECCCategory.ARCHITECTURE,
            "description": "Especialista em arquitetura de dados e pipelines",
            "capabilities": ["design_data_architecture", "data_pipelines", "data_lake"],
            "required_skills": ["sql", "spark", "airflow"],
            "tags": ["data", "architecture", "pipelines"]
        },
        {
            "id": "ecc_cloud_architect",
            "name": "Cloud Architect",
            "category": ECCCategory.ARCHITECTURE,
            "description": "Especialista em arquitetura cloud (AWS, GCP, Azure)",
            "capabilities": ["design_cloud", "multi_cloud", "cost_optimization"],
            "required_skills": ["aws", "gcp", "azure"],
            "tags": ["cloud", "infrastructure", "scalability"]
        },
        {
            "id": "ecc_api_architect",
            "name": "API Architect",
            "category": ECCCategory.ARCHITECTURE,
            "description": "Especialista em design de APIs RESTful e gRPC",
            "capabilities": ["design_api", "api_versioning", "backwards_compatibility"],
            "required_skills": ["openapi", "graphql", "grpc"],
            "tags": ["api", "design", "integration"]
        },
        {
            "id": "ecc_security_architect",
            "name": "Security Architect",
            "category": ECCCategory.ARCHITECTURE,
            "description": "Especialista em arquitetura de segurança",
            "capabilities": ["security_design", "threat_modeling", "compliance"],
            "required_skills": ["threat-modeling", "security-frameworks"],
            "tags": ["security", "architecture", "compliance"]
        },
        {
            "id": "ecc_performance_architect",
            "name": "Performance Architect",
            "category": ECCCategory.ARCHITECTURE,
            "description": "Especialista em otimização de performance de sistemas",
            "capabilities": ["design_performance", "scalability", "caching_strategies"],
            "required_skills": ["performance", "caching", "load-balancing"],
            "tags": ["performance", "architecture", "scalability"]
        },
        {
            "id": "ecc_frontend_architect",
            "name": "Frontend Architect",
            "category": ECCCategory.ARCHITECTURE,
            "description": "Especialista em arquitetura frontend e UI/UX",
            "capabilities": ["design_frontend", "component_architecture", "state_management"],
            "required_skills": ["react", "vue", "angular"],
            "tags": ["frontend", "ui-ux", "architecture"]
        },
        {
            "id": "ecc_infrastructure_architect",
            "name": "Infrastructure Architect",
            "category": ECCCategory.ARCHITECTURE,
            "description": "Especialista em infraestrutura e DevOps",
            "capabilities": ["design_infrastructure", "automation", "monitoring"],
            "required_skills": ["terraform", "ansible", "prometheus"],
            "tags": ["infrastructure", "devops", "automation"]
        }
    ]
    
    # 6 agentes DEVOPS
    DEVOPS_AGENTS = [
        {
            "id": "ecc_deployment_specialist",
            "name": "Deployment Specialist",
            "category": ECCCategory.DEVOPS,
            "description": "Especialista em estratégias de deployment e rollout",
            "capabilities": ["plan_deployment", "blue_green", "canary_deployment"],
            "required_skills": ["deployment", "orchestration", "rollback"],
            "tags": ["devops", "deployment", "reliability"]
        },
        {
            "id": "ecc_monitoring_expert",
            "name": "Monitoring Expert",
            "category": ECCCategory.DEVOPS,
            "description": "Especialista em monitoramento e observabilidade",
            "capabilities": ["setup_monitoring", "log_aggregation", "alerting"],
            "required_skills": ["prometheus", "grafana", "elk"],
            "tags": ["monitoring", "observability", "devops"]
        },
        {
            "id": "ecc_incident_commander",
            "name": "Incident Commander",
            "category": ECCCategory.DEVOPS,
            "description": "Especialista em resposta a incidentes e SLA",
            "capabilities": ["incident_response", "postmortem", "root_cause_analysis"],
            "required_skills": ["incident-management", "runbooks"],
            "tags": ["devops", "incident", "reliability"]
        },
        {
            "id": "ecc_infrastructure_inspector",
            "name": "Infrastructure Inspector",
            "category": ECCCategory.DEVOPS,
            "description": "Inspetor de infraestrutura e compliance",
            "capabilities": ["inspect_infrastructure", "compliance_check", "audit_logs"],
            "required_skills": ["terraform-validate", "compliance-tools"],
            "tags": ["devops", "compliance", "infrastructure"]
        },
        {
            "id": "ecc_database_expert",
            "name": "Database Expert",
            "category": ECCCategory.DEVOPS,
            "description": "Especialista em otimização e gerenciamento de bancos de dados",
            "capabilities": ["optimize_database", "query_tuning", "backup_strategy"],
            "required_skills": ["sql", "database-tools", "replication"],
            "tags": ["database", "devops", "performance"]
        },
        {
            "id": "ecc_network_engineer",
            "name": "Network Engineer",
            "category": ECCCategory.DEVOPS,
            "description": "Engenheiro de rede e conectividade",
            "capabilities": ["network_design", "vpn_config", "load_balancing"],
            "required_skills": ["networking", "firewall", "dns"],
            "tags": ["network", "devops", "infrastructure"]
        }
    ]
    
    # 5 agentes DATA
    DATA_AGENTS = [
        {
            "id": "ecc_data_engineer",
            "name": "Data Engineer",
            "category": ECCCategory.DATA,
            "description": "Engenheiro de dados para pipelines e ETL",
            "capabilities": ["build_pipelines", "etl_design", "data_quality"],
            "required_skills": ["spark", "airflow", "sql"],
            "tags": ["data", "engineering", "pipelines"]
        },
        {
            "id": "ecc_ml_engineer",
            "name": "ML Engineer",
            "category": ECCCategory.DATA,
            "description": "Engenheiro de machine learning e modelos",
            "capabilities": ["develop_ml_models", "feature_engineering", "model_tuning"],
            "required_skills": ["tensorflow", "pytorch", "sklearn"],
            "tags": ["ml", "data-science", "ai"]
        },
        {
            "id": "ecc_analytics_engineer",
            "name": "Analytics Engineer",
            "category": ECCCategory.DATA,
            "description": "Engenheiro de analytics e business intelligence",
            "capabilities": ["analytics_design", "dashboards", "reporting"],
            "required_skills": ["sql", "looker", "tableau"],
            "tags": ["analytics", "bi", "reporting"]
        },
        {
            "id": "ecc_data_scientist",
            "name": "Data Scientist",
            "category": ECCCategory.DATA,
            "description": "Cientista de dados e estatístico",
            "capabilities": ["statistical_analysis", "predictive_modeling", "experimentation"],
            "required_skills": ["python", "r", "statistics"],
            "tags": ["data-science", "analytics", "research"]
        },
        {
            "id": "ecc_data_quality_manager",
            "name": "Data Quality Manager",
            "category": ECCCategory.DATA,
            "description": "Gerenciador de qualidade de dados",
            "capabilities": ["quality_assurance", "data_validation", "governance"],
            "required_skills": ["data-validation", "governance-tools"],
            "tags": ["data", "quality", "governance"]
        }
    ]
    
    # Agentes UTILITIES (7+)
    UTILITIES_AGENTS = [
        {
            "id": "ecc_task_orchestrator",
            "name": "Task Orchestrator",
            "category": ECCCategory.UTILITIES,
            "description": "Orquestrador de tarefas e workflows",
            "capabilities": ["orchestrate_tasks", "manage_queues", "handle_dependencies"],
            "required_skills": ["task-management", "workflow-engine"],
            "tags": ["orchestration", "workflow", "management"]
        },
        {
            "id": "ecc_knowledge_manager",
            "name": "Knowledge Manager",
            "category": ECCCategory.UTILITIES,
            "description": "Gerenciador de conhecimento e documentação",
            "capabilities": ["manage_knowledge", "organize_docs", "search_knowledge"],
            "required_skills": ["knowledge-base", "wiki-tools"],
            "tags": ["knowledge", "documentation", "management"]
        },
        {
            "id": "ecc_communication_specialist",
            "name": "Communication Specialist",
            "category": ECCCategory.UTILITIES,
            "description": "Especialista em comunicação e reportes",
            "capabilities": ["report_generation", "communication", "stakeholder_management"],
            "required_skills": ["reporting", "presentation"],
            "tags": ["communication", "reporting", "management"]
        },
        {
            "id": "ecc_automation_engineer",
            "name": "Automation Engineer",
            "category": ECCCategory.UTILITIES,
            "description": "Engenheiro de automação de processos",
            "capabilities": ["automate_processes", "scripting", "integration"],
            "required_skills": ["scripting", "automation-tools"],
            "tags": ["automation", "efficiency", "engineering"]
        },
        {
            "id": "ecc_quality_assurance",
            "name": "Quality Assurance",
            "category": ECCCategory.UTILITIES,
            "description": "Especialista em QA e testes",
            "capabilities": ["test_automation", "quality_check", "regression_testing"],
            "required_skills": ["testing-frameworks", "selenium"],
            "tags": ["qa", "testing", "quality"]
        },
        {
            "id": "ecc_compliance_officer",
            "name": "Compliance Officer",
            "category": ECCCategory.UTILITIES,
            "description": "Oficial de conformidade e regulamentação",
            "capabilities": ["compliance_check", "audit", "policy_enforcement"],
            "required_skills": ["compliance-frameworks", "audit-tools"],
            "tags": ["compliance", "governance", "audit"]
        },
        {
            "id": "ecc_emergency_responder",
            "name": "Emergency Responder",
            "category": ECCCategory.UTILITIES,
            "description": "Respondente a emergências e fallback specialist",
            "capabilities": ["emergency_response", "failover", "disaster_recovery"],
            "required_skills": ["disaster-recovery", "backup-systems"],
            "tags": ["emergency", "reliability", "backup"]
        }
    ]
    
    def get_all_specs(self) -> List[Dict]:
        """Retorna todas as 48 especificações de agentes"""
        all_specs = (
            self.CODE_REVIEW_AGENTS +
            self.BUILD_TOOLS_AGENTS +
            self.RESEARCH_AGENTS +
            self.ARCHITECTURE_AGENTS +
            self.DEVOPS_AGENTS +
            self.DATA_AGENTS +
            self.UTILITIES_AGENTS
        )
        return all_specs
    
    def get_specs_by_category(self, category: ECCCategory) -> List[Dict]:
        """Retorna especificações filtradas por categoria"""
        all_specs = self.get_all_specs()
        return [s for s in all_specs if s["category"] == category]


class ECCParser:
    """Parser para especificações ECC"""
    
    def __init__(self):
        self.db = ECCAgentDatabase()
        self.agents: Dict[str, ECCAgentSpec] = {}
    
    def load_from_database(self) -> int:
        """Carrega todas as 48 especificações do banco de dados"""
        specs = self.db.get_all_specs()
        
        for spec_dict in specs:
            category_str = spec_dict.pop("category")
            category = (
                ECCCategory[category_str.upper()]
                if isinstance(category_str, str)
                else category_str
            )
            
            spec = ECCAgentSpec(
                id=spec_dict["id"],
                name=spec_dict["name"],
                category=category,
                description=spec_dict["description"],
                capabilities=spec_dict.get("capabilities", []),
                required_skills=spec_dict.get("required_skills", []),
                dependencies=spec_dict.get("dependencies", []),
                tags=set(spec_dict.get("tags", []))
            )
            self.agents[spec.id] = spec
        
        return len(self.agents)
    
    def load_from_json(self, json_path: str) -> int:
        """Carrega especificações de arquivo JSON"""
        path = Path(json_path)
        if not path.exists():
            return 0
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        agents_data = data.get("agents", [])
        for agent_data in agents_data:
            try:
                spec = ECCAgentSpec(
                    id=agent_data["id"],
                    name=agent_data["name"],
                    category=ECCCategory[agent_data.get("category", "UTILITIES").upper()],
                    description=agent_data["description"],
                    capabilities=agent_data.get("capabilities", []),
                    required_skills=agent_data.get("required_skills", []),
                    dependencies=agent_data.get("dependencies", []),
                    tags=set(agent_data.get("tags", []))
                )
                self.agents[spec.id] = spec
            except (KeyError, ValueError) as e:
                print(f"Erro ao parsear agente {agent_data.get('id')}: {e}")
        
        return len(self.agents)
    
    def get_agent(self, agent_id: str) -> Optional[ECCAgentSpec]:
        """Obtém especificação de um agente"""
        return self.agents.get(agent_id)
    
    def get_agents_by_category(self, category: ECCCategory) -> List[ECCAgentSpec]:
        """Retorna agentes filtrados por categoria"""
        return [a for a in self.agents.values() if a.category == category]
    
    def get_agents_by_capability(self, capability: str) -> List[ECCAgentSpec]:
        """Busca agentes por capacidade"""
        return [
            a for a in self.agents.values()
            if capability.lower() in [c.lower() for c in a.capabilities]
        ]
    
    def get_agents_by_tag(self, tag: str) -> List[ECCAgentSpec]:
        """Busca agentes por tag"""
        return [
            a for a in self.agents.values()
            if tag.lower() in [t.lower() for t in a.tags]
        ]
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas dos agentes carregados"""
        by_category = {}
        total_capabilities = set()
        total_tags = set()
        
        for agent in self.agents.values():
            category_name = agent.category.value
            by_category[category_name] = by_category.get(category_name, 0) + 1
            total_capabilities.update(agent.capabilities)
            total_tags.update(agent.tags)
        
        return {
            "total_agents": len(self.agents),
            "by_category": by_category,
            "total_unique_capabilities": len(total_capabilities),
            "total_unique_tags": len(total_tags),
            "average_capabilities_per_agent": sum(
                len(a.capabilities) for a in self.agents.values()
            ) / len(self.agents) if self.agents else 0
        }
    
    def export_as_json(self, output_path: str) -> None:
        """Exporta agentes como JSON"""
        data = {
            "total_agents": len(self.agents),
            "agents": [
                {
                    **asdict(agent),
                    "category": agent.category.value,
                    "tags": list(agent.tags)
                }
                for agent in self.agents.values()
            ]
        }
        
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def validate_dependencies(self) -> Dict[str, List[str]]:
        """Valida se todas as dependências existem"""
        issues = {}
        
        for agent_id, agent in self.agents.items():
            missing_deps = []
            for dep in agent.dependencies:
                if dep not in self.agents:
                    missing_deps.append(dep)
            
            if missing_deps:
                issues[agent_id] = missing_deps
        
        return issues


if __name__ == "__main__":
    parser = ECCParser()
    
    # Carrega banco de dados
    count = parser.load_from_database()
    print(f"[OK] {count} agentes ECC carregados")
    
    # Mostra estatísticas
    stats = parser.get_statistics()
    print(f"\n[STATS] Estatísticas:")
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Valida dependências
    issues = parser.validate_dependencies()
    if issues:
        print(f"\n[WARN] {len(issues)} problemas de dependência encontrados")
    else:
        print(f"\n[OK] Todas as dependências sao validas")
