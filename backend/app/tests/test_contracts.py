"""
Tests for contract endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.db.models.contract import Contract, ContractStatus


class TestContracts:
    """Tests for contract endpoints."""
    
    def test_create_contract(self, client: TestClient, auth_headers, db):
        """Test contract creation."""
        response = client.post(
            "/api/v1/contracts",
            headers=auth_headers,
            json={
                "title": "Test Contract",
                "description": "A test contract",
                "content": "This is the contract content..."
            }
        )
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Contract"
        assert data["status"] == "draft"
        assert data["version"] == 1
    
    def test_list_contracts(self, client: TestClient, auth_headers, db, test_user):
        """Test listing contracts."""
        # Create a contract first
        contract = Contract(
            title="List Test Contract",
            content="Content...",
            created_by=test_user.id,
            status=ContractStatus.DRAFT
        )
        db.add(contract)
        db.commit()
        
        response = client.get("/api/v1/contracts", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_contract(self, client: TestClient, auth_headers, db, test_user):
        """Test getting a single contract."""
        contract = Contract(
            title="Get Test Contract",
            content="Content...",
            created_by=test_user.id,
            status=ContractStatus.DRAFT
        )
        db.add(contract)
        db.commit()
        
        response = client.get(f"/api/v1/contracts/{contract.id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Get Test Contract"
    
    def test_get_contract_not_found(self, client: TestClient, auth_headers):
        """Test getting nonexistent contract."""
        from uuid import uuid4
        response = client.get(f"/api/v1/contracts/{uuid4()}", headers=auth_headers)
        assert response.status_code == 404
    
    def test_update_contract(self, client: TestClient, auth_headers, db, test_user):
        """Test updating a contract."""
        contract = Contract(
            title="Update Test Contract",
            content="Original content",
            created_by=test_user.id,
            status=ContractStatus.DRAFT
        )
        db.add(contract)
        db.commit()
        
        response = client.put(
            f"/api/v1/contracts/{contract.id}",
            headers=auth_headers,
            json={"title": "Updated Title", "content": "Updated content"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["content"] == "Updated content"
    
    def test_submit_for_review(self, client: TestClient, auth_headers, db, test_user):
        """Test submitting contract for review."""
        contract = Contract(
            title="Submit Test Contract",
            content="Content...",
            created_by=test_user.id,
            status=ContractStatus.DRAFT
        )
        db.add(contract)
        db.commit()
        
        response = client.post(
            f"/api/v1/contracts/{contract.id}/submit",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "pending_review"
    
    def test_approve_contract(self, client: TestClient, reviewer_headers, db, test_user):
        """Test approving a contract as reviewer."""
        contract = Contract(
            title="Approve Test Contract",
            content="Content...",
            created_by=test_user.id,
            status=ContractStatus.PENDING_REVIEW
        )
        db.add(contract)
        db.commit()
        
        response = client.post(
            f"/api/v1/contracts/{contract.id}/approve",
            headers=reviewer_headers,
            json={"notes": "Looks good"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "approved"
    
    def test_reject_contract(self, client: TestClient, reviewer_headers, db, test_user):
        """Test rejecting a contract as reviewer."""
        contract = Contract(
            title="Reject Test Contract",
            content="Content...",
            created_by=test_user.id,
            status=ContractStatus.PENDING_REVIEW
        )
        db.add(contract)
        db.commit()
        
        response = client.post(
            f"/api/v1/contracts/{contract.id}/reject",
            headers=reviewer_headers,
            json={"reason": "Needs revision"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "rejected"
        assert data["rejection_reason"] == "Needs revision"
    
    def test_create_new_version(self, client: TestClient, auth_headers, db, test_user):
        """Test creating a new version of a contract."""
        contract = Contract(
            title="Version Test Contract",
            content="Original content",
            created_by=test_user.id,
            status=ContractStatus.APPROVED,
            version=1
        )
        db.add(contract)
        db.commit()
        
        response = client.post(
            f"/api/v1/contracts/{contract.id}/new-version",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["version"] == 2
        assert data["status"] == "draft"
    
    def test_archive_contract(self, client: TestClient, auth_headers, db, test_user):
        """Test archiving a contract."""
        contract = Contract(
            title="Archive Test Contract",
            content="Content...",
            created_by=test_user.id,
            status=ContractStatus.DRAFT
        )
        db.add(contract)
        db.commit()
        
        response = client.delete(
            f"/api/v1/contracts/{contract.id}",
            headers=auth_headers
        )
        assert response.status_code == 204
    
    def test_unauthorized_access(self, client: TestClient):
        """Test accessing contracts without authentication."""
        response = client.get("/api/v1/contracts")
        assert response.status_code == 403
