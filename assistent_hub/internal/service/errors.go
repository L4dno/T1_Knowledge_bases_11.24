package service

import "fmt"

var (
	ErrCannotSignToken  = fmt.Errorf("cannot sign token")
	ErrCannotParseToken = fmt.Errorf("cannot parse token")

	ErrUserAlreadyExists = fmt.Errorf("user already exists")
	ErrCannotCreateUser  = fmt.Errorf("cannot create user")
	ErrUserNotFound      = fmt.Errorf("user not found")
	ErrCannotGetUser     = fmt.Errorf("cannot get user")

	// guess we cant get similar pessages by firstkey
	ErrMessageAlreadyExists = fmt.Errorf("message already exists")
	ErrCannotCreateMessage  = fmt.Errorf("cannot create message")
	ErrMessageNotFound      = fmt.Errorf("message not found")
	ErrCannotGetMessage     = fmt.Errorf("cannot get message")

	ErrCannotCreateReservation = fmt.Errorf("cannot create reservation")
)
