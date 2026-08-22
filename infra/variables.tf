variable "aws_region" {
  description = "AWS region for all resources"
  type        = string
  default     = "eu-west-1"
}

variable "aws_account_id" {
  description = "AWS account ID resources are deployed into"
  type        = string
  default     = "861580917950"
}

variable "github_repository" {
  description = "GitHub repository URL backing the Amplify app"
  type        = string
  default     = "https://github.com/akin-mustapha/plant-catalog"
}

variable "amplify_branch_name" {
  description = "Git branch Amplify builds and deploys from"
  type        = string
  default     = "main"
}

variable "github_access_token" {
  description = "GitHub personal access token granting Amplify read access to the repository. Supply via TF_VAR_github_access_token or a gitignored .tfvars file — never commit it."
  type        = string
  sensitive   = true
}
