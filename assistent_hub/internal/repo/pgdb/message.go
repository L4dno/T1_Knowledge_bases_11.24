package pgdb

import (
	"account-management-service/internal/entity"
	"account-management-service/internal/repo/repoerrs"
	"account-management-service/pkg/postgres"
	"context"
	"errors"
	"fmt"

	"github.com/Masterminds/squirrel"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	log "github.com/sirupsen/logrus"
)

type MessageRepo struct {
	*postgres.Postgres
}

func NewMessageRepo(pg *postgres.Postgres) *MessageRepo {
	return &MessageRepo{pg}
}

func (r *MessageRepo) CreateMessage(ctx context.Context) (int, error) {
	sql, args, _ := r.Builder.
		Insert("messages").
		Values(squirrel.Expr("DEFAULT")).
		Suffix("RETURNING id").
		ToSql()

	var id int
	err := r.Pool.QueryRow(ctx, sql, args...).Scan(&id)
	if err != nil {
		log.Debugf("err: %v", err)
		var pgErr *pgconn.PgError
		if ok := errors.As(err, &pgErr); ok {
			if pgErr.Code == "23505" {
				return 0, repoerrs.ErrAlreadyExists
			}
		}
		return 0, fmt.Errorf("MessageRepo.CreateMessage - r.Pool.QueryRow: %v", err)
	}

	return id, nil
}

func (r *MessageRepo) GetMessageById(ctx context.Context, id int) (entity.Message, error) {
	sql, args, _ := r.Builder.
		Select("*").
		From("messages").
		Where("id = ?", id).
		ToSql()

	var message entity.Message
	err := r.Pool.QueryRow(ctx, sql, args...).Scan(
		&message.Uid,
		&message.Prompt,
	)
	if err != nil {
		if errors.Is(err, pgx.ErrNoRows) {
			return entity.Message{}, repoerrs.ErrNotFound
		}
		return entity.Message{}, fmt.Errorf("MessageRepo.GetMessageById - r.Pool.QueryRow: %v", err)
	}

	return message, nil
}
