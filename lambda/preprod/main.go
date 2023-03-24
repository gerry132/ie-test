package main

import (
	"log"
	rds_create "restore-from-snapshot/rds-restore"

	"github.com/aws/aws-lambda-go/events"
	"github.com/aws/aws-lambda-go/lambda"
)

func main() {
	lambda.Start(handler)
}

func handler(request events.APIGatewayProxyRequest) (events.APIGatewayProxyResponse, error) {
	response := events.APIGatewayProxyResponse{
		StatusCode: 200,
	}

	snapArn := rds_create.GetMostRecentSnapshot()
	log.Println(*snapArn)
	dbName := rds_create.RestoreDBInstanceFromDBSnapshot(*snapArn)
	rds_create.SaveNewUrl(dbName)
	return response, nil
}
