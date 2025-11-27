package service

import (
	"context"
	"fmt"

	"github.com/hemanthpathath/flexy-db/internal/repository"
)

// RelationshipService handles relationship business logic
type RelationshipService struct {
	repo repository.RelationshipRepository
}

// NewRelationshipService creates a new RelationshipService
func NewRelationshipService(repo repository.RelationshipRepository) *RelationshipService {
	return &RelationshipService{repo: repo}
}

// Create creates a new relationship
func (s *RelationshipService) Create(ctx context.Context, tenantID, sourceNodeID, targetNodeID, relType, data string) (*repository.Relationship, error) {
	if tenantID == "" {
		return nil, fmt.Errorf("tenant_id is required")
	}
	if sourceNodeID == "" {
		return nil, fmt.Errorf("source_node_id is required")
	}
	if targetNodeID == "" {
		return nil, fmt.Errorf("target_node_id is required")
	}
	if relType == "" {
		return nil, fmt.Errorf("relationship_type is required")
	}

	rel := &repository.Relationship{
		TenantID:         tenantID,
		SourceNodeID:     sourceNodeID,
		TargetNodeID:     targetNodeID,
		RelationshipType: relType,
		Data:             data,
	}

	return s.repo.Create(ctx, rel)
}

// GetByID retrieves a relationship by ID
func (s *RelationshipService) GetByID(ctx context.Context, tenantID, id string) (*repository.Relationship, error) {
	if id == "" {
		return nil, fmt.Errorf("id is required")
	}
	if tenantID == "" {
		return nil, fmt.Errorf("tenant_id is required")
	}
	return s.repo.GetByID(ctx, tenantID, id)
}

// Update updates an existing relationship
func (s *RelationshipService) Update(ctx context.Context, tenantID, id, relType, data string) (*repository.Relationship, error) {
	if id == "" {
		return nil, fmt.Errorf("id is required")
	}
	if tenantID == "" {
		return nil, fmt.Errorf("tenant_id is required")
	}

	rel, err := s.repo.GetByID(ctx, tenantID, id)
	if err != nil {
		return nil, err
	}

	if relType != "" {
		rel.RelationshipType = relType
	}
	if data != "" {
		rel.Data = data
	}

	return s.repo.Update(ctx, rel)
}

// Delete deletes a relationship
func (s *RelationshipService) Delete(ctx context.Context, tenantID, id string) error {
	if id == "" {
		return fmt.Errorf("id is required")
	}
	if tenantID == "" {
		return fmt.Errorf("tenant_id is required")
	}
	return s.repo.Delete(ctx, tenantID, id)
}

// List retrieves relationships with pagination and optional filtering
func (s *RelationshipService) List(ctx context.Context, tenantID, sourceNodeID, targetNodeID, relType string, pageSize int32, pageToken string) ([]*repository.Relationship, *repository.ListResult, error) {
	if tenantID == "" {
		return nil, nil, fmt.Errorf("tenant_id is required")
	}

	opts := repository.ListOptions{
		PageSize:  int(pageSize),
		PageToken: pageToken,
	}
	return s.repo.List(ctx, tenantID, sourceNodeID, targetNodeID, relType, opts)
}
