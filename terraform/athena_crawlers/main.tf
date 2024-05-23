provider "aws" {
  access_key = var.AWS_ACCESS_KEY
  secret_key = var.AWS_SECRET_KEY
  region     = var.AWS_REGION
}

resource "aws_s3_bucket" "athena_query_results" {
  bucket = "de-project-covid19-athena-query-results-197398273774"

  tags = {
    Name        = "AthenaQueryResults"
    Environment = "Dev"
  }
}

resource "aws_s3_bucket_versioning" "athena_query_results_versioning" {
  bucket = aws_s3_bucket.athena_query_results.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_glue_catalog_database" "covid19_data_br" {
  name = "covid19_data_br"
}

resource "aws_glue_crawler" "boletim" {
  name          = "boletim"
  role          = "arn:aws:iam::${var.AWS_ACCOUNT_ID}:role/s3-glue-role"
  database_name = aws_glue_catalog_database.covid19_data_br.name
  s3_target {
    path = "s3://de-project-covid19-197398273774/boletim/"
  }
}

resource "aws_glue_crawler" "caso" {
  name          = "caso"
  role          = "arn:aws:iam::${var.AWS_ACCOUNT_ID}:role/s3-glue-role"
  database_name = aws_glue_catalog_database.covid19_data_br.name
  s3_target {
    path = "s3://de-project-covid19-197398273774/caso/"
  }
}

resource "aws_glue_crawler" "caso_full" {
  name          = "caso_full"
  role          = "arn:aws:iam::${var.AWS_ACCOUNT_ID}:role/s3-glue-role"
  database_name = aws_glue_catalog_database.covid19_data_br.name
  s3_target {
    path = "s3://de-project-covid19-197398273774/caso_full/"
  }
}

resource "aws_glue_crawler" "obito_cartorio" {
  name          = "obito_cartorio"
  role          = "arn:aws:iam::${var.AWS_ACCOUNT_ID}:role/s3-glue-role"
  database_name = aws_glue_catalog_database.covid19_data_br.name
  s3_target {
    path = "s3://de-project-covid19-197398273774/obito_cartorio/"
  }
}
