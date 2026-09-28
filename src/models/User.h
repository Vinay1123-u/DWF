#pragma once

#include <QString>

class User
{
public:
    User();
    User(int id, const QString& username, const QString& email, const QString& passwordHash = QString(),
         const QString& createdAt = QString(), const QString& updatedAt = QString());

    int id() const;
    QString username() const;
    QString email() const;
    QString passwordHash() const;
    QString createdAt() const;
    QString updatedAt() const;

    void setId(int id);
    void setUsername(const QString& username);
    void setEmail(const QString& email);
    void setPasswordHash(const QString& passwordHash);
    void setCreatedAt(const QString& createdAt);
    void setUpdatedAt(const QString& updatedAt);

private:
    int m_id;
    QString m_username;
    QString m_email;
    QString m_passwordHash;
    QString m_createdAt;
    QString m_updatedAt;
};
