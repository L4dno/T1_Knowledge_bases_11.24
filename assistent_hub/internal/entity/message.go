package entity

// prev account

type Message struct {
	// we can get chat by uid and return ordered by firstkey
	Id     int    `db:id`
	Uid    int    `db:"uid"`
	Prompt string `db:"prompt"`
}
