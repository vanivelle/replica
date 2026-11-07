"""Tests for REPLICA identity module."""

from __future__ import annotations

import pytest

from openjarvis.identity.replica import ReplicaIdentity, get_replica_identity


def test_replica_identity_creation():
    """Test REPLICA identity can be created with default values."""
    replica = ReplicaIdentity.create_default()
    
    assert replica.name == "REPLICA"
    assert replica.type == "Sovereign AI Assistant"
    assert replica.status == "operational"
    assert replica.version == "1.0.0"
    assert replica.repositories_count == 46
    assert replica.agents_count == 71


def test_replica_identity_to_dict():
    """Test REPLICA identity can be converted to dictionary."""
    replica = ReplicaIdentity.create_default()
    data = replica.to_dict()
    
    assert isinstance(data, dict)
    assert data["name"] == "REPLICA"
    assert data["type"] == "Sovereign AI Assistant"
    assert "specialties" in data
    assert len(data["specialties"]) > 0
    assert "lore" in data


def test_replica_system_prompt():
    """Test REPLICA system prompt is properly formatted."""
    replica = ReplicaIdentity.create_default()
    prompt = replica.system_prompt
    
    assert isinstance(prompt, str)
    assert "REPLICA" in prompt
    assert "alienígena soberano" in prompt
    assert "46 repositórios" in prompt
    assert "71 agentes" in prompt
    assert "Ponytail" in prompt


def test_replica_lore():
    """Test REPLICA lore is available."""
    replica = ReplicaIdentity.create_default()
    lore = replica.lore
    
    assert isinstance(lore, str)
    assert "REPLICA" in lore
    assert "World Trigger" in lore
    assert "OpenJarvis" in lore


def test_get_replica_identity_singleton():
    """Test get_replica_identity returns singleton instance."""
    replica1 = get_replica_identity()
    replica2 = get_replica_identity()
    
    assert replica1 is replica2
    assert replica1.name == "REPLICA"


def test_replica_specialties():
    """Test REPLICA has proper specialties."""
    replica = ReplicaIdentity.create_default()
    
    assert replica.specialties is not None
    assert "tactical analysis" in replica.specialties
    assert "AI engineering" in replica.specialties
    assert "intelligent routing" in replica.specialties
