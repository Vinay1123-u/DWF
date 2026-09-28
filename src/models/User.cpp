#include "models/User.h"

User::User() : m_id(-1)
{
}

User::User(int id, const QString& username, const QString& email,
           const QString& passwordHash, const QString& createdAt, const QString& updatedAt)
    : m_id(id), m_username(username), m_email(email), m_passwordHash(passwordHash),
      m_createdAt(createdAt), m_updatedAt(updatedAt)
{
}

int User::id() const { return m_id; }
QString User::username() const { return m_username; }
QString User::email() const { return m_email; }
QString User::passwordHash() const { return m_passwordHash; }
QString User::createdAt() const { return m_createdAt; }
QString User::updatedAt() const { return m_updatedAt; }

void User::setId(int id) { m_id = id; }
void User::setUsername(const QString& username) { m_username = username; }
void User::setEmail(const QString& email) { m_email = email; }
void User::setPasswordHash(const QString& passwordHash) { m_passwordHash = passwordHash; }
void User::setCreatedAt(const QString& createdAt) { m_createdAt = createdAt; }
void User::setUpdatedAt(const QString& updatedAt) { m_updatedAt = updatedAt; }
