package service

import (
	"account-management-service/internal/entity"
	"account-management-service/internal/repo"
	"account-management-service/internal/webapi"
	"account-management-service/pkg/hasher"
	"context"
	"time"
)

type AuthCreateUserInput struct {
	Username string
	Password string
}

type AuthGenerateTokenInput struct {
	Username string
	Password string
}

type Auth interface {
	CreateUser(ctx context.Context, input AuthCreateUserInput) (int, error)
	GenerateToken(ctx context.Context, input AuthGenerateTokenInput) (string, error)
	ParseToken(token string) (int, error)
}

type Message interface {
	CreateMessage(ctx context.Context) (int, error)
	GetMessageById(ctx context.Context, userId int) (entity.Message, error)
}

// type OperationHistoryInput struct {
// 	AccountId int
// 	SortType  string
// 	Offset    int
// 	Limit     int
// }

// type OperationHistoryOutput struct {
// 	Amount      int       `json:"amount"`
// 	Operation   string    `json:"operation"`
// 	Time        time.Time `json:"time"`
// 	Product     string    `json:"product,omitempty"`
// 	Order       *int      `json:"order,omitempty"`
// 	Description string    `json:"description,omitempty"`
// }

// type Operation interface {
// 	OperationHistory(ctx context.Context, input OperationHistoryInput) ([]OperationHistoryOutput, error)
// 	MakeReportLink(ctx context.Context, month, year int) (string, error)
// 	MakeReportFile(ctx context.Context, month, year int) ([]byte, error)
// }

type Services struct {
	Auth    Auth
	Message Message
}

type ServicesDependencies struct {
	Repos  *repo.Repositories
	GDrive webapi.GDrive
	Hasher hasher.PasswordHasher

	SignKey  string
	TokenTTL time.Duration
}

func NewServices(deps ServicesDependencies) *Services {
	return &Services{
		Auth:    NewAuthService(deps.Repos.User, deps.Hasher, deps.SignKey, deps.TokenTTL),
		Message: NewMessageService(deps.Repos.Message),
	}
}
