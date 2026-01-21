[
    {
        "name": "build_sitemaps",
		"image": "${ecr_image_url}",
        "assignPublicIp": false,
		"networkMode": "awsvpc",
        "entryPoint": [
            "sh",
            "/app/tasks/build_sitemaps.sh"
        ],
		"logConfiguration": {
			"logDriver": "awslogs",
			"options": {
                "awslogs-group": "${log_group}",
                "awslogs-region": "${region}",
                "awslogs-stream-prefix": "ecs"
			}
		},
        "environment": [
            {
                "name": "ALLOWED_HOSTS",
                "value": "*"
            },
            {
                "name": "AWS_SECRET_ACCESS_KEY",
                "value": "${SETTINGS_AWS_SECRET_ACCESS_KEY}"
            },
            {
                "name": "OPENSEARCH_ENDPOINT",
                "value": "${SETTINGS_OPENSEARCH_ENDPOINT}"
            },
            {
                "name": "OPENSEARCH_ENDPOINT",
                "value": "${SETTINGS_OPENSEARCH_ENDPOINT}"
            },
            {
                "name": "OPENSEARCH_SECRET",
                "value": "${SETTINGS_OPENSEARCH_SECRET}"
            },
                        {
                "name": "OPENSEARCH_KEY",
                "value": "${SETTINGS_OPENSEARCH_KEY}"
            },
            {
                "name": "AWS_ACCESS_KEY_ID",
                "value": "${SETTINGS_AWS_ACCESS_KEY_ID}"
            },
            {
                "name": "AWS_REGION",
                "value": "${region}"
            },
            {
                "name": "AWS_STATIC_BUCKET_NAME",
                "value": "${SETTINGS_AWS_STATIC_BUCKET_NAME}"
            },
            {
                "name": "BASE_URL",
                "value": "${SETTINGS_BASE_URL}"
            },
            {
                "name": "DATABASE_URL",
                "value": "${SETTINGS_DATABASE_URL}"
            },
            {
                "name": "SECRET_KEY",
                "value": "${SETTINGS_SECRET_KEY}"
            },
            {
                "name": "AWS_S3_CUSTOM_DOMAIN", 
                "value": "${assets_url}"
            },
            {
                "name": "AWS_STORAGE_BUCKET_NAME", 
                "value": "${assets_s3_bucket}"
            },
            {
                "name": "CORS_ALLOWED_ORIGINS",
                "value": "${SETTINGS_CORS_ALLOWED_ORIGINS}"
            }
        ],
        "secrets": []
    }
]
