locals {
  lambda_sources = {
    public_stats = {
      handler_dir = "${path.module}/../funcs/public_stats"
    }
    public_facts = {
      handler_dir = "${path.module}/../funcs/public_facts"
    }
    private_stats = {
      handler_dir = "${path.module}/../funcs/private_stats"
    }
  }

  lambda_source_hashes = {
    for name, cfg in local.lambda_sources :
    name => sha256(join("", concat(
      [
        filesha256("${cfg.handler_dir}/handler.py"),
      ],
      [
        filesha256("${path.module}/../funcs/common/__init__.py"),
        filesha256("${path.module}/../funcs/common/response.py"),
        filesha256("${path.module}/../funcs/common/stats_table.py"),
      ]
    )))
  }
}

resource "terraform_data" "package_lambda" {
  for_each = local.lambda_sources

  triggers_replace = [
    local.lambda_source_hashes[each.key]
  ]

  provisioner "local-exec" {
    command     = <<-EOT
      set -euo pipefail
      rm -rf "${path.module}/../build/${each.key}"
      mkdir -p "${path.module}/../build/${each.key}"
      cp "${each.value.handler_dir}/handler.py" "${path.module}/../build/${each.key}/handler.py"
      cp -R "${path.module}/../funcs/common" "${path.module}/../build/${each.key}/common"
    EOT
    interpreter = ["/bin/bash", "-c"]
  }
}

data "archive_file" "lambda_zip" {
  for_each = local.lambda_sources

  type        = "zip"
  source_dir  = "${path.module}/../build/${each.key}"
  output_path = "${path.module}/../build/${each.key}.zip"

  depends_on = [terraform_data.package_lambda]
}
