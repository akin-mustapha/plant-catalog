module "notifications" {
  source = "./modules/notifications"

  aws_region     = var.aws_region
  aws_account_id = var.aws_account_id
}
