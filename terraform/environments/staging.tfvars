# Staging Environment Configuration

environment = "staging"
cluster_name = "my-app-staging-eks"
app_name = "my-app"

aws_region = "us-east-1"
kubernetes_version = "1.31"

# Medium resources for staging
node_instance_types = ["t3.medium"]
node_group_min_size = 2
node_group_max_size = 5
node_group_desired_size = 2

tags = {
  Environment = "staging"
  ManagedBy   = "terraform"
  Project     = "my-app"
}
