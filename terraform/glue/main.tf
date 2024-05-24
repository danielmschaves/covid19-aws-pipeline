provider "aws" {
  region = var.AWS_REGION
}

resource "aws_glue_job" "etl_job" {
  name       = "covid19-etl-job"
  role_arn   = var.GLUE_ROLE_ARN
  command {
    name            = "glueetl"
    script_location = "s3://${var.S3_BUCKET}/transform/transform.py"
    python_version  = "3"
  }

  default_arguments = {
    "--job-language" = "python"
    "--TempDir" = "s3://${var.S3_BUCKET}/temp/"
    "--extra-jars" = "s3://${var.S3_BUCKET}/libs/athena-jdbc-3.2.0-with-dependencies.jar"
    "--AWS_REGION" = var.AWS_REGION
    "--ATHENA_DATABASE" = var.ATHENA_DATABASE
    "--ATHENA_OUTPUT_BUCKET" = var.ATHENA_OUTPUT_BUCKET
    "--REDSHIFT_USER" = var.REDSHIFT_USER
    "--REDSHIFT_PASSWORD" = var.REDSHIFT_PASSWORD
    "--REDSHIFT_JDBC_URL" = var.REDSHIFT_JDBC_URL
    "--REDSHIFT_DATABASE" = var.REDSHIFT_DATABASE
    "--REDSHIFT_SCHEMA" = var.REDSHIFT_SCHEMA
    "--enable-glue-datacatalog" = "true"
  }

  max_retries = 1
  glue_version = "3.0"
  number_of_workers = 2
  worker_type = "G.1X"
}

resource "aws_iam_role_policy" "glue_s3_policy" {
  name = "GlueS3AccessPolicy"
  role = var.GLUE_ROLE_NAME 

  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        Resource = [
          "arn:aws:s3:::${var.S3_BUCKET}",
          "arn:aws:s3:::${var.S3_BUCKET}/libs/*",
          "arn:aws:s3:::${var.S3_BUCKET}/transform/*"
        ]
      }
    ]
  })
}

resource "null_resource" "run_glue_job" {
  depends_on = [aws_glue_job.etl_job, aws_iam_role_policy.glue_s3_policy]

  provisioner "local-exec" {
    command = "aws glue start-job-run --job-name ${aws_glue_job.etl_job.name}"
  }
}
