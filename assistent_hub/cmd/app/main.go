package main

import (
	"account-management-service/internal/app"
	"fmt"
	"log"
	"os"
)

const configPath = "config/config.yaml"

func getPostgresURL() string {
	user := os.Getenv("POSTGRES_USER")
	password := os.Getenv("POSTGRES_PASSWORD")
	host := os.Getenv("POSTGRES_HOST")
	port := os.Getenv("POSTGRES_PORT")
	database := os.Getenv("POSTGRES_DB")

	return fmt.Sprintf("postgres://%s:%s@%s:%s/%s", user, password, host, port, database)
}

func getPostgresURLS() string {
	user := "unix"
	password := "unix"
	host := "0.0.0.0"
	port := "5432"
	database := "testing"

	return fmt.Sprintf("postgres://%s:%s@%s:%s/%s", user, password, host, port, database)
}

func main() {
	log.Printf("Connection string: %s", getPostgresURLS())
	app.Run(configPath)
}
