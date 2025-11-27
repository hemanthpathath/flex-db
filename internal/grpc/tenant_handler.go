package grpc

import (
	"context"
	"errors"

	pb "github.com/hemanthpathath/flexy-db/api/proto"
	"github.com/hemanthpathath/flexy-db/internal/repository"
	"github.com/hemanthpathath/flexy-db/internal/service"
	"google.golang.org/grpc/codes"
	"google.golang.org/grpc/status"
	"google.golang.org/protobuf/types/known/timestamppb"
)

// TenantHandler implements the TenantService gRPC server
type TenantHandler struct {
	pb.UnimplementedTenantServiceServer
	svc *service.TenantService
}

// NewTenantHandler creates a new TenantHandler
func NewTenantHandler(svc *service.TenantService) *TenantHandler {
	return &TenantHandler{svc: svc}
}

// CreateTenant creates a new tenant
func (h *TenantHandler) CreateTenant(ctx context.Context, req *pb.CreateTenantRequest) (*pb.CreateTenantResponse, error) {
	tenant, err := h.svc.Create(ctx, req.Slug, req.Name)
	if err != nil {
		return nil, mapError(err)
	}

	return &pb.CreateTenantResponse{
		Tenant: tenantToProto(tenant),
	}, nil
}

// GetTenant retrieves a tenant by ID
func (h *TenantHandler) GetTenant(ctx context.Context, req *pb.GetTenantRequest) (*pb.GetTenantResponse, error) {
	tenant, err := h.svc.GetByID(ctx, req.Id)
	if err != nil {
		return nil, mapError(err)
	}

	return &pb.GetTenantResponse{
		Tenant: tenantToProto(tenant),
	}, nil
}

// UpdateTenant updates an existing tenant
func (h *TenantHandler) UpdateTenant(ctx context.Context, req *pb.UpdateTenantRequest) (*pb.UpdateTenantResponse, error) {
	tenant, err := h.svc.Update(ctx, req.Id, req.Slug, req.Name, req.Status)
	if err != nil {
		return nil, mapError(err)
	}

	return &pb.UpdateTenantResponse{
		Tenant: tenantToProto(tenant),
	}, nil
}

// DeleteTenant deletes a tenant
func (h *TenantHandler) DeleteTenant(ctx context.Context, req *pb.DeleteTenantRequest) (*pb.DeleteTenantResponse, error) {
	if err := h.svc.Delete(ctx, req.Id); err != nil {
		return nil, mapError(err)
	}

	return &pb.DeleteTenantResponse{}, nil
}

// ListTenants retrieves tenants with pagination
func (h *TenantHandler) ListTenants(ctx context.Context, req *pb.ListTenantsRequest) (*pb.ListTenantsResponse, error) {
	var pageSize int32 = 10
	var pageToken string

	if req.Pagination != nil {
		if req.Pagination.PageSize > 0 {
			pageSize = req.Pagination.PageSize
		}
		pageToken = req.Pagination.PageToken
	}

	tenants, result, err := h.svc.List(ctx, pageSize, pageToken)
	if err != nil {
		return nil, mapError(err)
	}

	pbTenants := make([]*pb.Tenant, len(tenants))
	for i, t := range tenants {
		pbTenants[i] = tenantToProto(t)
	}

	return &pb.ListTenantsResponse{
		Tenants: pbTenants,
		Pagination: &pb.PaginationResponse{
			NextPageToken: result.NextPageToken,
			TotalCount:    int32(result.TotalCount),
		},
	}, nil
}

// tenantToProto converts a repository.Tenant to pb.Tenant
func tenantToProto(t *repository.Tenant) *pb.Tenant {
	return &pb.Tenant{
		Id:        t.ID,
		Slug:      t.Slug,
		Name:      t.Name,
		Status:    t.Status,
		CreatedAt: timestamppb.New(t.CreatedAt),
		UpdatedAt: timestamppb.New(t.UpdatedAt),
	}
}

// mapError converts domain errors to gRPC status errors
func mapError(err error) error {
	if errors.Is(err, repository.ErrNotFound) {
		return status.Error(codes.NotFound, err.Error())
	}
	// Check for validation errors
	if err != nil && (containsAny(err.Error(), "required", "invalid")) {
		return status.Error(codes.InvalidArgument, err.Error())
	}
	return status.Error(codes.Internal, err.Error())
}

// containsAny checks if the string contains any of the substrings
func containsAny(s string, substrs ...string) bool {
	for _, substr := range substrs {
		if contains(s, substr) {
			return true
		}
	}
	return false
}

func contains(s, substr string) bool {
	return len(s) >= len(substr) && (s == substr || len(s) > 0 && containsAt(s, substr))
}

func containsAt(s, substr string) bool {
	for i := 0; i <= len(s)-len(substr); i++ {
		if s[i:i+len(substr)] == substr {
			return true
		}
	}
	return false
}
