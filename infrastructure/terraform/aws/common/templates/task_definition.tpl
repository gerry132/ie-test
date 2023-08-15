[
    {
        "name": "${name}",
		"image": "${ecr_image_url}",
		"cpu": ${task_cpu},
		"memory": ${task_memory},
		"networkMode": "awsvpc",
		"logConfiguration": {
			"logDriver": "awslogs",
			"options": {
                "awslogs-group": "${log_group}",
                "awslogs-region": "${region}",
                "awslogs-stream-prefix": "ecs"
			}
		},
		"portMappings": [
            {
                "containerPort": ${port},
                "hostPort": ${port}
            }
		],
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
                "name": "CACHE_ADDRESS",
                "value": "${SETTINGS_CACHE_ADDRESS}"
            },
            {
                "name": "DATABASE_URL",
                "value": "${SETTINGS_DATABASE_URL}"
            },
            {
                "name": "DEBUG",
                "value": "${SETTINGS_DEBUG}"
            },
            {
                "name": "DEBUG_TOOLBAR",
                "value": "${SETTINGS_DEBUG_TOOLBAR}"
            },
            {
                "name": "SECRET_KEY",
                "value": "${SETTINGS_SECRET_KEY}"
            },
            {
                "name": "USE_CACHE",
                "value": "${SETTINGS_USE_CACHE}"
            },
            {
                "name": "USE_S3",
                "value": "${SETTINGS_USE_S3}"
            },
            {
                "name": "CORS_ALLOWED_ORIGINS",
                "value": "${SETTINGS_CORS_ALLOWED_ORIGINS}"
            },
            {
                "name": "CORS_ALLOW_ALL_ORIGINS",
                "value": "${SETTINGS_CORS_ALLOW_ALL_ORIGINS}"
            },
            {
                "name": "EMAIL_HOST",
                "value": "${SETTINGS_EMAIL_HOST}"
            },
            {
                "name": "DEFAULT_FROM_EMAIL",
                "value": "${SETTINGS_DEFAULT_FROM_EMAIL}"
            }
        ],
        "secrets": []
    }
]
