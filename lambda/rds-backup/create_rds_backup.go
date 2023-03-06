package rds_backup

import (
	"fmt"
	"log"
	"os"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/rds"
)

// This example creates a DB snapshot.
func RDS_CreateDBSnapshot_shared() (response *string) {
	svc := rds.New(session.New())
	currentTime := time.Now()
	dbSnapshotName := "a" + currentTime.Format("2006-01-02")
	input := &rds.CreateDBSnapshotInput{
		DBInstanceIdentifier: aws.String(os.Getenv("DB_NAME")),
		DBSnapshotIdentifier: aws.String(dbSnapshotName),
	}

	result, err := svc.CreateDBSnapshot(input)

	if err != nil {
		if awserr, ok := err.(awserr.Error); ok {
			switch awserr.Code() {
			case rds.ErrCodeDBSnapshotAlreadyExistsFault:
				fmt.Println(rds.ErrCodeDBSnapshotAlreadyExistsFault, awserr.Error())
			case rds.ErrCodeInvalidDBInstanceStateFault:
				fmt.Println(rds.ErrCodeInvalidDBInstanceStateFault, awserr.Error())
			case rds.ErrCodeDBInstanceNotFoundFault:
				fmt.Println(rds.ErrCodeDBInstanceNotFoundFault, awserr.Error())
			case rds.ErrCodeSnapshotQuotaExceededFault:
				fmt.Println(rds.ErrCodeSnapshotQuotaExceededFault, awserr.Error())
			default:
				fmt.Println(awserr.Error())
			}
		} else {
			// Print the error, cast err to awserr.Error to get the Code and
			// Message from an error.
			fmt.Println(err.Error())
		}
		//return nil
	}

	poll := &rds.DescribeDBSnapshotsInput{
		DBSnapshotIdentifier: aws.String(dbSnapshotName),
	}
	runner := true

	for runner {
		snapshot, err := svc.DescribeDBSnapshots(poll)
		if *snapshot.DBSnapshots[0].Status == "available" {
			runner = false
		}
		log.Println(err)
		log.Println(result)
		time.Sleep(10 * time.Second)
		log.Println("INCREASING THRESHOLD")

	}

	return &dbSnapshotName
}

func RDS_ModifyDBSnapshotAttribute(db string) bool {
	svc := rds.New(session.New())
	input := &rds.ModifyDBSnapshotAttributeInput{
		AttributeName:        aws.String("restore"),
		DBSnapshotIdentifier: aws.String(db),
		ValuesToAdd: []*string{
			aws.String(os.Getenv("ACCOUNT_ID")),
		},
	}

	result, err := svc.ModifyDBSnapshotAttribute(input)
	if err != nil {
		if awserr, ok := err.(awserr.Error); ok {
			switch awserr.Code() {
			case rds.ErrCodeDBSnapshotNotFoundFault:
				fmt.Println(rds.ErrCodeDBSnapshotNotFoundFault, awserr.Error())
			case rds.ErrCodeInvalidDBSnapshotStateFault:
				fmt.Println(rds.ErrCodeInvalidDBSnapshotStateFault, awserr.Error())
			case rds.ErrCodeSharedSnapshotQuotaExceededFault:
				fmt.Println(rds.ErrCodeSharedSnapshotQuotaExceededFault, awserr.Error())
			default:
				fmt.Println(awserr.Error())
			}
		} else {
			// Print the error, cast err to awserr.Error to get the Code and
			// Message from an error.
			fmt.Println(err.Error())
		}
		return false
	}

	fmt.Println(result)
	return true
}

func doEvery(d time.Duration, f func(time.Time)) {
	for x := range time.Tick(d) {
		f(x)
	}
}

//run build
// from ubuntu chmod to make main executable
