package service

import (
	"account-management-service/internal/entity"
	"account-management-service/internal/repo"
	"account-management-service/internal/repo/repoerrs"
	"context"
)

type MessageService struct {
	messageRepo repo.Message
}

func NewMessageService(messageRepo repo.Message) *MessageService {
	return &MessageService{messageRepo: messageRepo}
}

func (s *MessageService) CreateMessage(ctx context.Context) (int, error) {
	id, err := s.messageRepo.CreateMessage(ctx)
	if err != nil {
		if err == repoerrs.ErrAlreadyExists {
			return 0, ErrMessageAlreadyExists
		}
		return 0, ErrCannotCreateMessage
	}

	return id, nil
}

func (s *MessageService) GetMessageById(ctx context.Context, userId int) (entity.Message, error) {
	return s.messageRepo.GetMessageById(ctx, userId)
}
