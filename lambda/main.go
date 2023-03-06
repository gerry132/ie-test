package main

import (
	rds_backup "create-db-snap/rds-backup"
	"log"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

func main() {
	lambda.Start(handler)
}

func handler(request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {

	backup_created_name := rds_backup.RDS_CreateDBSnapshot_shared()
	var shared bool
	log.Println(backup_created_name)
	if backup_created_name != nil {
		shared = rds_backup.RDS_ModifyDBSnapshotAttribute("a2023-03-06")
	} else {
		shared = false
	}

	response := events.APIGatewayProxyResponse{
		StatusCode: 200,
	}
	if !shared {
		response.StatusCode = 400
	}

	return response, nil
}

func Use(vals ...interface{}) {
	for _, val := range vals {
		_ = val
	}
}
