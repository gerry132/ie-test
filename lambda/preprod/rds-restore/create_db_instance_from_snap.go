package rds_restore

import (
	"fmt"
	"log"
	"time"

	"github.com/aws/aws-sdk-go/aws"
	"github.com/aws/aws-sdk-go/aws/awserr"
	"github.com/aws/aws-sdk-go/aws/session"
	"github.com/aws/aws-sdk-go/service/rds"
	"github.com/aws/aws-sdk-go/service/ssm"
)

func GetParam(param string) string {
	svc := ssm.New(session.New())

	input := &ssm.GetParameterInput{
		Name:           aws.String(param),
		WithDecryption: aws.Bool(true),
	}
	parameter, err := svc.GetParameter(input)
	value := *parameter.Parameter.Value

	if err != nil {
		log.Println(err)
		return "Error"
	}
	return value
}

func SaveNewUrl(dbName *string) bool {

	// prodUserName := "prod_ireland_ie_username"
	// postgres://${module.database.db_username}:${data.aws_ssm_parameter.random_db_password.value}@${module.database.address}:${module.database.db_port}/${module.database.db_name}
	svc_one := rds.New(session.New())
	input_one := &rds.DescribeDBInstancesInput{
		DBInstanceIdentifier: aws.String(*dbName),
	}

	snapshot, err := svc_one.DescribeDBInstances(input_one)

	address := *snapshot.DBInstances[0].Endpoint.Address
	prodPass := GetParam("prod_pass")
	prodUser := "prod_ireland_ie_username"

	master_url := fmt.Sprintf("postgres://%s:%s@%s:5432/prod_ireland_ie", prodUser, prodPass, address)

	svc := ssm.New(session.New())
	input := &ssm.PutParameterInput{
		Name:      aws.String("master_url"),
		Value:     aws.String(master_url),
		Type:      aws.String("SecureString"),
		Overwrite: aws.Bool(true),
	}

	success, err := svc.PutParameter(input)
	if err != nil {
		log.Println("PARAM STORE")
		log.Println(success)
		log.Println(err)
		return false
	}
	return true
}

func GetMostRecentSnapshot() *string {
	svc := rds.New(session.New())
	input := &rds.DescribeDBSnapshotsInput{
		IncludeShared: aws.Bool(true),
	}

	snapshots, err := svc.DescribeDBSnapshots(input)

	if err != nil {
		return nil
	}
	var last *string
	var lastCreated time.Time
	for _, snapshot := range snapshots.DBSnapshots {
		if *snapshot.DBInstanceIdentifier == "prod-db-postgres" && *snapshot.SnapshotType == "shared" {
			log.Println("DB DB DB DBD B")
			if lastCreated.IsZero() {
				lastCreated = *snapshot.SnapshotCreateTime
				last = snapshot.DBSnapshotIdentifier
			} else {
				if lastCreated.Before(*snapshot.SnapshotCreateTime) {
					lastCreated = *snapshot.SnapshotCreateTime
					last = snapshot.DBSnapshotIdentifier
				}
			}
			log.Println(snapshot.SnapshotCreateTime)
			log.Println(*last)
			log.Println("DB DB DB DBD B")
		}
	}
	return last
}

func RestoreDBInstanceFromDBSnapshot(snapshot string) *string {
	svc := rds.New(session.New())
	currentTime := time.Now()
	dbName := "a" + currentTime.Format("2006-01-02")
	var s []*string
	s = append(s, aws.String("sg-0447ea8351a9c68cc"))
	input := &rds.RestoreDBInstanceFromDBSnapshotInput{
		DBInstanceIdentifier: aws.String(dbName),
		DBSnapshotIdentifier: aws.String(snapshot),
		DBSubnetGroupName:    aws.String("db-clone-preprod-subnet-group"),
		VpcSecurityGroupIds:  s,
	}

	result, err := svc.RestoreDBInstanceFromDBSnapshot(input)
	log.Println(result)
	if err != nil {
		if aerr, ok := err.(awserr.Error); ok {
			switch aerr.Code() {
			case rds.ErrCodeDBInstanceAlreadyExistsFault:
				fmt.Println(rds.ErrCodeDBInstanceAlreadyExistsFault, aerr.Error())
			case rds.ErrCodeDBSnapshotNotFoundFault:
				fmt.Println(rds.ErrCodeDBSnapshotNotFoundFault, aerr.Error())
			case rds.ErrCodeInstanceQuotaExceededFault:
				fmt.Println(rds.ErrCodeInstanceQuotaExceededFault, aerr.Error())
			case rds.ErrCodeInsufficientDBInstanceCapacityFault:
				fmt.Println(rds.ErrCodeInsufficientDBInstanceCapacityFault, aerr.Error())
			case rds.ErrCodeInvalidDBSnapshotStateFault:
				fmt.Println(rds.ErrCodeInvalidDBSnapshotStateFault, aerr.Error())
			case rds.ErrCodeStorageQuotaExceededFault:
				fmt.Println(rds.ErrCodeStorageQuotaExceededFault, aerr.Error())
			case rds.ErrCodeInvalidVPCNetworkStateFault:
				fmt.Println(rds.ErrCodeInvalidVPCNetworkStateFault, aerr.Error())
			case rds.ErrCodeInvalidRestoreFault:
				fmt.Println(rds.ErrCodeInvalidRestoreFault, aerr.Error())
			case rds.ErrCodeDBSubnetGroupNotFoundFault:
				fmt.Println(rds.ErrCodeDBSubnetGroupNotFoundFault, aerr.Error())
			case rds.ErrCodeDBSubnetGroupDoesNotCoverEnoughAZs:
				fmt.Println(rds.ErrCodeDBSubnetGroupDoesNotCoverEnoughAZs, aerr.Error())
			case rds.ErrCodeInvalidSubnet:
				fmt.Println(rds.ErrCodeInvalidSubnet, aerr.Error())
			case rds.ErrCodeProvisionedIopsNotAvailableInAZFault:
				fmt.Println(rds.ErrCodeProvisionedIopsNotAvailableInAZFault, aerr.Error())
			case rds.ErrCodeOptionGroupNotFoundFault:
				fmt.Println(rds.ErrCodeOptionGroupNotFoundFault, aerr.Error())
			case rds.ErrCodeStorageTypeNotSupportedFault:
				fmt.Println(rds.ErrCodeStorageTypeNotSupportedFault, aerr.Error())
			case rds.ErrCodeAuthorizationNotFoundFault:
				fmt.Println(rds.ErrCodeAuthorizationNotFoundFault, aerr.Error())
			case rds.ErrCodeKMSKeyNotAccessibleFault:
				fmt.Println(rds.ErrCodeKMSKeyNotAccessibleFault, aerr.Error())
			case rds.ErrCodeDBSecurityGroupNotFoundFault:
				fmt.Println(rds.ErrCodeDBSecurityGroupNotFoundFault, aerr.Error())
			case rds.ErrCodeDomainNotFoundFault:
				fmt.Println(rds.ErrCodeDomainNotFoundFault, aerr.Error())
			case rds.ErrCodeDBParameterGroupNotFoundFault:
				fmt.Println(rds.ErrCodeDBParameterGroupNotFoundFault, aerr.Error())
			case rds.ErrCodeBackupPolicyNotFoundFault:
				fmt.Println(rds.ErrCodeBackupPolicyNotFoundFault, aerr.Error())
			case rds.ErrCodeNetworkTypeNotSupported:
				fmt.Println(rds.ErrCodeNetworkTypeNotSupported, aerr.Error())
			case rds.ErrCodeDBClusterSnapshotNotFoundFault:
				fmt.Println(rds.ErrCodeDBClusterSnapshotNotFoundFault, aerr.Error())
			default:
				fmt.Println(aerr.Error())
			}
		} else {
			// Print the error, cast err to awserr.Error to get the Code and
			// Message from an error.
			fmt.Println(err.Error())
		}
		return nil
	}
	runner := true
	for runner {
		input := &rds.DescribeDBInstancesInput{
			DBInstanceIdentifier: aws.String(dbName),
		}

		snapshot, err := svc.DescribeDBInstances(input)
		if *snapshot.DBInstances[0].DBInstanceStatus == "available" {
			runner = false
		}

		log.Println(err)
		log.Println(snapshot)
		time.Sleep(10 * time.Second)
		log.Println("INCREASING THRESHOLD")

	}
	inputPlace := &rds.DescribeDBInstancesInput{}
	dbList, err := svc.DescribeDBInstances(inputPlace)

	for _, db := range dbList.DBInstances {
		if *db.DBInstanceIdentifier != dbName {
			log.Println("DELETE")
			log.Println("DELETE")
			log.Println(*db.DBInstanceIdentifier)
			dbInstance := &rds.DeleteDBInstanceInput{
				DBInstanceIdentifier: *&db.DBInstanceIdentifier,
				SkipFinalSnapshot:    aws.Bool(true),
			}
			del, err := svc.DeleteDBInstance(dbInstance)
			log.Println(del)
			log.Println(err)
		}
	}

	return &dbName
}
