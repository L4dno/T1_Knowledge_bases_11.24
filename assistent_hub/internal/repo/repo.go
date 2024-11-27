package repo

import (
	"account-management-service/internal/entity"
	"account-management-service/internal/repo/pgdb"
	"account-management-service/pkg/postgres"
	"context"
)

type User interface {
	CreateUser(ctx context.Context, user entity.User) (int, error)
	GetUserByUsernameAndPassword(ctx context.Context, username, password string) (entity.User, error)
	GetUserById(ctx context.Context, id int) (entity.User, error)
	GetUserByUsername(ctx context.Context, username string) (entity.User, error)
}

type Message interface {
	CreateMessage(ctx context.Context) (int, error)
	GetMessageById(ctx context.Context, id int) (entity.Message, error)
}

type Repositories struct {
	User
	Message
}

func NewRepositories(pg *postgres.Postgres) *Repositories {
	return &Repositories{
		User:    pgdb.NewUserRepo(pg),
		Message: pgdb.NewMessageRepo(pg),
	}
}
