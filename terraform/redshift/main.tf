provider "aws" {
  region = var.AWS_REGION
}

resource "aws_redshift_subnet_group" "default" {
  name       = "default"
  subnet_ids = var.SUBNET_IDS

  tags = {
    Name = "default"
  }
}

resource "aws_security_group" "redshift_sg" {
  name        = "redshift-security-group"
  description = "Redshift security group"
  vpc_id      = var.VPC_ID

  ingress {
    from_port   = 5439
    to_port     = 5439
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "redshift-security-group"
  }
}

resource "aws_redshift_cluster" "redshift" {
  cluster_identifier      = "covid19-redshift-cluster"
  database_name           = var.REDSHIFT_DBNAME
  master_username         = var.REDSHIFT_USER
  master_password         = var.REDSHIFT_PASSWORD
  node_type               = "dc2.large"
  cluster_type            = "single-node"
  port                    = 5439
  cluster_subnet_group_name = aws_redshift_subnet_group.default.name
  vpc_security_group_ids  = [aws_security_group.redshift_sg.id]

  tags = {
    Name = "covid19-redshift-cluster"
  }
}

# Redshift database and schema creation
resource "null_resource" "redshift_init" {
  provisioner "local-exec" {
    command = <<EOT
      PGPASSWORD='${var.REDSHIFT_PASSWORD}' psql -h ${aws_redshift_cluster.redshift.endpoint} -U ${var.REDSHIFT_USER} -d ${var.REDSHIFT_DBNAME} -c "CREATE SCHEMA IF NOT EXISTS ${var.REDSHIFT_SCHEMA};"
    EOT
    environment = {
      PATH = "${path.module}/bin:${env.PATH}"
    }
  }

  depends_on = [aws_redshift_cluster.redshift]
}
