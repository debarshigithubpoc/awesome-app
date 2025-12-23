# Development Environment Configuration

environment = "dev"
cluster_name = "my-app-dev-eks"
app_name = "my-app"

aws_region = "us-east-1"
kubernetes_version = "1.31"

# Smaller resources for dev
node_instance_types = ["t3.small"]
node_group_min_size = 1
node_group_max_size = 3
node_group_desired_size = 1

tags = {
  Environment = "dev"
  ManagedBy   = "terraform"
  Project     = "my-app"
}
