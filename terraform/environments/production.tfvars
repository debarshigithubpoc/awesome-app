# Production Environment Configuration

environment = "production"
cluster_name = "my-app-prod-eks"
app_name = "my-app"

aws_region = "us-east-1"
kubernetes_version = "1.31"

# Production-ready resources
node_instance_types = ["t3.large"]
node_group_min_size = 3
node_group_max_size = 10
node_group_desired_size = 3

tags = {
  Environment = "production"
  ManagedBy   = "terraform"
  Project     = "my-app"
  CostCenter  = "engineering"
}
