resource "aws_eks_cluster" "flowsale_cluster" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks_role.arn

  vpc_config {
    subnet_ids         = var.subnet_ids
    security_group_ids = [aws_security_group.eks_sg.id]
  }

  enabled_cluster_log_types = ["api", "audit", "authenticator"]
}

resource "aws_eks_node_group" "flowsale_nodes" {
  cluster_name    = aws_eks_cluster.flowsale_cluster.name
  node_group_name = "${var.cluster_name}-node-group"
  node_role_arn   = aws_iam_role.node_group_role.arn
  subnet_ids      = var.subnet_ids
  instance_types  = ["t3.medium"]

  scaling_config {
    desired_size = 3
    max_size     = 6
    min_size     = 3
  }

  update_config {
    max_unavailable = 1
  }

  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}
