package pwd

import "golang.org/x/crypto/bcrypt"

func Hash(password string) (hashed string, err error) {
	hashbyte, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		return "", err
	}
	return string(hashbyte), nil
}

func Compare(storedHash string, rawInput string) error {
	return bcrypt.CompareHashAndPassword([]byte(storedHash), []byte(rawInput))
}
