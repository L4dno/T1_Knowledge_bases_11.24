package entity

// prev account

type Message struct {
	// we can get chat by uid and return ordered by firstkey
	Uid    int    `db:"uid"`
	Prompt string `db:"prompt"`
}
