package postgres

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/Masterminds/squirrel"
	"github.com/jackc/pgx/v5"
	"github.com/jackc/pgx/v5/pgconn"
	"github.com/jackc/pgx/v5/pgxpool"
)

const (
	defaultMaxPoolSize  = 1
	defaultConnAttempts = 10
	defaultConnTimeout  = time.Second
)

type PgxPool interface {
	Close()
	Acquire(ctx context.Context) (*pgxpool.Conn, error)
	Exec(ctx context.Context, sql string, arguments ...any) (pgconn.CommandTag, error)
	Query(ctx context.Context, sql string, args ...any) (pgx.Rows, error)
	QueryRow(ctx context.Context, sql string, args ...any) pgx.Row
	SendBatch(ctx context.Context, b *pgx.Batch) pgx.BatchResults
	Begin(ctx context.Context) (pgx.Tx, error)
	BeginTx(ctx context.Context, txOptions pgx.TxOptions) (pgx.Tx, error)
	CopyFrom(ctx context.Context, tableName pgx.Identifier, columnNames []string, rowSrc pgx.CopyFromSource) (int64, error)
	Ping(ctx context.Context) error
}

type Postgres struct {
	maxPoolSize  int
	connAttempts int
	connTimeout  time.Duration

	Builder squirrel.StatementBuilderType
	Pool    PgxPool
}

func New(url string, opts ...Option) (*Postgres, error) {
	pg := &Postgres{
		maxPoolSize:  defaultMaxPoolSize,
		connAttempts: defaultConnAttempts,
		connTimeout:  defaultConnTimeout,
	}

	for _, opt := range opts {
		opt(pg)
	}

	pg.Builder = squirrel.StatementBuilder.PlaceholderFormat(squirrel.Dollar)

	poolConfig, err := pgxpool.ParseConfig(url)
	if err != nil {
		return nil, fmt.Errorf("pgdb - New - pgxpool.ParseConfig: %w", err)
	}

	poolConfig.MaxConns = int32(pg.maxPoolSize)

	for pg.connAttempts > 0 {
		pg.Pool, err = pgxpool.NewWithConfig(context.Background(), poolConfig)
		if err == nil {
			break
		}

		log.Printf("Postgres is trying to connect, attempts left: %d", pg.connAttempts)
		time.Sleep(pg.connTimeout)
		pg.connAttempts--
	}

	if err != nil {
		return nil, fmt.Errorf("pgdb - New - pgxpool.ConnectConfig: %w", err)
	}

	return pg, nil
}

func (p *Postgres) Close() {
	if p.Pool != nil {
		p.Pool.Close()
	}
}

// package to manage settings of pg
// package postgres

// import (
// 	"fmt"
// 	"log"
// 	"time"

// 	"gorm.io/driver/postgres"
// 	"gorm.io/gorm"
// 	"gorm.io/gorm/logger"
// 	"gorm.io/gorm/schema"
// )

// type Postgres struct {
// 	maxPoolSize  int
// 	connAttempts int
// 	connTimeout  time.Duration
// 	DB           *gorm.DB
// }

// const (
// 	defaultMaxPoolSize  = 1
// 	defaultConnAttempts = 10
// 	defaultConnTimeout  = time.Second
// )

// func New(dsn string, opts ...Option) (*Postgres, error) {
// 	pg := &Postgres{
// 		maxPoolSize:  defaultMaxPoolSize,
// 		connAttempts: defaultConnAttempts,
// 		connTimeout:  defaultConnTimeout,
// 	}

// 	for _, opt := range opts {
// 		opt(pg)
// 	}

// 	var db *gorm.DB
// 	var err error

// 	for pg.connAttempts > 0 {
// 		db, err = gorm.Open(postgres.Open(dsn), &gorm.Config{
// 			Logger: logger.Default.LogMode(logger.Info),
// 			NamingStrategy: schema.NamingStrategy{
// 				SingularTable: true,
// 			},
// 		})
// 		if err == nil {
// 			sqlDB, err := db.DB()
// 			if err != nil {
// 				return nil, fmt.Errorf("failed to get database instance: %w", err)
// 			}

// 			// Configure connection pool
// 			sqlDB.SetMaxOpenConns(pg.maxPoolSize)
// 			sqlDB.SetMaxIdleConns(pg.maxPoolSize / 2)
// 			sqlDB.SetConnMaxLifetime(10 * time.Minute)
// 			break
// 		}

// 		log.Printf("Postgres is trying to connect, attempts left: %d", pg.connAttempts)
// 		time.Sleep(pg.connTimeout)
// 		pg.connAttempts--
// 	}

// 	if err != nil {
// 		return nil, fmt.Errorf("failed to connect to Postgres: %w", err)
// 	}

// 	pg.DB = db
// 	return pg, nil
// }

// func (p *Postgres) Close() error {
// 	if p.DB != nil {
// 		sqlDB, err := p.DB.DB()
// 		if err != nil {
// 			return fmt.Errorf("failed to get SQL DB instance: %w", err)
// 		}
// 		return sqlDB.Close()
// 	}
// 	return nil
// }
