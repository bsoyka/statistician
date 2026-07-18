terraform {
  backend "s3" {
    bucket = "bsoyka-tfstate"
    key    = "statistician.tfstate"
    region = "us-east-1"
  }
}
