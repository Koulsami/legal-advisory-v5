#!/bin/bash
#
# Legal Advisory System v5.0 - Deployment Script
# Automates deployment process for Docker and manual deployments
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo ""
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ $1${NC}"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed"
        return 1
    else
        print_success "$1 is installed"
        return 0
    fi
}

# Main script
print_header "Legal Advisory System v5.0 - Deployment"

# Check deployment method
echo "Select deployment method:"
echo "  1. Docker Compose (Recommended)"
echo "  2. Docker (Simple)"
echo "  3. Manual (Direct Python)"
echo ""
read -p "Enter choice (1-3): " DEPLOY_METHOD

case $DEPLOY_METHOD in
    1)
        print_header "Docker Compose Deployment"

        # Check prerequisites
        print_info "Checking prerequisites..."
        check_command docker || exit 1
        check_command docker-compose || exit 1

        # Check for .env file
        if [ ! -f .env ]; then
            print_warning ".env file not found"
            read -p "Do you want to create one from .env.example? (y/n): " CREATE_ENV
            if [ "$CREATE_ENV" = "y" ]; then
                cp .env.example .env
                print_success "Created .env file"
                print_warning "Please edit .env with your configuration before continuing"
                print_info "Press Enter when ready..."
                read
            else
                print_error "Deployment cancelled - .env file required"
                exit 1
            fi
        fi

        # Ask about services
        print_info "Which services do you want to deploy?"
        echo "  1. API only (no database/cache)"
        echo "  2. API + PostgreSQL"
        echo "  3. API + Redis"
        echo "  4. Full stack (API + PostgreSQL + Redis + Nginx)"
        echo ""
        read -p "Enter choice (1-4): " SERVICE_CHOICE

        # Build Docker Compose command
        COMPOSE_CMD="docker-compose"

        case $SERVICE_CHOICE in
            2) COMPOSE_CMD="$COMPOSE_CMD --profile with-db" ;;
            3) COMPOSE_CMD="$COMPOSE_CMD --profile with-cache" ;;
            4) COMPOSE_CMD="$COMPOSE_CMD --profile with-db --profile with-cache --profile with-nginx" ;;
        esac

        # Stop existing containers
        print_info "Stopping existing containers..."
        $COMPOSE_CMD down || true

        # Build and start
        print_info "Building and starting services..."
        $COMPOSE_CMD up -d --build

        # Wait for services to be ready
        print_info "Waiting for services to start..."
        sleep 5

        # Health check
        print_info "Performing health check..."
        for i in {1..30}; do
            if curl -f http://localhost:8000/health &> /dev/null; then
                print_success "API is healthy!"
                break
            fi
            if [ $i -eq 30 ]; then
                print_error "Health check failed after 30 attempts"
                print_info "Checking logs..."
                docker-compose logs api
                exit 1
            fi
            sleep 1
        done

        # Show status
        print_header "Deployment Successful!"
        print_success "Services are running"
        echo ""
        print_info "Service Status:"
        docker-compose ps
        echo ""
        print_info "Access Points:"
        echo "  - API Health: http://localhost:8000/health"
        echo "  - API Docs: http://localhost:8000/docs"
        echo "  - ReDoc: http://localhost:8000/redoc"
        echo ""
        print_info "Useful Commands:"
        echo "  - View logs: docker-compose logs -f api"
        echo "  - Stop services: docker-compose down"
        echo "  - Restart: docker-compose restart"
        ;;

    2)
        print_header "Docker Simple Deployment"

        # Check prerequisites
        print_info "Checking prerequisites..."
        check_command docker || exit 1

        # Build image
        print_info "Building Docker image..."
        docker build -t legal-advisory:v5.0 .

        # Stop existing container
        print_info "Stopping existing container..."
        docker stop legal-advisory 2>/dev/null || true
        docker rm legal-advisory 2>/dev/null || true

        # Run container
        print_info "Starting container..."
        docker run -d \
            --name legal-advisory \
            -p 8000:8000 \
            -e ENVIRONMENT=production \
            -e LOG_LEVEL=info \
            legal-advisory:v5.0

        # Wait and health check
        print_info "Waiting for service to start..."
        sleep 5

        for i in {1..30}; do
            if curl -f http://localhost:8000/health &> /dev/null; then
                print_success "API is healthy!"
                break
            fi
            if [ $i -eq 30 ]; then
                print_error "Health check failed"
                docker logs legal-advisory
                exit 1
            fi
            sleep 1
        done

        print_header "Deployment Successful!"
        print_info "Container is running"
        echo ""
        print_info "Access Points:"
        echo "  - API Health: http://localhost:8000/health"
        echo "  - API Docs: http://localhost:8000/docs"
        echo ""
        print_info "Useful Commands:"
        echo "  - View logs: docker logs -f legal-advisory"
        echo "  - Stop: docker stop legal-advisory"
        echo "  - Restart: docker restart legal-advisory"
        ;;

    3)
        print_header "Manual Deployment"

        # Check prerequisites
        print_info "Checking prerequisites..."
        check_command python3.12 || check_command python3 || exit 1
        check_command pip || exit 1

        # Create virtual environment
        if [ ! -d "venv" ]; then
            print_info "Creating virtual environment..."
            python3.12 -m venv venv || python3 -m venv venv
            print_success "Virtual environment created"
        fi

        # Activate virtual environment
        print_info "Activating virtual environment..."
        source venv/bin/activate

        # Install dependencies
        print_info "Installing dependencies..."
        pip install -r requirements.txt

        # Install Gunicorn
        print_info "Installing Gunicorn..."
        pip install gunicorn

        # Check for .env
        if [ ! -f .env ]; then
            print_warning ".env file not found - creating from template"
            cp .env.example .env
            print_info "Please configure .env before running"
        fi

        # Set Python path
        export PYTHONPATH="${PYTHONPATH}:$(pwd)"

        print_header "Setup Complete!"
        print_success "Environment is ready"
        echo ""
        print_info "To start the server:"
        echo "  source venv/bin/activate"
        echo "  export PYTHONPATH=\"\${PYTHONPATH}:\$(pwd)\""
        echo "  gunicorn backend.api.routes:app \\"
        echo "    --workers 4 \\"
        echo "    --worker-class uvicorn.workers.UvicornWorker \\"
        echo "    --bind 0.0.0.0:8000"
        echo ""
        print_info "Or use the provided script:"
        echo "  ./scripts/start.sh"
        ;;

    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

print_header "Deployment Complete!"
print_success "Legal Advisory System v5.0 is running"
