package entity

// changed user

type User struct {
	Uid      int    `db:"uid"`
	Username string `db:"username"`
	Password string `db:"password"`
	IsAdmin  bool   `db:"is_admin"`
}
