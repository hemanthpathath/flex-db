# flex-db Go Backend Dockerfile
#
# Multi-stage build for optimized image size and security
#

# Stage 1: Build stage
FROM golang:1.24-alpine AS builder

WORKDIR /app

# Install build dependencies
RUN apk add --no-cache git

# Copy go.mod and go.sum first for better caching
COPY go.mod go.sum ./

# Download dependencies
RUN go mod download

# Copy source code
COPY . .

# Build the application
RUN CGO_ENABLED=0 GOOS=linux go build -a -installsuffix cgo -o dbaas-server ./cmd/dbaas-server

# Stage 2: Production stage
FROM alpine:3.19

WORKDIR /app

# Install ca-certificates for TLS connections
RUN apk add --no-cache ca-certificates

# Create a non-root user for security
RUN adduser -D -g '' appuser

# Copy the binary from builder stage
COPY --from=builder /app/dbaas-server .

# Switch to non-root user
USER appuser

# Default environment variables (can be overridden at runtime)
ENV DB_HOST=localhost \
    DB_PORT=5432 \
    DB_USER=postgres \
    DB_NAME=dbaas \
    DB_SSL_MODE=disable \
    GRPC_PORT=50051

# Expose the gRPC port
EXPOSE 50051

# Run the application
CMD ["./dbaas-server"]
